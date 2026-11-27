'''
AT-SPI 快照 / 元素定位 / 动作派发的单元测试。

全部用假的 Snapshot + 假 X11,不需要 DISPLAY、不需要微信、也不需要 at-spi2。
这样在 CI 或 Windows 上也能跑(保证"接口一致",弥补没有 Windows 机器)。
'''
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pyweixin.platform.base import ElementNotFound
from pyweixin.platform.linux.atspi import Node, Snapshot
from pyweixin.platform.linux.element import LinuxElement, LinuxWindowSpecification


# --------------------------------------------------------------------------- #
# 测试替身
# --------------------------------------------------------------------------- #
def build_snapshot(spec, app_name='wechat') -> Snapshot:
    '''把嵌套的 dict 结构变成 Snapshot。

    spec 形如::

        {'role': 'application', 'name': '', 'rect': (0,0,0,0), 'children': [...]}
    '''
    nodes: list[Node] = []

    def visit(item, depth, parent):
        x, y, w, h = item.get('rect', (0, 0, 0, 0))
        idx = len(nodes)
        nodes.append(Node(idx, item['role'], item.get('name', ''), x, y, w, h,
                          depth, parent, None,
                          showing=item.get('showing', True),
                          selected=item.get('selected', False)))
        for child in item.get('children', []):
            cidx = visit(child, depth + 1, idx)
            nodes[idx].children.append(cidx)
        return idx

    visit(spec, 0, None)
    return Snapshot(app_name, nodes)


class FakeSession:
    def __init__(self, snap):
        self._snap = snap
        self.scale = 1.0
        self.invalidated = 0

    def snapshot(self, app_name, force=False):
        return self._snap

    def invalidate(self, app_name=None):
        self.invalidated += 1

    def applications(self):
        return [self._snap.app_name]


class FakeX11:
    def __init__(self):
        self.calls = []

    def move(self, x, y):
        self.calls.append(('move', x, y))

    def click(self, x, y, button=1, count=1):
        self.calls.append(('click', x, y, button, count))

    def double_click(self, x, y, button=1):
        self.calls.append(('double_click', x, y))

    def key(self, spec):
        self.calls.append(('key', spec))

    def type_keys(self, keys, pause=0.0):
        self.calls.append(('type_keys', keys))

    def type_text(self, text, delay_ms=12):
        self.calls.append(('type_text', text))

    def paste_text(self, text):
        self.calls.append(('paste_text', text))

    def screenshot(self, path, region=None):
        self.calls.append(('screenshot', path, region))
        return path

    def move_to_center(self):
        return None


#: 一棵模仿微信主窗口的最小树
WECHAT_TREE = {
    'role': 'application', 'name': 'wechat', 'rect': (0, 0, 0, 0),
    'children': [
        {'role': 'frame', 'name': '微信', 'rect': (180, 60, 1240, 880), 'children': [
            {'role': 'list', 'name': '会话', 'rect': (241, 141, 240, 797), 'children': [
                {'role': 'list item', 'name': '文件传输助手\n\n\n',
                 'rect': (241, 141, 240, 65)},
                {'role': 'list item', 'name': '好友A\n\n\n',
                 'rect': (241, 206, 240, 65)},
            ]},
            {'role': 'text', 'name': '搜索', 'rect': (279, 106, 148, 22)},
            # 隐藏的控件:visible_only 必须把它过滤掉
            {'role': 'list', 'name': '消息', 'rect': (0, 0, 0, 0), 'showing': False},
        ]},
        {'role': 'frame', 'name': '文件传输助手', 'rect': (500, 179, 598, 640),
         'children': [
             {'role': 'list', 'name': '消息', 'rect': (501, 260, 596, 418), 'children': [
                 {'role': 'list item', 'name': '20:20', 'rect': (501, 260, 596, 41)},
                 {'role': 'list item', 'name': '你好呀',
                  'rect': (501, 301, 596, 57)},
             ]},
             {'role': 'text', 'name': '输入', 'rect': (521, 687, 560, 79)},
         ]},
    ],
}


class BaseCase(unittest.TestCase):
    def setUp(self):
        self.snap = build_snapshot(WECHAT_TREE)
        self.session = FakeSession(self.snap)
        self.x11 = FakeX11()

    def spec(self, **criteria):
        return LinuxWindowSpecification(self.session, self.x11, criteria,
                                        app_name='wechat')


