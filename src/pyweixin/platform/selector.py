'''
platform.selector
=================
把 pywinauto / UIAutomation 风格的 `**kwargs` 选择器翻译成平台无关的判据。

`pyweixin/Uielements.py` 里的选择器表长这样::

    {'control_type':'List', 'title':'会话', 'framework_id':'Qt'}
    {'control_type':'Edit', 'auto_id':'chat_input_field'}
    {'class_name':'mmui::ChatInputField'}

其中 `control_type` + `title` 在 Linux(AT-SPI)上有直接对应物,而 `auto_id` /
`class_name` / `framework_id` 没有。本模块负责:

1. `control_type` -> AT-SPI role 集合(Qt 的 QAccessible 角色);
2. `title` -> `name`(支持 `''` 表示"名称为空"、支持 `^...$` 正则);
3. `class_name` -> 一张**显式的**兼容表(微信内部类名没有 AT-SPI 对应物,
   这里给出人工标定的启发式角色,找不到就明确报错而不是猜);
4. 完全无法翻译的选择器抛 `UnsupportedSelector`,避免"静默匹配到错误控件"。

这样上层 `Uielements` 里的选择器表在 Linux 上**能复用多少就复用多少**,
不能复用的会立刻暴露出来。
'''
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Pattern, Sequence

from .base import UnsupportedSelector

# --------------------------------------------------------------------------- #
# UIA control_type -> (AT-SPI role, ...)
# Qt 的 QAccessible::Role 在 AT-SPI 上的名字,见 at-spi2-core 的 role 表。
# 这里给出"上界"集合:同一个 UIA 控件类型在不同 Qt 版本里可能退化成多个角色。
# --------------------------------------------------------------------------- #
CONTROL_TYPE_ROLES: dict[str, tuple[str, ...]] = {
    'Button': ('push button', 'button', 'toggle button'),
    'SplitButton': ('push button', 'button'),
    'CheckBox': ('check box',),
    'RadioButton': ('radio button',),
    'ComboBox': ('combo box',),
    'Custom': ('filler', 'panel', 'section'),
    'Document': ('document',),
    'Edit': ('text', 'entry', 'password text'),
    'Group': ('panel', 'filler', 'grouping'),
    'Image': ('image', 'icon'),
    'List': ('list', 'table', 'tree'),
    'ListItem': ('list item', 'table row', 'tree item'),
    'Menu': ('menu',),
    'MenuBar': ('menu bar',),
    'MenuItem': ('menu item',),
    'Pane': ('panel', 'layered pane', 'filler', 'scroll pane'),
    'ProgressBar': ('progress bar',),
    'ScrollBar': ('scroll bar',),
    'Slider': ('slider',),
    'StatusBar': ('status bar',),
    'Tab': ('page tab list',),
    'TabItem': ('page tab',),
    'Table': ('table', 'tree'),
    'Text': ('label', 'text', 'paragraph', 'heading'),
    'TitleBar': ('title bar',),
    'ToolBar': ('tool bar',),
    'ToolTip': ('tool tip',),
    'Tree': ('tree', 'table'),
    'TreeItem': ('tree item', 'table row'),
    'Window': ('frame', 'dialog', 'window'),
    # -- 以下是 AT-SPI 风格的常见写法别名(方便 Linux 侧直接写 role 名) --
    'Frame': ('frame', 'dialog', 'window'),
    'Label': ('label', 'text'),
    'Entry': ('text', 'entry'),
    'PushButton': ('push button', 'button'),
    'Panel': ('panel', 'filler'),
    'Paragraph': ('paragraph', 'label', 'text'),
    'ScrollPane': ('scroll pane', 'panel'),
}

#: 无法翻译的 pywinauto 关键字(会被忽略,但会记录在 `Selector.ignored` 里)
IGNORED_KEYS = frozenset({
    'auto_id', 'framework_id', 'top_level_only', 'found_index', 'backend',
    'visible_only', 'enabled_only', 'best_match', 'handle', 'process',
    'depth', 'regex_name', 'regex_name_re', 'control_id', 'control_type_re',
})

#: 微信内部类名 -> AT-SPI 角色。**人工标定的启发式**,不是等价映射。
#: 只收录 Linux 后端实际用到、且语义稳定的那几个。
CLASS_NAME_ROLES: dict[str, tuple[str, ...]] = {
    'mmui::MainWindow': ('frame', 'window'),
    'mmui::LoginWindow': ('frame', 'window'),
    'mmui::ChatInputField': ('text', 'entry', 'paragraph'),
    'mmui::XValidatorTextEdit': ('text', 'entry'),
    'mmui::StickyHeaderRecyclerListView': ('list', 'tree', 'table'),
    'mmui::ContactsManagerControlView': ('list', 'tree'),
    'mmui::XRecyclerTableView': ('list', 'table', 'tree'),
    'mmui::PublishComponent': ('panel', 'filler'),
    'mmui::ProfileView': ('panel', 'filler', 'frame'),
    'mmui::ContactProfileView': ('panel', 'filler', 'frame'),
    'mmui::ChatItemView': ('list item',),
    'mmui::ChatSystemInfoItemView': ('list item',),
    'mmui::ChatTextItemView': ('list item', 'label', 'paragraph'),
    'mmui::ChatBubbleItemView': ('list item',),
    'mmui::ChatBubbleReferItemView': ('list item',),
    'mmui::ChatImageItemView': ('list item', 'image'),
    'mmui::ChatVoiceItemView': ('list item',),
    'mmui::ChatPersonalCardItemView': ('list item',),
}

