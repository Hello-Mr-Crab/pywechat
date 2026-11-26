'''
platform.linux.driver
=====================
Linux 驱动:发现应用、启动微信、拿到主窗口/登录窗口。

设计上刻意保持"薄":它只负责
    * 找到 AT-SPI 上的 wechat 应用;
    * 按角色 + 名称定位 frame(微信主窗口 / 登录窗口);
    * 需要时把微信拉起来(带无障碍环境变量)或调整窗口大小。

具体的会话/消息操作在 `pyweixin.linux_auto` 里。
'''
from __future__ import annotations

import os
import shutil
import subprocess
import time
from typing import Optional

from ..base import PlatformNotSupported
from .atspi import AtspiSession, AtspiUnavailable, Snapshot
from .element import LinuxElement, LinuxWindowSpecification
from .x11 import X11, X11Unavailable

#: AT-SPI 里微信的应用名(小写,来自可执行文件名)
APP_NAME_CANDIDATES = ('wechat', 'WeChat', 'weixin', 'Weixin')

#: 主窗口 / 登录窗口的标题(多语言)
MAIN_WINDOW_TITLES = ('微信', 'Weixin', 'WeChat')
LOGIN_WINDOW_TITLES = ('微信', 'Weixin', 'WeChat')

#: 二进制候选路径
WECHAT_PATH_CANDIDATES = (
    '/opt/wechat/wechat',
    '/usr/bin/wechat',
    '/usr/lib/wechat/wechat',
    '/opt/weixin/weixin',
)


def find_wechat_binary() -> Optional[str]:
    '''按顺序找微信可执行文件。'''
    env = os.environ.get('PYWEIXIN_WECHAT_PATH')
    if env and os.path.exists(env):
        return env
    for p in WECHAT_PATH_CANDIDATES:
        if os.path.isfile(p) and os.access(p, os.X_OK):
            return p
    return shutil.which('wechat') or shutil.which('weixin')


def is_wechat_running() -> bool:
    '''不看 UI,只看进程/可执行文件。'''
    try:
        for pid in os.listdir('/proc'):
            if not pid.isdigit():
                continue
            try:
                with open(f'/proc/{pid}/comm', 'r') as f:
                    comm = f.read().strip()
            except OSError:
                continue
            if comm in ('wechat', 'weixin'):
                return True
    except OSError:
        pass
    return False


class LinuxDesktop:
    '''相当于 pywinauto 的 `Desktop(backend='uia')`。'''

    def __init__(self, session: AtspiSession, x11: X11):
        self._session = session
        self._x11 = x11

    @property
    def session(self) -> AtspiSession:
        return self._session

    @property
    def x11(self) -> X11:
        return self._x11

    def applications(self) -> list[str]:
        return self._session.applications()

    def app_name(self) -> str:
        '''当前 AT-SPI 上微信的应用名。'''
        names = self._session.applications()
        for cand in APP_NAME_CANDIDATES:
            if cand in names:
                return cand
        for n in names:
            if 'wechat' in n.lower() or 'weixin' in n.lower():
                return n
        raise AtspiUnavailable(f'无障碍总线上没有微信应用(当前有: {names!r})')

    def window(self, **criteria) -> LinuxWindowSpecification:
        '''按选择器找顶层窗口/元素。'''
        return LinuxWindowSpecification(self._session, self._x11, criteria,
                                        app_name=self.app_name())

    def windows(self) -> list[LinuxWindowSpecification]:
        snap = self._session.snapshot(self.app_name())
        return [LinuxWindowSpecification(self._session, self._x11,
                                         {'role': 'frame', 'title': n.name},
                                         app_name=snap.app_name, snap=snap)
                for n in snap.nodes
                if n.role in ('frame', 'dialog') and n.depth <= 2]

    def snapshot(self, force: bool = False) -> Snapshot:
        return self._session.snapshot(self.app_name(), force=force)


