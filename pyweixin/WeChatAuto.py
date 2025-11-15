'''
WechatAuto
===========


微信4.0版本自动化主模块,实现了绝大多数的自动化功能,包括发送消息,文件,音视频通话

Method:
=======

所有的方法都位于这些静态类内

    - `Messages`: 两种类型的发送消息功能包括:单人发送与多人发送
    - `Files`:  两种类型的发送文件功能包括:单人发送与多人发送
    - `Call`: 给某个好友打视频或语音电话

functions:
=========

    - `dump_sessions`: 导出会话列表中所有聊天对象
    - `dump_recent_sessions`:  导出会话列表中最近的聊天对象
    - ·pull_messages: 从聊天页面中获取一定数量的聊天记录
    - `dump_chat_history`: 导出一定数量的聊天记录

Examples:
=========

使用模块时,你可以:

    >>> from pyweixin.WeChatAuto import Messages
    >>> Messages.send_messages_to_friend()

或者:

    >>> from pyweixin import Messages
    >>> Messages.send_messages_to_friend()

Also:
====
    pyweixin内所有方法及函数的位置参数支持全局设定,be like:
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

#########################################依赖环境#####################################
import os
import re
import time
import pyautogui
from .Config import GlobalConfig
from warnings import warn
from .Warnings import LongTextWarning
from .WeChatTools import Tools,Navigator,mouse
from .WinSettings import Systemsettings
from .Errors import NoFilesToSendError
from .Errors import CantSendEmptyMessageError
from .Errors import WrongParameterError
from .Uielements import (Main_window,SideBar,Independent_window,Buttons,
Edits,Texts,TabItems,Lists,Panes,Windows,CheckBoxes,MenuItems,Menus)
#######################################################################################
Main_window=Main_window()#主界面UI
SideBar=SideBar()#侧边栏UI
Independent_window=Independent_window()#独立主界面UI
Buttons=Buttons()#所有Button类型UI
Edits=Edits()#所有Edit类型UI
Texts=Texts()#所有Text类型UI
TabItems=TabItems()#所有TabIem类型UI
Lists=Lists()#所有列表类型UI
Panes=Panes()#所有Pane类型UI
Windows=Windows()#所有Window类型UI
CheckBoxes=CheckBoxes()#所有CheckBox类型UI
MenuItems=MenuItems()#所有MenuItem类型UI
Menus=Menus()#所有Menu类型UI
pyautogui.FAILSAFE=False#防止鼠标在屏幕边缘处造成的误触


class Messages():
    @staticmethod
    def send_messages_to_friend(friend:str,messages:list[str],send_delay:float=None,is_maximize:bool=None,close_weixin:bool=None):
        '''
        该函数用于给单个好友或群聊发送信息
        Args:
            friend:好友或群聊备注。格式:friend="好友或群聊备注"
            messages:所有待发送消息列表。格式:message=["消息1","消息2"]
            is_maximize:微信界面是否全屏,默认不全屏。
            delay:发送单条消息延迟,单位:秒/s,默认0.2s。
            close_weixin:任务结束后是否关闭微信,默认关闭
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if send_delay is None:
            send_delay=GlobalConfig.send_delay
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if not messages:
            raise CantSendEmptyMessageError
        #先使用open_dialog_window打开对话框
        main_window=Navigator.open_dialog_window(friend=friend,is_maximize=is_maximize)
        for message in messages:
            if len(message)==0:
                main_window.close()
                raise CantSendEmptyMessageError
            if len(message)<2000:
                Systemsettings.copy_text_to_windowsclipboard(message)
                pyautogui.hotkey('ctrl','v',_pause=False)
                time.sleep(send_delay)
                pyautogui.hotkey('alt','s',_pause=False)
            elif len(message)>2000:#字数超过200字发送txt文件
                Systemsettings.convert_long_text_to_txt(message)
                pyautogui.hotkey('ctrl','v',_pause=False)
                time.sleep(send_delay)
                pyautogui.hotkey('alt','s',_pause=False)
                warn(message=f"微信消息字数上限为2000,超过2000字部分将被省略,该条长文本消息已为你转换为txt发送",category=LongTextWarning)
        if close_weixin:
            main_window.close()

    @staticmethod
    def send_messages_to_friends(friends:list[str],messages:list[list[str]],send_delay:float=None,is_maximize:bool=None,close_weixin:bool=None):
        '''
        该函数用于给多个好友或群聊发送信息
        Args:
            friends:好友或群聊备注列表,格式:firends=["好友1","好友2","好友3"]。
            messages:待发送消息,格式: message=[[发给好友1的消息],[发给好友2的消息],[发给好友3的信息]]。
            is_maximize:微信界面是否全屏,默认不全屏。
            send_delay:发送单条消息延迟,单位:秒/s,默认0.2s。
            close_weixin:任务结束后是否关闭微信,默认关闭
        注意!messages与friends长度需一致,并且messages内每一个列表顺序需与friends中好友名称出现顺序一致,否则会出现消息发错的尴尬情况
        '''
        #多个好友的发送任务不需要使用open_dialog_window方法了直接在顶部搜索栏搜索,一个一个打开好友的聊天界面，发送消息,这样最高效
        def get_searh_result(friend,search_result):#查看搜索列表里有没有名为friend的listitem
            contacts=search_result.children(control_type="ListItem")
            texts=[listitem.window_text() for listitem in contacts]
            if '联系人' in texts or '群聊' in texts:
                names=[re.sub(r'[\u2002\u2004\u2005\u2006\u2009]',' ',item.window_text()) for item in contacts]
                if friend in names:#如果在的话就返回整个搜索到的所有联系人,以及其所处的index
                    location=names.index(friend)         
                    return contacts[location]
            return None
        
        def send_messages(friend):
            for message in Chats.get(friend):
                if 0<len(message)<2000:
                    Systemsettings.copy_text_to_windowsclipboard(message)
                    pyautogui.hotkey('ctrl','v',_pause=False)
                    time.sleep(send_delay)
                    pyautogui.hotkey('alt','s',_pause=False)
                if len(message)>2000:
                    Systemsettings.convert_long_text_to_txt(message)
                    pyautogui.hotkey('ctrl','v',_pause=False)
                    time.sleep(send_delay)
                    pyautogui.hotkey('alt','s',_pause=False)
                    warn(message=f"微信消息字数上限为2000,超过2000字部分将被省略,该条长文本消息已为你转换为txt发送",
                    category=LongTextWarning) 
        
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if send_delay is None:
            send_delay=GlobalConfig.send_delay
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        Chats=dict(zip(friends,messages))
        main_window=Navigator.open_weixin(is_maximize=is_maximize)
        rec=main_window.rectangle()
        x,y=rec.right-50,rec.bottom-100
        for friend in Chats:
            search=main_window.descendants(**Main_window.Search)[0]
            search.click_input()
            Systemsettings.copy_text_to_windowsclipboard(friend)
            pyautogui.hotkey('ctrl','v')
            search_results=main_window.child_window(title='',control_type='List').wait(timeout=1)
            friend_button=get_searh_result(friend=friend,search_result=search_results)
            if friend_button:
                friend_button.click_input()
                mouse.click(coords=(x,y))
                send_messages(friend)
        Tools.cancel_pin(main_window)
        if close_weixin:
            main_window.close()


