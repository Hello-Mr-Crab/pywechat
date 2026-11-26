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
    GlobalConfig.language='English'#自动检测,无需手动传入
    GlobalConfig.window_size=(900,900)#自动调整,无需手动传入
    GlobalConfig.load_delay=3.5
    GlobalConfig.is_maximize=True
    GlobalConfig.close_weixin=False
    Navigator.search_channels(search_content='微信4.0')
    Navigator.search_miniprogram(name='问卷星')
    Navigator.search_official_account(name='微信')
    ```
'''

#pyweixin全局参数配置
import os
import re
import sys
import glob
import ctypes
from warnings import warn
from .Warnings import LanguageDetectionFailedWarning

#psutil 在 Linux/macOS 上同样是跨平台的,但没有安装时不应该让整个包导入失败
try:
    import psutil
except Exception:  # pragma: no cover - 环境相关
    psutil=None

IS_WINDOWS=sys.platform.startswith('win')
if IS_WINDOWS:
    import winreg
else:
    winreg=None#Linux/macOS 上没有注册表
class globalConfig:
    '''位置参数全局配置'''
    _instance=None
    def __new__(cls):
        #初始化默认值
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._is_maximize=False
            cls._instance._close_weixin=False
            cls._instance._load_delay=3.5
            cls._instance._search_pages=5
            cls._instance._window_maximize=False
            cls._instance._send_delay=0.2
            cls._instance._audio_length=60
            cls._instance._window_size=(1000,1000)
            cls._instance._language=None
            cls._instance._Version=None
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
        if self._window_size is None:    
            self._window_size=self._adjust_window_size()
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
        '''发送语音的长度(微信4.1.9以后可以使用)'''
        return self._audio_length
    
    @audio_length.setter
    def audio_length(self,value):
        if not isinstance(value,int):
            raise TypeError(f"audio_length必须是int类型,但传入了{type(value)}:{value}")
        self._audio_length=value
    
    @property
    def Version(self):
        '''微信当前版本'''
        if self._Version is None:
            try:
                self._Version=self._get_weixin_version()
            except Exception:
                warn(f"获取微信版本失败,使用默认值'4.1.9.30'", RuntimeWarning)
                self._Version='4.1.9.30'
        return self._Version

    @Version.setter
    def Version(self, value):
        if not isinstance(value, str):
            raise TypeError(f"version必须是str类型,但传入了{type(value)}: {value}")
        self._Version=value #允许手动设置覆盖缓存

    @property
    def language(self):
        '''微信当前语言'''
        if self._language is None:
            self._language=self._language_detector()
            if self._language is None:
                warn("语言检测失败，使用默认 '简体中文'", LanguageDetectionFailedWarning)
                self._language='简体中文'
        return self._language

    @language.setter
    def language(self, value):
        if not isinstance(value, str):
            raise TypeError(f"language必须是str类型,但传入了 {type(value)}: {value}")
        if value not in {'简体中文', 'English', '繁體中文'}:
            raise ValueError(f"不支持的语言: {value}")
        self._language=value  #允许手动设置覆盖缓存

    def _language_detector(self)->(str|None):
        '''
        通过WechatAppex的命令行参数判断语言版本
        Returns:
            lang:简体中文,繁體中文,English
        '''
        lang=None
        cmdline=''
        cmdlines=[]
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if proc.info['name'] and 'wechatappex' in proc.info['name'].lower():
                cmdlines.append(proc.info['cmdline'])#wechatappex.exr不止一个！所以把所有的exe命令行参数都保留
        for cmdline in cmdlines:
            cmd_str=' '.join(cmdline).lower()
            if '--type=renderer' in cmd_str:
                if '--lang=zh-cn' in cmd_str:lang='简体中文'
                if '--lang=zh-tw' in cmd_str:lang='繁體中文'
                if '--lang=en' in cmd_str:lang='English'
        return lang

    def _get_weixin_version(self):
        '''获取微信版本号。
        Windows 上查注册表,Linux 上从可执行文件里提取字符串。
        Returns:
            weixin_version:微信版本号,4.1.x.xx
        '''
        if not IS_WINDOWS:
            return self._get_weixin_version_linux()
        try:
            reg_path=r"Software\Tencent\Weixin"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,reg_path) as key:
                int_version=winreg.QueryValueEx(key,"Version")[0]
                #0xf254186b,0xf25之后是微信版本,每隔一位加个.,最后两位16转10进制就是版本号
                hex_str=hex(int_version)[5:]
                weixin_version=f'{hex_str[0]}.{hex_str[1]}.{int(hex_str[2],16)}.{int(hex_str[-2:],16)}'
            return weixin_version
        except Exception:
            return None
    
    def _get_weixin_version_linux(self):
        '''Linux 上没有注册表,版本号只能从二进制/包信息里取。

        查找顺序:
            1. 环境变量 `PYWEIXIN_WECHAT_VERSION`(最高优先级,便于测试)
            2. 可执行文件里的 `4.x.y.z` 字符串
            3. `/opt/wechat/version` 之类的版本文件
        Returns:
            weixin_version:形如 '4.1.13.29',取不到时返回 None(由调用方回退默认值)
        '''
        override=os.environ.get('PYWEIXIN_WECHAT_VERSION')
        if override:
            return override.strip()
        candidates=['/opt/wechat/wechat','/opt/weixin/weixin','/usr/bin/wechat','/usr/lib/wechat/wechat']
        for exe in candidates:
            if not os.path.isfile(exe):
                continue
            found=self._scan_version_strings(exe)
            if found:
                return found
        for path in glob.glob('/opt/wechat/*version*')+glob.glob('/opt/weixin/*version*'):
            try:
                text=open(path,'r',encoding='utf-8',errors='ignore').read(4096)
            except OSError:
                continue
            match=re.search(r'\b(4\.\d+\.\d+\.\d+)\b',text)
            if match:
                return match.group(1)
        return None

    @staticmethod
    def _scan_version_strings(path:str,chunk_size:int=8*1024*1024):
        '''分块扫描二进制里形如 4.1.13.29 的版本号,取最大的一个(避免误匹配依赖库版本)'''
        pattern=re.compile(rb'(?<![0-9.])(4\.\d{1,2}\.\d{1,2}\.\d{1,2})(?![0-9.])')
        versions=set()
        try:
            with open(path,'rb') as fh:
                tail=b''
                while True:
                    chunk=fh.read(chunk_size)
                    if not chunk:
                        break
                    for match in pattern.finditer(tail+chunk):
                        versions.add(match.group(1).decode())
                    tail=chunk[-32:]
        except OSError:
            return None
        if not versions:
            return None
        def key(v):
            return tuple(int(x) for x in v.split('.'))
        return max(versions,key=key)

    def _adjust_window_size(self) -> tuple[int, int]:
        '''固定比例调整微信窗口大小,先定高度,再定宽度,高度取全局分辨率80%,宽略比高大一些,窗口整体是一个正方形'''
        if not IS_WINDOWS:
            return (1200,1100)
        user32=ctypes.windll.user32
        try:
            dpi=user32.GetDpiForWindow(self.hwnd)
            sc_height=user32.GetSystemMetricsForDpi(1, dpi)
        except:
            sc_height=user32.GetSystemMetrics(1)
            dpi=96
        height=int(0.8*sc_height)
        width=int(1.1*height)
        return width,height
   
#全局实例
GlobalConfig=globalConfig()