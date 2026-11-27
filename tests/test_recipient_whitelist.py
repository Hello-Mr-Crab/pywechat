'''
收件人白名单（可选）的回归测试。

历史背景：PR #306 曾把白名单硬编码成 ``{'文件传输助手', '好友A'}``，和 Windows 端
（任意备注都能发）不一致。现在改成"默认不限制 + 可选参数"，这组测试固定住新语义：

    LinuxWeChat()                                 -> 不限制
    LinuxWeChat(allowed_recipients=None)          -> 不限制
    LinuxWeChat(allowed_recipients=set())         -> 不限制
    LinuxWeChat(allowed_recipients={'A'})         -> 只允许 A（strip 后精确匹配）

并且：
  * ``open_chat`` 不再受白名单约束（只做导航/读取）；
  * 校验下沉到 ``_compose_and_send``，私有路径同样被挡，且发生在碰输入框之前；
  * 用"当前实际打开的会话名"比对，而不是调用方传入的名字。
'''
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pyweixin import linux_auto as wx
from pyweixin.linux_auto import (DEFAULT_ALLOWED_RECIPIENTS, RecipientNotAllowed,
                                 assert_allowed_recipient, is_allowed_recipient,
                                 normalize_allowed_recipients)


class ExplodingBackend:
    '''任何属性访问都会失败的假后端，用来证明"拒绝发生在 UI 之前"。'''

    def __getattr__(self, item):
        raise AssertionError(f'不允许触碰后端: {item}')


class FakeBot(wx.LinuxWeChat):
    '''受控的 LinuxWeChat：current_chat 返回固定值，输入框/后端一律爆炸。'''

    def __init__(self, current_chat, **kwargs):
        self._chat = current_chat
        super().__init__(backend=object(), **kwargs)

    def current_chat(self):
        return self._chat

    @property
    def backend(self):
        raise AssertionError('不允许触碰后端(x11)')

    def _input_box(self):
        raise AssertionError('不允许触碰输入框')


class TestDefaultsUnrestricted(unittest.TestCase):
    def test_module_default_is_none(self):
        self.assertIsNone(DEFAULT_ALLOWED_RECIPIENTS)

    def test_instance_default_is_none(self):
        self.assertIsNone(wx.LinuxWeChat().allowed_recipients)

    def test_explicit_none_is_unrestricted(self):
        bot = wx.LinuxWeChat(allowed_recipients=None)
        self.assertIsNone(bot.allowed_recipients)

    def test_empty_iterables_are_unrestricted(self):
        for empty in (set(), frozenset(), [], (), {'', '  '}):
            with self.subTest(empty=empty):
                self.assertIsNone(wx.LinuxWeChat(allowed_recipients=empty).allowed_recipients)

    def test_default_allows_anyone(self):
        for name in ('文件传输助手', '好友A（备注）', '张三', '某个群'):
            with self.subTest(name=name):
                self.assertEqual(assert_allowed_recipient(name), name)

    def test_default_is_allowed_for_empty_whitelist_lookup(self):
        self.assertTrue(is_allowed_recipient('张三'))
        self.assertTrue(is_allowed_recipient('张三', None))

    def test_hardcoded_name_is_gone(self):
        # 旧的硬编码常量必须彻底消失，防止有人不小心又加回去
        self.assertFalse(hasattr(wx, 'ALLOWED_RECIPIENTS'))


class TestAllowListSemantics(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize_allowed_recipients({' a ', 'b'}),
                         frozenset({'a', 'b'}))
        self.assertIsNone(normalize_allowed_recipients(None))
        self.assertIsNone(normalize_allowed_recipients(set()))
        self.assertIsNone(normalize_allowed_recipients({'   '}))

    def test_string_is_treated_as_single_name(self):
        # 传字符串是常见误用：按单个名字处理，不做逗号拆分
        self.assertEqual(normalize_allowed_recipients('张三'), frozenset({'张三'}))

    def test_allowed_hit(self):
        allowed = {'文件传输助手', '好友A（备注）'}
        self.assertEqual(assert_allowed_recipient('文件传输助手', allowed), '文件传输助手')
        # 完整显示名 + 首尾空白
        self.assertEqual(assert_allowed_recipient('  好友A（备注） ', allowed),
                         '好友A（备注）')

    def test_allowed_miss(self):
        allowed = {'文件传输助手'}
        with self.assertRaises(RecipientNotAllowed) as ctx:
            assert_allowed_recipient('张三', allowed)
        self.assertIn('白名单', str(ctx.exception))
        self.assertIn('张三', str(ctx.exception))

    def test_partial_name_does_not_match(self):
        # 精确匹配：'好友A' 不能命中 '好友A（备注）'
        allowed = {'好友A（备注）'}
        with self.assertRaises(RecipientNotAllowed):
            assert_allowed_recipient('好友A', allowed)

    def test_non_string_rejected(self):
        for bad in (None, 123, ['a'], b'x'):
            with self.subTest(value=bad):
                with self.assertRaises(RecipientNotAllowed):
                    assert_allowed_recipient(bad)


