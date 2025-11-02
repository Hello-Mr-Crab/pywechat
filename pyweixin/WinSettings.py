'''
WinSettins:一些修改windows系统设置的方法\n
--------------------------------
模块:\n
Systemsettings:通过python代码来对windows系统下的一些设置进行修改\n
函数:\n
Systemsettings内的10个方法\n
使用该模块的方法时,你可以:\n
```
from pywechat.WinSettings import Systemsettings
Systemsettings.set_system_volume()
```
或者:\n
```
from pywechat import WinSettings as ws
ws.set_system_volume()
```
'''
import os
import ctypes
import win32com.client
import win32clipboard
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
ES_DISPLAY_REQUIRED=0x00000002
ES_CONTINUOUS=0x80000000
ES_CONTINUOUS=0x80000000
class Systemsettings():
    '''该模块中有7个修改windows系统设置的方法,包括:  \n  
    set_system_volume:设置windows系统音量      \n
    open_listening_mode:开启监听模式,开启后屏幕保持常亮  \n
    close_listening_mode:关闭监听模式,开启后结束屏幕保持常亮  \n
    speaker:调用windows Word中朗读文本的API来进行语音播报  \n
    get_files_in_folder:返回给定绝对路径的文件夹下的所有非文件夹类型文件的绝对路径\n
    copy_file_to_windowsclipboard:将给定绝对路径的文件复制到windows系统下的剪贴板\n
    copy_files_to_windwosclipbioard:将给定绝对路径的文件夹内的所有文件复制到windows系统下的剪贴板\n
    3个判断文件类型的方法,包括:\n
    is_file:判断给定路径的内容是否为文件\n
    is_empty_file:通过文件大小判断给的文件是否是空文件\n
    is_directory:判断给定路径的内容是否是文件夹\n
    '''
    @staticmethod
    def set_system_volume(volume_level:float=100.0):
        """
        设置系统主音量
        Args:
            volume_level:音量级别,范围为0.0到100.0
        """
        if not (0<=volume_level<=100):
            raise ValueError("音量级别必须在0到100之间")
        devices=AudioUtilities.GetSpeakers()
        interface=devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume=cast(interface, POINTER(IAudioEndpointVolume))
        #需要判断是不是静音,倘若是静音需要解除静音,否则计时设置音量成功也还是静音状态
        mute=volume.GetMute()
        if mute==1:
            volume.SetMute(False,None)
        #设置音量
        volume.SetMasterVolumeLevelScalar(volume_level/100, None)

    @staticmethod
    def open_listening_mode(volume:bool=True):
        '''用来开启监听模式,此时电脑将不会息屏且电脑音量设置为100,除非断电否则屏幕保持常亮\n
        关闭时运行close_listening_mode方法即可'''
        ES_DISPLAY_REQUIRED=0x00000002
        ES_CONTINUOUS=0x80000000
        if volume:
            Systemsettings.set_system_volume()
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS|ES_DISPLAY_REQUIRED)

    @staticmethod   
    def close_listening_mode():
        '''用来关闭监听模式,需要与open_listening_mode函数结合使用,单独使用无意义\n''' 
        ES_CONTINUOUS=0x80000000
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)

    @staticmethod   
    def speaker(text:str,times:int=1):
        '''
        text:朗读文本的内容\n
        times:重复朗读次数\n
        调用windows Word中朗读文本的API来进行语音播报\n'''
        speaker=win32com.client.Dispatch("SAPI.SpVoice")
        for _ in range(times):
            speaker.speak(text)

    @staticmethod
    def is_empty_file(file_path:str):
        '''
        file_path:文件路径\n
        该方法通过文件大小判断文件是否为空
        '''
        if os.path.getsize(file_path)==0:
            return True
        return False
    
    @staticmethod
    def is_file(file_path):
        '''
        file_path:文件路径\n
        该方法判断给定路径的内容是否为文件
        '''
        if os.path.isfile(file_path):
            return True
        return False
    
    @staticmethod
    def is_dirctory(folder_path):
        '''
        folder_path:文件夹路径\n
        该方法判断给定路径的内容是否为文件夹
        '''
        if os.path.isdir(folder_path):
            return True
        return False

    @staticmethod
    def get_files_in_folder(folder_path:str):
     '''
     folder_path:文件夹路径\n
     该方法返回给定文件夹下所有非文件夹类型的文件的绝对路径'''
     files=os.listdir(folder_path)#获取的是当前文件夹下所有的文件名称
     absolute_paths=[os.path.abspath(os.path.join(folder_path,file)) for file in files]#当前文件及下所有不是文件夹的所有文件的绝对路径
     files_in_folder=[file for file in absolute_paths if not Systemsettings.is_dirctory(file)]
     files_in_folder=[file for file in files_in_folder if Systemsettings.is_file(file)]
     files_in_folder=[file for file in files_in_folder if not Systemsettings.is_empty_file(file)]
     return files_in_folder
    
    @staticmethod
    def copy_files_to_windowsclipboard(filepaths_list:list[str]):
        '''
        filepaths_list:文件路径列表\n
        该方法将给定绝对路径的路径列表内所有文件复制到windows系统下的剪贴板\n
        '''
        os.environ.update({"__COMPAT_LAYER":"RUnAsInvoker"})#添加管理员权限
        filepaths_list=[file_path.replace('/','\\') for file_path in filepaths_list]
        class DROPFILES(ctypes.Structure):
            _fields_ = [
                ("pFiles", ctypes.c_uint),
                ("x", ctypes.c_long),
                ("y", ctypes.c_long),
                ("fNC", ctypes.c_int),
                ("fWide", ctypes.c_bool),
            ]
        pDropFiles = DROPFILES()
        pDropFiles.pFiles = ctypes.sizeof(DROPFILES)
        pDropFiles.fWide = True
        #获取文件绝对路径
        files = ("\0".join(filepaths_list)).replace("/", "\\")
        data = files.encode("U16")[2:] + b"\0\0"        #结尾一定要两个\0\0字符，这是规定！
        win32clipboard.OpenClipboard()  #打开剪贴板（独占）
        try:
            #若要将信息放在剪贴板上，首先需要使用 EmptyClipboard 函数清除当前的剪贴板内容
            win32clipboard.EmptyClipboard() #清空当前的剪贴板信息
            win32clipboard.SetClipboardData(win32clipboard.CF_HDROP,bytes(pDropFiles)+data) #设置当前剪贴板数据
        except Exception as e:
            print("复制文件到剪贴板时出错！")
        finally:
            win32clipboard.CloseClipboard() #无论什么情况，都关闭剪贴板

    @staticmethod
    def copy_file_to_windowsclipboard(file_path:str):
        '''file_path:文件的绝对路径\n
        该方法将给定绝对路径的文件复制到windows系统下的剪贴板\n'''
        os.environ.update({"__COMPAT_LAYER":"RUnAsInvoker"})#添加管理员权限
        class DROPFILES(ctypes.Structure):
            _fields_ = [
                ("pFiles", ctypes.c_uint),
                ("x", ctypes.c_long),
                ("y", ctypes.c_long),
                ("fNC", ctypes.c_int),
                ("fWide", ctypes.c_bool),
            ]
        pDropFiles = DROPFILES()
        pDropFiles.pFiles = ctypes.sizeof(DROPFILES)
        pDropFiles.fWide = True
        #获取文件绝对路径
        files = file_path.replace("/", "\\")
        data=files.encode("U16")[2:] + b"\0\0"     #结尾一定要两个\0\0字符，这是规定！
        win32clipboard.OpenClipboard()  #打开剪贴板（独占）
        try:
            #若要将信息放在剪贴板上，首先需要使用 EmptyClipboard 函数清除当前的剪贴板内容
            win32clipboard.EmptyClipboard() #清空当前的剪贴板信息
            win32clipboard.SetClipboardData(win32clipboard.CF_HDROP,bytes(pDropFiles)+data)#设置当前剪贴板数据
        except Exception:
            print("复制文件到剪贴板时出错！")
        finally:
            win32clipboard.CloseClipboard() #c出错后关闭剪贴板
    
    @staticmethod
    def copy_text_to_windowsclipboard(text:str):
        '''text:字符串\n
        该方法将给定绝对路径的文件复制到windows系统下的剪贴板\n'''
        os.environ.update({"__COMPAT_LAYER":"RUnAsInvoker"})#添加管理员权限
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text,win32clipboard.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()

    @staticmethod
    def convert_long_text_to_txt(LongText:str):
        '''
        Longtext:长字符串\n
        该方法将长字符串转换为txt文件,并将该文件复制到windows系统下的剪贴板\n
        '''
        f=open("LongText.txt",'w',encoding="utf-8")
        f.write(LongText)
        f.close()
        path=os.path.join(os.getcwd(),"LongText.txt")
        Systemsettings.copy_file_to_windowsclipboard(path)

