'''
pyweixin.platform.windows
=========================
Windows 后端:直接透传 pywinauto,行为与移植前**完全一致**。

这一层的意义不是重写,而是给上层一个统一的入口:任何走
`pyweixin.platform.backend()` 的代码在 Windows 上拿到的仍然是原生的
`WindowSpecification` / `UIAWrapper`,因此现有 300+ 处 `child_window`` /
`click_input` 调用不需要任何改动。
'''
from __future__ import annotations

import os
from typing import Any, Optional

from ..base import PlatformNotSupported


class WindowsBackend:
    '''把 pywinauto 包装成 `Backend` 协议。'''

    name = 'windows'

    def __init__(self, pywinauto_backend: str = 'uia'):
        self._backend = pywinauto_backend
        self._desktop = None

    # -- pywinauto --------------------------------------------------------- #
    @staticmethod
    def require_pywinauto():
        try:
            import pywinauto  # noqa: F401
        except Exception as exc:
            raise PlatformNotSupported(
                'pywinauto', 'windows: 未安装 pywinauto,请 pip install pywinauto pywin32'
            ) from exc
        return pywinauto

    def desktop(self):
        if self._desktop is None:
            pywinauto = self.require_pywinauto()
            self._desktop = pywinauto.Desktop(backend=self._backend)
        return self._desktop

    # -- Backend 协议 ------------------------------------------------------ #
    def attach(self, name: Optional[str] = None):
        self.require_pywinauto()
        from pyweixin.WeChatTools import Tools
        hwnd = Tools.get_weixin_hwnd()
        if not hwnd:
            return None
        return self.desktop().window(handle=hwnd)

    def launch(self, path: Optional[str] = None, args: tuple = ()):
        target = path or self.wechat_path()
        if not target:
            raise PlatformNotSupported('启动微信', 'windows: 找不到微信可执行文件')
        os.startfile(target)  # noqa: S606 - Windows 专有
        return self.attach()

    def wechat_path(self) -> Optional[str]:
        try:
            from pyweixin.WeChatTools import Tools
            return Tools.where_weixin()
        except Exception:
            return None
