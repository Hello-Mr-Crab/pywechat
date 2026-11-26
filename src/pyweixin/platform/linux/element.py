'''
platform.linux.element
======================
AT-SPI 元素,以及一个 pywinauto 风格的"惰性定位器"。

`LinuxWindowSpecification` 对应 pywinauto 的 `WindowSpecification`:
它只保存"怎么找",不保存"找到了谁"。每次真正要操作时才重新遍历一次无障碍树
并解析到具体节点 —— 这样才能容忍 AT-SPI 对象路径的频繁失效。

`LinuxElement` 对应 `UIAWrapper`:一个已经解析到、且只在一个快照内有效的元素。
'''
from __future__ import annotations

import time
from typing import Any, Optional

from ..base import ElementInfo, ElementNotFound, PlatformNotSupported, Rect
from ..selector import Selector, translate
from .atspi import Node, Snapshot, AtspiSession


class ImageHandle:
    '''`capture_as_image()` 的返回值。没有装 Pillow 时也能 `.save()`。'''

    def __init__(self, path: str):
        self.path = path

    def save(self, path: str) -> str:
        if path == self.path:
            return path
        import shutil
        shutil.copyfile(self.path, path)
        return path

    def __repr__(self) -> str:
        return f'ImageHandle({self.path!r})'


def _criteria_to_selector(criteria: dict) -> Selector:
    return translate(criteria)


def _visible_flag(criteria: dict) -> bool:
    return bool(criteria.get('visible_only', True))


