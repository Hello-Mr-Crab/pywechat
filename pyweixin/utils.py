import re
import time
import psutil
import pyautogui
from functools import wraps
from pywinauto import WindowSpecification
from .Config import GlobalConfig
from .WeChatTools import Navigator,Tools
from .WinSettings import SystemSettings
from .Errors import TimeNotCorrectError,NotFriendError
from .Uielements import Main_window,SideBar,Buttons,Edits,Lists
#######################################################################################
Main_window=Main_window()#主界面UI
SideBar=SideBar()#侧边栏UI
Buttons=Buttons()#所有Button类型UI
Edits=Edits()#所有Edit类型UI
Lists=Lists()#所有List类型UI
pyautogui.FAILSAFE=False#防止鼠标在屏幕边缘处造成的误触


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
                raise NotFriendError('auto_reply_to_friend只用来自动回复好友,如需自动回复群聊请使用auto_reply_to_group!')
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
    
def scan_for_new_messages(main_window:WindowSpecification=None,is_maximize:bool=None,close_weixin:bool=None)->dict:
    '''
    该函数用来扫描检查一遍消息列表中的所有新消息,返回发送对象以及新消息数量(不包括免打扰)
    Args:
        main_window:微信主界面实例,可以用于二次开发中直接传入main_window,也可以不传入,不传入自动打开
        is_maximize:微信界面是否全屏，默认不全屏
        close_weixin:任务结束后是否关闭微信，默认关闭
    Returns:
        newMessages_dict:有新消息的好友备注及其对应的新消息数量构成的字典
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
    if main_window is None:
        main_window=Navigator.open_weixin(is_maximize=is_maximize)
    newMessageSenders=[]
    newMessageNums=[]
   
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
        return {}
    if new_message_num:
        new_message_num=int(new_message_num.group(0))
        message_list=main_window.child_window(**Main_window.ConversationList)
    while sum(newMessageNums)<new_message_num:#当最终的新消息总数之和大于时退出循环
        #遍历获取带有新消息的ListItem
        listItems=message_list.children(control_type='ListItem')
        senders,nums=traverse_messsage_list(listItems)
        # #提取姓名和数量
        newMessageNums.extend(nums)
        newMessageSenders.extend(senders)
        message_list.type_keys('{PGDN}')
    message_list.type_keys('{HOME}')
    newMessages_dict=dict(zip(newMessageSenders,newMessageNums))
    if close_weixin:
        main_window.close()
    return newMessages_dict

def language_detector():
    """
    通过WechatAppex.exe的命令行参数判断语言版本
    Returns:
        lang:简体中文,繁体中文,English
    """
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
