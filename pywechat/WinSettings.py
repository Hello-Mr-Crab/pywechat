'''
WinSettins:一些修改windows系统设置的方法\n
--------------------------------
模块:\n
SystemSettings:通过python代码来对windows系统下的一些设置进行修改\n
函数:\n
SystemSettings内的10个方法\n
使用该模块的方法时,你可以:\n
```
from pywechat.WinSettings import SystemSettings
SystemSettings.set_system_volume()
```
'''
import os
import ctypes
import shutil
from io import BytesIO
import win32com.client
import win32clipboard
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities,IAudioEndpointVolume
ES_DISPLAY_REQUIRED=0x00000002
ES_CONTINUOUS=0x80000000
ES_CONTINUOUS=0x80000000

class SystemSettings():
    '''该模块中主要包含了一些关于windows系统设置的方法,包括:\n  
    close_listening_mode:关闭监听模式,开启后结束屏幕保持常亮\n
    copy_file:将单个文件从原始文件夹复制到目标文件夹\n
    copy_files:将多个文件从原始文件夹复制到目标文件夹\n
    copy_file_to_windowsclipboard:将给定绝对路径的文件复制到windows系统下的剪贴板\n
    copy_files_to_windwosclipbioard:将给定绝对路径的文件夹内的所有文件复制到windows系统下的剪贴板\n
    is_file:判断给定路径的内容是否为文件\n
    is_empty_file:通过文件大小判断给的文件是否是空文件\n
    is_directory:判断给定路径的内容是否是文件夹\n
    get_files_in_folder:返回给定文件夹下第一级目录内所有非空文件的绝对路径\n
    open_listening_mode:开启监听模式,开启后屏幕保持常亮\n
    speaker:调用windowsWord中朗读文本的API来进行语音播报\n
    set_english_input:强制将当前输入法转为系统默认英文输入法\n
    set_system_volume:设置windows系统音量\n
    '''
    @staticmethod
    def set_system_volume(volume_level:float=100.0):
        '''
        设置系统主音量
        Args:
            volume_level:音量级别,范围为0.0到100.0
        '''
        if not (0<=volume_level<=100):
            raise ValueError("音量级别必须在0到100之间!")
        devices=AudioUtilities.GetSpeakers()
        interface=devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume=cast(interface, POINTER(IAudioEndpointVolume))
        #需要判断是不是静音,倘若是静音需要解除静音,否则即使设置音量成功也还是静音状态
        mute=volume.GetMute()
        if mute==1:
            volume.SetMute(False,None)
        #设置音量
        volume.SetMasterVolumeLevelScalar(volume_level/100, None)

    @staticmethod
    def open_listening_mode(full_volume:bool=True):
        '''用来开启监听模式,此时电脑将不会息屏且电脑音量设置为100,除非断电否则屏幕保持常亮\n
        关闭时运行close_listening_mode方法即可'''
        ES_DISPLAY_REQUIRED=0x00000002
        ES_CONTINUOUS=0x80000000
        if full_volume:
            SystemSettings.set_system_volume()
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS|ES_DISPLAY_REQUIRED)

    @staticmethod   
    def close_listening_mode():
        '''用来关闭监听模式,需要与open_listening_mode函数结合使用,单独使用无意义\n''' 
        ES_CONTINUOUS=0x80000000
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)

    @staticmethod   
    def speaker(text:str,times:int=1):
        '''
        该方法通过windows com接口调用Word中朗读文本的API来进行语音播报\n
        Args:
            text:朗读文本的内容\n
            times:重复朗读次数\n
        '''
        speaker=win32com.client.Dispatch("SAPI.SpVoice")
        for _ in range(times):
            speaker.speak(text)

    @staticmethod
    def is_empty_file(file_path:str):
        '''
        该方法封装os.path.getsize函数通过文件大小来判断文件是否为空
        Args:
            file_path:文件路径\n
        '''
        if os.path.getsize(file_path)==0:
            return True
        return False
    
    @staticmethod
    def is_empty_folder(folder_path):
        '''该方法通过扫描文件夹内部是否东西来判断文件夹是否为空'''
        with os.scandir(folder_path) as it:
            return not any(it)

    @staticmethod
    def get_files_in_folder(folder_path:str):
        '''
        该函数返回给定文件夹下第一级目录内所有非空文件的绝对路径\n
        如果你传入的文件夹里有很多文件夹但只有一个.pdf类型文件\n
        那么最后返回的是这个pdf文件的路径\n
        该函数主要用来配合send_files函数来使用\n
        Args:
            folder_path:文件夹路径\n
        '''
        files=os.listdir(folder_path)#获取的是当前文件夹下所有的文件名称
        absolute_paths=[os.path.abspath(os.path.join(folder_path,file)) for file in files]#当前文件及下所有不是文件夹的所有文件的绝对路径
        files_in_folder=[file for file in absolute_paths if not SystemSettings.is_dirctory(file)]
        files_in_folder=[file for file in files_in_folder if SystemSettings.is_file(file)]
        files_in_folder=[file for file in files_in_folder if not SystemSettings.is_empty_file(file)]
        return files_in_folder
    
    @staticmethod
    def copy_files_to_windowsclipboard(filepaths_list:list[str]):
        '''
        该方法将给定绝对路径的路径列表内所有文件复制到windows系统下的剪贴板\n
        Args:
            filepaths_list:文件路径列表\n
        '''
        filepaths_list=[file_path.replace('/','\\') for file_path in filepaths_list]
        class DROPFILES(ctypes.Structure):
            _fields_=[
                ("pFiles", ctypes.c_uint),
                ("x", ctypes.c_long),
                ("y", ctypes.c_long),
                ("fNC", ctypes.c_int),
                ("fWide", ctypes.c_bool),
            ]
        pDropFiles=DROPFILES()
        pDropFiles.pFiles=ctypes.sizeof(DROPFILES)
        pDropFiles.fWide=True
        #获取文件绝对路径
        files=("\0".join(filepaths_list)).replace("/", "\\")
        data=files.encode("U16")[2:] + b"\0\0"        #结尾一定要两个\0\0字符，这是规定！
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
        '''
        该方法将给定绝对路径的文件复制到windows系统下的剪贴板\n
        Args:
            file_path:文件的绝对路径\n
        '''
        class DROPFILES(ctypes.Structure):
            _fields_=[
                ("pFiles", ctypes.c_uint),
                ("x", ctypes.c_long),
                ("y", ctypes.c_long),
                ("fNC", ctypes.c_int),
                ("fWide", ctypes.c_bool),
            ]
        pDropFiles=DROPFILES()
        pDropFiles.pFiles=ctypes.sizeof(DROPFILES)
        pDropFiles.fWide=True
        #获取文件绝对路径
        files=file_path.replace("/", "\\")
        data=files.encode("U16")[2:] + b"\0\0"     #结尾一定要两个\0\0字符，这是规定！
        win32clipboard.OpenClipboard()  #打开剪贴板（独占）
        try:
            #若要将信息放在剪贴板上，首先需要使用 EmptyClipboard 函数清除当前的剪贴板内容
            win32clipboard.EmptyClipboard() #清空当前的剪贴板信息
            win32clipboard.SetClipboardData(win32clipboard.CF_HDROP,bytes(pDropFiles)+data)#设置当前剪贴板数据
        except Exception:
            print("复制文件到剪贴板时出错！")
        finally:
            win32clipboard.CloseClipboard() #出错后关闭剪贴板
    
    @staticmethod
    def copy_screenshot_to_clipboard(screenshot):
        '''
        该方法用来将pywinauto的capture_as_image()\n
        方法捕获的控件截图(Pillow Image对象)复制到windows系统下的剪贴板
        Args:
            screenshot:xxx.capture_as_image(),xxx为某个UI控件
        '''
        output=BytesIO()
        screenshot.save(output,format="BMP")#必须保存为BMP格式
        data=output.getvalue()[14:]#去掉BMP文件头
        output.close()
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()

    @staticmethod
    def copy_text_to_windowsclipboard(text:str):
        '''
        该方法将给定绝对路径的文件复制到windows系统下的剪贴板\n
        Args:
            text:字符串\n
        '''
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text,win32clipboard.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()

    @staticmethod
    def convert_long_text_to_txt(LongText:str):
        '''
        该方法将长字符串转换为txt文件,并将该文件复制到windows系统下的剪贴板\n
        Args:
            Longtext:长字符串\n
        '''
        f=open("长文本消息.txt",'w',encoding="utf-8")
        f.write(LongText)
        f.close()
        path=os.path.join(os.getcwd(),"长文本消息.txt")
        SystemSettings.copy_file_to_windowsclipboard(path)
    
    @staticmethod
    def copy_files(file_paths:list[str],target_folder:str):
        '''
        该方法用来将文件路径列表中的所有文件到复制到目标文件夹\n
        Args:
            file_paths: 文件路径列表，例如 ['/path/to/file1.txt', '/path/to/file2.jpg']
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
        该方法同来将给定file_path下的文件到复制到目标文件夹target_folder\n
        Args:
            file_path: 文件绝对路径:'/path/to/file2.jpg'
            target_folder: 目标文件夹路径，例如 '/path/to/destination/'
        '''
        os.makedirs(target_folder, exist_ok=True)
        if not os.path.exists(os.path.join(target_folder,os.path.basename(file_path))):
            try:
                shutil.copy2(file_path, target_folder)
            except Exception:
                pass
    
    @staticmethod
    def set_english_input():
        '''
        该方法用来强制将输入法切换为windows系统内置英文输入法\n
        无论是pywinauto还是pyautogui只要使用type_keys或者typewrite类似的打字的方法时\n
        输入中文时,写出来有可能是一堆乱码(第三方输入法中文状态下)\n
        '''
        try:
            #获取当前活动窗口的线程ID
            hwnd=ctypes.windll.user32.GetForegroundWindow()
            thread_id=ctypes.windll.user32.GetWindowThreadProcessId(hwnd, 0)
            #加载美式键盘布局 
            klid=ctypes.windll.user32.LoadKeyboardLayoutW("00000409", 1)       
            #为当前线程设置键盘布局
            ctypes.windll.user32.ActivateKeyboardLayout(klid, 0)
            #发送WM_INPUTLANGCHANGEREQUEST消息
            ctypes.windll.user32.PostMessageW(hwnd, 0x0050, 0, klid)
        except Exception as e:
            print(f"设置英文输入法时出错: {e}")

