'''
WechatTools
=================
该模块中封装了一系列关于PC微信自动化的工具,主要用来辅助WechatAuto模块下的各个函数与方法的实现

类:
--
-   Tools:一些关于PC微信自动化过程中的工具,可以用于二次开发
-   API:打开指定公众号与微信小程序以及视频号,可为微信内部小程序公众号自动化操作提供便利

函数:
--
函数为上述模块内的所有方法
使用该模块的方法时,你可以:
--
#打开指定微信小程序
```
from pywechat.WechatTools import API
API.open_wechat_miniprogram(name='问卷星')
```
或者:
```
from pywechat import open_wechat_miniprogram
open_wechat_miniprogram(name='问卷星')
```
#从聊天界面内拉取200条消息
```
from pywechat import pull_messages
message_contents,message_senders,message_types=pull_messages(friend='文件传输助手',number=200)
```
或者:
```
from pywechat.WechatTools import Tools
message_contents,message_senders,message_types=Tools.pull_messages(friend='文件传输助手',number=200)
```
'''
############################依赖环境###########################
import os
import re
import time
import winreg
import win32api
import pyautogui
import win32gui
import win32con
import subprocess
import win32com.client
import psutil
import ctypes
from pywinauto import mouse,Desktop
from .WinSettings import Systemsettings
from pywinauto.controls.uia_controls import ListItemWrapper
from pywinauto.controls.uia_controls import ListViewWrapper
from pywinauto import WindowSpecification
from .Errors import NetWorkNotConnectError
from .Errors import WeChatNotStartError
from .Errors import NoSuchFriendError
from .Errors import ScanCodeToLogInError
from .Errors import NoResultsError,NotFriendError,NotInstalledError
from .Errors import ElementNotFoundError
from .Errors import WrongParameterError
from .Errors import NoPaymentLedgerError
from pywinauto.findwindows import ElementNotFoundError
from .Uielements import (Login_window,Main_window,SideBar,Lists,
Independent_window,Buttons,Texts,Menus,TabItems,MenuItems,Edits,Windows,Panes,SpecialMessages)
##########################################################################################
Login_window=Login_window()#登录主界面内的UI
Main_window=Main_window()#微信主界面内的UI
SideBar=SideBar()#微信主界面侧边栏的UI
Independent_window=Independent_window()#一些独立界面
Buttons=Buttons()#微信内部Button类型UI
Texts=Texts()#微信内部Text类型UI
Menus=Menus()#微信内部Menu类型UI
TabItems=TabItems()#微信内部TabItem类型UI
MenuItems=MenuItems()#w微信内部MenuItems类型UI
Edits=Edits()#微信内部Edit类型Ui
Windows=Windows()#微信内部Window类型UI
Panes=Panes()#微信内部Pane类型UI
Lists=Lists()#微信内部Text类型UI
SpecialMessages=SpecialMessages()#特殊消息
pyautogui.FAILSAFE=False#防止鼠标在屏幕边缘处造成的误触
#pywechat内的ffmpeg.exe路径
module_dir=os.path.dirname(os.path.abspath(__file__))
ffmpeg_path=os.path.join(module_dir, 'ffmpeg', 'ffmpeg.exe')
class Tools():
    '''该类中封装了一些关于PC微信的工具
    '''
    @staticmethod
    def is_wechat_installed():
        '''
        该方法通过查询注册表来判断本机是否安装微信
        '''
        #微信注册表的一般路径
        reg_path=r"Software\Tencent\WeChat"
        is_installed=True
        try:
            winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path)
        except Exception:
            is_installed=False
        return is_installed

    @staticmethod
    def is_wechat_running()->bool:
        '''
        该方法通过检测当前windows系统的进程中\n
        是否有WeChat.exe该项进程来判断微信是否在运行
        '''
        wmi=win32com.client.GetObject('winmgmts:')
        processes=wmi.InstancesOf('Win32_Process')
        for process in processes:
            if process.Name.lower()=='Wechat.exe'.lower():
                return True
        return False

    @staticmethod
    def language_detector()->str:
        '''
        该方法通过查询注册表来检测当前微信的语言版本
        '''
        #微信3.9版本一般的注册表路径
        reg_path=r"Software\Tencent\WeChat"
        if not Tools.is_wechat_installed():
            raise NotInstalledError
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
            value=winreg.QueryValueEx(key,"LANG_ID")[0]
            language_map={
                0x00000009: '英文',
                0x00000004: '简体中文',
                0x00000404: '繁体中文'
            }
            return language_map.get(value)

    @staticmethod
    def find_wechat_path(copy_to_clipboard:bool=True):
        '''该方法用来查找微信的路径,无论微信是否运行都可以查找到
        Args:
            copy_to_clipboard:是否将微信路径复制到剪贴板
        Returns:
            wechat_path:微信路径
        '''
        wechat_path=''
        if is_wechat_running():
            wmi=win32com.client.GetObject('winmgmts:')
            processes=wmi.InstancesOf('Win32_Process')
            for process in processes:
                if process.Name.lower() == 'WeChat.exe'.lower():
                    exe_path=process.ExecutablePath
                    if exe_path:
                        # 规范化路径并检查文件是否存在
                        exe_path=os.path.abspath(exe_path)
                        wechat_path=exe_path
            if copy_to_clipboard:
                Systemsettings.copy_text_to_windowsclipboard(wechat_path)
                print("已将微信程序路径复制到剪贴板")
            return wechat_path
        else:
            #windows环境变量中查找WeChat.exe路径
            try:
                reg_path=r"Software\Tencent\WeChat"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                    Installdir=winreg.QueryValueEx(key,"InstallPath")[0]
                wechat_path=os.path.join(Installdir,'WeChat.exe')
                if copy_to_clipboard:
                    Systemsettings.copy_text_to_windowsclipboard(wechat_path)
                    print("已将微信程序路径复制到剪贴板")
                return wechat_path
            except FileNotFoundError:
                raise NotInstalledError

    @staticmethod
    def is_VerticalScrollable(List:ListViewWrapper)->bool:
        '''
        该函数用来判断微信内的列表类型控件是否可以垂直滚动\n
        原理:微信内停靠在List右侧的灰色scrollbar无Ui\n
        该函数通过判断List组件是否具有iface_scorll这个属性即可判断其是否具有scrollbar进而判断其是否scrollable
        Args:
            List:微信内control_type为List的列表
        Returns:
            scrollable:是否可以竖直滚动
        '''
        try:
            #如果能获取到这个属性,说明可以滚动
            List.iface_scroll.CurrentVerticallyScrollable
            scrollable=True
        except Exception:#否则会引发NoPatternInterfaceError,此时返回False
            scrollable=False
        return scrollable


    @staticmethod
    def set_wechat_as_environ_path()->None:
        '''该方法用来自动打开系统环境变量设置界面,将微信路径自动添加至其中'''
        counter=0
        retry_interval=30
        Systemsettings.set_english_input()
        os.environ.update({"__COMPAT_LAYER":"RUnAsInvoker"})
        subprocess.Popen(["SystemPropertiesAdvanced.exe"])
        systemwindow=win32gui.FindWindow(None,u'系统属性')
        while not systemwindow:
            time.sleep(0.2)
            counter+=1
            systemwindow==win32gui.FindWindow(None,u'系统属性')
            if counter>=retry_interval:
                break
        if win32gui.IsWindow(systemwindow):#将系统变量窗口置于桌面最前端
            win32gui.ShowWindow(systemwindow,win32con.SW_SHOW)
            win32gui.SetWindowPos(systemwindow,win32con.HWND_TOPMOST,0,0,0,0,win32con.SWP_NOMOVE|win32con.SWP_NOSIZE)
        pyautogui.hotkey('alt','n',interval=0.5)#添加管理员权限后使用一系列快捷键来填写微信刻路径为环境变量
        pyautogui.hotkey('alt','n',interval=0.5)
        pyautogui.press('shift')
        pyautogui.typewrite('wechatpath')
        try:
            Tools.find_wechat_path()
            pyautogui.hotkey('Tab',interval=0.5)
            pyautogui.hotkey('ctrl','v')
            pyautogui.press('enter')
            pyautogui.press('enter')
            pyautogui.press('esc')
        except Exception:
            pyautogui.press('esc')
            pyautogui.hotkey('alt','f4')
            pyautogui.hotkey('alt','f4')
            raise NotInstalledError

    @staticmethod
    def judge_wechat_state()->int:
        '''该方法用来判断微信运行状态
        Returns:
            state:取值(-1,0,1,2)
        -1:微信未启动\n
        0:主界面不可见\n
        1:主界面最小化\n
        2:主界面可见(不一定置顶!)\n
        '''
        state=-1
        if Tools.is_wechat_running():
            window=win32gui.FindWindow(Main_window.MainWindow['class_name'],Main_window.MainWindow['title'])
            if win32gui.IsIconic(window):
                state=1
            elif win32gui.IsWindowVisible(window):
                state=2
            else:
                state=0
        return state

    @staticmethod
    def judge_independant_window_state(window:dict)->int:
        '''该方法用来判断微信内独立于微信主界面的窗口的状态
        Args:
            window:pywinauto定位控件时的kwargs字典,可以在Uielements模块中找到
        Returns:
            state:取值(-1,0,1)
        -1表示界面未打开,需要从微信内打开\n
        0表示界面最小化\n
        1表示界面可见(不一定置顶!)\n
        '''
        state=-1
        handle=win32gui.FindWindow(window.get('class_name'),None)
        if win32gui.IsIconic(handle):
            state=0
        if win32gui.IsWindowVisible(handle):
            state=1
        return state


    @staticmethod
    def move_window_to_center(Window:dict=Main_window.MainWindow,handle:int=0)->WindowSpecification:
        '''该方法用来将已打开的界面置顶并移动到屏幕中央并返回该窗口的Windowspecification实例\n
        可以直接传入窗口句柄或pywinauto定位控件时的kwargs参数字典
        Args:
            Window:pywinauto定位控件的kwargs参数字典
            handle:窗口句柄
        Returns:
            window:WindowSpecification对象
        '''
        counter=0
        retry_interval=40
        desktop=Desktop(**Independent_window.Desktop)
        class_name=Window['class_name'] if 'class_name' in Window else None
        title=Window['title'] if 'title' in Window else None
        if not class_name:
            raise WrongParameterError(f'参数错误!kwargs参数字典中必须包含class_name')
        if handle==0:
            handle=win32gui.FindWindow(class_name,title)
        while not handle:
            time.sleep(0.1)
            counter+=1
            handle=win32gui.FindWindow(class_name,title)
            if counter>=retry_interval:
                break
        screen_width,screen_height=win32api.GetSystemMetrics(win32con.SM_CXSCREEN),win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        window=desktop.window(handle=handle)
        window_width,window_height=window.rectangle().width(),window.rectangle().height()
        new_left=(screen_width-window_width)//2
        new_top=(screen_height-window_height)//2
        win32gui.SetWindowPos(
            handle,
            win32con.HWND_TOPMOST,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE |
            win32con.SWP_NOSIZE |
            win32con.SWP_SHOWWINDOW
        )
        if screen_width!=window_width:
            win32gui.MoveWindow(handle, new_left, new_top, window_width, window_height, True)
        return window

    @staticmethod
    def open_wechat(wechat_path:str=None,is_maximize:bool=True)->WindowSpecification:
        '''
        该方法用来打开微信
        Args:
            wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
            is_maximize:微信界面是否全屏,默认全屏。
        Returns:
            main_window:微信主界面
        微信的打开分为四种情况:\n
        1.未登录,此时调用该函数会自动查找并使用命令行启动wechat.exe路径,在弹出的登录界面中点击进入微信打开微信主界面\n
        启动并点击登录进入微信(注:需勾选自动登录按钮,否则启动后为扫码登录)\n
        2.未登录但已弹出微信的登录界面,此时会自动点击进入微信打开微信\n
        注意:未登录的情况下打开微信需要在手机端第一次扫码登录后勾选自动登入的选项,否则启动微信后\n
        聊天界面没有进入微信按钮,将会触发异常提示扫码登录\n
        3.已登录，主界面最小化在状态栏，此时调用该函数会直接打开后台中的微信。\n
        4.已登录，主界面关闭，此时调用该函数会打开已经关闭的微信界面。\n
        '''
        max_retry_times=40
        retry_interval=0.5
        wechat_path=wechat_path
        #处理登录界面的闭包函数，点击进入微信，若微信登录界面存在直接传入窗口句柄，否则自己查找
        def handle_login_window(wechat_path=wechat_path,is_maximize=is_maximize,max_retry_times=max_retry_times,retry_interval=retry_interval):
            counter=0
            if wechat_path:#看看有没有传入wechat_path
                subprocess.Popen(wechat_path)
            if not wechat_path:#没有传入就自己找
                wechat_path=Tools.find_wechat_path(copy_to_clipboard=False)
                subprocess.Popen(wechat_path)
            #没有传入登录界面句柄，需要自己查找(此时对应的情况是微信未启动)
            login_window_handle= win32gui.FindWindow(Login_window.LoginWindow['class_name'],None)
            while not login_window_handle:
                login_window_handle= win32gui.FindWindow(Login_window.LoginWindow['class_name'],None)
                if login_window_handle:
                    break
                counter+=1
                time.sleep(0.2)
                if counter>=max_retry_times:
                    raise NoResultsError(f'微信打开失败,请检查网络连接或者微信是否正常启动！')
            #移动登录界面到屏幕中央
            login_window=Tools.move_window_to_center(Login_window.LoginWindow,login_window_handle)
            #点击登录按钮,等待主界面出现并返回
            try:
                login_button=login_window.child_window(**Login_window.LoginButton)
                login_button.set_focus()
                login_button.click_input()
                main_window_handle=0
                while not main_window_handle:
                    main_window_handle=win32gui.FindWindow(Main_window.MainWindow['class_name'],None)
                    if main_window_handle:
                        break
                    counter+=1
                    time.sleep(retry_interval)
                    if counter >= max_retry_times:
                        raise NetWorkNotConnectError
                main_window=Tools.move_window_to_center(handle=main_window_handle)
                if is_maximize:
                    main_window.maximize()
                NetWorkErrotText=main_window.child_window(**Texts.NetWorkError)
                if NetWorkErrotText.exists():
                    main_window.close()
                    raise NetWorkNotConnectError(f'未连接网络,请连接网络后再进行后续自动化操作！')
                return main_window
            except ElementNotFoundError:
                raise ScanCodeToLogInError
         #最多尝试40次，每次间隔0.5秒，20秒内无法打开微信则抛出异常

        #open_wechat函数的主要逻辑：
        if Tools.is_wechat_running():#微信如果已经打开无需登录可以直接连接
            #同时查找主界面与登录界面句柄，二者有一个存在都证明微信已经启动
            main_window_handle=win32gui.FindWindow(Main_window.MainWindow['class_name'],None)
            login_window_handle=win32gui.FindWindow(Login_window.LoginWindow['class_name'],None)
            if main_window_handle:
                #威信运行时有最小化，主界面可见未关闭,主界面不可见关闭三种情况
                if win32gui.IsWindowVisible(main_window_handle):#主界面可见包含最小化
                    if win32gui.IsIconic(main_window_handle):#主界面最小化
                        win32gui.ShowWindow(main_window_handle,win32con.SW_SHOWNORMAL)
                        main_window=Tools.move_window_to_center(handle=main_window_handle)
                        if is_maximize:
                            main_window.maximize()
                        NetWorkErrotText=main_window.child_window(**Texts.NetWorkError)
                        if NetWorkErrotText.exists():
                            main_window.close()
                            raise NetWorkNotConnectError(f'未连接网络,请连接网络后再进行后续自动化操作！')
                        return main_window
                    else:#主界面存在且未最小化
                        main_window=Tools.move_window_to_center(handle=main_window_handle)
                        if is_maximize:
                            main_window.maximize()
                        NetWorkErrotText=main_window.child_window(**Texts.NetWorkError)
                        if NetWorkErrotText.exists():
                            main_window.close()
                            raise NetWorkNotConnectError(f'未连接网络,请连接网络后再进行后续自动化操作！')
                        return main_window
                else:#主界面不可见
                    #打开过主界面，关闭掉了，需要重新打开
                    win32gui.ShowWindow(main_window_handle,win32con.SW_SHOWNORMAL)
                    main_window=Tools.move_window_to_center(handle=main_window_handle)
                    if is_maximize:
                        main_window.maximize()
                    NetWorkErrotText=main_window.child_window(**Texts.NetWorkError)
                    if NetWorkErrotText.exists():
                        main_window.close()
                        raise NetWorkNotConnectError(f'未连接网络,请连接网络后再进行后续自动化操作！')
                    return main_window
            if login_window_handle:#微信启动了，但是.是登录界面在桌面上，不是主界面
                #处理登录界面
                return handle_login_window()
        else:#微信未启动
            #处理登录界面
            return handle_login_window()

    @staticmethod
    def open_settings(wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True)->tuple[WindowSpecification,WindowSpecification|None]:
        '''
        该方法用来打开微信设置界面。
        Args:
            wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
            is_maximize:微信界面是否全屏,默认全屏。
            close_wechat:任务结束后是否关闭微信,默认关闭
        Returns:
            (settings_window,main_window):settings_window:设置界面窗口
            main_window:微信主界面,当close_wechat设置为True时,main_window为None
        '''
        main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=is_maximize)
        if judge_independant_window_state(window=Independent_window.SettingWindow)!=-1:
            handle=win32gui.FindWindow(Independent_window.SettingWindow['class_name'],Independent_window.SettingWindow['title'])
            win32gui.ShowWindow(handle,win32con.SW_SHOWNORMAL)
        else:
            setting=main_window.child_window(**SideBar.SettingsAndOthers)
            setting.click_input()
            settings_menu=main_window.child_window(**Main_window.SettingsMenu)
            settings_button=settings_menu.child_window(**Buttons.SettingsButton)
            settings_button.click_input()
        if close_wechat:
            main_window.close()
            main_window=None
        settings_window=Tools.move_window_to_center(Independent_window.SettingWindow)
        return settings_window,main_window

    @staticmethod
    def open_dialog_window(friend:str,wechat_path:str=None,is_maximize:bool=True,search_pages:int=5)->tuple[WindowSpecification,WindowSpecification]:
        '''
        该方法用于打开某个好友(非公众号)的聊天窗口
        Args:
            friend:好友或群聊备注名称,需提供完整名称
            wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
                    尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
                    传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
            is_maximize:微信界面是否全屏,默认全屏。
            search_pages:在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
        Returns:
            (edit_area,main_window):editarea:主界面右下方与好友的消息编辑区域,main_window:微信主界面
        '''
        def get_searh_result(friend,search_result):#查看搜索列表里有没有名为friend的listitem
            listitem=search_result.children(control_type="ListItem")
            #descendants带有按钮能够排除掉非好友的其他搜索结果
            contacts=[item for item in listitem if item.descendants(control_type='Button')]
            names=[re.sub(r'[\u2002\u2004\u2005\u2006\u2009]',' ',item.window_text()) for item in contacts]
            if friend in names:#如果在的话就返回整个搜索到的所有联系人,以及其所处的index
                location=names.index(friend)
                return contacts[location]
            return None
        #如果search_pages不为0,即需要在会话列表中滚动查找时，使用find_friend_in_Messagelist方法找到好友,并点击打开对话框
        if search_pages:
            edit_area,main_window=Tools.find_friend_in_MessageList(friend=friend,wechat_path=wechat_path,is_maximize=is_maximize,search_pages=search_pages)
            chat_button=main_window.child_window(**SideBar.Chats)
            if edit_area:#edit_area不为None,即说明find_friend_in_MessageList找到了聊天窗口,直接返回结果
                return edit_area,main_window
            #edit_area为None没有在会话列表中找到好友,直接在顶部搜索栏中搜索好友
            #先点击侧边栏的聊天按钮切回到聊天主界面
            #顶部搜索按钮搜索好友
            search=main_window.child_window(**Main_window.Search).wait(wait_for='visible',retry_interval=0.1,timeout=3)
            search.click_input()
            Systemsettings.copy_text_to_windowsclipboard(friend)
            pyautogui.hotkey('ctrl','v')
            search_results=main_window.child_window(**Main_window.SearchResult)
            time.sleep(1)
            friend_button=get_searh_result(friend=friend,search_result=search_results)
            if friend_button:
                friend_button.click_input()
                edit_area=main_window.child_window(title=friend,control_type='Edit')
                return edit_area,main_window #同时返回搜索到的该好友的聊天窗口与主界面！若只需要其中一个需要使用元祖索引获取。
            else:#搜索结果栏中没有关于传入参数friend好友昵称或备注的搜索结果，关闭主界面,引发NosuchFriend异常
                chat_button.click_input()
                main_window.close()
                raise NoSuchFriendError
        else: #searchpages为0，不在会话列表查找
            #这部分代码先判断微信主界面是否可见,如果可见不需要重新打开,这在多个close_wechat为False需要进行来连续操作的方式使用时要用到
            main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=is_maximize)
            chat_button=main_window.child_window(**SideBar.Chats)
            message_list_pane=main_window.child_window(**Main_window.ConversationList)
            #先看看当前聊天界面是不是好友的聊天界面
            current_chat=main_window.child_window(**Main_window.CurrentChatWindow)
            #如果当前主界面是某个好友的聊天界面且聊天界面顶部的名称为好友名称，直接返回结果
            if current_chat.exists() and friend==current_chat.window_text():
                edit_area=current_chat
                edit_area.click_input()
                return edit_area,main_window
            else:#否则直接从顶部搜索栏出搜索结果
                #如果会话列表不存在或者不可见的话才点击一下聊天按钮
                if not message_list_pane.exists():
                    chat_button.click_input()
                if not message_list_pane.is_visible():
                    chat_button.click_input()
                search=main_window.child_window(**Main_window.Search)
                search.click_input()
                Systemsettings.copy_text_to_windowsclipboard(friend)
                pyautogui.hotkey('ctrl','v')
                search_results=main_window.child_window(**Main_window.SearchResult)
                time.sleep(1)
                friend_button=get_searh_result(friend=friend,search_result=search_results)
                if friend_button:
                    friend_button.click_input()
                    edit_area=main_window.child_window(title=friend,control_type='Edit')
                    return edit_area,main_window #同时返回搜索到的该好友的聊天窗口与主界面！若只需要其中一个需要使用元祖索引获取。
                else:#搜索结果栏中没有关于传入参数friend好友昵称或备注的搜索结果，关闭主界面,引发NosuchFriend异常
                    chat_button.click_input()
                    main_window.close()
                    raise NoSuchFriendError
    @staticmethod
    def open_dialog_windows(friends:list[str],wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True):
        '''
        该方法用于打开多个好友(非公众号)的独立聊天窗口
        Args:
            friend:好友或群聊备注名称,需提供完整名称
            wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
                  尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
                  传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
            is_maximize:微信界面是否全屏,默认全屏。
        Returns:
            chat_windows:所有已打开并在桌面单独显示的独立聊天窗口的列表
        '''
        def get_searh_result(friend,search_result):#查看搜索列表里有没有名为friend的listitem
            listitem=search_result.children(control_type="ListItem")
            #descendants带有按钮能够排出掉非好友的其他搜索结果
            contacts=[item for item in listitem if item.descendants(control_type='Button')]
            names=[re.sub(r'[\u2002\u2004\u2005\u2006\u2009]',' ',item.window_text()) for item in contacts]
            if friend in names:#如果在的话就返回整个搜索到的所有联系人,以及其所处的index
                location=names.index(friend)
                return contacts[location]
            return None
        desktop=Desktop(**Independent_window.Desktop)
        main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=is_maximize)
        chats_button=main_window.child_window(**SideBar.Chats)
        message_list=main_window.child_window(**Main_window.ConversationList)
        search=main_window.child_window(**Main_window.Search)
        if not message_list.exists():
            chats_button.click_input()
        if not message_list.is_visible():
            chats_button.click_input()
        chat_windows=[]
        for friend in friends:
            search.click_input()
            Systemsettings.copy_text_to_windowsclipboard(friend)
            pyautogui.hotkey('ctrl','v')
            search_results=main_window.child_window(**Main_window.SearchResult)
            time.sleep(1)
            friend_button=get_searh_result(friend=friend,search_result=search_results)
            if friend_button:
                friend_button.click_input()
                time.sleep(0.5)
                selected_item=[item for item in message_list.children(control_type='ListItem') if item.is_selected()][0]
                selected_item.double_click_input()
                chat_window={'title':friend,'class_name':'ChatWnd','framework_id':'Win32'}
                chat_window=desktop.window(**chat_window)
                chat_windows.append(chat_window)
                chat_window.minimize()
            else:#搜索结果栏中没有关于传入参数friend好友昵称或备注的搜索结果，关闭主界面,引发NosuchFriend异常
                chats_button.click_input()
                main_window.close()
                raise NoSuchFriendError
        if close_wechat:
            main_window.close()
        return chat_windows

    @staticmethod
    def find_friend_in_MessageList(friend:str,wechat_path:str=None,is_maximize:bool=True,search_pages:int=5)->tuple[WindowSpecification|None,WindowSpecification]:
        '''
        该方法用于在会话列表中寻找好友(非公众号)。
        Args:
            friend:好友或群聊备注名称,需提供完整名称
            wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
            is_maximize:微信界面是否全屏,默认全屏。
            search_pages:在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
        Returns:
            (edit_area,main_windwo):若edit_area存在:返回值为 (edit_area,main_window) 同时返回好友聊天界面内的编辑区域与主界面
            否则:返回值为(None,main_window)
        '''
        def selecte_in_messageList(friend):
            '''
            用来返回会话列表中名称为friend的ListItem项内的Button与是否为最后一项
            '''
            is_last=False
            message_list=message_list_pane.children(control_type='ListItem')
            buttons=[friend.children()[0].children()[0] for friend in message_list]
            friend_button=None
            for i in range(len(buttons)):
                if friend==buttons[i].texts()[0]:
                    friend_button=buttons[i]
                    break
            if i==len(buttons)-1:
                is_last=True
            return friend_button,is_last

        main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=is_maximize)
        #先看看当前微信右侧界面是不是聊天界面可能存在不是聊天界面的情况比如是纯白色的微信的icon
        current_chat=main_window.child_window(**Main_window.CurrentChatWindow)
        chats_button=main_window.child_window(**SideBar.Chats)
        message_list_pane=main_window.child_window(**Main_window.ConversationList)
        if not message_list_pane.exists():
            chats_button.click_input()
        if not message_list_pane.is_visible():
            chats_button.click_input()
        rectangle=message_list_pane.rectangle()
        scrollable=Tools.is_VerticalScrollable(message_list_pane)
        activateScollbarPosition=(rectangle.right-5, rectangle.top+20)
        if current_chat.exists() and current_chat.window_text()==friend:
        #如果当前主界面是某个好友的聊天界面且聊天界面顶部的名称为好友名称，直接返回结果,current_chat可能是刚登录打开微信的纯白色icon界面
            edit_area=current_chat
            edit_area.click_input()
            return edit_area,main_window
        else:
            message_list=message_list_pane.children(control_type='ListItem')
            if len(message_list)==0:
                return None,main_window
            if not scrollable:
                friend_button,index=selecte_in_messageList(friend)
                if friend_button:
                    if index:
                        rec=friend_button.rectangle()
                        mouse.click(coords=(int(rec.left+rec.right)//2,rec.top-12))
                        edit_area=main_window.child_window(title=friend,control_type='Edit')
                    else:
                        friend_button.click_input()
                        edit_area=main_window.child_window(title=friend,control_type='Edit')
                    return edit_area,main_window
                else:
                    return None,main_window
            if scrollable:
                rectangle=message_list_pane.rectangle()
                message_list_pane.iface_scroll.SetScrollPercent(verticalPercent=0.0,horizontalPercent=1.0)#调用SetScrollPercent方法向上滚动,verticalPercent=0.0表示直接将scrollbar一下子置于顶部
                mouse.click(coords=activateScollbarPosition)
                for _ in range(search_pages):
                    friend_button,index=selecte_in_messageList(friend)
                    if friend_button:
                        if index:
                            rec=friend_button.rectangle()
                            mouse.click(coords=(int(rec.left+rec.right)//2,rec.top-12))
                            edit_area=main_window.child_window(title=friend,control_type='Edit')
                        else:
                            friend_button.click_input()
                            edit_area=main_window.child_window(title=friend,control_type='Edit')
                        break
                    else:
                        pyautogui.press("pagedown",_pause=False)
                        time.sleep(0.5)
                mouse.click(coords=activateScollbarPosition)
                pyautogui.press('Home')
                edit_area=main_window.child_window(title=friend,control_type='Edit')
                if edit_area.exists():
                    return edit_area,main_window
                else:
                    return None,main_window

    @staticmethod
    def open_friend_settings(friend:str,wechat_path:str=None,is_maximize:bool=True,search_pages:int=5)->tuple[WindowSpecification,WindowSpecification]:
        '''
        该方法用于打开好友右侧的设置界面
        Args:
            friend:好友备注名称,需提供完整名称
            wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
            is_maximize:微信界面是否全屏,默认全屏。
            search_pages:在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
        Returns:
            (friend_settings_window,main_window):friend_settings_window:好友右侧的设置界面
            main_window:微信主界面
        '''
        main_window=Tools.open_dialog_window(friend=friend,wechat_path=wechat_path,is_maximize=is_maximize,search_pages=search_pages)[1]
        try:
            ChatMessage=main_window.child_window(**Buttons.ChatMessageButton)
            ChatMessage.click_input()
            friend_settings_window=main_window.child_window(**Main_window.FriendSettingsWindow)
        except ElementNotFoundError:
            main_window.close()
            raise NotFriendError(f'非正常好友,无法打开设置界面！')
        return friend_settings_window,main_window

    @staticmethod
    def open_contacts_manage(wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True)->tuple[WindowSpecification,WindowSpecification]:
        '''
        该方法用于打开通讯录管理界面
        Args:
            wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
            is_maximize:微信界面是否全屏,默认全屏。
            close_wechat:任务结束后是否关闭微信,默认关闭
        Returns:
            (contacts_manage_window,main_window):contacts_manage_window:通讯录管理界面
            main_window:微信主界面,当close_wechat设置为True时返回None
        '''
        main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=is_maximize)
        contacts=main_window.child_window(**SideBar.Contacts)
        contacts.click_input()
        cancel_button=main_window.child_window(**Buttons.CancelButton)
        if cancel_button.exists():
            cancel_button.click_input()
        ContactsLists=main_window.child_window(**Main_window.ContactsList)
        #############################
        rec=ContactsLists.rectangle()
        mouse.click(coords=(rec.right-5,rec.top))
        pyautogui.press('Home')
        pyautogui.press('pageup')
        contacts_manage=main_window.child_window(**Buttons.ContactsManageButton)#通讯录管理窗口按钮
        #############################
        contacts_manage.click_input()
        contacts_manage_window=Tools.move_window_to_center(Window=Independent_window.ContactManagerWindow)
        if close_wechat:
            main_window.close()
            main_window=None
        return contacts_manage_window,main_window

    @staticmethod
    def open_friend_settings_menu(friend:str,wechat_path:str=None,is_maximize:bool=True,search_pages:int=5)->tuple[WindowSpecification,WindowSpecification,WindowSpecification]:
        '''
        该方法用于打开好友设置菜单
        Args:
            friend:好友备注名称,需提供完整名称
            wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
            is_maximize:微信界面是否全屏,默认全屏。
            search_pages:在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
        Returns:
            (friend_menu,friend_settings_window,main_window):friend_menu:在friend_settings_window界面里点击好友头像弹出的菜单
            friend_settings_window:好友右侧的设置界面
            main_window:微信主界面
        '''
        friend_settings_window,main_window=Tools.open_friend_settings(friend=friend,wechat_path=wechat_path,is_maximize=is_maximize,search_pages=search_pages)
        friend_button=friend_settings_window.child_window(title=friend,control_type="Button",found_index=0)
        friend_button.click_input()
        profile_window=friend_settings_window.child_window(**Panes.FriendProfilePane)
        more_button=profile_window.child_window(**Buttons.MoreButton)
        more_button.click_input()
        friend_menu=profile_window.child_window(**Menus.FriendProfileMenu)
        return friend_menu,friend_settings_window,main_window

    @staticmethod
    def open_collections(wechat_path:str=None,is_maximize:bool=True)->WindowSpecification:
        '''
        该方法用于打开收藏界面
        Args:
            wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
            is_maximize:微信界面是否全屏,默认全屏。
        Returns:
            main_window:微信主界面
        '''
        main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=is_maximize)
        collections_button=main_window.child_window(**SideBar.Collections)
        collections_button.click_input()
        return main_window

    @staticmethod
    def open_group_settings(group_name:str,wechat_path:str=None,is_maximize:bool=True,search_pages:int=5)->tuple[WindowSpecification,WindowSpecification]:
        '''
        该方法用来打开群聊设置界面
        Args:
            group_name:群聊备注名称,需提供完整名称
            wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
            is_maximize:微信界面是否全屏,默认全屏。
            search_pages:在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
        Returns:
            (group_settings_window,main_window):group_sttings_window:群聊设置界面
            main_window:微信主界面
        '''
        main_window=Tools.open_dialog_window(friend=group_name,wechat_path=wechat_path,is_maximize=is_maximize,search_pages=search_pages)[1]
        ChatMessage=main_window.child_window(**Buttons.ChatMessageButton)
        ChatMessage.click_input()
        group_settings_window=main_window.child_window(**Main_window.GroupSettingsWindow)
        group_settings_window.child_window(**Texts.GroupNameText).click_input()
        return group_settings_window,main_window

    @staticmethod
    def open_moments(wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True)->tuple[WindowSpecification,WindowSpecification|None]:
        '''
        该方法用于打开微信朋友圈
        Args:
            wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
            is_maximize:微信界面是否全屏,默认全屏。
            close_wechat:任务结束后是否关闭微信,默认关闭
        Returns:
            (moments_window,main_window):moments_window:朋友圈主界面
            main_window:微信主界面,当close_wechat设置为True时,main_window为None
        '''
        main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=is_maximize)
        moments_button=main_window.child_window(**SideBar.Moments)
        moments_button.click_input()
        moments_window=Tools.move_window_to_center(Independent_window.MomentsWindow)
        moments_window.child_window(**Buttons.RefreshButton).click_input()
        if close_wechat:
            main_window.close()
            main_window=None
        return moments_window,main_window

    @staticmethod
    def open_chatfiles(wechat_path:str=None,wechat_maximize:bool=True,is_maximize:bool=True,close_wechat:bool=True)->tuple[WindowSpecification,WindowSpecification|None]:
        '''
        该方法用于打开聊天文件界面
        Args:
            wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
            wechat_maximize:微信界面是否全屏,默认全屏
            is_maximize:聊天文件界面是否全屏,默认全屏。
            close_wechat:任务结束后是否关闭微信,默认关闭
        Returns:
            (filelist_window,main_window):filelist_window:聊天文件界面
            main_window:微信主界面,当close_wechat设置为True时main_window为None
        '''
        main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=wechat_maximize)
        moments_button=main_window.child_window(**SideBar.ChatFiles)
        moments_button.click_input()
        desktop=Desktop(**Independent_window.Desktop)
        filelist_window=desktop.window(**Independent_window.ChatFilesWindow)
        if is_maximize:
            filelist_window.maximize()
        if close_wechat:
            main_window.close()
            main_window=None
        return filelist_window,main_window

    @staticmethod
    def open_friend_profile(friend:str,wechat_path:str=None,is_maximize:bool=True,search_pages:int=5)->tuple[WindowSpecification,WindowSpecification]:
        '''
        该方法用于打开好友个人简介界面
        Args:
            friend:好友备注名称,需提供完整名称
            wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
            is_maximize:信界面是否全屏,默认全屏。
            search_pages:在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
        Returns:
            (profile_window,main_window):profile_window:好友设置界面内点击好友头像后的好友个人简介界面
            main_window:微信主界面
        '''
        friend_settings_window,main_window=Tools.open_friend_settings(friend=friend,wechat_path=wechat_path,is_maximize=is_maximize,search_pages=search_pages)
        friend_button=friend_settings_window.child_window(title=friend,control_type="Button",found_index=0)
        friend_button.click_input()
        profile_window=friend_settings_window.child_window(**Panes.FriendProfilePane)
        return profile_window,main_window

    @staticmethod
    def open_contacts(wechat_path:str=None,is_maximize:bool=True)->WindowSpecification:
        '''
        该方法用于打开微信通信录界面
        Args:
            friend:好友或群聊备注名称,需提供完整名称
            wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
            is_maximize:微信界面是否全屏,默认全屏。
        Returns:
            main_window:微信主界面
        '''
        main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=is_maximize)
        contacts=main_window.child_window(**SideBar.Contacts)
        contacts.set_focus()
        contacts.click_input()
        cancel_button=main_window.child_window(**Buttons.CancelButton)
        if cancel_button.exists():
            cancel_button.click_input()
        ContactsLists=main_window.child_window(**Main_window.ContactsList)
        rec=ContactsLists.rectangle()
        mouse.click(coords=(rec.right-5,rec.top))
        pyautogui.press('Home')
        pyautogui.press('pageup')
        return main_window

    @staticmethod
    def open_chat_history(friend:str,TabItem:str=None,search_pages:int=5,wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True)->tuple[WindowSpecification,WindowSpecification|None]:
        '''
        该方法用于打开好友聊天记录界面
        Args:
            friend:好友备注名称,需提供完整名称
            TabItem:点击聊天记录顶部的Tab选项,默认为None,可选值为:文件,图片与视频,链接,音乐与音频,小程序,视频号,日期
            search_pages:在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
            wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
            is_maximize:微信界面是否全屏,默认全屏。
            close_wechat:任务结束后是否关闭微信,默认关闭
        Returns:
            (chat_history_window,main_window):chat_history_window:好友设置界面内点击好友头像后的好友个人简介界面
            main_window:微信主界面,当close_wechat设置为True时,main_window为None
        '''
        tabItems={'文件':TabItems.FileTabItem,'图片与视频':TabItems.PhotoAndVideoTabItem,'链接':TabItems.LinkTabItem,'音乐与音频':TabItems.MusicTabItem,'小程序':TabItems.MiniProgramTabItem,'视频号':TabItems.ChannelTabItem,'日期':TabItems.DateTabItem}
        if TabItem:
            if TabItem not in tabItems.keys():
                raise WrongParameterError('TabItem参数错误!')
        main_window=Tools.open_dialog_window(friend=friend,wechat_path=wechat_path,is_maximize=is_maximize,search_pages=search_pages)[1]
        chat_toolbar=main_window.child_window(**Main_window.ChatToolBar)
        chat_history_button=chat_toolbar.child_window(**Buttons.ChatHistoryButton)
        if not chat_history_button.exists():
            #公众号没有聊天记录这个按钮
            main_window.close()
            raise NotFriendError(f'非正常好友!无法打开聊天记录界面')
        chat_history_button.click_input()
        chat_history_window=Tools.move_window_to_center(Independent_window.ChatHistoryWindow)
        if close_wechat:
            main_window.close()
            main_window=None
        if TabItem:
            # if TabItem=='视频号' or TabItem=='日期':
            #     chat_history_window.child_window(control_type='Button',title='').click_input()
            chat_history_window.child_window(**tabItems[TabItem]).click_input()
        return chat_history_window,main_window

    @staticmethod
    def open_program_pane(wechat_path:str=None,is_maximize:bool=True,wechat_maximize:bool=True,close_wechat:bool=True)->tuple[WindowSpecification,WindowSpecification|None]:
        '''
        该方法用来打开小程序面板
        Args:
            wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
            is_maximize:小程序面板界面是否全屏,默认全屏。
            wechat_maximize:微信主界面是否全屏,默认全屏
            close_wechat:任务结束后是否关闭微信,默认关闭
        Returns:
            (program_window,main_window):program_window:小程序面板
            main_window:微信主界面,当close_wechat设置为True时,main_window为None
        '''
        main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=wechat_maximize)
        program_button=main_window.child_window(**SideBar.Miniprogram_pane)
        program_button.click_input()
        if close_wechat:
            main_window.close()
            main_window=None
        program_window=Tools.move_window_to_center(Independent_window.MiniProgramWindow)
        if is_maximize:
            program_window.maximize()
        return program_window,main_window

    @staticmethod
    def open_top_stories(wechat_path:str=None,is_maximize:bool=True,wechat_maximize:bool=True,close_wechat:bool=True)->tuple[WindowSpecification,WindowSpecification|None]:
        '''
        该方法用于打开看一看
        Args:
            wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
            is_maximize:看一看界面是否全屏,默认全屏。
            wechat_maximize:微信主界面是否全屏,默认全屏
            close_wechat:任务结束后是否关闭微信,默认关闭
        Returns:
            (top_stories_window,main_window):topstories_window:看一看主界面
            main_window:微信主界面,当close_wechat设置为True时,main_window为None
        '''
        main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=wechat_maximize)
        top_stories_button=main_window.child_window(**SideBar.Topstories)
        top_stories_button.click_input()
        top_stories_window=Tools.move_window_to_center(Independent_window.TopStoriesWindow)
        reload_button=top_stories_window.child_window(**Buttons.ReloadButton)
        reload_button.click_input()
        if is_maximize:
            top_stories_window.maximize()
        if close_wechat:
            main_window.close()
            main_window=None
        return top_stories_window,main_window

    @staticmethod
    def open_search(wechat_path:str=None,is_maximize:bool=True,wechat_maximize:bool=True,close_wechat:bool=True)->tuple[WindowSpecification,WindowSpecification|None]:
        '''
        该方法用于打开搜一搜
        Args:
            wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
            is_maximize:搜一搜界面是否全屏,默认全屏。
            wechat_maximize:微信主界面是否全屏,默认全屏
            close_wechat:任务结束后是否关闭微信,默认关闭
        Returns:
            (search_window,main_window):search_window:搜一搜界面
            main_window:微信主界面,当close_wechat设置为True时,main_window为None
        '''
        main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=wechat_maximize)
        search_button=main_window.child_window(**SideBar.Search)
        search_button.click_input()
        search_window=Tools.move_window_to_center(Independent_window.SearchWindow)
        if is_maximize:
            search_window.maximize()
        if close_wechat:
            main_window.close()
            main_window=None
        return search_window,main_window

    @staticmethod
    def open_channels(wechat_path:str=None,is_maximize:bool=True,wechat_maximize:bool=True,close_wechat:bool=True)->tuple[WindowSpecification,WindowSpecification|None]:
        '''
        该方法用于打开视频号
        Args:
            wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
            is_maximize:视频号界面是否全屏,默认全屏。
            wechat_maximize:微信主界面是否全屏,默认全屏
            close_wechat:任务结束后是否关闭微信,默认关闭
        Returns:
            (channel_window,main_window):channel_window:视频号窗口
            main_window:微信主界面,当close_wechat设置为True时返回None
        '''
        main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=wechat_maximize)
        channel_button=main_window.child_window(**SideBar.Channel)
        channel_button.click_input()
        channel_window=Tools.move_window_to_center(Independent_window.ChannelWindow)
        if is_maximize:
            channel_window.maximize()
        if close_wechat:
            main_window.close()
            main_window=None
        return channel_window,main_window

    @staticmethod
    def open_payment_ledger(wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True)->tuple[WindowSpecification,WindowSpecification]:
        '''
        该方法用于打开微信收款助手的小账本界面
        Args:
            wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
            is_maximize:视频号界面是否全屏,默认全屏。
            wechat_maximize:微信主界面是否全屏,默认全屏
            close_wechat:任务结束后是否关闭微信,默认关闭
        Returns:
            (ledger_window,main_window):微信收款助手的小账本界面
            main_window:微信主界面,当close_wechat设置为True时返回None
        '''
        try:
            main_window=Tools.open_dialog_window(friend='微信收款助手',wechat_path=wechat_path,is_maximize=is_maximize,search_pages=0)[1]
            main_window.child_window(**Buttons.LedgerButton).click_input()
            menu=main_window.child_window(**Menus.RightClickMenu)
            menu.child_window(**MenuItems.EnterLedgerMenuItem).click_input()
            ledger_window=Tools.move_window_to_center(Window=Independent_window.ReceiptLedgerWindow)
            if close_wechat:
                main_window.close()
                main_window=None
            return ledger_window,main_window
        except NoSuchFriendError:
            raise NoPaymentLedgerError

    @staticmethod
    def open_payment_code_window(wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True,close_ledger:bool=True)->tuple[WindowSpecification,WindowSpecification]:
        '''
        该方法用于打开微信收款助手小账本界面内的个人收款码
        Args:
            wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
            is_maximize:视频号界面是否全屏,默认全屏。
            wechat_maximize:微信主界面是否全屏,默认全屏
            close_wechat:任务结束后是否关闭微信,默认关闭
            close_ledger:任务结束后是否关闭微信收款助手小账本，默认关闭
        Returns:
            (payment_code_window,main_window):微信收款助手的小账本界面
            main_window:微信主界面,当close_wechat设置为True时返回None
        '''
        ledger_window,main_window=Tools.open_payment_ledger(wechat_path=wechat_path,is_maximize=is_maximize,close_wechat=close_wechat)
        paymentcode=ledger_window.child_window(**Buttons.PaymentCodeButton).wait(wait_for='visible')
        paymentcode.double_click_input()
        payment_code_window=Tools.move_window_to_center(Window=Independent_window.PaymentCodeWindow)
        if close_ledger:
            ledger_window.close()
        return payment_code_window,main_window

    @staticmethod
    def pull_messages(number:int,friend:str=None,chatWnd:WindowSpecification=None,parse:bool=True,chats_only:bool=True,search_pages:int=5,wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True)->list[dict]|list[ListItemWrapper]:
        '''
        该方法用来从主界面右侧的聊天区域或单独的聊天窗口内获取指定条数的聊天记录消息\n
        消息具体类型:{'文本','图片','视频','语音','文件','动画表情','视频号','链接','卡片链接','微信转账','系统消息'}
        Args:
            number:聊天记录条数
            friend:好友或群聊备注
            chatWnd:独立的好友聊天窗口
            parse:是否解析聊天记录为文本(主界面右侧聊天区域内的聊天记录形式为ListItem),设置为False时返回的类型为ListItem
            chats_only:是否只查找聊天消息不包含系统消息,设置为False时连同灰色的系统消息一起查找
            search_pages:在会话列表中查询查找好友时滚动列表的次数,默认为10,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏法搜索好友信息打开聊天界面
            wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
            is_maximize:微信主界面是否全屏,默认全屏。
            close_wechat:任务结束后是否关闭微信,默认关闭
        Returns:
            chats:[{'发送人':'','消息内容':'','消息类型':''}]*number\n
            list[ListItemWrapper]:聊天消息的ListItem形式

        '''
        chats=[]
        friendtype='好友'#默认是好友
        if chatWnd is not None:
            main_window=chatWnd
        if friend is None and chatWnd is None:
            raise ValueError('friend与ChatWnd至少要有一个!')
        if chatWnd is None and friend is not None:
            main_window=Tools.open_dialog_window(friend=friend,search_pages=search_pages,wechat_path=wechat_path,is_maximize=is_maximize)[1]
            chat_history_button=main_window.child_window(**Buttons.ChatHistoryButton)
            if not chat_history_button.exists():#没有聊天记录按钮是公众号或其他类型的东西
                raise NotFriendError(f'{friend}不是好友，无法获取聊天记录！')
        chatList=main_window.child_window(**Main_window.FriendChatList)#聊天区域内的消息列表
        scrollable=Tools.is_VerticalScrollable(chatList)
        viewMoreMesssageButton=main_window.child_window(**Buttons.CheckMoreMessagesButton)#查看更多消息按钮
        if len(chatList.children(control_type='ListItem'))==0:#没有聊天记录直接返回空列表
            return []
        video_call_button=main_window.child_window(**Buttons.VideoCallButton)
        if not video_call_button.exists():##没有视频聊天按钮是群聊
            friendtype='群聊'
        #if message.descendants(conrol_type)是用来筛选这个消息(control_type为ListItem)内有没有按钮(消息是人发的必然会有头像按钮这个UI,系统消息比如'8:55'没有这个UI)
        ListItems=[message for message in chatList.children(control_type='ListItem') if message.window_text()!=Buttons.CheckMoreMessagesButton['title']]#产看更多消息内部也有按钮,所以需要筛选一下
        if chats_only:
            ListItems=[message for message in ListItems if message.descendants(control_type='Button')]
        #点击聊天区域侧边栏和头像之间的位置来激活滑块,不直接main_window.click_input()是为了防止点到消息
        x,y=chatList.rectangle().left+8,(main_window.rectangle().top+main_window.rectangle().bottom)//2#
        if len(ListItems)>=number:#聊天区域内部不需要遍历就可以获取到的消息数量大于number条
            ListItems=ListItems[-number:]#返回从后向前数number条消息
        if len(ListItems)<number:#
            ##########################################################
            if scrollable:
                mouse.click(coords=(chatList.rectangle().right-10,chatList.rectangle().bottom-5))
                while len(ListItems)<number:
                    chatList.iface_scroll.SetScrollPercent(verticalPercent=0.0,horizontalPercent=1.0)#调用SetScrollPercent方法向上滚动,verticalPercent=0.0表示直接将scrollbar一下子置于顶部
                    mouse.scroll(coords=(x,y),wheel_dist=1000)
                    ListItems=[message for message in chatList.children(control_type='ListItem') if message.window_text()!=Buttons.CheckMoreMessagesButton['title']]
                    if chats_only:
                        ListItems=[message for message in ListItems if message.descendants(control_type='Button')]
                    if not viewMoreMesssageButton.exists():#向上遍历时如果查看更多消息按钮不在存在说明已经到达最顶部,没有必要继续向上,直接退出循环
                        break
                ListItems=ListItems[-number:]
            else:#无法滚动,说明就这么多了,有可能是刚添加好友或群聊或者是清空了聊天记录,只发了几条消息
                ListItems=ListItems[-number:]
        #######################################################
        if close_wechat:
            main_window.close()
        if parse:
            for ListItem in ListItems:
                message_sender,message_content,message_type=Tools.parse_message_content(ListItem=ListItem,friendtype=friendtype)
                chats.append({'发送人':message_sender,'消息内容':message_content,'消息类型':message_type})
            return chats
        else:
            return ListItems

    @staticmethod
    def parse_message_content(ListItem:ListItemWrapper,friendtype:str)->tuple[str,str,str]:
        '''
        该方法用来将主界面右侧聊天区域内的单个ListItem消息转换为文本,传入对象为Listitem
        Args:
            ListItem:主界面右侧聊天区域内ListItem形式的消息
            friendtype:聊天区域是群聊还是好友
        Returns:
            message_sender:发送消息的对象
            message_content:发送的消息
            message_type:消息类型,具体类型:{'文本','图片','视频','语音','文件','动画表情','视频号','链接','聊天记录','引用消息','卡片链接','微信转账'}
        '''
        language=Tools.language_detector()
        message_content=''
        message_type=''
        #至于消息的内容那就需要仔细判断一下了
        #微信在链接的判定上比较模糊,音乐和链接最后统一都以卡片的形式在聊天记录中呈现,所以这里不区分音乐和链接,都以链接卡片的形式处理
        specialMegCN={'[图片]':'图片','[视频]':'视频','[动画表情]':'动画表情','[视频号]':'视频号','[链接]':'链接','[聊天记录]':'聊天记录'}
        specialMegEN={'[Photo]':'图片','[Video]':'视频','[Sticker]':'动画表情','[Channel]':'视频号','[Link]':'链接','[Chat History]':'聊天记录'}
        specialMegTC={'[圖片]':'图片','[影片]':'视频','[動態貼圖]':'动画表情','[影音號]':'视频号','[連結]':'链接','[聊天記錄]':'聊天记录'}
        #系统消息
        if len(ListItem.descendants(control_type='Button'))==0:
            message_sender='系统'
            message_content=ListItem.window_text()
            message_type='系统消息'
        else: #不同语言,处理非系统消息内容时不同
            AudioPattern=SpecialMessages.AudioPattern
            message_sender=ListItem.children()[0].children(control_type='Button')[0].window_text()
            if language=='简体中文':
                if ListItem.window_text() in specialMegCN.keys():#内容在特殊消息中
                    message_sender=ListItem.children()[0].children(control_type='Button')[0].window_text()
                    message_content=specialMegCN.get(ListItem.window_text())
                    message_type=specialMegCN.get(ListItem.window_text())
                else:#文件,卡片链接,语音,以及正常的文本消息
                    if re.match(AudioPattern,ListItem.window_text()):#匹配是否是语音消息
                        try:#是语音消息就定位语音转文字结果
                            if friendtype=='群聊':
                                audio_content=ListItem.descendants(control_type='Text')[2].window_text()
                                message_content=ListItem.window_text()+f'  消息内容:{audio_content}'
                                message_type='语音'
                            else:
                                audio_content=ListItem.descendants(control_type='Text')[1].window_text()
                                message_content=ListItem.window_text()+f'  消息内容:{audio_content}'
                                message_type='语音'
                        except Exception:#定位时不排除有人只发送[语音]5秒这样的文本消息，所以可能出现异常
                            message_content=ListItem.window_text()
                            message_type='文本'
                    elif ListItem.window_text()=='[文件]':
                        filename=ListItem.descendants(control_type='Text')[0].window_text()
                        stem,extension=os.path.splitext(filename)
                        #文件这个属性的ListItem内有很多文本,正常来说文件名不是第一个就是第二个,这里哪一个有后缀名哪一个就是文件名
                        if not extension:
                            filename=ListItem.descendants(control_type='Text')[1].window_text()
                        message_content=f'{filename}'
                        message_type='文件'
                    elif len(ListItem.descendants(control_type='Text'))>=3:#ListItem内部文本ui个数大于3一般是卡片链接或引用消息或聊天记录
                        cardContent=ListItem.descendants(control_type='Text')
                        cardContent=[link.window_text() for link in cardContent]
                        message_content='卡片链接内容:'+','.join(cardContent)
                        message_type='卡片链接'
                        if ListItem.window_text()=='微信转账':
                            index=cardContent.index('微信转账')
                            message_content=f'微信转账:{cardContent[index-2]}:{cardContent[index-1]}'
                            message_type='微信转账'
                        if "引用  的消息 :" in ListItem.window_text():
                            splitlines=ListItem.window_text().splitlines()
                            message_content=f'{splitlines[0]}引用消息内容:{splitlines[1:]}'
                            message_type='引用消息'
                        if '小程序' in cardContent:
                            message_content='小程序内容:'+','.join(cardContent)
                            message_type='小程序'
                    else:#正常文本
                        message_content=ListItem.window_text()
                        message_type='文本'

            if language=='英文':
                if ListItem.window_text() in specialMegEN.keys():
                    message_content=specialMegEN.get(ListItem.window_text())
                    message_type=specialMegEN.get(ListItem.window_text())
                else:#文件,卡片链接,语音,以及正常的文本消息
                    if re.match(AudioPattern,ListItem.window_text()):#匹配是否是语音消息
                        try:#是语音消息就定位语音转文字结果
                            if friendtype=='群聊':
                                audio_content=ListItem.descendants(control_type='Text')[2].window_text()
                                message_content=ListItem.window_text()+f'  消息内容:{audio_content}'
                                message_type='语音'
                            else:
                                audio_content=ListItem.descendants(control_type='Text')[1].window_text()
                                message_content=ListItem.window_text()+f'  消息内容:{audio_content}'
                                message_type='语音'
                        except Exception:#定位时不排除有人只发送[语音]5秒这样的文本消息，所以可能出现异常
                            message_content=ListItem.window_text()
                            message_type='文本'
                    elif ListItem.window_text()=='[File]':
                        filename=ListItem.descendants(control_type='Text')[0].window_text()
                        stem,extension=os.path.splitext(filename)
                        #文件这个属性的ListItem内有很多文本,正常来说文件名不是第一个就是第二个,这里哪一个有后缀名哪一个就是文件名
                        if not extension:
                            filename=ListItem.descendants(control_type='Text')[1].window_text()
                        message_content=f'{filename}'
                        message_type='文件'

                    elif len(ListItem.descendants(control_type='Text'))>=3:#ListItem内部文本ui个数大于3一般是卡片链接或引用消息或聊天记录
                        cardContent=ListItem.descendants(control_type='Text')
                        cardContent=[link.window_text() for link in cardContent]
                        message_content='卡片链接内容:'+','.join(cardContent)
                        message_type='卡片链接'
                        if ListItem.window_text()=='Weixin Transfer':
                            index=cardContent.index('Weixin Transfer')
                            message_content=f'微信转账:{cardContent[index-2]}:{cardContent[index-1]}'
                            message_type='微信转账'
                        if "Quote 's message:" in ListItem.window_text():
                            splitlines=ListItem.window_text().splitlines()
                            message_content=f'{splitlines[0]}引用消息内容:{splitlines[1:]}'
                            message_type='引用消息'
                        if 'Mini Programs' in cardContent:
                            message_content='小程序内容:'+','.join(cardContent)
                            message_type='小程序'

                    else:#正常文本
                        message_content=ListItem.window_text()
                        message_type='文本'

            if language=='繁体中文':
                if ListItem.window_text() in specialMegTC.keys():
                    message_sender=ListItem.children()[0].children(control_type='Button')[0].window_text()
                    message_content=specialMegTC.get(ListItem.window_text())
                    message_type=specialMegTC.get(ListItem.window_text())
                else:#文件,卡片链接,语音,以及正常的文本消息
                    if re.match(AudioPattern,ListItem.window_text()):#匹配是否是语音消息
                        message_sender=ListItem.children()[0].children(control_type='Button')[0].window_text()
                        try:#是语音消息就定位语音转文字结果
                            if friendtype=='群聊':
                                audio_content=ListItem.descendants(control_type='Text')[2].window_text()
                                message_content=ListItem.window_text()+f'  消息内容:{audio_content}'
                                message_type='语音'
                            else:
                                audio_content=ListItem.descendants(control_type='Text')[1].window_text()
                                message_content=ListItem.window_text()+f'  消息内容:{audio_content}'
                                message_type='语音'
                        except Exception:#定位时不排除有人只发送[语音]5秒这样的文本消息，所以可能出现异常
                            message_content=ListItem.window_text()
                            message_type='文本'

                    elif ListItem.window_text()=='[檔案]':
                        message_sender=ListItem.children()[0].children(control_type='Button')[0].window_text()
                        filename=ListItem.descendants(control_type='Text')[0].window_text()
                        stem,extension=os.path.splitext(filename)
                        #文件这个属性的ListItem内有很多文本,正常来说文件名不是第一个就是第二个,这里哪一个有后缀名哪一个就是文件名
                        if not extension:
                            filename=ListItem.descendants(control_type='Text')[1].window_text()
                        message_content=f'{filename}'
                        message_type='文件'

                    elif len(ListItem.descendants(control_type='Text'))>=3:#ListItem内部文本ui个数大于3一般是卡片链接或引用消息或聊天记录
                        message_sender=ListItem.children()[0].children(control_type='Button')[0].window_text()
                        cardContent=ListItem.descendants(control_type='Text')
                        cardContent=[link.window_text() for link in cardContent]
                        message_content='卡片链接内容:'+','.join(cardContent)
                        message_type='卡片链接'
                        if ListItem.window_text()=='微信轉賬':
                            index=cardContent.index('微信轉賬')
                            message_content=f'微信转账:{cardContent[index-2]}:{cardContent[index-1]}'
                            message_type='微信转账'
                        if "引用  的訊息 :" in ListItem.window_text():
                            splitlines=ListItem.window_text().splitlines()
                            message_content=f'{splitlines[0]}引用消息内容:{splitlines[1:]}'
                            message_type='引用消息'
                        if '小程式' in cardContent:
                            message_content='小程序内容:'+','.join(cardContent)
                            message_type='小程序'

                    elif len(ListItem.descendants(control_type='Button'))==0:
                        message_sender='系统'
                        message_content=ListItem.window_text()
                        message_type='系统消息'

                    else:#正常文本
                        message_sender=ListItem.children()[0].children(control_type='Button')[0].window_text()
                        message_content=ListItem.window_text()
                        message_type='文本'
        return message_sender,message_content,message_type

    @staticmethod
    def parse_moments_content(ListItem:ListItemWrapper)->dict[str]:
        '''
        该方法用来将朋友圈内每一个ListItem消息转换dict,传入对象为Listitem
        Args:
            ListItem:朋友圈内ListItem形式的消息
        Returns:
            parse_result:{'好友备注':friend,'发布时间':post_time,\n
            '文本内容':text_content,'点赞者':likes,'评论内容':comments,\n
            '图片数量':image_num,'视频数量':video_num,'卡片链接':cardlink,\n
            '卡片链接内容':cardlink_content,'视频号':channel,'公众号链接内容':official_account_link}
        '''
        def get_next_sibling(element):
            """获取当前元素的同级下一个元素,如果不存在则返回None"""
            parent = element.parent()
            siblings = parent.children()
            try:
                current_idx=siblings.index(element)
                next_sibling=siblings[current_idx + 1]
            except IndexError:
                next_sibling=None
            return next_sibling
        comment_button=ListItem.descendants(**Buttons.CommentButton)[0]#朋友圈评论按钮
        channel_button=ListItem.descendants(**Buttons.ChannelButton)#视频号按钮
        panes=ListItem.descendants(control_type='Pane')
        #包含\d+张图片窗格如果存在那么说明有图片数量
        include_photo_pane=[pane.window_text() for pane in panes if re.match(r'包含\d+张图片',pane.window_text())]
        #注意uia_control查找时descendants方法是无法使用title_re的，只有win32_control的child_window才可以
        #不然直接title_re省的遍历了
        video_pane=[pane for pane in panes if pane.window_text()==Panes.VideoPane['title']]#视频播放窗格
        comment_list=ListItem.descendants(**Lists.CommentList)#朋友圈评论列表,可能有可能没有
        buttons=ListItem.descendants(control_type='Button')#一条朋友圈内所有的按钮
        friend=buttons[0].window_text()#好友名称也就是头像按钮的文本，头像按钮必然是所有按钮元素的首个
        texts=ListItem.descendants(control_type='Text')#texts为一条朋友圈内所有的文本内容列表,最大长度为3
        texts=[ctrl.window_text() for ctrl in texts]
        comment_pane_text=comment_button.parent().children(control_type='Text')
        like_pane=get_next_sibling(comment_button.parent())
        if like_pane:
            likes=like_pane.descendants(control_type='Text')[0].window_text().split('，')
        else:
            likes=[]#点赞共同好友,可能有可能没有
        #可能包含朋友圈文本内容,时间戳,点赞好友名字
        #texts长度为1时,必然是时间戳，没有文本与点赞
        #texts长度为3时文本内容,时间戳,点赞好友名字都有
        #texts长度为2时最麻烦,可能是前两个或后两个的组合:
        #朋友圈文本内容+时间戳,时间戳+点赞好友名字
        #时间戳与评论按钮同一个parent，因此可以直接获取
        post_time=comment_pane_text[0].window_text()
        image_num=0 if not include_photo_pane else int(re.search(r'\d+',include_photo_pane[0])[0])
        video_num=len(video_pane)#视频数量,可能有可能无
        text_content=''#文本内容,可能有可能无,默认无
        comments=[]#评论内容,可能可能没有
        channel=''#视频号
        cardlink=''#卡片链接
        official_account_link=''#公众号链接
        cardlink_content=''#卡片链接的具体内容
        if comment_list:#有人给这个朋友圈评论了
            comments=[ListItem.window_text() for ListItem in comment_list[0].children(control_type='ListItem')]
        #评论按钮父窗口内的文本，一般而言长度是1，即只有时间戳
        #如果长度为3，那么是卡片链接(BiliBili,QQ音乐等支持以卡片形式分享到朋友圈的连接)或者视频号
        if len(comment_pane_text)==2:
            if channel_button:#视频号按钮存在说明分享的是视频号
                channel=comment_pane_text[1].window_text()
            else:
                cardlink=comment_pane_text[1].window_text()
                cardlink_content=buttons[2].window_text()
            if len(texts)>=4:#文本内容+时间戳+来源(哔哩哔哩或QQ音乐等)+评论
                text_content=texts[0]
            if len(texts)==3 and texts[0]!=post_time:#文本内容+时间戳+来源
                text_content=texts[0]
        if len(comment_pane_text)==1:
            official_account_button=[button for button in buttons if button.window_text() in ListItem.window_text() and button.window_text()!=friend and button.window_text()!=Buttons.ImageButton['title']]
            if len(texts)>=3:
                text_content=texts[0]
            if len(texts)==2 and texts[0]!=post_time:#文本内容+时间戳
                text_content=texts[0]
            if official_account_button:
                official_account_link=official_account_button[0].window_text()
        parse_result={'好友备注':friend,'发布时间':post_time,'文本内容':text_content,
        '点赞者':likes,'评论内容':comments,'图片数量':image_num,'视频数量':video_num,
        '卡片链接':cardlink,'卡片链接内容':cardlink_content,'视频号':channel,'公众号链接内容':official_account_link}
        return parse_result

    @staticmethod
    def parse_chat_history(ListItem:ListItemWrapper):
        '''
        该方法用来将聊天记录窗口内每一条聊天记录的ListItem消息转换为文本,传入对象为Listitem
        Args:
            ListItem:主界面右侧聊天区域内ListItem形式的消息
        Returns:
            message_sender:发送消息的对象
            message_content:发送的消息
            message_type:消息类型,具体类型:{'文本','图片','视频','语音','文件','动画表情','视频号','链接','聊天记录','引用消息','卡片链接','微信转账'}
        '''
        language=Tools.language_detector()
        message_sender=ListItem.descendants(control_type='Text')[0].window_text()#无论什么类型消息,发送人永远是属性为Texts的UI组件中的第一个
        send_time=ListItem.descendants(control_type='Text')[1].window_text()#无论什么类型消息.发送时间都是属性为Texts的UI组件中的第二个
        #至于消息的内容那就需要仔细判断一下了
        specialMegCN={'[图片]':'图片消息','[视频]':'视频消息','[动画表情]':'动画表情','[视频号]':'视频号'}
        specialMegEN={'[Photo]':'图片消息','[Video]':'视频消息','[Sticker]':'动画表情','[Channel]':'视频号'}
        specialMegTC={'[圖片]':'图片消息','[影片]':'视频消息','[動態貼圖]':'动画表情','[影音號]':'视频号'}
        #不同语言,处理消息内容时不同
        AudioPattern=SpecialMessages.AudioPattern
        if language=='简体中文':
            if ListItem.window_text() in specialMegCN.keys():#内容在特殊消息中
                message_content=specialMegCN.get(ListItem.window_text())
            else:#文件,卡片链接,语音,以及正常的文本消息
                if ListItem.window_text()=='[文件]':
                    filename=ListItem.descendants(control_type='Text')[2].texts()[0]
                    message_content=f'文件:{filename}'
                elif re.match(AudioPattern,ListItem.window_text()):
                    message_content='语音消息'
                elif len(ListItem.descendants(control_type='Text'))>3:#
                    cardContent=ListItem.descendants(control_type='Text')[2:]
                    cardContent=[link.window_text() for link in cardContent]
                    if '微信转账' in cardContent:
                        index=cardContent.index('微信转账')
                        message_content=f'微信转账:{cardContent[index-2]}:{cardContent[index-1]}'
                    else:
                        message_content='卡片内容:'+','.join(cardContent)
                else:#正常文本
                    texts=ListItem.descendants(control_type='Text')
                    texts=[text.window_text() for text in texts]
                    message_content=texts[2]
        if language=='英文':
            if ListItem.window_text() in specialMegEN.keys():
                message_content=specialMegEN.get(ListItem.window_text())
            else:#文件,卡片链接,语音,以及正常的文本消息
                if ListItem.window_text()=='[File]':
                    filename=ListItem.descendants(control_type='Text')[2].texts()[0]
                    message_content=f'文件:{filename}'
                elif re.match(AudioPattern,ListItem.window_text()):
                    message_content='语音消息'

                elif len(ListItem.descendants(control_type='Text'))>3:#
                    cardContent=ListItem.descendants(control_type='Text')[2:]
                    cardContent=[link.window_text() for link in cardContent]
                    if 'Weixin Transfer' in cardContent:
                        index=cardContent.index('Weixin Transfer')
                        message_content=f'微信转账:{cardContent[index-2]}:{cardContent[index-1]}'
                    else:
                        message_content='卡片内容:'+','.join(cardContent)
                else:#正常文本
                    texts=ListItem.descendants(control_type='Text')
                    texts=[text.window_text() for text in texts]
                    message_content=texts[2]

        if language=='繁体中文':
            if ListItem.window_text() in specialMegTC.keys():
                message_content=specialMegTC.get(ListItem.window_text())
            else:#文件,卡片链接,语音,以及正常的文本消息
                if ListItem.window_text()=='[檔案]':
                    filename=ListItem.descendants(control_type='Text')[2].texts()[0]
                    message_content=f'文件:{filename}'
                elif re.match(AudioPattern,ListItem.window_text()):
                    message_content='语音消息'
                elif len(ListItem.descendants(control_type='Text'))>3:#
                    cardContent=ListItem.descendants(control_type='Text')[2:]
                    cardContent=[link.window_text() for link in cardContent]
                    if ListItem.window_text()=='' and '微信轉賬' in cardContent:
                        index=cardContent.index('微信轉賬')
                        message_content=f'微信转账:{cardContent[index-2]}:{cardContent[index-1]}'
                    else:
                        message_content='链接卡片内容:'+','.join(cardContent)
                else:#正常文本
                    texts=ListItem.descendants(control_type='Text')
                    texts=[text.window_text() for text in texts]
                    message_content=texts[2]
        return message_sender,send_time,message_content

    @staticmethod
    def pull_latest_message(chatList:ListViewWrapper)->tuple[str,str]|tuple[None,None]:#获取聊天界面内的聊天记录
        '''
        该方法用来获取聊天界面内的最新的一条聊天消息(非时间戳或系统消息:以下是新消息)
        返回值为最新的消息内容以及消息发送人,需要注意的是如果界面内没有消息或最新消息是系统消息
        那么返回None,None,该方法可以用来配合自动回复方法使用
        Args:
            chatList:打开好友的聊天窗口后的右侧聊天列表,该函数主要用内嵌于自动回复消息功能中使用
                因此传入的参数为主界面右侧的聊天列表,也就是Main_window.FriendChatList

        Returns:
            (content,sender):消息发送人最新的新消息内容
        Examples:
            ```
            from pywechat import Tools,Main_window,pull_latest_message
            edit_area,main_window=Tools.open_dialog_window(friend='路人甲')
            content,sender=pull_latest_message(chatList=main_window.child_window(**Main_window.FriendChatList))
            print(content,sender)
            ```
        '''
        #筛选消息，每条消息都是一个listitem
        if chatList.exists():
            if chatList.children():#如果聊天列表存在(不存在的情况:清空了聊天记录)
                ###################
                if chatList.children()[-1].descendants(control_type='Button') and chatList.children()[-1].window_text()!='':#必须是非系统消息也就是消息内部含有发送人按钮这个UI
                    content=chatList.children()[-1].window_text()
                    sender=chatList.children()[-1].descendants(control_type='Button')[0].window_text()
                    return content,sender
        return None,None

    @staticmethod
    def find_current_wxid()->str:
        '''
        该方法通过解析Accinfo.dat文件来检测当前登录的wxid,使用时必须登录微信,否则返回空字符串
        '''
        config=Tools.where_config_folder(open_folder=False)
        AccInfo=os.path.join(config,'AccInfo.dat')
        if os.path.exists(AccInfo):
            with open(AccInfo, 'rb') as f:
                bytes=f.read()
            wxid_start=bytes.find(b'wxid_')
            wxid_end=bytes.find(b'\x1a',wxid_start)
            wxid=bytes[wxid_start:wxid_end].decode()
            return wxid
        return ''

    @staticmethod
    def where_database_folder(open_folder:bool=False):
        '''
        该方法用来获取微信数据库存放路径(文件夹)\n
        使用时微信必须登录,否则无法获取到完整路径
        Args:
            open_folder:是否打开微信数据库所在文件夹,默认不打开
        Returns:
            folder_path:数据库存放路径
        '''
        wechat_process=None
        for process in psutil.process_iter(['pid', 'name']):
            if process.info['name']=='WeChat.exe':
                wechat_process=process
                break
        #只要微信登录了,就一定会用到本地聊天文件保存位置:Wechat Files下的一个wxid开头的文件下的Msg,
        #这个文件夹里包含了聊天纪录数据等内容
        #wechat_process是进程句柄,通过这个进程句柄的memory_maps方法可以实现
        #内存映射文件检测
        folder_path=''
        for mem_map in wechat_process.memory_maps():
            if 'Msg'  in mem_map.path:
                folder_path=mem_map.path
                #获取到的路径的basename是含\Msg\xxx.db，我们只需要他的dir就可以然后
                folder_path=os.path.dirname(folder_path)
                break
        if open_folder and os.path.exists(folder_path):
            os.startfile(folder_path)
        return folder_path

    @staticmethod
    def where_chatfiles_folder(open_folder:bool=False):
        '''
        该方法用来获取微信聊天文件存放路径(文件夹)\n
        使用时微信必须登录,否则无法获取到完整路径
        Args:
            open_folder:是否打开存放聊天文件的文件夹,默认不打开
        Returns:
            folder_path:聊天文件存放路径
        '''
        wechat_process=None
        for process in psutil.process_iter(['pid', 'name']):
            if process.info['name']=='WeChat.exe':
                wechat_process=process
                break
        #只要微信登录了,就一定会用到本地聊天文件保存位置:Wechat Files下的一个wxid开头的文件下的Msg,
        #这个文件夹里包含了聊天纪录数据等内容
        #wechat_process是进程句柄,通过这个进程句柄的memory_maps方法可以实现
        #内存映射文件检测
        base_folder=''
        for mem_map in wechat_process.memory_maps():
            if 'Msg'  in mem_map.path:
                base_folder=mem_map.path
                #获取到的路径的basename是含\Msg\xxx.db，我们只需要他的dir就可以然后把Msg换为FileStorage
                base_folder=os.path.dirname(base_folder).replace('Msg','FileStorage')
                break
        folder_path=os.path.join(base_folder,'File')
        if open_folder and folder_path:
            os.startfile(folder_path)
        return folder_path

    @staticmethod
    def where_videos_folder(open_folder:bool=False):
        '''
        该方法用来获取微信聊天视频存放路径(文件夹)\n
        使用时微信必须登录,否则无法获取到完整路径
        Args:
            open_folder:是否打开聊天视频存放路径,默认不打开
        Returns:
            folder_path:聊天视频存放路径
        '''
        wechat_process=None
        for process in psutil.process_iter(['pid', 'name']):
            if process.info['name']=='WeChat.exe':
                wechat_process=process
                break
        #只要微信登录了,就一定会用到本地聊天文件保存位置:Wechat Files下的一个wxid开头的文件下的Msg,
        #这个文件夹里包含了聊天纪录数据等内容
        #wechat_process是进程句柄,通过这个进程句柄的memory_maps方法可以实现
        #内存映射文件检测
        base_folder=''
        for mem_map in wechat_process.memory_maps():
            if 'Msg'  in mem_map.path:
                base_folder=mem_map.path
                #获取到的路径的basename是含\Msg\xxx.db，我们只需要他的dir就可以然后把Msg换为FileStorage
                base_folder=os.path.dirname(base_folder).replace('Msg','FileStorage')
                break
        folder_path=os.path.join(base_folder,'Video')
        if open_folder and folder_path:
            os.startfile(folder_path)
        return folder_path

    @staticmethod
    def where_SnsCache_folder(open_folder:bool=False):
        '''
        该方法用来获取微信朋友圈图片视频缓存路径(文件夹)\n
        使用时微信必须登录,否则无法获取到完整路径
        Args:
            open_folder:是否打开朋友圈图片视频缓存路径,默认不打开
        Returns:
            folder_path:朋友圈图片视频缓存路径
        '''
        wechat_process=None
        for process in psutil.process_iter(['pid', 'name']):
            if process.info['name']=='WeChat.exe':
                wechat_process=process
                break
        #只要微信登录了,就一定会用到本地聊天文件保存位置:Wechat Files下的一个wxid开头的文件下的Msg,
        #这个文件夹里包含了聊天纪录数据等内容
        #wechat_process是进程句柄,通过这个进程句柄的memory_maps方法可以实现
        #内存映射文件检测
        base_folder=''
        for mem_map in wechat_process.memory_maps():
            if 'Msg'  in mem_map.path:
                base_folder=mem_map.path
                #获取到的路径的basename是含\Msg\xxx.db，我们只需要他的dir就可以然后把Msg换为FileStorage
                base_folder=os.path.dirname(base_folder).replace('Msg','FileStorage')
                break
        sns_cache=os.path.join(base_folder,'Sns','Cache')
        if open_folder and os.path.exists(sns_cache):
            os.startfile(sns_cache)
        return sns_cache

    @staticmethod
    def where_config_folder(open_folder:bool=False):
        '''
        该方法用来获取微信配置文件存放路径(文件夹)\n
        使用时微信必须登录,否则无法获取到完整路径
        Args:
            open_folder:是否打开微信配置文件所在文件夹,默认不打开
        Returns:
            folder_path:配置文件存放路径
        '''
        wechat_process=None
        for process in psutil.process_iter(['pid', 'name']):
            if process.info['name']=='WeChat.exe':
                wechat_process=process
                break
        # 只要微信登录了,就一定会用到本地聊天文件保存位置:Wechat Files下的一个wxid开头的文件下的Msg,
        # 这个文件夹里包含了聊天纪录数据等内容
        # wechat_process是进程句柄,通过这个进程句柄的memory_maps方法可以实现
        # 内存映射文件检测
        folder_path=''
        for mem_map in wechat_process.memory_maps():
            if 'Msg'  in mem_map.path:
                folder_path=mem_map.path
                #获取到的路径的basename是含\Msg\xxx.db，我们只需要他的dir就可以然后把Msg换为config
                folder_path=os.path.dirname(folder_path).replace('Msg','config')
                break
        if open_folder and os.path.exists(folder_path):
            os.startfile(folder_path)
        return folder_path


    @staticmethod
    def NativeSaveFile(folder_path)->None:
        '''
        该方法用来处理微信内部点击另存为后弹出的windows本地保存文件窗口
        Args:
            folder_path:保存文件的文件夹路径
        '''
        desktop=Desktop(**Independent_window.Desktop)
        save_as_window=desktop.window(**Windows.NativeSaveFileWindow)
        prograss_bar=save_as_window.child_window(control_type='ProgressBar',class_name='msctls_progress32',framework_id='Win32')
        path_bar=prograss_bar.child_window(class_name='ToolbarWindow32',control_type='ToolBar',found_index=0)
        if re.search(r':\s*(.*)',path_bar.window_text().lower()).group(1)!=folder_path.lower():
            rec=path_bar.rectangle()
            mouse.click(coords=(rec.right-5,int(rec.top+rec.bottom)//2))
            pyautogui.press('backspace')
            pyautogui.hotkey('ctrl','v',_pause=False)
            pyautogui.press('enter')
            time.sleep(0.5)
        pyautogui.hotkey('alt','s')

    @staticmethod
    def NativeChooseFolder(folder_path)->None:
        '''
        该方法用来处理微信内部点击选择文件夹后弹出的windows本地选择文件夹窗口
        Args:
            folder_path:保存文件的文件夹路径
        '''
        #如果path_bar上的内容与folder_path不一致,那么删除复制粘贴
        #如果一致,点击选择文件夹窗口
        Systemsettings.copy_text_to_windowsclipboard(folder_path)
        desktop=Desktop(**Independent_window.Desktop)
        save_as_window=desktop.window(**Windows.NativeChooseFolderWindow)
        prograss_bar=save_as_window.child_window(control_type='ProgressBar',class_name='msctls_progress32',framework_id='Win32')
        path_bar=prograss_bar.child_window(class_name='ToolbarWindow32',control_type='ToolBar',found_index=0)
        if re.search(r':\s*(.*)',path_bar.window_text()).group(1)!=folder_path:
            rec=path_bar.rectangle()
            mouse.click(coords=(rec.right-5,int(rec.top+rec.bottom)//2))
            pyautogui.press('backspace')
            pyautogui.hotkey('ctrl','v',_pause=False)
            pyautogui.press('enter')
            time.sleep(0.5)
        choose_folder_button=save_as_window.child_window(control_type='Button',title='选择文件夹')
        choose_folder_button.click_input()

    def open_traywnd()->WindowSpecification:
        '''点击右下角的显示隐藏图标按钮打开系统托盘'''
        #打开系统托盘
        desktop=Desktop(backend='uia')
        #微信的新消息通知托盘的句柄
        #任务栏
        tool_bar_handle=win32gui.FindWindow("Shell_TrayWnd",None)
        tool_bar=desktop.window(handle=tool_bar_handle)#要进行后续点击等操作需要一个pywinauto的windowSpecification对象
        #右下角^按钮,名称为显示隐藏图标的按钮
        tool_bar.child_window(control_type='Button',auto_id="SystemTrayIcon",title='显示隐藏的图标').click_input()
        #弹出的溢出菜单
        tray_wnd=desktop.window(class_name="TopLevelWindowForOverflowXamlIsland")
        return tray_wnd

    def open_wechat_traywnd()->WindowSpecification:
        tray_notify=None
        desktop=Desktop(backend='uia')
        #微信的新消息通知托盘的句柄
        #任务栏
        tray_wnd=Tools.open_traywnd()
        tray_notify=desktop.window(class_name="TrayNotifyWnd",title='微信')
        #在弹出的溢出菜单中找到绿色的微信图标
        wechat_button=tray_wnd.descendants(control_type='Button',title='微信')[0]
        if not wechat_button:
            raise WeChatNotStartError
        mid_point=wechat_button.rectangle().mid_point()
        center_x=mid_point.x
        center_y=mid_point.y
        #必须使用该底层方法将鼠标移动到微信按钮上才可以激活新消息窗口,使用pyautogui和mouse.move都不行！
        def hardware_mouse_move(x,y):
            """使用硬件级鼠标移动"""
            #直接设置光标位置
            ctypes.windll.user32.SetCursorPos(x, y)
            #发送硬件鼠标移动事件
            for _ in range(3):
                ctypes.windll.user32.mouse_event(0x0001, 1, 0, 0, 0)  # MOUSEEVENTF_MOVE
                time.sleep(0.05)
        hardware_mouse_move(center_x,center_y)
        if not tray_notify.exists():
            tray_notify=None
        return tray_notify


class API():
    '''这个模块包括打开指定名称小程序,打开制定名称微信公众号的功能
    若有其他自动化开发者需要在微信内的这两个功能下进行自动化操作可调用此模块
    '''
    @staticmethod
    def open_wechat_miniprogram(name:str,load_delay:float=2.5,wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True)->tuple[WindowSpecification,WindowSpecification|None]:
        '''
        该方法用于打开指定小程序
        Args:
            name:微信小程序名字
            load_delay:搜索小程序名称后等待时长,默认为2.5秒
            wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
            is_maximize:微信界面是否全屏,默认全屏。
            close_wechat:任务结束后是否关闭微信,默认关闭
        Returns:
            (program_window,main_window):program_window:小程序主界面
            main_window:微信主界面,当close_wechat设置为True时,main_window为None
        '''
        desktop=Desktop(**Independent_window.Desktop)
        program_window,main_window=Tools.open_program_pane(wechat_path=wechat_path,is_maximize=is_maximize,close_wechat=close_wechat)
        miniprogram_tab=program_window.child_window(title='小程序',control_type='TabItem')
        miniprogram_tab.click_input()
        time.sleep(load_delay)
        try:
            more=program_window.child_window(title='更多',control_type='Text',found_index=0)#小程序面板内的更多文本
        except Exception:
            program_window.close()
            print('网络不良,请尝试增加load_delay时长,或更换网络')
        rec=more.rectangle()
        mouse.click(coords=(rec.right+20,rec.top-50))
        up=5
        search=program_window.child_window(control_type='Edit',title='搜索小程序')
        while not search.exists():
            mouse.click(coords=(rec.right+20,rec.top-50-up))
            search=program_window.child_window(control_type='Edit',title='搜索小程序')
            up+=5
        search.click_input()
        Systemsettings.copy_text_to_windowsclipboard(name)
        pyautogui.hotkey('ctrl','v',_pause=False)
        pyautogui.press("enter")
        time.sleep(load_delay)
        try:
            search_result=program_window.child_window(control_type="Document",class_name="Chrome_RenderWidgetHostHWND")
            text=search_result.child_window(title_re=name,control_type='Text',found_index=0)
            text.click_input()
            program_window.close()
            program=desktop.window(control_type='Pane',title=name)
            return program,main_window
        except Exception:
            program_window.close()
            raise NoResultsError('查无此小程序!')

    @staticmethod
    def open_official_account(name:str,load_delay:float=1,wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True)->tuple[WindowSpecification,WindowSpecification|None]:
        '''
        该方法用于打开指定的微信公众号
        Args:
            name:微信公众号名称
            load_delay:加载搜索公众号结果的时间,单位:s
            wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
            is_maximize:微信界面是否全屏,默认全屏。
        Returns:
            (chat_window,main_window):chat_window:与公众号的聊天界面
            main_window:微信主界面,当close_wechat设置为True时返回值为None
        '''
        desktop=Desktop(**Independent_window.Desktop)
        try:
            search_window,main_window=Tools.open_search(wechat_path=wechat_path,is_maximize=is_maximize,close_wechat=close_wechat)
            time.sleep(load_delay)
        except ElementNotFoundError:
            search_window.close()
            print('网络不良,请尝试增加load_delay时长,或更换网络')
        try:
            official_acount_button=search_window.child_window(**Buttons.OfficialAcountButton)
            official_acount_button.click_input()
        except ElementNotFoundError:
            search_window.close()
            print('网络不良,请尝试增加load_delay时长,或更换网络')
        search=search_window.child_window(control_type='Edit',found_index=0)
        search.click_input()
        Systemsettings.copy_text_to_windowsclipboard(name)
        pyautogui.hotkey('ctrl','v')
        pyautogui.press('enter')
        time.sleep(load_delay)
        try:
            search_result=search_window.child_window(control_type="Button",found_index=1,framework_id="Chrome")
            search_result.click_input()
            official_acount_window=Tools.move_window_to_center(Independent_window.OfficialAccountWindow)
            search_window.close()
            subscribe_button=official_acount_window.child_window(**Buttons.SubscribeButton)
            if subscribe_button.exists():
                subscribe_button.click_input()
                time.sleep(2)
            send_message_text=official_acount_window.child_window(**Texts.SendMessageText)
            send_message_text.click_input()
            chat_window=desktop.window(**Independent_window.OfficialAccountChatWindow)
            chat_window.maximize()
            official_acount_window.close()
            return chat_window,main_window
        except ElementNotFoundError:
            search_window.close()
            raise NoResultsError('查无此公众号!')

    @staticmethod
    def search_channels(search_content:str,load_delay:float=1,wechat_path:str=None,wechat_maximize:bool=True,is_maximize:bool=True,close_wechat:bool=True)->tuple[WindowSpecification,WindowSpecification|None]:
        '''
        该方法用于打开视频号并搜索指定内容
        Args:
            search_content:在视频号内待搜索内容
            load_delay:加载查询结果的时间,单位:s
            wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
            is_maximize:微信界面是否全屏,默认全屏。
        Returns:
            (chat_history_window,main_window):chat_history_window:好友设置界面内点击好友头像后的好友个人简介界面
            main_window:微信主界面,close_wechat设置为True时,main_window为None
        '''
        Systemsettings.copy_text_to_windowsclipboard(search_content)
        channel_widow,main_window=Tools.open_channels(wechat_maximize=wechat_maximize,is_maximize=is_maximize,wechat_path=wechat_path,close_wechat=close_wechat)
        search_bar=channel_widow.child_window(control_type='Edit',title='搜索',framework_id='Chrome')
        while not search_bar.exists():
            time.sleep(0.1)
            search_bar=channel_widow.child_window(control_type='Edit',title='搜索',framework_id='Chrome')
        search_bar.click_input()
        pyautogui.hotkey('ctrl','a')
        pyautogui.press('backspace')
        pyautogui.hotkey('ctrl','v')
        pyautogui.press('enter')
        time.sleep(load_delay)
        try:
            search_result=channel_widow.child_window(control_type='Document',title=f'{search_content}_搜索')
            return channel_widow,main_window
        except ElementNotFoundError:
            channel_widow.close()
            print('网络不良,请尝试增加load_delay时长,或更换网络')


def is_wechat_running()->bool:
    '''
    该方法通过检测当前windows系统的进程中
    是否有WeChat.exe该项进程来判断微信是否在运行
    '''
    wmi=win32com.client.GetObject('winmgmts:')
    processes=wmi.InstancesOf('Win32_Process')
    for process in processes:
        if process.Name.lower()=='Wechat.exe'.lower():
            return True
    return False

def language_detector()->str|None:
    """
    该函数查询注册表来检测当前微信的语言版本
    """
    #微信3.9版本的一般注册表路径
    reg_path=r"Software\Tencent\WeChat"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
            value=winreg.QueryValueEx(key,"LANG_ID")[0]
            language_map={
                0x00000009: '英文',
                0x00000004: '简体中文',
                0x00000404: '繁体中文'
            }
            return language_map.get(value)
    except FileNotFoundError:
        raise NotInstalledError

def open_wechat(wechat_path:str=None,is_maximize:bool=True)->WindowSpecification:
    '''
    该函数用来打开微信
    Args:
        wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
        is_maximize:微信界面是否全屏,默认全屏。
    Returns:
        main_window:微信主界面
    微信的打开分为四种情况:
    1.未登录,此时调用该函数会自动查找并使用命令行启动wechat.exe路径,在弹出的登录界面中点击进入微信打开微信主界面
    启动并点击登录进入微信(注:需勾选自动登录按钮,否则启动后为扫码登录)
    2.未登录但已弹出微信的登录界面,此时会自动点击进入微信打开微信
    注意:未登录的情况下打开微信需要在手机端第一次扫码登录后勾选自动登入的选项,否则启动微信后
    聊天界面没有进入微信按钮,将会触发异常提示扫码登录
    3.已登录，主界面最小化在状态栏，此时调用该函数会直接打开后台中的微信。
    4.已登录，主界面关闭，此时调用该函数会打开已经关闭的微信界面。
    '''
    #最多尝试40次，每次间隔0.5秒，最多20秒无法打开微信则抛出异常
    max_retry_times=40
    retry_interval=0.5
    #处理登录界面的闭包函数，点击进入微信，若微信登录界面存在直接传入窗口句柄，否则自己查找
    def handle_login_window(wechat_path=wechat_path,max_retry_times=max_retry_times, retry_interval=retry_interval, is_maximize=is_maximize):
        counter=0
        if wechat_path:#看看有没有传入wechat_path
            subprocess.Popen(wechat_path)
        if not wechat_path:#没有传入就自己找
            wechat_path=Tools.find_wechat_path(copy_to_clipboard=False)
            subprocess.Popen(wechat_path)
        #没有传入登录界面句柄，需要自己查找(此时对应的情况是微信未启动)
        login_window_handle=win32gui.FindWindow(Login_window.LoginWindow['class_name'],None)
        while not login_window_handle:
            login_window_handle= win32gui.FindWindow(Login_window.LoginWindow['class_name'],None)
            if login_window_handle:
                break
            counter+=1
            time.sleep(0.2)
            if counter>=max_retry_times:
                raise NoResultsError(f'微信打开失败,请检查网络连接或者微信是否正常启动！')
        #移动登录界面到屏幕中央
        login_window=Tools.move_window_to_center(Login_window.LoginWindow,login_window_handle)
        #点击登录按钮,等待主界面出现并返回
        try:
            login_button=login_window.child_window(**Login_window.LoginButton)
            login_button.set_focus()
            login_button.click_input()
            main_window_handle = 0
            while not main_window_handle:
                main_window_handle=win32gui.FindWindow(Main_window.MainWindow['class_name'],None)
                if main_window_handle:
                    break
                counter+=1
                time.sleep(retry_interval)
                if counter>=max_retry_times:
                    raise NetWorkNotConnectError
            main_window=Tools.move_window_to_center(handle=main_window_handle)
            if is_maximize:
                main_window.maximize()
            NetWorkErrotText=main_window.child_window(**Texts.NetWorkError)
            if NetWorkErrotText.exists():
                main_window.close()
                raise NetWorkNotConnectError(f'未连接网络,请连接网络后再进行后续自动化操作！')
            return main_window
        except ElementNotFoundError:
            raise ScanCodeToLogInError
    #open_wechat函数的主要逻辑：
    if Tools.is_wechat_running():#微信如果已经打开无需登录可以直接连接
        #同时查找主界面与登录界面句柄，二者有一个存在都证明微信已经启动
        main_window_handle=win32gui.FindWindow(Main_window.MainWindow['class_name'],None)
        login_window_handle=win32gui.FindWindow(Login_window.LoginWindow['class_name'],None)
        if main_window_handle:
            #威信运行时有最小化，主界面可见未关闭,主界面不可见关闭三种情况
            if win32gui.IsWindowVisible(main_window_handle):#主界面可见包含最小化
                if win32gui.GetWindowPlacement(main_window_handle)[1]==win32con.SW_SHOWMINIMIZED:#主界面最小化
                    win32gui.ShowWindow(main_window_handle,win32con.SW_SHOWNORMAL)
                    main_window=Tools.move_window_to_center(handle=main_window_handle)
                    if is_maximize:
                        main_window.maximize()
                    NetWorkErrotText=main_window.child_window(**Texts.NetWorkError)
                    if NetWorkErrotText.exists():
                        main_window.close()
                        raise NetWorkNotConnectError(f'未连接网络,请连接网络后再进行后续自动化操作！')
                    return main_window
                else:#主界面存在且未最小化
                    main_window=Tools.move_window_to_center(handle=main_window_handle)
                    if is_maximize:
                        main_window.maximize()
                    NetWorkErrotText=main_window.child_window(**Texts.NetWorkError)
                    if NetWorkErrotText.exists():
                        main_window.close()
                        raise NetWorkNotConnectError(f'未连接网络,请连接网络后再进行后续自动化操作！')
                    return main_window
            else:#主界面不可见
                #打开过主界面，关闭掉了，需要重新打开
                win32gui.ShowWindow(main_window_handle,win32con.SW_SHOWNORMAL)
                main_window=Tools.move_window_to_center(handle=main_window_handle)
                if is_maximize:
                    main_window.maximize()
                NetWorkErrotText=main_window.child_window(**Texts.NetWorkError)
                if NetWorkErrotText.exists():
                    main_window.close()
                    raise NetWorkNotConnectError(f'未连接网络,请连接网络后再进行后续自动化操作！')
                return main_window
        if login_window_handle:#微信启动了，但是.是登录界面在桌面上，不是主界面
            #处理登录界面
            return handle_login_window(max_retry_times,retry_interval,is_maximize)
    else:#微信未启动，需要先使用subprocess.Popen启动微信弹出登录界面后点击进入微信
        #处理登录界面
        return handle_login_window(max_retry_times,retry_interval,is_maximize)

def find_friend_in_MessageList(friend:str,wechat_path:str=None,is_maximize:bool=True,search_pages:int=5)->tuple[WindowSpecification|None,WindowSpecification]:
    '''
    该函数用于在会话列表中寻找好友(非公众号)。
    Args:
        friend:好友或群聊备注名称,需提供完整名称
        wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
        is_maximize:微信界面是否全屏,默认全屏。
        search_pages:在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
    Returns:
        (edit_area,main_windwo):若edit_area存在:返回值为 (edit_area,main_window) 同时返回好友聊天界面内的编辑区域与主界面
        否则:返回值为(None,main_window)
    '''
    def selecte_in_messageList(friend):
        '''
        用来返回会话列表中名称为friend的ListItem项内的Button与是否为最后一项
        '''
        is_last=False
        message_list=message_list_pane.children(control_type='ListItem')
        buttons=[friend.children()[0].children()[0] for friend in message_list]
        friend_button=None
        for i in range(len(buttons)):
            if friend==buttons[i].texts()[0]:
                friend_button=buttons[i]
                break
        if i==len(buttons)-1:
            is_last=True
        return friend_button,is_last

    main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=is_maximize)
    #先看看当前微信右侧界面是不是聊天界面可能存在不是聊天界面的情况比如是纯白色的微信的icon
    current_chat=main_window.child_window(**Main_window.CurrentChatWindow)
    chats_button=main_window.child_window(**SideBar.Chats)
    message_list_pane=main_window.child_window(**Main_window.ConversationList)
    if not message_list_pane.exists():
        chats_button.click_input()
    if not message_list_pane.is_visible():
        chats_button.click_input()
    rectangle=message_list_pane.rectangle()
    scrollable=Tools.is_VerticalScrollable(message_list_pane)
    activateScollbarPosition=(rectangle.right-5, rectangle.top+20)
    if current_chat.exists() and current_chat.window_text()==friend:
    #如果当前主界面是某个好友的聊天界面且聊天界面顶部的名称为好友名称，直接返回结果,current_chat可能是刚登录打开微信的纯白色icon界面
        edit_area=current_chat
        edit_area.click_input()
        return edit_area,main_window
    else:
        message_list=message_list_pane.children(control_type='ListItem')
        if len(message_list)==0:
            return None,main_window
        if not scrollable:
            friend_button,index=selecte_in_messageList(friend)
            if friend_button:
                if index:
                    rec=friend_button.rectangle()
                    mouse.click(coords=(int(rec.left+rec.right)//2,rec.top-12))
                    edit_area=main_window.child_window(title=friend,control_type='Edit')
                else:
                    friend_button.click_input()
                    edit_area=main_window.child_window(title=friend,control_type='Edit')
                return edit_area,main_window
            else:
                return None,main_window
        if scrollable:
            rectangle=message_list_pane.rectangle()
            message_list_pane.iface_scroll.SetScrollPercent(verticalPercent=0.0,horizontalPercent=1.0)#调用SetScrollPercent方法向上滚动,verticalPercent=0.0表示直接将scrollbar一下子置于顶部
            mouse.click(coords=activateScollbarPosition)
            for _ in range(search_pages):
                friend_button,index=selecte_in_messageList(friend)
                if friend_button:
                    if index:
                        rec=friend_button.rectangle()
                        mouse.click(coords=(int(rec.left+rec.right)//2,rec.top-12))
                        edit_area=main_window.child_window(title=friend,control_type='Edit')
                    else:
                        friend_button.click_input()
                        edit_area=main_window.child_window(title=friend,control_type='Edit')
                    break
                else:
                    pyautogui.press("pagedown",_pause=False)
                    time.sleep(0.5)
            mouse.click(coords=activateScollbarPosition)
            pyautogui.press('Home')
            edit_area=main_window.child_window(title=friend,control_type='Edit')
            if edit_area.exists():
                return edit_area,main_window
            else:
                return None,main_window

def open_dialog_window(friend:str,wechat_path:str=None,is_maximize:bool=True,search_pages:int=5)->tuple[WindowSpecification,WindowSpecification]:
    '''
    该函数用于打开某个好友(非公众号)的聊天窗口
    Args:
        friend:好友或群聊备注名称,需提供完整名称
        independent:是否单独打开为独立窗口(双击会话列表内好友ListItem)
        wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
        is_maximize:微信界面是否全屏,默认全屏。
        search_pages:在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
    Returns:
        (edit_area,main_window):editarea:主界面右侧下方与好友的消息编辑区域,main_window:微信主界面
    '''
    def get_searh_result(friend,search_result):#查看搜索列表里有没有名为friend的listitem
        listitem=search_result.children(control_type="ListItem")
        #descendants带有按钮能够排除掉非好友的其他搜索结果
        contacts=[item for item in listitem if item.descendants(control_type='Button')]
        names=[re.sub(r'[\u2002\u2004\u2005\u2006\u2009]',' ',item.window_text()) for item in contacts]
        if friend in names:#如果在的话就返回整个搜索到的所有联系人,以及其所处的index
            location=names.index(friend)
            return contacts[location]
        return None
    #如果search_pages不为0,即需要在会话列表中滚动查找时，使用find_friend_in_Messagelist方法找到好友,并点击打开对话框
    if search_pages:
        edit_area,main_window=Tools.find_friend_in_MessageList(friend=friend,wechat_path=wechat_path,is_maximize=is_maximize,search_pages=search_pages)
        chat_button=main_window.child_window(**SideBar.Chats)
        if edit_area:#edit_area不为None,即说明find_friend_in_MessageList找到了聊天窗口,直接返回结果
            return edit_area,main_window
        #edit_area为None没有在会话列表中找到好友,直接在顶部搜索栏中搜索好友
        #先点击侧边栏的聊天按钮切回到聊天主界面
        #顶部搜索按钮搜索好友
        search=main_window.child_window(**Main_window.Search).wait(wait_for='visible',retry_interval=0.1,timeout=3)
        search.click_input()
        Systemsettings.copy_text_to_windowsclipboard(friend)
        pyautogui.hotkey('ctrl','v')
        search_results=main_window.child_window(**Main_window.SearchResult)
        time.sleep(1)
        friend_button=get_searh_result(friend=friend,search_result=search_results)
        if friend_button:
            friend_button.click_input()
            edit_area=main_window.child_window(title=friend,control_type='Edit')
            return edit_area,main_window #同时返回搜索到的该好友的聊天窗口与主界面！若只需要其中一个需要使用元祖索引获取。
        else:#搜索结果栏中没有关于传入参数friend好友昵称或备注的搜索结果，关闭主界面,引发NosuchFriend异常
            chat_button.click_input()
            main_window.close()
            raise NoSuchFriendError
    else: #searchpages为0，不在会话列表查找
        desktop=Desktop(**Independent_window.Desktop)
        #这部分代码先判断微信主界面是否可见,如果可见不需要重新打开,这在多个close_wechat为False需要进行来连续操作的方式使用时要用到
        main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=is_maximize)
        chat_button=main_window.child_window(**SideBar.Chats)
        message_list=main_window.child_window(**Main_window.ConversationList)
        #先看看当前聊天界面是不是好友的聊天界面
        current_chat=main_window.child_window(**Main_window.CurrentChatWindow)
        #如果当前主界面是某个好友的聊天界面且聊天界面顶部的名称为好友名称，直接返回结果
        if current_chat.exists() and friend==current_chat.window_text():
            edit_area=current_chat
            edit_area.click_input()
            return edit_area,main_window
        else:#否则直接从顶部搜索栏出搜索结果
            #如果会话列表不存在或者不可见的话才点击一下聊天按钮
            if not message_list.exists():
                chat_button.click_input()
            if not message_list.is_visible():
                chat_button.click_input()
            search=main_window.child_window(**Main_window.Search)
            search.click_input()
            Systemsettings.copy_text_to_windowsclipboard(friend)
            pyautogui.hotkey('ctrl','v')
            search_results=main_window.child_window(**Main_window.SearchResult)
            time.sleep(1)
            friend_button=get_searh_result(friend=friend,search_result=search_results)
            if friend_button:
                friend_button.click_input()
                edit_area=main_window.child_window(title=friend,control_type='Edit')
                return edit_area,main_window #同时返回搜索到的该好友的聊天窗口与主界面！若只需要其中一个需要使用元祖索引获取。
            else:#搜索结果栏中没有关于传入参数friend好友昵称或备注的搜索结果，关闭主界面,引发NosuchFriend异常
                chat_button.click_input()
                main_window.close()
                raise NoSuchFriendError

def open_settings(wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True)->tuple[WindowSpecification,WindowSpecification|None]:
    '''
    该函数用来打开微信设置界面。
    Args:
        wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
        is_maximize:微信界面是否全屏,默认全屏。
        close_wechat:任务结束后是否关闭微信,默认关闭
    Returns:
        (settings_window,main_window):settings_window:设置界面窗口
        main_window:微信主界面,当close_wechat设置为True时,main_window为None
    '''
    main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=is_maximize)
    if Tools.judge_independant_window_state(window=Independent_window.SettingWindow)!=-1:
        handle=win32gui.FindWindow(Independent_window.SettingWindow['class_name'],Independent_window.SettingWindow['title'])
        win32gui.ShowWindow(handle,win32con.SW_SHOWNORMAL)
    else:
        setting=main_window.child_window(**SideBar.SettingsAndOthers)
        setting.click_input()
        settings_menu=main_window.child_window(**Main_window.SettingsMenu)
        settings_button=settings_menu.child_window(**Buttons.SettingsButton)
        settings_button.click_input()
    if close_wechat:
        main_window.close()
        main_window=None
    settings_window=Tools.move_window_to_center(Independent_window.SettingWindow)
    return settings_window,main_window

def judge_independant_window_state(window:dict)->int:
    '''该函数用来判断微信内独立于微信主界面的窗口的状态
    Args:
        window:pywinauto定位控件时的kwargs字典,可以在Uielements模块中找到
    Returns:
        state:取值(-1,0,1)
        -1表示界面未打开,需要从微信内打开
        0表示界面最小化
        1表示界面可见(不一定置顶!)
    '''
    state=-1
    handle=win32gui.FindWindow(window.get('class_name'),None)
    if win32gui.IsIconic(handle):
        state=0
    if win32gui.IsWindowVisible(handle):
        state=1
    return state

def open_moments(wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True)->tuple[WindowSpecification,WindowSpecification|None]:
    '''
    该函数用于打开微信朋友圈
    Args:
        wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
        is_maximize:微信界面是否全屏,默认全屏。
        close_wechat:任务结束后是否关闭微信,默认关闭
    Returns:
        (moments_window,main_window):moments_window:朋友圈主界面
        main_window:微信主界面,当close_wechat设置为True时,main_window为None
    '''
    main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=is_maximize)
    moments_button=main_window.child_window(**SideBar.Moments)
    moments_button.click_input()
    moments_window=Tools.move_window_to_center(Independent_window.MomentsWindow)
    moments_window.child_window(**Buttons.RefreshButton).click_input()
    if close_wechat:
        main_window.close()
        main_window=None
    return moments_window,main_window

def open_wechat_miniprogram(name:str,load_delay:float=2.5,wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True)->tuple[WindowSpecification,WindowSpecification|None]:
    '''
    该函数用于打开指定小程序
    Args:
        name:微信小程序名字
        load_delay:搜索小程序名称后等待时长,默认为2.5秒
        wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
        is_maximize:微信界面是否全屏,默认全屏。
        close_wechat:任务结束后是否关闭微信,默认关闭
    Returns:
        (program_window,main_window):program_window:小程序主界面
        main_window:微信主界面,当close_wechat设置为True时,main_window为None
    '''
    desktop=Desktop(**Independent_window.Desktop)
    program_window,main_window=Tools.open_program_pane(wechat_path=wechat_path,is_maximize=is_maximize,close_wechat=close_wechat)
    miniprogram_tab=program_window.child_window(title='小程序',control_type='TabItem')
    miniprogram_tab.click_input()
    time.sleep(load_delay)
    try:
        more=program_window.child_window(title='更多',control_type='Text',found_index=0)#小程序面板内的更多文本
    except Exception:
        program_window.close()
        print('网络不良,请尝试增加load_delay时长,或更换网络')
    rec=more.rectangle()
    mouse.click(coords=(rec.right+20,rec.top-50))
    up=5
    search=program_window.child_window(control_type='Edit',title='搜索小程序')
    while not search.exists():
        mouse.click(coords=(rec.right+20,rec.top-50-up))
        search=program_window.child_window(control_type='Edit',title='搜索小程序')
        up+=5
    search.click_input()
    Systemsettings.copy_text_to_windowsclipboard(name)
    pyautogui.hotkey('ctrl','v',_pause=False)
    pyautogui.press("enter")
    time.sleep(load_delay)
    try:
        search_result=program_window.child_window(control_type="Document",class_name="Chrome_RenderWidgetHostHWND")
        text=search_result.child_window(title=name,control_type='Text',found_index=0)
        text.click_input()
        program_window.close()
        program=desktop.window(control_type='Pane',title_re=name)
        return program,main_window
    except Exception:
        program_window.close()
        raise NoResultsError('查无此小程序!')

def open_official_account(name:str,load_delay:float=1,wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True)->tuple[WindowSpecification,WindowSpecification|None]:
    '''
    该函数用于打开指定的微信公众号
    Args:
        name:微信公众号名称
        load_delay:加载搜索公众号结果的时间,单位:s
        wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
        is_maximize:微信界面是否全屏,默认全屏。
    Returns:
        (chat_window,main_window):chat_window:与公众号的聊天界面
        main_window:微信主界面,当close_wechat设置为True时返回值为None
    '''
    desktop=Desktop(**Independent_window.Desktop)
    try:
        search_window,main_window=Tools.open_search(wechat_path=wechat_path,is_maximize=is_maximize,close_wechat=close_wechat)
        time.sleep(load_delay)
    except ElementNotFoundError:
        search_window.close()
        print('网络不良,请尝试增加load_delay时长,或更换网络')
    try:
        official_acount_button=search_window.child_window(**Buttons.OfficialAcountButton)
        official_acount_button.click_input()
    except ElementNotFoundError:
        search_window.close()
        print('网络不良,请尝试增加load_delay时长,或更换网络')
    search=search_window.child_window(control_type='Edit',found_index=0)
    search.click_input()
    Systemsettings.copy_text_to_windowsclipboard(name)
    pyautogui.hotkey('ctrl','v')
    pyautogui.press('enter')
    time.sleep(load_delay)
    try:
        search_result=search_window.child_window(control_type="Button",found_index=1,framework_id="Chrome")
        search_result.click_input()
        official_acount_window=Tools.move_window_to_center(Independent_window.OfficialAccountWindow)
        search_window.close()
        subscribe_button=official_acount_window.child_window(**Buttons.SubscribeButton)
        if subscribe_button.exists():
            subscribe_button.click_input()
            time.sleep(2)
        send_message_text=official_acount_window.child_window(**Texts.SendMessageText)
        send_message_text.click_input()
        chat_window=desktop.window(**Independent_window.OfficialAccountChatWindow)
        chat_window.maximize()
        official_acount_window.close()
        return chat_window,main_window
    except ElementNotFoundError:
        search_window.close()
        raise NoResultsError('查无此公众号!')

def open_contacts(wechat_path:str=None,is_maximize:bool=True)->WindowSpecification:
    '''
    该函数用于打开微信通信录界面
    Args:
        friend:好友或群聊备注名称,需提供完整名称
        wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
        is_maximize:微信界面是否全屏,默认全屏。
    Returns:
        main_window:微信主界面
    '''
    main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=is_maximize)
    contacts=main_window.child_window(**SideBar.Contacts)
    contacts.set_focus()
    contacts.click_input()
    cancel_button=main_window.child_window(**Buttons.CancelButton)
    if cancel_button.exists():
        cancel_button.click_input()
    ContactsLists=main_window.child_window(**Main_window.ContactsList)
    rec=ContactsLists.rectangle()
    mouse.click(coords=(rec.right-5,rec.top))
    pyautogui.press('Home')
    pyautogui.press('pageup')
    return main_window

def open_friend_settings(friend:str,wechat_path:str=None,is_maximize:bool=True,search_pages:int=5):
    '''
    该函数用于打开好友右侧的设置界面
    Args:
        friend:好友备注名称,需提供完整名称
        wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
        is_maximize:微信界面是否全屏,默认全屏。
        search_pages:在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
    Returns:
        (friend_settings_window,main_window):friend_settings_window:好友右侧的设置界面
        main_window:微信主界面
    '''
    editarea,main_window=Tools.open_dialog_window(friend=friend,wechat_path=wechat_path,is_maximize=is_maximize,search_pages=search_pages)
    try:
        ChatMessage=main_window.child_window(**Buttons.ChatMessageButton)
        ChatMessage.click_input()
        friend_settings_window=main_window.child_window(**Main_window.FriendSettingsWindow)
    except ElementNotFoundError:
        main_window.close()
        raise NotFriendError(f'非正常好友,无法打开设置界面！')
    return friend_settings_window,main_window

def open_friend_settings_menu(friend:str,wechat_path:str=None,is_maximize:bool=True,search_pages:int=5)->tuple[WindowSpecification,WindowSpecification,WindowSpecification]:
    '''
    该函数用于打开好友设置菜单
    Args:
        friend:好友备注名称,需提供完整名称
        wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
        is_maximize:微信界面是否全屏,默认全屏。
        search_pages:在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
    Returns:
        (friend_menu,friend_settings_window,main_window):friend_menu:在friend_settings_window界面里点击好友头像弹出的菜单
        friend_settings_window:好友右侧的设置界面
        main_window:微信主界面
    '''
    friend_settings_window,main_window=Tools.open_friend_settings(friend=friend,wechat_path=wechat_path,is_maximize=is_maximize,search_pages=search_pages)
    friend_button=friend_settings_window.child_window(title=friend,control_type="Button",found_index=0)
    friend_button.click_input()
    profile_window=friend_settings_window.child_window(**Panes.FriendProfilePane)
    more_button=profile_window.child_window(**Buttons.MoreButton)
    more_button.click_input()
    friend_menu=profile_window.child_window(**Menus.FriendProfileMenu)
    return friend_menu,friend_settings_window,main_window

def open_collections(wechat_path:str=None,is_maximize:bool=True)->WindowSpecification:
    '''
    该函数用于打开收藏界面
    Args:
        wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
        is_maximize:微信界面是否全屏,默认全屏。
    Returns:
        main_window:微信主界面
    '''
    main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=is_maximize)
    collections_button=main_window.child_window(**SideBar.Collections)
    collections_button.click_input()
    return main_window

def open_group_settings(group_name:str,wechat_path:str=None,is_maximize:bool=True,search_pages:int=5)->tuple[WindowSpecification,WindowSpecification]:
    '''
    该函数用来打开群聊设置界面
    Args:
        group_name:群聊备注名称,需提供完整名称
        wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
        is_maximize:微信界面是否全屏,默认全屏。
        search_pages:在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
    Returns:
        (group_settings_window,main_window):group_sttings_window:群聊设置界面
        main_window:微信主界面
    '''
    main_window=Tools.open_dialog_window(friend=group_name,wechat_path=wechat_path,is_maximize=is_maximize,search_pages=search_pages)[1]
    ChatMessage=main_window.child_window(**Buttons.ChatMessageButton)
    ChatMessage.click_input()
    group_settings_window=main_window.child_window(**Main_window.GroupSettingsWindow)
    group_settings_window.child_window(**Texts.GroupNameText).click_input()
    return group_settings_window,main_window

def open_chatfiles(wechat_path:str=None,wechat_maximize:bool=True,is_maximize:bool=True,close_wechat:bool=True)->tuple[WindowSpecification,WindowSpecification|None]:
    '''
    该函数用于打开聊天文件界面
    Args:
        wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
        wechat_maximize:微信界面是否全屏,默认全屏
        is_maximize:聊天文件界面是否全屏,默认全屏。
        close_wechat:任务结束后是否关闭微信,默认关闭
    Returns:
        (filelist_window,main_window):filelist_window:聊天文件界面
        main_window:微信主界面,当close_wechat设置为True时main_window为None
    '''
    main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=wechat_maximize)
    moments_button=main_window.child_window(**SideBar.ChatFiles)
    moments_button.click_input()
    desktop=Desktop(**Independent_window.Desktop)
    filelist_window=desktop.window(**Independent_window.ChatFilesWindow)
    if is_maximize:
        filelist_window.maximize()
    if close_wechat:
        main_window.close()
        main_window=None
    return filelist_window,main_window

def open_friend_profile(friend:str,wechat_path:str=None,is_maximize:bool=True)->tuple[WindowSpecification,WindowSpecification]:
    '''
    该函数用于打开好友个人简介界面
    Args:
        friend:好友备注名称,需提供完整名称
        wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
        is_maximize:信界面是否全屏,默认全屏。
        search_pages:在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
    Returns:
        (profile_window,main_window):profile_window:好友设置界面内点击好友头像后的好友个人简介界面
        main_window:微信主界面
    '''
    friend_settings_window,main_window=Tools.open_friend_settings(friend=friend,wechat_path=wechat_path,is_maximize=is_maximize)
    friend_button=friend_settings_window.child_window(title=friend,control_type="Button",found_index=0)
    friend_button.click_input()
    profile_window=friend_settings_window.child_window(**Panes.FriendProfilePane)
    return profile_window,main_window

def open_program_pane(wechat_path:str=None,is_maximize:bool=True,wechat_maximize:bool=True,close_wechat:bool=True)->WindowSpecification:
    '''
    该函数用来打开小程序面板
    Args:
        wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
        is_maximize:小程序面板界面是否全屏,默认全屏。
        wechat_maximize:微信主界面是否全屏,默认全屏
        close_wechat:任务结束后是否关闭微信,默认关闭
    Returns:
        program_window:小程序面板
    '''
    main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=wechat_maximize)
    program_button=main_window.child_window(**SideBar.Miniprogram_pane)
    program_button.click_input()
    if close_wechat:
        main_window.close()
    program_window=Tools.move_window_to_center(Independent_window.MiniProgramWindow)
    if is_maximize:
        program_window.maximize()
    return program_window

