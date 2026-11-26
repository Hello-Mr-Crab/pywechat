'''
收件人白名单的回归测试。

这条规则是硬约束:**只允许向「文件传输助手」和「依依」发送消息**,
其它任何收件人必须在触碰 UI / 后端之前就被拒绝。测试故意用一个"碰一下就炸"
的假后端,确保拒绝发生在任何 UI 交互之前。
'''
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pyweixin import linux_auto as wx
from pyweixin.linux_auto import (ALLOWED_RECIPIENTS, RecipientNotAllowed,
                                 assert_allowed_recipient, is_allowed_recipient)


class ExplodingBackend:
    '''任何属性访问都会失败的假后端,用来证明"拒绝发生在 UI 之前"。'''

    def __getattr__(self, item):
        raise AssertionError(f'不允许触碰后端: {item}')


class TestWhitelistContent(unittest.TestCase):
    def test_exact_members(self):
        # 白名单必须恰好是这两个名字,新增/删除都必须改这里
        self.assertEqual(ALLOWED_RECIPIENTS, frozenset({'文件传输助手', '依依'}))

    def test_is_frozen(self):
        self.assertIsInstance(ALLOWED_RECIPIENTS, frozenset)

    def test_allowed_names(self):
        for name in ('文件传输助手', '依依'):
            self.assertEqual(assert_allowed_recipient(name), name)
            self.assertTrue(is_allowed_recipient(name))

    def test_whitespace_is_normalized(self):
        self.assertEqual(assert_allowed_recipient('  文件传输助手 '), '文件传输助手')
        self.assertEqual(assert_allowed_recipient('依依\n'), '依依')

    def test_rejected_names(self):
        for bad in ('张三', '李四', '', '   ', '文件传输助手2', '依依2',
                    '文件传输助', 'All Files', 'filehelper',
                    '文件传输助手,依依', '［文件传输助手］'):
            with self.subTest(name=bad):
                self.assertFalse(is_allowed_recipient(bad))
                with self.assertRaises(RecipientNotAllowed):
                    assert_allowed_recipient(bad)

    def test_non_string_rejected(self):
        for bad in (None, 123, ['文件传输助手'], b'\xe6\x96\x87'):
            with self.subTest(value=bad):
                with self.assertRaises(RecipientNotAllowed):
                    assert_allowed_recipient(bad)

    def test_error_message_mentions_whitelist(self):
        with self.assertRaises(RecipientNotAllowed) as ctx:
            assert_allowed_recipient('张三')
        self.assertIn('白名单', str(ctx.exception))


class TestSendRejectsBeforeUI(unittest.TestCase):
    def test_send_message_to_stranger_never_touches_backend(self):
        bot = wx.LinuxWeChat(backend=ExplodingBackend())
        with self.assertRaises(RecipientNotAllowed):
            bot.send_message('张三', 'should never be sent')
        # 能走到这里说明没有任何后端属性被访问过

    def test_open_chat_to_stranger_never_touches_backend(self):
        bot = wx.LinuxWeChat(backend=ExplodingBackend())
        with self.assertRaises(RecipientNotAllowed):
            bot.open_chat('群聊·家人')

    def test_allowed_name_does_reach_backend(self):
        # 反向验证:白名单内的名字不会被闸门挡住(它会继续往下走并因假后端失败)
        bot = wx.LinuxWeChat(backend=ExplodingBackend())
        with self.assertRaises(AssertionError):
            bot.open_chat('文件传输助手')


if __name__ == '__main__':
    unittest.main(verbosity=2)