def set_system_volume(volume_level:float=100.0):
    '''
    该函数用来设置系统主音量\n
    Args:
        volume_level:音量级别,范围为0.0到100.0,默认100.0
    '''
    if not (0<=volume_level<=100):
        raise ValueError("音量级别必须在0到100之间")
    devices=AudioUtilities.GetSpeakers()
    interface=devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume=cast(interface, POINTER(IAudioEndpointVolume))
    #需要判断是不是静音,倘若是静音需要解除静音,否则 设置音量成功也还是静音状态
    mute=volume.GetMute()
    if mute==1:
        volume.SetMute(False,None)
    #设置音量
    volume.SetMasterVolumeLevelScalar(volume_level/100, None)

def open_listening_mode(full_volume:bool=True):
    '''用来开启监听模式,此时电脑音量设置为100,除非断电否则屏幕保持常亮\n'''
    ES_DISPLAY_REQUIRED=0x00000002
    ES_CONTINUOUS=0x80000000
    if full_volume:
        SystemSettings.set_system_volume()
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS|ES_DISPLAY_REQUIRED)

def close_listening_mode():
    '''用来关闭监听模式,需要与open_listening_mode函数结合使用,单独使用无意义\n''' 
    ES_CONTINUOUS=0x80000000
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)

def speaker(text:str,times:int=1):
    '''
    Args:
        text:朗读文本的内容\n
        times:重复朗读次数\n
    调用windows系统下的Word中的朗读文本的API来进行语音播报\n
    '''
    speaker=win32com.client.Dispatch("SAPI.SpVoice")
    for _ in range(times):
        speaker.speak(text)

