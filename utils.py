import re
import time
import emoji
import psutil
import pyautogui
from functools import wraps
from pywinauto import WindowSpecification,Desktop
from pywinauto.controls.uia_controls import ListItemWrapper #TypeHint要用到
from .Config import GlobalConfig
from .WeChatTools import Navigator,Tools
from .WinSettings import SystemSettings
from .Errors import TimeNotCorrectError,NotFriendError
from .Uielements import Main_window,SideBar,Buttons,Edits,Lists,Windows
#######################################################################################
Main_window=Main_window()#主界面UI
SideBar=SideBar()#侧边栏UI
Buttons=Buttons()#所有Button类型UI
Edits=Edits()#所有Edit类型UI
Lists=Lists()#所有List类型UI
Windows=Windows()#所有Windows类型UI
pyautogui.FAILSAFE=False#防止鼠标在屏幕边缘处造成的误触
desktop=Desktop(backend='uia')

class Regex_Patterns():
    '''常用正则pattern'''
    def __init__(self):
        #|表示或的逻辑关系,关于Python正则表达式的任何问题和入门级教程可以差看这篇博客:https://blog.csdn.net/weixin_73953650/article/details/151123336?spm=1001.2014.3001.5501
        self.Sns_Timestamp_pattern=re.compile(r'\d+分钟前|\d+小时前|昨天|\d+天前')#朋友圈好友发布内容左下角的时间戳
        self.Chafile_Timestamp_pattern=re.compile(r'(\d{4}年\d{1,2}月\d{1,2}日|\d{1,2}月\d{1,2}日|昨天|星期\w|\d{1,2}:\d{2})')#微信聊天文件时间戳
        self.Snsdetail_Timestamp_pattern=re.compile(r'(?<=\s)\d{4}年\d{1,2}月\d{1,2}日\s\d{1,2}:\d{2}|\d{1,2}月\d{1,2}日\s\d{1,2}:\d{2}|昨天\s\d{1,2}:\d{2}|星期\w\s\d{1,2}:\d{2}|\d{1,2}:\d{2}\s$')#微信好友朋友圈主页内的时间戳
        self.Chathistory_Timestamp_pattern=re.compile(r'(?<=\s)(\d{4}年\d{1,2}月\d{1,2}日\s\d{2}:\d{2}|\d{1,2}月\d{1,2}日\s\d{2}:\d{2}|\d{2}:\d{2}|昨天\s\d{2}:\d{2}|星期\w\s\d{2}:\d{2})$')#聊天记录界面内的时间戳
        self.Session_Timestamp_pattern=re.compile(r'(?<=\s)(\d{4}/\d{1,2}/\d{1,2}|\d{1,2}/\d{1,2}|\d{2}:\d{2}|昨天 \d{2}:\d{2}|星期\w)$')#主界面左侧会话列表内的时间戳
        self.GroupMember_Num_pattern=re.compile(r'\((\d+)\)$')#通讯录设置界面中每个最近群聊ListItem后边的数字
        self.QtWindow_pattern=re.compile(r'Qt\d+QWindowIcon')#qt窗口通用classname
        self.Filename_pattern=re.compile(r'.*\.\w+\s')#用来匹配.docx,.ppt等文件名，只适合在微信聊天文件界面中使用
        self.File_Pattern=re.compile(r'文件\n(.*)\n')#微信聊天窗口发送的聊天文件卡片上的内容(有两个换行符)
        

def auto_reply_to_friend_decorator(duration:str,friend:str,search_pages:int=5,is_maximize:bool=False,close_weixin:bool=False):
    '''
    该函数为自动回复指定好友的修饰器
    Args:
        friend:好友或群聊备注
        duration:自动回复持续时长,格式:'s','min','h',单位:s/秒,min/分,h/小时
        search_pages:在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
        is_maximize:微信界面是否全屏,默认全屏。
        close_weixin:任务结束后是否关闭微信,默认关闭
    Examples:
    ```
    from pyweixin.utils import auto_reply_to_friend_decorator
    @auto_reply_to_friend_decorator(duration='10min',friend='好友')
    def reply_func(newMessage):
        if '在吗' in newMessage:
            return '你好,我不在'
        if '在干嘛?' in newMessage:
            return '在挂机'
        return '不在'
    reply_func()
    ```
    '''
    def decorator(reply_func):
        @wraps(reply_func)
        def wrapper():
            durations=Tools.match_duration(duration)#将's','min','h'转换为秒
            if not durations:#不按照指定的时间格式输入,需要提前中断退出
                raise TimeNotCorrectError
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
                raise NotFriendError('auto_reply_to_friend只用来自动回复好友')
            ########################################################################################################
            chatList=main_window.child_window(**Lists.FriendChatList)#聊天界面内存储所有信息的容器
            edit_area=main_window.child_window(**Edits.CurrentChatEdit)
            initial_message=chatList.children(control_type='ListItem')[-1]#刚打开聊天界面时的最后一条消息的listitem
            initial_runtime_id=initial_message.element_info.runtime_id
            SystemSettings.open_listening_mode()#开启监听模式,此时电脑只要不断电不会息屏 
            end_timestamp=time.time()+durations#根据秒数计算截止时间
            while time.time()<end_timestamp:
                newMessage=chatList.children(control_type='ListItem')[-1]
                runtime_id=newMessage.element_info.runtime_id
                if runtime_id!=initial_runtime_id:
                    if not Tools.is_my_bubble(main_window,newMessage,edit_area):
                        reply_content=reply_func(newMessage.window_text())
                        edit_area.click_input()
                        SystemSettings.copy_text_to_windowsclipboard(reply_content)#复制回复内容到剪贴板
                        pyautogui.hotkey('ctrl','v',_pause=False)
                        pyautogui.hotkey('alt','s',_pause=False)
                        initial_runtime_id=runtime_id
            SystemSettings.close_listening_mode()
            if close_weixin:
                main_window.close()
        return wrapper
    return decorator 