class Files():
    @staticmethod
    def send_files_to_friend(friend:str,files:list[str],with_messages:bool=False,messages:list=[str],messages_first:bool=False,send_delay:float=None,is_maximize:bool=None,close_weixin:bool=None):
        '''
        该方法用于给单个好友或群聊发送多个文件
        Args:
            friend:好友或群聊备注。格式:friend="好友或群聊备注"
            files:所有待发送文件所路径列表。
            with_messages:发送文件时是否给好友发消息。True发送消息,默认为False。
            messages:与文件一同发送的消息。格式:message=["消息1","消息2","消息3"]
            is_maximize:微信界面是否全屏,默认不全屏。
            send_delay:发送单条信息或文件的延迟,单位:秒/s,默认0.2s。
            messages_first:默认先发送文件后发送消息,messages_first设置为True,先发送消息,后发送文件,
            close_weixin:任务结束后是否关闭微信,默认关闭
        '''
        #发送消息逻辑
        def send_messages(messages):
            for message in messages:
                if 0<len(message)<2000:
                    Systemsettings.copy_text_to_windowsclipboard(message)
                    pyautogui.hotkey('ctrl','v',_pause=False)
                    time.sleep(send_delay)
                    pyautogui.hotkey('alt','s',_pause=False)
                if len(message)>2000:
                    Systemsettings.convert_long_text_to_txt(message)
                    pyautogui.hotkey('ctrl','v',_pause=False)
                    time.sleep(send_delay)
                    pyautogui.hotkey('alt','s',_pause=False)
                    warn(message=f"微信消息字数上限为2000,超过2000字部分将被省略,该条长文本消息已为你转换为txt发送",category=LongTextWarning) 
        #发送文件逻辑
        def send_files(files):
            if len(files)<=9:
                Systemsettings.copy_files_to_windowsclipboard(filepaths_list=files)
                pyautogui.hotkey("ctrl","v")
                time.sleep(send_delay)
                pyautogui.hotkey('alt','s',_pause=False)
            else:
                files_num=len(files)
                rem=len(files)%9
                for i in range(0,files_num,9):
                    if i+9<files_num:
                        Systemsettings.copy_files_to_windowsclipboard(filepaths_list=files[i:i+9])
                        pyautogui.hotkey("ctrl","v")
                        time.sleep(send_delay)
                        pyautogui.hotkey('alt','s',_pause=False)
                if rem:
                    Systemsettings.copy_files_to_windowsclipboard(filepaths_list=files[files_num-rem:files_num])
                    pyautogui.hotkey("ctrl","v")
                    time.sleep(send_delay)
                    pyautogui.hotkey('alt','s',_pause=False)
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if send_delay is None:
            send_delay=GlobalConfig.send_delay
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        #对发送文件校验
        if files:            
            files=[file for file in files if os.path.isfile(file)]
            files=[file for file in files if 0<os.path.getsize(file)<1073741824]
        if not files:
            raise NoFilesToSendError
        main_window=Navigator.open_dialog_window(friend=friend,is_maximize=is_maximize)
        if with_messages and messages_first:
            send_messages(messages)
            send_files(files)
        if with_messages and not messages_first:
            send_files(files)
            send_messages(messages)
        if not with_messages:
            send_files(files)       
        if close_weixin:
            main_window.close()

    @staticmethod
    def send_files_to_friends(friends:list[str],files_lists:list[list[str]],with_messages:bool=False,messages_lists:list[list[str]]=[],messages_first:bool=False,send_delay:float=None,is_maximize:bool=None,close_weixin:bool=None):
        '''
        该方法用于给多个好友或群聊发送文件
        Args:
            friends:好友或群聊备注。格式:friends=["好友1","好友2","好友3"]
            folder_paths:待发送文件列表,格式[[一些文件],[另一些文件],...[]]
            with_messages:发送文件时是否给好友发消息。True发送消息,默认为False
            messages_lists:待发送消息列表,格式:message=[[一些消息],[另一些消息]....]
            messages_first:先发送消息还是先发送文件,默认先发送文件
            send_delay:发送单条消息延迟,单位:秒/s,默认0.2s。
            is_maximize:微信界面是否全屏,默认全屏。
            close_weixin:任务结束后是否关闭微信,默认关闭
        注意! messages_lists,files_lists与friends长度需一致且顺序一致,否则会出现发错的尴尬情况
        '''
        def verify(Files):
            verified_files=dict()
            if len(Files)<len(friends):
                raise WrongParameterError(f'friends与files_lists长度不一致!发送人{len(friends)}个,发送文件列表个数{len(Files)}')
            for friend,files in Files.items():         
                files=[file for file in files if os.path.isfile(file)]
                files=[file for file in files if 0<os.path.getsize(file)<1073741824]
                if files:
                    verified_files[friend]=files
                if not files:
                    print(f'发给{friend}的文件列表内没有可发送的文件！')
            return verified_files

        def get_searh_result(friend,search_result):#查看搜索列表里有没有名为friend的listitem
            texts=[listitem.window_text() for listitem in search_result.children(control_type="ListItem")]
            if '联系人' in texts or '群聊' in texts:
                contacts=[item for item in search_result.children(control_type="ListItem")]
                names=[re.sub(r'[\u2002\u2004\u2005\u2006\u2009]',' ',item.window_text()) for item in search_result.children(control_type="ListItem")]
                if friend in names:#如果在的话就返回整个搜索到的所有联系人,以及其所处的index
                    location=names.index(friend)         
                    return contacts[location]
            return None
        
        def open_dialog_window_by_search(friend):
            search=main_window.descendants(**Main_window.Search)[0]
            search.click_input()
            Systemsettings.copy_text_to_windowsclipboard(friend)
            pyautogui.hotkey('ctrl','v')
            search_results=main_window.child_window(**Main_window.SearchResult)
            if search_results.exists(timeout=2,retry_interval=0.1):
                friend_button=get_searh_result(friend=friend,search_result=search_results)
                if friend_button:
                    friend_button.click_input()
                    rec=main_window.rectangle()
                    x,y=rec.right-50,rec.bottom-100
                    mouse.click(coords=(x,y))
                    return True
            return False
        
        #消息发送逻辑
        def send_messages(messages):
            for message in messages:
                if 0<len(message)<2000:
                    Systemsettings.copy_text_to_windowsclipboard(message)
                    pyautogui.hotkey('ctrl','v',_pause=False)
                    time.sleep(send_delay)
                    pyautogui.hotkey('alt','s',_pause=False)
                if len(message)>2000:
                    Systemsettings.convert_long_text_to_txt(message)
                    pyautogui.hotkey('ctrl','v',_pause=False)
                    time.sleep(send_delay)
                    pyautogui.hotkey('alt','s',_pause=False)
                    warn(message=f"微信消息字数上限为2000,超过2000字部分将被省略,该条长文本消息已为你转换为txt发送",category=LongTextWarning) 
        
        #发送文件逻辑，必须9个9个发！
        def send_files(files):
            if len(files)<=9:
                Systemsettings.copy_files_to_windowsclipboard(filepaths_list=files)
                pyautogui.hotkey("ctrl","v")
                time.sleep(send_delay)
                pyautogui.hotkey('alt','s',_pause=False)
            else:
                files_num=len(files)
                rem=len(files)%9#
                for i in range(0,files_num,9):
                    if i+9<files_num:
                        Systemsettings.copy_files_to_windowsclipboard(filepaths_list=files[i:i+9])
                        pyautogui.hotkey("ctrl","v")
                        time.sleep(send_delay)
                        pyautogui.hotkey('alt','s',_pause=False)
                if rem:#余数
                    Systemsettings.copy_files_to_windowsclipboard(filepaths_list=files[files_num-rem:files_num])
                    pyautogui.hotkey("ctrl","v")
                    time.sleep(send_delay)
                    pyautogui.hotkey('alt','s',_pause=False)

        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if send_delay is None:
            send_delay=GlobalConfig.send_delay
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        Files=dict(zip(friends,files_lists))
        Files=verify(Files)
        if not Files:
            raise NoFilesToSendError
        Chats=dict(zip(friends,messages_lists))
        main_window=Navigator.open_weixin(is_maximize=is_maximize)
        chat_button=main_window.child_window(**SideBar.Chats)
        chat_button.click_input()
        if with_messages and messages_lists:#文件消息一起发且message_lists不空
            for friend in Files:
                ret=open_dialog_window_by_search(friend)
                if messages_first and ret:#打开了好友聊天界面,且先发消息
                    messages_to_send=Chats.get(friend)
                    files_to_send=Files.get(friend)
                    send_messages(messages_to_send)
                    send_files(files_to_send)
                if not messages_first and ret:#打开了好友聊天界面,后发消息
                    messages_to_send=Chats.get(friend)
                    files_to_send=Files.get(friend)
                    send_files(files_to_send)
                    send_messages(messages_to_send)
                if not ret:#没有打开好友聊天界面
                    print(f'未能正确打开好友聊天窗口！')
        else:
            for friend in Files:#只发文件
                ret=open_dialog_window_by_search(friend)
                if ret:
                    files_to_send=Files.get(friend)
                    send_files(files_to_send)
                if not ret:
                     print(f'未能正确打开好友聊天窗口！')
        if close_weixin:
            main_window.close()