def is_empty_file(file_path):
    '''
    Args:
        file_path:文件夹路径\n
    该函数封装os.path.getsize函数来根据文件大小判断文件是否为空\n
    '''
    if os.path.getsize(file_path)==0:
        return True
    return False
    
def is_empty_folder(folder_path):
    '''该函数通过扫描文件夹内部是否东西来判断文件夹是否为空'''
    with os.scandir(folder_path) as it:
        return not any(it)

def get_files_in_folder(folder_path:str):
    '''
    该函数返回给定文件夹下第一级目录内所有非空文件的绝对路径\n
    如果你传入的文件夹里有很多文件夹但只有一个.pdf类型文件\n
    那么最后返回的是这个pdf文件的路径\n
    该函数主要用来配合send_files函数来使用\n
    Args:
        folder_path:文件夹路径\n
    '''
    files=os.listdir(folder_path)#获取的是当前文件夹下所有的文件名称
    absolute_paths=[os.path.abspath(os.path.join(folder_path,file)) for file in files]#当前文件及下所有不是文件夹的所有文件的绝对路径
    files_in_folder=[file for file in absolute_paths if not SystemSettings.is_dirctory(file)]
    files_in_folder=[file for file in files_in_folder if SystemSettings.is_file(file)]
    files_in_folder=[file for file in files_in_folder if not SystemSettings.is_empty_file(file)]
    return files_in_folder