def get_new_message_num(main_window:WindowSpecification=None,is_maximize:bool=None,close_weixin:bool=None):
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
    if main_window is None:
        main_window=Navigator.open_weixin(is_maximize=is_maximize)
    weixin_button=main_window.child_window(auto_id="main_tabbar", control_type="ToolBar").children()[0]
    #左上角微信按钮的红色消息提示(\d+条新消息)在FullDescription属性中,
    #只能通过id来获取,id是30159，之前是30007,可能是qt组件映射关系不一样
    full_desc=weixin_button.element_info.element.GetCurrentPropertyValue(30159)
    new_message_num=re.search(r'\d+',full_desc)#正则提取数量
    if close_weixin:
        main_window.close()
    return int(new_message_num.group(0)) if new_message_num  else 0


def At_all(main_window:WindowSpecification):
    '''在群里@所有人'''
    if Tools.is_group_chat(main_window):
        edit_area=main_window.child_window(**Edits.CurrentChatEdit)
        mention_popover=main_window.child_window(**Windows.MentionPopOverWindow)
        edit_area.type_keys(f'@')
        if mention_popover.exists(timeout=0.1):
            mention_list=mention_popover.child_window(control_type='List',title='')
            first_item=mention_list.children()[0].window_text()#弹出列表后的第一个人
            if first_item!='所有人':
                pyautogui.press('backspace',presses=1)
                print(f'你不是该群群主或管理员,无权@所有人')
            else:
                edit_area.type_keys('{ENTER}')

def At(main_window:WindowSpecification,at_members:list[str]):
    '''
    在群里@指定的好友,可用于自定义的消息发送函数中
    Args:
        main_window:微信主界面
        at_members:群内所有at对象,必须是群昵称
    '''
    def select(mention_popover:WindowSpecification,member:str):
        '''
        微信的@机制必须type_keys打字才可以唤醒,并且是模糊文字匹配(只匹配文字,空格表情都不匹配)
        若好友的名字中有空格和表情,那么打字的内容只能是第一个空格之前的所有非空格文字,但凡多一个空格
        就不会唤醒@,同时由于表情不好打字,所以替换掉,出现mention面板然后在弹出的列表里完整匹配
        '''
        is_find=True
        mention_list=mention_popover.child_window(control_type='List',title='')
        first_item=mention_list.children()[0].window_text()#弹出列表后的第一个人
        selected_listitem=[listitem for listitem in mention_list.children() if listitem.is_selected()][0]
        while selected_listitem.window_text()!=member:#一直按着下键找，找到了结束循环，或者遍历完一圈又回到了起点也结束循环(即选中的对象与第一个人名字相同)
            mention_list.type_keys('{DOWN}')
            selected_listitem=[listitem for listitem in mention_list.children() if listitem.is_selected()][0]
            if selected_listitem.window_text()==first_item:
                is_find=False
                break
        return is_find
        
    if Tools.is_group_chat(main_window):
        edit_area=main_window.child_window(**Edits.CurrentChatEdit)
        mention_popover=main_window.child_window(**Windows.MentionPopOverWindow)
        for member in at_members:
            cleaned_member=emoji.replace_emoji(member,'')#去掉emoji
            cleaned_member=cleaned_member.split(' ')[0]#找到第一个空格字段之前内容
            edit_area.type_keys(f'@{cleaned_member}')
            if mention_popover.exists(timeout=0.1):
                is_find=select(mention_popover,member)
                if is_find:
                    edit_area.type_keys('{ENTER}')
                if not is_find:
                    pyautogui.press('backspace',presses=len(cleaned_member)+1)
            else:
                edit_area.set_text('')
    