def set_system_volume(volume_level:float=100.0):
    """
    设置系统主音量
    Args:
        volume_level:音量级别,范围为0.0到100.0
    """
    if not (0<=volume_level<=100):
        raise ValueError("音量级别必须在0到100之间")
    devices=AudioUtilities.GetSpeakers()
    interface=devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume=cast(interface, POINTER(IAudioEndpointVolume))
    #需要判断是不是静音,倘若是静音需要解除静音,否则计时设置音量成功也还是静音状态
    mute=volume.GetMute()
    if mute==1:
        volume.SetMute(False,None)
    #设置音量
    volume.SetMasterVolumeLevelScalar(volume_level/100, None)

def open_listening_mode(volume:bool=True):
        '''用来开启监听模式,此时电脑音量设置为100,除非断电否则屏幕保持常亮\n'''
        ES_DISPLAY_REQUIRED=0x00000002
        ES_CONTINUOUS=0x80000000
        if volume:
            Systemsettings.set_system_volume()
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS|ES_DISPLAY_REQUIRED)

def close_listening_mode():
        '''用来关闭监听模式,需要与open_listening_mode函数结合使用,单独使用无意义\n''' 
        ES_CONTINUOUS=0x80000000
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)

def speaker(text:str,times:int=1):
        '''
        text:朗读文本的内容\n
        times:重复朗读次数\n
        调用windows系统下的Word中的朗读文本的API来进行语音播报\n
        '''
        speaker=win32com.client.Dispatch("SAPI.SpVoice")
        for _ in range(times):
            speaker.speak(text)

