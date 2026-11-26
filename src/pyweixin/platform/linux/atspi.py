'''
platform.linux.atspi
====================
AT-SPI2 的低层访问:连总线、取快照(整棵无障碍树)。

为什么是"快照"
--------------
AT-SPI 的对象路径(`/org/a11y/atspi/accessible/<id>`)每次 UI 重建都会变,
缓存单个节点引用非常容易拿到已失效的路径。因此这里**一次性遍历整棵树**,
把 role / name / 坐标 / 状态全部读出来放进 `Node`,之后所有查询都在快照上做。
一次全量遍历(微信主界面约 1000 个节点)在本机约 0.3-0.6 秒。

约定
----
* 只读遍历(`GetChildren` / `GetRoleName` / `GetName` / `GetExtents` / `GetStateSet`)。
* **绝不调用 `Action.DoAction`**:微信的侧边栏等控件是自绘控件,只有 role 没有
  `QAccessibleActionInterface`,Qt 的 Action adaptor 会在空指针上解引用导致主进程
  SIGSEGV。点击一律走 XTest(见 `x11.py`)。
'''
from __future__ import annotations

import os
import time
from typing import Iterator, Optional

from ..base import Rect

#: AT-SPI role -> 中文/通用语义别名(仅用于日志与文档)
_ROLE_ALIASES = {
    'push button': 'button',
    'list item': 'listitem',
    'check box': 'checkbox',
}


class AtspiUnavailable(RuntimeError):
    '''无障碍总线不可用(没装 at-spi2、没开 toolkit-accessibility、或没有会话总线)。'''

    HINT = (
        '无法连接 AT-SPI 总线。请确认:\n'
        '  1) 已安装 at-spi2-core 与 python-gobject;\n'
        '  2) 存在 D-Bus 会话总线(DBUS_SESSION_BUS_ADDRESS);\n'
        '  3) `busctl --user call org.a11y.Bus /org/a11y/bus org.a11y.Bus.GetAddress` 有返回;\n'
        '  4) 微信进程带 QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1 启动(或桌面已开\n'
        '     gsettings set org.gnome.desktop.interface toolkit-accessibility true)。'
    )

    def __init__(self, detail: str = ''):
        super().__init__(f'{detail}\n{self.HINT}' if detail else self.HINT)


class Node:
    '''快照里的一个节点。只存纯数据 + 一个可选的 Atspi 代理(用于取正文)。'''

    __slots__ = ('index', 'role', 'name', 'x', 'y', 'w', 'h', 'depth',
                 'parent', 'children', 'showing', 'sensitive', 'selected',
                 'obj')

    def __init__(self, index, role, name, x, y, w, h, depth, parent, obj,
                 showing=False, sensitive=True, selected=False):
        self.index = index
        self.role = role
        self.name = name
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.depth = depth
        self.parent = parent
        self.children: list[int] = []
        self.showing = showing
        self.sensitive = sensitive
        self.selected = selected
        self.obj = obj

    @property
    def rect(self) -> Rect:
        return Rect(self.x, self.y, self.w, self.h)

    @property
    def visible(self) -> bool:
        return self.showing and self.w > 0 and self.h > 0

    def __repr__(self) -> str:
        return (f'Node(#{self.index} role={self.role!r} name={self.name!r} '
                f'@{self.x},{self.y} {self.w}x{self.h})')


class Snapshot:
    '''某一时刻某应用的整棵无障碍树。'''

    def __init__(self, app_name: str, nodes: list[Node], scale: float = 1.0,
                 taken_at: float = None):
        self.app_name = app_name
        self.nodes = nodes
        self.scale = scale
        self.taken_at = time.time() if taken_at is None else taken_at

    # -- 查询 ------------------------------------------------------------- #
    @property
    def root(self) -> Node:
        return self.nodes[0]

    def get(self, index: int) -> Node:
        return self.nodes[index]

    def iter_nodes(self) -> Iterator[Node]:
        # 跳过根(application)本身
        for n in self.nodes[1:]:
            yield n

    def children_of(self, node: Node) -> list[Node]:
        return [self.nodes[i] for i in node.children]

    def find(self, match, root: Optional[Node] = None, max_depth: Optional[int] = None,
             visible_only: bool = False, hits: Optional[list] = None) -> list[Node]:
        '''广度优先查找所有满足 `match(role, name)` 的节点。'''
        out: list[Node] = [] if hits is None else hits
        start = self.root if root is None else root
        queue = [start]
        base_depth = start.depth
        while queue:
            n = queue.pop(0)
            if n is not start and match(n.role, n.name):
                if not visible_only or n.visible:
                    out.append(n)
            if max_depth is not None and (n.depth - base_depth) >= max_depth:
                continue
            queue.extend(self.nodes[i] for i in n.children)
        return out

    def find_first(self, match, root: Optional[Node] = None,
                   visible_only: bool = False) -> Optional[Node]:
        hits = self.find(match, root=root, visible_only=visible_only)
        return hits[0] if hits else None

    def path_to_root(self, node: Node) -> list[Node]:
        out = [node]
        while node.parent is not None:
            node = self.nodes[node.parent]
            out.append(node)
        return out


