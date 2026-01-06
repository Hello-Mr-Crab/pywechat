'''
WechatAuto
===========


微信4.0版本自动化主模块,实现了绝大多数的自动化功能,包括发送消息,文件,音视频通话等
所有的方法都位于这些静态类内,导入后使用XX.yy的方式使用即可

    - `Messages`: 关于微信消息的一些方法,包括收发消息,获取聊天记录,获取聊天会话等功能
    - `Files`:  关于微信文件的一些方法,包括发送文件,导出文件等功能
    - `Call`: 给某个好友打视频或语音电话
    - `Moments`: 与朋友圈相关的一些方法(开发ing...)
    - `Collections`: 与收藏相关的一些方法(开发ing...)
    - `Settings`: 与微信设置相关的一些方法,更换主题,更换语言等(开发ing...)
    - `FriendSettings`: 与好友设置相关的一些方法(开发ing..)

Examples:
=========

使用模块时,你可以:

    >>> from pyweixin.WeChatAuto import Messages
    >>> Messages.scan_for_new_messages()

或者:

    >>> from pyweixin import Messages
    >>> Messages.scan_for_new_messages()

Also:
====
    pyweixin内所有方法及函数的位置参数支持全局设定,be like:
    ```
        from pyweixin import Navigator,GlobalConfig
        GlobalConfig.load_delay=2.5
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
import json
import pyautogui
from typing import Literal
from .Config import GlobalConfig
from warnings import warn
from .Warnings import LongTextWarning,NoChatHistoryWarning
from .WeChatTools import Tools,Navigator,mouse,Desktop
from .WinSettings import SystemSettings
from .Errors import NoFilesToSendError
from .Errors import CantSendEmptyMessageError
from .Errors import WrongParameterError
from .Errors import NotFolderError
from .Uielements import (Main_window,SideBar,Independent_window,Buttons,
Edits,Texts,TabItems,Lists,Panes,Windows,CheckBoxes,MenuItems,Menus,Groups,Customs,ListItems)
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
Groups=Groups()#所有Group类型UI
Customs=Customs()#所有Custom类型UI
ListItems=ListItems()#所有ListItems类型UI
pyautogui.FAILSAFE=False#防止鼠标在屏幕边缘处造成的误触


class Messages():
    @staticmethod
    def send_messages_to_friend(friend:str,messages:list[str],clear:bool=None,
        send_delay:float=None,is_maximize:bool=None,close_weixin:bool=None)->None:
        '''
        该函数用于给单个好友或群聊发送信息
        Args:
            friend:好友或群聊备注。格式:friend="好友或群聊备注"
            messages:所有待发送消息列表。格式:message=["消息1","消息2"]
            send_delay:发送单条消息延迟,单位:秒/s,默认0.2s。
            clear:是否删除编辑区域已有的内容,默认删除
            is_maximize:微信界面是否全屏,默认不全屏。
            close_weixin:任务结束后是否关闭微信,默认关闭
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if send_delay is None:
            send_delay=GlobalConfig.send_delay
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if clear is None:
            clear=GlobalConfig.clear
        if not messages:
            raise CantSendEmptyMessageError
        #先使用open_dialog_window打开对话框
        main_window=Navigator.open_dialog_window(friend=friend,is_maximize=is_maximize)
        if clear:
            pyautogui.hotkey('ctrl','a',_pause=False)
            pyautogui.hotkey('backspace',_pause=False)
        for message in messages:
            if len(message)==0:
                main_window.close()
                raise CantSendEmptyMessageError
            if len(message)<2000:
                SystemSettings.copy_text_to_windowsclipboard(message)
                pyautogui.hotkey('ctrl','v',_pause=False)
                time.sleep(send_delay)
                pyautogui.hotkey('alt','s',_pause=False)
            elif len(message)>2000:#字数超过200字发送txt文件
                SystemSettings.convert_long_text_to_txt(message)
                pyautogui.hotkey('ctrl','v',_pause=False)
                time.sleep(send_delay)
                pyautogui.hotkey('alt','s',_pause=False)
                warn(message=f"微信消息字数上限为2000,超过2000字部分将被省略,该条长文本消息已为你转换为txt发送",category=LongTextWarning)
        if close_weixin:
            main_window.close()

    @staticmethod
    def send_messages_to_friends(friends:list[str],messages:list[list[str]],clear:bool=None,
        send_delay:float=None,is_maximize:bool=None,close_weixin:bool=None)->None:
        '''
        该函数用于给多个好友或群聊发送信息
        Args:
            friends:好友或群聊备注列表,格式:firends=["好友1","好友2","好友3"]。
            messages:待发送消息,格式: message=[[发给好友1的消息],[发给好友2的消息],[发给好友3的信息]]。
            clear:是否删除编辑区域已有的内容,默认删除。
            send_delay:发送单条消息延迟,单位:秒/s,默认0.2s。
            is_maximize:微信界面是否全屏,默认不全屏。
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
            if clear:
                pyautogui.hotkey('ctrl','a',_pause=False)
                pyautogui.hotkey('backspace',_pause=False)
            for message in Chats.get(friend):
                if 0<len(message)<2000:
                    SystemSettings.copy_text_to_windowsclipboard(message)
                    pyautogui.hotkey('ctrl','v',_pause=False)
                    time.sleep(send_delay)
                    pyautogui.hotkey('alt','s',_pause=False)
                if len(message)>2000:
                    SystemSettings.convert_long_text_to_txt(message)
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
        if clear is None:
            clear=GlobalConfig.clear
        Chats=dict(zip(friends,messages))
        main_window=Navigator.open_weixin(is_maximize=is_maximize)
        rec=main_window.rectangle()
        x,y=rec.right-50,rec.bottom-100
        for friend in Chats:
            search=main_window.descendants(**Main_window.Search)[0]
            search.click_input()
            SystemSettings.copy_text_to_windowsclipboard(friend)
            pyautogui.hotkey('ctrl','v')
            time.sleep(1)
            search_results=main_window.child_window(title='',control_type='List')
            friend_button=get_searh_result(friend=friend,search_result=search_results)
            if friend_button:
                friend_button.click_input()
                mouse.click(coords=(x,y))
                send_messages(friend)
        Tools.cancel_pin(main_window)
        if close_weixin:
            main_window.close()
    
    @staticmethod
    def dump_recent_sessions(recent:Literal['Today','Yesterday','Week','Month','Year']='Today',
        chat_only:bool=False,is_maximize:bool=None,close_weixin:bool=None)->list[tuple]:
        '''
        该函数用来获取会话列表内最近的聊天对象的名称,最后聊天时间,以及最后一条聊天消息,使用时建议全屏这样不会有遗漏!
        Args:
            recent:获取最近消息的时间节点,可选值为'Today','Yesterday','Week','Month','Year'分别获取当天,昨天,本周,本月,本年
            chat_only:只获取会话列表中有消息的好友(ListItem底部有灰色消息不是空白),默认为False
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        Returns:
            sessions:[('发送人','最后聊天时间','最后聊天内容')]
        '''
        #去除列表重复元素
        def remove_duplicates(list):
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
        
        #正则匹配获取时间
        def get_sending_time(listitem):
            timestamp=timestamp_pattern.search(listitem.window_text().replace('消息免打扰 ',''))
            if timestamp:
                return timestamp.group(0)
            else:
                return ''

        #获取最后一条消息内容
        def get_latest_message(listitem):
            name=listitem.automation_id().replace('session_item_','')
            res=listitem.window_text().replace(name,'')
            res=timestamp_pattern.sub(repl='',string=res).replace('已置顶 ','').replace('消息免打扰','')
            return res
        
        #根据recent筛选和过滤会话
        def filter_sessions(ListItems):
            ListItems=[ListItem for ListItem in ListItems if get_sending_time(ListItem)]
            if recent=='Year' or recent=='Month':
                ListItems=[ListItem for ListItem in ListItems if lastyear not in get_sending_time(ListItem)]
            if recent=='Week':
                ListItems=[ListItem for ListItem in ListItems if '/' not in get_sending_time(ListItem)]
            if recent=='Today' or recent=='Yesterday':
                ListItems=[ListItem for ListItem in ListItems if ':' in get_sending_time(ListItem)]
            if chat_only:
                ListItems=[ListItem for ListItem in ListItems if get_latest_message(ListItem)!='']
            return ListItems
        
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin

        #匹配位于句子结尾处,开头是空格,格式是2024/05/06或05/06或11:29的日期
        sessions=[]#会话对象 ListItem
        names=[]#会话名称
        last_sending_times=[]#最后聊天时间,最右侧的时间戳
        lastest_message=[]
        lastyear=str(int(time.strftime('%y'))-1)+'/'#去年
        thismonth=str(int(time.strftime('%m')))+'/'#去年
        yesterday='昨天'
        #最右侧时间戳正则表达式:五种,2024/05/01,10/25,昨天,星期一,10:59,
        timestamp_pattern=re.compile(r'(?<=\s)(\d{4}/\d{2}/\d{2}|\d{2}/\d{2}|\d{2}:\d{2}|昨天 \d{2}:\d{2}|星期\w)$')
        main_window=Navigator.open_weixin(is_maximize=is_maximize)
        chats_button=main_window.child_window(**SideBar.Chats)
        message_list_pane=main_window.child_window(**Main_window.ConversationList)
        if not message_list_pane.exists():
            chats_button.click_input()
        if not message_list_pane.is_visible():
            chats_button.click_input()
        scrollable=Tools.is_scrollable(message_list_pane,back='end')
        if not scrollable:
            listItems=message_list_pane.children(control_type='ListItem')
            listItems=filter_sessions(listItems)
            names.extend([get_name(listitem) for listitem in listItems])
            last_sending_times.extend([get_sending_time(listitem) for listitem in listItems])
            lastest_message.extend([get_latest_message(listitem)for listitem in listItems])
        if scrollable:
            last=message_list_pane.children(control_type='ListItem')[-1].window_text()
            message_list_pane.type_keys('{HOME}')
            time.sleep(1)
            while True:
                listItems=message_list_pane.children(**ListItems.SessionLitItem)
                listItems=filter_sessions(listItems)
                if not listItems:
                    break
                if listItems[-1].window_text()==last:
                    break
                names.extend([get_name(listitem) for listitem in listItems])
                last_sending_times.extend([get_sending_time(listitem) for listitem in listItems])
                lastest_message.extend([get_latest_message(listitem)for listitem in listItems])
                message_list_pane.type_keys('{PGDN}') 
            message_list_pane.type_keys('{HOME}')
        #list zip为[(发送人,发送时间,最后一条消息)]
        sessions=list(zip(names,last_sending_times,lastest_message))
        #去重
        sessions=remove_duplicates(sessions)
        if close_weixin:
            main_window.close()
        #进一步筛选
        if recent=='Yesterday':
            sessions=[session for session in sessions if yesterday in session[1]]
        if recent=='Today':
            sessions=[session for session in sessions if yesterday not in session[1]]
        if recent=='Month':
            weeek_sessions=[session for session in sessions if '/' not  in session[1]]
            month_sessions=[session for session in sessions if thismonth in session[1]]
            sessions=weeek_sessions+month_sessions
        return sessions

    @staticmethod
    def dump_sessions(chat_only:bool=False,is_maximize:bool=None,close_weixin:bool=None)->list[tuple]:
        '''
        该函数用来获取会话列表内所有聊天对象的名称,最后聊天时间,以及最后一条聊天消息,使用时建议全屏这样不会有遗漏!
        Args:
            chat_only:只获取会话列表中有消息的好友(ListItem底部有灰色消息不是空白),默认为False
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        Returns:
            sessions:[('发送人','最后聊天时间','最后聊天内容')]
        '''
        def filter_sessions(ListItems):
            ListItems=[ListItem for ListItem in ListItems if get_sending_time(ListItem)]
            if chat_only:
                ListItems=[ListItem for ListItem in ListItems if get_latest_message(ListItem)!='']
            return ListItems
        
        def remove_duplicates(list):
            """去除列表重复元素"""
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
        
        #正则匹配获取时间
        def get_sending_time(listitem):
            timestamp=timestamp_pattern.search(listitem.window_text().replace('消息免打扰 ',''))
            if timestamp:
                return timestamp.group(0)
            else:
                return ''

        #获取最后一条消息内容
        def get_latest_message(listitem):
            name=listitem.automation_id().replace('session_item_','')
            res=listitem.window_text().replace(name,'')
            res=timestamp_pattern.sub(repl='',string=res).replace('已置顶 ','').replace('消息免打扰','')
            return res
        
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
    
        names=[]
        last_sending_times=[]
        lastest_message=[]
        #最右侧时间戳正则表达式:五种,2024/05/01,10/25,昨天,星期一,10:59,
        timestamp_pattern=re.compile(r'(?<=\s)(\d{4}/\d{2}/\d{2}|\d{2}/\d{2}|\d{2}:\d{2}|昨天 \d{2}:\d{2}|星期\w)$')
        main_window=Navigator.open_weixin(is_maximize=is_maximize)
        chats_button=main_window.child_window(**SideBar.Chats)
        message_list_pane=main_window.child_window(**Main_window.ConversationList)
        if not message_list_pane.exists():
            chats_button.click_input()
        if not message_list_pane.is_visible():
            chats_button.click_input()
        scrollable=Tools.is_scrollable(message_list_pane,back='end')
        if not scrollable:
            names=[get_name(listitem) for listitem in message_list_pane.children(control_type='ListItem')]
            last_sending_times=[get_sending_time(listitem) for listitem in message_list_pane.children(control_type='ListItem')]
            lastest_message=[get_latest_message(listitem) for listitem in message_list_pane.children(control_type='ListItem')]
        if scrollable:
            time.sleep(1)
            last=message_list_pane.children(control_type='ListItem')[-1].window_text()
            message_list_pane.type_keys('{HOME}')
            while True:
                listItems=message_list_pane.children(**ListItems.SessionLitItem)
                listItems=filter_sessions(ListItems)
                names.extend([get_name(listitem) for listitem in listItems])
                last_sending_times.extend([get_sending_time(listitem) for listitem in listItems])
                lastest_message.extend([get_latest_message(listitem) for listitem in listItems])
                message_list_pane.type_keys('{PGDN}')
                if listItems[-1].window_text()==last:
                    break
            names.extend([get_name(listitem) for listitem in message_list_pane.children(control_type='ListItem')])
            last_sending_times.extend([get_sending_time(listitem) for listitem in message_list_pane.children(control_type='ListItem')])
            lastest_message.extend([get_latest_message(listitem) for listitem in message_list_pane.children(control_type='ListItem')])
            message_list_pane.type_keys('{HOME}')
        if close_weixin:
            main_window.close()
        #list zip为[(发送人,发送时间,最后一条消息)]
        sessions=list(zip(names,last_sending_times,lastest_message))
        #去重
        sessions=remove_duplicates(sessions)
        return sessions

    @staticmethod
    def dump_chat_history(friend:str,number:int,is_maximize:bool=None,close_weixin:bool=None)->tuple[list,list]:
        '''该函数用来获取一定的聊天记录
        Args:
            friend:好友名称
            number:获取的消息数量
            is_maximize:微信界面是否全屏，默认不全屏
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
            messages=[listitem.window_text() for listitem in ListItems if listitem.class_name()!="mmui::ChatItemView"]  
        if scrollable:
            while len(messages)<number:
                ListItems=chat_list.children(control_type='ListItem')
                ListItems=[listitem for listitem in ListItems if listitem.class_name()!="mmui::ChatItemView"]  
                messages.extend([listitem.window_text() for listitem in ListItems])
                chat_list.type_keys('{PGDN}')
            chat_list.type_keys('{HOME}')
        chat_history_window.close()
        messages=messages[:number][::-1]
        timestamps=[timestamp_pattern.search(message).group(0) for message in messages]
        messages=[timestamp_pattern.sub('',message) for message in messages]
        return messages,timestamps

    @staticmethod
    def pull_messages(friend:str,number:int,is_maximize:bool=None,close_weixin:bool=None)->list[str]:
        '''
        该函数用来从聊天界面获取聊天消息,也可当做获取聊天记录
        Args:
            friend:好友名称
            number:获取的消息数量
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        Returns:
            messages:聊天记录中的消息(时间顺序从早到晚)
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        messages=[]
        main_window=Navigator.open_dialog_window(friend=friend,is_maximize=is_maximize)
        chat_list=main_window.child_window(**Lists.FriendChatList)
        scrollable=Tools.is_scrollable(chat_list,back='end')
        if not chat_list.children(control_type='ListItem'):
            warn(message=f"你与{friend}的聊天记录为空,无法获取聊天记录",category=NoChatHistoryWarning)
        if not scrollable:
            ListItems=chat_list.children(control_type='ListItem')
            ListItems=[listitem for listitem in ListItems if listitem.class_name()!="mmui::ChatItemView"]
            messages=[listitem.window_text() for listitem in ListItems]
        if scrollable:
            while len(messages)<number:
                ListItems=chat_list.children(control_type='ListItem')[::-1]
                ListItems=[listitem for listitem in ListItems if listitem.class_name()!="mmui::ChatItemView"]
                messages.extend([listitem.window_text() for listitem in ListItems])
                chat_list.type_keys('{PGUP}')
            chat_list.type_keys('{END}')
        if close_weixin:
            main_window.close()
        messages=messages[::-1][-number:]
        return messages
    
    @staticmethod
    def get_new_message_num(is_maximize:bool=None,close_weixin:bool=None):
        '''
        该函数用来获取侧边栏左侧微信按钮上的红色新消息总数
        Args:
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        Returns:
            new_message_num:新消息总数
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        main_window=Navigator.open_weixin(is_maximize=is_maximize)
        chats_button=main_window.child_window(**SideBar.Chats)
        chats_button.click_input()
        #左上角微信按钮的红色消息提示(\d+条新消息)在FullDescription属性中,
        #只能通过id来获取,id是30159，之前是30007,可能是qt组件映射关系不一样
        full_desc=chats_button.element_info.element.GetCurrentPropertyValue(30159)
        new_message_num=re.search(r'\d+',full_desc)#正则提取数量
        if close_weixin:
            main_window.close()
        if new_message_num:
            return int(new_message_num.group(0))
        else:
            return 0

    @staticmethod
    def scan_for_new_messages(is_maximize:bool=None,close_weixin:bool=None)->dict:
        '''
        该函数用来扫描检查一遍消息列表中的所有新消息,返回发送对象以及新消息数量(不包括免打扰)
        Args:
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        Returns:
            newMessages:有新消息的好友备注及其对应的新消息数量构成的字典
        '''

        def traverse_messsage_list(listItems):
            #newMessageTips为newMessagefriends中每个元素的文本:['测试365 5条新消息','一家人已置顶20条新消息']这样的字符串列表
            listItems=[listItem for listItem in listItems if '条未读' in listItem.window_text()]
            listItems=[listItem for listItem in listItems if '公众号' not in listItem.window_text()]
            listItems=[listItem for listItem in listItems if '服务号' not in listItem.window_text()]
            listItems=[listItem for listItem in listItems if '消息免打扰' not in listItem.window_text()]
            senders=[listItem.automation_id().replace('session_item_','') for listItem in listItems]
            newMessageTips=[listItem.window_text() for listItem in listItems]
            newMessageTips=list(dict.fromkeys(newMessageTips))
            newMessageNum=[int(new_message_pattern.search(text).group(1)) for text in newMessageTips]
            return senders,newMessageNum
    
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        
        newMessageSenders=[]
        newMessageNums=[]
        main_window=Navigator.open_weixin(is_maximize=is_maximize)
        chats_button=main_window.child_window(**SideBar.Chats)
        chats_button.click_input()
        #左上角微信按钮的红色消息提示(\d+条新消息)在FullDescription属性中,
        #只能通过id来获取,id是30159，之前是30007,可能是qt组件映射关系不一样
        full_desc=chats_button.element_info.element.GetCurrentPropertyValue(30159)
        message_list_pane=main_window.child_window(**Main_window.ConversationList)
        message_list_pane.type_keys('{HOME}')
        new_message_num=re.search(r'\d+',full_desc)#正则提取数量
        #微信会话列表内ListItem标准格式:备注\s(已置顶)\s(\d+)条未读\s最后一条消息内容\s时间
        new_message_pattern=re.compile(r'\s(\d+)条未读\s')#只给数量分组,.group(1)获取
        if not new_message_num:
            print(f'没有新消息')
            return [],[]
        if new_message_num:
            new_message_num=int(new_message_num.group(0))
            message_list=main_window.child_window(**Main_window.ConversationList)
        while sum(newMessageNums)<new_message_num:#当最终的新消息总数之和比
            #遍历获取带有新消息的ListItem
            listItems=message_list.children(control_type='ListItem')
            senders,nums=traverse_messsage_list(listItems)
            #提取姓名和数量
            if senders not in newMessageSenders:#避免重复
                newMessageNums.extend(nums)
                newMessageSenders.extend(senders)
            message_list.type_keys('{PGDN}')
        message_list.type_keys('{HOME}')
        newMessages=dict(zip(newMessageSenders,newMessageNums))
        if close_weixin:
            main_window.close()
        return newMessages

