'''微信自动化过程中各种可能产生的错误'''
class NotStartError(Exception):
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
class NoSuchFriendError(Exception):
    def __init__(self, Error='好友或群聊备注有误！查无此人！'):
        super().__init__(Error)
class AlreadyInContactsError(Exception):
    def __init__(self, Error='好友已在通讯录中,无需添加！'):
        super().__init__(Error)
class CantSendEmptyMessageError(Exception):
    def __init__(self, Error='不能发送空白消息！'):
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
        super().__init__(Error)
class NotFriendError(Exception):
    def __init__(self, Error):
        super().__init__(Error)
class NoChatHistoryError(Exception):
    def __init__(self, Error):
        super().__init__(Error)
class NoResultsError(Exception):
    def __init__(self, Error):
        super().__init__(Error)
