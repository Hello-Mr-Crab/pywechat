'''
WeChatAuto
===========


微信4.0版本自动化主模块,实现了绝大多数的自动化功能,包括发送消息,文件,音视频通话等
所有的方法都位于这些静态类内,导入后使用XX.yy的方式使用即可

    - `AutoReply`:微信自动回复的一些方法
    - `Call`: 给某个好友打视频或语音电话
    - `Collections`: 与收藏相关的一些方法
    - `Contacts`: 获取通讯录联系人的一些方法
    - `Files`:  关于微信文件的一些方法,包括发送文件,导出文件等功能
    - `Messages`: 关于微信消息的一些方法,包括收发消息,获取聊天记录,获取聊天会话等功能
    - `Monitor`: 关于微信监听消息的一些方法,包括监听单个聊天窗口的消息
    - `Moments`: 与朋友圈相关的一些方法,发布朋友圈,导出朋友圈,好友朋友圈内容
    - `Settings`: 与微信设置相关的一些方法,更换主题,更换语言,修改自动下载文件大小
    - `FriendSettings`: 与好友设置相关的一些方法

Examples:
=========

使用模块时,你可以:

    >>> from pyweixin.WeChatAuto import Monitor
    >>> from pyweixin.WeChatTools import Navigator 
    >>> dialog_window=Navigator.open_seperate_dialog_window(friend='好友')
    >>> newMessages=Monitor.listen_on_chat(dialog_window,'1min')
    >>> print(newMessages)

或者:

    >>> from pyweixin import Monitor,Navigator
    >>> dialog_window=Navigator.open_seperate_dialog_window(friend='好友')
    >>> newMessages=Monitor.listen_on_chat(dialog_window,'1min')
    >>> print(newMessages)


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
#第三方库
import os
import re
import time
import json
import pyautogui
import win32clipboard
import win32gui,win32con
from collections import Counter
from typing import Literal
from warnings import warn
from pywinauto import WindowSpecification
from pywinauto.controls.uia_controls import ListItemWrapper,ListViewWrapper#TypeHint要用到
from typing import Callable
from packaging import version#字符串版本比较,4.1.9>4.1.8>4.1.7
#####################################################################################
#内部依赖
from .Config import GlobalConfig
from .utils import scan_for_new_messages,get_new_message_num
from .utils import At,At_all,ColorMatch,Regex_Patterns,Special_Labels
from .Warnings import LongTextWarning,NoChatHistoryWarning
from .WeChatTools import Tools,Navigator,mouse,Desktop
from .WinSettings import SystemSettings
from .Errors import TimeNotCorrectError
from .Errors import NoFilesToSendError
from .Errors import NotFolderError
from .Errors import NotFriendError
from .Uielements import (Main_window,SideBar,Buttons,
Edits,Texts,Lists,Panes,Windows,CheckBoxes,MenuItems,Groups,Customs,ListItems)#导入的是自动判断语言后的实例化对象,如果自行使用需要导入xxx_Control
#######################################################################################
desktop=Desktop(backend='uia')#pywinauto的windows桌面对象(WindowSpecification)实例化
pyautogui.FAILSAFE=False#防止鼠标在屏幕边缘处造成的误触

class AutoReply():
    
    @staticmethod
    def auto_reply_to_friend(dialog_window:WindowSpecification,duration:str,callback:Callable[[str,list[str]],str],contexts:list[str]=[],save_file:bool=False,save_media:bool=False,target_folder:str=None,close_dialog_window:bool=True)->dict:
        '''
        该方法用来在指定时间内自动回复会话窗口内的新消息并监听内容
        Args:
            dialog_window:好友单独的聊天窗口或主界面内的聊天窗口,可使用Navigator内的open_seperate_dialoig_window打开
            duraiton:监听持续时长,监听消息持续时长,格式:'s','min','h'单位:s/秒,min/分,h/小时
            callback:新消息处理函数,入参是当前消息和上下文消息(可见的消息列表内的所有文本构成的列表)
            contexts:上下文信息字符串列表,可通过Messages.dump_chat_history获取后传入,在实际运行时会传入给callback函数
            save_file:是否保存文件,需开启自动下载文件并设置为1024MB,默认为False
            save_media:是否保存图片或视频
            target_folder:文件或图片的保存文件夹
            close_dialog_window:是否关闭dialog_window,默认关闭
        Examples:
            >>> from pyweixin import AutoReply,Navigator
            >>> def reply_func2(newMessage:str,contexts:list[str]):
            >>>     return '自动回复[微信机器人]:您好,我当前不在,请您稍后再试'
            >>> main_window=Navigator.open_dialog_window(friend='abcdefghijklmnopqrstuvwxyz123456')
            >>> AutoReply.auto_reply_to_friend(dialog_window=main_window,duration='20s',callback=reply_func2)
            #多线程使用方法:
            >>> from pyweixin import Navigator
            >>> from concurrent.futures import ThreadPoolExecutor
            >>> from pyweixin import Navigator,AutoReply
            >>> def reply_func1(newMessage:str,contexts:list[str]):
            >>>     if '你好' in newMessage:
            >>>        return '你好,有什么可以帮您的吗[呲牙]?'
            >>>     if '在吗' in newMessage:
            >>>        return '在的[旺柴]'
            >>>     return '自动回复[微信机器人]:您好,我当前不在,请您稍后再试'
            >>> def reply_func2(newMessage:str,contexts:list[str]):
            >>>     return '自动回复[微信机器人]:您好,我当前不在,请您稍后再试'
            >>> dialog_windows=[]
            >>> friends=['好友1','好友2']
            >>> for friend in friends:
            >>>     dialog_window=Navigator.open_seperate_dialog_window(friend=friend,window_minimize=True,close_weixin=True)
            >>>     dialog_windows.append(dialog_window)
            >>> durations=['1min']*len(friends)
            >>> callbacks=[reply_func1,reply_func2]
            >>> with ThreadPoolExecutor() as pool:
            >>>     results=pool.map(lambda args: AutoReply.auto_reply_to_friend(*args),list(zip(dialog_windows,durations,callbacks)))
            >>> for friend,result in zip(friends,results):
            >>>     print(friend,result)
        无论是主界面还是单独聊天窗口都可以最小化到状态栏,但千万不要关闭！
        Returns:
            details:该聊天窗口内的新消息(文本内容),格式为{'新消息总数':x,'文本数量':x,'文件数量':x,'图片数量':x,'视频数量':x,'链接数量':x,'文本内容':x}
        '''
        duration=Tools.match_duration(duration)#将's','min','h'转换为秒
        if duration is None:#不按照指定的时间格式输入,需要提前中断退出
            raise TimeNotCorrectError
        if save_file and target_folder is None:
            target_folder=os.path.join(os.getcwd(),f'{dialog_window.window_text()}_listen_on_chat聊天文件保存')
            print(f'未传入文件夹路径,文件,图片,群昵称截图将分别保存到{target_folder}内的Files,Images,Alias文件夹下\n')
            os.makedirs(target_folder,exist_ok=True)
        if save_file:
            file_folder=os.path.join(target_folder,'Files')
            os.makedirs(file_folder,exist_ok=True)
        if save_media:
            media_folder=os.path.join(target_folder,'Media')
            os.makedirs(media_folder,exist_ok=True)
        files=[]
        texts=[]
        total=0
        link_count=0
        video_count=0
        image_count=0
        initial_runtime_id=0
        link_label=Special_Labels.Link
        image_labal=Special_Labels.Image
        video_label=Special_Labels.Video
        file_label=Special_Labels.File
        file_pattern=Regex_Patterns.File_pattern
        timestamp=time.strftime('%Y-%m')
        friend=dialog_window.window_text()
        chatName=dialog_window.child_window(**Texts.CurrentChatNameText)
        if chatName.exists(timeout=0.2):friend=chatName.window_text()
        chatfile_folder=Tools.where_chatfile_folder()
        chatList=dialog_window.child_window(**Lists.FriendChatList)#聊天界面内存储所有信息的容器
        input_edit=dialog_window.child_window(**Edits.InputEdit)
        Tools.activate_chatList(chatList)
        if chatList.children(control_type='ListItem'):
            initial_message=chatList.children(control_type='ListItem')[-1]#刚打开聊天界面时的最后一条消息的listitem
            initial_runtime_id=initial_message.element_info.runtime_id    
        end_timestamp=time.time()+duration#根据秒数计算截止时间
        SystemSettings.open_listening_mode(volume=False)
        while time.time()<end_timestamp:
            if chatList.children(control_type='ListItem'):
                newMessage=chatList.children(control_type='ListItem')[-1]
                runtime_id=newMessage.element_info.runtime_id
                if runtime_id!=initial_runtime_id: 
                    total+=1
                    if newMessage.class_name()=='mmui::ChatTextItemView':
                        texts.append(newMessage.window_text())
                        dialog_window.restore()
                        is_my_bubble=Tools.is_my_bubble(dialog_window,newMessage)
                        if not is_my_bubble:
                            reply_content=callback(newMessage.window_text(),contexts)
                            if reply_content is not None:
                                input_edit.set_text(reply_content)
                                pyautogui.hotkey('alt','s')
                    if newMessage.class_name()=='mmui::ChatBubbleItemView' and newMessage.window_text()[:2]==link_label:
                        link_count+=1 
                    if newMessage.class_name()=='mmui::ChatBubbleReferItemView' and newMessage.window_text()==image_labal:
                        image_count+=1      
                    if newMessage.class_name()=='mmui::ChatBubbleReferItemView' and video_label in newMessage.window_text():
                        video_count+=1
                    if newMessage.class_name()=='mmui::ChatBubbleItemView' and file_label in newMessage.window_text():
                        filename=file_pattern.search(newMessage.window_text()).group(1)
                        filepath=os.path.join(chatfile_folder,timestamp,filename)
                        files.append(filepath)
                    initial_runtime_id=runtime_id
        media_count=image_count+video_count
        SystemSettings.close_listening_mode()
        if close_dialog_window:dialog_window.close()
        #最后结束时再批量复制到target_folder,不在循环里逐个复制是考虑到若文件过大(几百mb)没有自动下载完成移动不了
        if save_file and files:SystemSettings.copy_files(files,file_folder)#文件复制粘贴到target_folder/Files内
        if save_media and media_count:Messages.save_media(friend=friend,number=media_count,target_folder=target_folder)#保存图片到target_folder/Images内
        details={'新消息总数':total,'文本数量':len(texts),'文件数量':len(files),'图片数量':image_count,'视频数量':video_count,'链接数量':link_count,'文本内容':texts}
        return details
    

class Call():
    @staticmethod
    def voice_call(friend:str,is_maximize:bool=None,close_weixin:bool=None)->(WindowSpecification|None):
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
        is_group=Tools.is_group_chat(main_window)
        voice_call_button=main_window.child_window(**Buttons.VoiceCallButton)
        current_version=version.parse(GlobalConfig.version)
        old_version=version.parse('4.1.7')#4.1.8开始微信把语言和视频电话合并在顶部
        if not is_group:
            if current_version>old_version:
                voice_call_button.click_input()
                pyautogui.press('down')
                pyautogui.press('enter')
            else:
                voice_call_button=main_window.child_window(**Buttons.VoiceCallButton)
                voice_call_button.click_input()
            VoipCall_window=Tools.move_window_to_center(Windows.VoipCallWindow)
        if is_group:
            print(f'不支持群聊语音电话(SessionPicker-Window Ui自动化有Bug,微信会卡死崩溃！')
            VoipCall_window=None
        if close_weixin:main_window.close()
        return VoipCall_window

    @staticmethod
    def video_call(friend:str,is_maximize:bool=None,close_weixin:bool=None)->(WindowSpecification|None):
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
        is_group=Tools.is_group_chat(main_window)
        current_version=version.parse(GlobalConfig.version)
        old_version=version.parse('4.1.7')#4.1.8开始微信把语言和视频电话合并在顶部
        if not is_group: 
            if current_version>old_version:
                voice_call_button=main_window.child_window(**Buttons.VoiceCallButton)
                voice_call_button.click_input()
                pyautogui.press('down',presses=2)
                pyautogui.press('enter')
            else:
                video_call_button=main_window.child_window(**Buttons.VideoCallButton)
                video_call_button.click_input()
            VoipCall_window=Tools.move_window_to_center(Windows.VoipCallWindow)
        if is_group:
            VoipCall_window=None
            print(f'不支持群聊视频电话(SessionPicker-Window Ui自动化有Bug,微信会卡死崩溃！')
        if close_weixin:main_window.close()
        return VoipCall_window

class Collections():
    
    @staticmethod
    def cardLink_to_url(number:int,delete:bool=False,delay:float=0.5,is_maximize:bool=None,close_weixin:bool=None)->dict[str,str]:
        '''该函数用来获取收藏界面内指定数量卡片链接的url
        Args:
            number:卡片链接的数量
            delete:复制链接后是否将该条卡片链接移除掉
            delay:复制链接后的等待时间,默认为0.5s,不要设置太低
            is_maximize:微信界面是否全屏,默认全屏
            close_weixin:任务结束后是否关闭微信,默认关闭
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin

        def copy_url(listitem):
            y=listitem.rectangle().mid_point().y#竖直方向上居中,水平方向上靠右
            x=listitem.rectangle().right-offset
            mouse.right_click(coords=(x,y))
            copylink_item.click_input()
            win32clipboard.OpenClipboard()
            url=win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            if delete:
                mouse.right_click(coords=(x,y))
                deletelink_item.click_input()
                delete_button.click_input()
            time.sleep(delay)#0.3是极限,等待复制到剪贴板标签消失
            return url
        links=dict()
        offset=120#固定的offset,右键都在右边点
        timestamp_pattern=Regex_Patterns.Article_Timestamp_pattern
        main_window=Navigator.open_collections(is_maximize=is_maximize)
        copylink_item=main_window.child_window(**MenuItems.CopyLinkMenuItem)
        deletelink_item=main_window.child_window(**MenuItems.DeleteMenuItem)
        delete_button=main_window.child_window(**Buttons.DeleteButton)
        link_item=main_window.child_window(**ListItems.LinkListItem)
        if not link_item.exists(timeout=0.1):
            return links
        link_item.double_click_input()
        link_list=main_window.child_window(**Lists.LinkList)
        link_list.type_keys('{END}')
        last_item=link_list.children(control_type='ListItem')[-2].window_text()
        link_list.type_keys('{HOME}')
        link_list.type_keys('{DOWN}')
        selected_item=[listitem for listitem in link_list.children(control_type='ListItem') if listitem.has_keyboard_focus() and listitem.window_text()!=''][0]
        rectangle=selected_item.rectangle()
        side_x=rectangle.right-15
        center_y=rectangle.mid_point().y
        while selected_item.window_text()!=last_item:#while循环的结束条件是到达底部
            url=copy_url(selected_item)
            title=selected_item.window_text()[2:]#前两个字是固定的,为链接二字,后边的文本才是需要的
            title=timestamp_pattern.sub('',title)#替换掉时间戳
            links[url]=title
            mouse.click(coords=(side_x,center_y))
            link_list.type_keys('{DOWN}',pause=0.15)
            selected_item=[listitem for listitem in link_list.children(control_type='ListItem') if listitem.has_keyboard_focus() and listitem.window_text()!=''][0]
            if len(links)>=number:
                break
        if selected_item.window_text()==last_item:#已经到达底部需要将最后一条也记录一下
            last_item=link_list.children(control_type='ListItem')[-1]
            last_url=copy_url(last_item)
            last_title=last_item.window_text()[2:]#前两个字是固定的,为链接二字,后边的文本才是需要的
            last_title=timestamp_pattern.sub('',title)#替换掉时间戳
            links[last_url]=last_title
        if close_weixin:main_window.close()
        return links
    
    @staticmethod
    def collect_offAcc_articles(name:str,number:int,delay:float=0.3,is_maximize:bool=None,close_weixin:bool=None):
        '''
        该方法用来收藏一定数量的某个公众号的文章
        Args:
            name:公众号名称
            delay:点击收藏后的延迟等待时间
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        Returns:
            collected_num:实际收藏的数量
        '''
        #注意,公众号窗口内的内容pywinauto,dump_tree后与inspect看到的不一致
        #使用pywinauto只能定位到每篇文章的发布日期,点赞数量这样的文本,该方法便是基于此实现,不断右键可见的每篇文章的日期点击收藏
        #pagedown翻页重复记录达到收藏数量或者已到达底部没有文章日期可用于点击
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        clicked=[]
        collected_num=0
        seperate_window=Navigator.open_seperate_dialog_window(friend=name,is_maximize=is_maximize,close_weixin=close_weixin)
        homepage_button=seperate_window.child_window(**Buttons.HomePageButton)
        homepage_button.click_input()
        offAcc_window=Tools.move_window_to_center(Window=Panes.OfficialAccountPane)
        seperate_window.close()
        offAcc_window.maximize()
        rectangle=offAcc_window.rectangle()
        side_x,center_y=rectangle.right-45,rectangle.mid_point().y
        articles_link=offAcc_window.child_window(title='文章',control_type='Hyperlink')
        articles_link.click_input()
        container=offAcc_window.child_window(control_type='Group')
        timestamp_pattern=Regex_Patterns.Article_Timestamp_pattern
        while collected_num<number:
            visible_texts=[child for child in container.children(control_type='Text') if child.is_visible() and timestamp_pattern.search(child.window_text()) and child.element_info.runtime_id not in clicked]
            if visible_texts:
                for child in visible_texts:
                    collected_num+=1
                    time.sleep(delay)
                    child.right_click_input()
                    clicked.append(child.element_info.runtime_id)
                    # rec=child.rectangle()
                    # mouse.click(coords=(rec.mid_point().x+5,rec.mid_point().y+50))
                    offAcc_window.child_window(title='收藏',control_type='Text').click_input()
                    if collected_num>=number:
                        break
                mouse.click(coords=(side_x,center_y))
                pyautogui.press('pagedown',_pause=False)
            else:
                break
        offAcc_window.close()
        return collected_num
            
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
        #鼠标移动到朋友圈顶部右下角,点击头像按钮，激活弹出窗口
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
        profile_pane=desktop.window(**Windows.PopUpProfileWindow)
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
  
        #获取右侧好友信息面板
        def get_specific_info():
            wx_number='无'
            region='无'#好友的地区
            tag='无'#好友标签
            common_group_num='无'
            remark='无'#备注
            signature='无'#个性签名
            source='无'#好友来源
            descrption='无'#描述
            mobile='无'#电话号
            privacy='无'#朋友权限
            texts=contact_profile.descendants(control_type='Text')
            texts=[item.window_text() for item in texts]
            nickname=texts[0]
            if wxnum_label in texts:wx_number=texts[texts.index(wxnum_label)+1]#微信号
            if nickname_label in texts:nickname=texts[texts.index(nickname_label)+1]
            if region_label in texts:region=texts[texts.index(region_label)+1]
            if remark_label in texts:
                remark=texts[texts.index(remark_label)+1]
                if remark in labels:remark='无'
            if sharedgroups_label in texts:common_group_num=texts[texts.index(sharedgroups_label)+1]
            if signature_label in texts:signature=texts[texts.index(signature_label)+1]
            if source_label in texts:source=texts[texts.index(source_label)+1]
            if mobile_label in texts:mobile=texts[texts.index(mobile_label)+1]
            if description_label in texts:descrption=texts[texts.index(description_label)+1]
            if tags_label in texts:tag=texts[texts.index(tags_label)+1]
            if privacy_label in texts:privacy=texts[texts.index(privacy_label)+1]
            info={'昵称':nickname,'微信号':wx_number,'地区':region,'备注':remark,'电话':mobile,
            '标签':tag,'描述':descrption,'朋友权限':privacy,'共同群聊':f'{common_group_num}','个性签名':signature,'来源':source}
            return info
        
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        #所有的标签,这些标签的下一个便是其对应的值,即texts[texts.index(label)+1]
        wxnum_label=Special_Labels.WxNum
        nickname_label=Special_Labels.Nickname
        region_label=Special_Labels.Region
        remark_label=Special_Labels.Remark
        sharedgroups_label=Special_Labels.SharedGroups
        signature_label=Special_Labels.Signature
        source_label=Special_Labels.Source
        mobile_label=Special_Labels.Mobile
        description_label=Special_Labels.Description
        tags_label=Special_Labels.Tags
        privacy_label=Special_Labels.Privacy
        moments_label=Special_Labels.Moments
        friends_detail=[]
        labels={wxnum_label,nickname_label,region_label,remark_label,sharedgroups_label,signature_label,
        source_label,mobile_label,description_label,tags_label, privacy_label,moments_label}#联系人分区的标签
        #通讯录列表
        contact_list,main_window=Navigator.open_contacts(is_maximize=is_maximize)
        #右侧的自定义面板
        contact_custom=main_window.child_window(**Customs.ContactDetailCustom)
        #右侧自定义面板下的好友信息所在面板
        contact_profile=contact_custom.child_window(**Groups.ContactProfileGroup)
        area=(contact_custom.rectangle().mid_point().x,contact_custom.rectangle().mid_point().y)
        #联系人分区
        Tools.collapse_contacts(main_window,contact_list)
        contact_item=main_window.child_window(**ListItems.ContactsListItem)
        if contact_item.exists(timeout=0.1):
            total_num=int(re.search(r'\d+',contact_item.window_text()).group(0))
            if total_num>2000:interval=0.3
            if 1000<total_num<2000:interval=0.1
            if total_num<1000:interval=0
            contact_item.click_input()
            #有具体的数量,后续可以更换为for循环
            switch_to_first_friend()
            info=get_specific_info()
            friends_detail.append(info)
            mouse.move(coords=area)
            for _ in range(total_num-1):
                if interval:time.sleep(interval)
                pyautogui.keyDown('down',_pause=False)#不能press,press比keydown更频繁容易被检测,keydown是一直长按
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
            company='无'#好友的企业
            remark='无'#备注
            realname='无'#实名
            state='在职'#员工状态
            duty='无'#职务
            online_time='无'#在线时间
            working_time='无'#工作时间
            location='无'#地址
            texts=contact_profile.descendants(control_type='Text')
            texts=[item.window_text() for item in texts]
            nickname=texts[0] 
            company=texts[texts.index(enterprise_label)+1]#微信号
            if nickname_label in texts:nickname=texts[texts.index(nickname_label)+1]
            if remark_label in texts:
                remark=texts[texts.index(remark_label)+1]
                if remark==enterprise_label or remark==moments_label:
                    remark='无'
            if realname_label in texts:realname=texts[texts.index(realname_label)+1]
            if duty_label in texts:duty=texts[texts.index(duty_label)+1]
            if state_label in texts:state=texts[texts.index(state_label)+1]
            if workingtime_label in texts:working_time=texts[texts.index(workingtime_label)+1]
            if onlinetime_label in texts:online_time=texts[texts.index(onlinetime_label)+1]
            if location_label in texts:location=texts[texts.index(location_label)+1]
            info={'昵称':nickname,'备注':remark,'企业':company,'实名':realname,'在职状态':state,
            '职务':duty,'工作时间':working_time,'在线时间':online_time,'地址':location}
            no_need_labels.extend(info.values())
            others=[text for text in texts if text not in no_need_labels and text!=f'@{company}']
            if others:info['其他']=others
            return info
        
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        #所有的标签,这些标签的下一个是其对应的值
        wecom_label=Special_Labels.WeCom
        nickname_label=Special_Labels.Nickname
        enterprise_label=Special_Labels.EnterPrise
        moments_label=Special_Labels.Moments
        remark_label=Special_Labels.Remark
        realname_label=Special_Labels.RealName
        duty_label=Special_Labels.Duty
        state_label=Special_Labels.State
        workingtime_label=Special_Labels.WorkingTime
        onlinetime_label=Special_Labels.OnlineTime
        location_label=Special_Labels.Location
        messages_label=Special_Labels.Messages
        voicecall_label=Special_Labels.VoiceCall
        from_label=Special_Labels.From
        enterinfo_label=Special_Labels.EnterPriseInfomation
        videocall_label=Special_Labels.VideoCall
        #没用的文本信息
        no_need_labels=[enterprise_label,nickname_label,remark_label,realname_label,duty_label,state_label,moments_label,workingtime_label,
        onlinetime_label,location_label,messages_label,voicecall_label,videocall_label,enterinfo_label,from_label,wecom_label]
        friends_detail=[]
        #通讯录列表
        contact_list,main_window=Navigator.open_contacts(is_maximize=is_maximize)
        #右侧的自定义面板
        contact_custom=main_window.child_window(**Customs.ContactDetailCustom)
        #右侧自定义面板下的好友信息所在面板
        contact_profile=contact_custom.child_window(**Groups.ContactProfileGroup)
        area=(contact_custom.rectangle().mid_point().x,contact_custom.rectangle().mid_point().y)
        #企业微信联系人分区
        Tools.collapse_contacts(main_window,contact_list)
        wecom_item=main_window.child_window(**ListItems.WeComContactsListItems)
        if not wecom_item.exists(timeout=0.1):
            print(f'你没有企业微信联系人,无法获取企业微信好友信息！')
        if wecom_item.exists(timeout=0.1):
            total_num=int(re.search(r'\d+',wecom_item.window_text()).group(0))
            if total_num>2000:interval=0.3
            if 1000<total_num<2000:interval=0.1
            if total_num<1000:interval=0
            wecom_item.click_input()
            switch_to_first_friend()
            info=get_specific_info()
            friends_detail.append(info)
            mouse.move(coords=area)
            for _ in range(total_num+1):
                if interval:time.sleep(interval)
                pyautogui.keyDown('Down',_pause=False)
                info=get_specific_info()
                friends_detail.append(info)
            Tools.collapse_contacts(main_window,contact_list)
            if is_json:
                friends_detail=json.dumps(obj=friends_detail,ensure_ascii=False,indent=2)
        if close_weixin:main_window.close()
        return friends_detail 
    
    @staticmethod
    def get_serAcc_info(is_maximize:bool=None,close_weixin:bool=None,is_json:bool=False)->(list[dict]|str):
        '''
        该方法用来获取通讯录内服务号信息
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
            wx_number=texts[texts.index(wxnum_label)+1]
            description=texts[-2] if len(texts)==5 else '无'
            info={'名称':name,'微信号':wx_number,'描述':description}
            return info
        
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        wxnum_label=Special_Labels.WxNum
        friends_detail=[]
        #通讯录列表
        contact_list,main_window=Navigator.open_contacts(is_maximize=is_maximize)
        #右侧的自定义面板
        contact_custom=main_window.child_window(**Customs.ContactDetailCustom)
        area=(contact_custom.rectangle().mid_point().x,contact_custom.rectangle().mid_point().y)
        #右侧自定义面板下的好友信息所在面板
        contact_profile=contact_custom.child_window(**Groups.ContactProfileGroup)
        #企业微信联系人分区
        Tools.collapse_contacts(main_window,contact_list)
        service_item=main_window.child_window(**ListItems.ServiceAccountsListItem)
        if not service_item.exists(timeout=0.1):
            print(f'你没有关注过任何服务号,无法获取服务号信息！')
        if service_item.exists(timeout=0.1):
            total_num=int(re.search(r'\d+',service_item.window_text()).group(0))
            if total_num>2000:interval=0.3
            if 1000<total_num<2000:interval=0.1
            if total_num<1000:interval=0
            service_item.click_input()
            switch_to_first_friend()
            info=get_specific_info()
            friends_detail.append(info)
            mouse.move(coords=area)
            for _ in range(total_num):
                time.sleep(interval)
                pyautogui.keyDown('Down',_pause=False)
                info=get_specific_info()
                friends_detail.append(info)
            Tools.collapse_contacts(main_window,contact_list)
            friends_detail=remove_duplicates(friends_detail)
            if is_json:
                friends_detail=json.dumps(obj=friends_detail,ensure_ascii=False,indent=2)
        if close_weixin:main_window.close()
        return friends_detail 

    @staticmethod
    def get_offAcc_info(is_maximize:bool=None,close_weixin:bool=None,is_json:bool=False)->(list[dict]|str):
        '''
        该方法用来获取通讯录内公众号信息
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
            wx_number=texts[texts.index(wxnum_label)+1]
            description=texts[-2] if len(texts)==5 else '无'
            info={'名称':name,'微信号':wx_number,'描述':description}
            return info
        
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        wxnum_label=Special_Labels.WxNum
        friends_detail=[]
        #通讯录列表
        contact_list,main_window=Navigator.open_contacts(is_maximize=is_maximize)
        #右侧的自定义面板
        contact_custom=main_window.child_window(**Customs.ContactDetailCustom)
        area=(contact_custom.rectangle().mid_point().x,contact_custom.rectangle().mid_point().y)
        #右侧自定义面板下的好友信息所在面板
        contact_profile=contact_custom.child_window(**Groups.ContactProfileGroup)
        #企业微信联系人分区
        Tools.collapse_contacts(main_window,contact_list)
        official_item=main_window.child_window(**ListItems.OfficialAccountsListItem)
        if not official_item.exists(timeout=0.1):
            print(f'你没有关注过任何公众号,无法获取公众号信息！')
        if official_item.exists(timeout=0.1):
            total_num=int(re.search(r'\d+',official_item.window_text()).group(0))
            if total_num<1000:interval=0
            if 1000<total_num<2000:interval=0.1
            if total_num>2000:interval=0.3
            official_item.click_input()
            switch_to_first_friend()
            info=get_specific_info()
            friends_detail.append(info)
            mouse.move(coords=area)
            for _ in range(total_num):
                if interval:time.sleep(interval)
                pyautogui.keyDown('Down',_pause=False)
                info=get_specific_info()
                friends_detail.append(info)
            Tools.collapse_contacts(main_window,contact_list)
            friends_detail=remove_duplicates(friends_detail)
            if is_json:
                friends_detail=json.dumps(obj=friends_detail,ensure_ascii=False,indent=2)
        if close_weixin:main_window.close()
        return friends_detail 
        
    @staticmethod
    def get_groups_info(is_maximize:bool=None,close_weixin:bool=None)->list[str]:
        '''
        该函数用来获取我加入的所有群聊,原理是搜索个人昵称在群聊结果一栏中遍历查找
        Args:

            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        Returns:
            groups:所有已加入的群聊名称
        '''
        def switct_to_top():
            first_group=Tools.get_next_item(search_results,group_label)
            pyautogui.press('down')
            focused_item=[listitem for listitem in 
            search_results.children(control_type='ListItem') 
            if listitem.has_keyboard_focus()]
            while focused_item[0]!=first_group:#当前选中对象不是群聊标签下方第一个群聊时一直向下
                pyautogui.press('down')
                focused_item=[listitem for listitem in 
                search_results.children(control_type='ListItem') 
                if listitem.has_keyboard_focus()]

        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
       
        groups=[]
        viewAll_label=Special_Labels.ViewAll
        main_window=Navigator.open_weixin(is_maximize=is_maximize)
        myname=Contacts.check_my_info(close_weixin=False,is_maximize=is_maximize).get('昵称')
        chat_button=main_window.child_window(**SideBar.Weixin)
        chat_button.click_input()
        search=main_window.descendants(**Main_window.Search)[0]
        search.click_input()
        search.set_text(myname)
        search_results=main_window.child_window(title='',control_type='List')
        search_results.wait(wait_for='active',timeout=3)
        group_label=search_results.child_window(**ListItems.GroupLabelListItem)
        if group_label.exists(timeout=0.2):
            check_all_buttons=[button for button in search_results.children() if viewAll_label in button.window_text()]
            if check_all_buttons:
                total=int(re.search(r'\d+',check_all_buttons[0].window_text()).group(0))
                check_all_buttons[0].click_input()
                pyautogui.press('up',presses=20,_pause=False)#回到顶部,无法使用Home健
                #微信潜规则,展开全部按钮之上只显示3个搜索结果，
                switct_to_top()
                for _ in range(total+1):
                    #获取灰色的被选中的listitem记录
                    focused_item=[listitem for listitem in search_results.children(control_type='ListItem',class_name="mmui::SearchContentCellView") if listitem.has_keyboard_focus()]
                    if focused_item:
                        groups.append(focused_item[0].window_text())
                    else:
                        break
                    pyautogui.press('down',_pause=False)
            else:
                total=4
                #先定位到群聊这个灰色标签
                length=len(search_results.children(control_type='ListItem'))
                for i in range(length):
                    if search_results.children(control_type='ListItem')[i]==group_label:#群聊标签的下一个，也就是第一个共同群聊
                        break
                for listitem in search_results.children(control_type='ListItem')[i:i+total]:
                    if listitem.class_name()=="mmui::SearchContentCellView":
                        groups.append(listitem.window_text())#
                #从前往后逆序倒过来total个
        groups=groups[-total:]
        if close_weixin:main_window.close()
        return groups

    @staticmethod
    def get_common_groups(friend:str,is_maximize:bool=None,close_weixin:bool=None)->list[str]:
        '''
        该方法用来获取我与某些好友加入的所有共同群聊名称
        Args:

            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        Returns:
            groups:所有已加入的群聊名称
        '''
        def switct_to_top():
            first_group=Tools.get_next_item(search_results,group_label)
            pyautogui.press('up',presses=20,_pause=False)#回到顶部,无法使用Home健
            pyautogui.press('down')
            focused_item=[listitem for listitem in 
            search_results.children(control_type='ListItem') 
            if listitem.has_keyboard_focus()]
            while focused_item[0]!=first_group:#当前选中对象不是群聊标签下方第一个群聊时一直向下
                pyautogui.press('down')
                focused_item=[listitem for listitem in 
                search_results.children(control_type='ListItem') 
                if listitem.has_keyboard_focus()]

        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        groups=[]
        viewAll_label=Special_Labels.ViewAll
        main_window=Navigator.open_weixin(is_maximize=is_maximize)
        chat_button=main_window.child_window(**SideBar.Weixin)
        chat_button.click_input()
        search_bar=main_window.descendants(**Main_window.Search)[0]
        search_bar.click_input()
        search_bar.set_text(friend)
        time.sleep(1)#必须停顿1s等待加载出结果来
        search_results=main_window.child_window(title='',control_type='List')
        group_label=search_results.child_window(**ListItems.GroupLabelListItem)
        #微信搜索相关好友后会显示共同群聊，如果搜索结果中有群聊这个灰色标签的ListItem，说明有共同群聊
        if not group_label.exists():
            print(f'你与 {friend} 并无共同群聊!')
        else:#
            #只有当共同群聊数量大于4时候微信才会将其收起，此时有一个名为查看全部(\d+)的按钮
            check_all_buttons=[button for button in search_results.children() if viewAll_label in button.window_text()]
            if check_all_buttons:
                total=int(re.search(r'\d+',check_all_buttons[0].window_text()).group(0))
                check_all_buttons[0].click_input()#点一下查看全部按钮，此时focus的listitem是第共同群聊中的第四个
                switct_to_top()
                # pyautogui.press('up',presses=4,interval=0.1)
                #然后按total+1下按钮获取被选中的listitem的window_text*()
                for _ in range(total+1):
                    #获取灰色的被选中的listitem记录
                    focused_item=[listitem for listitem in search_results.children(control_type='ListItem',class_name="mmui::SearchContentCellView") if listitem.has_keyboard_focus()]
                    if focused_item:
                        groups.append(focused_item[0].window_text())
                        pyautogui.press('down',_pause=False)
                    else:
                        break
            else:#共同群聊总数小于4,最多就是3
                total=4
                #先定位到群聊这个灰色标签
                length=len(search_results.children(control_type='ListItem'))
                for i in range(length):
                    if search_results.children(control_type='ListItem')[i]==group_label:#群聊标签的下一个，也就是第一个共同群聊
                        break
                for listitem in search_results.children(control_type='ListItem')[i:i+total]:
                    if listitem.class_name()=="mmui::SearchContentCellView":
                        groups.append(listitem.window_text())#
            #从前往后逆序倒过来total个
            groups=groups[-total:]
        chat_button.click_input()
        if close_weixin:main_window.close()
        return groups
    
    @staticmethod
    def get_friend_profile(friend:str,search_pages:int=None,is_maximize:bool=None,close_weixin:bool=None):
        '''
        该函数用来获取单个好友的个人简介信息
        Args:
            friend:好友备注
            search_pages:在会话列表中查找好友时滚动列表的次数,默认为5,一次可查询5-12人,为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
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
        wxnum_label=Special_Labels.WxNum
        nickname_label=Special_Labels.Nickname
        region_label=Special_Labels.Region
        remark_label=Special_Labels.Remark
        sharedgroups_label=Special_Labels.SharedGroups
        signature_label=Special_Labels.Signature
        source_label=Special_Labels.Source
        mobile_label=Special_Labels.Mobile
        description_label=Special_Labels.Description
        tags_label=Special_Labels.Tags
        privacy_label=Special_Labels.Privacy
        wx_number='无'#好友的微信号
        region='无'#好友的地区
        tag='无'#好友标签
        common_group_num='无'
        remark='无'#备注
        signature='无'#个性签名
        source='无'#好友来源
        descrption='无'#描述
        mobile='无'#电话号
        privacy='无'#朋友权限
        #没用的文本信息
        no_need_labels=['企业','昵称：','备注','实名','职务','员工状态','朋友圈','工作时间',
        '在线时间','地址','发消息','语音聊天','视频聊天','企业信息','来自','企业微信']
        profile_pane,main_window=Navigator.open_friend_profile(friend=friend,search_pages=search_pages,is_maximize=is_maximize)
        text_uis=profile_pane.descendants(control_type='Text')
        texts=[item.window_text() for item in text_uis]
        nickname=texts[0]#昵称肯定有
        if wxnum_label in texts:wx_number=texts[texts.index(wxnum_label)+1]
        if nickname_label in texts:nickname=texts[texts.index(nickname_label)+1]
        if region_label in texts:region=texts[texts.index(region_label)+1]
        if remark_label in texts:
            remark=texts[texts.index(remark_label)+1]
            if remark in no_need_labels:remark='无'
        if sharedgroups_label in texts:common_group_num=texts[texts.index(sharedgroups_label)+1]
        if signature_label in texts:signature=texts[texts.index(signature_label)+1]
        if source_label in texts:source=texts[texts.index(source_label)+1]
        if mobile_label in texts:mobile=texts[texts.index(mobile_label)+1]
        if description_label in texts:  descrption=texts[texts.index(description_label)+1]
        if tags_label in texts:tag=texts[texts.index(tags_label)+1]
        if privacy_label in texts:privacy=texts[texts.index(privacy_label)+1]
        profile={'昵称':nickname,'微信号':wx_number,'地区':region,'备注':remark,'电话':mobile,
        '标签':tag,'描述':descrption,'朋友权限':privacy,'共同群聊':f'{common_group_num}','个性签名':signature,'来源':source}
        friend_text=main_window.child_window(title=friend,control_type='Text',found_index=1)
        friend_text.click_input()
        if close_weixin:main_window.close()
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
    
        texts=[]
        num_pattern=Regex_Patterns.GroupMember_Num_pattern
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
            contacts_manage_list.type_keys('{END}',pause=1)
            last=contacts_manage_list.children(control_type='ListItem',
            class_name="mmui::ContactsManagerControlSessionCell")[-1].window_text()
            contacts_manage_list.type_keys('{HOME}')
            listitems=contacts_manage_list.children(control_type='ListItem',class_name="mmui::ContactsManagerControlSessionCell")
            texts.extend([listitem.window_text() for listitem in listitems])
            while texts[-1]!=last:
                contacts_manage_list.type_keys('{PGDN}')
                listitems=contacts_manage_list.children(control_type='ListItem',class_name="mmui::ContactsManagerControlSessionCell")
                texts.extend([listitem.window_text() for listitem in listitems])
            texts=remove_duplicates(texts)#去重,Texts内是群聊+(人数)构成的文本,如果群聊名称与人数都相同那就没法筛选了
            group_names,member_nums=get_specific_info(texts)#正则提取与替换便是群名与人数
            recent_groups=list(zip(group_names,member_nums))#不使用dict(zip)是考虑到可能有相同群聊的,dict key不能有重复
            contacts_manage.close()
            return recent_groups
    
    @staticmethod
    def check_new_friends(verify:bool=False,limit:int=8,clear:bool=False,is_maximize:bool=None,close_weixin:bool=None)->list[str]:
        '''
        该方法用来检查一遍通讯录中新的朋友的信息,可以通过验证被动添加好友
        Args:
            verify:是否通过好友验证同意添加好友
            limit:通过验证的上限数:单次≤8人,每日≤4次,间隔≥2小时,无论新老号超过这个频率大概率封号
            clear:是否删除单条验证消息,遍历结束后会全部删除
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        Returns:
            newfriends_detail:所有新朋友的信息
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        
        def clear_item(current_item):
            current_item.right_click_input()
            pyautogui.press('down')
            pyautogui.press('enter')
        
        def friend_verification(current_item):
            time.sleep(1)
            if verify and verify_button.exists(timeout=0.1):
                verify_button.click_input()
                confirm_button=verifyFriend_window.child_window(**Buttons.ConfirmButton)
                confirm_button.click_input()
                current_item.click_input()
                return True
            return False

        verified_num=0
        newfriends_detail=[]
        #通讯录列表
        contact_list,main_window=Navigator.open_contacts(is_maximize=is_maximize)
        #右侧的自定义面板
        chat_button=main_window.child_window(**SideBar.Weixin)
        contact_custom=main_window.child_window(**Customs.ContactDetailCustom)
        verify_button=contact_custom.child_window(**Buttons.VerifyNowButton)
        more_button=contact_custom.child_window(**Buttons.MoreButton)
        Tools.collapse_contacts(main_window,contact_list)
        #验证好友窗口
        verifyFriend_window=desktop.window(**Windows.VerifyFriendWindow2)
        #新的朋友联系人分区
        newfriend_item=main_window.child_window(**ListItems.NewFriendListItem)
        if not newfriend_item.exists(timeout=0.1):
            print(f'你没有新的朋友,无法获取新的朋友信息!')
        if newfriend_item.exists(timeout=0.1):
            newfriend_item.click_input()
            contact_list.type_keys('{END}')
            newfriends=[listitem for listitem in contact_list.children() if listitem.class_name()=='mmui::XTableCell']
            if newfriends:
                last=newfriends[-1].window_text()
                contact_list.type_keys('{HOME}')
                contact_list.type_keys('{DOWN}'*2)
                selected=[listitem for listitem in contact_list.children(control_type='ListItem') if listitem.is_selected()]
                while selected[0].window_text()!=last:
                    newfriends_detail.append(selected[0].window_text())
                    if verified_num<limit:
                        is_verified=friend_verification(selected[0])
                        if is_verified:verified_num+=1
                    if clear:
                        clear_item(selected[0])
                        contact_list.children(control_type='ListItem')[2].click_input()
                    else:
                        pyautogui.keyDown('down')
                    selected=[listitem for listitem in contact_list.children(control_type='ListItem') if listitem.is_selected()]
            if clear:clear_item(selected[0])
            contact_list.type_keys('{HOME}')
            Tools.collapse_contacts(main_window,contact_list)
        chat_button.click_input()
        if close_weixin:main_window.close()
        return newfriends_detail