def is_empty_file(file_path):
    '''
    file_path:文件夹路径\n
    该方法通过文件大小判断文件是否为空\n
    '''
    if os.path.getsize(file_path)==0:
        return True
    return False
    
def is_file(file_path):
    '''
    file_path:文件夹路径\n
    该方法判断给定路径的内容是否为文件\n
    '''
    if os.path.isfile(file_path):
        return True
    return False

def is_dirctory(file_path):
    '''
    file_path:文件夹路径\n
    该方法判断给定路径的内容是否为文件\n
    '''
    if os.path.isdir(file_path):
        return True
    return False

def get_files_in_folder(folder_path:str):
    '''
    folder_path:文件夹路径\n
    该函数返回给定文件夹下所有非文件夹类型的文件的绝对路径'''
    files=os.listdir(folder_path)#获取的是当前文件夹下所有的文件名称
    absolute_paths=[os.path.abspath(os.path.join(folder_path,file)) for file in files]#当前文件及下所有不是文件夹的所有文件的绝对路径
    files_in_folder=[file for file in absolute_paths if not Systemsettings.is_dirctory(file)]
    files_in_folder=[file for file in files_in_folder if Systemsettings.is_file(file)]
    files_in_folder=[file for file in files_in_folder if not Systemsettings.is_empty_file(file)]
    return files_in_folder

