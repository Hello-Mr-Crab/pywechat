'''
WechatTools
---------------
该模块中封装了一系列关于PC微信的工具,主要包括:检测微信运行状态;\n
打开微信主界面内绝大多数界面\n
模块:\n
---------------
Tools:一些关于PC微信的工具,以及13个open方法用于打开微信主界面内所有能打开的界面\n
API:打开指定公众号与微信小程序以及视频号,可为微信内部小程序公众号自动化操作提供便利\n
------------------------------------
函数:\n
函数为上述模块内的所有方法\n
--------------------------------------
使用该模块的方法时,你可以:\n
```
from pyweixin.WechatTools import API
API.open_weixin_miniprogram(name='问卷星')
```
或者:\n
```
from pyweixin import WechatTools as wt
wt.open_weixin_miniprogram(name='问卷星')
```
或者:\n
```
from pyweixin.WechatTools import open_weixin_miniprogram
open_weixin_miniprogram(name='问卷星')
```
或者:\n
```
from pyweixin import open_weixin_miniprogram
open_weixin_miniprogram(name='问卷星')
```
'''
############################依赖环境###########################
import os
import re
import time
import winreg
import psutil
import win32api
import pyautogui
import win32gui
import win32con
import subprocess
import win32com.client
from pywinauto import mouse,Desktop
from pywinauto.controls.uia_controls import ListItemWrapper
from pywinauto.controls.uia_controls import ListViewWrapper
from .Errors import NetWorkNotConnectError
from .Errors import NoSuchFriendError
from .Errors import ScanCodeToLogInError
from .Errors import NoResultsError,NotFriendError,NotInstalledError
from .Errors import NoChatHistoryError
from .Errors import NoSuchMessageError
from .Errors import ElementNotFoundError
from pywinauto.findwindows import ElementNotFoundError
from pywinauto import WindowSpecification
from pyweixin.Uielements import Login_window,Main_window,SideBar,Independent_window,Buttons,Texts,Menus,TabItems,Lists
from pyweixin.WinSettings import Systemsettings 
##########################################################################################
Login_window=Login_window()
Main_window=Main_window()
SideBar=SideBar()
Independent_window=Independent_window()
Buttons=Buttons()
Texts=Texts()
Menus=Menus()
TabItems=TabItems()
Lists=Lists()
pyautogui.FAILSAFE = False#防止鼠标在屏幕边缘处造成的误触