class FriendSettings():
    '''关于好友设置的一些方法'''
    
    @staticmethod
    def add_new_friend(number:str,greetings:str=None,remark:str=None,chat_only:bool=False,is_maximize:bool=None,close_weixin:bool=None):
        '''
        该方法用来添加新朋友,不建议频繁使用,会封号!
        Args:
            number:微信号或手机号
            greetings:添加好友时的招呼用语
            remark:给对方的备注
            chat_only:朋友权限仅聊天
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        add_friend_pane,main_window=Navigator.open_add_friend_panel(is_maximize=is_maximize)
        search_edit=add_friend_pane.child_window(control_type='Edit')
        search_edit.set_text('')
        search_edit.type_keys(number,with_spaces=True)
        search_edit.type_keys('{ENTER}')
        time.sleep(1)
        contact_profile_view=add_friend_pane.child_window(**Groups.ContactProfileViewGroup)
        if contact_profile_view.exists(timeout=0.2):
            add_to_contact=contact_profile_view.child_window(**Buttons.AddToContactsButton)
            if add_to_contact.exists(timeout=2):
                add_to_contact.click_input()
                verify_friend_window=Tools.move_window_to_center(Window=Windows.VerifyFriendWindow)
                request_content_edit=verify_friend_window.child_window(control_type='Edit',found_index=0)
                remark_edit=verify_friend_window.child_window(control_type='Edit',found_index=1)
                chat_only_group=verify_friend_window.child_window(**Groups.ChatOnlyGroup)
                confirm_button=verify_friend_window.child_window(**Buttons.ConfirmButton)
                if greetings is not None:
                    request_content_edit.set_text(greetings)
                if remark is not None:
                    remark_edit.set_text(remark)
                if chat_only:
                    chat_only_group.click_input()
                confirm_button.click_input()
        add_friend_pane.close()
        if close_weixin:
            main_window.close()

    @staticmethod
    def mute_notification(friend:str,mute:int=0,fold_chat:int=0,search_pages:int=None,is_maximize:bool=None,close_weixin:bool=None):
        '''该方法用来将好友消息设置为免打扰和折叠聊天,只有在免打扰开启的时候才可以设置折叠聊天
        Args:
            friend:好友备注
            mute:关闭或设置为消息免打扰,0:关闭消息免打扰,1:开启消息免打扰
            fold_chat:是否折叠聊天,0:取消折叠聊天,1:开启折叠聊天
            search_pages:在会话列表中查找好友时滚动列表的次数,默认为5,一次可查询5-12人,为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭 
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if search_pages is None:
            search_pages=GlobalConfig.search_pages
        if mute not in {0,1}:
            raise ValueError('mute的取整为0或1!')
        if fold_chat not in {0,1}:
            raise ValueError('fold_chat的取整为0或1!')
        chatinfo_pane,main_window=Navigator.open_chatinfo(friend=friend,is_maximize=is_maximize,search_pages=search_pages)
        chatinfo_button=main_window.child_window(**Buttons.ChatInfoButton)       
        mute_notification=chatinfo_pane.child_window(**CheckBoxes.MuteNotificationsCheckBox)
        foldchat=chatinfo_pane.child_window(**CheckBoxes.FoldChatCheckBox)
        if not mute_notification.get_toggle_state() and mute==1:
            mute_notification.click_input()
        if mute_notification.get_toggle_state() and mute==0:
            mute_notification.click_input()
        if foldchat.exists(timeout=0.1):
            if fold_chat==1 and not foldchat.get_toggle_state():
                foldchat.click_input()
            if fold_chat==0 and foldchat.get_toggle_state():
                fold_chat.click_input()
        chatinfo_button.click_input()
        if close_weixin:
            main_window.close()

    @staticmethod
    def pin_chat(friend:str,state:int=0,search_pages:int=None,is_maximize:bool=None,close_weixin:bool=None):
        '''该方法用来将好友聊天置顶
        Args:
            friend:好友备注
            state:置顶或不置顶,0:不置顶,1:置顶
            search_pages:在会话列表中查找好友时滚动列表的次数,默认为5,一次可查询5-12人,为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭 
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if search_pages is None:
            search_pages=GlobalConfig.search_pages
        if state not in {0,1}:
            raise ValueError('state的取整为0或1!')
        chatinfo_pane,main_window=Navigator.open_chatinfo(friend=friend,is_maximize=is_maximize,search_pages=search_pages)
        chatinfo_button=main_window.child_window(**Buttons.ChatInfoButton)
        pinchat=chatinfo_pane.child_window(**CheckBoxes.PinChatCheckBox)
        if state==1 and not pinchat.get_toggle_state():
            pinchat.click_input()
        if state==0 and pinchat.get_toggle_state():
            pinchat.click_input()
        chatinfo_button.click_input()
        if close_weixin:
            main_window.close()

    @staticmethod
    def clear_chat_histpry(friend:str,search_pages:int=None,is_maximize:bool=None,close_weixin:bool=None):
        '''该方法用来清空与好友的聊天记录
        Args:
            friend:好友备注
            search_pages:在会话列表中查找好友时滚动列表的次数,默认为5,一次可查询5-12人,为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭 
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if search_pages is None:
            search_pages=GlobalConfig.search_pages
        chatinfo_pane,main_window=Navigator.open_chatinfo(friend=friend,is_maximize=is_maximize,search_pages=search_pages)
        chatinfo_button=main_window.child_window(**Buttons.ChatInfoButton)
        clear_chat_history_button=chatinfo_pane.child_window(**Buttons.ClearChatHistoryButton)
        empty_button=main_window.child_window(**Buttons.EmptyButton)
        clear_chat_history_button.click_input()
        empty_button.click_input()
        chatinfo_button.click_input()
        if close_weixin:
            main_window.close()

    @staticmethod
    def change_privacy(friend:str,chat_privacy:int=1,sns_privacy:int=0,search_pages:int=None,is_maximize:bool=None,close_weixin:bool=None):
        '''该方法用来设置好友权限
        Args:
            friend:好友备注
            chat_privacy:0:仅聊天,1:聊天,朋友圈,微信运动等
            sns_privacy:0:取消所有朋友圈权限,1:不让他看,2:不看他
            search_pages:在会话列表中查找好友时滚动列表的次数,默认为5,一次可查询5-12人,为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭 
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if search_pages is None:
            search_pages=GlobalConfig.search_pages
        if chat_privacy not in {0,1}:
            raise ValueError('chat_privacy的取整为0或1!')
        if sns_privacy not in {0,1,}:
            raise ValueError('sns_privac的取整为0,1,!')
        profile_pane,main_window=Navigator.open_friend_profile(friend=friend,is_maximize=is_maximize)
        chatinfo_button=main_window.child_window(**Buttons.ChatInfoButton)
        more_button=profile_pane.child_window(**Buttons.MoreButton)
        more_button.click_input()
        pyautogui.press('down',presses=2)
        pyautogui.press('enter')
        privacy_window=desktop.window(**Windows.PrivacyWindow) if '4.1.9' in GlobalConfig.version else profile_pane
        open_privacy_group=privacy_window.child_window(**Groups.OpenPrivacyGroup)
        chat_only_group=privacy_window.child_window(**Groups.ChatOnlyGroup)
        check_box1=privacy_window.child_window(**CheckBoxes.DontShowOthersCheckBox)
        check_box2=privacy_window.child_window(**CheckBoxes.DontSeeOthersCheckBox)
        if chat_privacy==1:
             open_privacy_group.click_input()
        if chat_privacy==0:
            chat_only_group.click_input()
        if check_box1.exists(timeout=0.1):
            if sns_privacy==0:
                if check_box1.get_toggle_state():
                    check_box1.click_input()
                if check_box2.get_toggle_state():   
                    check_box2.click_input()                                                    
            if sns_privacy==1: 
                if not check_box1.get_toggle_state():
                    check_box1.click_input()
            if sns_privacy==2:
                if not check_box2.get_toggle_state():
                    check_box2.click_input()
        complete_button=profile_pane.child_window(**Buttons.FinishButton)
        if complete_button.exists():
            complete_button.click_input()
        chatinfo_button.click_input()
        if close_weixin:
            main_window.close()

    @staticmethod
    def star_friend(friend:str,state:int=1,search_pages:int=None,is_maximize:bool=None,close_weixin:bool=None):
        '''该方法用来将好友设为星标朋友或取消星标朋友
        Args:
            friend:好友备注
            state:设置为星标朋友还是取消设置为星标朋友
            search_pages:在会话列表中查找好友时滚动列表的次数,默认为5,一次可查询5-12人,为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭 
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if search_pages is None:
            search_pages=GlobalConfig.search_pages
        if state not in {0,1}:
            raise ValueError('state的取整为0或1!')
        star=Special_Labels.Star
        unstar=Special_Labels.UnStar
        profile_pane,main_window=Navigator.open_friend_profile(friend=friend,is_maximize=is_maximize,search_pages=search_pages)
        chatinfo_button=main_window.child_window(**Buttons.ChatInfoButton)
        more_button=profile_pane.child_window(**Buttons.MoreButton)
        more_button.click_input()
        pyautogui.press('down',presses=4)
        menu=profile_pane.child_window(class_name='mmui::XMenu',title='Weixin')
        selected_item=[item for item in menu.children(control_type='MenuItem') if item.has_keyboard_focus()]
        if selected_item[0].window_text()==star and state==1:
            pyautogui.press('enter')
        if selected_item[0].window_text()==unstar and state==0:
            pyautogui.press('enter')
        chatinfo_button.click_input()
        if close_weixin:
            main_window.close()

    @staticmethod
    def delete_friend(friend:str,clear_chat_history:int=1,search_pages:int=None,is_maximize:bool=None,close_weixin:bool=None):
        '''该方法用来删除好友
        Args:
            friend:好友备注
            clear_chat_history:删除好友时是否勾选清空聊天记录,1清空,0不清空
            search_pages:在会话列表中查找好友时滚动列表的次数,默认为5,一次可查询5-12人,为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭 
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if clear_chat_history not in {0,1}:
            raise ValueError('clear_chat_history的取整为0或1!')
        profile_pane,main_window=Navigator.open_friend_profile(friend=friend,is_maximize=is_maximize,search_pages=search_pages)
        chatinfo_button=main_window.child_window(**Buttons.ChatInfoButton)
        more_button=profile_pane.child_window(**Buttons.MoreButton)
        more_button.click_input()
        pyautogui.press('down',presses=6)
        pyautogui.press('enter')
        check_box=profile_pane.child_window(title='',control_type='CheckBox')
        if not clear_chat_history:
            check_box.click_input()
        delete_button=profile_pane.child_window(**Buttons.DeleteButton)
        delete_button.click_input()
        chatinfo_button.click_input()
        if close_weixin:
            main_window.close()
    
    @staticmethod
    def block_friend(friend:str,state:int=0,search_pages:int=None,is_maximize:bool=None,close_weixin:bool=None):
        '''该方法用来将好友添加至黑名单或从黑名单移出
        Args:
            friend:好友备注
            state:将好友移出黑名单还是加入黑名单,0移出黑名单,1加入黑名单
            search_pages:在会话列表中查找好友时滚动列表的次数,默认为5,一次可查询5-12人,为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭 
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if search_pages is None:
            search_pages=GlobalConfig.search_pages
        if state not in {0,1}:
            raise ValueError('state的取整为0或1!')
        block=Special_Labels.Block
        unblock=Special_Labels.UnBlock
        profile_pane,main_window=Navigator.open_friend_profile(friend=friend,is_maximize=is_maximize,search_pages=search_pages)
        chatinfo_button=main_window.child_window(**Buttons.ChatInfoButton)
        more_button=profile_pane.child_window(**Buttons.MoreButton)
        more_button.click_input()
        pyautogui.press('down',presses=5)
        menu=profile_pane.child_window(class_name='mmui::XMenu',title='Weixin')
        selected_item=[item for item in menu.children(control_type='MenuItem') if item.has_keyboard_focus()]
        if selected_item[0].window_text()==block and state==1:
            pyautogui.press('enter')
            confirm_button=profile_pane.child_window(**Buttons.ConfirmButton)
            confirm_button.click_input()
        if selected_item[0].window_text()==unblock and state==0:
            pyautogui.press('enter')
        chatinfo_button.click_input()
        if close_weixin:
            main_window.close()
    
    @staticmethod
    def change_remark(friend:str,remark:str,description:str=None,phoneNum:str=None,clear_phoneNum:bool=False,search_pages:int=None,is_maximize:bool=None,close_weixin:bool=None):
        '''该方法用来修改好友备注,描述,电话号码等内容
        Args:
            friend:好友备注
            remark:待修改的备注
            description:对好友的描述
            phoneNum:电话号码
            clear_phoneNum:清空之前所有的电话号码
            search_pages:在会话列表中查找好友时滚动列表的次数,默认为5,一次可查询5-12人,为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭 
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if search_pages is None:
            search_pages=GlobalConfig.search_pages
        profile_pane,main_window=Navigator.open_friend_profile(friend=friend,is_maximize=is_maximize,search_pages=search_pages)
        chatinfo_button=main_window.child_window(**Buttons.ChatInfoButton)
        more_button=profile_pane.child_window(**Buttons.MoreButton)
        more_button.click_input()
        pyautogui.press('down',presses=1)
        pyautogui.press('enter')
        remarkAndtag_window=desktop.window(**Windows.EditContactWindow) if '4.1.9' in GlobalConfig.version else main_window.window(**Windows.EditContactWindow)
        remark_edit=remarkAndtag_window.child_window(control_type='Edit',found_index=0)
        clearPhoneNum_buttons=remarkAndtag_window.descendants(**Buttons.ClearPhoneNumButton)
        if clearPhoneNum_buttons and clear_phoneNum:
            for button in clearPhoneNum_buttons:
                button.click_input()
        if isinstance(phoneNum,str):
            addphone_button=remarkAndtag_window.child_window(**Buttons.AddPhoneNumButon)
            addphone_button.click_input()
            remarkAndtag_window.child_window(control_type='Edit',found_index=1).set_text(phoneNum)
        if isinstance(description,str):
            description_edit=remarkAndtag_window.child_window(control_type='Edit',found_index=2)
            description_edit.set_text(description)
        addphone_button=remarkAndtag_window.child_window(**Buttons.AddPhoneNumButon)
        remark_edit.set_text(remark)
        confirm_button=remarkAndtag_window.child_window(**Buttons.FinishButton)
        confirm_button.click_input()
        chatinfo_button.click_input()
        if close_weixin:
            main_window.close()
    
    @staticmethod
    def get_common_groups(friend:str,search_pages:int=None,is_maximize:bool=None,close_weixin:bool=None)->list[str]:
        '''
        该方法用来获取我与某些好友加入的所有共同群聊名称
        Args:
            friend:好友备注
            search_pages:在会话列表中查找好友时滚动列表的次数,默认为5,一次可查询5-12人,为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        Returns:
            groups:所有已加入的群聊名称
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if search_pages is None:
            search_pages=GlobalConfig.search_pages
        common_groups=[]
        profile_window,main_window=Navigator.open_friend_profile(friend=friend,is_maximize=is_maximize,search_pages=search_pages)
        chatinfo_button=main_window.child_window(**Buttons.ChatInfoButton) 
        shared_groups_label=profile_window.child_window(**Texts.SharedGroupsText)
        if shared_groups_label.exists(timeout=2):
            number_button=shared_groups_label.parent().descendants(control_type='Button',class_name='mmui::XMouseEventView')[0]
            total_num=int(number_button.window_text().replace('个','').replace('個',''))
            number_button.click_input()
            popup_window=main_window.window(**Windows.PopUpProfileWindow)
            shared_groups_list=popup_window.child_window(**Lists.CommonGroupList)
            shared_groups_list.type_keys('{END}')
            last_item=shared_groups_list.children()[-1].window_text()
            shared_groups_list.type_keys('{HOME}')
            while len(common_groups)<total_num:
                texts=[listitem.window_text() for listitem in shared_groups_list.children()]
                texts=[text for text in texts if text not in  common_groups]
                common_groups.extend(texts)
                shared_groups_list.type_keys('{PGDN}')
                if common_groups[-1]==last_item:
                    break
        profile_window.close()
        chatinfo_button.click_input() 
        if close_weixin:
            main_window.close()
        return common_groups

    # @staticmethod
    # # SessionPicker window无法ui自动化,微信直接白屏卡死程序崩溃！不信,可以尝试一下
    # def add_tag(friends:list[str],tag:str,is_maximize:bool=None,window_maximize:bool=None,close_weixin:bool=None):
    #     '''
    #     该方法用来批量给好友设置标签
    #     Args:
    #         friends:所有的好友备注列表
    #         tag:标签名字
    #         is_maximize:微信界面是否全屏，默认不全屏
    #         close_weixin:任务结束后是否关闭微信，默认关闭
    #     '''
    #     def session_picker():
    #         SessionPickerWindow=Windows.SessionPickerWindow
    #         SessionPickerWindow['title']='微信添加成员'
    #         session_pick_window=contacts_manage.child_window(**Windows.SessionPickerWindow)
    #         complete_button=session_pick_window.child_window(**Buttons.FinishButton)
    #         checkbox=session_pick_window.child_window(control_type='CheckBox',found_index=0)
    #         search_field=session_pick_window.child_window(control_type='Edit',found_index=0)
    #         search_field.click_input()
    #         for friend in friends:
    #             search_field.set_text(friend)
    #             time.sleep(1)
    #             checkbox.click_input()
    #             search_field.click_input()
    #             search_field.set_text('')
    #         complete_button.click_input()
    #     if is_maximize is None:
    #         is_maximize=GlobalConfig.is_maximize
    #     if close_weixin is None:
    #         close_weixin=GlobalConfig.close_weixin
    #     if window_maximize is None:
    #         window_maximize=GlobalConfig.window_maximize
    #     contacts_manage=Navigator.open_contacts_manage(is_maximize=is_maximize,window_maximize=window_maximize,close_weixin=close_weixin)
    #     add_button=contacts_manage.child_window(**Buttons.AddButton)
    #     tagListItem=contacts_manage.child_window(**ListItems.TagListItem)
    #     contacts_manage_list=contacts_manage.child_window(**Lists.ContactsManageList)
    #     Tools.collapse_contact_manage(contacts_manage)
    #     tagListItem.click_input()
    #     contacts_manage_list.type_keys('{END}')
    #     createLabelListItem=contacts_manage_list.children(**ListItems.CreateLabelListItem)[0]
    #     createLabelListItem.click_input()
    #     pyautogui.hotkey('ctrl','a')
    #     pyautogui.press('backspace')
    #     SystemSettings.copy_text_to_clipboard(tag)
    #     pyautogui.hotkey('ctrl','v')
    #     pyautogui.press('enter')
    #     add_button.click_input()
    #     session_picker()

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
                    SystemSettings.copy_text_to_clipboard(message)
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
                SystemSettings.copy_files_to_clipboard(filepaths_list=files)
                pyautogui.hotkey("ctrl","v")
                time.sleep(send_delay)
                pyautogui.hotkey('alt','s',_pause=False)
            else:
                files_num=len(files)
                rem=len(files)%9
                for i in range(0,files_num,9):
                    if i+9<files_num:
                        SystemSettings.copy_files_to_clipboard(filepaths_list=files[i:i+9])
                        pyautogui.hotkey('ctrl','v')
                        time.sleep(send_delay)
                        pyautogui.hotkey('alt','s',_pause=False)
                if rem:
                    SystemSettings.copy_files_to_clipboard(filepaths_list=files[files_num-rem:files_num])
                    pyautogui.hotkey('ctrl','v')
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
            files=[file for file in files if 0<os.path.getsize(file)<1073741824]#0到1g之间的文件才可以发送
        if not files:
            raise NoFilesToSendError
        main_window=Navigator.open_dialog_window(friend=friend,is_maximize=is_maximize)
        edit_area=main_window.child_window(**Edits.CurrentChatEdit)
        if not edit_area.exists(timeout=0.1):
            raise NotFriendError(f'非正常好友,无法发送文件!')
        if clear:
            edit_area=main_window.child_window(**Edits.CurrentChatEdit)
            edit_area.set_text('')
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
    def send_files_to_friends(friends:list[str],files_list:list[list[str]],
        with_messages:bool=False,messages_list:list[list[str]]=[],messages_first:bool=False,
        clear:bool=None,send_delay:float=None,is_maximize:bool=None,close_weixin:bool=None)->None:
        '''
        该方法用于给多个好友或群聊发送文件
        Args:
            friends:好友或群聊备注。格式:friends=["好友1","好友2","好友3"]
            files_list:待发送文件列表,格式[[一些文件],[另一些文件],...[]]
            with_messages:发送文件时是否给好友发消息。True发送消息,默认为False
            messages_list:待发送消息列表,格式:message=[[一些消息],[另一些消息]....]
            messages_first:先发送消息还是先发送文件,默认先发送文件
            clear:是否删除编辑区域已有的内容,默认删除。
            send_delay:发送单条消息延迟,单位:秒/s,默认0.2s。
            is_maximize:微信界面是否全屏,默认不全屏。
            close_weixin:任务结束后是否关闭微信,默认关闭
        注意! messages_list,files_list与friends长度需一致且顺序一致,否则会出现发错的尴尬情况
        '''
        def verify(Files):
            verified_files=dict()
            if len(Files)<len(friends):
                raise ValueError(f'friends与files_lists长度不一致!发送人{len(friends)}个,发送文件列表个数{len(Files)}')
            for friend,files in Files.items():         
                files=[file for file in files if os.path.isfile(file)]
                files=[file for file in files if 0<os.path.getsize(file)<1073741824]#文件大小不能超过1个G!
                if files:
                    verified_files[friend]=files
                if not files:
                    print(f'发给{friend}的文件列表内没有可发送的文件！')
            return verified_files

        
        def open_dialog_window_by_search(friend):
            search=main_window.descendants(**Main_window.Search)[0]
            search.click_input()
            search.set_text(friend)
            time.sleep(0.8)
            search_results=main_window.child_window(**Main_window.SearchResult)
            friend_listitem=Tools.get_search_result(friend=friend,search_result=search_results)
            if friend_listitem is not None:
                friend_listitem.click_input()
                edit_area=main_window.child_window(**Edits.CurrentChatEdit)
                if edit_area.exists(timeout=0.1):
                    edit_area.click_input()
                    return True
            return False
        
        #消息发送逻辑
        def send_messages(messages):
            for message in messages:
                if 0<len(message)<2000:
                    SystemSettings.copy_text_to_clipboard(message)
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
                SystemSettings.copy_files_to_clipboard(filepaths_list=files)
                pyautogui.hotkey("ctrl","v")
                time.sleep(send_delay)
                pyautogui.hotkey('alt','s',_pause=False)
            else:
                files_num=len(files)
                rem=len(files)%9#
                for i in range(0,files_num,9):
                    if i+9<files_num:
                        SystemSettings.copy_files_to_clipboard(filepaths_list=files[i:i+9])
                        pyautogui.hotkey('ctrl','v')
                        time.sleep(send_delay)
                        pyautogui.hotkey('alt','s',_pause=False)
                if rem:#余数
                    SystemSettings.copy_files_to_clipboard(filepaths_list=files[files_num-rem:files_num])
                    pyautogui.hotkey('ctrl','v')
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
        Files=dict(zip(friends,files_list))
        Files=verify(Files)
        if not Files:
            raise NoFilesToSendError
        Chats=dict(zip(friends,messages_list))
        main_window=Navigator.open_weixin(is_maximize=is_maximize)
        edit_area=main_window.child_window(**Edits.CurrentChatEdit)
        chat_button=main_window.child_window(**SideBar.Weixin)
        chat_button.click_input()
        if with_messages and messages_list:#文件消息一起发且messages_list不空
            for friend in Files:
                Navigator.open_dialog_window(friend=friend,is_maximize=is_maximize,search_pages=0)
                ret=open_dialog_window_by_search(friend)
                if clear:
                   edit_area.set_text('')
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
                    edit_area.set_text('')
                if ret:
                    files_to_send=Files.get(friend)
                    send_files(files_to_send)
                if not ret:
                     print(f'未能正确打开好友聊天窗口！')
        if close_weixin:
            main_window.close()

    @staticmethod
    def save_chatfiles(friend:str,number:int,target_folder:str=None,is_maximize:bool=None,close_weixin:bool=None):
        '''该方法用来导出与某个好友的聊天文件,过期未下载的无法导出
        Args:
            friend:好友或群聊的名称
            target_folder:导出文件存放的文件夹路径,不传入会自动在本地新建一个
            number:导出的文件数量
            is_maximize:微信界面是否全屏,默认不全屏。
            close_weixin:任务结束后是否关闭微信,默认关闭
        Returns:
            filepaths:导出的文件路径列表 
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin

        def is_duplicate_filename(original,filename):
            '''用来判断两个文件是否属于副本,比如test.csv与text(1).csv
            '''
            #os.path.splittext可以快速提取一个basename中的文件名称和后缀名
            #'简历.docx'使用os.path.splittext后得到‘简历’与'.docx'
            original_stem,original_extension=os.path.splitext(original)
            #pattern:主干相同+(n)+相同扩展名
            #简历.docx与简历(1).docx为副本
            pattern=re.compile(rf'^{re.escape(original_stem)}\(\d+\){re.escape(original_extension)}$') 
            return bool(pattern.match(filename))
        
        def extract_info(text:str):
            texts=text.split('|')
            filename=filename_pattern.search(texts[0]).group(0)
            timestamp=timestamp_pattern.search(texts[1]).group(1) 
            year=int(time.strftime('%Y'))
            month=int(time.strftime('%m'))
            timestamp_folder=time.strftime('%Y-%m')#默认当年当月
            if year_sep in timestamp and year_sep=='-':
                year=int(re.search(r'(\d{4})-\d{1,2}-\d{1,2}',timestamp).group(1))
            if year_sep in timestamp and year_sep=='年':
                year=int(re.search(r'(\d+)年',timestamp).group(1))
            if month_sep in timestamp and month_sep=='月':
                month=int(re.search(r'(\d+)月',timestamp).group(1))
            if month_sep in timestamp and month_sep=='-':
                month=int(re.search(r'\d{4}-(\d{1,2})-\d{1,2}',timestamp).group(1))
            timestamp_folder=f'{year}-{month}' if month>=10 else f'{year}-0{month}'
            return filename,timestamp_folder
        
        if target_folder is not None and not os.path.isdir(target_folder):
            raise NotFolderError(f'所选路径不是文件夹!无法保存聊天记录,请重新选择!')
        if target_folder is None:
            folder_name='save_files聊天文件保存'
            target_folder=os.path.join(os.getcwd(),folder_name,friend)
            os.makedirs(name=target_folder,exist_ok=True)
            print(f'未传入文件夹路径,聊天文件将保存至 {target_folder}')

        filepaths=[]
        filenames=[]
        year_sep=Special_Labels.YearSep
        month_sep=Special_Labels.MonthSep
        not_download=Special_Labels.NotDownloaded
        expired=Special_Labels.Expired
        send_interrupt=Special_Labels.SendInterrupt
        filename_pattern=Regex_Patterns.Filename_pattern
        timestamp_pattern=Regex_Patterns.Chafile_Timestamp_pattern
        chatfile_folder=Tools.where_chatfile_folder()
        filename_pattern=Regex_Patterns.Filename_pattern
        timestamp_pattern=Regex_Patterns.Chafile_Timestamp_pattern
        chatfile_window=Navigator.open_chatfiles(is_maximize=is_maximize,close_weixin=close_weixin)
        empty_button=chatfile_window.child_window(**Buttons.EmptyButton)
        if empty_button.exists(timeout=0.1):
            empty_button.click_input()
        all_item=chatfile_window.child_window(**ListItems.AllListItem)
        all_item.click_input()
        search_button=chatfile_window.child_window(title='',control_type='Button',class_name='mmui::XButton')
        search_button.click_input()
        SystemSettings.copy_text_to_clipboard(friend)
        pyautogui.hotkey('ctrl','v')
        fileList=chatfile_window.child_window(**Lists.FileList)
        search_result=chatfile_window.descendants(control_type='Text')[-1]
        total_num=int(re.search(r'\d+',search_result.window_text()).group(0))
        fileList.type_keys('{END}'*100)
        last_file=fileList.children(control_type='ListItem',class_name='mmui::FileListCell')[-1].window_text()
        fileList.type_keys('{HOME}')
        labels=[listitem.window_text() for listitem in fileList.children(control_type='ListItem',class_name='mmui::FileListCell')]
        labels=[label for label in labels if (not_download not in label) or (expired not in label) or (send_interrupt not in label)]
        while len(labels)<number:
            fileList.type_keys('{PGDN}')
            last=fileList.children(control_type='ListItem',class_name='mmui::FileListCell')[-1].window_text()
            texts=[listitem.window_text() for listitem in fileList.children(control_type='ListItem',class_name='mmui::FileListCell')]
            texts=[file for file in texts if file not in labels]
            labels.extend(texts)
            if len(labels)>=total_num:#大于等于总数
                break
            if last==last_file:#到达底部
                break
        labels=[label for label in labels if (not_download not in label) or (expired not in label) or (send_interrupt not in label)]
        for label in labels:
            filename,timestamp=extract_info(label)
            filepath=os.path.join(chatfile_folder,timestamp,filename)
            if os.path.exists(filepath):
                filenames.append(filename)
                filepaths.append(filepath)
        filepaths=filepaths[:number]
        fileList.type_keys('{HOME}')
        #微信聊天记录中的文件名存在n个文件共用一个名字的情况
        ##比如;给文件传输助手同时发6次'简历.docx',那么在聊天记录页面中显示的是六个名为简历.docx的文件
        #但,实际上这些名字相同的文件,在widnows系统下的微信聊天文件夹内
        #会按照: 文件名(1).docx,文件名(2).docx...文件名(n-1).docx,文件名.docx的格式来存储
        #因此,这里使用内置Counter函数,来统计每个路径重复出现的次数,如果没有重复那么count是1
        repeat_counts=Counter(filepaths)#filepaths是刚刚遍历聊天记录列表按照基址+文件名组合而成的路径列表
        #如果有重复的就找到这个月份的文件夹内的所有重复文件全部移动
        for filepath,count in repeat_counts.items():
            if count>1:#重复次数大于1
                #从filepath中得到文件名与上一级目录
                folder,filename=os.path.split(filepath)#folder为同名文件的上一级文件夹
                #os.listdir()列出上一级文件夹然后遍历,查找所有包含纯文件名的文件,然后使用os.path.join将其与folder结合
                #samefilepaths中的是所有名字重复但实际上是:'文件(1).docx,文件名(2).docx,..文件名(n-1).docx,文件名.docx'格式的文件的路径
                samefilepaths=[os.path.join(folder,file) for file in os.listdir(folder) if is_duplicate_filename(filename,file)]
                SystemSettings.copy_files(samefilepaths,target_folder)
            else:#没有重复的直接移动就行
                #当然还得保证,folder_path里没有该文件
                SystemSettings.copy_file(filepath,target_folder)
        chatfile_window.close()
        return filepaths

    @staticmethod
    def export_recent_files(target_folder:str=None,is_maximize:bool=None,close_weixin:bool=None):
        ''' 该方法用来导出最近打开使用的文件,过期未下载的无法导出
        Args:
            target_folder:导出文件存放的文件夹路径,不传入会自动在本地新建一个
            is_maximize:微信界面是否全屏,默认不全屏。
            close_weixin:任务结束后是否关闭微信,默认关闭
        Returns:
            filepaths:导出的文件路径列表 
        '''
        def is_duplicate_filename(original,filename):
            '''用来判断两个文件是否属于副本,比如test.csv与text(1).csv
            '''
            #os.path.splittext可以快速提取一个basename中的文件名称和后缀名
            #'简历.docx'使用os.path.splittext后得到‘简历’与'.docx'
            original_stem,original_extension=os.path.splitext(original)
            #pattern:主干相同+(n)+相同扩展名
            #简历.docx与简历(1).docx为副本
            pattern=re.compile(rf'^{re.escape(original_stem)}\(\d+\){re.escape(original_extension)}$') 
            return bool(pattern.match(filename))
        
        def extract_info(text:str):
            texts=text.split('|')
            filename=filename_pattern.search(texts[0]).group(0)
            timestamp=timestamp_pattern.search(texts[1]).group(1) 
            year=int(time.strftime('%Y'))
            month=int(time.strftime('%m'))
            timestamp_folder=time.strftime('%Y-%m')#默认当年当月
            if year_sep in timestamp and year_sep=='-':
                year=int(re.search(r'(\d{4})-\d{1,2}-\d{1,2}',timestamp).group(1))
            if year_sep in timestamp and year_sep=='年':
                year=int(re.search(r'(\d+)年',timestamp).group(1))
            if month_sep in timestamp and month_sep=='月':
                month=int(re.search(r'(\d+)月',timestamp).group(1))
            if month_sep in timestamp and month_sep=='-':
                month=int(re.search(r'\d{4}-(\d{1,2})-\d{1,2}',timestamp).group(1))
            timestamp_folder=f'{year}-{month}' if month>=10 else f'{year}-0{month}'
            return filename,timestamp_folder
        
        if target_folder and not os.path.isdir(target_folder):
            raise NotFolderError(f'所选路径不是文件夹!无法保存聊天记录,请重新选择!')
        if not target_folder:
            folder_name='export_recent最近聊天文件保存'
            os.makedirs(name=folder_name,exist_ok=True)
            target_folder=os.path.join(os.getcwd(),folder_name)
            print(f'未传入文件夹路径,聊天文件将保存至 {target_folder}')
       
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
    
        filenames=[]
        filepaths=[]
        year_sep=Special_Labels.YearSep
        month_sep=Special_Labels.MonthSep
        not_download=Special_Labels.NotDownloaded
        expired=Special_Labels.Expired
        send_interrupt=Special_Labels.SendInterrupt
        filename_pattern=Regex_Patterns.Filename_pattern
        timestamp_pattern=Regex_Patterns.Chafile_Timestamp_pattern
        chatfile_folder=Tools.where_chatfile_folder()
        chatfile_window=Navigator.open_chatfiles(is_maximize=is_maximize,close_weixin=close_weixin)
        recent_used=chatfile_window.child_window(**ListItems.RecentUsedListItem)
        recent_used.click_input()
        search_button=chatfile_window.child_window(title='',control_type='Button',class_name='mmui::XButton')
        search_button.click_input()
        fileList=chatfile_window.child_window(**Lists.FileList)
        fileList.type_keys('{END}'*5)
        last_file=fileList.children(control_type='ListItem',class_name='mmui::FileListCell')[-1].window_text()
        fileList.type_keys('{HOME}')
        labels=[listitem.window_text() for listitem in fileList.children(control_type='ListItem',class_name='mmui::FileListCell')]
        while labels[-1]!=last_file:
            fileList.type_keys('{PGDN}')
            listitems=fileList.children(control_type='ListItem',class_name='mmui::FileListCell')
            texts=[listitem.window_text() for listitem in listitems]
            texts=[file for file in texts if file not in labels]
            labels.extend(texts)
        labels=[label for label in labels if (not_download not in label) or (expired not in label) or (send_interrupt not in label)]
        for label in labels:
            filename,timestamp=extract_info(label)
            filepath=os.path.join(chatfile_folder,timestamp,filename)
            if os.path.exists(filepath):
                filenames.append(filename)
                filepaths.append(filepath)
        fileList.type_keys('{HOME}')
        # 微信聊天记录中的文件名存在n个文件共用一个名字的情况
        # #比如;给文件传输助手同时发6次'简历.docx',那么在聊天记录页面中显示的是六个名为简历.docx的文件
        # 但,实际上这些名字相同的文件,在widnows系统下的微信聊天文件夹内
        # 会按照: 文件名(1).docx,文件名(2).docx...文件名(n-1).docx,文件名.docx的格式来存储
        # 因此,这里使用内置Counter函数,来统计每个路径重复出现的次数,如果没有重复那么count是1
        repeat_counts=Counter(filepaths)#filepaths是刚刚遍历聊天记录列表按照基址+文件名组合而成的路径列表
        # 如果有重复的就找到这个月份的文件夹内的所有重复文件全部移动
        for filepath,count in repeat_counts.items():
            if count>1:#重复次数大于1
                #从filepath中得到文件名与上一级目录
                folder,filename=os.path.split(filepath)#folder为同名文件的上一级文件夹
                #os.listdir()列出上一级文件夹然后遍历,查找所有包含纯文件名的文件,然后使用os.path.join将其与folder结合
                #samefilepaths中的是所有名字重复但实际上是:'文件(1).docx,文件名(2).docx,..文件名(n-1).docx,文件名.docx'格式的文件的路径
                samefilepaths=[os.path.join(folder,file) for file in os.listdir(folder) if is_duplicate_filename(filename,file)]
                SystemSettings.copy_files(samefilepaths,target_folder)
            else:#没有重复的直接移动就行
                #当然还得保证,target_folder里没有该文件
                SystemSettings.copy_file(filepath,target_folder)
        chatfile_window.close()
        return filepaths
    
    @staticmethod
    def export_videos(year:str=time.strftime('%Y'),month:str=None,target_folder:str=None)->list[str]:
        '''
        该函数用来导出微信保存到本地的聊天视频,只有点击下载过的视频才可以被导出
        Args:
            year:年份,除非手动删除聊天视频否则一直保存,格式:YYYY:2025,2024
            month:月份,微信聊天视屏是按照YYYY年-XX月分批存储的格式:2025-12,2025-06
            target_folder:导出的聊天视频保存的位置,需要是文件夹
        Returns:
            exported_videos:导出的mp4视频路径列表
        '''
        folder_name=f'{year}-{month}微信聊天视频导出' if month else f'{year}微信聊天视频导出' 
        if target_folder is None:
            os.makedirs(name=folder_name,exist_ok=True)
            target_folder=os.path.join(os.getcwd(),folder_name)
            print(f'未传入文件夹路径,所有导出的微信聊天视频将保存至 {target_folder}')
        if target_folder is not None and not os.path.isdir(target_folder):
            raise NotFolderError(f'给定路径不是文件夹,无法导入保存聊天文件')
        exported_videos=[]
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
    def export_wxfiles(year:str=time.strftime('%Y'),month:str=None,target_folder:str=None)->list[str]:
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


class Settings():

    @staticmethod
    def change_style(style:int,is_maximize:bool=None,close_weixin:bool=None):
        '''
        该方法用来修改微信的主题样式
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
        DarkMode=Special_Labels.DarkMode
        LightMode=Special_Labels.LightMode
        settings_window=Navigator.open_settings(is_maximize=is_maximize,close_weixin=close_weixin)
        general_button=settings_window.child_window(**Buttons.GeneralButton)
        general_button.click_input()
        outline_text=settings_window.child_window(**Texts.OutLineText)
        outline_button=outline_text.parent().children()[1]
        current_style=outline_button.children(control_type='Text')[0].window_text()
        outline_button.click_input()
        #弹出的菜单无论怎么都无法定位到，干脆纯按键操作
        #顺序是固定的:跟随系统,浅色模式,深色模式
        #无论怎么说先回到顶部
        if current_style==LightMode:
            pyautogui.press('up')
        if current_style==DarkMode:
            pyautogui.press('up',presses=2)
        #回到顶部后根据传入的style来选择向下按几次
        if style==1:
            pyautogui.press('down')
        if style==2:
            pyautogui.press('down',presses=2)
        pyautogui.press('enter')
        print(f'已将微信主题设置为{style_map.get(style)}')
        settings_window.close()
    
    @staticmethod
    def change_language(language:int,is_maximize:bool=None,close_weixin:bool=None):
        '''
        该方法用来修改微信的语言
        Args:
            language:语言,0:跟随系统,1:简体中文,2:'English',3:'繁體中文'
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        language_map={0:'跟随系统',1:'简体中文',2:'English',3:'繁體中文'}
        settings_window=Navigator.open_settings(is_maximize=is_maximize,close_weixin=close_weixin)
        general_button=settings_window.child_window(**Buttons.GeneralButton)
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
        if confirm_button.exists(timeout=0.1):
            confirm_button.click_input()
        print(f'已将微信语言设置为{language_map.get(language)},如需进行后续自动化操作,请手动登录')

    @staticmethod
    def auto_download_size(size:int=1024,state:bool=True,is_maximize:bool=None,close_weixin:bool=None):
        '''该方法用来修改微信自动下载文件大小
        Args:
            size:大小,1~1024之间的整数
            state:是否开启自动下载文件
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if size<=0:
            raise ValueError(f'size取值在1-1024之间!')
        if size>1024:
            size=1024
        settings_window=Navigator.open_settings(is_maximize=is_maximize,close_weixin=close_weixin)
        input_filed=settings_window.child_window(control_type='Text',class_name='mmui::XLineField')
        checkbox=input_filed.parent().children(control_type='CheckBox')[0]
        if state:
            input_filed.click_input()
            SystemSettings.copy_text_to_clipboard(str(size))
            pyautogui.hotkey('ctrl','a',_pause=False)
            pyautogui.press('backspace')
            pyautogui.hotkey('ctrl','v',_pause=False)
            if not checkbox.get_toggle_state():
                checkbox.click_input()
            print(f'已开启自动下载小于{size}MB文件功能')
        if not state and checkbox.get_toggle_state():
            checkbox.click_input()
            print(f'已关闭自动下载文件功能')
        settings_window.close()
    
    @staticmethod
    def change_fontsize(value:int=2,is_maximize:bool=None,close_weixin:bool=None):
        '''
        该方法用来修改微信的字体大小
        Args:
            value:字体大小,1-9之间,2为标准
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:是否关闭微信，默认关闭
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if value<1 or value>10:
            raise ValueError(f"值必须在1到9 之间")
        settings_window=Navigator.open_settings(is_maximize=is_maximize,close_weixin=close_weixin)
        general_button=settings_window.child_window(**Buttons.GeneralButton)
        general_button.click_input()
        fontsize_text=settings_window.child_window(**Texts.FontSizeText)
        slider=fontsize_text.parent().children(control_type='Slider')[0]
        value_map={1:0,2:22,3:44,4:66,5:88,6:110,7:140,8:175,9:190}
        rec=slider.rectangle()
        y=rec.mid_point().y#y方向在中间
        x=rec.left+value_map.get(value)#增加offset然后点击,经过测试,value_map中的offset可以实现
        mouse.click(coords=(x,y))
        settings_window.close()
    
    @staticmethod
    def notification_alert(alert_map:dict={'newMessage':True,'Call':True,'Moments':True,'Game':True,'Interaction_only':True},
        is_maximize:bool=None,close_weixin:bool=None):
        '''
        该方法用于修改微信设置中的通知或声音标记
        Args:
            alert_map:微信通知标记字典,格式:{'newMessage':True,'Call':True,'Moments':True,'Game':True,'Interaction_only':True}
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:是否关闭微信，默认关闭
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        settings_window=Navigator.open_settings(is_maximize=is_maximize,close_weixin=close_weixin)
        notification_button=settings_window.child_window(**Buttons.NotificationButton)
        notification_button.click_input()
        newMessage_checkbox=settings_window.child_window(**CheckBoxes.newMessageAlertCheckBox)
        call_checkbox=settings_window.child_window(**CheckBoxes.CallAlertCheckBox)
        moments_checkbox=settings_window.child_window(**CheckBoxes.MomentsCheckBox)
        game_checkbox=settings_window.child_window(**CheckBoxes.GameCheckBox)
        interactionOnly_checkbox=settings_window.child_window(**CheckBoxes.InteractionOnlyCheckBox)
        #异或,不一样的才点checkbox
        if alert_map.get('newMessage') is not None:
            if alert_map.get('newMessage')^newMessage_checkbox.get_toggle_state():
                newMessage_checkbox.click_input()
        if alert_map.get('Call') is not None:
            if alert_map.get('Call')^call_checkbox.get_toggle_state():
                call_checkbox.click_input()
        if alert_map.get('Moments') is not None and moments_checkbox.exists(timeout=0.1):
            if alert_map.get('Moments')^moments_checkbox.get_toggle_state():
                moments_checkbox.click_input()
        if alert_map.get('Game') is not None and game_checkbox.exists(timeout=0.1):
            if alert_map.get('Game')^game_checkbox.get_toggle_state():
                game_checkbox.click_input()
        if alert_map.get('Interaction_only') is not None and interactionOnly_checkbox.exists(timeout=0.1):
            if alert_map.get('Interaction_only')^interactionOnly_checkbox.get_toggle_state():
                interactionOnly_checkbox.click_input()
        settings_window.close()

