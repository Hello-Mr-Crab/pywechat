'''
WinSettings
===========
该模块中封装了SystemSettings这个静态类,主要用来修改和查询Windows操作系统的一些设置


SystemSettings:
-------------
    - `set_system_volume`: 修改系统音量
    - `open_listening_mode`: 开启监听模式(保证屏幕不息屏)
    - `close_listening_mode`: 关闭监听模式(配合open_listening_mode使用)
    - `copy_file_to_windowsclipboard`: 将文件粘贴到windows剪贴板
    - `copy_files_to_windowsclipboard`: 将多个文件粘贴到windows剪贴板
    - `copy_text_to_windwosclipboard`: 将文本粘贴到windows剪贴板
    - `copy_files`: 使用复制粘贴的方式将文件迁移(主要是导出微信聊天文件时要用到)
    - `save_pasted_image`:将复制到剪贴板的图片数据保存到指定路径

Examples:
========
使用该模块的方法时,你可以:

    >>> from pyweixin.WinSettings import SystemSettings
    >>> SystemSettings.copy_file_to_windowsclipboard('test.jopg')

或者:

    >>> from pyweixin import SystemSettings
    >>> SystemSettings.copy_file_to_windowsclipboard('test.jopg')

'''
import os
import shutil
import ctypes
import win32com.client
import win32clipboard
import ctypes
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from PIL import Image
import io

#常量
ES_DISPLAY_REQUIRED=0x00000002
ES_CONTINUOUS=0x80000000
ES_CONTINUOUS=0x80000000

class SystemSettings():
    '''
    修改和查询windows系统设置的一些方法
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
        volume=cast(interface,POINTER(IAudioEndpointVolume))
        #需要判断是不是静音,倘若是静音需要解除静音,否则即使设置音量成功也还是静音状态
        mute=volume.GetMute()
        if mute==1:
            volume.SetMute(False,None)
        #设置音量
        volume.SetMasterVolumeLevelScalar(volume_level/100,None)

    @staticmethod
    def open_listening_mode(volume:bool=True):
        '''运行后电脑将不会息屏且电脑音量设置为100,除非断电否则屏幕保持常亮
        关闭时运行close_listening_mode方法即可'''
        ES_DISPLAY_REQUIRED=0x00000002
        ES_CONTINUOUS=0x80000000
        if volume:
            SystemSettings.set_system_volume()
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS|ES_DISPLAY_REQUIRED)

    @staticmethod   
    def close_listening_mode():
        '''需要与open_listening_mode函数结合使用,单独使用无意义''' 
        ES_CONTINUOUS=0x80000000
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)

    @staticmethod   
    def speaker(text:str,times:int=1):
        '''
        调用windows Word中朗读文本的API来进行语音播报
        Args:
            text:朗读文本的内容
            times:重复朗读次数
        '''
        speaker=win32com.client.Dispatch("SAPI.SpVoice")
        for _ in range(times):
            speaker.speak(text)

    @staticmethod
    def copy_files_to_windowsclipboard(filepaths_list:list[str]):
        '''
        该方法将给定绝对路径的路径列表内所有文件复制到windows系统下的剪贴板
        Args:
            filepaths_list:文件路径列表
        '''
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
        data = files.encode("U16")[2:] + b"\0\0"#结尾一定要两个\0\0字符，这是规定！
        win32clipboard.OpenClipboard()#打开剪贴板（独占）
        try:
            #若要将信息放在剪贴板上，首先需要使用 EmptyClipboard 函数清除当前的剪贴板内容
            win32clipboard.EmptyClipboard() #清空当前的剪贴板信息
            win32clipboard.SetClipboardData(win32clipboard.CF_HDROP,bytes(pDropFiles)+data) #设置当前剪贴板数据
        except Exception as e:
            print(f"复制文件到剪贴板时出错！{e}")
        finally:
            win32clipboard.CloseClipboard()#最后,无论什么情况都关闭剪贴板

    @staticmethod
    def copy_file_to_windowsclipboard(file_path:str):
        '''
        该方法将给定绝对路径的文件复制到windows系统下的剪贴板
        Args:
            file_path:文件的绝对路径
        '''
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
        '''
        该方法使用pywin32的windowsAPI复制文本到剪贴板
        Args:
            text:字符串
        '''
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text,win32clipboard.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()

    @staticmethod
    def convert_long_text_to_txt(LongText:str):
        '''
        该方法将长字符串转换为txt文件,并将该文件复制到windows系统下的剪贴板
        Args:
            Longtext:长字符串
        '''
        f=open("LongText.txt",'w',encoding="utf-8")
        f.write(LongText)
        path=os.path.join(os.getcwd(),"LongText.txt")
        f.close()
        SystemSettings.copy_file_to_windowsclipboard(path)


    @staticmethod
    def copy_files(file_paths:list[str],target_folder:str):
        '''
        该方法用来将文件路径列表中的所有文件到复制到目标文件夹
        Args:
            file_paths: 文件路径列表，例如 ['/path/to/file1.txt','/path/to/file2.jpg']
            target_folder: 目标文件夹路径，例如 '/path/to/destination/'
        '''
        os.makedirs(target_folder, exist_ok=True)
        for file_path in file_paths:
            #目标文件夹中没有该文件时再复制
            if not os.path.exists(os.path.join(target_folder,os.path.basename(file_path))):
                try:
                    shutil.copy2(file_path, target_folder)
                except Exception:
                    pass
    
    @staticmethod
    def copy_file(file_path:str,target_folder:str):
        '''
        将给定file_path下的文件到复制到目标文件夹
        Args:
            file_path: 文件绝对路径:'/path/to/file2.jpg'
            target_folder: 目标文件夹路径，例如 '/path/to/destination/'
        '''
        os.makedirs(target_folder, exist_ok=True)
        if not os.path.exists(os.path.join(target_folder,os.path.basename(file_path))):
            shutil.copy2(file_path, target_folder)
    
    @staticmethod
    def save_pasted_image(img_path:str):
        '''
        将复制到剪贴板的图片数据并保存到指定路径
        Args:
            img_path:图片待保存路径
        '''
        win32clipboard.OpenClipboard()
        if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_DIB):
            data=win32clipboard.GetClipboardData(win32clipboard.CF_DIB)
            image=Image.open(io.BytesIO(data))
            image.save(img_path)
        win32clipboard.CloseClipboard()