def open_top_stories(wechat_path:str=None,is_maximize:bool=True,wechat_maximize:bool=True,close_wechat:bool=True)->tuple[WindowSpecification,WindowSpecification|None]:
    '''
    该函数用于打开看一看
    Args:
        wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
        is_maximize:看一看界面是否全屏,默认全屏。
        wechat_maximize:微信主界面是否全屏,默认全屏
        close_wechat:任务结束后是否关闭微信,默认关闭
    Returns:
        (top_stories_window,main_window):topstories_window:看一看主界面
        main_window:微信主界面,当close_wechat设置为True时,main_window为None
    '''
    main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=wechat_maximize)
    top_stories_button=main_window.child_window(**SideBar.Topstories)
    top_stories_button.click_input()
    top_stories_window=Tools.move_window_to_center(Independent_window.TopStoriesWindow)
    reload_button=top_stories_window.child_window(**Buttons.ReloadButton)
    reload_button.click_input()
    if is_maximize:
        top_stories_window.maximize()
    if close_wechat:
        main_window.close()
        main_window=None
    return top_stories_window,main_window

def open_search(wechat_path:str=None,is_maximize:bool=True,wechat_maximize:bool=True,close_wechat:bool=True)->tuple[WindowSpecification,WindowSpecification|None]:
    '''
    该函数用于打开搜一搜
    Args:
        wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
        is_maximize:搜一搜界面是否全屏,默认全屏。
        wechat_maximize:微信主界面是否全屏,默认全屏
        close_wechat:任务结束后是否关闭微信,默认关闭
    Returns:
        (search_window,main_window):search_window:搜一搜界面
        main_window:微信主界面,当close_wechat设置为True时,main_window为None
    '''
    main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=wechat_maximize)
    search_button=main_window.child_window(**SideBar.Search)
    search_button.click_input()
    search_window=Tools.move_window_to_center(Independent_window.SearchWindow)
    if is_maximize:
        search_window.maximize()
    if close_wechat:
        main_window.close()
        main_window=None
    return search_window,main_window