class TestOpenChatNotGated(unittest.TestCase):
    def test_open_chat_reaches_backend_for_stranger(self):
        # 白名单只限制发送；open_chat 必须照常往下走（这里会因为假后端而失败）
        bot = wx.LinuxWeChat(backend=ExplodingBackend(),
                             allowed_recipients={'文件传输助手'})
        with self.assertRaises(AssertionError):
            bot.open_chat('张三')

    def test_open_chat_validates_type_only(self):
        bot = wx.LinuxWeChat(backend=ExplodingBackend())
        for bad in ('', '   ', None, 123):
            with self.subTest(value=bad):
                with self.assertRaises(ValueError):
                    bot.open_chat(bad)


class TestPrivateSendPathGated(unittest.TestCase):
    '''校验下沉的意义：绕过 send_message 也发不出去。'''

    def test_compose_blocks_disallowed_current_chat(self):
        bot = FakeBot('张三', allowed_recipients={'文件传输助手'})
        with self.assertRaises(RecipientNotAllowed):
            bot._compose_and_send('hi')          # 不传 recipient，用当前会话判断
        # 能抛出说明没走到 _input_box / backend

    def test_compose_blocks_explicit_recipient(self):
        bot = FakeBot('文件传输助手', allowed_recipients={'文件传输助手'})
        with self.assertRaises(RecipientNotAllowed):
            bot._compose_and_send('hi', recipient='张三')

    def test_compose_blocks_when_target_mismatch(self):
        # 两个名字都在白名单里，但"打开的会话"和"调用方以为的会话"不一致 -> 拒绝
        bot = FakeBot('文件传输助手',
                      allowed_recipients={'文件传输助手', '好友A（备注）'})
        with self.assertRaises(RuntimeError):
            bot._compose_and_send('hi', recipient='好友A（备注）')

    def test_compose_fails_closed_without_current_chat(self):
        bot = FakeBot(None, allowed_recipients={'文件传输助手'})
        with self.assertRaises(RecipientNotAllowed):
            bot._compose_and_send('hi')

    def test_compose_allows_when_unrestricted(self):
        # 默认不限制时不应因为白名单报错（会继续走到 _input_box 才失败）
        bot = FakeBot('张三')
        with self.assertRaises(AssertionError):
            bot._compose_and_send('hi')

    def test_compose_allows_when_chat_is_whitelisted(self):
        bot = FakeBot('文件传输助手', allowed_recipients={'文件传输助手'})
        with self.assertRaises(AssertionError):   # 过了闸，才轮到 _input_box 爆炸
            bot._compose_and_send('hi')


class TestSendMessagePreCheck(unittest.TestCase):
    def test_send_message_rejects_before_ui(self):
        bot = wx.LinuxWeChat(backend=ExplodingBackend(),
                             allowed_recipients={'文件传输助手'})
        with self.assertRaises(RecipientNotAllowed):
            bot.send_message('张三', 'should never be sent')

    def test_send_message_default_does_not_reject(self):
        # 默认不限制：不会因为收件人报错（会继续往下走到 require_login/后端）
        bot = wx.LinuxWeChat(backend=ExplodingBackend())
        with self.assertRaises(AssertionError):
            bot.send_message('张三', 'hi')

    def test_send_message_requires_non_empty_message(self):
        bot = wx.LinuxWeChat(backend=ExplodingBackend())
        with self.assertRaises(ValueError):
            bot.send_message('张三', '   ')


if __name__ == '__main__':
    unittest.main(verbosity=2)
