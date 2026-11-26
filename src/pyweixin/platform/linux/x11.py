'''
platform.linux.x11
==================
X11 输入/截图。全部通过外部命令(`xdotool` / `xclip` / `ffmpeg`)实现,
不依赖任何需要 root 的组件,也不需要注入微信进程。

为什么用 XTest 点击而不是 AT-SPI 的 `Action.DoAction`
----------------------------------------------------
微信的侧边栏、会话列表项等都是 Qt 自绘控件:它们在无障碍树里只有 role 和
name,没有实现 `QAccessibleActionInterface`。对它们调用 `DoAction` 会让 Qt 的
Action adaptor 解引用空指针,微信主进程直接 SIGSEGV。XTest 是内核输入层,
对应用完全透明,是唯一安全的"写"通道。

坐标系
------
所有坐标都是**物理屏幕像素**。窗口在 X11 上没有窗口管理器时(裸 Xvfb)也可以
直接用绝对坐标点击。
'''
from __future__ import annotations

import os
import shutil
import subprocess
import time
from typing import Optional, Sequence

#: pywinauto `type_keys` 的 `{TOKEN}` -> X keysym
KEY_TOKENS = {
    'ENTER': 'Return', 'RETURN': 'Return', 'TAB': 'Tab', 'ESC': 'Escape',
    'ESCAPE': 'Escape', 'BACKSPACE': 'BackSpace', 'BKSP': 'BackSpace',
    'DELETE': 'Delete', 'DEL': 'Delete', 'INSERT': 'Insert', 'INS': 'Insert',
    'UP': 'Up', 'DOWN': 'Down', 'LEFT': 'Left', 'RIGHT': 'Right',
    'HOME': 'Home', 'END': 'End', 'PGUP': 'Prior', 'PGDN': 'Next',
    'PAGEUP': 'Prior', 'PAGEDOWN': 'Next', 'SPACE': 'space',
    'WIN': 'Super_L', 'CTRL': 'ctrl', 'SHIFT': 'shift', 'ALT': 'alt',
}

MODIFIER_PREFIX = {'^': 'ctrl', '%': 'alt', '+': 'shift'}


class X11Unavailable(RuntimeError):
    def __init__(self, detail: str):
        super().__init__(detail + '\n需要 xdotool / xclip / ffmpeg,请先安装:'
                         ' pacman -S xdotool xclip ffmpeg')