def open_channels(wechat_path:str=None,is_maximize:bool=True,wechat_maximize:bool=True,close_wechat:bool=True)->tuple[WindowSpecification,WindowSpecification|None]:
    '''
    该函数用于打开视频号
    Args:
        wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
        is_maximize:视频号界面是否全屏,默认全屏。
        wechat_maximize:微信主界面是否全屏,默认全屏
        close_wechat:任务结束后是否关闭微信,默认关闭
    Returns:
        (channel_window,main_window):channel_window:视频号窗口
        main_window:微信主界面,当close_wechat设置为True时返回None
    '''
    main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=wechat_maximize)
    channel_button=main_window.child_window(**SideBar.Channel)
    channel_button.click_input()
    desktop=Desktop(**Independent_window.Desktop)
    channel_window=desktop.window(**Independent_window.ChannelWindow)
    if is_maximize:
        channel_window.maximize()
    if close_wechat:
        main_window.close()
        main_window=None
    return channel_window,main_window

def open_payment_ledger(wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True)->tuple[WindowSpecification,WindowSpecification]:
    '''
    该函数用于打开微信收款助手的小账本界面
    Args:
        wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
        is_maximize:视频号界面是否全屏,默认全屏。
        wechat_maximize:微信主界面是否全屏,默认全屏
        close_wechat:任务结束后是否关闭微信,默认关闭
    Returns:
        (ledger_window,main_window):微信收款助手的小账本界面
        main_window:微信主界面,当close_wechat设置为True时返回None
    '''
    main_window=Tools.open_dialog_window(friend='微信收款助手',wechat_path=wechat_path,is_maximize=is_maximize,search_pages=0)[1]
    main_window.child_window(**Buttons.LedgerButton).click_input()
    menu=main_window.child_window(**Menus.RightClickMenu)
    menu.child_window(**MenuItems.EnterLedgerMenuItem).click_input()
    ledger_window=Tools.move_window_to_center(Window=Independent_window.ReceiptLedgerWindow)
    if close_wechat:
        main_window.close()
        main_window=None
    return ledger_window,main_window