_ROLE_TITLE = re.compile(r'^[A-Z][A-Za-z]*$')


def normalize_role(role: str) -> str:
    '''把 AT-SPI role 名统一成小写、单词间单空格的形式。'''
    return ' '.join(str(role).strip().lower().split())


def normalize_name(name: str) -> str:
    return '' if name is None else str(name)


@dataclass
class Selector:
    '''翻译后的判据。`match(role, name)` 即"是否命中"。'''

    roles: frozenset[str] = frozenset()
    name: Optional[str] = None          # None = 不限制
    name_regex: Optional[Pattern] = None
    ignored: tuple[str, ...] = ()       # 被忽略的 Windows 专有键
    source: dict = field(default_factory=dict)

    def match(self, role: str, name: str) -> bool:
        if self.roles and normalize_role(role) not in self.roles:
            return False
        if self.name is not None and normalize_name(name) != self.name:
            return False
        if self.name_regex is not None and not self.name_regex.search(normalize_name(name)):
            return False
        return True

    def as_callable(self) -> Callable[[str, str], bool]:
        return self.match

    def __str__(self) -> str:
        parts = []
        if self.roles:
            parts.append('role in ' + '/'.join(sorted(self.roles)))
        if self.name is not None:
            parts.append(f'name == {self.name!r}')
        if self.name_regex is not None:
            parts.append(f'name =~ {self.name_regex.pattern!r}')
        if self.ignored:
            parts.append('ignored ' + ','.join(self.ignored))
        return 'Selector(' + '; '.join(parts) + ')'


def translate(criteria: dict) -> Selector:
    '''把一个 pywinauto 风格选择器翻译成 `Selector`。

    Raises:
        UnsupportedSelector: 选择器不含任何可在 AT-SPI 上判定的条件。
    '''
    if not isinstance(criteria, dict):
        raise TypeError(f'选择器必须是 dict,收到 {type(criteria)!r}')

    roles: set[str] = set()
    name: Optional[str] = None
    name_regex: Optional[Pattern] = None
    ignored: list[str] = []
    translatable = 0

    # Linux 侧原生写法:直接给 AT-SPI 的 role / name
    raw_role = criteria.get('role')
    if raw_role:
        roles.update(normalize_role(r) for r in
                     (raw_role if isinstance(raw_role, (tuple, list, set)) else [raw_role]))
        translatable += 1

    raw_name = criteria.get('name')
    if raw_name is not None:
        if isinstance(raw_name, re.Pattern):
            name_regex = raw_name
        else:
            name = str(raw_name)
        translatable += 1

    control_type = criteria.get('control_type')
    if control_type:
        key = str(control_type)
        if key in CONTROL_TYPE_ROLES:
            roles.update(normalize_role(r) for r in CONTROL_TYPE_ROLES[key])
            translatable += 1
        else:
            # 允许直接写 AT-SPI role(方便 Linux 侧原生使用),但必须是规范的小写写法。
            # 形如 'NoSuchType' 的驼峰串一律当成"未知的 UIA 类型"报错,
            # 绝不猜成某个 role —— 猜错的代价是点到别的控件。
            if key == key.lower() and _ROLE_TITLE.match(key.replace(' ', '')):
                roles.add(normalize_role(key))
                translatable += 1
            else:
                raise UnsupportedSelector(criteria, f'未知的 control_type {key!r}')

    title = criteria.get('title')
    if title is not None:
        translatable += 1
        if isinstance(title, re.Pattern):
            name_regex = title
        elif isinstance(title, str):
            if len(title) > 1 and title.startswith('^') and title.endswith('$'):
                name_regex = re.compile(title)
            else:
                name = title
        else:
            raise UnsupportedSelector(criteria, f'title 类型不支持: {type(title)!r}')

    class_name = criteria.get('class_name')
    if class_name:
        mapped = CLASS_NAME_ROLES.get(str(class_name))
        if mapped:
            class_roles = {normalize_role(r) for r in mapped}
            roles = (roles & class_roles) if roles else class_roles
            if not roles:
                # control_type 与 class_name 推出的角色没有交集 -> 以 control_type 为准,
                # 因为 UIA 的 control_type 更可信
                roles = {normalize_role(r)
                         for r in CONTROL_TYPE_ROLES.get(str(criteria.get('control_type')), ())}
            translatable += 1
        else:
            ignored.append('class_name')
            if not control_type and not title:
                raise UnsupportedSelector(
                    criteria, f'class_name {class_name!r} 无 AT-SPI 等价物')

    if 'role' in criteria or 'name' in criteria:
        pass
    for key in criteria:
        if key in ('control_type', 'title', 'class_name', 'role', 'name'):
            continue
        if key in IGNORED_KEYS:
            ignored.append(key)
        else:
            ignored.append(key)

    if translatable == 0:
        raise UnsupportedSelector(criteria, '缺少 control_type / title / 可标定的 class_name')

    return Selector(roles=frozenset(roles), name=name, name_regex=name_regex,
                    ignored=tuple(ignored), source=dict(criteria))


def translate_all(criteria_list: Sequence[dict]) -> list[Selector]:
    '''依次翻译多个候选选择器(常用于多语言),跳过不可翻译项。'''
    out = []
    for c in criteria_list:
        try:
            out.append(translate(c))
        except UnsupportedSelector:
            continue
    return out
