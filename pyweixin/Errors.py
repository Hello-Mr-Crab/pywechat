'''微信自动化过程中各种可能产生的错误'''
class NotStartError(Exception):
    def __init__(self, Error='微信未启动,请先启动并登录微信后再使用pyweixin!'):
        super().__init__(Error)
class NotLoginError(Exception):
    def __init__(self, Error='微信未登录,请先点击登录后再使用pyweixin!'):
        super().__init__(Error)  
class NetWorkError(Exception):
    def __init__(self, Error='当前网络不可用,无法进行UI自动化!'):
        super().__init__(Error)
class TimeNotCorrectError(Exception):
    def __init__(self, Error='请输入合法的时间长度！'):
        super().__init__(Error)
class NoFilesToSendError(Exception):
    def __init__(self, Error='没有任何可以发送的文件！请检查文件类型(文件夹)\n以及文件大小(微信不能发送空文件以及大小超过1GB的文件)'):
        super().__init__(Error)
class NotFriendError(Exception):
    def __init__(self,Error='非正常好友,无法打开好友聊天信息界面！'):
        super().__init__(Error)
class NoSuchFriendError(Exception):
    def __init__(self, Error='好友或群聊备注有误！查无此人！'):
        super().__init__(Error)
class NotInstalledError(Exception):
    def __init__(self, Error='未找到微信注册表路径,可能未安装4.0版本PC微信!'):
        super().__init__(Error)
class NotFolderError(Exception):
    def __init__(self,Error='该路径非文件夹,无法保存文件！'):
        super().__init__(Error)
class NotFoundError(Exception):
    def __init__(self,Error='无法识别定位到微信主界面,请在微信登录前运行无障碍服务(讲述人)后再尝试!'):
        super().__init__(Error)
class NoChatHistoryError(Exception):
    def __init__(self, Error):
        super().__init__(Error)
class NoResultsError(Exception):
    def __init__(self, Error):
        super().__init__(Error)