class Moments():

    @staticmethod
    def post_moments(texts:str='',medias:list[str]=[],is_maximize:bool=None,close_weixin:bool=None):
        '''该方法用来发布朋友圈
        Args:
            texts:朋友圈文本内容
            medias:mp4,jpg,png等多个图像或视频的路径列表
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        '''
        def build_path(medias):
            '''用来构造windows文件选择界面内选择多个文件时底部输入的路径'''
            path=''
            for media in medias:
                if os.path.exists(media):
                    path+=f'"{media}" '
            return path
        
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if not texts and not medias:
            raise ValueError(f'文本与图片视频至少要有一个!')
        if medias:
            paths=build_path(medias)
            if not paths:raise ValueError(f'medias列表内无可用图片或视频路径!')
        moments=Navigator.open_moments(is_maximize=is_maximize,close_weixin=close_weixin)
        post_button=moments.child_window(**Buttons.PostButton)
        post_button.right_click_input(),
        pyautogui.press('up',presses=2)
        if medias:
            pyautogui.press('enter')
            native_window=desktop.window(**Windows.NativeChooseFileWindow)
            edit=native_window.child_window(**Edits.NativeFileSaveEdit)
            edit.set_text(paths)
            pyautogui.hotkey('alt','o')
        if texts and not medias:
            pyautogui.press('down',presses=1)
            pyautogui.press('enter')
        publish_panel=moments.child_window(**Groups.SnsPublishGroup)
        if texts:
            text_input=publish_panel.child_window(**Edits.SnsEdit)
            text_input.click_input()
            text_input.set_text(texts)
        post_button=publish_panel.child_window(**Buttons.PostButton)
        post_button.click_input()

    @staticmethod
    def dump_recent_posts(recent:Literal['Today','Yesterday','Week','Month']='Today',number:int=None,is_maximize:bool=None,close_weixin:bool=None)->list[dict]:
        '''
        该方法用来获取最近一月内微信朋友圈内好友发布过的具体内容
        Args:
            recent:最近的时间,取值为['Today','Yesterday','Week','Month']
            number:指定的数量(如果传入了该参数那么按照recent和数量返回内容,如果不传入那么只按照recent的时间节点返回内容)
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        Returns:
            posts:朋友圈具体内容,list[dict]的格式,具体为[{'内容':xx,'图片数量':xx,'视频数量':xx,'发布时间':xx}]

        '''
        def save_media(listitem):
            #后期点击保存图片或视频的逻辑
            listitem.click_input()
            pass

        def parse_post(listitem:ListItemWrapper):
            '''获取朋友圈文本中的时间戳,图片数量,以及剩余内容'''
            video_num=0
            photo_num=0
            text=listitem.window_text()
            post_time=sns_timestamp_pattern.search(text).group(0)
            if GlobalConfig.language=='简体中文':
                contain_video_pattern=re.compile(rf'\s视频\s{post_time}')
                content_pattern=re.compile(rf'((\s包含\d+张图片\s)|(\s视频\s)).*{post_time}')
            if GlobalConfig.language=='English':
                contain_video_pattern=re.compile(rf'\sVideo\s{post_time}')
                content_pattern=re.compile(rf'((\sContain\s(\d+)\simage\(s\)\s)|(\sVideo\s)).*{post_time}')
            if GlobalConfig.language=='繁體中文':
                contain_video_pattern=re.compile(rf'\s影片\s{post_time}')
                content_pattern=re.compile(rf'((\s包含\s\d+\s張圖片\s)|(\s影片\s)).*{post_time}')
            if contain_image_pattern.search(text):
                photo_num=int(contain_image_pattern.search(text).group(1))
            if contain_video_pattern.search(text):
                video_num=1
            content=content_pattern.sub('',text)
            content=re.sub(r'^\s+','',content)
            return content,photo_num,video_num,post_time
        
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin

        recorded_num=0
        posts=[]
        sns_timestamp_pattern=Regex_Patterns.Sns_Timestamp_pattern#朋友圈好友发布内容左下角的时间戳
        contain_image_pattern=Regex_Patterns.Contain_Images_pattern#朋友圈包含1~9张图片
        not_contents=['mmui::TimelineCommentCell','mmui::TimelineCell','mmui::TimelineAdGridImageCell']#评论区，余下x条,广告,这三种不需要
        moments_window=Navigator.open_moments(is_maximize=is_maximize,close_weixin=close_weixin)
        win32gui.SendMessage(moments_window.handle,win32con.WM_SYSCOMMAND,win32con.SC_MAXIMIZE,0)
        moments_list=moments_window.child_window(**Lists.MomentsList)
        moments_list.type_keys('{HOME}')
        #微信朋友圈当天发布时间是xx分钟前,xx小时前,一周内的时间在7天内,且包含当天时间,同理一月内的时间在30天内,包含本周的时间
        month_days=Special_Labels.MonthDays
        week_days=Special_Labels.WeekDays
        yesterday=Special_Labels.Yesterday
        days_ago=Special_Labels.DaysAgo
        time.sleep(2)#等待一下刷新
        if moments_list.children(control_type='ListItem'):
            while True:
                listitems=[listitem for listitem in moments_list.children(control_type='ListItem') if listitem.class_name() not in not_contents]
                selected=[listitem for listitem in listitems if listitem.has_keyboard_focus()]
                if selected:
                    content,photo_num,video_num,post_time=parse_post(selected[0])
                    posts.append({'内容':content,'图片数量':photo_num,'视频数量':video_num,'发布时间':post_time})
                    recorded_num+=1
                    if isinstance(number,int) and recorded_num>=number:
                        break
                    if recent=='Today' and (yesterday in post_time or days_ago in post_time):#昨天或者x天前在时间戳里不属于今天了
                        break
                    if recent=='Yesterday' and days_ago in post_time:#当前的朋友圈内容发布时间没有天前,说明是当天和昨天
                        break
                    if recent=='Week' and post_time not in week_days:#当前的朋友圈内容发布时间不在一周的时间内
                        break
                    if recent=='Month' and post_time not in month_days:#当前的朋友圈内容发布时间不在一个月的时间内
                        break
                moments_list.type_keys('{DOWN}',pause=0.1)
            if recent=='Today':
                posts=[post for post in posts if  yesterday not in post.get('发布时间')]
            if recent=='Yesterday':
                posts=[post for post in posts if post.get('发布时间')==yesterday]
            if recent=='Week':
                posts=[post for post in posts if post.get('发布时间') in week_days]
            if recent=='Month':
                posts=[post for post in posts if post.get('发布时间') in month_days]
        moments_window.close()
        return posts
    
    @staticmethod
    def like_posts(recent:Literal['Today','Yesterday','Week','Month']='Today',number:int=None,callback:Callable[[str],str]=None,is_maximize:bool=None,close_weixin:bool=None)->list[dict]:
        '''
        该方法用来给朋友圈内最近发布的内容点赞和评论
        Args:
            recent:最近的时间,取值为['Today','Yesterday','Week','Month']
            callback:评论回复函数,入参为字符串是好友朋友圈的内容,返回值为要评论的内容
            number:数量,如果指定了一定的数量,那么点赞数量超过number时结束,如果没有则在recent指定的范围内全部点赞
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        Returns:
           posts:朋友圈内容,list[dict]的格式,具体为[{'内容':xx,'图片数量':xx,'视频数量':xx,'发布时间':xx}]
        '''
        def parse_listitem(listitem:ListItemWrapper):
            '''获取朋友圈文本中的时间戳,图片数量,以及剩余内容'''
            video_num=0
            photo_num=0
            text=listitem.window_text()
            post_time=sns_timestamp_pattern.search(text).group(0)
            if GlobalConfig.language=='简体中文':
                contain_video_pattern=re.compile(rf'\s视频\s{post_time}')
                content_pattern=re.compile(rf'((\s包含\d+张图片\s)|(\s视频\s)).*{post_time}')
            if GlobalConfig.language=='English':
                contain_video_pattern=re.compile(rf'\sVideo\s{post_time}')
                content_pattern=re.compile(rf'((\sContain\s(\d+)\simage\(s\)\s)|(\sVideo\s)).*{post_time}')
            if GlobalConfig.language=='繁體中文':
                contain_video_pattern=re.compile(rf'\s影片\s{post_time}')
                content_pattern=re.compile(rf'((\s包含\s\d+\s張圖片\s)|(\s影片\s)).*{post_time}')
            if contain_image_pattern.search(text):
                photo_num=int(contain_image_pattern.search(text).group(1))
            if contain_video_pattern.search(text):
                video_num=1
            content=content_pattern.sub('',text)
            content=re.sub(r'^\s+','',content)
            return content,photo_num,video_num,post_time
        
        def like(content_listitem:ListItemWrapper):
            #点赞操作
            mouse.move(coords=center_point)
            rectangle=content_listitem.rectangle()
            ColorMatch.click_gray_ellipsis_button(rectangle)
            if like_button.exists(timeout=0.1):
                like_button.click_input()

        def comment(content_listitem:ListItemWrapper,comment_listitem:ListItemWrapper,content:str):
            #评论操作
            mouse.move(coords=center_point)
            ellipsis_area=(content_listitem.rectangle().right-44,content_listitem.rectangle().bottom-15)#省略号按钮所处位置
            mouse.click(coords=ellipsis_area)
            reply=callback(content) 
            if comment_button.exists(timeout=0.1) and reply is not None:
                comment_button.click_input()
                pyautogui.hotkey('ctrl','a')
                pyautogui.press('backspace')
                SystemSettings.copy_text_to_clipboard(text=reply)
                pyautogui.hotkey('ctrl','v')
                rectangle=comment_listitem.rectangle()
                ColorMatch.click_green_send_button(rectangle,x_offset=70,y_offset=42)
               
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        
        posts=[]
        liked_num=0
        month_days=Special_Labels.MonthDays
        week_days=Special_Labels.WeekDays
        yesterday=Special_Labels.Yesterday
        days_ago=Special_Labels.DaysAgo
        sns_timestamp_pattern=Regex_Patterns.Sns_Timestamp_pattern#朋友圈好友发布内容左下角的时间戳
        contain_image_pattern=Regex_Patterns.Contain_Images_pattern#朋友圈包含1~9张图片
        not_contents=['mmui::TimelineCommentCell','mmui::TimelineCell','mmui::TimelineAdGridImageCell']#评论区，余下x条,广告,这三种不需要
        moments_window=Navigator.open_moments(is_maximize=is_maximize,close_weixin=close_weixin)
        time.sleep(2)#等待刷新
        like_button=moments_window.child_window(**Buttons.LikeButton)
        comment_button=moments_window.child_window(**Buttons.CommentButton)
        moments_list=moments_window.child_window(**Lists.MomentsList)
        center_point=(moments_list.rectangle().mid_point().x,moments_list.rectangle().mid_point().y)
        moments_list.type_keys('{HOME}')
        if moments_list.children(control_type='ListItem'):
            while True:
                moments_list.type_keys('{DOWN}',pause=0.1)
                selected=[listitem for listitem in moments_list.children(control_type='ListItem') if listitem.has_keyboard_focus()]
                if selected and selected[0].class_name() not in not_contents:
                    content,photo_num,video_num,post_time=parse_listitem(selected[0])
                    posts.append({'内容':content,'图片数量':photo_num,'视频数量':video_num,'发布时间':post_time})
                    like(selected[0])
                    liked_num+=1
                    if callback is not None:
                        comment_listitem=Tools.get_next_item(moments_list,selected[0])
                        comment(selected[0],comment_listitem,content)
                    if isinstance(number,int) and liked_num>=number:
                        break
                    if recent=='Today' and (yesterday in post_time or days_ago in post_time):
                        break
                    if recent=='Yesterday' and days_ago in post_time:#当前的朋友圈内容发布时间没有天前,说明是当天和昨天
                        break
                    if recent=='Week' and post_time not in week_days:#当前的朋友圈内容发布时间不在一周的时间内
                        break
                    if recent=='Month' and post_time not in month_days:#当前的朋友圈内容发布时间不在一个月的时间内
                        break
        if recent=='Today':
            posts=[post for post in posts if  yesterday not in post.get('发布时间')]
        if recent=='Yesterday':
            posts=[post for post in posts if post.get('发布时间')==yesterday]
        if recent=='Week':
            posts=[post for post in posts if post.get('发布时间') in week_days]
        if recent=='Month':
            posts=[post for post in posts if post.get('发布时间') in month_days]
        moments_window.close()
        return posts

    @staticmethod
    def dump_friend_posts(friend:str,number:int,save_detail:bool=False,target_folder:str=None,search_pages:int=None,is_maximize:bool=None,close_weixin:bool=None)->list[dict]:
        '''
        该方法用来获取某个好友的微信朋友圈的内一定数量的内容
        Args:
            friend:好友备注
            number:具体数量
            save_detail:是否保存好友单条朋友圈的具体内容到本地(图片,文本,内容截图)
            target_folder:save_detail所需的文件夹路径
            search_pages:在会话列表中查找好友时滚动列表的次数,默认为5,一次可查询5-12人,为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        Returns:
            posts:朋友圈具体内容,list[dict]的格式,具体为[{'内容':xx,'图片数量':xx,'视频数量':xx,'发布时间':xx}]
        '''
        def save_media(sns_detail_list:ListViewWrapper,photo_num:int,video_num:int,detail_folder:str,content:str):
            content_path=os.path.join(detail_folder,'内容.txt')
            capture_path=os.path.join(detail_folder,'内容截图.png')
            video_path=os.path.join(detail_folder,'朋友圈视频.mp4')
            #保存截图
            sns_detail_list.children(control_type='ListItem')[0].capture_as_image().save(capture_path)
            #保存内容
            with open(content_path,'w',encoding='utf-8') as f:
                f.write(content) if content else f.write(f'无文本内容')
            #保存视频
            if video_num: 
                content_listitem=sns_detail_list.children(control_type='ListItem',title='')[0]
                rectangle=content_listitem.rectangle()
                center_y=rectangle.mid_point().y
                side_x=rectangle.left+150 
                mouse.right_click(coords=(side_x,center_y))
                is_download=moments_window.child_window(**MenuItems.AddToFavoritesMenuItem).exists(timeout=0.1)
                pyautogui.doubleClick(x=side_x-10,y=center_y,interval=0.1)
                image_preview_window.right_click_input()
                while not is_download:
                    image_preview_window.right_click_input()
                    copy_item=image_preview_window.child_window(**MenuItems.CopyMenuItem)
                    if copy_item.exists(timeout=0.5):
                        is_download=True 
                    time.sleep(1)       
                pyautogui.press('down',presses=2)
                pyautogui.press('enter')
                time.sleep(3)#缓存到剪贴板
                SystemSettings.save_pasted_video(video_path)
                pyautogui.press('esc')
            #保存图片
            if photo_num:
                rec=sns_detail_list.rectangle()
                right_click_position=rec.mid_point().x+20,rec.mid_point().y+25
                comment_detail=sns_detail_list.children(control_type='ListItem',title='')[1]
                rec=comment_detail.rectangle()
                x,y=rec.left+120,rec.top-80
                mouse.click(coords=(x,y))
                pyautogui.press('left',presses=photo_num,interval=0.15)
                for i in range(photo_num):
                    sns_detail_list.right_click_input(coords=right_click_position)
                    moments_window.child_window(**MenuItems.CopyMenuItem).click_input()
                    path=os.path.join(detail_folder,f'{i}.png')
                    time.sleep(0.5)#0.5s缓存到剪贴板时间
                    SystemSettings.save_pasted_image(path)
                    pyautogui.press('right',interval=0.05)
                pyautogui.press('esc')
            

        def parse_friend_post(listitem:ListItemWrapper):
            '''获取朋友圈文本中的时间戳,图片数量,以及剩余内容'''
            video_num=0
            photo_num=0
            text=listitem.window_text()
            text=text.replace(friend,'')#好友
            post_time=sns_detail_pattern.search(text).group(0)
            if GlobalConfig.language=='简体中文':
                contain_video_pattern=re.compile(rf'\s视频\s{post_time}')
                content_pattern=re.compile(rf'((\s包含\d+张图片\s)|(\s视频\s)).*{post_time}')
            if GlobalConfig.language=='English':
                contain_video_pattern=re.compile(rf'\sVideo\s{post_time}')
                content_pattern=re.compile(rf'((\sContain\s(\d+)\simage\(s\)\s)|(\sVideo\s)).*{post_time}')
            if GlobalConfig.language=='繁體中文':
                contain_video_pattern=re.compile(rf'\s影片\s{post_time}')
                content_pattern=re.compile(rf'((\s包含\s\d+\s張圖片\s)|(\s影片\s)).*{post_time}')
            if contain_image_pattern.search(text):
                photo_num=int(contain_image_pattern.search(text).group(1))
            if contain_video_pattern.search(text):
                video_num=1
            content=content_pattern.sub('',text)
            content=re.sub(r'^\s+','',content)
            return content,photo_num,video_num,post_time

        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if search_pages is None:
            search_pages=GlobalConfig.search_pages
        if save_detail  and target_folder is None:
            target_folder=os.path.join(os.getcwd(),'dump_friend_posts朋友圈内容保存')
            print(f'未传入文件夹图片和内容将保存到{target_folder}内的 {friend} 文件夹下')
            os.makedirs(target_folder,exist_ok=True)
        if save_detail and (not os.path.exists(target_folder) or not os.path.isdir(target_folder)):
            raise NotFolderError
        if save_detail and target_folder is not None:
            friend_folder=os.path.join(target_folder,f'{friend}')
            os.makedirs(friend_folder,exist_ok=True)
        posts=[]
        recorded_num=0
        sns_detail_pattern=Regex_Patterns.Snsdetail_Timestamp_pattern#朋友圈好友发布内容左下角的时间戳pattern
        contain_image_pattern=Regex_Patterns.Contain_Images_pattern#朋友圈包含1~9张图片
        not_contents=['mmui::AlbumBaseCell','mmui::AlbumTopCell']#置顶内容不需要
        image_preview_window=desktop.window(**Windows.ImagePreviewWindow)
        moments_window=Navigator.open_friend_moments(friend=friend,is_maximize=is_maximize,close_weixin=close_weixin,search_pages=search_pages)
        backbutton=moments_window.child_window(**Buttons.BackButton)
        #直接maximize不行,需要使用win32gui
        win32gui.SendMessage(moments_window.handle,win32con.WM_SYSCOMMAND,win32con.SC_MAXIMIZE,0)
        moments_list=moments_window.child_window(**Lists.MomentsList)
        sns_detail_list=moments_window.child_window(**Lists.SnsDetailList)
        moments_list.type_keys('{PGDN}')
        moments_list.type_keys('{PGUP}')
        contents=[listitem for listitem in moments_list.children(control_type='ListItem') if listitem.class_name() not in not_contents]
        if contents:
            while True:
                moments_list.type_keys('{DOWN}')
                selected=[listitem for listitem in moments_list.children(control_type='ListItem') if listitem.has_keyboard_focus()]
                if selected and selected[0].class_name() not in not_contents:
                    selected[0].click_input()
                    listitem=sns_detail_list.children(control_type='ListItem')[0]
                    content,photo_num,video_num,post_time=parse_friend_post(listitem)
                    posts.append({'内容':content,'图片数量':photo_num,'视频数量':video_num,'发布时间':post_time})
                    if save_detail:
                        detail_folder=os.path.join(friend_folder,f'{recorded_num}')
                        os.makedirs(detail_folder,exist_ok=True)
                        save_media(sns_detail_list,photo_num,video_num,detail_folder,content)
                    recorded_num+=1
                    if recorded_num>=number:
                        break
                    if sns_detail_list.exists(timeout=0.1):
                        backbutton.click_input()
                    if Tools.is_sns_at_bottom(moments_list,selected[0]):
                        break     
        moments_window.close()
        return posts

    @staticmethod
    def like_friend_posts(friend:str,number:int,callback:Callable[[str],str]=None,is_maximize:bool=None,close_weixin:bool=None)->list[dict]:
        '''
        该方法用来给某个好友朋友圈内发布的内容点赞和评论
        Args:
            friend:好友备注
            number:点赞或评论的数量
            callback:评论回复函数,入参为字符串是好友朋友圈的内容,返回值为要评论的内容
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        Returns:
           posts:朋友圈内容,list[dict]的格式,具体为[{'内容':xx,'图片数量':xx,'视频数量':xx,'发布时间':xx}]
        '''
        def parse_friend_post(listitem:ListItemWrapper):
            '''获取朋友圈文本中的时间戳,图片数量,以及剩余内容'''
            video_num=0
            photo_num=0
            text=listitem.window_text()
            text=text.replace(friend,'')#先去掉头尾的空格去掉换行符
            post_time=sns_detail_pattern.search(text).group(1)
            if GlobalConfig.language=='简体中文':
                contain_video_pattern=re.compile(rf'\s视频\s{post_time}')
                content_pattern=re.compile(rf'((\s包含\d+张图片\s)|(\s视频\s)).*{post_time}')
            if GlobalConfig.language=='English':
                contain_video_pattern=re.compile(rf'\sVideo\s{post_time}')
                content_pattern=re.compile(rf'((\sContain\s(\d+)\simage\(s\)\s)|(\sVideo\s)).*{post_time}')
            if GlobalConfig.language=='繁體中文':
                contain_video_pattern=re.compile(rf'\s影片\s{post_time}')
                content_pattern=re.compile(rf'((\s包含\s\d+\s張圖片\s)|(\s影片\s)).*{post_time}')
            if contain_image_pattern.search(text):
                photo_num=int(contain_image_pattern.search(text).group(1))
            if contain_video_pattern.search(text):
                video_num=1
            content=content_pattern.sub('',text)
            content=re.sub(r'^\s+','',content)
            return content,photo_num,video_num,post_time

        def like(listview:ListViewWrapper,content_listitem:ListItemWrapper):
            #点赞操作
            center_point=(listview.rectangle().mid_point().x,listview.rectangle().mid_point().y)
            mouse.move(coords=center_point)
            rectangle=content_listitem.rectangle()
            ColorMatch.click_gray_ellipsis_button(rectangle)
            if like_button.exists(timeout=0.1):
                like_button.click_input()

        def comment(listview:ListViewWrapper,content_listitem:ListItemWrapper,content:str):
            #评论操作
            comment_listitem=Tools.get_next_item(listview,content_listitem)
            center_point=(listview.rectangle().mid_point().x,listview.rectangle().mid_point().y)
            mouse.move(coords=center_point)
            ColorMatch.click_gray_ellipsis_button(content_listitem.rectangle())
            reply=callback(content) 
            if comment_button.exists(timeout=0.1) and reply is not None:
                comment_button.click_input()
                pyautogui.hotkey('ctrl','a')
                pyautogui.press('backspace')
                SystemSettings.copy_text_to_clipboard(text=reply)
                pyautogui.hotkey('ctrl','v')
                ColorMatch.click_green_send_button(comment_listitem.rectangle(),x_offset=70,y_offset=42)
              
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        posts=[]
        liked_num=0
        sns_detail_pattern=Regex_Patterns.Snsdetail_Timestamp_pattern#朋友圈好友发布内容左下角的时间戳pattern
        contain_image_pattern=Regex_Patterns.Contain_Images_pattern#朋友圈包含1~9张图片
        not_contents=['mmui::AlbumBaseCell','mmui::AlbumTopCell']#置顶内容不需要
        moments_window=Navigator.open_friend_moments(friend=friend,is_maximize=is_maximize,close_weixin=close_weixin)
        backbutton=moments_window.child_window(**Buttons.BackButton)
        #直接maximize不行,需要使用win32gui
        win32gui.SendMessage(moments_window.handle,win32con.WM_SYSCOMMAND,win32con.SC_MAXIMIZE,0)
        moments_list=moments_window.child_window(**Lists.MomentsList)
        sns_detail_list=moments_window.child_window(**Lists.SnsDetailList)
        like_button=moments_window.child_window(**Buttons.LikeButton)
        comment_button=moments_window.child_window(**Buttons.CommentButton)
        moments_list.type_keys('{PGDN}')
        moments_list.type_keys('{PGUP}')
        contents=[listitem for listitem in moments_list.children(control_type='ListItem') if listitem.class_name() not in not_contents]
        if contents:
            while True:
                moments_list.type_keys('{DOWN}')
                selected=[listitem for listitem in moments_list.children(control_type='ListItem') if listitem.has_keyboard_focus()]
                if selected and selected[0].class_name() not in not_contents:
                    selected[0].click_input()
                    content_listitem=sns_detail_list.children(control_type='ListItem')[0]
                    content,photo_num,video_num,post_time=parse_friend_post(content_listitem)
                    posts.append({'内容':content,'图片数量':photo_num,'视频数量':video_num,'发布时间':post_time})
                    like(sns_detail_list,content_listitem)
                    if callback is not None:
                        comment(sns_detail_list,content_listitem,content)
                    liked_num+=1
                    backbutton.click_input()
                    if Tools.is_sns_at_bottom(moments_list,selected[0]):
                        break
                if liked_num>=number:
                    break
        moments_window.close()
        return posts