class LinuxBackend:
    '''平台驱动的 Linux 实现。'''

    name = 'linux'

    def __init__(self, display: Optional[str] = None, dry_run: bool = False):
        self.x11 = X11(display=display, dry_run=dry_run)
        self.session = AtspiSession()
        self._desktop = LinuxDesktop(self.session, self.x11)

    # -- Backend 协议 ------------------------------------------------------ #
    def desktop(self) -> LinuxDesktop:
        return self._desktop

    def attach(self, name: Optional[str] = None) -> Optional[LinuxWindowSpecification]:
        '''附着到微信主窗口(或登录窗口)。'''
        return self.frame(title=name or MAIN_WINDOW_TITLES)

    def launch(self, path: Optional[str] = None,
               args: tuple = ()) -> Optional[LinuxWindowSpecification]:
        return launch_wechat(path=path, extra_args=args, x11=self.x11)

    # -- 窗口 ------------------------------------------------------------- #
    def frame(self, title, timeout: float = 0.0) -> Optional[LinuxWindowSpecification]:
        ''':param title: 标题字符串或字符串元组'''
        titles = (title,) if isinstance(title, str) else tuple(title)
        deadline = time.time() + max(timeout, 0.0)
        while True:
            try:
                app = self._desktop.app_name()
            except AtspiUnavailable:
                app = None
            if app:
                for t in titles:
                    spec = LinuxWindowSpecification(self.session, self.x11,
                                                    {'role': 'frame', 'title': t},
                                                    app_name=app)
                    if spec.exists():
                        return spec
            if time.time() >= deadline:
                return None
            time.sleep(0.2)

    def main_window(self, timeout: float = 0.0) -> Optional[LinuxWindowSpecification]:
        return self.frame(MAIN_WINDOW_TITLES, timeout=timeout)

    def login_window(self, timeout: float = 0.0) -> Optional[LinuxWindowSpecification]:
        return self.frame(LOGIN_WINDOW_TITLES, timeout=timeout)

    def is_logged_in(self) -> bool:
        '''主窗口里出现会话列表 = 已登录。'''
        win = self.main_window()
        if win is None:
            return False
        try:
            return win.child_window(control_type='List', title='会话').exists() or \
                   win.child_window(control_type='List', title='Chats').exists()
        except Exception:
            return False

    def resize_main_window(self, width: int = 1200, height: int = 900) -> None:
        '''把主窗口调到一个适合自动化的大小(裸 Xvfb 没有窗口管理器,需要手动摆)。'''
        win = self.main_window(timeout=3)
        if win is None:
            return
        rect = win.rectangle()
        screen_w, screen_h = self.x11.screen_size()
        x = max((screen_w - width) // 2, 0)
        y = max((screen_h - height) // 2, 0)
        found = self.x11.find_window(win.window_text())
        if found:
            self.x11.resize_window(found['id'], width, height, x, y)

    def screenshot(self, path: str, region=None) -> str:
        return self.x11.screenshot(path, region=region)


# --------------------------------------------------------------------------- #
# 启动
# --------------------------------------------------------------------------- #
def wechat_env(base: Optional[dict] = None) -> dict:
    '''启动微信所需的环境:强制 X11 后端 + 强制打开 Qt 无障碍。

    在无头环境(Xvfb)里,`toolkit-accessibility` 的 gsettings 往往不可用,
    Qt 就不会把自己的控件注册到 a11y 总线上。`QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1`
    是 Qt 官方提供的开关,可以绕过这个检测。
    '''
    env = dict(os.environ if base is None else base)
    env.setdefault('QT_LINUX_ACCESSIBILITY_ALWAYS_ON', '1')
    env.setdefault('QT_QPA_PLATFORM', 'xcb')
    env.setdefault('NO_AT_BRIDGE', '0')
    env.setdefault('XDG_SESSION_TYPE', 'x11')
    return env


def launch_wechat(path: Optional[str] = None, extra_args: tuple = (),
                  x11: Optional[X11] = None, wait: float = 20.0,
                  log_path: str = '/tmp/pyweixin-wechat.log'
                  ) -> Optional[LinuxWindowSpecification]:
    '''启动微信并等待它的窗口出现在无障碍总线上。'''
    exe = path or find_wechat_binary()
    if not exe:
        raise PlatformNotSupported('启动微信', 'linux: 找不到微信可执行文件')

    env = wechat_env()
    env['DISPLAY'] = (x11.display if x11 else env.get('DISPLAY', ':0'))

    if is_wechat_running():
        backend = LinuxBackend(display=env['DISPLAY'])
        return backend.main_window() or backend.login_window()

    log = open(log_path, 'wb')
    subprocess.Popen([exe, *extra_args], env=env, cwd=os.path.dirname(exe) or '/',
                     stdout=log, stderr=subprocess.STDOUT, start_new_session=True)

    backend = LinuxBackend(display=env['DISPLAY'])
    deadline = time.time() + wait
    while time.time() < deadline:
        win = backend.main_window()
        if win is not None:
            return win
        time.sleep(0.5)
    raise AtspiUnavailable(
        f'微信已启动但 {wait:.0f} 秒内没有在 AT-SPI 上出现窗口。\n'
        f'请检查:登录窗口是否弹出、QT_LINUX_ACCESSIBILITY_ALWAYS_ON 是否生效、'
        f'日志 {log_path}。')