class Call():
    @staticmethod
    def voice_call(friend:str,is_maximize:bool=None,close_weixin:bool=None):
        '''
        该方法用来给好友拨打语音电话
        Args:
            friend:好友备注
            close_weixin:任务结束后是否关闭微信,默认关闭
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        main_window=Navigator.open_dialog_window(friend=friend,is_maximize=is_maximize)  
        voice_call_button=main_window.child_window(**Buttons.VoiceCallButton).wait(wait_for='ready',timeout=1)
        voice_call_button.click_input()
        if close_weixin:
            main_window.close()

    @staticmethod
    def video_call(friend:str,is_maximize:bool=None,close_weixin:bool=None):
        '''
        该方法用来给好友拨打视频电话
        Args:
            friend:好友备注
            close_weixin:任务结束后是否关闭微信,默认关闭
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        main_window=Navigator.open_dialog_window(friend=friend,is_maximize=is_maximize)  
        video_call_button=main_window.child_window(**Buttons.VideoCallButton).wait(wait_for='ready',timeout=1)
        video_call_button.click_input()
        if close_weixin:
            main_window.close()

def dump_sessions(is_maximize:bool=None,close_weixin:bool=None):

    def remove_duplicates(list):
        """去除列表重复元素，保持顺序"""
        seen=set()
        result=[]
        for item in list:
            if item[0] not in seen:
                seen.add(item[0])
                result.append(item)
        return result
    
    #通过automation_id获取到名字,然后使用正则提取时间,最后把名字与时间去掉便是最后发送消息内容
    def get_name(listitem):
        name=listitem.automation_id().replace('session_item_','')
        return name
    
    def get_sending_time(listitem):
        time=time_pattern.search(listitem.window_text())
        if time:
            return time.group(0)
        else:
            return ''
    def get_latest_message(listitem):
        name=listitem.automation_id().replace('session_item_','')
        res=listitem.window_text().replace(name,'')
        res=time_pattern.sub(repl='',string=res).replace('已置顶 ','')
        return res

    if is_maximize is None:
        is_maximize=GlobalConfig.is_maximize
    if close_weixin is None:
        close_weixin=GlobalConfig.close_weixin
    #匹配位于句子结尾处,开头是空格,格式是2024/05/06或05/06或11:29的日期
    names=[]
    last_sending_times=[]
    lastest_message=[]
    time_pattern=re.compile(r'(?<=\s)(\d{4}/\d{2}/\d{2}|\d{2}/\d{2}|\d{2}:\d{2}|昨天 \d{2}:\d{2})$')
    main_window=Navigator.open_weixin(is_maximize=is_maximize)
    chats_button=main_window.child_window(**SideBar.Chats)
    message_list_pane=main_window.child_window(**Main_window.ConversationList)
    if not message_list_pane.exists():
        chats_button.click_input()
    if not message_list_pane.is_visible():
        chats_button.click_input()
    scrollable=Tools.is_scrollable(message_list_pane)
    if not scrollable:
        names=[get_name(listitem) for listitem in message_list_pane.children(control_type='ListItem')]
        last_sending_times=[get_sending_time(listitem) for listitem in message_list_pane.children(control_type='ListItem')]
        lastest_message=[get_latest_message(listitem) for listitem in message_list_pane.children(control_type='ListItem')]
        results=list(zip(names,last_sending_times,lastest_message))
        results=remove_duplicates(results)
    if scrollable:
        message_list_pane.type_keys('{END}')
        time.sleep(1)
        last=message_list_pane.children(control_type='ListItem')[-1].window_text()
        message_list_pane.type_keys('{HOME}')
        while message_list_pane.children(control_type='ListItem')[-1].window_text()!=last:
            ListItems=list(message_list_pane.children(control_type='ListItem'))
            names.extend([get_name(listitem) for listitem in ListItems])
            last_sending_times.extend([get_sending_time(listitem) for listitem in ListItems])
            lastest_message.extend([get_latest_message(listitem) for listitem in ListItems])
            message_list_pane.type_keys('{PGDN}')
        names.extend([get_name(listitem) for listitem in message_list_pane.children(control_type='ListItem')])
        last_sending_times.extend([get_sending_time(listitem) for listitem in message_list_pane.children(control_type='ListItem')])
        lastest_message.extend([get_latest_message(listitem) for listitem in message_list_pane.children(control_type='ListItem')])
        results=list(zip(names,last_sending_times,lastest_message))
        results=remove_duplicates(results)
    if close_weixin:
        main_window.close()
    return results