class LinuxElement:
    '''一个已解析的元素。所有坐标都是物理屏幕像素。'''

    def __init__(self, node: Node, snap: Snapshot, session: AtspiSession,
                 x11, locator: Optional['LinuxWindowSpecification'] = None):
        self._node = node
        self._snap = snap
        self._session = session
        self._x11 = x11
        self._locator = locator

    # -- 基本信息 --------------------------------------------------------- #
    @property
    def role(self) -> str:
        return self._node.role

    @property
    def name(self) -> str:
        return self._node.name

    @property
    def node(self) -> Node:
        return self._node

    def window_text(self) -> str:
        return self._node.name

    def class_name(self) -> str:
        '''AT-SPI 没有 `class_name`。保留该方法是为了让上层代码无需修改即可运行;
        依赖类名区分控件的地方请改用 `role` / `name`(见 docs/LINUX.md)。'''
        return ''

    def automation_id(self) -> str:
        return ''

    def text(self) -> str:
        '''取控件正文。Qt 的 label / list item 通常把正文放在 `name` 里。'''
        if self._node.obj is None:
            return self._node.name
        try:
            txt = self._node.obj.get_text()
            if txt:
                return txt
        except Exception:
            pass
        try:
            return self._node.obj.get_text(0)
        except Exception:
            return self._node.name

    def rectangle(self) -> Rect:
        return self._node.rect

    def is_visible(self) -> bool:
        return self._node.visible

    def is_selected(self) -> bool:
        return bool(self._node.selected)

    @property
    def element_info(self) -> ElementInfo:
        return ElementInfo(control_type=self._node.role,
                           rectangle=self._node.rect,
                           runtime_id=self._node.index,
                           name=self._node.name)

    # -- 导航 ------------------------------------------------------------- #
    def children(self, **criteria: Any) -> list['LinuxElement']:
        kids = self._snap.children_of(self._node)
        if not criteria:
            return [LinuxElement(k, self._snap, self._session, self._x11) for k in kids]
        sel = _criteria_to_selector(criteria)
        visible_only = _visible_flag(criteria)
        return [LinuxElement(k, self._snap, self._session, self._x11)
                for k in kids
                if (not visible_only or k.visible) and sel.match(k.role, k.name)]

    def descendants(self, **criteria: Any) -> list['LinuxElement']:
        sel = _criteria_to_selector(criteria)
        visible_only = _visible_flag(criteria)
        hits = self._snap.find(sel.match, root=self._node, visible_only=visible_only)
        return [LinuxElement(h, self._snap, self._session, self._x11) for h in hits]

    def child_window(self, **criteria: Any) -> 'LinuxWindowSpecification':
        return LinuxWindowSpecification(self._session, self._x11, criteria,
                                        anchor=self._node, app_name=self._snap.app_name,
                                        snap=self._snap)

    def exists(self, timeout: float = 0.0) -> bool:
        return True

    def wait(self, wait_for: str = 'exists', timeout: float = 5.0) -> 'LinuxElement':
        return self

    # -- 动作 ------------------------------------------------------------- #
    def move_mouse(self) -> tuple[int, int]:
        p = self._node.rect.center
        self._x11.move(p.x, p.y)
        return p.x, p.y

    def click_input(self, coords: Optional[tuple[int, int]] = None) -> None:
        if coords is not None:
            x, y = int(coords[0]), int(coords[1])
        else:
            x, y = self._node.rect.center
        self._x11.click(x, y)

    def double_click_input(self, coords: Optional[tuple[int, int]] = None) -> None:
        if coords is not None:
            x, y = int(coords[0]), int(coords[1])
        else:
            x, y = self._node.rect.center
        self._x11.double_click(x, y)

    def right_click_input(self, coords: Optional[tuple[int, int]] = None) -> None:
        if coords is not None:
            x, y = int(coords[0]), int(coords[1])
        else:
            x, y = self._node.rect.center
        self._x11.click(x, y, button=3)

    def set_focus(self) -> None:
        '''优先用 AT-SPI 的 `Component.grab_focus`(不产生鼠标事件,不会误点)。'''
        obj = self._node.obj
        if obj is not None:
            try:
                obj.grab_focus()
                return
            except Exception:
                pass
        x, y = self._node.rect.center
        self._x11.click(x, y)

    def type_keys(self, keys: str, pause: Optional[float] = None,
                  with_newlines: bool = True) -> None:
        self.set_focus()
        time.sleep(0.05)
        self._x11.type_keys(keys, pause=pause or 0.0)

    def send_keys(self, keys: str, pause: Optional[float] = None) -> None:
        self.type_keys(keys, pause=pause)

    def set_text(self, text: str) -> None:
        '''清空并写入。中文走剪贴板(输入法不经过 XTEST,逐字输入不可靠)。'''
        self.set_focus()
        time.sleep(0.05)
        self._x11.key('ctrl+a')
        time.sleep(0.03)
        if text:
            self._x11.paste_text(text)
        else:
            self._x11.key('BackSpace')

    def press_enter(self) -> None:
        self.set_focus()
        self._x11.key('Return')

    def close(self) -> None:
        '''点窗口右上角的「关闭」。找不到就什么也不做(绝不 kill 进程)。'''
        try:
            btn = self.child_window(control_type='Button', title='关闭').resolve()
            btn.click_input()
        except ElementNotFound:
            pass

    def capture_as_image(self, path: Optional[str] = None) -> ImageHandle:
        rect = self._node.rect
        if path is None:
            path = f'/tmp/pyweixin-capture-{self._node.index}.png'
        self._x11.screenshot(path, region=(rect.left, rect.top, rect.width, rect.height))
        return ImageHandle(path)

    # -- 其它 ------------------------------------------------------------- #
    def top_level_parent(self) -> 'LinuxElement':
        root = self._snap.root
        for n in reversed(self._snap.path_to_root(self._node)):
            if n.role in ('frame', 'dialog', 'window'):
                return LinuxElement(n, self._snap, self._session, self._x11)
        return LinuxElement(root, self._snap, self._session, self._x11)

    def __bool__(self) -> bool:
        return True

    def __repr__(self) -> str:
        n = self._node
        return f'<LinuxElement {n.role!r} {n.name!r} @{n.x},{n.y} {n.w}x{n.h}>'