class Files():
    @staticmethod
    def send_files_to_friend(friend:str,files:list[str],with_messages:bool=False,messages:list=[str],messages_first:bool=False,
        send_delay:float=None,clear:bool=None,is_maximize:bool=None,close_weixin:bool=None)->None:
        '''
        该方法用于给单个好友或群聊发送多个文件
        Args:
            friend:好友或群聊备注。格式:friend="好友或群聊备注"
            files:所有待发送文件所路径列表。
            with_messages:发送文件时是否给好友发消息。True发送消息,默认为False。
            messages:与文件一同发送的消息。格式:message=["消息1","消息2","消息3"]
            clear:是否删除编辑区域已有的内容,默认删除。
            send_delay:发送单条信息或文件的延迟,单位:秒/s,默认0.2s。
            is_maximize:微信界面是否全屏,默认不全屏。
            messages_first:默认先发送文件后发送消息,messages_first设置为True,先发送消息,后发送文件,
            close_weixin:任务结束后是否关闭微信,默认关闭
        '''
        #发送消息逻辑
        def send_messages(messages):
            for message in messages:
                if 0<len(message)<2000:
                    SystemSettings.copy_text_to_windowsclipboard(message)
                    pyautogui.hotkey('ctrl','v',_pause=False)
                    time.sleep(send_delay)
                    pyautogui.hotkey('alt','s',_pause=False)
                if len(message)>2000:
                    SystemSettings.convert_long_text_to_txt(message)
                    pyautogui.hotkey('ctrl','v',_pause=False)
                    time.sleep(send_delay)
                    pyautogui.hotkey('alt','s',_pause=False)
                    warn(message=f"微信消息字数上限为2000,超过2000字部分将被省略,该条长文本消息已为你转换为txt发送",category=LongTextWarning) 
        #发送文件逻辑
        def send_files(files):
            if len(files)<=9:
                SystemSettings.copy_files_to_windowsclipboard(filepaths_list=files)
                pyautogui.hotkey("ctrl","v")
                time.sleep(send_delay)
                pyautogui.hotkey('alt','s',_pause=False)
            else:
                files_num=len(files)
                rem=len(files)%9
                for i in range(0,files_num,9):
                    if i+9<files_num:
                        SystemSettings.copy_files_to_windowsclipboard(filepaths_list=files[i:i+9])
                        pyautogui.hotkey("ctrl","v")
                        time.sleep(send_delay)
                        pyautogui.hotkey('alt','s',_pause=False)
                if rem:
                    SystemSettings.copy_files_to_windowsclipboard(filepaths_list=files[files_num-rem:files_num])
                    pyautogui.hotkey("ctrl","v")
                    time.sleep(send_delay)
                    pyautogui.hotkey('alt','s',_pause=False)
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if send_delay is None:
            send_delay=GlobalConfig.send_delay
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if clear is None:
            clear=GlobalConfig.clear
        #对发送文件校验
        if files:            
            files=[file for file in files if os.path.isfile(file)]
            files=[file for file in files if 0<os.path.getsize(file)<1073741824]
        if not files:
            raise NoFilesToSendError
        main_window=Navigator.open_dialog_window(friend=friend,is_maximize=is_maximize)
        if clear:
            pyautogui.hotkey('ctrl','a',_pause=False)
            pyautogui.hotkey('backspace',_pause=False)
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
    def send_files_to_friends(friends:list[str],files_lists:list[list[str]],
        with_messages:bool=False,messages_lists:list[list[str]]=[],messages_first:bool=False,
        clear:bool=None,send_delay:float=None,is_maximize:bool=None,close_weixin:bool=None)->None:
        '''
        该方法用于给多个好友或群聊发送文件
        Args:
            friends:好友或群聊备注。格式:friends=["好友1","好友2","好友3"]
            folder_paths:待发送文件列表,格式[[一些文件],[另一些文件],...[]]
            with_messages:发送文件时是否给好友发消息。True发送消息,默认为False
            messages_lists:待发送消息列表,格式:message=[[一些消息],[另一些消息]....]
            messages_first:先发送消息还是先发送文件,默认先发送文件
            clear:是否删除编辑区域已有的内容,默认删除。
            send_delay:发送单条消息延迟,单位:秒/s,默认0.2s。
            is_maximize:微信界面是否全屏,默认不全屏。
            close_weixin:任务结束后是否关闭微信,默认关闭
        注意! messages_lists,files_lists与friends长度需一致且顺序一致,否则会出现发错的尴尬情况
        '''
        def verify(Files):
            verified_files=dict()
            if len(Files)<len(friends):
                raise WrongParameterError(f'friends与files_lists长度不一致!发送人{len(friends)}个,发送文件列表个数{len(Files)}')
            for friend,files in Files.items():         
                files=[file for file in files if os.path.isfile(file)]
                files=[file for file in files if 0<os.path.getsize(file)<1073741824]#文件大小不能超过1个G!
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
            SystemSettings.copy_text_to_windowsclipboard(friend)
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
                    SystemSettings.copy_text_to_windowsclipboard(message)
                    pyautogui.hotkey('ctrl','v',_pause=False)
                    time.sleep(send_delay)
                    pyautogui.hotkey('alt','s',_pause=False)
                if len(message)>2000:
                    SystemSettings.convert_long_text_to_txt(message)
                    pyautogui.hotkey('ctrl','v',_pause=False)
                    time.sleep(send_delay)
                    pyautogui.hotkey('alt','s',_pause=False)
                    warn(message=f"微信消息字数上限为2000,超过2000字部分将被省略,该条长文本消息已为你转换为txt发送",category=LongTextWarning) 
        
        #发送文件逻辑，必须9个9个发！
        def send_files(files):
            if len(files)<=9:
                SystemSettings.copy_files_to_windowsclipboard(filepaths_list=files)
                pyautogui.hotkey("ctrl","v")
                time.sleep(send_delay)
                pyautogui.hotkey('alt','s',_pause=False)
            else:
                files_num=len(files)
                rem=len(files)%9#
                for i in range(0,files_num,9):
                    if i+9<files_num:
                        SystemSettings.copy_files_to_windowsclipboard(filepaths_list=files[i:i+9])
                        pyautogui.hotkey("ctrl","v")
                        time.sleep(send_delay)
                        pyautogui.hotkey('alt','s',_pause=False)
                if rem:#余数
                    SystemSettings.copy_files_to_windowsclipboard(filepaths_list=files[files_num-rem:files_num])
                    pyautogui.hotkey("ctrl","v")
                    time.sleep(send_delay)
                    pyautogui.hotkey('alt','s',_pause=False)

        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if send_delay is None:
            send_delay=GlobalConfig.send_delay
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if clear is None:
            clear=GlobalConfig.clear
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
                if clear:
                    pyautogui.hotkey('ctrl','a',_pause=False)
                    pyautogui.hotkey('backspace',_pause=False)
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
                if clear:
                    pyautogui.hotkey('ctrl','a',_pause=False)
                    pyautogui.hotkey('backspace',_pause=False)
                if ret:
                    files_to_send=Files.get(friend)
                    send_files(files_to_send)
                if not ret:
                     print(f'未能正确打开好友聊天窗口！')
        if close_weixin:
            main_window.close()
    @staticmethod
    def export_chatfiles():
        '''该方法用来导出与某个好友的聊天文件'''
        pass

    @staticmethod
    def export_videos(year:str=time.strftime('%Y'),month:str=None,target_folder:str=None)->list[str]:
        '''
        该函数用来导出微信保存到本地的聊天视频
        Args:
            year:年份,除非手动删除聊天视频否则一直保存,格式:YYYY:2025,2024
            month:月份,微信聊天视屏是按照xxxx年-xx月分批存储的格式:XX:05,11
            target_folder:导出的聊天视频保存的位置,需要是文件夹
        Returns:
            exported_videos:导出的mp4视频路径列表
        '''
        folder_name=f'{year}-{month}微信聊天视频导出' if month else f'{year}微信聊天视频导出' 
        if not target_folder:
            os.makedirs(name=folder_name,exist_ok=True)
            target_folder=os.path.join(os.getcwd(),folder_name)
            print(f'未传入文件夹路径,所有导出的微信聊天视频将保存至 {target_folder}')
        if not os.path.isdir(target_folder):
            raise NotFolderError(f'给定路径不是文件夹,无法导入保存聊天文件')
        chatfiles_folder=Tools.where_video_folder()
        folders=os.listdir(chatfiles_folder)
        #先找到所有以年份开头的文件夹,并将得到的文件夹名字与其根目录chatfile_folder这个路径join
        filtered_folders=[os.path.join(chatfiles_folder,folder) for folder in folders if folder.startswith(year)]
        if month:
            #如果有月份传入，那么在上一步基础上根据月份筛选
            filtered_folders=[folder for folder in filtered_folders if folder.endswith(month)]
        for folder_path in filtered_folders:#遍历筛选后的每个文件夹
            #获取该文件夹下以.mp4结尾的所有文件路径列表，然后使用copy_files方法复制过去，
            exported_videos=[os.path.join(folder_path,filename) for filename in  os.listdir(folder_path) if filename.endswith('.mp4')]
            SystemSettings.copy_files(exported_videos,target_folder)
        print(f'已导出{len(os.listdir(target_folder))}个视频至:{target_folder}')
        return exported_videos

    @staticmethod
    def export_files(year:str=time.strftime('%Y'),month:str=None,target_folder:str=None)->list[str]:
        '''
        该函数用来快速导出微信聊天文件
        Args:
            year:年份,除非手动删除否则聊天文件持续保存,格式:YYYY:2025,2024
            month:月份,微信聊天文件是按照xxxx年-xx月分批存储的格式:XX:06
            target_folder:导出的聊天文件保存的位置,需要是文件夹
        '''
        folder_name=f'{year}年-{month}月微信聊天文件导出' if month else f'{year}年微信聊天文件导出' 
        if not target_folder:
            os.makedirs(name=folder_name,exist_ok=True)
            target_folder=os.path.join(os.getcwd(),folder_name)
            print(f'未传入文件夹路径,所有导出的微信聊天文件将保存至 {target_folder}')
        if not os.path.isdir(target_folder):
            raise NotFolderError(f'给定路径不是文件夹,无法导入保存聊天文件')
        chatfiles_folder=Tools.where_chatfile_folder()
        folders=os.listdir(chatfiles_folder)
        #先找到所有以年份开头的文件夹,并将得到的文件夹名字与其根目录chatfile_folder这个路径join
        filtered_folders=[os.path.join(chatfiles_folder,folder) for folder in folders if folder.startswith(year)]
        if month:
            #如果有月份传入，那么在上一步基础上根据月份筛选
            filtered_folders=[folder for folder in filtered_folders if folder.endswith(month)]
        for folder_path in filtered_folders:#遍历筛选后的每个文件夹
            #获取该文件夹下的所有文件路径列表，然后使用copy_files方法复制过去，
            files_in_folder=[os.path.join(folder_path,filename) for filename in  os.listdir(folder_path)] 
            SystemSettings.copy_files(files_in_folder,target_folder)
        exported_files=os.listdir(target_folder)
        print(f'已导出{len(exported_files)}个文件至:{target_folder}')
        return exported_files

