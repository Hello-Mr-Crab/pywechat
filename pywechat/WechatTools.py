'''
 
WeChatTools
===========
该模块中封装了Tools静态类,主要用来辅助WeChatAuto实现其他自动化功能。


Tools
-----
    - `is_wechat_running`: 判断微信是否在运行
    - `where_wechat`: 查找微信路径
    - `get_current_wxid`: 获取当前登录账号wxid
    - `where_wxid_folder`: 当前登录微信的wxid文件夹
    - `where_msg_folder`: 获取微信msg文件夹路径
    - `where_chatfiles_folder`: 获取微信聊天文件存放路径(文件夹)
    - `set_weixin_as_environ_path`: 将微信路径添加到用户变量
    - `cancle_pin`: 取消窗口置顶,为了保证准确性(基于微信主界面的操作,必须让微信主界面置于顶层,不然在当前界面内乱点就尴尬了),
        open_weixin需要将微信主窗口置于桌面顶层,但这可能导致打开微信内独立(比如朋友圈)窗口时,该窗口无法自动浮于微信窗口顶层,
        只是在微信主界面底部,为解决该问题,已在涉及各种类似操作的方法中调用过该方法,如果二次开发时遇到这个特性,可以使用该方法取消微信主窗口置顶
    - `move_window_to_center`: 将未全屏的窗口移动到屏幕中央
    - `...`
    - `is_scrollable`: 判断列表类型UI是否可以滚动
    - `open_weixin`: 打开微信主界面
    - `find_friend_in_MessageList`: 在会话列表中查找好友
    - `open_moments`: 打开通讯录界面
    - `open_moments`: 打开通讯录管理界面
    - `open_moments`: 打开收藏
    - `open_moments`: 打开朋友圈
    - `open_channels`: 打开视频号
    - `open_search`: 打开搜一搜
    - `open_miniprograme_pane`: 打开小程序面板
    - `open_settings`: 打开设置
    - `open_chatfiles`: 打开微信聊天文件
    - `open_dialog_window`: 打开与好友的聊天窗口
    - `open_friend_profile`:打开好友个人简介界面
    - `open_chatinfo`:  打开好友或群聊右侧的聊天信息界面
    - `open_chat_history`: 打开与好友demo 聊天记录窗口
    - `search_miniprogram`: 搜索并打开指定小程序
    - `search_official_account`: 搜索并打开指定公众号
    - `search_channels`: 打开视频号并搜索指定内容


Examples
========
使用该模块的方法时,你可以:

    >>> from pyweixin.WeChatTools import Tools
    >>> Navigator.open_dialog_window(name='一家人')

或者:

    >>> from pyweixin import Tools
    >>> Navigator.open_dialog_window(friend='一家人')


Also:
=====

    pywechat内所有方法的位置参数的支持全局设置,be like:

    ```
    from pyweixin import Navigator,GlobalConfig
    GlobalConfig.load_delay=1.5
    GlobalConfig.is_maximize=True
    GlobalConfig.close_weixin=False
    Navigator.search_channels(search_content='微信4.0')
    Navigator.search_miniprogram(name='问卷星')
    Navigator.search_official_account(name='微信')
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
import ctypes
from pywinauto import mouse,Desktop
###########################内部依赖###################################
from .WinSettings import SystemSettings
from pywinauto.controls.uia_controls import ListItemWrapper
from pywinauto.controls.uia_controls import ListViewWrapper
from pywinauto import WindowSpecification
from .Config import GlobalConfig
from .Errors import NetWorkNotConnectError
from .Errors import WeChatNotStartError
from .Errors import NoSuchFriendError
from .Errors import ScanCodeToLogInError
from .Errors import NoResultsError,NotFriendError,NotInstalledError
from .Errors import ElementNotFoundError
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
desktop=Desktop(backend='uia')

class Tools():
    '''
    该类中封装了一些关于PC微信的工具
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
        该方法通过检测当前windows系统的进程中
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
    def where_wechat(copy_to_clipboard:bool=True):
        '''该方法用来查找微信的路径,无论微信是否运行都可以查找到
        Args:
            copy_to_clipboard:是否将微信路径复制到剪贴板
        Returns:
            wechat_path:微信路径
        '''
        wechat_path=''
        if Tools.is_wechat_running():
            wmi=win32com.client.GetObject('winmgmts:')
            processes=wmi.InstancesOf('Win32_Process')
            for process in processes:
                if process.Name.lower() == 'WeChat.exe'.lower():
                    exe_path=process.ExecutablePath
                    if exe_path:
                        #规范化路径并检查文件是否存在
                        exe_path=os.path.abspath(exe_path)
                        wechat_path=exe_path
            if copy_to_clipboard:
                SystemSettings.copy_text_to_clipboard(wechat_path)
                print("已将微信程序路径复制到剪贴板")
            return wechat_path
        else:
            try:
                reg_path=r"Software\Tencent\WeChat"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                    Installdir=winreg.QueryValueEx(key,"InstallPath")[0]
                wechat_path=os.path.join(Installdir,'WeChat.exe')
                if copy_to_clipboard:
                    SystemSettings.copy_text_to_clipboard(wechat_path)
                    print("已将微信程序路径复制到剪贴板")
                return wechat_path
            except FileNotFoundError:
                raise NotInstalledError

    @staticmethod
    def is_VerticalScrollable(List:ListViewWrapper)->bool:
        '''
        该函数用来判断微信内的列表类型控件是否可以垂直滚动
        原理:微信内停靠在List右侧的灰色scrollbar无Ui
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
    def judge_wechat_state()->int:
        '''该方法用来判断微信运行状态
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

    @staticmethod
    def judge_independant_window_state(window:dict)->int:
        '''该方法用来判断微信内独立于微信主界面的窗口的状态
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


    @staticmethod
    def move_window_to_center(Window:dict=Main_window.MainWindow,handle:int=0)->WindowSpecification:
        '''该方法用来将已打开的界面置顶并移动到屏幕中央并返回该窗口的Windowspecification实例
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
            raise ValueError(f'参数错误!kwargs参数字典中必须包含class_name')
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

    @staticmethod
    def parse_message_content(ListItem:ListItemWrapper,friendtype:str):
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
    def parse_moments_content(ListItem:ListItemWrapper):
        '''
        该方法用来将朋友圈内每一个ListItem消息转换dict,传入对象为Listitem
        Args:
            ListItem:朋友圈内ListItem形式的消息
        Returns:
            parse_result:{'好友备注':friend,'发布时间':post_time,
            '文本内容':text_content,'点赞者':likes,'评论内容':comments,
            '图片数量':image_num,'视频数量':video_num,'卡片链接':cardlink,
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
    def pull_latest_message(chatList:ListViewWrapper):#获取聊天界面内的聊天记录
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
            edit_area,main_window=Navigator.open_dialog_window(friend='路人甲')
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
    def where_filesave_folder()->str:
        try:
            reg_path=r"Software\Tencent\WeChat"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                FileSavedir=winreg.QueryValueEx(key,"FileSavePath")[0]
            return FileSavedir
        except FileNotFoundError:
                raise NotInstalledError

    @staticmethod
    def get_current_wxid()->str:
        FileSavedir=Tools.where_filesave_folder()
        config_data=os.path.join(FileSavedir,'WeChat Files','All Users','config','config.data')
        with open(config_data,'rb') as f:
            data=f.read()
            wxid_start=data.find(b'wxid_')
            wxid=data[wxid_start:wxid_start+18].decode(encoding='utf-8')
        return wxid
    
    @staticmethod
    def where_wxid_folder(open_folder:bool=False)->str:
        '''
        该方法用来获取当前登录微信的wxid文件夹
        Args:
            open_folder:是否打开存放聊天文件的文件夹,默认不打开
        Returns:
            folder_path:聊天文件存放路径
        '''
        wxid=Tools.get_current_wxid()
        FileSavedir=Tools.where_filesave_folder()
        folder_path=os.path.join(FileSavedir,'WeChat Files',wxid)
        if open_folder and folder_path:
            os.startfile(folder_path)
        return folder_path

    @staticmethod
    def where_chatfile_folder(open_folder:bool=False)->str:
        '''
        该方法用来获取微信聊天文件存放路径(文件夹)
        使用时微信必须登录,否则无法获取到完整路径
        Args:
            open_folder:是否打开存放聊天文件的文件夹,默认不打开
        Returns:
            folder_path:聊天文件存放路径
        '''
        wxid_folder=Tools.where_wxid_folder()
        folder_path=os.path.join(wxid_folder,'FileStorage','File')
        if open_folder and folder_path:
            os.startfile(folder_path)
        return folder_path
    
    @staticmethod
    def where_video_folder(open_folder:bool=False)->str:
        '''
        该方法用来获取微信聊天视频存放路径(文件夹)
        使用时微信必须登录,否则无法获取到完整路径
        Args:
            open_folder:是否打开存放微信聊天视频的文件夹,默认不打开
        Returns:
            folder_path:聊天文件存放路径
        '''
        wxid_folder=Tools.where_wxid_folder()
        folder_path=os.path.join(wxid_folder,'FileStorage','Video')
        if open_folder and folder_path:
            os.startfile(folder_path)
        return folder_path

    @staticmethod
    def where_SnsCache_folder(open_folder:bool=False)->str:
        '''
        该方法用来获取微信朋友圈缓存路径(文件夹)
        使用时微信必须登录,否则无法获取到完整路径
        Args:
            open_folder:是否打开存放微信朋友圈缓存的文件夹,默认不打开
        Returns:
            folder_path:聊天文件存放路径
        '''
        wxid_folder=Tools.where_wxid_folder()
        folder_path=os.path.join(wxid_folder,'FileStorage','Sns','Cache')
        if open_folder and folder_path:
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
        SystemSettings.copy_text_to_clipboard(folder_path)
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


class Navigator():
    '''
    打开微信内一切能打开的界面
    '''
    @staticmethod
    def open_wechat(is_maximize:bool=None,window_size:tuple=None)->WindowSpecification:
        '''
        该方法用来打开微信
        Args:
            is_maximize:微信界面是否全屏,默认不全屏
        Returns:
            main_window:微信主界面
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if window_size is None:
            window_size=GlobalConfig.window_size
        max_retry_times=40
        retry_interval=0.5
        #处理登录界面的闭包函数，点击进入微信，若微信登录界面存在直接传入窗口句柄，否则自己查找
        def move_window_to_center(main_window:WindowSpecification):
            #将微信主界面移动到窗口正中间,并调整全屏
            main_window.restore()
            win32gui.SetWindowPos(main_window.handle,win32con.HWND_TOPMOST, 
            0, 0,window_size[0], window_size[1],win32con.SWP_NOMOVE)
            window_width,window_height=window_size[0],window_size[1]
            screen_width,screen_height=win32api.GetSystemMetrics(win32con.SM_CXSCREEN),win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
            new_left=(screen_width-window_width)//2
            new_top=(screen_height-window_height)//2
            if screen_width!=window_width:
                #移动窗口到屏幕中央
                win32gui.MoveWindow(main_window.handle,new_left,new_top,window_width,window_height,True)
            ###############################
            return main_window
    
        def handle_login_window(is_maximize=is_maximize,max_retry_times=max_retry_times,retry_interval=retry_interval):
            counter=0
            wechat_path=Tools.where_wechat(copy_to_clipboard=False)
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
            login_window=Tools.move_window_to_center(handle=login_window_handle)
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
                main_window=move_window_to_center(main_window)
                if is_maximize:
                    main_window.maximize()
                NetWorkErrotText=main_window.child_window(**Texts.NetWorkError)
                if NetWorkErrotText.exists():
                    main_window.close()
                    raise NetWorkNotConnectError(f'未连接网络,请连接网络后再进行后续自动化操作！')
                return main_window
            except ElementNotFoundError:
                raise ScanCodeToLogInError
        #同时查找主界面与登录界面句柄，二者有一个存在都证明微信已经启动
        main_window_handle=win32gui.FindWindow(Main_window.MainWindow['class_name'],None)
        if main_window_handle:
            main_window=desktop.window(handle=main_window_handle)
            win32gui.ShowWindow(main_window_handle,win32con.SW_SHOWNORMAL)
            main_window=move_window_to_center(main_window)
            if is_maximize:
                main_window.maximize()
            NetWorkErrotText=main_window.child_window(**Texts.NetWorkError)
            if NetWorkErrotText.exists():
                main_window.close()
                raise NetWorkNotConnectError(f'未连接网络,请连接网络后再进行后续自动化操作！')
            return main_window
        else:#微信未启动
            #处理登录界面
            return handle_login_window()

    @staticmethod
    def open_settings(is_maximize:bool=None,close_wechat:bool=None):
        '''
        该方法用来打开微信设置界面。
        Args:
            is_maximize:微信界面是否全屏,默认全屏。
            close_wechat:任务结束后是否关闭微信,默认关闭
        Returns:
            (settings_window,main_window):settings_window:设置界面窗口
            main_window:微信主界面,当close_wechat设置为True时,main_window为None
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_wechat is None:
            close_wechat=GlobalConfig.close_wechat
        main_window=Navigator.open_wechat(is_maximize=is_maximize)
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

    @staticmethod
    def open_dialog_window(friend:str,is_maximize:bool=None,search_pages:int=None):
        '''
        该方法用于打开某个好友(非公众号)的聊天窗口
        Args:
            friend:好友或群聊备注名称,需提供完整名称
            is_maximize:微信界面是否全屏,默认全屏。
            search_pages:在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
        Returns:
            (edit_area,main_window):editarea:主界面右下方与好友的消息编辑区域,main_window:微信主界面
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if search_pages is None:
            search_pages=GlobalConfig.search_pages
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
            edit_area,main_window=Navigator.find_friend_in_SessionList(friend=friend,is_maximize=is_maximize,search_pages=search_pages)
            chat_button=main_window.child_window(**SideBar.Chats)
            if edit_area:#edit_area不为None,即说明find_friend_in_MessageList找到了聊天窗口,直接返回结果
                return edit_area,main_window
            #edit_area为None没有在会话列表中找到好友,直接在顶部搜索栏中搜索好友
            #先点击侧边栏的聊天按钮切回到聊天主界面
            #顶部搜索按钮搜索好友
            search=main_window.child_window(**Main_window.Search).wait(wait_for='visible',retry_interval=0.1,timeout=3)
            search.click_input()
            SystemSettings.copy_text_to_clipboard(friend)
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
            main_window=Navigator.open_wechat(is_maximize=is_maximize)
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
                SystemSettings.copy_text_to_clipboard(friend)
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
    def open_seperate_dialog_window(friend:str,is_maximize:bool=None,close_wechat:bool=None,window_minimize:bool=True):
        '''
        该方法用于打开多个好友(非公众号)的独立聊天窗口
        Args:
            friend:好友或群聊备注名称,需提供完整名称
            is_maximize:微信界面是否全屏,默认全屏
            close_wechat:是否关闭微信，默认关闭
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
    
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_wechat is None:
            close_wechat=GlobalConfig.close_wechat
        desktop=Desktop(**Independent_window.Desktop)
        main_window=Navigator.open_wechat(is_maximize=is_maximize)
        chats_button=main_window.child_window(**SideBar.Chats)
        message_list=main_window.child_window(**Main_window.ConversationList)
        search=main_window.child_window(**Main_window.Search)
        if not message_list.exists():
            chats_button.click_input()
        if not message_list.is_visible():
            chats_button.click_input()     
        search.click_input()
        SystemSettings.copy_text_to_clipboard(friend)
        pyautogui.hotkey('ctrl','v')
        search_results=main_window.child_window(**Main_window.SearchResult)
        time.sleep(1)
        friend_button=get_searh_result(friend=friend,search_result=search_results)
        if friend_button:
            friend_button.click_input()
            time.sleep(0.5)
            selected_item=[item for item in message_list.children(control_type='ListItem') if item.is_selected()][0]
            selected_item.double_click_input()
            dialog_window=desktop.window(title=friend,class_name='ChatWnd',framework_id='Win32')
            if close_wechat:
                main_window.close()
            if window_minimize:
                dialog_window.minimize()
            return dialog_window
        else:#搜索结果栏中没有关于传入参数friend好友昵称或备注的搜索结果，关闭主界面,引发NosuchFriend异常
            chats_button.click_input()
            main_window.close()
            raise NoSuchFriendError
        
    @staticmethod
    def find_friend_in_SessionList(friend:str,is_maximize:bool=None,search_pages:int=None):
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

        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if search_pages is None:
            search_pages=GlobalConfig.search_pages
        main_window=Navigator.open_wechat(is_maximize=is_maximize)
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
    def open_friend_settings(friend:str,is_maximize:bool=None,search_pages:int=None):
        '''
        该方法用于打开好友右侧的设置界面
        Args:
            friend:好友备注名称,需提供完整名称
            is_maximize:微信界面是否全屏,默认全屏。
            search_pages:在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
        Returns:
            (friend_settings_window,main_window):friend_settings_window:好友右侧的设置界面
            main_window:微信主界面
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if search_pages is None:
            search_pages=GlobalConfig.search_pages
        main_window=Navigator.open_dialog_window(friend=friend,is_maximize=is_maximize,search_pages=search_pages)[1]
        try:
            ChatMessage=main_window.child_window(**Buttons.ChatMessageButton)
            ChatMessage.click_input()
            friend_settings_window=main_window.child_window(**Main_window.FriendSettingsWindow)
        except ElementNotFoundError:
            main_window.close()
            raise NotFriendError(f'非正常好友,无法打开设置界面！')
        return friend_settings_window,main_window

    @staticmethod
    def open_contacts_manage(is_maximize:bool=None,close_wechat:bool=None):
        '''
        该方法用于打开通讯录管理界面
        Args:
            is_maximize:微信界面是否全屏,默认全屏。
            close_wechat:任务结束后是否关闭微信,默认关闭
        Returns:
            (contacts_manage_window,main_window):contacts_manage_window:通讯录管理界面
            main_window:微信主界面,当close_wechat设置为True时返回None
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_wechat is None:
            close_wechat=GlobalConfig.close_wechat
        main_window=Navigator.open_wechat(is_maximize=is_maximize)
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
    def open_friend_settings_menu(friend:str,is_maximize:bool=None,search_pages:int=None):
        '''
        该方法用于打开好友设置菜单
        Args:
            friend:好友备注名称,需提供完整名称
            is_maximize:微信界面是否全屏,默认全屏。
            search_pages:在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
        Returns:
            (friend_menu,friend_settings_window,main_window):friend_menu:在friend_settings_window界面里点击好友头像弹出的菜单
            friend_settings_window:好友右侧的设置界面
            main_window:微信主界面
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if search_pages is None:
            search_pages=GlobalConfig.search_pages
        friend_settings_window,main_window=Navigator.open_friend_settings(friend=friend,is_maximize=is_maximize,search_pages=search_pages)
        friend_button=friend_settings_window.child_window(title=friend,control_type="Button",found_index=0)
        friend_button.click_input()
        profile_window=friend_settings_window.child_window(**Panes.FriendProfilePane)
        more_button=profile_window.child_window(**Buttons.MoreButton)
        more_button.click_input()
        friend_menu=profile_window.child_window(**Menus.FriendProfileMenu)
        return friend_menu,friend_settings_window,main_window

    @staticmethod
    def open_collections(is_maximize:bool=None)->WindowSpecification:
        '''
        该方法用于打开收藏界面
        Args:
            is_maximize:微信界面是否全屏,默认全屏。
        Returns:
            main_window:微信主界面
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        main_window=Navigator.open_wechat(is_maximize=is_maximize)
        collections_button=main_window.child_window(**SideBar.Collections)
        collections_button.click_input()
        return main_window

    @staticmethod
    def open_group_settings(group_name:str,is_maximize:bool=None,search_pages:int=None):
        '''
        该方法用来打开群聊设置界面
        Args:
            group_name:群聊备注名称,需提供完整名称
            is_maximize:微信界面是否全屏,默认全屏。
            search_pages:在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
        Returns:
            (group_settings_window,main_window):group_sttings_window:群聊设置界面
            main_window:微信主界面
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if search_pages is None:
            search_pages=GlobalConfig.search_pages
        main_window=Navigator.open_dialog_window(friend=group_name,is_maximize=is_maximize,search_pages=search_pages)[1]
        ChatMessage=main_window.child_window(**Buttons.ChatMessageButton)
        ChatMessage.click_input()
        group_settings_window=main_window.child_window(**Main_window.GroupSettingsWindow)
        group_settings_window.child_window(**Texts.GroupNameText).click_input()
        return group_settings_window,main_window

    @staticmethod
    def open_moments(is_maximize:bool=None,close_wechat:bool=None):
        '''
        该方法用于打开微信朋友圈
        Args:
            is_maximize:微信界面是否全屏,默认全屏。
            close_wechat:任务结束后是否关闭微信,默认关闭
        Returns:
            (moments_window,main_window):moments_window:朋友圈主界面
            main_window:微信主界面,当close_wechat设置为True时,main_window为None
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_wechat is None:
            close_wechat=GlobalConfig.close_wechat
        main_window=Navigator.open_wechat(is_maximize=is_maximize)
        moments_button=main_window.child_window(**SideBar.Moments)
        moments_button.click_input()
        moments_window=Tools.move_window_to_center(Independent_window.MomentsWindow)
        moments_window.child_window(**Buttons.RefreshButton).click_input()
        if close_wechat:
            main_window.close()
            main_window=None
        return moments_window,main_window

    @staticmethod
    def open_chatfiles(window_maximize:bool=None,is_maximize:bool=None,close_wechat:bool=None):
        '''
        该方法用于打开聊天文件界面
        Args:
            wechat_maximize:微信界面是否全屏,默认全屏
            is_maximize:聊天文件界面是否全屏,默认全屏。
            close_wechat:任务结束后是否关闭微信,默认关闭
        Returns:
            (filelist_window,main_window):filelist_window:聊天文件界面
            main_window:微信主界面,当close_wechat设置为True时main_window为None
        '''
        if window_maximize is None:
            window_maximize=GlobalConfig.window_maximize
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_wechat is None:
            close_wechat=GlobalConfig.close_wechat
        main_window=Navigator.open_wechat(is_maximize=is_maximize)
        moments_button=main_window.child_window(**SideBar.ChatFiles)
        moments_button.click_input()
        desktop=Desktop(**Independent_window.Desktop)
        filelist_window=desktop.window(**Independent_window.ChatFilesWindow)
        if window_maximize:
            filelist_window.maximize()
        if close_wechat:
            main_window.close()
            main_window=None
        return filelist_window,main_window

    @staticmethod
    def open_friend_profile(friend:str,is_maximize:bool=None,search_pages:int=None):
        '''
        该方法用于打开好友个人简介界面
        Args:
            friend:好友备注名称,需提供完整名称
            is_maximize:信界面是否全屏,默认全屏。
            search_pages:在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
        Returns:
            (profile_window,main_window):profile_window:好友设置界面内点击好友头像后的好友个人简介界面
            main_window:微信主界面
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if search_pages is None:
            search_pages=GlobalConfig.search_pages
        friend_settings_window,main_window=Navigator.open_friend_settings(friend=friend,is_maximize=is_maximize,search_pages=search_pages)
        friend_button=friend_settings_window.child_window(title=friend,control_type="Button",found_index=0)
        friend_button.click_input()
        profile_window=friend_settings_window.child_window(**Panes.FriendProfilePane)
        return profile_window,main_window

    @staticmethod
    def open_contacts(is_maximize:bool=None)->WindowSpecification:
        '''
        该方法用于打开微信通信录界面
        Args:
            friend:好友或群聊备注名称,需提供完整名称
            is_maximize:微信界面是否全屏,默认全屏。
        Returns:
            main_window:微信主界面
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        main_window=Navigator.open_wechat(is_maximize=is_maximize)
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
    def open_chat_history(friend:str,TabItem:str=None,search_pages:int=None,is_maximize:bool=None,close_wechat:bool=None):
        '''
        该方法用于打开好友聊天记录界面
        Args:
            friend:好友备注名称,需提供完整名称
            TabItem:点击聊天记录顶部的Tab选项,默认为None,可选值为:文件,图片与视频,链接,音乐与音频,小程序,视频号,日期
            search_pages:在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
            is_maximize:微信界面是否全屏,默认全屏。
            close_wechat:任务结束后是否关闭微信,默认关闭
        Returns:
            (chat_history_window,main_window):chat_history_window:好友设置界面内点击好友头像后的好友个人简介界面
            main_window:微信主界面,当close_wechat设置为True时,main_window为None
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if search_pages is None:
            search_pages=GlobalConfig.search_pages
        if close_wechat is None:
            close_wechat=GlobalConfig.close_wechat
        tabItems={'文件':TabItems.FileTabItem,'图片与视频':TabItems.PhotoAndVideoTabItem,'链接':TabItems.LinkTabItem,'音乐与音频':TabItems.MusicTabItem,'小程序':TabItems.MiniProgramTabItem,'视频号':TabItems.ChannelTabItem,'日期':TabItems.DateTabItem}
        if TabItem:
            if TabItem not in tabItems.keys():
                raise ValueError('TabItem参数错误!')
        main_window=Navigator.open_dialog_window(friend=friend,is_maximize=is_maximize,search_pages=search_pages)[1]
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
            chat_history_window.child_window(**tabItems[TabItem]).click_input()
        return chat_history_window,main_window

    @staticmethod
    def open_program_pane(is_maximize:bool=None,window_maximize:bool=None,close_wechat:bool=None):
        '''
        该方法用来打开小程序面板
        Args:
            is_maximize:微信主界面是否全屏,默认全屏。
            window_maximize:小程序面板主界面是否全屏,默认全屏
            close_wechat:任务结束后是否关闭微信,默认关闭
        Returns:
            (program_window,main_window):program_window:小程序面板
            main_window:微信主界面,当close_wechat设置为True时,main_window为None
        '''
        if window_maximize is None:
            window_maximize=GlobalConfig.window_maximize
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_wechat is None:
            close_wechat=GlobalConfig.close_wechat
        main_window=Navigator.open_wechat(is_maximize=is_maximize)
        program_button=main_window.child_window(**SideBar.Miniprogram_pane)
        program_button.click_input()
        if close_wechat:
            main_window.close()
            main_window=None
        program_window=Tools.move_window_to_center(Independent_window.MiniProgramWindow)
        if window_maximize:
            program_window.maximize()
        return program_window,main_window

    @staticmethod
    def open_top_stories(is_maximize:bool=None,window_maximize:bool=None,close_wechat:bool=None):
        '''
        该方法用于打开看一看
        Args:
            is_maximize:微信界面是否全屏,默认全屏
            wechat_maximize:看一看界面是否全屏,默认全屏
            close_wechat:任务结束后是否关闭微信,默认关闭
        Returns:
            (top_stories_window,main_window):topstories_window:看一看主界面
            main_window:微信主界面,当close_wechat设置为True时,main_window为None
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if window_maximize is None:
            window_maximize-GlobalConfig.window_maximize
        if close_wechat is None:
            close_wechat=GlobalConfig.close_wechat
        main_window=Navigator.open_wechat(is_maximize=is_maximize)
        top_stories_button=main_window.child_window(**SideBar.Topstories)
        top_stories_button.click_input()
        top_stories_window=Tools.move_window_to_center(Independent_window.TopStoriesWindow)
        reload_button=top_stories_window.child_window(**Buttons.ReloadButton)
        reload_button.click_input()
        if window_maximize:
            top_stories_window.maximize()
        if close_wechat:
            main_window.close()
            main_window=None
        return top_stories_window,main_window

    @staticmethod
    def open_search(is_maximize:bool=None,window_maximize:bool=None,close_wechat:bool=None):
        '''
        该方法用于打开搜一搜
        Args:
            is_maximize:微信主界面是否全屏,默认全屏
            window_maximize:搜一搜界面是否全屏,默认全屏
            close_wechat:任务结束后是否关闭微信,默认关闭
        Returns:
            (search_window,main_window):search_window:搜一搜界面
            main_window:微信主界面,当close_wechat设置为True时,main_window为None
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if window_maximize is None:
            window_maximize-GlobalConfig.window_maximize
        if close_wechat is None:
            close_wechat=GlobalConfig.close_wechat
        main_window=Navigator.open_wechat(is_maximize=is_maximize)
        search_button=main_window.child_window(**SideBar.Search)
        search_button.click_input()
        search_window=Tools.move_window_to_center(Independent_window.SearchWindow)
        if window_maximize:
            search_window.maximize()
        if close_wechat:
            main_window.close()
            main_window=None
        return search_window,main_window

    @staticmethod
    def open_channels(is_maximize:bool=None,window_maximize:bool=None,close_wechat:bool=None):
        '''
        该方法用于打开视频号
        Args:
            is_maximize:微信主界面是否全屏,默认全屏。
            wechat_maximize:视频号界面是否全屏,默认全屏
            close_wechat:任务结束后是否关闭微信,默认关闭
        Returns:
            (channel_window,main_window):channel_window:视频号窗口
            main_window:微信主界面,当close_wechat设置为True时返回None
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if window_maximize is None:
            window_maximize-GlobalConfig.window_maximize
        if close_wechat is None:
            close_wechat=GlobalConfig.close_wechat
        main_window=Navigator.open_wechat(is_maximize=is_maximize)
        channel_button=main_window.child_window(**SideBar.Channel)
        channel_button.click_input()
        channel_window=Tools.move_window_to_center(Independent_window.ChannelWindow)
        if window_maximize:
            channel_window.maximize()
        if close_wechat:
            main_window.close()
            main_window=None
        return channel_window,main_window
    
    @staticmethod
    def open_wechat_miniprogram(name:str,load_delay:float=None,is_maximize:bool=None,close_wechat:bool=None):
        '''
        该方法用于打开指定小程序
        Args:
            name:微信小程序名字
            load_delay:搜索小程序名称后等待时长,默认为2.5秒
            is_maximize:微信界面是否全屏,默认全屏。
            close_wechat:任务结束后是否关闭微信,默认关闭
        Returns:
            (program_window,main_window):program_window:小程序主界面
            main_window:微信主界面,当close_wechat设置为True时,main_window为None
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_wechat is None:
            close_wechat=GlobalConfig.close_wechat
        if load_delay is None:
            load_delay=GlobalConfig.load_delay
        up=5
        desktop=Desktop(**Independent_window.Desktop)
        program_window,main_window=Navigator.open_program_pane(is_maximize=is_maximize,close_wechat=close_wechat)
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
        search=program_window.child_window(control_type='Edit',title='搜索小程序')
        while not search.exists():
            mouse.click(coords=(rec.right+20,rec.top-50-up))
            search=program_window.child_window(control_type='Edit',title='搜索小程序')
            up+=5
        search.click_input()
        SystemSettings.copy_text_to_clipboard(name)
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

    @staticmethod
    def open_wechat_traywnd()->WindowSpecification:
        tray_notify=None
        desktop=Desktop(backend='uia')
        #微信的新消息通知托盘的句柄
        #任务栏
        tray_wnd=Navigator.open_traywnd()
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

    @staticmethod
    def open_official_account(name:str,load_delay:float=None,is_maximize:bool=None,close_wechat:bool=None):
        '''
        该方法用于打开指定的微信公众号
        Args:
            name:微信公众号名称
            load_delay:加载搜索公众号结果的时间,单位:s
            is_maximize:微信界面是否全屏,默认全屏。
        Returns:
            (chat_window,main_window):chat_window:与公众号的聊天界面
            main_window:微信主界面,当close_wechat设置为True时返回值为None
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_wechat is None:
            close_wechat=GlobalConfig.close_wechat
        if load_delay is None:
            load_delay=GlobalConfig.load_delay
        desktop=Desktop(**Independent_window.Desktop)
        try:
            search_window,main_window=Navigator.open_search(is_maximize=is_maximize,close_wechat=close_wechat)
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
        SystemSettings.copy_text_to_clipboard(name)
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
    def search_channels(search_content:str,load_delay:float=None,window_maximize:bool=None,is_maximize:bool=None,close_wechat:bool=None):
        '''
        该方法用于打开视频号并搜索指定内容
        Args:
            search_content:在视频号内待搜索内容
            load_delay:加载查询结果的时间,单位:s
            is_maximize:微信界面是否全屏,默认全屏。
        Returns:
            (chat_history_window,main_window):chat_history_window:好友设置界面内点击好友头像后的好友个人简介界面
            main_window:微信主界面,close_wechat设置为True时,main_window为None
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if window_maximize is None:
            window_maximize=GlobalConfig.window_maximize
        if close_wechat is None:
            close_wechat=GlobalConfig.close_wechat
        if load_delay is None:
            load_delay=GlobalConfig.load_delay
        SystemSettings.copy_text_to_clipboard(search_content)
        channel_widow,main_window=Navigator.open_channels(window_maximize=window_maximize,is_maximize=is_maximize,close_wechat=close_wechat)
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
            channel_widow.child_window(control_type='Document',title=f'{search_content}_搜索')
            return channel_widow,main_window
        except ElementNotFoundError:
            channel_widow.close()
            print('网络不良,请尝试增加load_delay时长,或更换网络')