def open_red_packet(dialog_window:WindowSpecification,red_packet:ListItemWrapper)->int:
    '''
    该函数用来点击领取好友发送的红包
    Args:
        dialog_window:好友的聊天窗口,可使用Navigator内的方法打开
        redpacket:红包对应的ListItem
    '''
    red_envelop_view=dialog_window.child_window(class_name='mmui::PayRedEnvelopeInfoView',title='',control_type='Group')#微信红包点击后弹出的界面
    red_envelop_detail=desktop.window(class_name='mmui::PayRedEnvelopDetailWindow',control_type='Window',title='微信')
    red_packet.click_input()
    open_button=red_envelop_view.child_window(control_type='Button',title='拆开')
    open_button.click_input()
    red_envelop_detail.close()

def scan_for_new_messages(main_window:WindowSpecification=None,delay:float=0.3,is_maximize:bool=None,close_weixin:bool=None)->dict:
    '''
    该函数用来扫描检查一遍会话列表中的所有新消息,返回发送对象以及新消息数量(不包括免打扰)
    Args:
        main_window:微信主界面实例,可以用于二次开发中直接传入main_window,也可以不传入,不传入自动打开
        delay:在会话列表查询新消息时的翻页延迟时间,默认0.3秒
        is_maximize:微信界面是否全屏，默认不全屏
        close_weixin:任务结束后是否关闭微信，默认关闭
    Returns:
        newMessages_dict:有新消息的好友备注及其对应的新消息数量构成的字典
    '''
    def traverse_messsage_list(listItems):
        #newMessageTips为newMessagefriends中每个元素的文本:['测试365 5条新消息','一家人已置顶20条新消息']这样的字符串列表
        listItems=[listItem for listItem in listItems if listItem.automation_id() not in not_care 
        and '消息免打扰' not in listItem.window_text()]
        listItems=[listItem for listItem in listItems if new_message_pattern.search(listItem.window_text())]
        senders=[listItem.automation_id().replace('session_item_','') for listItem in listItems]
        newMessageTips=[listItem.window_text() for listItem in listItems if listItem.window_text() not in newMessageSenders]
        newMessageNum=[int(new_message_pattern.search(text).group(1)) for text in newMessageTips]
        return senders,newMessageNum

    not_care={'session_item_服务号','session_item_公众号'}
    if is_maximize is None:
        is_maximize=GlobalConfig.is_maximize
    if close_weixin is None:
        close_weixin=GlobalConfig.close_weixin
    if main_window is None:
        main_window=Navigator.open_weixin(is_maximize=is_maximize)
    newMessageSenders=[]
    newMessageNums=[]
    newMessages_dict=dict(zip(newMessageSenders,newMessageNums))
    chats_button=main_window.child_window(**SideBar.Chats)
    chats_button.click_input()
    #左上角微信按钮的红色消息提示(\d+条新消息)在FullDescription属性中,
    #只能通过id来获取,id是30159，之前是30007,可能是qt组件映射关系不一样
    full_desc=chats_button.element_info.element.GetCurrentPropertyValue(30159)
    message_list_pane=main_window.child_window(**Main_window.ConversationList)
    message_list_pane.type_keys('{HOME}')
    new_message_num=re.search(r'\d+',full_desc)#正则提取数量
    #微信会话列表内ListItem标准格式:备注\s(已置顶)\s(\d+)条未读\s最后一条消息内容\s时间
    new_message_pattern=re.compile(r'\n\[(\d+)条\]')#只给数量分组.group(1)获取
    if not new_message_num:
        print(f'没有新消息')
        return {}
    if new_message_num:
        new_message_num=int(new_message_num.group(0))
        session_list=main_window.child_window(**Main_window.ConversationList)
        session_list.type_keys('{END}')
        time.sleep(0.2)
        last_item=session_list.children(control_type='ListItem')[-1].window_text()
        session_list.type_keys('{HOME}')
        time.sleep(0.2)
        while sum(newMessages_dict.values())<new_message_num:#当最终的新消息总数之和大于等于实际新消息总数时退出循环
            #遍历获取带有新消息的ListItem
            listItems=session_list.children(control_type='ListItem')
            time.sleep(delay)
            senders,nums=traverse_messsage_list(listItems)
            ##提取姓名和数量
            newMessageNums.extend(nums)
            newMessageSenders.extend(senders)
            newMessages_dict=dict(zip(newMessageSenders,newMessageNums))
            session_list.type_keys('{PGDN}')
            if listItems[-1].window_text()==last_item:
                break
        session_list.type_keys('{HOME}')
    if close_weixin:
        main_window.close()
    return newMessages_dict

def language_detector()->(str|None):
    '''
    通过WechatAppex的命令行参数判断语言版本
    Returns:
        lang:简体中文,繁体中文,English
    '''
    lang=None
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if proc.info['name'] and 'wechatappex' in proc.info['name'].lower():
            cmdline = proc.info['cmdline']
            if not cmdline:
                continue
    cmd_str=' '.join(cmdline).lower()
    if '--lang=zh-cn' in cmd_str:
        lang='简体中文'
    if '--lang=zh-tw' in cmd_str:
        lang='繁体中文'
    if '--lang=en' in cmd_str:
        lang='English'
    return lang