class Call():
    @staticmethod
    def voice_call(friend:str,is_maximize:bool=None,close_weixin:bool=None)->None:
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
        voice_call_button=main_window.child_window(**Buttons.VoiceCallButton)
        voice_call_button.click_input()
        if close_weixin:
            main_window.close()

    @staticmethod
    def video_call(friend:str,is_maximize:bool=None,close_weixin:bool=None)->None:
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
        video_call_button=main_window.child_window(**Buttons.VideoCallButton)
        video_call_button.click_input()
        if close_weixin:
            main_window.close()


class Contacts():
    '''
    用来获取通讯录联系人的一些方法
    '''
    @staticmethod
    def check_my_info(is_maximize:bool=None,close_weixin:bool=None)->dict:
        '''
        该函数用来查看个人信息
        Args:
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        Returns:
        myinfo:个人资料{'昵称':,'微信号':,'地区':,'wxid':}
        '''
        #思路:鼠标移动到朋友圈顶部右下角,点击头像按钮，激活弹出窗口
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        wxid=Tools.get_current_wxid()
        moments_window=Navigator.open_moments(is_maximize=is_maximize,close_weixin=close_weixin)
        moments_list=moments_window.child_window(control_type='List',auto_id="sns_list")
        rec=moments_list.children()[0].rectangle()
        coords=(rec.right-60,rec.bottom-35)
        mouse.click(coords=coords)
        profile_pane=Desktop(backend='uia').window(**Windows.PopUpProfileWindow)
        group=profile_pane.child_window(control_type='Group',found_index=3).children()[1]
        texts=group.descendants(control_type='Text')
        texts=[item.window_text() for item in texts]
        myinfo={'昵称':texts[0],'微信号':texts[2],'wxid':wxid}
        if len(texts)==5:
            myinfo['地区']=texts[4]
        profile_pane.close()
        moments_window.close()
        return myinfo

    @staticmethod
    def get_friends_detail(is_maximize:bool=None,close_weixin:bool=None,is_json:bool=False)->(list[dict]|str):
        '''
        该方法用来获取通讯录内好友信息
        Args:

            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
            is_json:是否以json格式返回
        Returns:
            friends_detail:所有好友的信息
        '''
        
        #切换到联系人分区内的第一个好友
        def switch_to_first_friend():
            contact_list.type_keys('{HOME}')
            items=contact_list.children(control_type='ListItem')
            for i in range(len(items)):
                if items[i]==contact_item and i<len(items)-1:
                    first_friend=i+1
                    if items[i+1].window_text()=='':
                        first_friend+=1
                    break
            items[first_friend].click_input()
        
        #切换到联系人分区内的最后一个好友
        def switch_to_last_friend():
            contact_list.type_keys('{END}')
            last_friend=contact_list.children(control_type='ListItem',class_name="mmui::ContactsCellItemView")[-1]
            last_friend.click_input()
       
        #获取右侧好友信息面板
        def get_specific_info():
            region='无'#好友的地区
            tag='无'#好友标签
            common_group_num='无'
            remark='无'#备注
            signature='无'#个性签名
            source='无'#好友来源
            descrption='无'#描述
            phonenumber='无'#电话号
            permission='无'#朋友权限
            texts=contact_profile.descendants(control_type='Text')
            texts=[item.window_text() for item in texts]
            nickname=texts[0]
            wx_number=texts[texts.index('微信号：')+1]#微信号
            if '昵称：' in texts:
                nickname=texts[texts.index('昵称：')+1]
            if '地区：' in texts:
                region=texts[texts.index('地区：')+1]
            if '备注' in texts:
                remark=texts[texts.index('备注')+1]
                if remark=='标签':
                    remark='无'
            if '共同群聊' in texts:
                common_group_num=texts[texts.index('共同群聊')+1]
            if '个性签名' in texts:
                signature=texts[texts.index('个性签名')+1]
            if '来源' in texts:
                source=texts[texts.index('来源')+1]
            if '电话' in texts:
                phonenumber=texts[texts.index('电话')+1]
            if '描述' in texts:
                descrption=texts[texts.index('描述')+1]
            if '标签' in texts:
                tag=texts[texts.index('标签')+1]
            if '朋友权限' in texts:
                permission=texts[texts.index('朋友权限')+1]
            info={'昵称':nickname,'微信号':wx_number,'地区':region,'备注':remark,'电话':phonenumber,
            '标签':tag,'描述':descrption,'朋友权限':permission,'共同群聊':f'{common_group_num}','个性签名':signature,'来源':source}
            return info
        
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        friends_detail=[]
        #通讯录列表
        contact_list,main_window=Navigator.open_contacts(is_maximize=is_maximize)
        #右侧的自定义面板
        contact_custom=main_window.child_window(**Customs.ContactCustom)
        #右侧自定义面板下的好友信息所在面板
        contact_profile=contact_custom.child_window(**Groups.ContactProfileGroup)
        #联系人分区
        contact_item=main_window.child_window(control_type='ListItem',title_re=r'联系人\d+',class_name="mmui::ContactsCellGroupView")
        Tools.collapse_contacts(main_window,contact_list)
        contact_item.click_input()
        #有具体的数量,后续可以更换为for循环
        switch_to_last_friend()
        last_wx_number=get_specific_info().get('微信号')
        switch_to_first_friend()
        info=get_specific_info()
        friends_detail.append(info)
        while info.get('微信号')!=last_wx_number:
            pyautogui.keyDown('Down',_pause=False)
            info=get_specific_info()
            friends_detail.append(info)
        Tools.collapse_contacts(main_window,contact_list)
        if is_json:
            friends_detail=json.dumps(obj=friends_detail,ensure_ascii=False,indent=2)
        if close_weixin:
            main_window.close()
        return friends_detail
    
    @staticmethod
    def get_wecom_friends_detail(is_maximize:bool=None,close_weixin:bool=None,is_json:bool=False)->(list[dict]|str):
        '''
        该方法用来获取通讯录内企业微信好友详细信息
        Args:

            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
            is_json:是否以json格式返回
        Returns:
            friends_detail:所有企业微信好友的信息
        '''
     
        #切换到企业微信联系人分区内的第一个好友
        def switch_to_first_friend():
            contact_list.type_keys('{HOME}')
            items=contact_list.children(control_type='ListItem')
            for i in range(len(items)):
                if items[i]==wecom_item and i<len(items)-1:
                    first_friend=i+1
                    if items[i+1].window_text()=='':
                        first_friend+=1
                    break
            items[first_friend].click_input()
        
        #获取右侧好友信息面板内的具体信息
        def get_specific_info():
            #没用的文本信息
            no_need_labels=['企业','昵称：','备注','实名','职务','员工状态','朋友圈','工作时间',
            '在线时间','地址','发消息','语音聊天','视频聊天','企业信息','来自','企业微信']
            company='无'#好友的企业
            remark='无'#备注
            realname='无'#实名
            state='在职'#员工状态
            duty='无'#职务
            working_time='无'#工作时间
            location='无'#地址
            texts=contact_profile.descendants(control_type='Text')
            texts=[item.window_text() for item in texts]
            nickname=texts[0] 
            company=texts[texts.index('企业')+1]#微信号
            if '昵称：' in texts:
                nickname=texts[texts.index('昵称：')+1]
            if '备注' in texts:
                remark=texts[texts.index('备注')+1]
                if remark=='企业信息' or remark=='朋友圈':
                    remark='无'
            if '实名' in texts:
                realname=texts[texts.index('实名')+1]
            if '职务' in texts:
                duty=texts[texts.index('职务')+1]
            if '员工状态' in texts:
                state=texts[texts.index('员工状态')+1]
            if '工作时间' in texts:
                working_time=texts[texts.index('工作时间')+1]
            if '在线时间' in texts:
                working_time=texts[texts.index('在线时间')+1]
            if '地址' in texts:
                location=texts[texts.index('地址')+1]
            info={'昵称':nickname,'备注':remark,'企业':company,'实名':realname,'在职状态':state,
            '职务':duty,'工作时间':working_time,'地址':location}
            no_need_labels.extend(info.values())
            others=[text for text in texts if text not in no_need_labels and text!=f'@{company}']
            if others:
                info['其他']=others
            return info
        
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        friends_detail=[]
        #通讯录列表
        contact_list,main_window=Navigator.open_contacts(is_maximize=is_maximize)
        #右侧的自定义面板
        contact_custom=main_window.child_window(**Customs.ContactCustom)
        #右侧自定义面板下的好友信息所在面板
        contact_profile=contact_custom.child_window(**Groups.ContactProfileGroup)
        #企业微信联系人分区
        Tools.collapse_contacts(main_window,contact_list)
        wecom_item=main_window.child_window(control_type='ListItem',title_re=r'企业微信联系人\d+',class_name="mmui::ContactsCellGroupView")
        if not wecom_item.exists(timeout=0.1):
            print(f'你没有企业微信联系人,无法获取企业微信好友信息！')
        if wecom_item.exists(timeout=0.1):
            total=int(re.search(r'\d+',wecom_item.window_text()).group(0))
            wecom_item.click_input()
            switch_to_first_friend()
            info=get_specific_info()
            friends_detail.append(info)
            for _ in range(total+1):
                pyautogui.keyDown('Down',_pause=False)
                info=get_specific_info()
                friends_detail.append(info)
            Tools.collapse_contacts(main_window,contact_list)
            if is_json:
                friends_detail=json.dumps(obj=friends_detail,ensure_ascii=False,indent=2)
            if close_weixin:
                main_window.close()
        return friends_detail 
    
    @staticmethod
    def get_service_account_detail(is_maximize:bool=None,close_weixin:bool=None,is_json:bool=False)->(list[dict]|str):
        '''
        该方法用来获取通讯录内服务号详细信息
        Args:

            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
            is_json:是否以json格式返回
        Returns:
            friends_detail:所有关注过的服务号的详细信息
        '''
        def remove_duplicates(list):
            seen=set()
            result=[]
            for item in list:
                if item['微信号'] not in seen:
                    seen.add(item['微信号'])
                    result.append(item)
            return result

        #切换到服务号分区内的第一个好友
        def switch_to_first_friend():
            contact_list.type_keys('{HOME}')
            items=contact_list.children(control_type='ListItem')
            for i in range(len(items)):
                if items[i]==service_item and i<len(items)-1:
                    first_friend=i+1
                    if items[i+1].window_text()=='':
                        first_friend+=1
                    break
            items[first_friend].click_input()
        
        #获取右侧好友信息面板内的具体信息
        def get_specific_info():
            texts=contact_profile.descendants(control_type='Text')
            texts=[item.window_text() for item in texts]
            name=texts[0]
            wx_number=texts[texts.index("微信号：")+1]
            description=texts[-2] if len(texts)==5 else '无'
            info={'名称':name,'微信号':wx_number,'描述':description}
            return info
        
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        friends_detail=[]
        #通讯录列表
        contact_list,main_window=Navigator.open_contacts(is_maximize=is_maximize)
        #右侧的自定义面板
        contact_custom=main_window.child_window(**Customs.ContactCustom)
        #右侧自定义面板下的好友信息所在面板
        contact_profile=contact_custom.child_window(**Groups.ContactProfileGroup)
        #企业微信联系人分区
        Tools.collapse_contacts(main_window,contact_list)
        service_item=main_window.child_window(control_type='ListItem',title_re=r'服务号\d+',class_name="mmui::ContactsCellGroupView")
        if not service_item.exists(timeout=0.1):
            print(f'你没有关注过任何服务号,无法获取服务号信息！')
        if service_item.exists(timeout=0.1):
            total=int(re.search(r'\d+',service_item.window_text()).group(0))
            service_item.click_input()
            switch_to_first_friend()
            info=get_specific_info()
            friends_detail.append(info)
            for _ in range(total):
                pyautogui.keyDown('Down',_pause=False)
                info=get_specific_info()
                friends_detail.append(info)
            Tools.collapse_contacts(main_window,contact_list)
            friends_detail=remove_duplicates(friends_detail)
            if is_json:
                friends_detail=json.dumps(obj=friends_detail,ensure_ascii=False,indent=2)
            if close_weixin:
                main_window.close()
        return friends_detail 

    @staticmethod
    def get_official_account_detail(is_maximize:bool=None,close_weixin:bool=None,is_json:bool=False)->(list[dict]|str):
        '''
        该方法用来获取通讯录内公众号详细信息
        Args:

            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
            is_json:是否以json格式返回
        Returns:
            friends_detail:所有关注过的公众号的详细信息
        '''
        def remove_duplicates(list):
            seen=set()
            result=[]
            for item in list:
                if item['微信号'] not in seen:
                    seen.add(item['微信号'])
                    result.append(item)
            return result

        #切换到公众号分区内的第一个好友
        def switch_to_first_friend():
            contact_list.type_keys('{HOME}')
            items=contact_list.children(control_type='ListItem')
            for i in range(len(items)):
                if items[i]==official_item and i<len(items)-1:
                    first_friend=i+1
                    if items[i+1].window_text()=='':
                        first_friend+=1
                    break
            items[first_friend].click_input()
        
        #获取右侧好友信息面板内的具体信息
        def get_specific_info():
            texts=contact_profile.descendants(control_type='Text')
            texts=[item.window_text() for item in texts]
            name=texts[0]
            wx_number=texts[texts.index("微信号：")+1]
            description=texts[-2] if len(texts)==5 else '无'
            info={'名称':name,'微信号':wx_number,'描述':description}
            return info
        
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        friends_detail=[]
        #通讯录列表
        contact_list,main_window=Navigator.open_contacts(is_maximize=is_maximize)
        #右侧的自定义面板
        contact_custom=main_window.child_window(**Customs.ContactCustom)
        #右侧自定义面板下的好友信息所在面板
        contact_profile=contact_custom.child_window(**Groups.ContactProfileGroup)
        #企业微信联系人分区
        Tools.collapse_contacts(main_window,contact_list)
        official_item=main_window.child_window(control_type='ListItem',title_re=r'公众号\d+',class_name="mmui::ContactsCellGroupView")
        if not official_item.exists(timeout=0.1):
            print(f'你没有关注过任何公众号,无法获取公众号信息！')
        if official_item.exists(timeout=0.1):
            total=int(re.search(r'\d+',official_item.window_text()).group(0))
            official_item.click_input()
            switch_to_first_friend()
            info=get_specific_info()
            friends_detail.append(info)
            for _ in range(total):
                pyautogui.keyDown('Down',_pause=False)
                info=get_specific_info()
                friends_detail.append(info)
            Tools.collapse_contacts(main_window,contact_list)
            friends_detail=remove_duplicates(friends_detail)
            if is_json:
                friends_detail=json.dumps(obj=friends_detail,ensure_ascii=False,indent=2)
            if close_weixin:
                main_window.close()
        return friends_detail 
        
    @staticmethod
    def get_groups_detail(is_maximize:bool=None,close_weixin:bool=None)->list[str]:
        '''
        该函数用来获取我加入的所有群聊,原理是搜索个人昵称在群聊结果一栏中遍历查找
        Args:

            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        Returns:
            groups:所有已加入的群聊名称
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        
        groups=[]
        main_window=Navigator.open_weixin(is_maximize=is_maximize)
        myname=Contacts.check_my_info(close_weixin=False,is_maximize=is_maximize).get('昵称')
        chat_button=main_window.child_window(**SideBar.Chats)
        chat_button.click_input()
        search=main_window.descendants(**Main_window.Search)[0]
        search.click_input()
        SystemSettings.copy_text_to_windowsclipboard(myname)
        pyautogui.hotkey('ctrl','v',_pause=False)
        time.sleep(1)#必须停顿1s等待加载出结果来
        search_results=main_window.child_window(title='',control_type='List')
        check_all_buttons=[button for button in search_results.children() if r'查看全部' in button.window_text()]
        total=int(re.search(r'\d+',check_all_buttons[0].window_text()).group(0))
        check_all_buttons[0].click_input()
        pyautogui.press('up',presses=4,interval=0.1)
        #微信潜规则,展开全部按钮之上只显示3个搜索结果，
        #所以按四下up健可以到达第一个搜索结果
        for _ in range(total+1):
            #获取灰色的被选中的listitem记录
            focused_item=[listitem for listitem in search_results.children(control_type='ListItem',class_name="mmui::SearchContentCellView") if listitem.has_keyboard_focus()]
            if focused_item:
                groups.append(focused_item[0].window_text())
                pyautogui.keyDown('down',_pause=False)
            else:
                break
        #从前往后逆序倒过来total个
        groups=groups[-total:]
        if close_weixin:
            main_window.close()
        return groups

    @staticmethod
    def get_common_groups(friend:str,is_maximize:bool=None,close_weixin:bool=None)->list[str]:
        '''
        该函数用来获取我与某些好友加入的所有共同群聊名称
        Args:

            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        Returns:
            groups:所有已加入的群聊名称
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        groups=[]
        main_window=Navigator.open_weixin(is_maximize=is_maximize)
        chat_button=main_window.child_window(**SideBar.Chats)
        chat_button.click_input()
        search=main_window.descendants(**Main_window.Search)[0]
        search.click_input()
        SystemSettings.copy_text_to_windowsclipboard(friend)
        pyautogui.hotkey('ctrl','v')
        time.sleep(1)#必须停顿1s等待加载出结果来
        search_results=main_window.child_window(title='',control_type='List')
        group_label=search_results.child_window(control_type='ListItem',title='群聊',class_name="mmui::XTableCell")
        #微信搜索相关好友后会显示共同群聊，如果搜索结果中有群聊这个灰色标签的ListItem，说明有共同群聊
        if not group_label.exists():
            print(f'你与 {friend} 并无共同群聊!')
        else:#
            #只有当共同群聊数量大于4时候微信才会将其收起，此时有一个名为查看全部(\d+)的按钮
            check_all_buttons=[button for button in search_results.children() if r'查看全部' in button.window_text()]
            if check_all_buttons:
                total=int(re.search(r'\d+',check_all_buttons[0].window_text()).group(0))
                check_all_buttons[0].click_input()#点一下查看全部按钮，此时focus的listitem是第共同群聊中的第四个
                #微信潜规则,展开全部按钮之上只显示3个共同群聊结果，
                #所以按四下up健可以到达第一个搜索结果
                pyautogui.press('up',presses=4,interval=0.1)
                #然后按total+1下按钮获取被选中的listitem的window_text*()
                for _ in range(total+1):
                    #获取灰色的被选中的listitem记录
                    focused_item=[listitem for listitem in search_results.children(control_type='ListItem',class_name="mmui::SearchContentCellView") if listitem.has_keyboard_focus()]
                    if focused_item:
                        groups.append(focused_item[0].window_text())
                        pyautogui.keyDown('down',_pause=False)
                    else:
                        break
            else:#共同群聊总数小于4,最多就是3
                total=3
                #先定位到群聊这个灰色标签
                length=len(search_results.children(control_type='ListItem'))
                for i in range(length):
                    if search_results.children(control_type='ListItem')[i]==group_label:#群聊标签的下一个，也就是第一个共同群聊
                        break
                for listitem in search_results.children(control_type='ListItem')[i:i+3]:
                    if listitem.class_name()=="mmui::SearchContentCellView":
                        groups.append(listitem.window_text())#
            #从前往后逆序倒过来total个
            groups=groups[-total:]
        chat_button.click_input()
        if close_weixin:
            main_window.close()
        return groups
    
    def get_friend_profile(friend:str,search_pages:int=None,is_maximize:bool=None,close_weixin:bool=None):
        '''
        该函数用来获取单个好友的个人简介信息
        Args:
            friend:好友备注
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        Returns:
            profile:好友简介面板上的所有内容
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if search_pages is None:
            search_pages=GlobalConfig.search_pages
        region='无'#好友的地区
        tag='无'#好友标签
        common_group_num='无'
        remark='无'#备注
        signature='无'#个性签名
        source='无'#好友来源
        descrption='无'#描述
        phonenumber='无'#电话号
        permission='无'#朋友权限
        profile_pane,main_window=Navigator.open_friend_profile(friend=friend,search_pages=search_pages,is_maximize=is_maximize)
        text_uis=profile_pane.descendants(control_type='Text')
        texts=[item.window_text() for item in text_uis]
        nickname=texts[0]
        wx_number=texts[texts.index('微信号：')+1]#微信号
        if '昵称：' in texts:
            nickname=texts[texts.index('昵称：')+1]
        if '地区：' in texts:
            region=texts[texts.index('地区：')+1]
        if '备注' in texts:
            remark=texts[texts.index('备注')+1]
            if remark=='标签':
                remark='无'
        if '共同群聊' in texts:
            common_group_num=texts[texts.index('共同群聊')+1]
        if '个性签名' in texts:
            signature=texts[texts.index('个性签名')+1]
        if '来源' in texts:
            source=texts[texts.index('来源')+1]
        if '电话' in texts:
            phonenumber=texts[texts.index('电话')+1]
        if '描述' in texts:
            descrption=texts[texts.index('描述')+1]
        if '标签' in texts:
            tag=texts[texts.index('标签')+1]
        if '朋友权限' in texts:
            permission=texts[texts.index('朋友权限')+1]
        profile={'昵称':nickname,'微信号':wx_number,'地区':region,'备注':remark,'电话':phonenumber,
        '标签':tag,'描述':descrption,'朋友权限':permission,'共同群聊':f'{common_group_num}','个性签名':signature,'来源':source}
        friend_text=main_window.child_window(title=friend,control_type='Text',found_index=1)
        friend_text.click_input()
        if close_weixin:
            main_window.close()
        return profile
    
    @staticmethod
    def get_recent_groups(is_maximize:bool=None,close_weixin:bool=None)->list[tuple[str]]:
        '''
        该函数用来获取最近群聊信息(包括群聊名称与群聊人数)
        Args:

            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        Returns:
            recent_groups:最近群聊信息
        '''
        def remove_duplicates(list):
            seen=set()
            result=[]
            for item in list:
                if item not in seen:
                    seen.add(item)
                    result.append(item)
            return result
    
        def get_specific_info(texts):
            nums=[num_pattern.search(text).group(1) for text in texts]
            names=[num_pattern.sub('',text) for text in texts]
            return names,nums

        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
    
        Texts=[]
        num_pattern=re.compile(r'\((\d+)\)$')
        contacts_manage=Navigator.open_contacts_manage(is_maximize=is_maximize,close_weixin=close_weixin)
        contacts_manage_list=contacts_manage.child_window(**Lists.ContactsManageList)
        recent_group=contacts_manage.child_window(**ListItems.RecentGroupListItem)
        Tools.collapse_contact_manage(contacts_manage)
        if not recent_group.exists(timeout=0.1):
            print(f'无最近群聊,无法获取!')
            contacts_manage.close()
            return []
        else:
            recent_group.click_input()
            contacts_manage_list.type_keys('{END}')
            last=contacts_manage_list.children(control_type='ListItem',
            class_name="mmui::ContactsManagerControlSessionCell")[-1].window_text()
            contacts_manage_list.type_keys('{HOME}')
            listitems=contacts_manage_list.children(control_type='ListItem',class_name="mmui::ContactsManagerControlSessionCell")
            Texts.extend([listitem.window_text() for listitem in listitems])
            while Texts[-1]!=last:
                contacts_manage_list.type_keys('{PGDN}')
                listitems=contacts_manage_list.children(control_type='ListItem',class_name="mmui::ContactsManagerControlSessionCell")
                Texts.extend([listitem.window_text() for listitem in listitems])
            Texts=remove_duplicates(Texts)#去重,Texts内是群聊+(人数)构成的文本,如果群聊名称与人数都相同那就没法筛选了
            group_names,member_nums=get_specific_info(Texts)#正则提取与替换便是群名与人数
            recent_groups=list(zip(group_names,member_nums))#不使用dict(zip)是考虑到可能有相同群聊的,dict key不能有重复
            contacts_manage.close()
            return recent_groups
    
class Settings():

    def change_style(style:int,is_maximize:bool=None,close_weixin:bool=None):
        '''
        该函数用来修改微信的主题样式
        Args:
            style:主题样式,0:跟随系统,1:浅色模式,2:深色模式
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        style_map={0:'跟随系统',1:'浅色模式',2:'深色模式'}
        settings_window=Navigator.open_settings(is_maximize=is_maximize,close_weixin=close_weixin)
        general_button=settings_window.child_window(control_type='Button',title='通用')
        general_button.click_input()
        outline_text=settings_window.child_window(**Texts.OutLineText)
        outline_button=outline_text.parent().children()[1]
        current_style=outline_button.children(control_type='Text')[0].window_text()
        outline_button.click_input()
        #弹出的菜单无论怎么都无法定位到，干脆纯按键操作
        #顺序是固定的:跟随系统,浅色模式,深色模式
        #无论怎么说先回到顶部
        if current_style=='浅色模式':
            pyautogui.press('up')
        if current_style=='深色模式':
            pyautogui.press('up',presses=2)
        #回到顶部后根据传入的style来选择向下按几次
        if style==1:
            pyautogui.press('down')
        if style==2:
            pyautogui.press('down',presses=2)
        pyautogui.press('enter')
        print(f'已将主题设置为{style_map.get(style)}')
        settings_window.close()
    
    def change_language(language:int,is_maximize:bool=None,close_weixin:bool=None):
        '''
        该函数用来修改微信的语言
        Args:
            language:语言,0:跟随系统,1:浅色模式,2:深色模式
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        language_map={0:'跟随系统',1:'简体中文',2:'English',3:'繁體中文'}
        settings_window=Navigator.open_settings(is_maximize=is_maximize,close_weixin=close_weixin)
        general_button=settings_window.child_window(control_type='Button',title='通用')
        general_button.click_input()
        language_text=settings_window.child_window(**Texts.LanguageText)
        language_button=language_text.parent().children()[1]
        current_language=language_button.children(control_type='Text')[0].window_text()
        language_button.click_input()
        #弹出的菜单无论怎么都无法定位到，干脆纯按键操作
        #顺序是固定的:'跟随系统,简体中文,English,繁體中文
        #无论怎么说先回到顶部
        if current_language=='简体中文':
            pyautogui.press('up')
        if current_language=='English':
            pyautogui.press('up',presses=2)
        if current_language=='繁體中文':
            pyautogui.press('down',presses=1)
        #回到顶部后根据传入的style来选择向下按几次
        if language==1:
            pyautogui.press('down')
        if language==2:
            pyautogui.press('down',presses=2)
        if language==3:
            pyautogui.press('down',presses=3)
        pyautogui.press('enter')
        confirm_button=settings_window.child_window(**Buttons.ConfirmButton)
        confirm_button.click_input()
        print(f'已将语言设置为{language_map.get(language)}')

class FriendSettings():
    @staticmethod
    def add_new_friend(friend:str,is_maximize:bool=None,close_weixin:bool=None):
        '''
        该函数用来添加新朋友
        Args:
            number:微信号或手机号
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        add_friend_window=Navigator.open_add_friend_panel(is_maximize=is_maximize,close_weixin=close_weixin)
        SystemSettings.copy_text_to_windowsclipboard(friend)
        edit=add_friend_window.child_window(control_type='Edit')
        edit.set_text("")
        pyautogui.hotkey('ctrl','v')
        pyautogui.press('enter')

