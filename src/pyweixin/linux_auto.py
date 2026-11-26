'''
pyweixin.linux_auto
===================
Linux 下的最小可用 API:打开会话 / 发送消息 / 读取消息。

设计约束
--------
1. **收件人白名单(硬规则)**:只允许向 `ALLOWED_RECIPIENTS` 里的会话发送任何内容,
   其它收件人一律在**触碰 UI 之前**抛 `RecipientNotAllowed`。白名单是硬编码的,
   不接受运行时覆盖(改白名单只能改代码 + 改测试)。
2. 读走 AT-SPI,写走 XTest;绝不注入微信进程、不改注册表、不逆向二进制。
3. 找不到控件时抛 `ElementNotFound` / `NotLoginError`,不做"猜一个坐标点下去"。
4. 坐标方案(截图 + 固定坐标)只在 `COORDINATE_FALLBACK` 显式开启时使用,
   且必须配合 `docs/LINUX.md` 里的窗口尺寸约定 —— 默认关闭。

用法::

    from pyweixin import linux_auto as wx

    wx.is_logged_in()                       # True/False
    wx.open_chat('文件传输助手')
    wx.send_message('文件传输助手', 'hello from Xvfb')
    wx.read_messages(5)                     # [{'sender':..,'content':..,'type':..}, ...]
    wx.send_message('某个真实好友', 'hi')     # -> RecipientNotAllowed,且不会碰 UI
'''
from __future__ import annotations

import os
import re
import time
from typing import Iterable, Optional

from .Errors import NotLoginError, NotStartError, NotFoundError

#: 主窗口标题(多语言) —— 用于把主窗口自身从"会话窗口"里排除
MAIN_WINDOW_TITLES = ('微信', 'Weixin', 'WeChat')
from .platform.base import ElementNotFound, PlatformNotSupported

# --------------------------------------------------------------------------- #
# 收件人白名单 —— 唯一的"安全闸"
# --------------------------------------------------------------------------- #
#: 允许发送的目标。硬编码,不做任何形式的放宽。
#: 增加条目必须同时改 `tests/test_recipient_whitelist.py` 里的断言。
ALLOWED_RECIPIENTS: frozenset[str] = frozenset({
    '文件传输助手',
    '依依',
})


class RecipientNotAllowed(PermissionError):
    '''收件人不在白名单内。**任何**发送类操作都必须先过这一关。'''

    def __init__(self, friend: str):
        self.friend = friend
        super().__init__(
            f'拒绝向 {friend!r} 发送:收件人不在白名单 {sorted(ALLOWED_RECIPIENTS)} 内。\n'
            f'这是 pyweixin Linux 后端的安全硬规则(见 linux_auto.ALLOWED_RECIPIENTS),'
            f'不允许在运行时绕过。'
        )


def assert_allowed_recipient(friend: str) -> str:
    '''校验收件人并返回规范化后的名字;不合规立即抛 `RecipientNotAllowed`。'''
    if not isinstance(friend, str):
        raise RecipientNotAllowed(str(friend))
    name = friend.strip()
    if name not in ALLOWED_RECIPIENTS:
        raise RecipientNotAllowed(name)
    return name


def is_allowed_recipient(friend: str) -> bool:
    '''只判断不抛异常,便于调用方自己决定提示文案。'''
    return isinstance(friend, str) and friend.strip() in ALLOWED_RECIPIENTS


