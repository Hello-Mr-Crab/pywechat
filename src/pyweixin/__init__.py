'''
pyweixin
========

pywechat下的微信4.1+版本的自动化工具
    可前往 'https://github.com/Hello-Mr-Crab/pywechat' 查看详情


Modules
-------
    - `WeChatTools`:  该模块中封装了Tools与Navigator两个静态类,主要用来辅助WeChatAuto实现其他自动化功能(仅 Windows)
    - `WeChatAuto`:  pyweixin的主要模块,其内部包含消息,通讯录,文件,好友设置,朋友圈,自动回复,消息监控,微信设置这几个功能对应的静态类(仅 Windows)
    - `WinSettings`:  一些修改windows系统设置的方法(仅 Windows)
    - `Uielements`:  微信主界面内各种UI元素的POM封装(kwargs格式,适用于pywinauto的window,child_window,descendants,children四种定位元素方法)
    - `utils.py`:  内置一些配合WeChatAuto实现自动化的函数,比如@好友,遍历会话列表扫描新消息等(仅 Windows)
    - `Warnings`:  一些可能触发的警告
    - `platform`:  平台抽象层。`platform.backend()` 返回当前平台的驱动;
                   Linux 后端见 `platform.linux` 与 `linux_auto`(AT-SPI + XTest)
    - `linux_auto`: Linux 下的最小可用 API(打开会话、发消息、读消息)

平台支持
--------
    - `Windows`:  完整功能(pywinauto / UIAutomation)
    - `Linux`:    核心闭环(登录态检测、按名字打开会话、发送文本、读取消息),
                  基于 AT-SPI2 读 UI 树 + XTest 输入 + ffmpeg 截图
    - 其它平台:    不保证

Examples
--------

Windows:

    >>> from pyweixin.WeChatAuto import Monitor
    >>> from pyweixin.WeChatTools import Navigator
    >>> dialog_window=Navigator.open_seperate_dialog_window(friend='好友')
    >>> newMessages=Monitor.listen_on_chat(dialog_window,'1min')

Linux:

    >>> from pyweixin import linux_auto as wx
    >>> wx.send_message('文件传输助手','hello from Xvfb')
    >>> wx.read_messages(5)

支持版本:
--------
    - `Python版本`: 3.10+(需支持TypeHint)
    - `微信版本`:  4.1.6+

注意:
-----
    使用pyweixin时要保证微信已经登录!
    Linux 侧需要微信带 QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1 启动,详见 docs/LINUX.md


Have fun in WechatAutomation (＾＿－)
====
'''
import sys

#: 当前平台的规范名: 'windows' / 'linux' / 'darwin' / 其它
PLATFORM = ('windows' if sys.platform.startswith('win')
            else 'linux' if sys.platform.startswith('linux')
            else 'darwin' if sys.platform == 'darwin'
            else sys.platform)

#: 目前仍然只支持 Windows 的名字(历史包袱:pywinauto / win32 / 注册表)
WINDOWS_ONLY_NAMES = frozenset({
    'AutoReply', 'Call', 'Collections', 'Contacts', 'Files', 'FriendSettings',
    'Messages', 'Moments', 'Monitor', 'Settings', 'Tools', 'Navigator',
    'SystemSettings', 'WeChatAuto', 'WeChatTools', 'WinSettings', 'utils',
})


def _windows_only_error(name: str) -> NotImplementedError:
    return NotImplementedError(
        f'pyweixin.{name} 依赖 pywinauto / win32api,只能在 Windows 上使用。\n'
        f'当前平台是 {PLATFORM!r}。Linux 请使用:\n'
        f'    from pyweixin import linux_auto as wx\n'
        f'    wx.send_message("文件传输助手", "hello")\n'
        f'能力与限制见 docs/LINUX.md。'
    )


if PLATFORM == 'windows':  # pragma: no cover - 仅在 Windows 上执行
    from pyweixin.WeChatAuto import (AutoReply, Collections, Call, Contacts, Files,
                                     FriendSettings, Messages, Moments, Monitor, Settings)
    from pyweixin.WeChatTools import Tools, Navigator
    from pyweixin.WinSettings import SystemSettings
    from pyweixin.Config import GlobalConfig
else:
    # 非 Windows 平台上不导入 pywinauto 系模块,保持 `import pyweixin` 可用
    from pyweixin.Config import GlobalConfig

    def __getattr__(name):
        if name in WINDOWS_ONLY_NAMES:
            raise _windows_only_error(name)
        if name == 'linux_auto' and PLATFORM != 'linux':
            raise NotImplementedError('linux_auto 只在 Linux 上可用')
        raise AttributeError(f'module {__name__!r} has no attribute {name!r}')

    def __dir__():
        return sorted(list(globals()) + ['linux_auto'])


__all__ = ['GlobalConfig', 'platform']
if PLATFORM == 'windows':
    __all__ += ['AutoReply', 'Collections', 'Call', 'Contacts', 'Files',
                'FriendSettings', 'Messages', 'Moments', 'Monitor', 'Settings',
                'Tools', 'Navigator', 'SystemSettings']
elif PLATFORM == 'linux':
    __all__ += ['linux_auto']

#Author:Hello-Mr-Crab
#Contributor:Viper,Chanpoe,mrhan1993,nmhjklnm,clen1,guanjt3,Yjppj,SamCheng0717
#Linux backend:AT-SPI2 + XTest(见 platform/linux)