def copy_files_to_windowsclipboard(filepaths_list:list[str]):
    '''
    filepaths_list:所有给定文件的绝对路径列表\n
    该函数将给定绝对路径的路径列表内所有文件复制到windows系统下的剪贴板\n'''
    os.environ.update({"__COMPAT_LAYER":"RUnAsInvoker"})#添加管理员权限
    class DROPFILES(ctypes.Structure):
        _fields_ = [
            ("pFiles", ctypes.c_uint),
            ("x", ctypes.c_long),
            ("y", ctypes.c_long),
            ("fNC", ctypes.c_int),
            ("fWide", ctypes.c_bool),
        ]
    pDropFiles = DROPFILES()
    pDropFiles.pFiles = ctypes.sizeof(DROPFILES)
    pDropFiles.fWide = True
    #获取文件绝对路径
    files = ("\0".join(filepaths_list)).replace("/", "\\")
    data = files.encode("U16")[2:] + b"\0\0"        #结尾一定要两个\0\0字符，这是规定！
    win32clipboard.OpenClipboard()  #打开剪贴板（独占）
    try:
        #若要将信息放在剪贴板上，首先需要使用 EmptyClipboard 函数清除当前的剪贴板内容
        win32clipboard.EmptyClipboard() #清空当前的剪贴板信息
        win32clipboard.SetClipboardData(win32clipboard.CF_HDROP,bytes(pDropFiles)+data) #设置当前剪贴板数据
    except Exception as e:
        print("复制文件到剪贴板时出错！")
    finally:
        win32clipboard.CloseClipboard() #无论什么情况，都关闭剪贴板

def copy_file_to_windowsclipboard(file_path:str):
    '''
    file_path:文件的绝对路径\n
    该函数将给定绝对路径的文件复制到windows系统下剪贴板\n'''
    os.environ.update({"__COMPAT_LAYER":"RUnAsInvoker"})#添加管理员权限
    class DROPFILES(ctypes.Structure):
        _fields_ = [
            ("pFiles", ctypes.c_uint),
            ("x", ctypes.c_long),
            ("y", ctypes.c_long),
            ("fNC", ctypes.c_int),
            ("fWide", ctypes.c_bool),
        ]
    pDropFiles = DROPFILES()
    pDropFiles.pFiles = ctypes.sizeof(DROPFILES)
    pDropFiles.fWide = True
    files = file_path.replace("/", "\\")
    data=files.encode("U16")[2:] + b"\0\0"       #结尾一定要两个\0\0字符，这是规定！
    win32clipboard.OpenClipboard()  #打开剪贴板（独占）
    try:
        win32clipboard.EmptyClipboard() #清空当前的剪贴板信息
        win32clipboard.SetClipboardData(win32clipboard.CF_HDROP,bytes(pDropFiles)+data) #设置当前剪贴板数据
    except Exception:
        print("复制文件到剪贴板时出错！")
    finally:
        win32clipboard.CloseClipboard() #无论什么情况，都关闭剪贴板

def copy_text_to_windowsclipboard(text):
    '''text:字符串\n
    该方法将给定绝对路径的文件复制到windows系统下的剪贴板\n'''
    os.environ.update({"__COMPAT_LAYER":"RUnAsInvoker"})#添加管理员权限
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(text,win32clipboard.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()

def convert_long_text_to_txt(text):
    '''
    Longtext:长字符串\n
    该方法将长字符串转换为txt文件,并将该文件复制到windows系统下的剪贴板\n
    '''
    f=open("LongText.txt",'w',encoding="utf-8")
    f.write(text)
    f.close()
    path=os.path.join(os.getcwd(),"LongText.txt")
    Systemsettings.copy_file_to_windowsclipboard(path)

    