def open_payment_code_window(wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True,close_ledger:bool=True)->tuple[WindowSpecification,WindowSpecification]:
    '''
    该函数用于打开微信收款助手小账本界面内的个人收款码
    Args:
        wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
        is_maximize:视频号界面是否全屏,默认全屏。
        wechat_maximize:微信主界面是否全屏,默认全屏
        close_wechat:任务结束后是否关闭微信,默认关闭
        close_ledger:任务结束后是否关闭微信收款助手小账本，默认关闭
    Returns:
        (payment_code_window,main_window):微信收款助手的小账本界面
        main_window:微信主界面,当close_wechat设置为True时返回None
    '''
    ledger_window,main_window=Tools.open_payment_ledger(wechat_path=wechat_path,is_maximize=is_maximize,close_wechat=close_wechat)
    paymentcode=ledger_window.child_window(**Buttons.PaymentCodeButton).wait(wait_for='visible')
    paymentcode.double_click_input()
    payment_code_window=Tools.move_window_to_center(Window=Independent_window.PaymentCodeWindow)
    if close_ledger:
        ledger_window.close()
    return payment_code_window,main_window

def find_wechat_path(copy_to_clipboard:bool=True):
    '''该函数用来查找微信的路径,无论微信是否运行都可以查找到
        copy_to_clipboard:是否将微信路径复制到剪贴板
    '''
    if is_wechat_running():
        wmi=win32com.client.GetObject('winmgmts:')
        processes=wmi.InstancesOf('Win32_Process')
        for process in processes:
            if process.Name.lower() == 'WeChat.exe'.lower():
                exe_path=process.ExecutablePath
                if exe_path:
                    # 规范化路径并检查文件是否存在
                    exe_path=os.path.abspath(exe_path)
                    wechat_path=exe_path
        if copy_to_clipboard:
            Systemsettings.copy_text_to_windowsclipboard(wechat_path)
            print("已将微信程序路径复制到剪贴板")
        return wechat_path
    else:
        #windows环境变量中查找WeChat.exe路径
        wechat_environ_path=[path for path in dict(os.environ).values() if 'WeChat.exe' in path]#
        if wechat_environ_path:
            if copy_to_clipboard:
                Systemsettings.copy_text_to_windowsclipboard(wechat_environ_path[0])
                print("已将微信程序路径复制到剪贴板")
            return wechat_environ_path[0]
        if not wechat_environ_path:
            try:
                reg_path=r"Software\Tencent\WeChat"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                    Installdir=winreg.QueryValueEx(key,"InstallPath")[0]
                wechat_path=os.path.join(Installdir,'WeChat.exe')
                if copy_to_clipboard:
                    Systemsettings.copy_text_to_windowsclipboard(wechat_path)
                    print("已将微信程序路径复制到剪贴板")
                return wechat_path
            except FileNotFoundError:
                raise NotInstalledError

