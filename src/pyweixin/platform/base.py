'''
platform.base
=============
平台抽象层的最小契约。

pyweixin 原本是围绕 pywinauto(Windows UIAutomation) 写的,`WeChatAuto` 里几乎所有
操作最终都落到 `WindowSpecification` / `UIAWrapper` 的这些方法上:

    child_window / children / window_text / class_name / automation_id /
    click_input / double_click_input / right_click_input / type_keys / set_text /
    exists / wait / is_selected / is_visible / close / rectangle / element_info

本模块把这些能力抽象成与操作系统无关的接口。`platform.windows` 直接透传
pywinauto(行为零改动),`platform.linux` 用 AT-SPI + XTest 重新实现同一套语义。

坐标
----
所有坐标均为**物理屏幕像素**,且 AT-SPI 上报的逻辑坐标已按屏幕 DPI 归一化
(见 `linux.element.LinuxElement.rect`)。Xvfb 请用 `-dpi 96` 启动以保证 1:1。
'''
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator, NamedTuple, Optional, Protocol, Sequence, runtime_checkable


class PlatformNotSupported(NotImplementedError):
    '''当前平台不支持该能力。'''

    def __init__(self, feature: str, platform: str = ''):
        self.feature = feature
        self.platform = platform
        super().__init__(
            f'[pyweixin] 能力 {feature!r} 在当前平台 {platform or "unknown"!r} 上尚未实现。'
        )


class UnsupportedSelector(PlatformNotSupported):
    '''选择器里只包含 Windows 专有字段(如 class_name / auto_id),Linux 侧无法匹配。'''

    def __init__(self, selector: dict, reasons: str = ''):
        self.selector = selector
        self.reasons = reasons
        super().__init__(f'选择器 {selector!r} 无法翻译到 AT-SPI'
                         + (f' ({reasons})' if reasons else ''))


class ElementNotFound(LookupError):
    def __init__(self, selector: dict | None = None):
        self.selector = selector
        super().__init__(f'未找到匹配的 UI 元素: {selector!r}')


class Point(NamedTuple):
    '''屏幕点。用 NamedTuple 是为了既能 `p.x/p.y`,也能 `x, y = p`。'''

    x: int
    y: int


@dataclass(frozen=True)
class Rect:
    '''与 pywinauto 的 `Rect` 保持字段一致,方便上层代码原样迁移。'''

    left: int
    top: int
    width: int
    height: int

    @property
    def right(self) -> int:
        return self.left + self.width

    @property
    def bottom(self) -> int:
        return self.top + self.height

    @property
    def center(self) -> Point:
        return Point(self.left + self.width // 2, self.top + self.height // 2)

    def mid_point(self) -> Point:
        return self.center

    def is_empty(self) -> bool:
        return self.width <= 0 or self.height <= 0

    def __contains__(self, p: Point) -> bool:
        return self.left <= p.x < self.right and self.top <= p.y < self.bottom


@runtime_checkable
class UIElement(Protocol):
    '''一个 UI 元素。语义与 pywinauto 的 `UIAWrapper` 子集对齐。'''

    @property
    def role(self) -> str: ...
    def window_text(self) -> str: ...
    def class_name(self) -> str: ...
    def automation_id(self) -> str: ...
    def rectangle(self) -> Rect: ...
    def is_visible(self) -> bool: ...
    def is_selected(self) -> bool: ...
    def children(self, **criteria: Any) -> list['UIElement']: ...
    def child_window(self, **criteria: Any) -> 'UIElement': ...
    def descendants(self, **criteria: Any) -> list['UIElement']: ...
    def exists(self, timeout: float = 0.0) -> bool: ...
    def wait(self, wait_for: str = 'exists', timeout: float = 5.0) -> 'UIElement': ...
    def click_input(self, coords: tuple[int, int] | None = None) -> None: ...
    def double_click_input(self, coords: tuple[int, int] | None = None) -> None: ...
    def right_click_input(self, coords: tuple[int, int] | None = None) -> None: ...
    def type_keys(self, keys: str, pause: float | None = None) -> None: ...
    def set_text(self, text: str) -> None: ...
    def close(self) -> None: ...


@runtime_checkable
class Backend(Protocol):
    '''一个平台的驱动。'''

    name: str

    def desktop(self) -> Any: ...
    def attach(self, name: str | None = None) -> Optional[UIElement]: ...
    def launch(self, path: str | None = None, args: Sequence[str] = ()) -> Optional[UIElement]: ...


class ElementInfo:
    '''`element_info` 的替身,提供 `control_type` / `rectangle` / `runtime_id`。'''

    def __init__(self, control_type: str, rectangle: Rect, runtime_id: Any = None,
                 name: str = '', automation_id: str = '', class_name: str = ''):
        self.control_type = control_type
        self.rectangle = rectangle
        self.runtime_id = runtime_id
        self.name = name
        self.automation_id = automation_id
        self.class_name = class_name

    def __repr__(self) -> str:
        return (f'ElementInfo(control_type={self.control_type!r}, '
                f'rectangle={self.rectangle!r})')


def iter_depth_first(elements: Sequence[UIElement]) -> Iterator[tuple[int, UIElement]]:
    '''按深度优先顺序遍历,返回 (深度, 元素)。'''
    stack = [(0, e) for e in reversed(list(elements))]
    while stack:
        depth, el = stack.pop()
        yield depth, el
        try:
            kids = el.children()
        except Exception:
            kids = []
        for k in reversed(kids):
            stack.append((depth + 1, k))