class LinuxWindowSpecification:
    '''惰性定位器:等价于 pywinauto 的 `WindowSpecification`。

    它不复用旧快照,而是在每次解析时按需重新遍历无障碍树(必要时由调用方用
    `bind()` 显式绑定同一个快照,以便在一次操作里做多次查询)。
    '''

    __slots__ = ('_session', '_x11', '_criteria', '_anchor', '_snap', '_app_name')

    def __init__(self, session: AtspiSession, x11, criteria: Optional[dict] = None,
                 anchor: Optional[Node] = None, app_name: Optional[str] = None,
                 snap: Optional[Snapshot] = None):
        self._session = session
        self._x11 = x11
        self._criteria = dict(criteria or {})
        self._anchor = anchor
        self._snap = snap
        self._app_name = app_name

    # -- 解析 ------------------------------------------------------------- #
    def bind(self, snap: Snapshot) -> 'LinuxWindowSpecification':
        '''绑定到一个已存在的快照(避免同一操作里反复全量遍历)。'''
        return LinuxWindowSpecification(self._session, self._x11, self._criteria,
                                        anchor=self._anchor, app_name=snap.app_name,
                                        snap=snap)

    def _snapshot(self) -> Snapshot:
        if self._snap is not None:
            return self._snap
        if not self._app_name:
            raise ElementNotFound(self._criteria)
        return self._session.snapshot(self._app_name)

    def resolve(self, timeout: float = 0.0, refresh: bool = False) -> LinuxElement:
        '''解析到具体元素;找不到抛 `ElementNotFound`。'''
        deadline = time.time() + max(timeout, 0.0)
        while True:
            try:
                return self._resolve_once(refresh=refresh)
            except ElementNotFound:
                if time.time() >= deadline:
                    raise
                refresh = True
                time.sleep(0.15)

    def _resolve_once(self, refresh: bool = False) -> LinuxElement:
        if refresh and self._app_name:
            self._session.invalidate(self._app_name)
            self._snap = None
        snap = self._snapshot()
        anchor = self._anchor if self._anchor is not None else snap.root
        found_index = int(self._criteria.get('found_index', 0) or 0)
        search_criteria = {k: v for k, v in self._criteria.items() if k != 'found_index'}
        if not search_criteria:
            hits = [anchor]
        else:
            sel = _criteria_to_selector(search_criteria)
            visible_only = _visible_flag(self._criteria)
            hits = snap.find(sel.match, root=anchor, visible_only=visible_only)
        if len(hits) <= found_index:
            raise ElementNotFound(self._criteria)
        return LinuxElement(hits[found_index], snap, self._session, self._x11, locator=self)

    # -- pywinauto 兼容 API ----------------------------------------------- #
    def exists(self, timeout: float = 0.0) -> bool:
        try:
            self.resolve(timeout=timeout)
            return True
        except (ElementNotFound, PlatformNotSupported):
            return False

    def wait(self, wait_for: str = 'exists', timeout: float = 5.0):
        if wait_for not in ('exists', 'visible', 'ready', 'enabled'):
            raise PlatformNotSupported(f'wait(wait_for={wait_for!r})')
        return self.resolve(timeout=timeout)

    def children(self, **criteria: Any) -> list[LinuxElement]:
        return self.resolve().children(**criteria)

    def descendants(self, **criteria: Any) -> list[LinuxElement]:
        return self.resolve().descendants(**criteria)

    def child_window(self, **criteria: Any) -> 'LinuxWindowSpecification':
        el = self.resolve()
        return LinuxWindowSpecification(self._session, self._x11, criteria,
                                        anchor=el.node, app_name=el._snap.app_name,
                                        snap=el._snap)

    def window_text(self) -> str:
        return self.resolve().window_text()

    def class_name(self) -> str:
        return ''

    def automation_id(self) -> str:
        return ''

    def rectangle(self) -> Rect:
        return self.resolve().rectangle()

    def is_visible(self) -> bool:
        return self.exists()

    def is_selected(self) -> bool:
        return self.resolve().is_selected()

    @property
    def element_info(self) -> ElementInfo:
        return self.resolve().element_info

    @property
    def node(self) -> Node:
        return self.resolve().node

    def click_input(self, coords=None) -> None:
        self.resolve().click_input(coords)

    def double_click_input(self, coords=None) -> None:
        self.resolve().double_click_input(coords)

    def right_click_input(self, coords=None) -> None:
        self.resolve().right_click_input(coords)

    def set_focus(self) -> None:
        self.resolve().set_focus()

    def type_keys(self, keys: str, pause=None) -> None:
        self.resolve().type_keys(keys, pause=pause)

    def send_keys(self, keys: str, pause=None) -> None:
        self.resolve().type_keys(keys, pause=pause)

    def set_text(self, text: str) -> None:
        self.resolve().set_text(text)

    def press_enter(self) -> None:
        self.resolve().press_enter()

    def close(self) -> None:
        self.resolve().close()

    def capture_as_image(self, path: Optional[str] = None) -> ImageHandle:
        return self.resolve().capture_as_image(path)

    def __bool__(self) -> bool:
        return self.exists()

    def __repr__(self) -> str:
        return f'<LinuxWindowSpecification {self._criteria!r}>'