class X11:
    '''一个 X display 上的输入与截图能力。'''

    def __init__(self, display: Optional[str] = None, dry_run: bool = False):
        self.display = display or os.environ.get('DISPLAY', ':0')
        self.dry_run = dry_run
        self._env = dict(os.environ)
        self._env['DISPLAY'] = self.display

    # -- 基础 ------------------------------------------------------------- #
    def _which(self, name: str) -> str:
        path = shutil.which(name)
        if not path:
            raise X11Unavailable(f'找不到 {name}')
        return path

    def _run(self, cmd: Sequence[str], input_bytes: Optional[bytes] = None,
             check: bool = True, timeout: float = 10.0) -> subprocess.CompletedProcess:
        if self.dry_run:
            return subprocess.CompletedProcess(cmd, 0, b'', b'')
        return subprocess.run(cmd, input=input_bytes, env=self._env,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              check=check, timeout=timeout)

    # -- 指针 ------------------------------------------------------------- #
    def move(self, x: int, y: int) -> None:
        self._run([self._which('xdotool'), 'mousemove', '--sync', str(int(x)), str(int(y))])

    def click(self, x: int, y: int, button: int = 1, count: int = 1) -> None:
        self.move(x, y)
        time.sleep(0.03)
        args = [self._which('xdotool'), 'click', '--repeat', str(int(count)),
                '--delay', '40', str(int(button))]
        self._run(args)

    def double_click(self, x: int, y: int, button: int = 1) -> None:
        self.click(x, y, button=button, count=2)

    def scroll(self, x: int, y: int, clicks: int) -> None:
        '''clicks > 0 向上滚, < 0 向下滚(X11 button 4/5)。'''
        self.move(x, y)
        button = 4 if clicks > 0 else 5
        for _ in range(abs(int(clicks))):
            self._run([self._which('xdotool'), 'click', str(button)])
            time.sleep(0.02)

    # -- 键盘 ------------------------------------------------------------- #
    def key(self, spec: str) -> None:
        '''发一个 keysym 组合,如 `Return` / `ctrl+a`。'''
        self._run([self._which('xdotool'), 'key', '--clearmodifiers', spec])

    def type_text(self, text: str, delay_ms: int = 12) -> None:
        '''用 XTEST 逐字输入。

        `xdotool type` 会为 Unicode 字符临时映射 keysym,因此中文/emoji 也能输入;
        但输入法(ibus/fcitx)路径不经过 XTEST 时会失效。中文更稳的做法是
        `paste_text`(走剪贴板)。
        '''
        if not text:
            return
        xdotool = self._which('xdotool')
        for line_no, line in enumerate(text.split('\n')):
            if line_no:
                self._run([xdotool, 'key', 'Return'])
            if not line:
                continue
            self._run([xdotool, 'type', '--delay', str(int(delay_ms)), '--', line])

    def type_keys(self, keys: str, pause: float = 0.0) -> None:
        '''pywinauto `type_keys` 语法的子集:`{TOKEN}`、`^a`/`%a`/`+a`、普通文本。'''
        i = 0
        buf = []

        def flush():
            if buf:
                self.type_text(''.join(buf))
                buf.clear()

        while i < len(keys):
            ch = keys[i]
            if ch == '{':
                j = keys.find('}', i)
                if j == -1:
                    buf.append(ch)
                    i += 1
                    continue
                flush()
                token = keys[i + 1:j].strip().upper()
                if token in KEY_TOKENS:
                    self.key(KEY_TOKENS[token])
                elif token.startswith('VK_') or token.isdigit():
                    pass  # 虚拟键码在 Linux 无意义,忽略
                else:
                    self.key(token.lower())
                i = j + 1
                if pause:
                    time.sleep(pause)
                continue
            if ch in MODIFIER_PREFIX and i + 1 < len(keys):
                flush()
                self.key(f'{MODIFIER_PREFIX[ch]}+{keys[i + 1]}')
                i += 2
                continue
            buf.append(ch)
            i += 1
        flush()

    def paste_text(self, text: str) -> None:
        '''把文本放进 X 剪贴板再按 Ctrl+V —— 中文最可靠的输入方式。

        xclip 会 fork 一个常驻子进程来"持有"剪贴板(否则粘贴瞬间内容就没了),
        子进程继承了父进程的 stdout/stderr,用 `subprocess.run` + PIPE 会一直等
        EOF 从而挂死。所以这里必须用 DEVNULL + Popen,不等待它退出。
        '''
        if self.dry_run:
            return
        xclip = self._which('xclip')
        proc = subprocess.Popen([xclip, '-selection', 'clipboard', '-in', '-loops', '0'],
                                stdin=subprocess.PIPE, env=self._env,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                start_new_session=True)
        try:
            proc.stdin.write(text.encode('utf-8'))
            proc.stdin.close()
        except (BrokenPipeError, OSError):
            pass
        time.sleep(0.12)
        self.key('ctrl+v')
        time.sleep(0.05)

    # -- 截图 ------------------------------------------------------------- #
    def screenshot(self, path: str, region: Optional[tuple[int, int, int, int]] = None) -> str:
        '''截图到 `path`(PNG)。`region` 为 (x, y, w, h),None 表示整屏。'''
        ffmpeg = self._which('ffmpeg')
        if region is None:
            w, h = self.screen_size()
            x = y = 0
        else:
            x, y, w, h = (int(v) for v in region)
        w, h = max(int(w), 1), max(int(h), 1)
        cmd = [ffmpeg, '-loglevel', 'error', '-y', '-f', 'x11grab',
               '-video_size', f'{w}x{h}', '-i', f'{self.display}+{x},{y}',
               '-frames:v', '1', path]
        os.makedirs(os.path.dirname(os.path.abspath(path)) or '.', exist_ok=True)
        self._run(cmd)
        return path

    # -- 窗口 ------------------------------------------------------------- #
    def screen_size(self) -> tuple[int, int]:
        out = self._run([self._which('xdotool'), 'getdisplaygeometry']).stdout.decode()
        parts = out.split()
        return int(parts[0]), int(parts[1])

    def windows(self) -> list[dict]:
        '''列出当前所有可见顶层窗口。'''
        xdotool = self._which('xdotool')
        try:
            ids = self._run([xdotool, 'search', '--onlyvisible', '--name', '.']).stdout.decode().split()
        except subprocess.CalledProcessError:
            return []
        out = []
        for wid in ids:
            try:
                name = self._run([xdotool, 'getwindowname', wid]).stdout.decode().strip()
                geo = self._run([xdotool, 'getwindowgeometry', '--shell', wid]).stdout.decode()
            except subprocess.CalledProcessError:
                continue
            info = {'id': wid, 'name': name}
            for line in geo.splitlines():
                if '=' in line:
                    k, v = line.split('=', 1)
                    info[k.strip().lower()] = int(v) if v.strip().lstrip('-').isdigit() else v
            out.append(info)
        return out

    def find_window(self, name: str, exact: bool = False) -> Optional[dict]:
        for w in self.windows():
            if (w['name'] == name) if exact else (name in w['name']):
                return w
        return None

    def resize_window(self, wid: str, width: int, height: int,
                      x: Optional[int] = None, y: Optional[int] = None) -> None:
        xdotool = self._which('xdotool')
        self._run([xdotool, 'windowsize', str(wid), str(int(width)), str(int(height))])
        if x is not None and y is not None:
            self._run([xdotool, 'windowmove', str(wid), str(int(x)), str(int(y))])

    def focus_window(self, wid: str) -> None:
        '''尽力而为:没有窗口管理器时 windowactivate 会失败,退回 windowfocus。'''
        xdotool = self._which('xdotool')
        for cmd in ('windowactivate', 'windowfocus'):
            try:
                self._run([xdotool, cmd, str(wid)])
                return
            except subprocess.CalledProcessError:
                continue