def set_wechat_as_environ_path()->None:
    '''该函数用来自动打开系统环境变量设置界面,将微信路径自动添加至其中'''
    counter=0
    retry_interval=30
    Systemsettings.set_english_input()
    os.environ.update({"__COMPAT_LAYER":"RUnAsInvoker"})
    subprocess.Popen(["SystemPropertiesAdvanced.exe"])
    systemwindow=win32gui.FindWindow(None,u'系统属性')
    while not systemwindow:
        time.sleep(0.2)
        counter+=1
        systemwindow==win32gui.FindWindow(None,u'系统属性')
        if counter>=retry_interval:
            break
    if win32gui.IsWindow(systemwindow):#将系统变量窗口置于桌面最前端
        win32gui.ShowWindow(systemwindow,win32con.SW_SHOW)
        win32gui.SetWindowPos(systemwindow,win32con.HWND_TOPMOST,0,0,0,0,win32con.SWP_NOMOVE|win32con.SWP_NOSIZE)
    pyautogui.hotkey('alt','n',interval=0.5)#添加管理员权限后使用一系列快捷键来填写微信刻路径为环境变量
    pyautogui.hotkey('alt','n',interval=0.5)
    pyautogui.press('shift')
    pyautogui.typewrite('wechatpath')
    try:
        Tools.find_wechat_path()
        pyautogui.hotkey('Tab',interval=0.5)
        pyautogui.hotkey('ctrl','v')
        pyautogui.press('enter')
        pyautogui.press('enter')
        pyautogui.press('esc')
    except Exception:
        pyautogui.press('esc')
        pyautogui.hotkey('alt','f4')
        pyautogui.hotkey('alt','f4')
        raise NotInstalledError