class AutoReply():
    
    @staticmethod
    def auto_reply_to_friend(friend:str,duration:str,content:str,search_pages:int=None,is_maximize:bool=None,close_weixin:bool=None)->None:
        '''
        该方法用来实现类似QQ的自动回复某个好友指定的消息
        Args:
            friend:好友或群聊备注
            duration:自动回复持续时长,格式:'s','min','h',单位:s/秒,min/分,h/小时
            content:指定的回复内容,比如:自动回复[微信机器人]:您好,我当前不在,请您稍后再试
            search_pages:在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面\n
            folder_path:存放聊天记录截屏图片的文件夹路径
            is_maximize:微信界面是否全屏,默认全屏
            close_weixin:任务结束后是否关闭微信,默认关闭
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if search_pages is None:
            search_pages=GlobalConfig.search_pages
        duration=Tools.match_duration(duration)#将's','min','h'转换为秒
        if not duration:#不按照指定的时间格式输入,需要提前中断退出
            raise ValueError
        #打开好友的对话框,返回值为编辑消息框和主界面
        main_window=Navigator.open_dialog_window(friend=friend,is_maximize=is_maximize,search_pages=search_pages)
        #需要判断一下是不是公众号
        voice_call_button=main_window.child_window(**Buttons.VoiceCallButton)
        video_call_button=main_window.child_window(**Buttons.VideoCallButton)
        if not voice_call_button.exists(timeout=0.1):
            #公众号没有语音聊天按钮
            main_window.close()
            raise NotFriendError(f'非正常好友,无法自动回复!')
        if not video_call_button.exists(timeout=0.1) and voice_call_button.exists(timeout=0.1):
            main_window.close()
            raise NotFriendError('auto_reply_to_friend只用来自动回复好友,如需自动回复群聊请使用auto_reply_to_group!')
        ########################################################################################################
        chatList=main_window.child_window(**Lists.FriendChatList)#聊天界面内存储所有信息的容器
        initial_message=chatList.children(control_type='ListItem')[-1]#刚打开聊天界面时的最后一条消息的listitem
        initial_runtime_id=initial_message.element_info.runtime_id
        SystemSettings.copy_text_to_windowsclipboard(content)#复制回复内容到剪贴板
        SystemSettings.open_listening_mode()#开启监听模式,此时电脑只要不断电不会息屏 
        end_timestamp=time.time()+duration#根据秒数计算截止时间
        while time.time()<end_timestamp:
            newMessage=chatList.children(control_type='ListItem')[-1]
            runtime_id=newMessage.element_info.runtime_id
            if runtime_id!=initial_runtime_id and newMessage.window_text()!=content: 
            #消息列表内的最后一条消息(listitem)不等于刚打开聊天界面时的最后一条消息(listitem)
            #并且最后一条消息的发送者是好友时自动回复
            #这里我们判断的是两条消息(listitem)是否相等,不是文本是否相等,要是文本相等的话,对方一直重复发送
            #刚打开聊天界面时的最后一条消息的话那就一直不回复了
                pyautogui.hotkey('ctrl','v',_pause=False)
                pyautogui.hotkey('alt','s',_pause=False)
                initial_runtime_id=runtime_id
        SystemSettings.close_listening_mode()
        if close_weixin:
            main_window.close()

class Moments():
    pass
class GroupSettings():
    pass
class Collections():

    pass    

