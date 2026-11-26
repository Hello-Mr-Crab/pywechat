'''
`pyweixin.platform.selector` 的单元测试。

这个模块是移植的"语义翻译层",一旦翻译错了,上层就会点到错误的控件,
所以每个映射规则都要有断言。
'''
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pyweixin.platform.base import UnsupportedSelector
from pyweixin.platform.selector import (CLASS_NAME_ROLES, Selector, normalize_role,
                                        translate, translate_all)


class TestControlTypeMapping(unittest.TestCase):
    def test_list(self):
        sel = translate({'control_type': 'List', 'title': '会话'})
        self.assertEqual(sel.name, '会话')
        self.assertIn('list', sel.roles)
        self.assertTrue(sel.match('list', '会话'))
        self.assertFalse(sel.match('list', '消息'))
        self.assertFalse(sel.match('label', '会话'))

    def test_button(self):
        sel = translate({'control_type': 'Button', 'title': '登录'})
        self.assertTrue(sel.match('push button', '登录'))
        self.assertTrue(sel.match('button', '登录'))
        self.assertFalse(sel.match('push button', '取消'))

    def test_edit_accepts_multiple_roles(self):
        # Qt 的可编辑控件在不同版本里可能是 text / entry / password text
        sel = translate({'control_type': 'Edit', 'title': '搜索'})
        for role in ('text', 'entry', 'password text'):
            with self.subTest(role=role):
                self.assertTrue(sel.match(role, '搜索'))
        self.assertFalse(sel.match('label', '搜索'))

    def test_unknown_control_type_raises(self):
        with self.assertRaises(UnsupportedSelector):
            translate({'control_type': 'NoSuchType'})

    def test_raw_atspi_role_passthrough(self):
        sel = translate({'role': 'push button', 'title': '发送'})
        self.assertEqual(sel.roles, frozenset({'push button'}))


class TestTitleSemantics(unittest.TestCase):
    def test_empty_title_means_empty_name(self):
        # pywinauto 里 title='' 表示"名字为空",不是"任意名字"
        sel = translate({'title': '', 'control_type': 'List'})
        self.assertEqual(sel.name, '')
        self.assertTrue(sel.match('list', ''))
        self.assertFalse(sel.match('list', '会话'))

    def test_title_can_be_regex(self):
        sel = translate({'title': '^会.*$', 'control_type': 'List'})
        self.assertIsNotNone(sel.name_regex)
        self.assertTrue(sel.match('list', '会话'))
        self.assertFalse(sel.match('list', '消息'))

    def test_plain_title_is_not_regex(self):
        sel = translate({'title': '搜索', 'control_type': 'Edit'})
        self.assertIsNone(sel.name_regex)

    def test_title_only(self):
        sel = translate({'title': '微信'})
        self.assertEqual(sel.roles, frozenset())
        self.assertTrue(sel.match('frame', '微信'))
        self.assertTrue(sel.match('label', '微信'))


class TestClassNameCompat(unittest.TestCase):
    def test_known_class_name_gives_roles(self):
        sel = translate({'class_name': 'mmui::ChatInputField'})
        self.assertIn('text', sel.roles)
        self.assertTrue(sel.match('text', ''))

    def test_class_name_intersects_with_control_type(self):
        # Edit 的候选角色 ∩ ChatInputField 的候选角色
        sel = translate({'control_type': 'Edit', 'class_name': 'mmui::ChatInputField'})
        self.assertEqual(sel.roles, frozenset({'text', 'entry'}))
        self.assertTrue(sel.match('text', ''))

    def test_unknown_class_name_without_control_type_raises(self):
        # 不能"猜",必须显式报错,否则会静默匹配到错误控件
        with self.assertRaises(UnsupportedSelector):
            translate({'class_name': 'mmui::SomethingNew'})

    def test_unknown_class_name_is_recorded_as_ignored(self):
        sel = translate({'control_type': 'List', 'class_name': 'mmui::SomethingNew'})
        self.assertIn('class_name', sel.ignored)
        self.assertTrue(sel.match('list', ''))

    def test_auto_id_only_raises(self):
        with self.assertRaises(UnsupportedSelector):
            translate({'auto_id': 'chat_input_field'})

    def test_auto_id_with_title_is_recorded_as_ignored(self):
        sel = translate({'control_type': 'Edit', 'title': '搜索',
                         'auto_id': 'chat_input_field'})
        self.assertIn('auto_id', sel.ignored)
        self.assertIn('auto_id', str(sel))


class TestRealSelectorsFromUielements(unittest.TestCase):
    '''直接用仓库里真实的选择器表回归,防止"改了翻译层但没人发现"。'''

    def test_repository_selector_tables(self):
        from pyweixin.Uielements import Lists, Main_window
        cases = [
            (Lists.ConversationList, 'list', '会话'),
            (Lists.FriendChatList, 'list', '消息'),
            (Main_window.Search, 'text', '搜索'),
        ]
        for criteria, role, name in cases:
            with self.subTest(criteria=criteria):
                sel = translate(criteria)
                self.assertTrue(sel.match(role, name))

    def test_translate_all_skips_unsupported(self):
        sels = translate_all([
            {'control_type': 'List', 'title': '会话'},
            {'auto_id': 'only_windows_id'},
        ])
        self.assertEqual(len(sels), 1)


class TestMisc(unittest.TestCase):
    def test_normalize_role(self):
        self.assertEqual(normalize_role('  Push  Button '), 'push button')

    def test_non_dict_raises_type_error(self):
        with self.assertRaises(TypeError):
            translate('List')

    def test_str_repr_is_readable(self):
        self.assertIn('会话', str(translate({'control_type': 'List', 'title': '会话'})))

    def test_class_name_table_entries_are_lowercase_roles(self):
        for cls, roles in CLASS_NAME_ROLES.items():
            for role in roles:
                with self.subTest(cls=cls, role=role):
                    self.assertEqual(role, normalize_role(role))


if __name__ == '__main__':
    unittest.main(verbosity=2)
