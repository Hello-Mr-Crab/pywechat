'''
pyweixin.platform.linux
=======================
Linux 后端:AT-SPI2(读) + XTest(写) + ffmpeg(截图)。

用法::

    from pyweixin.platform import backend
    be = backend()                      # LinuxBackend
    win = be.main_window()              # 微信主窗口
    chat = win.child_window(control_type='List', title='会话')
    print([c.window_text() for c in chat.children()[:5]])

安全约束
--------
* **只读**使用 AT-SPI(`GetChildren`/`GetRoleName`/`GetName`/`GetExtents`)。
* 绝不调用 `Action.DoAction` —— 微信自绘控件上会让主进程 SIGSEGV。
* 绝不注入进程、不读写注册表、不逆向闭源二进制;所有"写"操作走内核 XTest。
'''
from .atspi import AtspiSession, AtspiUnavailable, Node, Snapshot
from .driver import (LinuxBackend, LinuxDesktop, find_wechat_binary,
                     is_wechat_running, launch_wechat, wechat_env)
from .element import ImageHandle, LinuxElement, LinuxWindowSpecification
from .x11 import X11, X11Unavailable

__all__ = [
    'AtspiSession', 'AtspiUnavailable', 'Node', 'Snapshot',
    'LinuxBackend', 'LinuxDesktop', 'find_wechat_binary', 'is_wechat_running',
    'launch_wechat', 'wechat_env',
    'ImageHandle', 'LinuxElement', 'LinuxWindowSpecification',
    'X11', 'X11Unavailable',
]
