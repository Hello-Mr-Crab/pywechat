'''微信自动化过程中各种可能产生的错误'''
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.uia_defines import NoPatternInterfaceError
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
class PrivacyNotCorrectError(Exception):
    def __init__(self, Error='权限不存在！请按照 仅聊天;聊天、朋友圈、微信运动等;\n不让他（她）看;不看他（她);的四种格式输入privacy'):
        super().__init__(Error)
class NoWechat_number_or_Phone_numberError(Exception):
    def __init__(self, Error='未输入微信号或手机号,请至少输入二者其中一个！'):
        super().__init__(Error)
class EmptyFileError(Exception):
    def __init__(self, Error='不能发送空文件！请重新选择文件路径!'):
        super().__init__(Error)
class NoFilesToSendError(Exception):
    def __init__(self, Error='没有任何可以发送的文件！请检查文件类型(文件夹)\n以及文件大小(微信不能发送空文件以及大小超过1GB的文件)'):
        super().__init__(Error)
class EmptyFolderError(Exception):
    def __init__(self, Error='文件夹内没有文件！请重新选择！'):
        super().__init__(Error)
class NotFileError(Exception):
    def __init__(self, Error='该路径下的内容不是文件,无法发送!'):
        super().__init__(Error)
class NoFilesError(Exception):
    def __init__(self, Error='files内无任何可发送文件,可能存在文件破损!'):
        super().__init__(Error)
class NotFriendError(Exception):
    def __init__(self,Error='非正常好友,无法打开好友聊天信息界面！'):
        super().__init__(Error)
class NotFolderError(Exception):
    def __init__(self, Error='给定路径不是文件夹！若需发送多个文件给好友,请将所有待发送文件置于文件夹内,并在此方法中传入文件夹路径'):
        super().__init__(Error)
class CantCreateGroupError(Exception):
    def __init__(self, Error='三人不成群,除自身外最少还需要两人才能建群！'):
        super().__init__(Error)
class NoSuchFriendError(Exception):
    def __init__(self, Error='好友或群聊备注有误！查无此人！'):
        super().__init__(Error)
class SameNameError(Exception):
    def __init__(self, Error='待修改的群名需与先前的群名不同才可修改！'):
        super().__init__(Error)
class AlreadyInContactsError(Exception):
    def __init__(self, Error='好友已在通讯录中,无需添加！'):
        super().__init__(Error)
class EmptyNoteError(Exception):
    def __init__(self, Error="笔记中至少要有文字和文件中的一个！"):
        super().__init__(Error)
class CantSendEmptyMessageError(Exception):
    def __init__(self, Error='不能发送空白消息！'):
        super().__init__(Error)
class CantReplyToOfficialAccountError(Exception):
    def __init__(self, Error='不能自动回复公众号!'):
        super().__init__(Error)
class WrongParameterError(Exception):
    def __init__(self, Error='state的取值应为open或close!'):
        super().__init__(Error)
class NotInstalledError(Exception):
    def __init__(self, Error='未找到微信注册表路径,可能未安装4.0版本PC微信!'):
        super().__init__(Error)
class NoTrayFindError(Exception):
    def __init__(self,Error='未找到微信托盘,可能未启动或已隐藏！'):
        super().__init__(Error)
class NotFolderError(Exception):
    def __init__(self,Error='该路径非文件夹,无法保存文件！'):
        super().__init__(Error)
class WrongParameterError(Exception):
    def __init__(self, Error):
        super().__init__(Error)
class ElementNotFoundError(ElementNotFoundError):
    def __init__(self, Error):
        super().__init__(Error)
class NoPatternInterfaceError(NoPatternInterfaceError):
    def __init__(self,Error):
        super().__init__(Error)
class NoSuchMessageError(Exception):
    def __init__(self, Error):
        super().__init__(Error)
class NotFriendError(Exception):
    def __init__(self, Error):
        super().__init__(Error)
class TickleError(Exception):
    def __init__(self, Error):
        super().__init__(Error)
class HaveBeenSetChatonlyError(Exception):
    def __init__(self, Error):
        super().__init__(Error)
class HaveBeenSetUnseentohimError(Exception):
    def __init__(self, Error):
        super().__init__(Error)
class HaveBeenSetDontseehimError(Exception):
    def __init__(self, Error):
        super().__init__(Error)
class NoPermissionError(Exception):
    def __init__(self, Error):
        super().__init__(Error)
class NoChatHistoryError(Exception):
    def __init__(self, Error):
        super().__init__(Error)
class HaveBeenSetError(Exception):
    def __init__(self, Error):
        super().__init__(Error)
class NoResultsError(Exception):
    def __init__(self, Error):
        super().__init__(Error)
class TaskNotBuildError(Exception):
    def __init__(self,Error):
        super().__init__(Error)
class AlreadyCloseError(Exception):
    def __init__(self,Error):
        super().__init__(Error)