# --------------------------------------------------------------------------- #
class TestSnapshot(BaseCase):
    def test_node_count(self):
        self.assertEqual(len(self.snap.nodes), 12)

    def test_find_by_role_and_name(self):
        from pyweixin.platform.selector import translate
        sel = translate({'control_type': 'List', 'title': '会话'})
        hits = self.snap.find(sel.match)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0].name, '会话')

    def test_visible_only_filters_hidden(self):
        from pyweixin.platform.selector import translate
        sel = translate({'control_type': 'List', 'title': '消息'})
        self.assertEqual(len(self.snap.find(sel.match)), 2)
        self.assertEqual(len(self.snap.find(sel.match, visible_only=True)), 1)
        self.assertEqual(self.snap.find(sel.match, visible_only=True)[0].x, 501)

    def test_children_of(self):
        root = self.snap.root
        roles = [n.role for n in self.snap.children_of(root)]
        self.assertEqual(roles, ['frame', 'frame'])

    def test_path_to_root(self):
        node = [n for n in self.snap.nodes if n.name == '你好呀'][0]
        chain = [n.name for n in self.snap.path_to_root(node)]
        self.assertEqual(chain[-1], 'wechat')
        self.assertIn('文件传输助手', chain)

    def test_rect_and_visible(self):
        node = [n for n in self.snap.nodes if n.name == '你好呀'][0]
        self.assertEqual(node.rect.left, 501)
        self.assertTrue(node.visible)


class TestSpecificationResolution(BaseCase):
    def test_resolve_by_control_type_and_title(self):
        el = self.spec(control_type='List', title='会话').resolve()
        self.assertEqual(el.role, 'list')
        self.assertEqual(el.window_text(), '会话')

    def test_resolve_returns_first_visible(self):
        # 树里有两个 '消息' list,隐藏的那个在前,必须解析到可见的那个
        el = self.spec(control_type='List', title='消息').resolve()
        self.assertEqual(el.rectangle().left, 501)

    def test_exists_true(self):
        self.assertTrue(self.spec(control_type='Frame', title='微信').exists())

    def test_exists_false(self):
        self.assertFalse(self.spec(control_type='List', title='不存在的列表').exists())

    def test_wait_raises_after_timeout(self):
        with self.assertRaises(ElementNotFound):
            self.spec(control_type='List', title='不存在的列表').wait(timeout=0.2)

    def test_found_index(self):
        first = self.spec(control_type='ListItem').resolve()
        second = self.spec(control_type='ListItem', found_index=1).resolve()
        self.assertEqual(first.window_text(), '文件传输助手\n\n\n')
        self.assertEqual(second.window_text(), '好友A\n\n\n')

    def test_children_only_direct(self):
        kids = self.spec(control_type='Frame', title='微信').children()
        roles = sorted(k.role for k in kids)
        self.assertEqual(roles, ['list', 'list', 'text'])

    def test_descendants_recursive(self):
        items = self.spec(control_type='Frame', title='微信').descendants(
            control_type='ListItem')
        self.assertEqual(len(items), 2)

    def test_child_window_anchors_and_carries_snapshot(self):
        win = self.spec(control_type='Frame', title='文件传输助手')
        msg = win.child_window(control_type='List', title='消息')
        self.assertTrue(msg.exists())
        self.assertEqual(msg.resolve().rectangle().width, 596)

    def test_element_info(self):
        el = self.spec(control_type='List', title='会话').resolve()
        info = el.element_info
        self.assertEqual(info.control_type, 'list')
        self.assertEqual(info.rectangle.top, 141)