def judge_wechat_state()->int:
    '''该函数用来判断微信运行状态
    Returns:
        state:取值(-1,0,1,2)
    -1:微信未启动
    0:主界面不可见
    1:主界面最小化
    2:主界面可见(不一定置顶!)
    '''
    state=-1
    if Tools.is_wechat_running():
        window=win32gui.FindWindow(Main_window.MainWindow['class_name'],Main_window.MainWindow['title'])
        if win32gui.IsIconic(window):
            state=1
        elif win32gui.IsWindowVisible(window):
            state=2
        else:
            state=0
    return state

def move_window_to_center(Window:dict=Main_window.MainWindow,handle:int=0)->WindowSpecification:
    '''该函数用来将已打开的界面置顶并移动到屏幕中央并返回该窗口的Windowspecification实例\n
    可以直接传入窗口句柄或pywinauto定位控件时的kwargs参数字典
    Args:
        Window:pywinauto定位控件的kwargs参数字典
        handle:窗口句柄
    Returns:
        window:WindowSpecification对象
    '''
    counter=0
    retry_interval=40
    desktop=Desktop(**Independent_window.Desktop)
    class_name=Window['class_name'] if 'class_name' in Window else None
    title=Window['title'] if 'title' in Window else None
    if not class_name:
        raise WrongParameterError(f'参数错误!kwargs参数字典中必须包含class_name')
    if handle==0:
        handle=win32gui.FindWindow(class_name,title)
    while not handle:
        time.sleep(0.1)
        counter+=1
        handle=win32gui.FindWindow(class_name,title)
        if counter>=retry_interval:
            break
    screen_width,screen_height=win32api.GetSystemMetrics(win32con.SM_CXSCREEN),win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
    window=desktop.window(handle=handle)
    window_width,window_height=window.rectangle().width(),window.rectangle().height()
    new_left=(screen_width-window_width)//2
    new_top=(screen_height-window_height)//2
    win32gui.SetWindowPos(
        handle,
        win32con.HWND_TOPMOST,
        0, 0, 0, 0,
        win32con.SWP_NOMOVE |
        win32con.SWP_NOSIZE |
        win32con.SWP_SHOWWINDOW
    )
    if screen_width!=window_width:
        win32gui.MoveWindow(handle, new_left, new_top, window_width, window_height, True)
    return window

