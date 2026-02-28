'''微信自动化过程中各种可能产生的错误'''
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.timings import TimeoutError
from pywinauto.uia_defines import NoPatternInterfaceError
####################################################### 
#继承于pywinauto内置的Error
class ElementNotFoundError(ElementNotFoundError):
    def __init__(self, Error):
        super().__init__(Error)
class NoPatternInterfaceError(NoPatternInterfaceError):
    def __init__(self,Error):
        super().__init__(Error)
class TimeoutError(TimeoutError):
    def __init__(self,Error):
        super().__init__(Error)
##########################################################
class WeChatNotStartError(Exception):
    def __init__(self, Error='微信未启动,请启动后再调用此函数！'):
        super().__init__(Error)
class NetWorkNotConnectError(Exception):
    def __init__(self, Error='网络可能未连接,暂时无法进入微信!请尝试连接wifi扫码进入微信'):
        super().__init__(Error)
class ScanCodeToLogInError(Exception):
    def __init__(self, Error='你还未在手机端开启PC端微信自动登录,可在本次手动进入微信后在顶部登录选项勾选'):
        super().__init__(Error)
class TimeNotCorrectError(Exception):
    def __init__(self, Error='请输入合法的时间长度！'):
        super().__init__(Error)
class EmptyFileError(Exception):
    def __init__(self, Error='不能发送空文件！请重新选择文件路径!'):
        super().__init__(Error)
class EmptyFolderError(Exception):
    def __init__(self, Error='文件夹内没有文件！请重新选择！'):
        super().__init__(Error)
class NotFileError(Exception):
    def __init__(self, Error='该路径下的内容不是文件,无法发送!'):
        super().__init__(Error)
class NotFolderError(Exception):
    def __init__(self, Error='给定路径不是文件夹！若需发送多个文件给好友,请将所有待发送文件置于文件夹内,并在此方法中传入文件夹路径'):
        super().__init__(Error)
class NoSuchFriendError(Exception):
    def __init__(self, Error='好友或群聊备注有误！查无此人！请提供准确且完整的好友或群聊备注!'):
        super().__init__(Error)
class NoGroupsError(Exception):
    def __init__(self,Error='还未加入过任何群聊,无法获取群聊信息!'):
        super().__init__(Error)
class CantCreateGroupError(Exception):
    def __init__(self, Error='除自身外至少两人以上才可以创建群聊!'):
        super().__init__(Error)
class NotInstalledError(Exception):
    def __init__(self, Error='未找到微信注册表路径,可能未安装3.9版本PC微信或手动删除了注册表!'):
        super().__init__(Error)
class NoSubOffAccError(Exception):
    def __init__(self, Error='从未关注过任何公众号,无法获取已关注的公众号名称！'):
        super().__init__(Error)
class NoWecomFriendsError(Exception):
    def __init__(self, Error='未查找到企业微信好友,无法获取企业微信好友信息！'):
        super().__init__(Error)
class NoChatsError(Exception):
    def __init__(self,Error='会话列表为空,无最近聊天对象!'):
        super().__init__(Error)
class NotFriendError(Exception):
    def __init__(self, Error):
        super().__init__(Error)
class TickleError(Exception):
    def __init__(self, Error):
        super().__init__(Error)
class NoPermissionError(Exception):
    def __init__(self, Error):
        super().__init__(Error)
class NoChatHistoryError(Exception):
    def __init__(self, Error):
        super().__init__(Error)
class NoResultsError(Exception):
    def __init__(self, Error):
        super().__init__(Error)