# --------------------------------------------------------------------------- #
# 会话
# --------------------------------------------------------------------------- #
class AtspiSession:
    '''AT-SPI 连接 + 快照缓存。'''

    def __init__(self, cache_ttl: float = 0.30):
        self._Atspi = None
        self.cache_ttl = cache_ttl
        self._cache: dict[str, Snapshot] = {}
        self._scale: Optional[float] = None

    # -- 惰性导入,避免 import pyweixin 时就要求装 gobject ------------------ #
    @property
    def Atspi(self):
        if self._Atspi is None:
            try:
                import gi
                gi.require_version('Atspi', '2.0')
                from gi.repository import Atspi
            except Exception as exc:  # pragma: no cover - 环境相关
                raise AtspiUnavailable(f'导入 Atspi 失败: {exc}') from exc
            try:
                Atspi.init()
            except Exception as exc:  # pragma: no cover
                raise AtspiUnavailable(f'Atspi.init() 失败: {exc}') from exc
            self._Atspi = Atspi
        return self._Atspi

    # -- 缩放 ------------------------------------------------------------- #
    @property
    def scale(self) -> float:
        '''AT-SPI 逻辑坐标 -> 物理像素 的比例。

        Xvfb 默认按屏幕毫米数算出 100 DPI,而 AT-SPI 以 96 DPI 为基准上报,
        于是逻辑坐标 = 物理 * 96/100。启动 Xvfb 时加 `-dpi 96` 可让它等于 1;
        真实桌面上可以用 `PYWEIXIN_ATSPI_SCALE` 覆盖。
        '''
        if self._scale is not None:
            return self._scale
        env = os.environ.get('PYWEIXIN_ATSPI_SCALE')
        if env:
            try:
                self._scale = float(env)
                return self._scale
            except ValueError:
                pass
        self._scale = 1.0
        return self._scale

    def calibrate(self, x_window_size: tuple[int, int],
                  atspi_size: tuple[int, int]) -> float:
        '''用同一个窗口的 X 尺寸 / AT-SPI 尺寸反推缩放比。'''
        aw, ah = atspi_size
        xw, xh = x_window_size
        if aw > 0 and ah > 0 and xw > 0 and xh > 0:
            ratio = (xw / aw + xh / ah) / 2.0
            if abs(ratio - 1.0) > 0.005:
                self._scale = round(ratio, 4)
                return self._scale
        self._scale = 1.0
        return self._scale

    # -- 应用 ------------------------------------------------------------- #
    def applications(self) -> list[str]:
        Atspi = self.Atspi
        desktop = Atspi.get_desktop(0)
        names = []
        for i in range(desktop.get_child_count()):
            app = desktop.get_child_at_index(i)
            if app is None:
                continue
            names.append(app.get_name() or '')
        return names

    def snapshot(self, app_name: str, force: bool = False) -> Snapshot:
        '''取某个应用的整棵树。`app_name` 为 AT-SPI 里的 application 名。'''
        now = time.time()
        cached = self._cache.get(app_name)
        if cached is not None and not force and (now - cached.taken_at) < self.cache_ttl:
            return cached
        Atspi = self.Atspi
        desktop = Atspi.get_desktop(0)
        app = None
        for i in range(desktop.get_child_count()):
            cand = desktop.get_child_at_index(i)
            if cand is not None and (cand.get_name() or '') == app_name:
                app = cand
                break
        if app is None:
            raise AtspiUnavailable(f'无障碍总线上找不到应用 {app_name!r} '
                                   f'(当前有: {self.applications()!r})')

        nodes: list[Node] = []
        scale = self.scale

        def role_name(obj) -> str:
            try:
                return obj.get_role_name() or ''
            except Exception:
                return ''

        def node_name(obj) -> str:
            try:
                return obj.get_name() or ''
            except Exception:
                return ''

        def extents(obj):
            try:
                e = obj.get_extents(Atspi.CoordType.SCREEN)
                return (e.x, e.y, e.width, e.height)
            except Exception:
                return (0, 0, 0, 0)

        def states(obj):
            try:
                st = obj.get_state_set()
                return (st.contains(Atspi.StateType.SHOWING),
                        st.contains(Atspi.StateType.SENSITIVE),
                        st.contains(Atspi.StateType.SELECTED))
            except Exception:
                return (False, True, False)

        def make(obj, depth, parent) -> int:
            # 物理像素:AT-SPI 上报的是 96 DPI 逻辑坐标
            x, y, w, h = extents(obj)
            if scale != 1.0:
                x, y, w, h = (int(round(x * scale)), int(round(y * scale)),
                              int(round(w * scale)), int(round(h * scale)))
            showing, sensitive, selected = states(obj)
            idx = len(nodes)
            nodes.append(Node(idx, role_name(obj), node_name(obj), x, y, w, h,
                              depth, parent, obj, showing, sensitive, selected))
            return idx

        root_idx = make(app, 0, None)
        # 显式栈,避免递归过深
        stack = [(app, root_idx, 1)]
        while stack:
            obj, parent_idx, depth = stack.pop()
            try:
                count = obj.get_child_count()
            except Exception:
                continue
            for i in range(count):
                try:
                    child = obj.get_child_at_index(i)
                except Exception:
                    continue
                if child is None:
                    continue
                idx = make(child, depth, parent_idx)
                nodes[parent_idx].children.append(idx)
                stack.append((child, idx, depth + 1))

        snap = Snapshot(app_name, nodes, scale=scale)
        self._cache[app_name] = snap
        return snap

    def invalidate(self, app_name: Optional[str] = None) -> None:
        if app_name is None:
            self._cache.clear()
        else:
            self._cache.pop(app_name, None)