def open_chat_history(friend:str,TabItem:str=None,search_pages:int=5,wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True)->tuple[WindowSpecification,WindowSpecification|None]:
    '''
    该函数用于打开好友聊天记录界面
    Args:
        friend:好友备注名称,需提供完整名称
        TabItem:点击聊天记录顶部的Tab选项,默认为None,可选值为:文件,图片与视频,链接,音乐与音频,小程序,视频号,日期
        search_pages:在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
        wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
        is_maximize:微信界面是否全屏,默认全屏。
        close_wechat:任务结束后是否关闭微信,默认关闭
    Returns:
        (chat_history_window,main_window):chat_history_window:好友设置界面内点击好友头像后的好友个人简介界面
        main_window:微信主界面,close_wechat设置为True时,main_window为None
    '''
    tabItems={'文件':TabItems.FileTabItem,'图片与视频':TabItems.PhotoAndVideoTabItem,'链接':TabItems.LinkTabItem,'音乐与音频':TabItems.MusicTabItem,'小程序':TabItems.MiniProgramTabItem,'视频号':TabItems.ChannelTabItem,'日期':TabItems.DateTabItem}
    if TabItem:
        if TabItem not in tabItems.keys():
            raise WrongParameterError('TabItem参数错误!')
    main_window=Tools.open_dialog_window(friend=friend,wechat_path=wechat_path,is_maximize=is_maximize,search_pages=search_pages)[1]
    chat_toolbar=main_window.child_window(**Main_window.ChatToolBar)
    chat_history_button=chat_toolbar.child_window(**Buttons.ChatHistoryButton)
    if not chat_history_button.exists():
        #公众号没有聊天记录这个按钮
        main_window.close()
        raise NotFriendError(f'非正常好友!无法打开聊天记录界面')
    chat_history_button.click_input()
    chat_history_window=Tools.move_window_to_center(Independent_window.ChatHistoryWindow)
    if TabItem:
        if TabItem=='视频号' or TabItem=='日期':
            chat_history_window.child_window(control_type='Button',title='').click_input()
        chat_history_window.child_window(**tabItems[TabItem]).click_input()
    if close_wechat:
        main_window.close()
        main_window=None
    return chat_history_window,main_window

def search_channels(search_content:str,load_delay:float=1,wechat_path:str=None,wechat_maximize:bool=True,is_maximize:bool=True,close_wechat:bool=True)->tuple[WindowSpecification,WindowSpecification|None]:
    '''
    该函数用于打开视频号并搜索指定内容
    Args:
        search_content:在视频号内待搜索内容
        load_delay:加载查询结果的时间,单位:s
        wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
        is_maximize:微信界面是否全屏,默认全屏。
    Returns:
        (chat_history_window,main_window):chat_history_window:好友设置界面内点击好友头像后的好友个人简介界面
        main_window:微信主界面,close_wechat设置为True时,main_window为None
    '''
    Systemsettings.copy_text_to_windowsclipboard(search_content)
    channel_widow,main_window=Tools.open_channels(wechat_maximize=wechat_maximize,is_maximize=is_maximize,wechat_path=wechat_path,close_wechat=close_wechat)
    search_bar=channel_widow.child_window(control_type='Edit',title='搜索',framework_id='Chrome')
    while not search_bar.exists():
        time.sleep(0.1)
        search_bar=channel_widow.child_window(control_type='Edit',title='搜索',framework_id='Chrome')
    search_bar.click_input()
    pyautogui.hotkey('ctrl','a')
    pyautogui.press('backspace')
    pyautogui.hotkey('ctrl','v')
    pyautogui.press('enter')
    time.sleep(load_delay)
    try:
        search_result=channel_widow.child_window(control_type='Document',title=f'{search_content}_搜索')
        return channel_widow,main_window
    except ElementNotFoundError:
        channel_widow.close()
        print('网络不良,请尝试增加load_delay时长,或更换网络')

def open_contacts_manage(wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True)->tuple[WindowSpecification,WindowSpecification|None]:
    '''
    该函数用于打开通讯录管理界面
    Args:
        wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
        is_maximize:微信界面是否全屏,默认全屏。
        close_wechat:任务结束后是否关闭微信,默认关闭
    Returns:
        (contacts_manage_window,main_window):contacts_manage_window:通讯录管理界面
        main_window:微信主界面,当close_wechat设置为True时返回None
    '''
    main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=is_maximize)
    contacts=main_window.child_window(**SideBar.Contacts)
    contacts.click_input()
    cancel_button=main_window.child_window(**Buttons.CancelButton)
    if cancel_button.exists():
        cancel_button.click_input()
    ContactsLists=main_window.child_window(**Main_window.ContactsList)
    ################
    rec=ContactsLists.rectangle()
    mouse.click(coords=(rec.right-5,rec.top))
    pyautogui.press('Home')
    pyautogui.press('pageup')
    contacts_manage=main_window.child_window(**Buttons.ContactsManageButton)#通讯录管理窗口按钮
    contacts_manage.click_input()
    #################
    contacts_manage_window=Tools.move_window_to_center(Window=Independent_window.ContactManagerWindow)
    if close_wechat:
        main_window.close()
    return contacts_manage_window,main_window

def parse_message_content(ListItem:ListItemWrapper,friendtype:str)->tuple[str,str,str]:
    '''
    该函数用来将主界面右侧聊天区域内的单个ListItem消息转换为文本,传入对象为Listitem
    Args:
        ListItem:主界面右侧聊天区域内ListItem形式的消息
        friendtype:聊天区域是群聊还是好友
    Returns:
        message_sender:发送消息的对象
        message_content:发送的消息
        message_type:消息类型,具体类型:{'文本','图片','视频','语音','文件','动画表情','视频号','链接','聊天记录','引用消息','卡片链接','微信转账'}
    '''
    language=Tools.language_detector()
    message_content=''
    message_type=''
    #至于消息的内容那就需要仔细判断一下了
    #微信在链接的判定上比较模糊,音乐和链接最后统一都以卡片的形式在聊天记录中呈现,所以这里不区分音乐和链接,都以链接卡片的形式处理
    specialMegCN={'[图片]':'图片','[视频]':'视频','[动画表情]':'动画表情','[视频号]':'视频号','[链接]':'链接','[聊天记录]':'聊天记录'}
    specialMegEN={'[Photo]':'图片','[Video]':'视频','[Sticker]':'动画表情','[Channel]':'视频号','[Link]':'链接','[Chat History]':'聊天记录'}
    specialMegTC={'[圖片]':'图片','[影片]':'视频','[動態貼圖]':'动画表情','[影音號]':'视频号','[連結]':'链接','[聊天記錄]':'聊天记录'}
    #系统消息
    if len(ListItem.descendants(control_type='Button'))==0:
        message_sender='系统'
        message_content=ListItem.window_text()
        message_type='系统消息'
    else: #不同语言,处理非系统消息内容时不同
        AudioPattern=SpecialMessages.AudioPattern
        message_sender=ListItem.children()[0].children(control_type='Button')[0].window_text()
        if language=='简体中文':
            if ListItem.window_text() in specialMegCN.keys():#内容在特殊消息中
                message_sender=ListItem.children()[0].children(control_type='Button')[0].window_text()
                message_content=specialMegCN.get(ListItem.window_text())
                message_type=specialMegCN.get(ListItem.window_text())
            else:#文件,卡片链接,语音,以及正常的文本消息
                if re.match(AudioPattern,ListItem.window_text()):#匹配是否是语音消息
                    try:#是语音消息就定位语音转文字结果
                        if friendtype=='群聊':
                            audio_content=ListItem.descendants(control_type='Text')[2].window_text()
                            message_content=ListItem.window_text()+f'  消息内容:{audio_content}'
                            message_type='语音'
                        else:
                            audio_content=ListItem.descendants(control_type='Text')[1].window_text()
                            message_content=ListItem.window_text()+f'  消息内容:{audio_content}'
                            message_type='语音'
                    except Exception:#定位时不排除有人只发送[语音]5秒这样的文本消息，所以可能出现异常
                        message_content=ListItem.window_text()
                        message_type='文本'
                elif ListItem.window_text()=='[文件]':
                    filename=ListItem.descendants(control_type='Text')[0].window_text()
                    stem,extension=os.path.splitext(filename)
                    #文件这个属性的ListItem内有很多文本,正常来说文件名不是第一个就是第二个,这里哪一个有后缀名哪一个就是文件名
                    if not extension:
                        filename=ListItem.descendants(control_type='Text')[1].window_text()
                    message_content=f'{filename}'
                    message_type='文件'
                elif len(ListItem.descendants(control_type='Text'))>=3:#ListItem内部文本ui个数大于3一般是卡片链接或引用消息或聊天记录
                    cardContent=ListItem.descendants(control_type='Text')
                    cardContent=[link.window_text() for link in cardContent]
                    message_content='卡片链接内容:'+','.join(cardContent)
                    message_type='卡片链接'
                    if ListItem.window_text()=='微信转账':
                        index=cardContent.index('微信转账')
                        message_content=f'微信转账:{cardContent[index-2]}:{cardContent[index-1]}'
                        message_type='微信转账'
                    if "引用  的消息 :" in ListItem.window_text():
                        splitlines=ListItem.window_text().splitlines()
                        message_content=f'{splitlines[0]}引用消息内容:{splitlines[1:]}'
                        message_type='引用消息'
                    if '小程序' in cardContent:
                        message_content='小程序内容:'+','.join(cardContent)
                        message_type='小程序'
                else:#正常文本
                    message_content=ListItem.window_text()
                    message_type='文本'

        if language=='英文':
            if ListItem.window_text() in specialMegEN.keys():
                message_content=specialMegEN.get(ListItem.window_text())
                message_type=specialMegEN.get(ListItem.window_text())
            else:#文件,卡片链接,语音,以及正常的文本消息
                if re.match(AudioPattern,ListItem.window_text()):#匹配是否是语音消息
                    try:#是语音消息就定位语音转文字结果
                        if friendtype=='群聊':
                            audio_content=ListItem.descendants(control_type='Text')[2].window_text()
                            message_content=ListItem.window_text()+f'  消息内容:{audio_content}'
                            message_type='语音'
                        else:
                            audio_content=ListItem.descendants(control_type='Text')[1].window_text()
                            message_content=ListItem.window_text()+f'  消息内容:{audio_content}'
                            message_type='语音'
                    except Exception:#定位时不排除有人只发送[语音]5秒这样的文本消息，所以可能出现异常
                        message_content=ListItem.window_text()
                        message_type='文本'
                elif ListItem.window_text()=='[File]':
                    filename=ListItem.descendants(control_type='Text')[0].window_text()
                    stem,extension=os.path.splitext(filename)
                    #文件这个属性的ListItem内有很多文本,正常来说文件名不是第一个就是第二个,这里哪一个有后缀名哪一个就是文件名
                    if not extension:
                        filename=ListItem.descendants(control_type='Text')[1].window_text()
                    message_content=f'{filename}'
                    message_type='文件'

                elif len(ListItem.descendants(control_type='Text'))>=3:#ListItem内部文本ui个数大于3一般是卡片链接或引用消息或聊天记录
                    cardContent=ListItem.descendants(control_type='Text')
                    cardContent=[link.window_text() for link in cardContent]
                    message_content='卡片链接内容:'+','.join(cardContent)
                    message_type='卡片链接'
                    if ListItem.window_text()=='Weixin Transfer':
                        index=cardContent.index('Weixin Transfer')
                        message_content=f'微信转账:{cardContent[index-2]}:{cardContent[index-1]}'
                        message_type='微信转账'
                    if "Quote 's message:" in ListItem.window_text():
                        splitlines=ListItem.window_text().splitlines()
                        message_content=f'{splitlines[0]}引用消息内容:{splitlines[1:]}'
                        message_type='引用消息'
                    if 'Mini Programs' in cardContent:
                        message_content='小程序内容:'+','.join(cardContent)
                        message_type='小程序'

                else:#正常文本
                    message_content=ListItem.window_text()
                    message_type='文本'

        if language=='繁体中文':
            if ListItem.window_text() in specialMegTC.keys():
                message_sender=ListItem.children()[0].children(control_type='Button')[0].window_text()
                message_content=specialMegTC.get(ListItem.window_text())
                message_type=specialMegTC.get(ListItem.window_text())
            else:#文件,卡片链接,语音,以及正常的文本消息
                if re.match(AudioPattern,ListItem.window_text()):#匹配是否是语音消息
                    message_sender=ListItem.children()[0].children(control_type='Button')[0].window_text()
                    try:#是语音消息就定位语音转文字结果
                        if friendtype=='群聊':
                            audio_content=ListItem.descendants(control_type='Text')[2].window_text()
                            message_content=ListItem.window_text()+f'  消息内容:{audio_content}'
                            message_type='语音'
                        else:
                            audio_content=ListItem.descendants(control_type='Text')[1].window_text()
                            message_content=ListItem.window_text()+f'  消息内容:{audio_content}'
                            message_type='语音'
                    except Exception:#定位时不排除有人只发送[语音]5秒这样的文本消息，所以可能出现异常
                        message_content=ListItem.window_text()
                        message_type='文本'

                elif ListItem.window_text()=='[檔案]':
                    message_sender=ListItem.children()[0].children(control_type='Button')[0].window_text()
                    filename=ListItem.descendants(control_type='Text')[0].window_text()
                    stem,extension=os.path.splitext(filename)
                    #文件这个属性的ListItem内有很多文本,正常来说文件名不是第一个就是第二个,这里哪一个有后缀名哪一个就是文件名
                    if not extension:
                        filename=ListItem.descendants(control_type='Text')[1].window_text()
                    message_content=f'{filename}'
                    message_type='文件'

                elif len(ListItem.descendants(control_type='Text'))>=3:#ListItem内部文本ui个数大于3一般是卡片链接或引用消息或聊天记录
                    message_sender=ListItem.children()[0].children(control_type='Button')[0].window_text()
                    cardContent=ListItem.descendants(control_type='Text')
                    cardContent=[link.window_text() for link in cardContent]
                    message_content='卡片链接内容:'+','.join(cardContent)
                    message_type='卡片链接'
                    if ListItem.window_text()=='微信轉賬':
                        index=cardContent.index('微信轉賬')
                        message_content=f'微信转账:{cardContent[index-2]}:{cardContent[index-1]}'
                        message_type='微信转账'
                    if "引用  的訊息 :" in ListItem.window_text():
                        splitlines=ListItem.window_text().splitlines()
                        message_content=f'{splitlines[0]}引用消息内容:{splitlines[1:]}'
                        message_type='引用消息'
                    if '小程式' in cardContent:
                        message_content='小程序内容:'+','.join(cardContent)
                        message_type='小程序'

                elif len(ListItem.descendants(control_type='Button'))==0:
                    message_sender='系统'
                    message_content=ListItem.window_text()
                    message_type='系统消息'

                else:#正常文本
                    message_sender=ListItem.children()[0].children(control_type='Button')[0].window_text()
                    message_content=ListItem.window_text()
                    message_type='文本'

    return message_sender,message_content,message_type

def pull_messages(number:int,friend:str=None,chatWnd:WindowSpecification=None,parse:bool=True,chats_only:bool=True,search_pages:int=5,wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True)->list[dict]|list[ListItemWrapper]:
    '''
    该函数用来从主界面右侧的聊天区域或单独的聊天窗口内获取指定条数的聊天记录消息\n
    消息具体类型:{'文本','图片','视频','语音','文件','动画表情','视频号','链接','卡片链接','微信转账','系统消息'}
    Args:
        number:聊天记录条数
        friend:好友或群聊备注
        chatWnd:独立的好友聊天窗口
        parse:是否解析聊天记录为文本(主界面右侧聊天区域内的聊天记录形式为ListItem),设置为False时返回的类型为ListItem
        chats_only:是否只查找聊天消息不包含系统消息,设置为False时连同灰色的系统消息一起查找
        search_pages:在会话列表中查询查找好友时滚动列表的次数,默认为10,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏法搜索好友信息打开聊天界面
        wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
        is_maximize:微信主界面是否全屏,默认全屏。
        close_wechat:任务结束后是否关闭微信,默认关闭
    Returns:
        chats:[{'发送人':'','消息内容':'','消息类型':''}]*number\n
        list[ListItemWrapper]:聊天消息的ListItem形式

    '''
    chats=[]
    friendtype='好友'#默认是好友
    if chatWnd is not None:
        main_window=chatWnd
    if friend is None and chatWnd is None:
        raise ValueError('friend与ChatWnd至少要有一个!')
    if chatWnd is None and friend is not None:
        main_window=Tools.open_dialog_window(friend=friend,search_pages=search_pages,wechat_path=wechat_path,is_maximize=is_maximize)[1]
        chat_history_button=main_window.child_window(**Buttons.ChatHistoryButton)
        if not chat_history_button.exists():#没有聊天记录按钮是公众号或其他类型的东西
            raise NotFriendError(f'{friend}不是好友，无法获取聊天记录！')
    chatList=main_window.child_window(**Main_window.FriendChatList)#聊天区域内的消息列表
    scrollable=Tools.is_VerticalScrollable(chatList)
    viewMoreMesssageButton=main_window.child_window(**Buttons.CheckMoreMessagesButton)#查看更多消息按钮
    if len(chatList.children(control_type='ListItem'))==0:#没有聊天记录直接返回空列表
        return []
    video_call_button=main_window.child_window(**Buttons.VideoCallButton)
    if not video_call_button.exists():##没有视频聊天按钮是群聊
        friendtype='群聊'
    #if message.descendants(conrol_type)是用来筛选这个消息(control_type为ListItem)内有没有按钮(消息是人发的必然会有头像按钮这个UI,系统消息比如'8:55'没有这个UI)
    ListItems=[message for message in chatList.children(control_type='ListItem') if message.window_text()!=Buttons.CheckMoreMessagesButton['title']]#产看更多消息内部也有按钮,所以需要筛选一下
    if chats_only:
        ListItems=[message for message in ListItems if message.descendants(control_type='Button')]
    #点击聊天区域侧边栏和头像之间的位置来激活滑块,不直接main_window.click_input()是为了防止点到消息
    x,y=chatList.rectangle().left+8,(main_window.rectangle().top+main_window.rectangle().bottom)//2#
    if len(ListItems)>=number:#聊天区域内部不需要遍历就可以获取到的消息数量大于number条
        ListItems=ListItems[-number:]#返回从后向前数number条消息
    if len(ListItems)<number:#
        ##########################################################
        if scrollable:
            mouse.click(coords=(chatList.rectangle().right-10,chatList.rectangle().bottom-5))
            while len(ListItems)<number:
                chatList.iface_scroll.SetScrollPercent(verticalPercent=0.0,horizontalPercent=1.0)#调用SetScrollPercent方法向上滚动,verticalPercent=0.0表示直接将scrollbar一下子置于顶部
                mouse.scroll(coords=(x,y),wheel_dist=1000)
                ListItems=[message for message in chatList.children(control_type='ListItem') if message.window_text()!=Buttons.CheckMoreMessagesButton['title']]
                if chats_only:
                    ListItems=[message for message in ListItems if message.descendants(control_type='Button')]
                if not viewMoreMesssageButton.exists():#向上遍历时如果查看更多消息按钮不在存在说明已经到达最顶部,没有必要继续向上,直接退出循环
                    break
            ListItems=ListItems[-number:]
        else:#无法滚动,说明就这么多了,有可能是刚添加好友或群聊或者是清空了聊天记录,只发了几条消息
            ListItems=ListItems[-number:]
    #######################################################
    if close_wechat:
        main_window.close()
    if parse:
        for ListItem in ListItems:
            message_sender,message_content,message_type=Tools.parse_message_content(ListItem=ListItem,friendtype=friendtype)
            chats.append({'发送人':message_sender,'消息内容':message_content,'消息类型':message_type})
        return chats
    else:
        return ListItems


def match_duration(duration:str)->float:
    '''
    该函数用来将字符串类型的时间段转换为秒
    Args:
        duration:持续时间,格式为:'30s','1min','1h'
    '''
    if "s" in duration:
        try:
            duration=duration.replace('s','')
            duration=float(duration)
            return duration
        except Exception:
            return None
    elif 'min' in duration:
        try:
            duration=duration.replace('min','')
            duration=float(duration)*60
            return duration
        except Exception:
            return None
    elif 'h' in duration:
        try:
            duration=duration.replace('h','')
            duration=float(duration)*60*60
            return duration
        except Exception:
            return None
    else:
        return None

def is_VerticalScrollable(List:ListViewWrapper)->bool:
    '''
    该函数用来判断微信内的列表类型控件是否可以垂直滚动\n
    原理:微信内的停靠在List右侧的灰色scrollbar无Ui且还只渲染可见部分\n
    该函数通过判断List组件是否具有iface_scorll这个属性即可判断其\n
    是否具有scrollbar进而判断其是否scrollable
    Args:
        List:微信内control_type为List的列表
    Returns:
        scrollable:是否可以竖直滚动
    '''
    try:
        #如果能获取到这个属性,说明可以滚动
        List.iface_scroll.CurrentVerticallyScrollable
        scrollable=True
    except Exception:#否则会引发NoPatternInterfaceError,返回False
        scrollable=False
    return scrollable

def pull_latest_message(chatList:ListViewWrapper)->tuple[str,str]|tuple[None,None]:#获取聊天界面内的聊天记录
    '''
    该函数用来获取聊天界面内的最新的一条聊天消息(非时间戳或系统消息:以下是新消息)
    返回值为最新的消息内容以及消息发送人,需要注意的是如果界面内没有消息或最新消息是系统消息
    那么返回None,None,该方法可以用来配合自动回复方法使用
    Args:
        chatList:打开好友的聊天窗口后的右侧聊天列表,该函数主要用内嵌于自动回复消息功能中使用
            因此传入的参数为主界面右侧的聊天列表,也就是Main_window.FriendChatList

    Returns:
        (content,sender):消息发送人最新的新消息内容
    Examples:
        ```
        from pywechat import Tools,Main_window,pull_latest_message
        edit_area,main_window=Tools.open_dialog_window(friend='路人甲')
        content,sender=pull_latest_message(chatList=main_window.child_window(**Main_window.FriendChatList))
        print(content,sender)
        ```
    '''
    #筛选消息，每条消息都是一个listitem
    if chatList.exists():
        if chatList.children():#如果聊天列表存在(不存在的情况:清空了聊天记录)
            if chatList.children()[-1].descendants(control_type='Button') and chatList.children()[-1].window_text()!='':#必须是非系统消息也就是消息内部含有发送人按钮这个UI
                content=chatList.children()[-1].window_text()
                sender=chatList.children()[-1].descendants(control_type='Button')[0].window_text()
                return content,sender
    return None,None

