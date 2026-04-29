'''
Config
======
微信参数全局配置,使用时需要导入GlobalConfig变量

Examples
========

    pyweixin内所有方法的位置参数支持全局设置,be like:
    ```
    from pyweixin import Navigator
    from pyweixin.Config import GlobalConfig
    GlobalConfig.language='English'
    GlobalConfig.load_delay=3.5
    GlobalConfig.is_maximize=True
    GlobalConfig.close_weixin=False
    Navigator.search_channels(search_content='微信4.0')
    Navigator.search_miniprogram(name='问卷星')
    Navigator.search_official_account(name='微信')
    ```
'''

# @property修饰getter函数可以实现直接访问类内属性,也就是class().xx,而不通过类内方法class().getter()的格式访问
# @xx.setter修饰setter函数可以实现直接等号赋值来修改类内属性值而不是通过类内的setter方法修改,
# 也就是class().xx=yy,而不是class().setter(yy)
# @xx.setter与@property修饰的方法名需要一致,必须先定义@property，再定义@xxx.setter

#example:
#方法调用,不够优雅
# t=Traditional(10)
# t.set_value(20)  
# print(t.get_value())

#像属性一样赋值,更加Pythonic
# m=Modern(10)
# m.value=20  
# print(m.value)
import psutil
import winreg
from warnings import warn
from .Errors import NotInstalledError
from .Warnings import LanguageDetectionFailedWarning
class globalConfig:
    '''位置参数全局配置'''
    _instance=None
    def __new__(cls):
        #初始化默认值
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._is_maximize=False
            cls._instance._close_weixin=True
            cls._instance._load_delay=3.5
            cls._instance._search_pages=5
            cls._instance._window_maximize=False
            cls._instance._send_delay=0.2
            cls._instance._audio_length=60
            cls._instance._clear=True
            cls._window_size=(1000,1000)
            cls._language='简体中文'
            cls._Version='4.1.8.107'
        return cls._instance
    
    @property
    def is_maximize(self):
        '''微信主界面是否全屏'''
        return self._is_maximize
    
    @is_maximize.setter
    def is_maximize(self,value):
        if not isinstance(value,bool):
            raise TypeError(f"is_maximize必须是bool类型,但传入了{type(value)}:{value}")
        self._is_maximize=value
    
    @property
    def window_size(self):
        '''微信主界面大小设定(宽,高)'''
        return self._window_size
    
    @window_size.setter
    def window_size(self,value):
        if not isinstance(value,tuple):
            raise TypeError(f"window_size必须是tuple类型,但传入了{type(value)}:{value}")
        self._window_size=value

    @property
    def close_weixin(self):
        '''任务结束是否关闭微信'''
        return self._close_weixin
    
    @close_weixin.setter
    def close_weixin(self, value):
        if not isinstance(value,bool):
            raise TypeError(f"close_weixin必须是bool类型,但传入了{type(value)}:{value}")
        self._close_weixin=value
    
    @property
    def load_delay(self):
        '''打开小程序、视频号、公众号的加载时长'''
        return self._load_delay
    
    @load_delay.setter
    def load_delay(self,value):
        if not isinstance(value,float):
            raise TypeError(f"load_delay必须是float类型,但传入了{type(value)}:{value}")
        self._load_delay=value
    
    @property
    def search_pages(self):
        '''会话列表查找好友时的搜索页数'''
        return self._search_pages
    
    @search_pages.setter
    def search_pages(self,value):
        if not isinstance(value,int):
            raise TypeError(f"search_pages必须是int类型,但传入了{type(value)}:{value}")
        self._search_pages=value
    
    @property
    def window_maximize(self):
        '''独立窗口是否全屏'''
        return self._window_maximize
    
    @window_maximize.setter
    def window_maximize(self,value):
        if not isinstance(value,bool):
            raise TypeError(f"window_maximize必须是bool类型,但传入了{type(value)}:{value}")
        self._window_maximize=value
    
    @property
    def send_delay(self):
        '''发送消息的间隔'''
        return self._send_delay
    
    @send_delay.setter
    def send_delay(self,value):
        if not isinstance(value,float):
            raise TypeError(f"send_delay必须是float类型,但传入了{type(value)}:{value}")
        self._send_delay=value
    @property
    def audio_length(self):
        '''微信当前的版本(4.1.9之后有变动)'''
        return self._audio_length
    
    @audio_length.setter
    def audio_length(self,value):
        if not isinstance(value,int):
            raise TypeError(f"audio_length必须是int类型,但传入了{type(value)}:{value}")
        self._audio_length=value
    
    @property
    def clear(self):
        '''发送消息,文件时是否先清除可能已有的内容'''
        return self._clear
    
    @clear.setter
    def clear(self,value):
        if not isinstance(value,bool):
            raise TypeError(f"clear必须是bool类型,但传入了{type(value)}:{value}")
        self._clear=value
    
    @property
    def language(self):
        '''微信当前的语言'''
        return self._language
    
    @language.setter
    def language(self,value):
        if not isinstance(value,str):
            raise TypeError(f"language必须是str类型,但传入了{type(value)}:{value}")
        if value not in {'简体中文','English','繁體中文'}:
            raise ValueError(f"language的取值为{'简体中文','English','繁體中文'}!")
        self._language=value
    
    @property
    def Version(self):
        '''微信当前的版本(4.1.9之后有变动)'''
        return self._Version
    
    @Version.setter
    def Version(self,value):
        if not isinstance(value,str):
            raise TypeError(f"Version必须是str类型,但传入了{type(value)}:{value}")
        self._Version=value
#全局实例
GlobalConfig=globalConfig()
#微信语言检测
def language_detector()->(str|None):
    '''
    通过WechatAppex的命令行参数判断语言版本
    Returns:
        lang:简体中文,繁體中文,English
    '''
    cmdline=''
    lang=None
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if proc.info['name'] and 'wechatappex' in proc.info['name'].lower():
            cmdline=proc.info['cmdline']
            if not cmdline:
                continue
    cmd_str=' '.join(cmdline).lower()
    if '--lang=zh-cn' in cmd_str:lang='简体中文'
    if '--lang=zh-tw' in cmd_str:lang='繁體中文'
    if '--lang=en' in cmd_str:lang='English'
    return lang

def get_weixin_version():
    '''通过查询注册表来获取微信版本
    Returns:
        weixin_version:微信版本号,4.1.x.xx
    '''
    try:
        reg_path=r"Software\Tencent\Weixin"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,reg_path) as key:
            int_version=winreg.QueryValueEx(key,"Version")[0]
            #0xf254186b,0xf25之后是微信版本,每隔一位加个.,最后两位16转10进制就是版本号
            hex_str=hex(int_version)[5:]
            weixin_version=f'{hex_str[0]}.{hex_str[1]}.{hex_str[2]}.{int(hex_str[-2:],16)}'
        return weixin_version
    except Exception:
        raise NotInstalledError
#检测不到只有可能是WechatAppex.exe没有被初始化过(需要打开一次小程序面板或视频号)或微信没有启动
language=language_detector()
Version=get_weixin_version()
GlobalConfig.Version=Version
if language is None:warn(message=f"无法探查到微信当前语言,若需自动检测，请手打打开一次视频号或小程序面板,亦可自行设定",category=LanguageDetectionFailedWarning)
if language is not None:GlobalConfig.language=language