def dump_recent_sessions(is_maximize:bool=None,close_weixin:bool=None):

    def remove_duplicates(list):
        """去除列表重复元素，保持顺序"""
        seen=set()
        result=[]
        for item in list:
            if item[0] not in seen:
                seen.add(item[0])
                result.append(item)
        return result
    
    #通过automation_id获取到名字,然后使用正则提取时间,最后把名字与时间去掉便是最后发送消息内容
    def get_name(listitem):
        name=listitem.automation_id().replace('session_item_','')
        return name
    
    def get_sending_time(listitem):
        time=time_pattern.search(listitem.window_text())
        if time:
            return time.group(0)
        else:
            return ''
    def get_latest_message(listitem):
        name=listitem.automation_id().replace('session_item_','')
        res=listitem.window_text().replace(name,'')
        res=time_pattern.sub(repl='',string=res).replace('已置顶 ','')
        return res

    if is_maximize is None:
        is_maximize=GlobalConfig.is_maximize
    if close_weixin is None:
        close_weixin=GlobalConfig.close_weixin
    #匹配位于句子结尾处,开头是空格,格式是2024/05/06或05/06或11:29的日期
    names=[]
    last_sending_times=[]
    lastest_message=[]
    time_pattern=re.compile(r'(?<=\s)(\d{4}/\d{2}/\d{2}|\d{2}/\d{2}|\d{2}:\d{2}|昨天 \d{2}:\d{2})$')
    main_window=Navigator.open_weixin(is_maximize=is_maximize)
    chats_button=main_window.child_window(**SideBar.Chats)
    message_list_pane=main_window.child_window(**Main_window.ConversationList)
    if not message_list_pane.exists():
        chats_button.click_input()
    if not message_list_pane.is_visible():
        chats_button.click_input()
    scrollable=Tools.is_scrollable(message_list_pane)
    if not scrollable:
        names=[get_name(listitem) for listitem in message_list_pane.children(control_type='ListItem')]
        last_sending_times=[get_sending_time(listitem) for listitem in message_list_pane.children(control_type='ListItem')]
        lastest_message=[get_latest_message(listitem) for listitem in message_list_pane.children(control_type='ListItem')]
        results=list(zip(names,last_sending_times,lastest_message))
        results=remove_duplicates(results)
    if scrollable:
        message_list_pane.type_keys('{END}')
        time.sleep(1)
        last=message_list_pane.children(control_type='ListItem')[-1].window_text()
        message_list_pane.type_keys('{HOME}')
        while message_list_pane.children(control_type='ListItem')[-1].window_text()!=last:
            ListItems=list(message_list_pane.children(control_type='ListItem'))
            names.extend([get_name(listitem) for listitem in ListItems])
            last_sending_times.extend([get_sending_time(listitem) for listitem in ListItems])
            lastest_message.extend([get_latest_message(listitem) for listitem in ListItems])
            message_list_pane.type_keys('{PGDN}')
        names.extend([get_name(listitem) for listitem in message_list_pane.children(control_type='ListItem')])
        last_sending_times.extend([get_sending_time(listitem) for listitem in message_list_pane.children(control_type='ListItem')])
        lastest_message.extend([get_latest_message(listitem) for listitem in message_list_pane.children(control_type='ListItem')])
        results=list(zip(names,last_sending_times,lastest_message))
        results=remove_duplicates(results)
    if close_weixin:
        main_window.close()
    return results