def copy_files_to_windowsclipboard(filepaths_list:list[str]):
    '''
    该函数将给定绝对路径的路径列表内所有文件复制到windows系统下的剪贴板\n
    Args:
        filepaths_list:所有给定文件的绝对路径列表\n
    '''
    class DROPFILES(ctypes.Structure):
        _fields_=[
            ("pFiles", ctypes.c_uint),
            ("x", ctypes.c_long),
            ("y", ctypes.c_long),
            ("fNC", ctypes.c_int),
            ("fWide", ctypes.c_bool),
        ]
    pDropFiles=DROPFILES()
    pDropFiles.pFiles=ctypes.sizeof(DROPFILES)
    pDropFiles.fWide=True
    #获取文件绝对路径
    files=("\0".join(filepaths_list)).replace("/", "\\")
    data=files.encode("U16")[2:] + b"\0\0"        #结尾一定要两个\0\0字符，这是规定！
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
    该函数将给定绝对路径的文件复制到windows系统下剪贴板\n
    Args:
        file_path:文件的绝对路径\n
    '''
    class DROPFILES(ctypes.Structure):
        _fields_=[
            ("pFiles", ctypes.c_uint),
            ("x", ctypes.c_long),
            ("y", ctypes.c_long),
            ("fNC", ctypes.c_int),
            ("fWide", ctypes.c_bool),
        ]
    pDropFiles=DROPFILES()
    pDropFiles.pFiles=ctypes.sizeof(DROPFILES)
    pDropFiles.fWide=True
    files=file_path.replace("/", "\\")
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
    '''
    该方法将给定的字符串复制到windows系统下的剪贴板\n
    Args:
        text:字符串\n
    '''
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(text,win32clipboard.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()

def convert_long_text_to_txt(Longtext:str):
    '''
    该方法将长字符串转换为txt文件,并将该文件复制到windows系统下的剪贴板\n
    Args:
        Longtext:长字符串\n
    '''
    f=open("长文本消息.txt",'w',encoding="utf-8")
    f.write(Longtext)
    f.close()
    path=os.path.join(os.getcwd(),"长文本消息.txt")
    SystemSettings.copy_file_to_windowsclipboard(path)


def copy_files(file_paths:list[str],target_folder:list[str]):
    '''
    将文件列表中的所有文件到复制到目标文件夹
    Args:
        file_paths:文件路径列表，例如 ['/path/to/file1.txt', '/path/to/file2.jpg']
        target_folder:目标文件夹路径，例如 '/path/to/destination/'
    '''
    os.makedirs(target_folder, exist_ok=True)
    for file_path in file_paths:
        #目标文件夹中没有该文件时再复制
        if not os.path.exists(os.path.join(target_folder,os.path.basename(file_path))):
            shutil.copy2(file_path, target_folder)

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

def set_english_input():
    '''
    该函数用来强制将输入法切换为windows系统内置英文输入法\n
    无论是pywinauto还是pyautogui只要使用type_keys或者typewrite类似的打字的方法时\n
    输入中文时,写出来有可能是一堆乱码(第三方输入法中文状态下)\n
    '''
    try:
        #获取当前活动窗口的线程ID
        hwnd=ctypes.windll.user32.GetForegroundWindow()
        thread_id=ctypes.windll.user32.GetWindowThreadProcessId(hwnd, 0)
        #加载美式键盘布局 
        klid=ctypes.windll.user32.LoadKeyboardLayoutW("00000409", 1)       
        #为当前线程设置键盘布局
        ctypes.windll.user32.ActivateKeyboardLayout(klid, 0)
        #发送WM_INPUTLANGCHANGEREQUEST消息
        ctypes.windll.user32.PostMessageW(hwnd, 0x0050, 0, klid)
    except Exception as e:
        print(f"设置英文输入法时出错: {e}")
