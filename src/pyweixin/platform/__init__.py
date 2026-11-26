'''
pyweixin.platform
=================
平台抽象层。上层代码通过 `backend()` 拿到当前平台的驱动,不再直接依赖
pywinauto / win32api。

约定
----
* `Backend.name` : 'windows' | 'linux'
* `Backend.desktop()` : 返回一个"桌面"对象,支持 `.window(**criteria)`
* `Backend.attach()` / `Backend.launch()` : 附着或启动微信,返回窗口对象

Linux 后端能力与限制见 `docs/LINUX.md`。
'''
from __future__ import annotations

import sys
from typing import Optional

from .base import (Backend, ElementInfo, ElementNotFound, PlatformNotSupported,
                   Point, Rect, UnsupportedSelector, UIElement)
from .selector import (CLASS_NAME_ROLES, CONTROL_TYPE_ROLES, Selector,
                       normalize_role, translate, translate_all)

__all__ = [
    'backend', 'current_platform', 'reset_backend',
    'Backend', 'ElementInfo', 'ElementNotFound', 'PlatformNotSupported',
    'Point', 'Rect', 'UnsupportedSelector', 'UIElement',
    'Selector', 'translate', 'translate_all', 'normalize_role',
    'CLASS_NAME_ROLES', 'CONTROL_TYPE_ROLES',
]

_backend_instance = None


def current_platform() -> str:
    '''返回 'windows' / 'linux' / 'darwin'。'''
    if sys.platform.startswith('win'):
        return 'windows'
    if sys.platform.startswith('linux'):
        return 'linux'
    if sys.platform == 'darwin':
        return 'darwin'
    return sys.platform


def backend(force: Optional[str] = None):
    '''拿到当前平台的驱动(单例)。

    :param force: 强制指定 'linux' / 'windows',便于测试与交叉调试。
    '''
    global _backend_instance
    platform = force or current_platform()
    if _backend_instance is not None and _backend_instance.name == platform:
        return _backend_instance
    if platform == 'linux':
        from .linux import LinuxBackend
        _backend_instance = LinuxBackend()
    elif platform == 'windows':
        from .windows import WindowsBackend
        _backend_instance = WindowsBackend()
    else:
        raise PlatformNotSupported('UI 自动化', platform)
    return _backend_instance


def reset_backend() -> None:
    '''清掉单例(测试用)。'''
    global _backend_instance
    _backend_instance = None