def find_current_wxid()->str:
    '''
    该函数通过解析Accinfo.dat文件来检测当前登录的wxid,使用时必须登录微信,否则返回空字符串
    '''
    config=Tools.where_config_folder(open_folder=False)
    AccInfo=os.path.join(config,'AccInfo.dat')
    if os.path.exists(AccInfo):
        with open(AccInfo, 'rb') as f:
            bytes=f.read()
        wxid_start=bytes.find(b'wxid_')
        wxid_end=bytes.find(b'\x1a',wxid_start)
        wxid=bytes[wxid_start:wxid_end].decode()
        return wxid
    return ''

def where_database_folder(open_folder:bool=False):
    '''
    该函数用来获取微信数据库存放路径(文件夹)\n
    使用时微信必须登录,否则无法获取到完整路径
    Args:
        open_folder:是否打开微信数据库所在文件夹,默认不打开
    Returns:
        folder_path:数据库存放路径
    '''
    wechat_process=None
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name']=='WeChat.exe':
            wechat_process=process
            break
    #只要微信登录了,就一定会用到本地聊天文件保存位置:Wechat Files下的一个wxid开头的文件下的Msg,
    #这个文件夹里包含了聊天纪录数据等内容
    #wechat_process是进程句柄,通过这个进程句柄的memory_maps方法可以实现
    #内存映射文件检测
    folder_path=''
    for mem_map in wechat_process.memory_maps():
        if 'Msg'  in mem_map.path:
            folder_path=mem_map.path
            #获取到的路径的basename是含\Msg\xxx.db，我们只需要他的dir就可以然后把
            folder_path=os.path.dirname(folder_path)
            break
    if open_folder and os.path.exists(folder_path):
        os.startfile(folder_path)
    return folder_path

def where_chatfiles_folder(open_folder:bool=False):
    '''
    该函数用来获取微信聊天文件存放路径(文件夹)\n
    使用时微信必须登录,否则无法获取到完整路径
    Args:
        open_folder:是否打开存放聊天文件的文件夹,默认不打开
    Returns:
        folder_path:聊天文件存放路径
    '''
    wechat_process=None
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name']=='WeChat.exe':
            wechat_process=process
            break
    #只要微信登录了,就一定会用到本地聊天文件保存位置:Wechat Files下的一个wxid开头的文件下的Msg,
    #这个文件夹里包含了聊天纪录数据等内容
    #wechat_process是进程句柄,通过这个进程句柄的memory_maps方法可以实现
    #内存映射文件检测
    base_folder=''
    for mem_map in wechat_process.memory_maps():
        if 'Msg'  in mem_map.path:
            base_folder=mem_map.path
            #获取到的路径的basename是含\Msg\xxx.db，我们只需要他的dir就可以然后把Msg换为FileStorage
            base_folder=os.path.dirname(base_folder).replace('Msg','FileStorage')
            break
    folder_path=os.path.join(base_folder,'File')
    if open_folder and folder_path:
        os.startfile(folder_path)
    return folder_path

def where_videos_folder(open_folder:bool=False):
    '''
    该函数用来获取微信聊天视频存放路径(文件夹)\n
    使用时微信必须登录,否则无法获取到完整路径
    Args:
        open_folder:是否打开聊天视频存放路径,默认不打开
    Returns:
        folder_path:聊天视频存放路径
    '''
    wechat_process=None
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name']=='WeChat.exe':
            wechat_process=process
            break
    #只要微信登录了,就一定会用到本地聊天文件保存位置:Wechat Files下的一个wxid开头的文件下的Msg,
    #这个文件夹里包含了聊天纪录数据等内容
    #wechat_process是进程句柄,通过这个进程句柄的memory_maps方法可以实现
    #内存映射文件检测
    base_folder=''
    for mem_map in wechat_process.memory_maps():
        if 'Msg'  in mem_map.path:
            base_folder=mem_map.path
            #获取到的路径的basename是含\Msg\xxx.db，我们只需要他的dir就可以然后把Msg换为FileStorage
            base_folder=os.path.dirname(base_folder).replace('Msg','FileStorage')
            break
    folder_path=os.path.join(base_folder,'Video')
    if open_folder and folder_path:
        os.startfile(folder_path)

def NativeSaveFile(folder_path)->None:
    '''
    该函数用来处理微信内部点击另存为后弹出的windows本地保存文件窗口
    Args:
        folder_path:保存文件的文件夹路径
    '''
    desktop=Desktop(**Independent_window.Desktop)
    save_as_window=desktop.window(**Windows.NativeSaveFileWindow)
    prograss_bar=save_as_window.child_window(control_type='ProgressBar',class_name='msctls_progress32',framework_id='Win32')
    path_bar=prograss_bar.child_window(class_name='ToolbarWindow32',control_type='ToolBar',found_index=0)
    if re.search(r':\s*(.*)',path_bar.window_text().lower()).group(1)!=folder_path.lower():
        rec=path_bar.rectangle()
        mouse.click(coords=(rec.right-5,int(rec.top+rec.bottom)//2))
        pyautogui.press('backspace')
        pyautogui.hotkey('ctrl','v',_pause=False)
        pyautogui.press('enter')
        time.sleep(0.5)
    pyautogui.hotkey('alt','s')

def NativeChooseFolder(folder_path)->None:
    '''
    该方法用来处理微信内部点击选择文件夹后弹出的windows本地选择文件夹窗口
    Args:
        folder_path:保存文件的文件夹路径
    '''
    #如果path_bar上的内容与folder_path不一致,那么删除复制粘贴
    #如果一致,点击选择文件夹窗口
    Systemsettings.copy_text_to_windowsclipboard(folder_path)
    desktop=Desktop(**Independent_window.Desktop)
    save_as_window=desktop.window(**Windows.NativeChooseFolderWindow)
    prograss_bar=save_as_window.child_window(control_type='ProgressBar',class_name='msctls_progress32',framework_id='Win32')
    path_bar=prograss_bar.child_window(class_name='ToolbarWindow32',control_type='ToolBar',found_index=0)
    if re.search(r':\s*(.*)',path_bar.window_text()).group(1)!=folder_path:
        rec=path_bar.rectangle()
        mouse.click(coords=(rec.right-5,int(rec.top+rec.bottom)//2))
        pyautogui.press('backspace')
        pyautogui.hotkey('ctrl','v',_pause=False)
        pyautogui.press('enter')
        time.sleep(0.5)
    choose_folder_button=save_as_window.child_window(control_type='Button',title='选择文件夹')
    choose_folder_button.click_input()

def where_SnsCache_folder(open_folder:bool=False):
    '''
    该方法用来获取微信朋友圈图片视频缓存路径(文件夹)\n
    使用时微信必须登录,否则无法获取到完整路径
    Args:
        open_folder:是否打开朋友圈图片视频缓存路径,默认不打开
    Returns:
        folder_path:朋友圈图片视频缓存路径
    '''
    wechat_process=None
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name']=='WeChat.exe':
            wechat_process=process
            break
    #只要微信登录了,就一定会用到本地聊天文件保存位置:Wechat Files下的一个wxid开头的文件下的Msg,
    #这个文件夹里包含了聊天纪录数据等内容
    #wechat_process是进程句柄,通过这个进程句柄的memory_maps方法可以实现
    #内存映射文件检测
    base_folder=''
    for mem_map in wechat_process.memory_maps():
        if 'Msg'  in mem_map.path:
            base_folder=mem_map.path
            #获取到的路径的basename是含\Msg\xxx.db，我们只需要他的dir就可以然后把Msg换为FileStorage
            base_folder=os.path.dirname(base_folder).replace('Msg','FileStorage')
            break
    folder_path=os.path.join(base_folder,'Sns','Cache')
    if open_folder and os.path.exists(folder_path):
        os.startfile(folder_path)
    return folder_path


def is_wechat_installed():
    '''
    该方法通过查询注册表来判断本机是否安装微信
    '''
    #微信注册表的一般路径
    reg_path=r"Software\Tencent\WeChat"
    is_installed=True
    try:
        winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path)
    except Exception:
        is_installed=False
    return is_installed

def open_dialog_windows(friends:list[str],wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True):
    '''
    该函数用于打开多个好友(非公众号)的独立聊天窗口
    Args:
        friends:好友或群聊备注名称,需提供完整名称
        wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数
        is_maximize:微信界面是否全屏,默认全屏。
        search_pages:在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面

    Returns:
        chat_windows:所有已打开并在桌面单独显示的独立聊天窗口的列表
    '''
    def get_searh_result(friend,search_result):#查看搜索列表里有没有名为friend的listitem
            listitem=search_result.children(control_type="ListItem")
            #descendants带有按钮能够排出掉非好友的其他搜索结果
            contacts=[item for item in listitem if item.descendants(control_type='Button')]
            names=[re.sub(r'[\u2002\u2004\u2005\u2006\u2009]',' ',item.window_text()) for item in contacts]
            if friend in names:#如果在的话就返回整个搜索到的所有联系人,以及其所处的index
                location=names.index(friend)
                return contacts[location]
            return None
    desktop=Desktop(**Independent_window.Desktop)
    main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=is_maximize)
    chats_button=main_window.child_window(**SideBar.Chats)
    message_list=main_window.child_window(**Main_window.ConversationList)
    search=main_window.child_window(**Main_window.Search)
    if not message_list.exists():
        chats_button.click_input()
    if not message_list.is_visible():
        chats_button.click_input()
    chat_windows=[]
    for friend in friends:
        search.click_input()
        Systemsettings.copy_text_to_windowsclipboard(friend)
        pyautogui.hotkey('ctrl','v')
        search_results=main_window.child_window(**Main_window.SearchResult)
        time.sleep(1)
        friend_button=get_searh_result(friend=friend,search_result=search_results)
        if friend_button:
            friend_button.click_input()
            selected_item=[item for item in message_list.children(control_type='ListItem') if item.is_selected()][0]
            selected_item.double_click_input()
            chat_window={'title':friend,'class_name':'ChatWnd','framework_id':'Win32'}
            chat_window=desktop.window(**chat_window)
            chat_windows.append(chat_window)
            chat_window.minimize()
        else:#搜索结果栏中没有关于传入参数friend好友昵称或备注的搜索结果，关闭主界面,引发NosuchFriend异常
            chats_button.click_input()
            main_window.close()
            raise NoSuchFriendError
    if close_wechat:
        main_window.close()
    return chat_windows

def parse_chat_history(ListItem:ListItemWrapper):
    '''
    该函数用来将聊天记录窗口内每一条聊天记录的ListItem消息转换为文本,传入对象为Listitem
    Args:
        ListItem:主界面右侧聊天区域内ListItem形式的消息
    Returns:
        message_sender:发送消息的对象
        message_content:发送的消息
        message_type:消息类型,具体类型:{'文本','图片','视频','语音','文件','动画表情','视频号','链接','聊天记录','引用消息','卡片链接','微信转账'}
    '''
    language=Tools.language_detector()
    message_sender=ListItem.descendants(control_type='Text')[0].window_text()#无论什么类型消息,发送人永远是属性为Texts的UI组件中的第一个
    send_time=ListItem.descendants(control_type='Text')[1].window_text()#无论什么类型消息.发送时间都是属性为Texts的UI组件中的第二个
    #至于消息的内容那就需要仔细判断一下了
    specialMegCN={'[图片]':'图片消息','[视频]':'视频消息','[动画表情]':'动画表情','[视频号]':'视频号'}
    specialMegEN={'[Photo]':'图片消息','[Video]':'视频消息','[Sticker]':'动画表情','[Channel]':'视频号'}
    specialMegTC={'[圖片]':'图片消息','[影片]':'视频消息','[動態貼圖]':'动画表情','[影音號]':'视频号'}
    #不同语言,处理消息内容时不同
    AudioPattern=SpecialMessages.AudioPattern
    if language=='简体中文':
        if ListItem.window_text() in specialMegCN.keys():#内容在特殊消息中
            message_content=specialMegCN.get(ListItem.window_text())
        else:#文件,卡片链接,语音,以及正常的文本消息
            if ListItem.window_text()=='[文件]':
                filename=ListItem.descendants(control_type='Text')[2].texts()[0]
                message_content=f'文件:{filename}'
            elif re.match(AudioPattern,ListItem.window_text()):
                message_content='语音消息'
            elif len(ListItem.descendants(control_type='Text'))>3:#
                cardContent=ListItem.descendants(control_type='Text')[2:]
                cardContent=[link.window_text() for link in cardContent]
                if '微信转账' in cardContent:
                    index=cardContent.index('微信转账')
                    message_content=f'微信转账:{cardContent[index-2]}:{cardContent[index-1]}'
                else:
                    message_content='卡片内容:'+','.join(cardContent)
            else:#正常文本
                texts=ListItem.descendants(control_type='Text')
                texts=[text.window_text() for text in texts]
                message_content=texts[2]

    if language=='英文':
        if ListItem.window_text() in specialMegEN.keys():
            message_content=specialMegEN.get(ListItem.window_text())
        else:#文件,卡片链接,语音,以及正常的文本消息
            if ListItem.window_text()=='[File]':
                filename=ListItem.descendants(control_type='Text')[2].texts()[0]
                message_content=f'文件:{filename}'
            elif re.match(AudioPattern,ListItem.window_text()):
                message_content='语音消息'

            elif len(ListItem.descendants(control_type='Text'))>3:#
                cardContent=ListItem.descendants(control_type='Text')[2:]
                cardContent=[link.window_text() for link in cardContent]
                if 'Weixin Transfer' in cardContent:
                    index=cardContent.index('Weixin Transfer')
                    message_content=f'微信转账:{cardContent[index-2]}:{cardContent[index-1]}'
                else:
                    message_content='卡片内容:'+','.join(cardContent)
            else:#正常文本
                texts=ListItem.descendants(control_type='Text')
                texts=[text.window_text() for text in texts]
                message_content=texts[2]

    if language=='繁体中文':
        if ListItem.window_text() in specialMegTC.keys():
            message_content=specialMegTC.get(ListItem.window_text())
        else:#文件,卡片链接,语音,以及正常的文本消息
            if ListItem.window_text()=='[檔案]':
                filename=ListItem.descendants(control_type='Text')[2].texts()[0]
                message_content=f'文件:{filename}'
            elif re.match(AudioPattern,ListItem.window_text()):
                message_content='语音消息'
            elif len(ListItem.descendants(control_type='Text'))>3:#
                cardContent=ListItem.descendants(control_type='Text')[2:]
                cardContent=[link.window_text() for link in cardContent]
                if ListItem.window_text()=='' and '微信轉賬' in cardContent:
                    index=cardContent.index('微信轉賬')
                    message_content=f'微信转账:{cardContent[index-2]}:{cardContent[index-1]}'
                else:
                    message_content='链接卡片内容:'+','.join(cardContent)
            else:#正常文本
                texts=ListItem.descendants(control_type='Text')
                texts=[text.window_text() for text in texts]
                message_content=texts[2]
    return message_sender,send_time,message_content

def parse_moments_content(ListItem:ListItemWrapper)->dict[str]:
    '''
    该函数用来将朋友圈内每一个ListItem消息转换dict,传入对象为Listitem
    Args:
        ListItem:朋友圈内ListItem形式的消息
    Returns:
        parse_result:{'好友备注':friend,'发布时间':post_time,\n
        '文本内容':text_content,'点赞者':likes,'评论内容':comments,\n
        '图片数量':image_num,'视频数量':video_num,'卡片链接':cardlink,\n
        '卡片链接内容':cardlink_content,'视频号':channel,'公众号链接内容':official_account_link}
    '''
    def get_next_sibling(element):
        """获取当前元素的同级下一个元素,如果不存在则返回None"""
        parent = element.parent()
        siblings = parent.children()
        try:
            current_idx=siblings.index(element)
            next_sibling=siblings[current_idx + 1]
        except IndexError:
            next_sibling=None
        return next_sibling
    comment_button=ListItem.descendants(**Buttons.CommentButton)[0]#朋友圈评论按钮
    channel_button=ListItem.descendants(**Buttons.ChannelButton)#视频号按钮
    panes=ListItem.descendants(control_type='Pane')
    #包含\d+张图片窗格如果存在那么说明有图片数量
    include_photo_pane=[pane.window_text() for pane in panes if re.match(r'包含\d+张图片',pane.window_text())]
    #注意uia_control查找时descendants方法是无法使用title_re的，只有win32_control的child_window才可以
    #不然直接title_re省的遍历了
    video_pane=[pane for pane in panes if pane.window_text()==Panes.VideoPane['title']]#视频播放窗格
    comment_list=ListItem.descendants(**Lists.CommentList)#朋友圈评论列表,可能有可能没有
    buttons=ListItem.descendants(control_type='Button')#一条朋友圈内所有的按钮
    friend=buttons[0].window_text()#好友名称也就是头像按钮的文本，头像按钮必然是所有按钮元素的首个
    texts=ListItem.descendants(control_type='Text')#texts为一条朋友圈内所有的文本内容列表,最大长度为3
    texts=[ctrl.window_text() for ctrl in texts]
    comment_pane_text=comment_button.parent().children(control_type='Text')
    like_pane=get_next_sibling(comment_button.parent())
    if like_pane:
        likes=like_pane.descendants(control_type='Text')[0].window_text().split('，')
    else:
        likes=[]#点赞共同好友,可能有可能没有
    #可能包含朋友圈文本内容,时间戳,点赞好友名字
    #texts长度为1时,必然是时间戳，没有文本与点赞
    #texts长度为3时文本内容,时间戳,点赞好友名字都有
    #texts长度为2时最麻烦,可能是前两个或后两个的组合:
    #朋友圈文本内容+时间戳,时间戳+点赞好友名字
    #时间戳与评论按钮同一个parent，因此可以直接获取
    post_time=comment_pane_text[0].window_text()
    image_num=0 if not include_photo_pane else int(re.search(r'\d+',include_photo_pane[0])[0])
    video_num=len(video_pane)#视频数量,可能有可能无
    text_content=''#文本内容,可能有可能无,默认无
    comments=[]#评论内容,可能可能没有
    channel=''#视频号
    cardlink=''#卡片链接
    official_account_link=''#公众号链接
    cardlink_content=''#卡片链接的具体内容
    if comment_list:#有人给这个朋友圈评论
        comments=[ListItem.window_text() for ListItem in comment_list[0].children(control_type='ListItem')]
    if len(comment_pane_text)==2: #评论按钮父窗口内的文本，一般而言长度是1，即只有时间戳
    #如果长度为2，那么是卡片链接(BiliBili,QQ音乐等支持以卡片形式分享到朋友圈的链接)或者视频号
        if channel_button:#视频号按钮存在说明分享的是视频号
            channel=comment_pane_text[1].window_text()
        else:#否则是其他卡片链接
            cardlink=comment_pane_text[1].window_text()
            cardlink_content=buttons[2].window_text()
        if len(texts)>=4:#文本内容+时间戳+来源(哔哩哔哩或QQ音乐等)+评论
            text_content=texts[0]
        if len(texts)==3 and texts[0]!=post_time:#文本内容+时间戳+来源
            text_content=texts[0]
    if len(comment_pane_text)==1:#不是卡片链接
        #公众号按钮是否存在
        official_account_button=[button for button in buttons if button.window_text() in ListItem.window_text() and button.window_text()!=friend and button.window_text()!=Buttons.ImageButton['title']]
        if len(texts)>=3:
            text_content=texts[0]
        if len(texts)==2 and texts[0]!=post_time:#文本内容+时间戳
            text_content=texts[0]
        if official_account_button:
            official_account_link=official_account_button.window_text()
    parse_result={'好友备注':friend,'发布时间':post_time,'文本内容':text_content,
    '点赞者':likes,'评论内容':comments,'图片数量':image_num,'视频数量':video_num,
    '卡片链接':cardlink,'卡片链接内容':cardlink_content,'视频号':channel,'公众号链接内容':official_account_link}
    return parse_result

def where_config_folder(open_folder:bool=False):
    '''
    该函数用来获取微信配置文件存放路径(文件夹)\n
    使用时微信必须登录,否则无法获取到完整路径
    Args:
        open_folder:是否打开微信配置文件所在文件夹,默认不打开
    Returns:
        folder_path:配置文件存放路径
    '''
    wechat_process=None
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name']=='WeChat.exe':
            wechat_process=process
            break
    #只要微信登录了,就一定会用到本地聊天文件保存位置:Wechat Files下的一个wxid开头的文件下的Msg,
    #这个文件夹里包含了聊天纪录数据等内容
    #wechat_process是进程句柄,通过这个进程句柄的memory_maps方法可以实现
    #内存映射文件检测
    folder_path=''
    for mem_map in wechat_process.memory_maps():
        if 'Msg'  in mem_map.path:
            folder_path=mem_map.path
            #获取到的路径的basename是含\Msg\xxx.db，我们只需要他的dir就可以然后把Msg换为config
            folder_path=os.path.dirname(folder_path).replace('Msg','config')
            break
    if open_folder and os.path.exists(folder_path):
        os.startfile(folder_path)
    return folder_path