class Messages():

    @staticmethod
    def send_messages_to_friend(friend:str,messages:list[str],at_members:list[str]=[],
        at_all:bool=False,search_pages:bool=None,clear:bool=None,
        send_delay:float=None,is_maximize:bool=None,close_weixin:bool=None)->None:
        '''
        该方法用于给单个好友或群聊发送信息
        Args:
            friend:好友或群聊备注。格式:friend="好友或群聊备注"
            messages:所有待发送消息列表。格式:message=["消息1","消息2"]
            at_members:群聊内所有需要@的群成员昵称列表(注意必须是群昵称)
            at_all:群聊内@所有人,默认为False
            search_pages:在会话列表中查找好友时滚动列表的次数,默认为5,一次可查询5-12人,为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
            send_delay:发送单条消息延迟,单位:秒/s,默认0.2s(0.1-0.2之间是极限)。
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
        if search_pages is None:
            search_pages=GlobalConfig.search_pages
        if clear is None:
            clear=GlobalConfig.clear
        if not messages:
            raise ValueError(f'不能发送空白消息!')
        #先使用open_dialog_window打开对话框
        main_window=Navigator.open_dialog_window(friend=friend,is_maximize=is_maximize,search_pages=search_pages)
        edit_area=main_window.child_window(**Edits.CurrentChatEdit)
        if not edit_area.exists(timeout=0.1):
            raise NotFriendError(f'非正常好友,无法发送消息')
        if clear:
            edit_area.set_text('')
        if at_all:
            At_all(main_window)
        if at_members:
            At(main_window,at_members)
        for message in messages:
            if 0<len(message)<2000:
                edit_area.click_input()
                SystemSettings.copy_text_to_clipboard(message)#不要直接set_text,直接set_text相当于默认clear了
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
    def message_chain(group:str,content:str=None,theme:str=None,example:str=None,description:str=None,search_pages:bool=None,
       is_maximize:bool=None,close_weixin:bool=None)->None:
        '''
        该方法用来在群聊中发起接龙
        Args:
            group:群聊备注
            content:发起接龙时自己所填的内容(默认是自己的群昵称)
            theme:接龙的主题
            example:接龙的例子
            description:接龙详细描述
            search_pages:在会话列表中查找群聊时滚动列表的次数,默认为5,一次可查询5-12人,为0时,直接从顶部搜索栏搜索好友信息打开聊天界面 
            is_maximize:微信界面是否全屏,默认不全屏。
            close_weixin:任务结束后是否关闭微信,默认关闭
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if search_pages is None:
            search_pages=GlobalConfig.search_pages
        #先使用open_dialog_window打开对话框
        main_window=Navigator.open_dialog_window(friend=group,is_maximize=is_maximize,search_pages=search_pages)
        edit_area=main_window.child_window(**Edits.CurrentChatEdit)
        if not edit_area.exists(timeout=0.1):
            raise NotFriendError(f'非正常好友,无法发送消息')
        if Tools.is_group_chat(main_window):
            edit_area.set_text('#接龙')
            pyautogui.press('down')
            pyautogui.press('enter')
            solitaire_window=main_window.child_window(**Windows.SolitaireWindow)
            solitaire_button=solitaire_window.child_window(**Buttons.SolitaireButton)
            solitaire_list=solitaire_window.child_window(**Lists.SolitaireList)
            if content is not None:
                SystemSettings.copy_text_to_clipboard(content)
                solitaire_list.click_input()#自己填写的内容正好在接龙列表的中间,所以直接click_input()
                pyautogui.hotkey('ctrl','a')#全选删除然后复制content
                pyautogui.press('backspace')
                pyautogui.hotkey('ctrl','v')
            if isinstance(theme,str):
                solitaire_window.child_window(control_type='Edit',found_index=0).set_text(theme)
            if isinstance(example,str):
                solitaire_window.child_window(control_type='Edit',found_index=1).set_text(example)
            if isinstance(description,str):
                text=solitaire_window.child_window(**Texts.AddContentText)
                rec=text.rectangle()
                position=rec.left+2,rec.mid_point().y
                mouse.click(coords=position)
                solitaire_window.child_window(control_type='Edit',found_index=2).set_text(description)
            solitaire_button.click_input()
        if close_weixin:
            main_window.close()

    @staticmethod
    def send_messages_to_friends(friends:list[str],messages:list[list[str]],clear:bool=None,
        send_delay:float=None,is_maximize:bool=None,close_weixin:bool=None)->None:
        '''
        该方法用于给多个好友或群聊发送信息
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
        def send_messages(friend):
            if clear:
               edit_area.set_text('')
            for message in Chats.get(friend):
                if 0<len(message)<2000:
                    edit_area.set_text(message)
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
        edit_area=main_window.child_window(**Edits.CurrentChatEdit)
        for friend in Chats:
            search=main_window.descendants(**Main_window.Search)[0]
            search.click_input()
            search.set_text(friend)
            time.sleep(0.8)
            search_results=main_window.child_window(title='',control_type='List')
            friend_button=Tools.get_search_result(friend=friend,search_result=search_results)
            if friend_button:
                friend_button.click_input()
                edit_area.click_input()
                send_messages(friend)
        Tools.cancel_pin(main_window)
        if close_weixin:
            main_window.close()

    @staticmethod
    def check_new_messages(is_maximize:bool=None,search_pages:int=None,close_weixin:bool=None):
    
        '''
        该函数用来检查一遍微信会话列表内的新消息
        Args:
            search_pages:打开好友聊天窗口时在会话列表中查找好友时滚动列表的次数,默认为5,一次可查询5-12人,为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        Returns:
            newMessages_dict
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if search_pages is None:
            search_pages=GlobalConfig.search_pages
        newMessages_dict={}
        main_window=Navigator.open_weixin(is_maximize=is_maximize)
        new_message_num=get_new_message_num(main_window,close_weixin=False)
        if new_message_num:
            new_messages=[]
            new_message_dict=scan_for_new_messages(main_window=main_window,is_maximize=is_maximize,close_weixin=False)
            for friend,num in new_message_dict.items():
                message=Messages.pull_messages(friend=friend,number=num,close_weixin=False,search_pages=search_pages)
                new_messages.append(message)
            newMessages_dict=dict(zip(new_message_dict.keys(),new_messages))
        if not new_message_num:
            print(f'未发现新消息')
        if close_weixin:
            main_window.close()
        return newMessages_dict
    
    #session_pick_window中使用ui自动化选择2个以上好友时微信会莫名奇妙白屏卡死，所以先暂时不实现这个方法了
    # @staticmethod
    # def forward_message(friends:list[str],message:str,clear:bool=None,
    #     send_delay:float=None,is_maximize:bool=None,close_weixin:bool=None)->None:
     
    #     if is_maximize is None:
    #         is_maximize=GlobalConfig.is_maximize
    #     if send_delay is None:
    #         send_delay=GlobalConfig.send_delay
    #     if close_weixin is None:
    #         close_weixin=GlobalConfig.close_weixin
    #     if clear is None:
    #         clear=GlobalConfig.clear
    #     if len(friends)<2:
    #         raise ValueError(f'friends数量不足2,无法转发消息!')
    #     def session_picker():
    #         session_pick_window=main_window.child_window(**Windows.SessionPickerWindow)
    #         send_button=session_pick_window.child_window(**Buttons.SendButton)
    #         checkbox=session_pick_window.child_window(control_type='CheckBox',found_index=0)
    #         rec=send_button.rectangle()
    #         x,y=rec.mid_point().x,rec.mid_point().y
    #         search_field=session_pick_window.child_window(control_type='Edit',found_index=0)
    #         search_field.click_input()
    #         for friend in friends[1:]:
    #             search_field.set_text(friend)
    #             checkbox.click_input()
    #         send_button.click_input()
    #     main_window=Navigator.open_dialog_window(friend=friends[0],is_maximize=is_maximize)
    #     edit_area=main_window.child_window(**Edits.CurrentChatEdit)
    #     chat_list=main_window.child_window(**Lists.FriendChatList)
    #     if not edit_area.exists(timeout=0.1):
    #         raise NotFriendError(f'非正常好友,无法发送消息')
    #     if clear:
    #         edit_area.set_text('')
    #     if len(message)==0:
    #         main_window.close()
    #         raise ValueError
    #     if 0<len(message)<2000:
    #         edit_area.set_text(message)
    #         time.sleep(send_delay)
    #         pyautogui.hotkey('alt','s',_pause=False)
    #     elif len(message)>2000:#字数超过200字发送txt文件
    #         SystemSettings.convert_long_text_to_txt(message)
    #         pyautogui.hotkey('ctrl','v',_pause=False)
    #         time.sleep(send_delay)
    #         pyautogui.hotkey('alt','s',_pause=False)
    #         warn(message=f"微信消息字数上限为2000,超过2000字部分将被省略,该条长文本消息已为你转换为txt发送",category=LongTextWarning)
    #     if len(friends)>1:
    #         listItems=chat_list.children(control_type='ListItem')
    #         message_sent=listItems[-1]
    #         rect=message_sent.rectangle()
    #         mouse.right_click(coords=(rect.right-100,rect.mid_point().y))
    #         forward_item=main_window.child_window(**MenuItems.ForwardMenuItem)
    #         forward_item.click_input()
    #         session_picker()
    #     if close_weixin:
    #         main_window.close()

    @staticmethod
    def dump_recent_sessions(recent:Literal['Today','Yesterday','Week','Month','Year']='Today',
        chat_only:bool=False,is_maximize:bool=None,close_weixin:bool=None)->list[tuple]:
        '''
        该函数用来获取会话列表内最近的聊天对象的名称,最后聊天时间
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
            #把名字发送时间最后一条消息内容拼接在一起作为unique_id
            #这三者完全一样的概率很小
            seen=set()
            result=[]
            for item in list:
                unique_id=item[0]+item[1]+item[2]
                if unique_id not in seen:
                    seen.add(unique_id)
                    result.append(item)
            return result
        
        def extract_info(listitem):
            timestamp=''
            pure_text=listitem.window_text().replace(SutckOnTop_label,'').replace(MuteNotifications_label,'')
            name=listitem.automation_id().replace('session_item_','')
            timestamp=timestamp_pattern.search(pure_text)
            if timestamp:timestamp=timestamp.group(0)    
            msg=pure_text.replace(f'{name}\n','').replace(f'\n{timestamp}\n','')
            return name,timestamp,msg

        #正则匹配获取时间
        def get_sending_time(listitem):
            pure_text=listitem.window_text().replace(SutckOnTop_label,'').replace(MuteNotifications_label,'')
            timestamp=timestamp_pattern.search(pure_text)
            if timestamp:return timestamp.group(0)
            return ''
        
        #根据recent筛选和过滤会话
        def filter_sessions(ListItems):
            ListItems=[ListItem for ListItem in ListItems if get_sending_time(ListItem)]
            if recent=='Year' or recent=='Month':
                ListItems=[ListItem for ListItem in ListItems if not year_pattern.search(get_sending_time(ListItem))]
            if recent=='Week':
                ListItems=[ListItem for ListItem in ListItems if '/' not in get_sending_time(ListItem)]
            if recent=='Today' or recent=='Yesterday':
                ListItems=[ListItem for ListItem in ListItems if ':' in get_sending_time(ListItem)]
            if chat_only:
                ListItems=[ListItem for ListItem in ListItems if extract_info(ListItem)[2]!='']
            return ListItems
        
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        
        sessions=[]#会话对象 ListItem
        SutckOnTop_label=Special_Labels.StuckonTop
        MuteNotifications_label=Special_Labels.MuteNotifications
        Yesterday_label=Special_Labels.Yesterday
        #符合year_pattern的肯定不是今年的
        year_pattern=re.compile(r'\d{4}/\d{2}/\d{2}')#
        thismonth=str(int(time.strftime('%m')))+'/'#去年
        #最右侧时间戳正则表达式:五种,2024/05/01,10/25,昨天,星期一,10:59,
        timestamp_pattern=Regex_Patterns.Session_Timestamp_pattern
        main_window=Navigator.open_weixin(is_maximize=is_maximize)
        chats_button=main_window.child_window(**SideBar.Weixin)
        session_list=main_window.child_window(**Main_window.SessionList)
        chats_button.click_input()
        scrollable=Tools.is_scrollable(session_list,back='end')
        if not scrollable:
            listItems=session_list.children(control_type='ListItem')
            listItems=filter_sessions(listItems)
            sessions.extend([extract_info(listitem) for listitem in listItems])
        if scrollable:
            last=session_list.children(control_type='ListItem')[-1].window_text()
            session_list.type_keys('{HOME}')
            time.sleep(1)
            while True:
                listItems=session_list.children(**ListItems.SessionListItem)
                filtered_listItems=filter_sessions(listItems)
                if not filtered_listItems:
                    break
                if listItems[-1].window_text()==last:
                    break
                sessions.extend([extract_info(listitem) for listitem in  filtered_listItems])
                session_list.type_keys('{PGDN}') 
            session_list.type_keys('{HOME}')
        sessions=remove_duplicates(sessions)
        if close_weixin:
            main_window.close()
        #进一步筛选
        if recent=='Yesterday':
            sessions=[session for session in sessions if Yesterday_label in session[1]]
        if recent=='Today':
            sessions=[session for session in sessions if Yesterday_label not in session[1]]
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
        def filter_sessions(listItems):
            listItems=[listItem for listItem in listItems if get_sending_time(listItem)]
            if chat_only:
                listItems=[listItem for listItem in listItems if extract_info(listItem)[2]!='']
            return listItems

        def get_sending_time(listitem):
            pure_text=listitem.window_text().replace(SutckOnTop_label,'').replace(MuteNotifications_label,'')
            timestamp=timestamp_pattern.search(pure_text)
            if timestamp:return timestamp.group(0)
            return ''
        
        def extract_info(listitem):
            timestamp=''
            pure_text=listitem.window_text().replace(SutckOnTop_label,'').replace(MuteNotifications_label,'')
            name=listitem.automation_id().replace('session_item_','')
            timestamp=timestamp_pattern.search(pure_text)
            if timestamp:timestamp=timestamp.group(0)    
            msg=pure_text.replace(f'{name}\n','').replace(f'\n{timestamp}\n','')
            return name,timestamp,msg
        
        def remove_duplicates(list):
            '''对sessions,这个list[tuple]对象去重'''
            #把名字，发送时间，还有最后一条消息内容拼接在一起作为unique_id
            #这三者完全一样的概率很小
            seen=set()
            result=[]
            for item in list:
                unique_id=item[0]+item[1]+item[2]
                if unique_id not in seen:
                    seen.add(unique_id)
                    result.append(item)
            return result
        
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin

        sessions=[]
        SutckOnTop_label=Special_Labels.StuckonTop
        MuteNotifications_label=Special_Labels.MuteNotifications
        #最右侧时间戳正则表达式:五种,2024/05/01,10/25,昨天,星期一,10:59,
        timestamp_pattern=Regex_Patterns.Session_Timestamp_pattern
        main_window=Navigator.open_weixin(is_maximize=is_maximize)
        chats_button=main_window.child_window(**SideBar.Weixin)
        session_list=main_window.child_window(**Main_window.SessionList)
        chats_button.click_input()
        scrollable=Tools.is_scrollable(session_list,back='end')
        if not scrollable:
           listItems=session_list.children(**ListItems.SessionListItem)
           filtered_listItems=filter_sessions(listItems)
           sessions.extend([extract_info(listitem) for listitem in filtered_listItems])
        if scrollable:
            time.sleep(1)
            listItems=session_list.children(**ListItems.SessionListItem)
            last=listItems[-1].window_text()
            session_list.type_keys('{HOME}')
            time.sleep(1)
            while True:
                listItems=session_list.children(**ListItems.SessionListItem)
                filtered_listItems=filter_sessions(listItems)
                sessions.extend([extract_info(listitem) for listitem in filtered_listItems])
                session_list.type_keys('{PGDN}')
                if listItems[-1].window_text()==last:
                    break
        session_list.type_keys('{HOME}')
        if close_weixin:
            main_window.close()
        sessions=remove_duplicates(sessions)
        return sessions

    @staticmethod
    def pull_messages(friend:str,number:int,chat_only:bool=True,search_pages:int=None,is_maximize:bool=None,close_weixin:bool=None)->list[str]:
        '''
        该函数用来从聊天界面获取聊天消息,也可当做获取聊天记录
        Args:
            friend:好友名称
            number:获取的消息数量
            search_pages:打开好友聊天窗口时在会话列表中查找好友时滚动列表的次数,默认为5,一次可查询5-12人,为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        Returns:
            messages:聊天记录中的消息(时间顺序从晚到早)
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if search_pages is None:
            search_pages=GlobalConfig.search_pages
        messages=[]
        audio_pattern=Regex_Patterns.Audio_pattern
        main_window=Navigator.open_dialog_window(friend=friend,is_maximize=is_maximize,search_pages=search_pages)
        chat_list=main_window.child_window(**Lists.FriendChatList)
        if not chat_list.exists(timeout=0.1):
            print(f'非正常好友或群聊,无法获取聊天信息！')
            return messages
        else:
            if not chat_list.children(control_type='ListItem'):
                warn(message=f'你与{friend}的聊天记录为空,无法获取聊天信息',category=NoChatHistoryWarning)
                return messages
            Tools.activate_chatList(chat_list)
            while len(messages)<number:
                selected=[listitem for listitem in chat_list.children(control_type='ListItem') if listitem.has_keyboard_focus()]
                if selected:
                    if selected[0].class_name()=='mmui::ChatItemView' and not chat_only:
                        messages.append(selected[0].window_text())
                    if selected[0].class_name()=='mmui::ChatVoiceItemView':
                        content=audio_pattern.search(selected[0].window_text()).group(1)
                        messages.append(f'语音转文字:{content}')
                    if selected[0].class_name()!='mmui::ChatItemView':
                        messages.append(selected[0].window_text())
                if not selected:
                    break
                chat_list.type_keys('{UP}') 
            chat_list.type_keys('{END}')
            messages=messages[-number:]
            if close_weixin:
                main_window.close()
        return messages


    @staticmethod
    def dump_chat_history(friend:str,number:int,search_content:str=None,capture_alia:bool=False,alias_folder:str=None,
        save_media:bool=False,media_folder:str=None,search_pages:int=None,is_maximize:bool=None,close_weixin:bool=None)->tuple[list,list]:
        '''
        该函数用来获取一定数量的聊天记录
        Args:  
            friend:好友名称
            number:获取的消息数量
            search_content:搜索关键字,传入后会先在顶部搜索关键字然后向下遍历
            capture_alia:是否截取聊天记录中聊天对象的昵称
            alias_folder:保存聊天对象昵称截图的文件夹
            save_media:是否保存聊天记录中的图片与视频
            media_folder:保存聊天对象昵称截图的文件夹
            search_pages:打开好友聊天窗口时在会话列表中查找好友时滚动列表的次数,默认为5,一次可查询5-12人,为0时,直接从顶部搜索栏搜索好友信息
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        Returns:
            (messages,timestamps):发送的消息(时间顺序从晚到早),每条消息对应的发送时间
        '''
        def save(listitem:ListItemWrapper,media_type:int):
            video_path=os.path.join(media_folder,f'{video_count}.mp4')
            image_path=os.path.join(media_folder,f'{image_count}.png')
            rec=listitem.rectangle()
            right_click_position=rec.left+120,rec.mid_point().y
            #保存视频
            if media_type==0:
                is_download=not download_label in listitem.window_text() 
                if not is_download:
                    mouse.click(coords=right_click_position)
                    while not is_download:
                        mouse.right_click(coords=right_click_position)
                        if copy_item.exists(timeout=0.2):
                            is_download=True 
                        time.sleep(0.2)     
                mouse.right_click(coords=right_click_position)     
                pyautogui.press('down',presses=video_pressed_num)
                pyautogui.press('enter')
                time.sleep(2)#2s时间延迟让视频保存到剪贴板
                SystemSettings.save_pasted_video(video_path)
            #保存图片
            if media_type==1:
                mouse.right_click(coords=right_click_position)
                pyautogui.press('down',image_pressed_num)
                pyautogui.press('enter')
                time.sleep(0.5)#0.5s延迟让图片缓存到剪贴板时间
                SystemSettings.save_pasted_image(image_path)
        
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if search_pages is None:
            search_pages=GlobalConfig.search_pages
        if capture_alia and alias_folder is None:
            alias_folder=os.path.join(os.getcwd(),f'dump_chat_history好友昵称截图',f'{friend}')
            print(f'未传入文件夹路径,好友昵称截图将分别保存到{alias_folder}内')
            os.makedirs(alias_folder,exist_ok=True)
        if save_media and media_folder is None:
            media_folder=os.path.join(os.getcwd(),f'dump_chat_history图片视频保存',f'{friend}')
            print(f'未传入文件夹路径,好友昵称截图将分别保存到{media_folder}内')
            os.makedirs(media_folder,exist_ok=True)
        messages=[]
        runtime_ids=[]
        image_count=0
        video_count=0
        image_label=Special_Labels.Image
        video_label=Special_Labels.Video
        download_label=Special_Labels.Download
        image_pressed_num=1 if '4.1.9' in GlobalConfig.version else 2
        video_pressed_num=2 if '4.1.9' in GlobalConfig.version else 3
        timestamp_pattern=Regex_Patterns.Chathistory_Timestamp_pattern
        chat_history_window=Navigator.open_chat_history(friend=friend,is_maximize=is_maximize,close_weixin=close_weixin,search_pages=search_pages)
        chat_history_list=chat_history_window.child_window(**Lists.ChatHistoryList)
        copy_item=chat_history_window.child_window(**MenuItems.CopyMenuItem)
        if isinstance(search_content,str):
            search_bar=chat_history_window.descendants(**Edits.SearchEdit)[0]
            search_bar.set_text(search_content)
        if not chat_history_list.exists(timeout=1):
            warn(message=f"你与{friend}的聊天记录为空,无法获取聊天记录",category=NoChatHistoryWarning)
            chat_history_window.close()
            return [],[]
        Tools.activate_chatHistoryList(chat_history_list)#激活滑块
        #因为要先按down向下遍历,第一个被selected的实际是第二条，所以第一项内容直接记录
        first_item=chat_history_list.children(control_type='ListItem')[0]
        messages.append(first_item.window_text())
        runtime_ids.append(first_item.element_info.runtime_id)
        if capture_alia:
            path=os.path.join(alias_folder,f'与{friend}聊天记录_1.png')
            alia_image=Tools.capture_alias(first_item)
            alia_image.save(path)
        if first_item.class_name()=='mmui::ChatBubbleReferItemView' and save_media:
            if video_label in first_item.window_text():save(listitem=first_item,media_type=0)
            if image_label in first_item.window_text():save(listitem=first_item,media_type=1)
        while len(messages)<number:
            pyautogui.press('down',presses=1,_pause=False)
            selected=[listitem for listitem in chat_history_list.children(control_type='ListItem') if listitem.has_keyboard_focus()]
            if selected:
                runtime_ids.append(selected[0].element_info.runtime_id)
                #同一个runtime_id挨着重复出现就说明到底部了无法继续下滑
                if runtime_ids[-1]==runtime_ids[-2]:
                    break
                if capture_alia:
                    time.sleep(0.1)#必须等待0.1s以上才能截出指定数量的图，不然过快来不及截图
                    path=os.path.join(alias_folder,f'与{friend}聊天记录_{len(messages)}.png')
                    alia_image=Tools.capture_alias(selected[0])
                    alia_image.save(path)
                if selected[0].class_name()=='mmui::ChatBubbleReferItemView' and save_media:
                    if video_label in selected[0].window_text():
                        video_count+=1
                        save(listitem=selected[0],media_type=0)
                    if image_label in selected[0].window_text():
                        image_count+=1
                        save(listitem=selected[0],media_type=1)
                messages.append(selected[0].window_text())
        chat_history_list.type_keys('{HOME}')
        chat_history_window.close()
        messages=messages[:number]
        timestamps=[timestamp_pattern.search(message).group(0) if timestamp_pattern.search(message) else '系统消息或为红包与转账(无法获取时间戳)' for message in messages]
        messages=[timestamp_pattern.sub('',message) for message in messages]
        return messages,timestamps

    @staticmethod
    def search_chat_history(keyword:str,is_maximize:bool=None,close_weixin:bool=None)->dict[str,list[str]]:
        '''
        该方法用来在微信顶部搜索关键字然后遍历查找聊天记录
        Args:
            keyword:聊天记录关键字
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        Returns:
            chat_history_detail:聊天记录明细
        '''
        def traverse_message_list(message_list:ListViewWrapper)->list[str]:
            messages=[]
            runtime_ids=[]
            total_num=int(re.search(r'\d+',total_label.window_text()).group(0))
            scrollable=Tools.is_scrollable(message_list,back='top')
            if not scrollable:
                messages=[listitem.window_text() for listitem in message_list.children(control_type='ListItem')]
            if scrollable:
                first_item=message_list.children(control_type='ListItem')[0]
                messages.append(first_item.window_text())
                runtime_ids.append(first_item.element_info.runtime_id)
                while len(messages)<total_num:
                    pyautogui.press('down',presses=2,_pause=False)
                    selected=[listitem for listitem in message_list.children(control_type='ListItem') if listitem.has_keyboard_focus()]
                    if selected:
                        runtime_ids.append(selected[0].element_info.runtime_id)
                        #同一个runtime_id挨着重复出现就说明到底部了无法继续下滑
                        if runtime_ids[-1]==runtime_ids[-2]:
                            break
                        messages.append(selected[0].window_text())
            return messages

        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        chat_history_detail={}
        chat_history_window,main_window=Navigator.open_chat_search_window(keyword=keyword,window_maximize=True)
        if chat_history_window is not None:
            search_list=chat_history_window.child_window(**Lists.SearchResult)
            message_list=chat_history_window.child_window(auto_id='message_list')
            rectangle=search_list.rectangle()
            scroll_position=(rectangle.mid_point().x,rectangle.mid_point().y)
            total_label=chat_history_window.child_window(control_type='Text',found_index=3)
            current_item=search_list.children(control_type='ListItem')[0]
            current_item.click_input()
            while True:
                Tools.activate_chatHistoryList(message_list)#激活滑块
                chat_history_detail[current_item.window_text()]=traverse_message_list(message_list)
                next_item=Tools.get_next_item(search_list,current_item)
                if next_item is None:
                    mouse.scroll(coords=scroll_position,wheel_dist=-12)
                    next_item=Tools.get_next_item(search_list,current_item)
                if next_item is None:
                    break
                rectangle=next_item.rectangle()
                click_position=rectangle.mid_point().x,rectangle.top+5
                mouse.click(coords=click_position)
                current_item=next_item
        chat_history_window.close()
        if close_weixin:
            main_window.close()
        return chat_history_detail
    
    @staticmethod
    def save_media(friend:str,number:int,target_folder:str=None,is_maximize:bool=None,close_weixin:bool=None,search_pages:int=None)->None:
        '''
        该方法用来保存与某个好友或群聊的图片和视频到指定文件夹中
        Args:
            friend:好友或群聊备注
            number:需要保存的图片数量
            target_folder:保存图片的文件夹路径,如果不传入则默认保存在当前运行代码所在的文件夹下
            search_pages:在会话列表中查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏法搜索好友信息打开聊天界面
            is_maximize:微信界面是否全屏,默认全屏。
            close_wechat:任务结束后是否关闭微信,默认关闭
        Examples:
            ```
            from pywechat import Messages
            target_folder=r'E:\\新建文件夹'
            save_media(friend='测试群',number=20,ftarget_folder=target_folder)
            ```
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if search_pages is None:
            search_pages=GlobalConfig.search_pages
        if target_folder and not os.path.isdir(target_folder):
            raise NotFolderError(f'所选路径不是文件夹!无法保存聊天记录,请重新选择!')
        if not target_folder:
            target_folder=os.path.join(os.getcwd(),'save_media聊天图片保存',friend)
            os.makedirs(name=target_folder,exist_ok=True)
            print(f'未传入文件夹路径,聊天图片或视频将保存至 {target_folder}')
        saved_num=0
        presses_num=1 if '4.1.9' in GlobalConfig.version else 2
        chat_history_window=Navigator.open_chat_history(friend=friend,TabItem='图片与视频',search_pages=search_pages,is_maximize=is_maximize,close_weixin=close_weixin)
        image_container=chat_history_window.child_window(control_type='Group',class_name="QFWidget")
        if not image_container.exists():#看一下是否存在聊天记录列表，如果不存在说明没有聊天记录    
            chat_history_window.close()
            raise ValueError(f'你还未与{friend}聊天,无法保存聊天图片!') 
        image_container.children()[1].click_input()
        #先右键最后一个图片激活菜单
        image_preview_window=Tools.move_window_to_center(Windows.ImagePreviewWindow)
        image_expired=image_preview_window.child_window(**Texts.ImageExpiredText)
        video_expired=image_preview_window.child_window(**Texts.VideoExpiredText)
        earliest_image=image_preview_window.child_window(**Texts.EarliestOneText)
        rotate_button=image_preview_window.child_window(**Buttons.RotateButton)
        image_area=image_preview_window.child_window(class_name='mmui::XViewPager',control_type='Custom')
        chat_history_window.close()
        while saved_num<number:
            is_image_expired=image_expired.exists(timeout=0.1)
            is_video_expired=video_expired.exists(timeout=0.1)
            is_image=rotate_button.exists(timeout=0.1)
            if is_image_expired or is_video_expired:  
                #如果图片过期或者视频直接跳过
                pyautogui.press('left',_pause=False)
            if is_image and not is_image_expired:
                #有旋转按钮是图片
                saved_num+=1
                pic_path=os.path.join(target_folder,f'与{friend}的聊天图片{saved_num}.png')
                image=image_area.capture_as_image()
                image.save(pic_path)
                pyautogui.press('left',_pause=False)
            if not is_image and not is_video_expired:
                #没有旋转按钮是视频
                is_download=False
                saved_num+=1
                image_area.right_click_input()
                video_path=os.path.join(target_folder,f'与{friend}的聊天视频{saved_num}.mp4')
                image_preview_window.click_input()
                while not is_download:
                    image_preview_window.right_click_input()
                    copy_item=image_preview_window.child_window(**MenuItems.CopyMenuItem)
                    if copy_item.exists(timeout=0.3):
                        is_download=True 
                    time.sleep(0.3)       
                pyautogui.press('down',presses=presses_num)
                pyautogui.press('enter')
                time.sleep(2)
                SystemSettings.save_pasted_video(video_path=video_path)
                pyautogui.press('left',_pause=False)
            if earliest_image.exists(timeout=0.1):
                #按下左键后可能会出现这是第一张图片的提示,那么直接退出循环
                break
        image_preview_window.close()
        if saved_num==0:
            print(f"你与{friend}无聊天图片与视频,未能保存!")
        if saved_num<number and saved_num!=0:
            print(f"你与{friend}的聊天图片与视频不足{number},已为你保存全部的{saved_num}张图片与视频")
  
    @staticmethod
    def accept_group_invitation(friend:str,number:int,max_num:int=100,is_maximize:bool=None,close_weixin:bool=None,search_pages:int=None)->None:
        '''
        该方法用来从聊天记录链接中查找入群邀请并加入
        Args:
            number:群聊邀请链接的数量
            max_num:在链接中查找入群邀请时的历史记录的最大遍历条数
            search_pages:在会话列表中查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏法搜索好友信息打开聊天界面
            is_maximize:微信界面是否全屏,默认全屏。
            close_wechat:任务结束后是否关闭微信,默认关闭
        Returns:
            joined_num:实际加入的数量
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if search_pages is None:
            search_pages=GlobalConfig.search_pages

        def click_cardLink(listitem):
            sign='无法加入'
            listitem.double_click_input()
            try:
                group_invitation_pane=desktop.window(**Panes.GroupInvitationPane)
                group_invitation_pane.restore()
                time.sleep(3)
                join_group_button=group_invitation_pane.child_window(**Buttons.JoinGroupButton)
                invitation_sent_text=group_invitation_pane.child_window(**Texts.InvitationSentText)
                invitation_expired_text=group_invitation_pane.child_window(**Texts.InvitationExpiredText)
                if invitation_sent_text.exists(timeout=0.1):
                    sign='邀请由自己发送,已加入该群'
                    group_invitation_pane.close()
                if invitation_expired_text.exists(timeout=0.1):
                    sign='邀请已过期'
                    group_invitation_pane.close()
                if join_group_button.exists(timeout=0.1):
                    join_group_button.click_input()
                    sign='成功入群'
            except Exception:
                sign='网络异常,未能正确打开群聊邀请界面'
                group_invitation_pane.close()
            return sign
        
        checked_num=0
        joined_num=0
        results=[]
        invitation_text='邀请你加入群聊'
        Timestamp_pattern=re.compile(r'(?<=\s)(\d{2}/\d{1,2}/\d{1,2}|\d{1,2}/\d{1,2}|星期\w|昨天|\d{2}:\d{2})$')
        chat_history_window=Navigator.open_chat_history(friend=friend,TabItem='链接',search_pages=search_pages,is_maximize=is_maximize,close_weixin=close_weixin)
        Tools.cancel_pin(chat_history_window)#取消聊天记录框置顶,不然入群邀请窗口只能在聊天记录窗口底部
        chat_history_list=chat_history_window.child_window(**Lists.ChatHistoryList)
        if not chat_history_list.exists(timeout=1):
            warn(message=f"你与{friend}的聊天记录为空,无法获取入群链接",category=NoChatHistoryWarning)
            chat_history_window.close()
            return [],[]
        search_edit=chat_history_window.child_window(control_type='Edit')
        search_edit.set_text(invitation_text)
        win32gui.SendMessage(chat_history_window.handle,win32con.WM_SYSCOMMAND,win32con.SC_MAXIMIZE,0)
        scrollable=Tools.is_scrollable(chat_history_list)
        if not scrollable:
            for listitem in chat_history_list.children(control_type='ListItem'):
                title=Timestamp_pattern.sub('',listitem.window_text()).strip()
                if title==invitation_text:
                    sign=click_cardLink(listitem)
                    results.append(sign)
        else:
            current_item=chat_history_list.children(control_type='ListItem')[0]
            while checked_num<max_num:
                next_item=Tools.get_next_item(chat_history_list,current_item)
                if next_item is None:
                    pyautogui.press('pagedown',interval=0.5)
                    chat_history_list=chat_history_window.child_window(**Lists.ChatHistoryList)
                    next_item=Tools.get_next_item(chat_history_list,current_item)
                if next_item is None:#到达底部
                    break
                sign=click_cardLink(current_item)
                results.append(sign)
                if sign=='成功入群':
                    joined_num+=1
                if joined_num>=number:
                    break
                current_item=next_item
                checked_num+=1
        chat_history_list.type_keys('{HOME}')
        chat_history_window.close()
        return results