def dump_chat_history(friend:str,number:int,is_maximize:bool=None,close_weixin:bool=None)->tuple[list,list]:
    '''该函数用来获取一定数量的聊天记录
    Args:
        friend:好友名称
        number:获取的消息数量
        is_maximize:微信界面是否全屏，默认全屏
        close_weixin:任务结束后是否关闭微信，默认关闭
    Returns:
        messages:发送的消息(时间顺序从早到晚)
        timestamps:每条消息对应的发送时间
    '''
    if is_maximize is None:
        is_maximize=GlobalConfig.is_maximize
    if close_weixin is None:
        close_weixin=GlobalConfig.close_weixin
    messages=[]
    timestamp_pattern=re.compile(r'(?<=\s)(\d{4}年\d{2}月\d{2}日 \d{2}:\d{2}|\d{2}月\d{2}日 \d{2}:\d{2}|\d{2}:\d{2}|昨天 \d{2}:\d{2}|星期\w \d{2}:\d{2})$')
    chat_history_window=Navigator.open_chat_history(friend=friend,is_maximize=is_maximize,close_weixin=close_weixin)
    chat_list=chat_history_window.child_window(**Lists.ChatHistoryList)
    scrollable=Tools.is_scrollable(chat_list)
    if not chat_list.children(control_type='ListItem'):
        warn(message=f"你与{friend}的聊天记录为空,无法获取聊天记录",category=NoChatHistoryWarning)
    if not scrollable: 
        ListItems=chat_list.children(control_type='ListItem')
        messages=[listitem.window_text() for listitem in ListItems if listitem.class_name!='mmui::ChatItemView']  
    if scrollable:
        while len(messages)<number:
            ListItems=chat_list.children(control_type='ListItem')
            messages.extend([listitem.window_text() for listitem in ListItems])
            chat_list.type_keys('{PGDN}')
        chat_list.type_keys('{HOME}')
    messages=messages[:number][::-1]
    timestamps=[timestamp_pattern.search(message).group(0) for message in messages]
    messages=[timestamp_pattern.sub('',message) for message in messages]
    chat_history_window.close()
    return messages,timestamps