# --------------------------------------------------------------------------- #
# 主体
# --------------------------------------------------------------------------- #
class LinuxWeChat:
    '''一个绑定到某个 X display 的微信操作句柄。'''

    #: 消息类型的文本前缀(AT-SPI 没有 class_name,只能按 name 文本推断)
    _TYPE_PREFIXES = (
        ('[图片]', '图片'), ('[视频]', '视频'), ('[文件]', '文件'),
        ('[链接]', '链接'), ('[小程序]', '小程序'), ('[动画表情]', '动画表情'),
        ('[语音]', '语音'), ('[视频号]', '视频号'), ('[聊天记录]', '聊天记录'),
        ('[微信红包]', '微信红包'), ('[微信转账]', '微信转账'),
    )

    #: 只含时间的分割行,如 "20:20" / "昨天 08:08" / "2026年11月26日 20:20"
    _TIME_ONLY = re.compile(
        r'^(\d{1,2}:\d{2}|昨天\s*\d{1,2}:\d{2}|前天\s*\d{1,2}:\d{2}'
        r'|\d{4}年\d{1,2}月\d{1,2}日(\s*\d{1,2}:\d{2})?'
        r'|\d{1,2}月\d{1,2}日(\s*\d{1,2}:\d{2})?)$')

    def __init__(self, backend=None, dry_run: bool = False):
        self._backend = backend
        self.dry_run = dry_run

    # -- 惰性拿 backend,避免 import 时就要求有 DISPLAY -------------------- #
    @property
    def backend(self):
        if self._backend is None:
            from .platform import backend as get_backend
            self._backend = get_backend()
        return self._backend

    # -- 状态 ------------------------------------------------------------- #
    def main_window(self, timeout: float = 5.0):
        win = self.backend.main_window(timeout=timeout)
        if win is None:
            raise NotStartError()
        return win

    def is_logged_in(self) -> bool:
        return bool(self.backend.is_logged_in())

    def require_login(self) -> None:
        if not self.is_logged_in():
            raise NotLoginError(
                '微信当前停在登录界面。请先扫码登录;二维码可用 '
                '`wx.capture_login_qrcode(path)` 保存后人工扫描。')

    # -- 登录二维码 ------------------------------------------------------- #
    def capture_login_qrcode(self, path: str = 'qr_login.png') -> str:
        '''把登录窗口里的二维码区域截出来(纯截图,不解析二维码内容)。'''
        win = self.backend.login_window(timeout=5) or self.backend.main_window(timeout=2)
        if win is None:
            raise NotFoundError()
        rect = win.rectangle()
        # 二维码在登录窗口里居中偏上,占窗口宽度的 ~68%,这里按比例裁剪,
        # 不依赖任何控件坐标(不同版本布局会变)
        side = int(rect.width * 0.68)
        x = rect.left + (rect.width - side) // 2
        y = rect.top + int(rect.height * 0.14)
        self.backend.x11.screenshot(path, region=(x, y, side, side))
        return os.path.abspath(path)

    # -- 会话 ------------------------------------------------------------- #
    def _session_list(self):
        from .Uielements import Lists
        win = self.main_window()
        spec = win.child_window(**Lists.ConversationList)
        if not spec.exists(timeout=2):
            raise NotFoundError('找不到会话列表(AT-SPI 里没有 role=list, name=会话 的节点)')
        return spec

    def open_chat(self, friend: str):
        """按会话列表项的名字打开会话(名字匹配"备注\n最后一条消息\n时间"的首行)。

        幂等:目标会话已经打开时直接返回,不会重复点击(重复点击会把会话切走)。
        """
        name = assert_allowed_recipient(friend)
        if self.current_chat() == name:
            return None
        lst = self._session_list()
        for item in lst.children():
            if (item.window_text() or '').split('\n')[0].strip() == name:
                item.click_input()
                self._wait_chat_open(name)
                return item
        return self._open_chat_by_search(name)

    def _chat_frames(self):
        """已打开会话的"子窗口"。

        微信 4.x 在 Linux 上把聊天区渲染成一个**以会话标题命名的子 frame**
        (例如 `[frame] '文件传输助手'`),没有打开任何会话时这棵子树不存在。
        这个信号比"消息列表非空"可靠得多:空会话的消息列表本来就是空的。
        """
        win = self.main_window()
        snap = win.resolve()._snap
        # 微信 4.x 把每个已打开的会话渲染成一个独立的顶层 frame,名字就是会话标题;
        # 主窗口自己叫 微信/Weixin/WeChat,所以按名字把主窗口排除掉。
        return [n for n in snap.iter_nodes()
                if n.role in ('frame', 'window') and n.visible
                and (n.name or '') not in MAIN_WINDOW_TITLES]

    def current_chat(self) -> Optional[str]:
        """当前打开的会话标题;没有打开任何会话时返回 None。"""
        frames = self._chat_frames()
        if not frames:
            return None
        frames.sort(key=lambda n: n.w * n.h, reverse=True)
        return frames[0].name or None

    def _chat_spec(self):
        """当前会话所在的窗口(用于定位消息列表和输入框)。

        微信 4.x 在 Linux 上把聊天区做成**独立顶层 frame**,它不在主窗口的子树里。
        所以"从主窗口 child_window 找消息列表"必然失败 —— 必须从会话 frame 往下找。
        若某个版本确实是内嵌渲染(没有独立 frame),退回主窗口。
        """
        title = self.current_chat()
        if title:
            spec = self.backend.desktop().window(role='frame', title=title)
            if spec.exists():
                return spec
        return self.main_window()

    def _wait_chat_open(self, name: str, timeout: float = 8.0) -> None:
        """等目标会话真正打开(子 frame 标题 == 会话名)。"""
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.current_chat() == name:
                return
            time.sleep(0.25)
        raise NotFoundError(
            f'点击会话后没有打开 {name!r}(当前会话是 {self.current_chat()!r})')

    def _open_chat_by_search(self, name: str):
        from .Uielements import Main_window
        win = self.main_window()
        box = win.child_window(**Main_window.Search)
        if not box.exists(timeout=2):
            raise NotFoundError('找不到顶部搜索框')
        box.click_input()
        box.set_text(name)
        time.sleep(1.0)
        # 搜索结果列表:role=list 且第一个 list item 命中名字
        snap = win.resolve()._snap
        for node in snap.iter_nodes():
            if node.role != 'list item' or not node.visible:
                continue
            if name in (node.name or ''):
                self.backend.x11.click(node.rect.center.x, node.rect.center.y)
                time.sleep(0.6)
                return None
        raise ElementNotFound({'search': name})

    # -- 发送 ------------------------------------------------------------- #
    def _input_box(self):
        """定位聊天输入框。

        Linux 侧输入框的 AT-SPI 角色是 `text`,而且 **name 是当前会话标题**
        (不是占位符),所以不能靠 name 或 auto_id 定位。这里用两条判据:
            1. 必须在下半屏(排除顶部搜索框);
            2. 取面积最大的那个(聊天输入区 > 其它文本控件)。
        找不到才退化到 Windows 那套 `auto_id=chat_input_field` 的选择器。
        """
        win = self._chat_spec()
        snap = win.resolve()._snap
        rect = win.rectangle()
        half = rect.top + rect.height // 2
        cands = [n for n in snap.iter_nodes()
                 if n.role in ('text', 'entry', 'paragraph')
                 and n.visible and n.y >= half
                 and n.w > rect.width * 0.3]
        if cands:
            cands.sort(key=lambda n: n.w * n.h, reverse=True)
            node = cands[0]
            from .platform.linux.element import LinuxElement
            return LinuxElement(node, snap, self.backend.session, self.backend.x11)
        # 退化:Windows 风格选择器(部分版本会暴露 auto_id)
        from .Uielements import Main_window
        spec = win.child_window(**Main_window.EditArea)
        if spec.exists(timeout=2):
            return spec
        raise NotFoundError('找不到聊天输入框(下半屏没有可见的 text 控件)')

    def send_message(self, friend: str, message: str) -> dict:
        """向白名单内的会话发送一条文本消息,返回读回的那条记录。

        发送后一定**回读校验**:微信的"发送失败"是弹窗而不是异常,不发校验就
        会把失败当成功。校验失败时先关掉"发送失败"弹窗、清空输入框再重试一次。
        """
        name = assert_allowed_recipient(friend)
        if not isinstance(message, str) or message.strip() == '':
            raise ValueError('message 不能为空')
        self.require_login()
        self.open_chat(name)

        for attempt in (1, 2):
            self._compose_and_send(message)
            # 注意顺序:微信弹出"发送失败/我知道了"这类模态框时,整棵无障碍树的
            # 其它节点都会丢掉 SHOWING 状态(visible=False),此时读列表必然失败。
            # 所以必须先把弹窗关掉,再回读。
            self._dismiss_error_dialog()
            hit = self._read_back(message)
            if hit is not None:
                return hit
            if attempt == 1:
                self._clear_input()
                time.sleep(0.5)
        recent = [m['content'][:40] for m in self.read_messages(5)]
        raise RuntimeError(
            f'消息连续两次没有出现在会话里,判定发送失败。最近消息: {recent}')

    def _compose_and_send(self, message: str) -> None:
        box = self._input_box()
        box.set_focus()
        time.sleep(0.2)
        self.backend.x11.paste_text(message)
        time.sleep(0.25)
        self.backend.x11.key('Return')
        time.sleep(0.9)

    def _read_back(self, message: str) -> Optional[dict]:
        target = message.strip()
        for _ in range(3):
            try:
                for item in self.read_messages(8):
                    if target in item['content']:
                        return item
            except Exception:
                pass
            time.sleep(0.4)
        return None

    def _clear_input(self) -> None:
        """清空输入框。只在重试前用:先全选再删,避免残留内容被拼到新消息前面。"""
        try:
            box = self._input_box()
            box.set_focus()
            time.sleep(0.1)
            self.backend.x11.key('ctrl+a')
            time.sleep(0.05)
            self.backend.x11.key('BackSpace')
            time.sleep(0.1)
        except Exception:
            pass

    def _dismiss_error_dialog(self) -> None:
        """关掉"发送失败/我知道了"这类弹窗(它们会阻塞后续的 UI 交互)。"""
        try:
            snap = self.main_window().resolve()._snap
        except Exception:
            return
        for node in snap.iter_nodes():
            if node.role in ('button', 'push button') and (node.name or '') == '我知道了':
                self.backend.x11.click(node.rect.center.x, node.rect.center.y)
                time.sleep(0.6)
                return

    # -- 读取 ------------------------------------------------------------- #
    def _message_list(self):
        from .Uielements import Lists
        for anchor in (self._chat_spec(), self.main_window()):
            spec = anchor.child_window(**Lists.FriendChatList)
            if spec.exists(timeout=2):
                return spec
        raise NotFoundError('找不到消息列表(role=list, name=消息)')

    @classmethod
    def _classify(cls, content: str) -> str:
        for prefix, kind in cls._TYPE_PREFIXES:
            if content.startswith(prefix):
                return kind
        return '文本'

    def read_messages(self, count: int = 10) -> list[dict]:
        '''读取当前会话最近 `count` 条消息。

        AT-SPI 里消息列表项没有 `class_name`,只能靠文本前缀推断类型;
        发送者是否是自己无法从树里区分,这里统一给 `sender=None`,
        由上层的业务逻辑按内容判断。
        '''
        if count <= 0:
            return []
        lst = self._message_list()
        items = lst.children()
        out = []
        for el in items:
            text = (el.window_text() or '').strip()
            # 消息列表里混着"20:20""昨天 08:08""2026年11月26日"这类时间分割行,
            # 它们不是消息,过滤掉(pywinauto 侧靠 class_name 判断,这里只能靠文本)
            if not text or self._TIME_ONLY.match(text):
                continue
            out.append({'sender': None, 'content': text,
                        'type': self._classify(text), 'role': el.role})
        return out[-count:] if count else out

    # -- 截图 ------------------------------------------------------------- #
    def screenshot(self, path: str) -> str:
        return self.backend.screenshot(path)


# --------------------------------------------------------------------------- #
# 模块级便捷函数(单例)
# --------------------------------------------------------------------------- #
_default: Optional[LinuxWeChat] = None


def client() -> LinuxWeChat:
    global _default
    if _default is None:
        _default = LinuxWeChat()
    return _default


def is_logged_in() -> bool:
    return client().is_logged_in()


def open_chat(friend: str):
    return client().open_chat(friend)


def send_message(friend: str, message: str) -> None:
    return client().send_message(friend, message)


def read_messages(count: int = 10) -> list[dict]:
    return client().read_messages(count)


def capture_login_qrcode(path: str = 'qr_login.png') -> str:
    return client().capture_login_qrcode(path)