class Monitor():
    '''监听消息的一些方法'''          

    @staticmethod
    def listen_on_chat(dialog_window:WindowSpecification,duration:str,save_file:bool=False,save_media:bool=False,target_folder:str=None,close_dialog_window:bool=True)->dict:
        '''
        该方法用来在指定时间内监听会话窗口内的新消息(可以配合多线程使用,一次监听多个会话内的消息)
        Args:
            dialog_window:好友单独的聊天窗口或主界面内的聊天窗口,可使用Navigator内的方法打开
            duraiton:监听持续时长,监听消息持续时长,格式:'s','min','h'单位:s/秒,min/分,h/小时
            save_file:是否保存文件,需开启自动下载文件并设置为1024MB,默认为False
            save_photo:是否保存图片,注意不要在多线程中设置为True,针对单个好友可以设置为True,默认为False
            target_folder:文件或图片的保存文件夹
            close_dialog_window:是否关闭dialog_window,默认关闭

        涉及到键鼠操作的选项须为False,无论是主界面还是单独聊天窗口都可以最小化到状态栏,但千万不要关闭！
        Examples:
            多线程使用示例:
            >>> from concurrent.futures import ThreadPoolExecutor
            >>> from pyweixin import Navigator,Monitor
            >>> #先打开所有好友的独立窗口
            >>> dialog_windows=[]
            >>> friends=['Hello,Mr Crab','Pywechat测试群']
            >>> durations=['1min']*len(friends)
            >>> for friend in friends:
            >>>    dialog_window=Navigator.open_seperate_dialog_window(friend=friend,window_minimize=True,close_weixin=True)
            >>>    dialog_windows.append(dialog_window)
            >>> with ThreadPoolExecutor() as pool:
            >>>    results=pool.map(lambda args: Monitor.listen_on_chat(*args),list(zip(dialog_windows,durations)))
            >>> for friend,result in zip(friends,results):
            >>>    print(friend,result)
        Returns:
            details:该聊天窗口内的新消息(文本内容),格式为{'新消息总数':x,'文本数量':x,'文件数量':x,'图片数量':x,'视频数量':x,'链接数量':x,'文本内容':x}
        '''
        duration=Tools.match_duration(duration)#将's','min','h'转换为秒
        if duration is None:#不按照指定的时间格式输入,需要提前中断退出
            raise TimeNotCorrectError
        if (save_file or save_media ) and target_folder is None:
            target_folder=os.path.join(os.getcwd(),f'{dialog_window.window_text()}_listen_on_chat聊天文件保存')
            print(f'未传入文件夹路径,文件,图片将分别保存到{target_folder}内的Files,Images文件夹下\n')
            os.makedirs(target_folder,exist_ok=True)
        if save_file:
            file_folder=os.path.join(target_folder,'Files')
            os.makedirs(file_folder,exist_ok=True)
        if save_media:
            media_folder=os.path.join(target_folder,'Images')
            os.makedirs(media_folder,exist_ok=True)
        total=0
        link_count=0
        video_count=0
        image_count=0
        files=[]
        texts=[]
        memberEvents=[]
        link_label=Special_Labels.Link
        image_labal=Special_Labels.Image
        video_label=Special_Labels.Video
        file_label=Special_Labels.File
        file_pattern=Regex_Patterns.File_pattern
        friend=dialog_window.window_text()
        chatName=dialog_window.child_window(**Texts.CurrentChatNameText)
        if chatName.exists(timeout=0.2):
            friend=chatName.window_text()
        timestamp=time.strftime('%Y-%m')
        chatfile_folder=Tools.where_chatfile_folder()
        chatList=dialog_window.child_window(**Lists.FriendChatList)#聊天界面内存储所有信息的容器
        timestamp_pattern=Regex_Patterns.Message_Timestamp_pattern#系统消息的时间戳
        Tools.activate_chatList(chatList)
        if chatList.children(control_type='ListItem'):
            initial_message=chatList.children(control_type='ListItem')[-1]#刚打开聊天界面时的最后一条消息的listitem
            initial_runtime_id=initial_message.element_info.runtime_id
        if not chatList.children(control_type='ListItem'):
            initial_runtime_id=0
        end_timestamp=time.time()+duration#根据秒数计算截止时间
        SystemSettings.open_listening_mode(volume=False)
        while time.time()<end_timestamp:
            if chatList.children(control_type='ListItem'):
                newMessage=chatList.children(control_type='ListItem')[-1]
                runtime_id=newMessage.element_info.runtime_id
                if runtime_id!=initial_runtime_id: 
                    total+=1
                    if newMessage.class_name()=='mmui::ChatTextItemView':
                        texts.append(newMessage.window_text())
                    if newMessage.class_name()=='mmui::ChatItemView' and not timestamp_pattern.search(newMessage.window_text()):
                        memberEvents.append(newMessage.window_text())
                    if newMessage.class_name()=='mmui::ChatBubbleItemView' and newMessage.window_text()[:2]==link_label:#
                        link_count+=1
                    if newMessage.class_name()=='mmui::ChatBubbleReferItemView' and newMessage.window_text()==image_labal:
                        image_count+=1
                    if newMessage.class_name()=='mmui::ChatBubbleReferItemView' and video_label in newMessage.window_text():
                        video_count+=1#视频需要下载直接右键复制不行,需要先点击,如果时间长,要等半天，不太方便
                    if newMessage.class_name()=='mmui::ChatBubbleItemView' and file_label in newMessage.window_text():
                        filename=file_pattern.search(newMessage.window_text()).group(1)
                        filepath=os.path.join(chatfile_folder,timestamp,filename)
                        files.append(filepath)
                    initial_runtime_id=runtime_id
        media_count=image_count+video_count
        SystemSettings.close_listening_mode()
        if close_dialog_window:dialog_window.close()
        #最后结束时再批量复制到target_folder,不在循环里逐个复制是考虑到若文件过大(几百mb)没有自动下载完成移动不了
        if save_file and files:SystemSettings.copy_files(files,file_folder)#文件复制粘贴到target_folder/Files内
        if save_media and media_count:Messages.save_media(friend=friend,number=media_count,target_folder=target_folder)#保存图片到target_folder/Images内
        details={'新消息总数':total,'文本数量':len(texts),'文件数量':len(files),'图片数量':image_count,'视频数量':video_count,'链接数量':link_count,'文本内容':texts,'出入群通知':memberEvents}
        return details

    @staticmethod
    def listen_on_newMemberJoin(dialog_window:WindowSpecification,duration:str,close_dialog_window:bool=True)->list[str]:
        '''
        该方法用来在指定时间内监听群聊内的出入群消息
        Args:
            dialog_window:群聊单独的聊天窗口或主界面内的聊天窗口,可使用Navigator内的方法打开
            duraiton:监听持续时长,监听消息持续时长,格式:'s','min','h'单位:s/秒,min/分,h/小时
            close_dialog_window:是否关闭dialog_window,默认关
        Examples:
            多线程使用示例:
            >>> from concurrent.futures import ThreadPoolExecutor
            >>> from pyweixin import Navigator,Monitor
            >>> #先打开所有好友的独立窗口
            >>> dialog_windows=[]
            >>> friends=['家族群','Pywechat测试群']
            >>> durations=['1min']*len(friends)
            >>> for friend in friends:
            >>>    dialog_window=Navigator.open_seperate_dialog_window(friend=friend,window_minimize=True,close_weixin=True)
            >>>    dialog_windows.append(dialog_window)
            >>> with ThreadPoolExecutor() as pool:
            >>>    results=pool.map(lambda args: Monitor.listen_on_newMemberJoin(*args),list(zip(dialog_windows,durations)))
            >>> for friend,result in zip(friends,results):
            >>>    print(friend,result)
        Returns:
            details:出入群消息列表
        '''
        details=[]
        duration=Tools.match_duration(duration)#将's','min','h'转换为秒
        if duration is None:#不按照指定的时间格式输入,需要提前中断退出
            raise TimeNotCorrectError
        is_group=Tools.is_group_chat(dialog_window)
        chatList=dialog_window.child_window(**Lists.FriendChatList)#聊天界面内存储所有信息的容器
        Tools.activate_chatList(chatList)
        if chatList.children(control_type='ListItem'):
            initial_message=chatList.children(control_type='ListItem')[-1]#刚打开聊天界面时的最后一条消息的listitem
            initial_runtime_id=initial_message.element_info.runtime_id
        if not chatList.children(control_type='ListItem'):
            initial_runtime_id=0
        timestamp_pattern=Regex_Patterns.Message_Timestamp_pattern#系统消息的时间戳
        end_timestamp=time.time()+duration#根据秒数计算截止时间
        SystemSettings.open_listening_mode(volume=False)
        while time.time()<end_timestamp:
            if chatList.children(control_type='ListItem') and is_group:
                newMessage=chatList.children(control_type='ListItem')[-1]
                runtime_id=newMessage.element_info.runtime_id
                if runtime_id!=initial_runtime_id: 
                    if newMessage.class_name()=='mmui::ChatItemView' and not timestamp_pattern.search(newMessage.window_text()):
                        details.append(newMessage.window_text())
                    initial_runtime_id=runtime_id
        SystemSettings.close_listening_mode()
        if close_dialog_window:dialog_window.close()
        return details