def pull_messages(friend:str,number:int,is_maximize:bool=None,close_weixin:bool=None):
    '''
    该函数用来从聊天界面获取聊天消息,也可当做获取聊天记录
    Args:
        friend:好友名称
        number:获取的消息数量
        is_maximize:微信界面是否全屏，默认全屏
        close_weixin:任务结束后是否关闭微信，默认关闭
    Returns:
        messages:聊天记录中的消息(时间顺序从早到晚)
    '''
    if is_maximize is None:
        is_maximize=GlobalConfig.is_maximize
    if close_weixin is None:
        close_weixin=GlobalConfig.close_weixin
    messages=[]
    main_window=Navigator.open_dialog_window(friend=friend,is_maximize=is_maximize,close_weixin=close_weixin)
    chat_list=main_window.child_window(**Lists.FriendChatList)
    scrollable=Tools.is_scrollable(chat_list,back='end')
    if not chat_list.children(control_type='ListItem'):
        warn(message=f"你与{friend}的聊天记录为空,无法获取聊天记录",category=NoChatHistoryWarning)
    if not scrollable:
        ListItems=chat_list.children(control_type='ListItem')
        messages=[listitem.window_text() for listitem in ListItems if listitem.class_name!='mmui::ChatItemView']
    if scrollable:
        while len(messages)<number:
            ListItems=chat_list.children(control_type='ListItem')[::-1]
            messages.extend([listitem.window_text() for listitem in ListItems])
            chat_list.type_keys('{PGUP}')
        chat_list.type_keys('{END}')
    if close_weixin:
        main_window.close()
    return messages[::-1]