class TestElementActions(BaseCase):
    def test_click_input_uses_center(self):
        el = self.spec(control_type='List', title='会话').resolve()
        el.click_input()
        # 会话列表中心 (241+120, 141+398)
        self.assertEqual(self.x11.calls[-1], ('click', 361, 539, 1, 1))

    def test_click_input_with_explicit_coords(self):
        el = self.spec(control_type='List', title='会话').resolve()
        el.click_input(coords=(10, 20))
        self.assertEqual(self.x11.calls[-1], ('click', 10, 20, 1, 1))

    def test_right_click_uses_button_3(self):
        el = self.spec(control_type='List', title='会话').resolve()
        el.right_click_input()
        self.assertEqual(self.x11.calls[-1][3], 3)

    def test_set_text_clicks_then_pastes(self):
        el = self.spec(control_type='Text', title='输入').resolve()
        el.set_text('你好')
        kinds = [c[0] for c in self.x11.calls]
        self.assertEqual(kinds, ['click', 'key', 'paste_text'])
        self.assertEqual(self.x11.calls[1], ('key', 'ctrl+a'))
        self.assertEqual(self.x11.calls[2], ('paste_text', '你好'))

    def test_type_keys_focuses_then_dispatches(self):
        el = self.spec(control_type='Text', title='输入').resolve()
        el.type_keys('{ENTER}')
        kinds = [c[0] for c in self.x11.calls]
        self.assertIn('click', kinds)
        self.assertEqual(self.x11.calls[-1], ('type_keys', '{ENTER}'))

    def test_class_name_is_empty(self):
        # AT-SPI 没有 class_name,必须明确返回空串而不是猜
        el = self.spec(control_type='List', title='会话').resolve()
        self.assertEqual(el.class_name(), '')
        self.assertEqual(el.automation_id(), '')

    def test_text_falls_back_to_name(self):
        el = self.spec(control_type='ListItem').resolve()
        self.assertEqual(el.text(), '文件传输助手\n\n\n')

    def test_capture_as_image_uses_element_rect(self):
        el = self.spec(control_type='Text', title='输入').resolve()
        el.capture_as_image('x.png')
        call = self.x11.calls[-1]
        self.assertEqual(call[0], 'screenshot')
        self.assertEqual(call[2], (521, 687, 560, 79))

    def test_is_visible_and_is_selected(self):
        el = self.spec(control_type='List', title='会话').resolve()
        self.assertTrue(el.is_visible())
        self.assertFalse(el.is_selected())


class TestNoPlatformLeak(BaseCase):
    def test_import_of_linux_module_does_not_need_display(self):
        # 纯导入 + 构造 spec 不应触碰 X / D-Bus
        spec = LinuxWindowSpecification(FakeSession(self.snap), FakeX11(),
                                       {'control_type': 'List', 'title': '会话'},
                                       app_name='wechat')
        self.assertIsInstance(spec, LinuxWindowSpecification)


if __name__ == '__main__':
    unittest.main(verbosity=2)


#: 内嵌渲染：聊天区直接画在主窗口里，没有独立 frame（真机上出现过这种形态）
INLINE_CHAT_TREE = {
    'role': 'application', 'name': 'wechat', 'rect': (0, 0, 0, 0),
    'children': [
        {'role': 'frame', 'name': '微信', 'rect': (180, 60, 1240, 880), 'children': [
            {'role': 'list', 'name': '会话', 'rect': (241, 141, 240, 797), 'children': [
                {'role': 'list item', 'name': '文件传输助手\n\n\n',
                 'rect': (241, 596, 240, 65)},
            ]},
            {'role': 'text', 'name': '搜索', 'rect': (279, 106, 148, 22)},
            {'role': 'label', 'name': '文件传输助手', 'rect': (497, 106, 84, 21)},
            {'role': 'list', 'name': '消息', 'rect': (481, 141, 937, 657), 'children': [
                {'role': 'list item', 'name': '你好', 'rect': (481, 182, 937, 57)},
            ]},
            {'role': 'text', 'name': '文件传输助手', 'rect': (501, 807, 901, 79)},
        ]},
    ],
}

#: 没有任何会话打开时：没有「消息」列表
NO_CHAT_TREE = {
    'role': 'application', 'name': 'wechat', 'rect': (0, 0, 0, 0),
    'children': [
        {'role': 'frame', 'name': '微信', 'rect': (180, 60, 1240, 880), 'children': [
            {'role': 'list', 'name': '会话', 'rect': (241, 141, 240, 797), 'children': []},
            {'role': 'text', 'name': '搜索', 'rect': (279, 106, 148, 22)},
        ]},
    ],
}


class _ChatBotMixin:
    def _bot(self, tree):
        from pyweixin import linux_auto as wx

        snap = build_snapshot(tree)
        session = FakeSession(snap)
        x11 = FakeX11()

        class _Bot(wx.LinuxWeChat):
            def main_window(self, timeout=5.0):
                return LinuxWindowSpecification(
                    session, x11, {'role': 'frame', 'title': '微信'}, app_name='wechat')

        return _Bot()


class TestCurrentChatDetection(_ChatBotMixin, unittest.TestCase):
    def test_separate_frame_wins(self):
        bot = self._bot(WECHAT_TREE)
        self.assertEqual(bot.current_chat(), '文件传输助手')

    def test_inline_render_detected_from_header_label(self):
        # 没有独立 frame 时，靠「消息」列表正上方的标题 label 识别
        bot = self._bot(INLINE_CHAT_TREE)
        self.assertEqual(bot.current_chat(), '文件传输助手')

    def test_no_chat_open(self):
        bot = self._bot(NO_CHAT_TREE)
        self.assertIsNone(bot.current_chat())