class Tools():
    '''该模块中封装了关于PC微信的工具\n
    以及13个open方法用于打开微信主界面内所有能打开的界面\n
    ''' 
    @staticmethod
    def is_weixin_running():
        '''
        该方法通过检测当前windows系统的进程中\n
        是否有Weixin.exe该项进程来判断微信是否在运行
        '''
        wmi=win32com.client.GetObject('winmgmts:')
        processes=wmi.InstancesOf('Win32_Process')
        for process in processes:
            if process.Name.lower() == 'Weixin.exe'.lower():
                return True
        return False
            
    @staticmethod
    def find_weixin_path(copy_to_clipboard:bool=True):
        '''该方法用来查找微信的路径,无论微信是否运行都可以查找到\n
            copy_to_clipboard:\t是否将微信路径复制到剪贴板\n
        '''
        if Tools.is_weixin_running():
            wmi=win32com.client.GetObject('winmgmts:')
            processes=wmi.InstancesOf('Win32_Process')
            for process in processes:
                if process.Name.lower() == 'Weixin.exe'.lower():
                    exe_path=process.ExecutablePath
                    if exe_path:
                        # 规范化路径并检查文件是否存在
                        exe_path=os.path.abspath(exe_path)
                        weixin_path=exe_path
            if copy_to_clipboard:
                Systemsettings.copy_text_to_windowsclipboard(weixin_path)
                print("已将微信程序路径复制到剪贴板")
            return weixin_path
        else:
            #windows环境变量中查找WeChat.exe路径
            weixin_environ_path=[path for path in dict(os.environ).values() if 'Weixin.exe' in path]#
            if weixin_environ_path:
                if copy_to_clipboard:
                    Systemsettings.copy_text_to_windowsclipboard(weixin_path)
                    print("已将微信程序路径复制到剪贴板")
                return weixin_environ_path
            if not weixin_environ_path:
                try:
                    reg_path=r"Software\Tencent\Weixin"
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                        Installdir=winreg.QueryValueEx(key,"InstallPath")[0]
                    weixin_path=os.path.join(Installdir,'Weixin.exe')
                    if copy_to_clipboard:
                        Systemsettings.copy_text_to_windowsclipboard(weixin_path)
                        print("已将微信程序路径复制到剪贴板")
                    return weixin_path
                except FileNotFoundError:
                    raise NotInstalledError
    
    @staticmethod
    def find_friend_in_MessageList(friend:str,is_maximize:bool=True,search_pages:int=5)->tuple[WindowSpecification|None,WindowSpecification]:
        '''
        该方法用于在会话列表中寻找好友(非公众号)。
        Args:
            friend:好友或群聊备注名称,需提供完整名称
            is_maximize:微信界面是否全屏,默认全屏。
            search_pages:在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
        Returns:
            (edit_area,main_windwo):若edit_area存在:返回值为 (edit_area,main_window) 同时返回好友聊天界面内的编辑区域与主界面
            否则:返回值为(None,main_window)
        '''
        def selecte_in_messageList(friend):
            '''
            用来返回会话列表中automation_id为friend的ListItem项是否为最后一项
            最后一项必须要点击顶部靠下位置，不然会误触
            '''
            is_last=False
            message_list=message_list_pane.children(control_type='ListItem')
            friend_button=None
            for i in range(len(message_list)):
                if friend in message_list[i].automation_id():
                    friend_button=message_list[i]
                    break
            if i==len(message_list)-1:
                is_last=True
            return friend_button,is_last

        main_window=Tools.open_weixin(is_maximize=is_maximize)
        #先看看当前微信右侧界面是不是聊天界面可能存在不是聊天界面的情况比如是纯白色的微信的icon
        chats_button=main_window.child_window(**SideBar.Chats)
        message_list_pane=main_window.child_window(**Main_window.ConversationList)
        rectangle=message_list_pane.rectangle()
        activateScollbarPosition=(rectangle.right-5,rectangle.top+20)
        if not message_list_pane.exists():
            chats_button.click_input()
        if not message_list_pane.is_visible():
            chats_button.click_input()
        scrollable=True if len(message_list_pane.children())>10 else False
        CurrentChatWindow={'control_type':'Edit','title':friend}
        current_chat=main_window.descendants(**CurrentChatWindow)
        if current_chat:
        #如果当前主界面是某个好友的聊天界面且聊天界面顶部的名称为好友名称，直接返回结果,current_chat可能是刚登录打开微信的纯白色icon界面
            edit_area=current_chat[0]
            edit_area.click_input()
            return edit_area,main_window
        else:
            message_list=message_list_pane.children(control_type='ListItem')
            if len(message_list)==0:
                return None,main_window
            if not scrollable:
                friend_button,is_last=selecte_in_messageList(friend)
                if friend_button:
                    if is_last:
                        rec=friend_button.rectangle()
                        mouse.click(coords=(int(rec.left+rec.right)//2,rec.top-12))
                        edit_area=main_window.descendants(title=friend,control_type='Edit')[0]
                    else:
                        friend_button.click_input()
                        edit_area=main_window.descendants(title=friend,control_type='Edit')[0]
                    return edit_area,main_window
                else:
                    return None,main_window
            if scrollable:
                mouse.click(coords=activateScollbarPosition)
                pyautogui.press('Home')
                edit_area=None
                for _ in range(search_pages):
                    friend_button,is_last=selecte_in_messageList(friend)
                    if friend_button:
                        if is_last:
                            rec=friend_button.rectangle()
                            mouse.click(coords=(int(rec.left+rec.right)//2,rec.top-12))
                            edit_area=main_window.descendants(title=friend,control_type='Edit')[0]
                        else:
                            friend_button.click_input()
                            edit_area=main_window.descendants(title=friend,control_type='Edit')[0]  
                        break
                    else:
                        pyautogui.press("pagedown",_pause=False)
                        time.sleep(0.5)
                mouse.click(coords=activateScollbarPosition)
                pyautogui.press('Home')
                if edit_area:
                    return edit_area,main_window
                else:
                    return None,main_window
    
    @staticmethod
    def set_weixin_as_environ_path():
        '''该方法用来自动打开系统环境变量设置界面,将微信路径自动添加至其中\n'''
        os.environ.update({"__COMPAT_LAYER":"RUnAsInvoker"})
        subprocess.Popen(["SystemPropertiesAdvanced.exe"])
        time.sleep(2)
        systemwindow=win32gui.FindWindow(None,u'系统属性')
        if win32gui.IsWindow(systemwindow):#将系统变量窗口置于桌面最前端
            win32gui.ShowWindow(systemwindow,win32con.SW_SHOW)
            win32gui.SetWindowPos(systemwindow,win32con.HWND_TOPMOST,0,0,0,0,win32con.SWP_NOMOVE|win32con.SWP_NOSIZE)    
        pyautogui.hotkey('alt','n',interval=0.5)#添加管理员权限后使用一系列快捷键来填写微信刻路径为环境变量
        pyautogui.hotkey('alt','n',interval=0.5)
        pyautogui.press('shift')
        pyautogui.typewrite('weixinpath')
        try:
            Tools.find_weixin_path()
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
    def open_weixin(is_maximize:bool=True):
        
        def handle_login_window(login_window:WindowSpecification,is_maximize:bool):
            retry_interval=0.5
            max_retry_times=20
            counter=0
            try:
                login_button=login_window.child_window(**Login_window.LoginButton)
                login_button.set_focus()
                login_button.click_input()
                main_window=Desktop(backend='uia').window(**Main_window.MainWindow)
                while not main_window.exists():
                    counter+=1
                    time.sleep(retry_interval)
                    if counter>=max_retry_times:
                        raise NetWorkNotConnectError
                move_window_to_center(main_window=main_window,is_maximize=is_maximize)
                NetWorkErrotText=main_window.child_window(**Texts.NetWorkError)
                if NetWorkErrotText.exists():
                    main_window.close()
                    raise NetWorkNotConnectError(f'未连接网络,请连接网络后再进行后续自动化操作！')
                return main_window 
            except ElementNotFoundError:
                raise ScanCodeToLogInError
                
        def move_window_to_center(main_window:WindowSpecification,is_maximize:bool):
            window_width,window_height=main_window.rectangle().width(),main_window.rectangle().height()
            handle=main_window.handle
            screen_width,screen_height=win32api.GetSystemMetrics(win32con.SM_CXSCREEN),win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
            new_left=(screen_width-window_width)//2
            new_top=(screen_height-window_height)//2
            if screen_width!=window_width:
                
                #以下的操作均使用win32gui实现,包括将主界面的大小,移动到前台，移动到屏幕中央
                ###################################
                #win32gui.SetWindowPos来实现移动窗口到前台来,相当于win32gui.SetForeGroundWindow()
                #但是win32gui.SetForeGroundWindow()函数可能会因为权限不足等一系列问题报错
                #所以使用win32gui.SetWindowPos()来实现类似的功能
                win32gui.SetWindowPos(handle,win32con.HWND_TOPMOST, 
                0, 0, 0, 0,win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                ###########################################
            #移动窗口到屏幕中央
                win32gui.MoveWindow(handle, new_left, new_top, window_width, window_height, True)
            ##############################
            if is_maximize:
                win32gui.ShowWindow(handle, win32con.SW_MAXIMIZE)
            if not is_maximize:
                win32gui.ShowWindow(handle,win32con.SW_SHOWDEFAULT)
        weixin_path=Tools.find_weixin_path(copy_to_clipboard=False)
        os.startfile(weixin_path)
        login_window=Desktop(backend='uia').window(**Login_window.LoginWindow)
        main_window=Desktop(backend='uia').window(**Main_window.MainWindow)
        if login_window.exists():
            handle_login_window(login_window=login_window,is_maximize=is_maximize)
        if main_window.exists():
            move_window_to_center(main_window=main_window,is_maximize=is_maximize)
        return main_window

    @staticmethod
    def open_dialog_window(friend:str,is_maximize:bool=True,search_pages:int=5)->tuple[WindowSpecification,WindowSpecification]: 
        '''
        该方法用于打开某个好友(非公众号)的聊天窗口
        Args:
            friend:好友或群聊备注名称,需提供完整名称
            is_maximize:微信界面是否全屏,默认全屏。
            search_pages:在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
        Returns:
            (edit_area,main_window):editarea:主界面右下方与好友的消息编辑区域,main_window:微信主界面
        '''
        def get_searh_result(friend,search_result):#查看搜索列表里有没有名为friend的listitem
            listitems=search_result.children(control_type="ListItem")
            contacts=[item for item in listitems]
            names=[re.sub(r'[\u2002\u2004\u2005\u2006\u2009]',' ',item.window_text()) for item in listitems]
            if friend in names:#如果在的话就返回整个搜索到的所有联系人,以及其所处的index
                location=names.index(friend)         
                return contacts[location]
            return None
        #如果search_pages不为0,即需要在会话列表中滚动查找时，使用find_friend_in_Messagelist方法找到好友,并点击打开对话框
        if search_pages:
            edit_area,main_window=Tools.find_friend_in_MessageList(friend=friend,is_maximize=is_maximize,search_pages=search_pages)
            chat_button=main_window.child_window(**SideBar.Chats)
            if edit_area:#edit_area不为None,即说明find_friend_in_MessageList找到了聊天窗口,直接返回结果
                edit_area.click_input()
                return edit_area,main_window
            #edit_area为None没有在会话列表中找到好友,直接在顶部搜索栏中搜索好友
            #先点击侧边栏的聊天按钮切回到聊天主界面
            #顶部搜索按钮搜索好友
            search=main_window.descendants(**Main_window.Search)[0]
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
            main_window=Tools.open_weixin(is_maximize=is_maximize)
            chat_button=main_window.child_window(**SideBar.Chats)
            message_list_pane=main_window.child_window(**Main_window.ConversationList)
            #先看看当前聊天界面是不是好友的聊天界面
            CurrentChatWindow=Main_window.CurrentChatWindow
            CurrentChatWindow['title']=friend
            current_chat=main_window.descendants(**CurrentChatWindow)
            if current_chat:
                edit_area=current_chat[0]
                edit_area.click_input()
                return edit_area,main_window
            else:#否则直接从顶部搜索栏出搜索结果
                #如果会话列表不存在或者不可见的话才点击一下聊天按钮
                if not message_list_pane.exists():
                    chat_button.click_input()
                if not message_list_pane.is_visible():
                    chat_button.click_input()        
                search=main_window.descendants(**Main_window.Search)[0]
                search.click_input()
                Systemsettings.copy_text_to_windowsclipboard(friend)
                pyautogui.hotkey('ctrl','v')
                search_results=main_window.child_window(title='',control_type='List')
                friend_button=get_searh_result(friend=friend,search_result=search_results)
                if friend_button:
                    friend_button.click_input()
                    edit_area=main_window.descendants(title=friend,control_type='Edit')[0]
                    edit_area.click_input()
                    return edit_area,main_window#同时返回搜索到的该好友的聊天窗口与主界面！若只需要其中一个需要使用元祖索引获取。
                else:#搜索结果栏中没有关于传入参数friend好友昵称或备注的搜索结果，关闭主界面,引发NosuchFriend异常
                    chat_button.click_input()
                    main_window.close()
                    raise NoSuchFriendError
