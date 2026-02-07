'''
WeChatAuto
===========


微信4.0版本自动化主模块,实现了绝大多数的自动化功能,包括发送消息,文件,音视频通话等
所有的方法都位于这些静态类内,导入后使用XX.yy的方式使用即可

    - `AutoReply`:微信自动回复的一些方法
    - `Call`: 给某个好友打视频或语音电话
    - `Collections`: 与收藏相关的一些方法
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
from pywinauto.controls.uia_controls import ListItemWrapper,ListViewWrapper #TypeHint要用到
from typing import Callable
#####################################################################################
#内部依赖
from .Config import GlobalConfig
from .utils import scan_for_new_messages,get_new_message_num
from .utils import At,At_all,Regex_Patterns
from .Warnings import LongTextWarning,NoChatHistoryWarning
from .WeChatTools import Tools,Navigator,mouse,Desktop
from .WinSettings import SystemSettings
from .Errors import TimeNotCorrectError
from .Errors import NoFilesToSendError
from .Errors import CantSendEmptyMessageError
from .Errors import NotFolderError
from .Errors import NotFriendError
from .Uielements import (Main_window,SideBar,Independent_window,Buttons,
Edits,Texts,TabItems,Lists,Panes,Windows,CheckBoxes,MenuItems,Menus,Groups,Customs,ListItems)
#######################################################################################
desktop=Desktop(backend='uia')#pywinauto的windows桌面对象(WindowSpecification)实例化
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
Regex_Patterns=Regex_Patterns()#所有的正则pattern


class AutoReply():
    
    @staticmethod
    def auto_reply_to_friend(dialog_window:WindowSpecification,duration:str,callback:Callable[[str],str],save_file:bool=False,target_folder:str=None,close_dialog_window:bool=True)->dict:
        '''
        该方法用来在指定时间内自动回复会话窗口内的新消息并监听内容
        Args:
            dialog_window:好友单独的聊天窗口或主界面内的聊天窗口,可使用Navigator内的open_seperate_dialoig_window打开
            duraiton:监听持续时长,监听消息持续时长,格式:'s','min','h'单位:s/秒,min/分,h/小时
            callback:新消息处理函数
            save_file:是否保存文件,需开启自动下载文件并设置为1024MB,默认为False
            target_folder:文件或图片的保存文件夹
            close_dialog_window:是否关闭dialog_window,默认关闭
        Examples:
            >>> from pyweixin import AutoReply,Navigator
            >>> def reply_func2(message):
            >>>     return '自动回复[微信机器人]:您好,我当前不在,请您稍后再试'
            >>> main_window=Navigator.open_dialog_window(friend='abcdefghijklmnopqrstuvwxyz123456')
            >>> AutoReply.auto_reply_to_friend(dialog_window=main_window,duration='20s',callback=reply_func2)
            #多线程使用方法:
            >>> from pyweixin import Navigator
            >>> from concurrent.futures import ThreadPoolExecutor
            >>> from pyweixin import Navigator,AutoReply
            >>> def reply_func1(message):
            >>>     if '你好' in message:
            >>>        return '你好,有什么可以帮您的吗[呲牙]?'
            >>>     if '在吗' in message:
            >>>        return '在的[旺柴]'
            >>>     return '自动回复[微信机器人]:您好,我当前不在,请您稍后再试'
            >>> def reply_func2(message):
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
        if not duration:#不按照指定的时间格式输入,需要提前中断退出
            raise TimeNotCorrectError
        if save_file and target_folder is None:
            target_folder=os.path.join(os.getcwd(),f'{dialog_window.window_text()}_listen_on_chat聊天文件保存')
            print(f'未传入文件夹路径,文件,图片,群昵称截图将分别保存到{target_folder}内的Files,Images,Alias文件夹下\n')
            os.makedirs(target_folder,exist_ok=True)
        if save_file:
            file_folder=os.path.join(target_folder,'Files')
            os.makedirs(file_folder,exist_ok=True)
        total=0
        link_count=0
        video_count=0
        image_count=0
        files=[]
        texts=[]
        file_pattern=Regex_Patterns.File_Pattern
        timestamp=time.strftime('%Y-%m')
        chatfile_folder=Tools.where_chatfile_folder()
        chatList=dialog_window.child_window(**Lists.FriendChatList)#聊天界面内存储所有信息的容器
        input_edit=dialog_window.child_window(**Edits.InputEdit)
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
                        dialog_window.restore()
                        is_my_bubble=Tools.is_my_bubble(dialog_window,newMessage,input_edit)
                        if not is_my_bubble:
                            reply_content=callback(newMessage.window_text())
                            input_edit.set_text(reply_content)
                            pyautogui.hotkey('alt','s')
                            win32gui.SendMessage(dialog_window.handle, win32con.WM_SYSCOMMAND, win32con.SC_MINIMIZE,0)
                    if newMessage.class_name()=='mmui::ChatBubbleItemView' and newMessage.window_text()[:2]=='[链接]':#
                        link_count+=1
                    if newMessage.class_name()=='mmui::ChatBubbleReferItemView' and newMessage.window_text()=='图片':
                        image_count+=1
                        #只是依靠class_name,window_text还有数量筛选，假如结束时又新发了几张图片，内容会对不上         
                    if newMessage.class_name()=='mmui::ChatBubbleReferItemView' and '视频' in newMessage.window_text():
                        video_count+=1#视频需要下载直接右键复制不行,需要先点击,如果时间长,要等半天，不太方便
                    if newMessage.class_name()=='mmui::ChatBubbleItemView' and '文件' in newMessage.window_text():
                        filename=file_pattern.search(newMessage.window_text()).group(1)
                        filepath=os.path.join(chatfile_folder,timestamp,filename)
                        files.append(filepath)
                    initial_runtime_id=runtime_id
        SystemSettings.close_listening_mode()
        #最后结束时再批量复制到target_folder,不在循环里逐个复制是考虑到若文件过大(几百mb)没有自动下载完成移动不了
        if save_file and files:SystemSettings.copy_files(files,file_folder)#文件复制粘贴到target_folder/Files内
        if close_dialog_window:dialog_window.close()
        details={'新消息总数':total,'文本数量':len(texts),'文件数量':len(files),'图片数量':image_count,'视频数量':video_count,'链接数量':link_count,'文本内容':texts}
        return details
    

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

class Collections():
    
    @staticmethod
    def cardLink_to_url(number:int,is_maximize:bool=None,close_weixin:bool=None)->dict[str,str]:
        '''该函数用来获取收藏界面内指定数量卡片链接的url
        Args:
            number:卡片链接的数量
            is_maximize:微信界面是否全屏,默认全屏
            close_weixin:任务结束后是否关闭微信,默认关闭
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin

        def copy_url(listitem):
            y=listitem.rectangle().mid_point().y# 竖直方向上居中,水平方向上靠右
            x=listitem.rectangle().right-offset
            mouse.right_click(coords=(x,y))
            copylink_item.click_input()
            win32clipboard.OpenClipboard()
            url=win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            time.sleep(0.5)#0.5是极限,等待复制到剪贴板标签消失
            return url
        
        offset=120#固定的offset,右键都在右边点
        links=dict()
        main_window=Navigator.open_collections(is_maximize=is_maximize)
        copylink_item=main_window.child_window(**MenuItems.CopyLinkMenuItem)
        link_item=main_window.child_window(**ListItems.LinkListItem)
        if not link_item.exists(timeout=0.1):return {}
        link_item.double_click_input()
        link_list=main_window.child_window(title='链接',control_type='List')
        link_list.type_keys('{END}')
        last_item=link_list.children(control_type='ListItem')[-2].window_text()
        link_list.type_keys('{HOME}')
        link_list.type_keys('{DOWN}')
        selected_item=[listitem for listitem in link_list.children(control_type='ListItem') if listitem.has_keyboard_focus() and listitem.window_text()!=''][0]
        while selected_item.window_text()!=last_item:
            url=copy_url(selected_item)
            text=selected_item.window_text()[2:]#前两个字是固定的,为链接二字,后边的文本才是需要的
            links[url]=text
            if len(links)>=number:
                break
            rectangle=selected_item.rectangle()
            side_x=rectangle.right-15
            center_y=rectangle.mid_point().y
            mouse.click(coords=(side_x,center_y))
            link_list.type_keys('{DOWN}',pause=0.15)
            selected_item=[listitem for listitem in link_list.children(control_type='ListItem') if listitem.has_keyboard_focus() and listitem.window_text()!=''][0]
        if close_weixin:
            main_window.close()
        return links

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
            phonenumber='无'#电话号
            permission='无'#朋友权限
            texts=contact_profile.descendants(control_type='Text')
            texts=[item.window_text() for item in texts]
            nickname=texts[0]
            if '微信号：' in texts:
                wx_number=texts[texts.index('微信号：')+1]#微信号
            if '昵称：' in texts:
                nickname=texts[texts.index('昵称：')+1]
            if '地区：' in texts:
                region=texts[texts.index('地区：')+1]
            if '备注' in texts:
                remark=texts[texts.index('备注')+1]
                if remark in labels:
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
        labels={'微信号：','昵称：','地区：','备注','共同群聊','个性签名','来源','电话','描述','标签','朋友权限','朋友圈'}#联系人分区的标签
        friends_detail=[]
        #通讯录列表
        contact_list,main_window=Navigator.open_contacts(is_maximize=is_maximize)
        #右侧的自定义面板
        contact_custom=main_window.child_window(**Customs.ContactCustom)
        #右侧自定义面板下的好友信息所在面板
        contact_profile=contact_custom.child_window(**Groups.ContactProfileGroup)
        area=(contact_custom.rectangle().mid_point().x,contact_custom.rectangle().mid_point().y)
        #联系人分区
        Tools.collapse_contacts(main_window,contact_list)
        contact_item=main_window.child_window(control_type='ListItem',title_re=r'联系人\d+',class_name="mmui::ContactsCellGroupView")
        if contact_item.exists(timeout=0.1):
            total_num=int(re.search(r'\d+',contact_item.window_text()).group(0))
            if total_num>2000:
                interval=0.3
            if 1000<total_num<2000:
                interval=0.1
            if total_num<1000:
                interval=0
            contact_item.click_input()
            #有具体的数量,后续可以更换为for循环
            switch_to_first_friend()
            info=get_specific_info()
            friends_detail.append(info)
            mouse.move(coords=area)
            for _ in range(total_num-1):
                time.sleep(interval)
                pyautogui.keyDown('down',_pause=False)#不能press,press比keydown更频繁容易被检测
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
        area=(contact_custom.rectangle().mid_point().x,contact_custom.rectangle().mid_point().y)
        #企业微信联系人分区
        Tools.collapse_contacts(main_window,contact_list)
        wecom_item=main_window.child_window(control_type='ListItem',title_re=r'企业微信联系人\d+',class_name="mmui::ContactsCellGroupView")
        if not wecom_item.exists(timeout=0.1):
            print(f'你没有企业微信联系人,无法获取企业微信好友信息！')
        if wecom_item.exists(timeout=0.1):
            total_num=int(re.search(r'\d+',wecom_item.window_text()).group(0))
            if total_num>2000:
                interval=0.3
            if 1000<total_num<2000:
                interval=0.1
            if total_num<1000:
                interval=0
            wecom_item.click_input()
            switch_to_first_friend()
            info=get_specific_info()
            friends_detail.append(info)
            mouse.move(coords=area)
            for _ in range(total_num+1):
                time.sleep(interval)
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
        area=(contact_custom.rectangle().mid_point().x,contact_custom.rectangle().mid_point().y)
        #右侧自定义面板下的好友信息所在面板
        contact_profile=contact_custom.child_window(**Groups.ContactProfileGroup)
        #企业微信联系人分区
        Tools.collapse_contacts(main_window,contact_list)
        service_item=main_window.child_window(control_type='ListItem',title_re=r'服务号\d+',class_name="mmui::ContactsCellGroupView")
        if not service_item.exists(timeout=0.1):
            print(f'你没有关注过任何服务号,无法获取服务号信息！')
        if service_item.exists(timeout=0.1):
            total_num=int(re.search(r'\d+',service_item.window_text()).group(0))
            if total_num>2000:
                interval=0.3
            if 1000<total_num<2000:
                interval=0.1
            if total_num<1000:
                interval=0
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
        if close_weixin:
            main_window.close()
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
        area=(contact_custom.rectangle().mid_point().x,contact_custom.rectangle().mid_point().y)
        #右侧自定义面板下的好友信息所在面板
        contact_profile=contact_custom.child_window(**Groups.ContactProfileGroup)
        #企业微信联系人分区
        Tools.collapse_contacts(main_window,contact_list)
        official_item=main_window.child_window(control_type='ListItem',title_re=r'公众号\d+',class_name="mmui::ContactsCellGroupView")
        if not official_item.exists(timeout=0.1):
            print(f'你没有关注过任何公众号,无法获取公众号信息！')
        if official_item.exists(timeout=0.1):
            total_num=int(re.search(r'\d+',official_item.window_text()).group(0))
            if total_num>2000:
                interval=0.3
            if 1000<total_num<2000:
                interval=0.1
            if total_num<1000:
                interval=0
            official_item.click_input()
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
        if close_weixin:
            main_window.close()
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
        group_label=search_results.child_window(control_type='ListItem',title='群聊',class_name="mmui::XTableCell")
        check_all_buttons=[button for button in search_results.children() if r'查看全部' in button.window_text()]
        if check_all_buttons:
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
        if close_weixin:
            main_window.close()
        return groups
    
    @staticmethod
    def get_friend_profile(friend:str,search_pages:int=None,is_maximize:bool=None,close_weixin:bool=None):
        '''
        该函数用来获取单个好友的个人简介信息
        Args:
            friend:好友备注
            search_pages:在会话列表中查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面
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
        wx_number='无'#好友的微信号
        region='无'#好友的地区
        tag='无'#好友标签
        common_group_num='无'
        remark='无'#备注
        signature='无'#个性签名
        source='无'#好友来源
        descrption='无'#描述
        phonenumber='无'#电话号
        permission='无'#朋友权限
        #没用的文本信息
        no_need_labels=['企业','昵称：','备注','实名','职务','员工状态','朋友圈','工作时间',
        '在线时间','地址','发消息','语音聊天','视频聊天','企业信息','来自','企业微信']
        profile_pane,main_window=Navigator.open_friend_profile(friend=friend,search_pages=search_pages,is_maximize=is_maximize)
        text_uis=profile_pane.descendants(control_type='Text')
        texts=[item.window_text() for item in text_uis]
        nickname=texts[0]
        if '微信号：' in texts:
            wx_number=texts[texts.index('微信号：')+1]#微信号
        if '昵称：' in texts:
            nickname=texts[texts.index('昵称：')+1]
        if '地区：' in texts:
            region=texts[texts.index('地区：')+1]
        if '备注' in texts:
            remark=texts[texts.index('备注')+1]
            if remark in no_need_labels:
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
        edit=add_friend_pane.child_window(control_type='Edit')
        edit.set_text('')
        edit.set_text(number)
        edit.type_keys('{ENTER}')
        time.sleep(1)
        contact_profile_view=add_friend_pane.child_window(**Groups.ContactProfileViewGroup)
        if contact_profile_view.exists(timeout=0.1):
            add_to_contact=contact_profile_view.child_window(**Buttons.AddToContactsButton)
            if add_to_contact.exists(timeout=0.1):
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
    def mute_notification(friend:str,mute:int=0,fold_chat:int=0,is_maximize:bool=None,close_weixin:bool=None):
        '''该方法用来将好友消息设置为免打扰和折叠聊天,只有在免打扰开启的时候才可以设置折叠聊天
        Args:
            friend:好友备注
            mute:关闭或设置为消息免打扰,0:关闭消息免打扰,1:开启消息免打扰
            fold_chat:是否折叠聊天,0:取消折叠聊天,1:开启折叠聊天
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭 
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if mute not in {0,1}:
            raise ValueError('mute的取整为0或1!')
        if fold_chat not in {0,1}:
            raise ValueError('fold_chat的取整为0或1!')
        chatinfo_pane,main_window=Navigator.open_chatinfo(friend=friend,is_maximize=is_maximize)
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
    def pin_chat(friend:str,state:int=0,is_maximize:bool=None,close_weixin:bool=None):
        '''该方法用来将好友聊天置顶
        Args:
            friend:好友备注
            state:置顶或不置顶,0:不置顶,1:置顶
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭 
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if state not in {0,1}:
            raise ValueError('state的取整为0或1!')
        chatinfo_pane,main_window=Navigator.open_chatinfo(friend=friend,is_maximize=is_maximize)
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
    def clear_chat_histpry(friend:str,is_maximize:bool=None,close_weixin:bool=None):
        '''该方法用来清空与好友的聊天记录
        Args:
            friend:好友备注
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭 
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        chatinfo_pane,main_window=Navigator.open_chatinfo(friend=friend,is_maximize=is_maximize)
        chatinfo_button=main_window.child_window(**Buttons.ChatInfoButton)
        clear_chat_history_button=chatinfo_pane.child_window(**Buttons.ClearChatHistoryButton)
        empty_button=main_window.child_window(**Buttons.EmptyButton)
        clear_chat_history_button.click_input()
        empty_button.click_input()
        chatinfo_button.click_input()
        if close_weixin:
            main_window.close()

    @staticmethod
    def change_privacy(friend:str,chat_privacy:int=1,sns_privacy:int=0,is_maximize:bool=None,close_weixin:bool=None):
        '''该方法用来设置好友权限
        Args:
            friend:好友备注
            chat_privacy:0:仅聊天,1:聊天,朋友圈,微信运动等
            sns_privacy:0:取消所有朋友圈权限,1:不让他看,2:不看他
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭 
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
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
        open_privacy_group=profile_pane.child_window(**Groups.OpenPrivacyGroup)
        chat_only_group=profile_pane.child_window(**Groups.ChatOnlyGroup)
        check_box1=profile_pane.child_window(**CheckBoxes.DontShowOthersCheckBox)
        check_box2=profile_pane.child_window(**CheckBoxes.DontSeeOthersCheckBox)
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
        complete_button=profile_pane.child_window(**Buttons.CompleteButton)
        complete_button.click_input()
        chatinfo_button.click_input()
        if close_weixin:
            main_window.close()

    @staticmethod
    def star_friend(friend:str,state:int=1,is_maximize:bool=None,close_weixin:bool=None):
        '''该方法用来将好友设为星标朋友或取消星标朋友
        Args:
            friend:好友备注
            state:设置为星标朋友还是取消设置为星标朋友
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭 
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if state not in {0,1}:
            raise ValueError('state的取整为0或1!')
        profile_pane,main_window=Navigator.open_friend_profile(friend=friend,is_maximize=is_maximize)
        chatinfo_button=main_window.child_window(**Buttons.ChatInfoButton)
        more_button=profile_pane.child_window(**Buttons.MoreButton)
        more_button.click_input()
        pyautogui.press('down',presses=4)
        menu=profile_pane.child_window(class_name='mmui::XMenu',title='Weixin')
        selected_item=[item for item in menu.children(control_type='MenuItem') if item.has_keyboard_focus()]
        if selected_item[0].window_text()=='设为星标朋友' and state==1:
            pyautogui.press('enter')
        if selected_item[0].window_text()=='不再设为星标朋友' and state==0:
            pyautogui.press('enter')
        chatinfo_button.click_input()
        if close_weixin:
            main_window.close()

    @staticmethod
    def delete_friend(friend:str,clear_chat_history:int=1,is_maximize:bool=None,close_weixin:bool=None):
        '''该方法用来删除好友
        Args:
            friend:好友备注
            is_maximize:微信界面是否全屏，默认不全屏
            clear_chat_history:删除好友时是否勾选清空聊天记录,1清空,0不清空
            close_weixin:任务结束后是否关闭微信，默认关闭 
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if clear_chat_history not in {0,1}:
            raise ValueError('clear_chat_history的取整为0或1!')
        profile_pane,main_window=Navigator.open_friend_profile(friend=friend,is_maximize=is_maximize)
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
    def add_to_blacklist(friend:str,state:int=0,is_maximize:bool=None,close_weixin:bool=None):
        '''该方法用来将好友添加至黑名单或从黑名单移出
        Args:
            friend:好友备注
            state:将好友移出黑名单还是加入黑名单,0移出黑名单,1加入黑名单
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭 
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if state not in {0,1}:
            raise ValueError('state的取整为0或1!')
        profile_pane,main_window=Navigator.open_friend_profile(friend=friend,is_maximize=is_maximize)
        chatinfo_button=main_window.child_window(**Buttons.ChatInfoButton)
        more_button=profile_pane.child_window(**Buttons.MoreButton)
        more_button.click_input()
        pyautogui.press('down',presses=5)
        menu=profile_pane.child_window(class_name='mmui::XMenu',title='Weixin')
        selected_item=[item for item in menu.children(control_type='MenuItem') if item.has_keyboard_focus()]
        if selected_item[0].window_text()=='加入黑名单' and state==1:
            pyautogui.press('enter')
            confirm_button=profile_pane.child_window(**Buttons.ConfirmButton)
            confirm_button.click_input()
        if selected_item[0].window_text()=='移出黑名单' and state==0:
            pyautogui.press('enter')
        chatinfo_button.click_input()
        if close_weixin:
            main_window.close()
    
    @staticmethod
    def change_remark(friend:str,remark:str,description:str=None,phoneNum:str=None,clear_phoneNum:bool=False,is_maximize:bool=None,close_weixin:bool=None):
        '''该方法用来修改好友备注,描述,电话号码等内容
        Args:
            friend:好友备注
            remark:待修改的备注
            description:对好友的描述
            phoneNum:电话号码
            clear_phoneNum:清空之前所有的电话号码
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭 
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        profile_pane,main_window=Navigator.open_friend_profile(friend=friend,is_maximize=is_maximize)
        chatinfo_button=main_window.child_window(**Buttons.ChatInfoButton)
        more_button=profile_pane.child_window(**Buttons.MoreButton)
        more_button.click_input()
        pyautogui.press('down',presses=1)
        pyautogui.press('enter')
        remarkAndtag_window=profile_pane.child_window(**Windows.RemarkAndTagWindow)
        remark_edit=remarkAndtag_window.child_window(control_type='Edit',found_index=0)
        clearPhoneNum_buttons=remarkAndtag_window.descendants(**Buttons.ClearPhoneNumButton)
        if clearPhoneNum_buttons and clear_phoneNum:
            for button in clearPhoneNum_buttons:
                button.click_input()
        if phoneNum is not None and isinstance(phoneNum,str):
            addphone_button=remarkAndtag_window.child_window(**Buttons.AddPhoneNumButon)
            addphone_button.click_input()
            remarkAndtag_window.child_window(control_type='Edit',found_index=1).set_text(phoneNum)
        if description is not None and isinstance(description,str):
            description_edit=remarkAndtag_window.child_window(control_type='Edit',found_index=2)
            description_edit.set_text(description)
        addphone_button=remarkAndtag_window.child_window(**Buttons.AddPhoneNumButon)
        remark_edit.set_text(remark)
        confirm_button=remarkAndtag_window.child_window(**Buttons.CompleteButton)
        confirm_button.click_input()
        chatinfo_button.click_input()
        if close_weixin:
            main_window.close()


    
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
                raise ValueError(f'friends与files_lists长度不一致!发送人{len(friends)}个,发送文件列表个数{len(Files)}')
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
        edit_area=main_window.child_window(**Edits.CurrentChatEdit)
        chat_button=main_window.child_window(**SideBar.Chats)
        chat_button.click_input()
        if with_messages and messages_lists:#文件消息一起发且message_lists不空
            for friend in Files:
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
    def save_chatfiles(friend:str,folder_path:str=None,number:int=10,is_maximize:bool=None,close_weixin:bool=None):
        '''该方法用来导出与某个好友的聊天文件,过期未下载的无法导出
        Args:
            friend:好友或群聊的名称
            folder_path:导出文件存放的文件夹路径,不传入会自动在本地新建一个
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
            text=text.replace(friend,'')
            texts=text.split('|')
            filename=filename_pattern.search(texts[0]).group(0)
            timestamp=timestamp_pattern.search(texts[1]).group(1) 
            year=time.strftime('%Y')
            month=time.strftime('%m')
            timestamp_folder=time.strftime('%Y-%m')#默认当年当月
            if '年' in timestamp:
                year=re.search(r'(\d+)年',timestamp).group(1)
            if '月' in timestamp:
                month=re.search(r'(\d+)月',timestamp).group(1)
            timestamp_folder=f'{year}-{month}'
            return filename,timestamp_folder
        
        if folder_path and not os.path.isdir(folder_path):
            raise NotFolderError(f'所选路径不是文件夹!无法保存聊天记录,请重新选择!')
        if not folder_path:
            folder_name='save_files聊天文件保存'
            os.makedirs(name=folder_name,exist_ok=True)
            folder_path=os.path.join(os.getcwd(),folder_name)
            print(f'未传入文件夹路径,聊天文件将保存至 {folder_path}')

        filepaths=[]
        filenames=[]
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
        SystemSettings.copy_text_to_windowsclipboard(friend)
        pyautogui.hotkey('ctrl','v')
        fileList=chatfile_window.child_window(**Lists.FileList)
        search_result=chatfile_window.descendants(control_type='Text')[-1]
        total_num=int(re.search(r'\d+',search_result.window_text()).group(0))
        fileList.type_keys('{END}')
        last_file=fileList.children(control_type='ListItem',class_name='mmui::FileListCell')[-1].window_text()
        fileList.type_keys('{HOME}')
        labels=[listitem.window_text() for listitem in fileList.children(control_type='ListItem',class_name='mmui::FileListCell')]
        labels=[label for label in labels if '未下载' not in labels or '已过期' not in label]
        while len(labels)<number:
            fileList.type_keys('{PGDN}')
            last=fileList.children(control_type='ListItem',class_name='mmui::FileListCell')[-1].window_text()
            texts=[listitem.window_text() for listitem in fileList.children(control_type='ListItem',class_name='mmui::FileListCell') 
            if '未下载' not in listitem.window_text() 
            or '已过期' in listitem.window_text()]
            texts=[file for file in texts if file not in labels]
            labels.extend(texts)
            if len(labels)>=total_num:#大于等于总数
                break
            if last==last_file:#到达底部
                break
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
                SystemSettings.copy_files(samefilepaths,folder_path)
            else:#没有重复的直接移动就行
                #当然还得保证,folder_path里没有该文件
                SystemSettings.copy_file(filepath,folder_path)
        chatfile_window.close()
        return filepaths

    @staticmethod
    def export_recent_files(folder_path:str=None,is_maximize:bool=None,close_weixin:bool=None):
        '''该方法用来导出与某个好友的聊天文件,过期未下载的无法导出
        Args:
            folder_path:导出文件存放的文件夹路径,不传入会自动在本地新建一个
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
            year=time.strftime('%Y')
            month=time.strftime('%m')
            timestamp_folder=time.strftime('%Y-%m')#默认当年当月
            if '年' in timestamp:
                year=re.search(r'(\d+)年',timestamp).group(1)
            if '月' in timestamp:
                month=re.search(r'(\d+)月',timestamp).group(1)
            timestamp_folder=f'{year}-{month}'
            return filename,timestamp_folder
        
        if folder_path and not os.path.isdir(folder_path):
            raise NotFolderError(f'所选路径不是文件夹!无法保存聊天记录,请重新选择!')
        if not folder_path:
            folder_name='export_recent最近聊天文件保存'
            os.makedirs(name=folder_name,exist_ok=True)
            folder_path=os.path.join(os.getcwd(),folder_name)
            print(f'未传入文件夹路径,聊天文件将保存至 {folder_path}')
        '''该方法用来导出最近打开使用的文件'''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
    
        filenames=[]
        filepaths=[]
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
            texts=[listitem.window_text() for listitem in listitems
            if '未下载' not in listitem.window_text() 
            or '已过期' in listitem.window_text()
            or '发送中断' not in listitem.window_text()]
            texts=[file for file in texts if file not in labels]
            labels.extend(texts)
        labels=[label for label in labels if '未下载' not in labels or '已过期' not in label or '发送中断' not in label]
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
                SystemSettings.copy_files(samefilepaths,folder_path)
            else:#没有重复的直接移动就行
                #当然还得保证,folder_path里没有该文件
                SystemSettings.copy_file(filepath,folder_path)
        chatfile_window.close()
        return filepaths
    
    @staticmethod
    def export_videos(year:str=time.strftime('%Y'),month:str=None,target_folder:str=None)->list[str]:
        '''
        该函数用来导出微信保存到本地的聊天视频,只有点击下载过的视频才可以被导出
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
    
    @staticmethod
    def change_language(language:int,is_maximize:bool=None,close_weixin:bool=None):
        '''
        该方法用来修改微信的语言
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
        confirm_button.click_input()
        print(f'已将语言设置为{language_map.get(language)}')

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
        if size>1024:
            size=1024
        if size<=0:
            raise ValueError(f'size取值在1-1024之间!')
        settings_window=Navigator.open_settings(is_maximize=is_maximize,close_weixin=close_weixin)
        input_filed=settings_window.child_window(control_type='Text',class_name='mmui::XLineField')
        checkbox=input_filed.parent().children(control_type='CheckBox')[0]
        if state:
            input_filed.click_input()
            SystemSettings.copy_text_to_windowsclipboard(str(size))
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
        paths=build_path(medias)
        if not paths:
            raise ValueError(f'medias列表内无可用图片或视频路径!')
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
    def dump_recent_moments(recent:Literal['Today','Yesterday','Week','Month']='Today',number:int=None,is_maximize:bool=None,close_weixin:bool=None)->list[dict]:
        '''
        该方法用来获取最近一月内微信朋友圈内好友发布过的具体内容
        Args:
            recent:最进的时间,取值为['Today','Yesterday','Week','Month']
            number:指定的数量
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
            #按照空格split比较理想的结果是['昵称','内容','时间戳'],但是有的人昵称中或者发布的内容都含有空格，甚至有可能内容是个时间戳
            #或者转发的是视频号，时间戳不在文本末尾，split后可能是
            #['昵','称','昨天xxx','1小时前','视频号xxx']
            #但是无论如何，在这个列表中真正满足时间戳格式的字符即使用re.match筛选后，永远在列表的最后
            video_num=0
            photo_num=0
            text=listitem.window_text()
            splited_text=text.split(' ')
            possible_timestamps=[text for text in splited_text if sns_timestamp_pattern.match(text)]
            post_time=possible_timestamps[-1]
            if re.search(rf'\s包含(\d+)张图片\s',text):
                photo_num=int(re.search(rf'\s包含(\d+)张图片\s',text).group(1))
            if re.search(rf'\s视频\s',text):
                video_num=1
            content=re.sub(rf'\s((包含\d+张图片\s|视频\s).*{post_time})\s','',text)
            return content,photo_num,video_num,post_time
        
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin

        recorded_num=0
        posts=[]
        sns_timestamp_pattern=Regex_Patterns.Sns_Timestamp_pattern#朋友圈好友发布内容左下角的时间戳
        not_contents=['mmui::TimelineCommentCell','mmui::TimelineCell','mmui::TimelineAdGridImageCell']#评论区，余下x条,广告,这三种不需要
        moments_window=Navigator.open_moments(is_maximize=is_maximize,close_weixin=close_weixin)
        moments_list=moments_window.child_window(**Lists.MomentsList)
        moments_list.type_keys('{HOME}')
        #微信朋友圈当天发布时间是xx分钟前,xx小时前,一周内的时间在7天内,且包含当天时间,同理一月内的时间在30天内,包含本周的时间
        minutes={f'{i}分钟前' for i in range(1,60)}
        hours={f'{i}小时前' for i in range(1,24)}
        month_days={f'{i}天前' for i in range(1,31)}
        week_days={f'{i}天前' for i in range(1,8)}
        week_days.update(minutes)
        week_days.update(hours)
        month_days.update(week_days)
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
                    if recent=='Today' and ('昨天' in post_time or '天前' in post_time):#昨天或者x天前在时间戳里不属于今天了
                        break
                    if recent=='Yesterday' and '天前' in post_time:#当前的朋友圈内容发布时间没有天前,说明是当天和昨天
                        break
                    if recent=='Week' and post_time not in week_days:#当前的朋友圈内容发布时间不在一周的时间内
                        break
                    if recent=='Month' and post_time not in month_days:#当前的朋友圈内容发布时间不在一个月的时间内
                        break
                moments_list.type_keys('{DOWN}',pause=0.1)
            if recent=='Today':
                posts=[post for post in posts if  '天' not in post.get('发布时间')]
            if recent=='Yesterday':
                posts=[post for post in posts if post.get('发布时间')=='昨天']
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
            #按照空格split比较理想的结果是['昵称','内容','时间戳'],但是有的人昵称中或者发布的内容都含有空格，甚至有可能内容是个时间戳
            #或者转发的是视频号，时间戳不在文本末尾，split后可能是
            #['昵','称','昨天xxx','1小时前','视频号xxx']
            #但是无论如何，在这个列表中真正满足时间戳格式的字符即使用re.match筛选后，永远在列表的最后,并且该列表不可能为空
            video_num=0
            photo_num=0
            text=listitem.window_text()
            text=text.strip(' ').replace('\n','')#先去掉头尾的空格去掉换行符
            splited_text=text.split(' ')
            possible_timestamps=[text for text in splited_text if sns_timestamp_pattern.match(text)]
            post_time=possible_timestamps[-1]
            if re.search(rf'\s包含(\d+)张图片\s',text):
                photo_num=int(re.search(rf'\s包含(\d+)张图片\s',text).group(1))
            if re.search(rf'\s视频\s',text):
                video_num=1
            content=re.sub(rf'\s((包含\d+张图片\s|视频\s).*{post_time})','',text)
            return content,photo_num,video_num,post_time
        
        def like(content_listitem:ListItemWrapper):
            #点赞操作
            mouse.move(coords=center_point)
            ellipsis_area=(content_listitem.rectangle().right-44,content_listitem.rectangle().bottom-15)#省略号按钮所处位置
            mouse.click(coords=ellipsis_area)
            if like_button.exists(timeout=0.1):
                like_button.click_input()

        def comment(content_listitem:ListItemWrapper,comment_listitem:ListItemWrapper,content:str):
            #评论操作
            mouse.move(coords=center_point)
            ellipsis_area=(content_listitem.rectangle().right-44,content_listitem.rectangle().bottom-15)#省略号按钮所处位置
            mouse.click(coords=ellipsis_area)
            reply=callback(content) 
            if comment_button.exists(timeout=0.1) and reply:
                comment_button.click_input()
                pyautogui.hotkey('ctrl','a')
                pyautogui.press('backspace')
                SystemSettings.copy_text_to_windowsclipboard(text=reply)
                pyautogui.hotkey('ctrl','v')
                rectangle=comment_listitem.rectangle()
                send_button_area=(rectangle.right-70,rectangle.bottom-42)
                mouse.click(coords=send_button_area)

        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        
        posts=[]
        liked_num=0
        minutes={f'{i}分钟前' for i in range(1,60)}
        hours={f'{i}小时前' for i in range(1,24)}
        month_days={f'{i}天前' for i in range(1,31)}
        week_days={f'{i}天前' for i in range(1,8)}
        week_days.update(minutes)
        week_days.update(hours)
        month_days.update(week_days)
        sns_timestamp_pattern=Regex_Patterns.Sns_Timestamp_pattern#朋友圈好友发布内容左下角的时间戳
        not_contents=['mmui::TimelineCommentCell','mmui::TimelineCell','mmui::TimelineAdGridImageCell']#评论区，余下x条,广告,这三种不需要
        moments_window=Navigator.open_moments(is_maximize=is_maximize,close_weixin=close_weixin)
        like_button=moments_window.child_window(control_type='Button',title='赞')
        comment_button=moments_window.child_window(control_type='Button',title='评论')
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
                    if recent=='Today' and ('昨天' in post_time or '天前' in post_time):
                        break
                    if recent=='Yesterday' and '天前' in post_time:#当前的朋友圈内容发布时间没有天前,说明是当天
                        break
                    if recent=='Week' and post_time not in week_days:#当前的朋友圈内容发布时间不在一周的时间内
                        break
                    if recent=='Month' and post_time not in month_days:#当前的朋友圈内容发布时间不在一个月的时间内
                        break
        if recent=='Today':
            posts=[post for post in posts if  '天' not in post.get('发布时间')]
        if recent=='Yesterday':
            posts=[post for post in posts if post.get('发布时间')=='昨天']
        if recent=='Week':
            posts=[post for post in posts if post.get('发布时间') in week_days]
        if recent=='Month':
            posts=[post for post in posts if post.get('发布时间') in month_days]
        moments_window.close()
        return posts

    @staticmethod
    def dump_friend_moments(friend:str,number:int,save_detail:bool=False,target_folder:str=None,is_maximize:bool=None,close_weixin:bool=None)->list[dict]:
        '''
        该方法用来获取某个好友的微信朋友圈的内一定数量的内容
        Args:
            friend:好友备注
            number:具体数量
            save_detail:是否保存好友单条朋友圈的具体内容到本地(图片,文本,内容截图)
            target_folder:save_detail所需的文件夹路径
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        Returns:
            posts:朋友圈具体内容,list[dict]的格式,具体为[{'内容':xx,'图片数量':xx,'视频数量':xx,'发布时间':xx}]
        '''
        def save_media(sns_detail_list:ListViewWrapper,photo_num:int,detail_folder:str,content:str):
            content_path=os.path.join(detail_folder,'内容.txt')
            capture_path=os.path.join(detail_folder,'内容截图.png')
            #保存截图
            sns_detail_list.children(control_type='ListItem')[0].capture_as_image().save(capture_path)
            #保存内容
            with open(content_path,'w',encoding='utf-8') as f:
                f.write(content)
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
                backbutton.click_input()

        def parse_friend_post(listitem:ListItemWrapper):
            '''获取朋友圈文本中的时间戳,图片数量,以及剩余内容'''
            video_num=0
            photo_num=0
            text=listitem.window_text()
            text=text.replace(friend,'')#先去掉头尾的空格去掉换行符
            post_time=sns_detail_pattern.search(text).group(0)
            if re.search(rf'\s包含(\d+)张图片\s',text):
                photo_num=int(re.search(r'\s包含(\d+)张图片\s',text).group(1))
            if re.search(rf'\s视频\s{post_time}',text):
                video_num=1
            content=re.sub(rf'\s((包含\d+张图片\s|视频\s).*{post_time})\s','',text)
            return content,photo_num,video_num,post_time

        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if save_detail  and target_folder is None:
            target_folder=os.path.join(os.getcwd(),f'dump_friend_moments朋友圈图片保存')
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
        not_contents=['mmui::AlbumBaseCell','mmui::AlbumTopCell']#置顶内容不需要
        moments_window=Navigator.open_friend_moments(friend=friend,is_maximize=is_maximize,close_weixin=close_weixin)
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
                        save_media(sns_detail_list,photo_num,detail_folder,content)
                    recorded_num+=1
                    if sns_detail_list.exists(timeout=0.1):
                        backbutton.click_input()
                    if Tools.is_sns_at_bottom(moments_list,selected[0]):
                        break
                if recorded_num>=number:
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
            post_time=sns_detail_pattern.search(text).group(0)
            if re.search(rf'\s包含(\d+)张图片\s',text):
                photo_num=int(re.search(r'\s包含(\d+)张图片\s',text).group(1))
            if re.search(rf'\s视频\s{post_time}',text):
                video_num=1
            content=re.sub(rf'\s((包含\d+张图片\s|视频\s).*{post_time})\s','',text)
            return content,photo_num,video_num,post_time

        def like(listview:ListViewWrapper,content_listitem:ListItemWrapper):
            #点赞操作
            center_point=(listview.rectangle().mid_point().x,listview.rectangle().mid_point().y)
            mouse.move(coords=center_point)
            ellipsis_area=(content_listitem.rectangle().right-44,content_listitem.rectangle().bottom-15)#省略号按钮所处位置
            mouse.click(coords=ellipsis_area)
            if like_button.exists(timeout=0.1):
                like_button.click_input()

        def comment(listview:ListViewWrapper,content_listitem:ListItemWrapper,content:str):
            #评论操作
            comment_listitem=Tools.get_next_item(listview,content_listitem)
            center_point=(listview.rectangle().mid_point().x,listview.rectangle().mid_point().y)
            mouse.move(coords=center_point)
            ellipsis_area=(content_listitem.rectangle().right-44,content_listitem.rectangle().bottom-15)#省略号按钮所处位置
            mouse.click(coords=ellipsis_area)
            reply=callback(content) 
            if comment_button.exists(timeout=0.1):
                comment_button.click_input()
                pyautogui.hotkey('ctrl','a')
                pyautogui.press('backspace')
                SystemSettings.copy_text_to_windowsclipboard(text=reply)
                pyautogui.hotkey('ctrl','v')
                rectangle=comment_listitem.rectangle()
                send_button_area=(rectangle.right-70,rectangle.bottom-42)
                mouse.click(coords=send_button_area)

        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        posts=[]
        liked_num=0
        sns_detail_pattern=Regex_Patterns.Snsdetail_Timestamp_pattern#朋友圈好友发布内容左下角的时间戳pattern
        not_contents=['mmui::AlbumBaseCell','mmui::AlbumTopCell']#置顶内容不需要
        moments_window=Navigator.open_friend_moments(friend=friend,is_maximize=is_maximize,close_weixin=close_weixin)
        backbutton=moments_window.child_window(**Buttons.BackButton)
        #直接maximize不行,需要使用win32gui
        win32gui.SendMessage(moments_window.handle,win32con.WM_SYSCOMMAND,win32con.SC_MAXIMIZE,0)
        moments_list=moments_window.child_window(**Lists.MomentsList)
        sns_detail_list=moments_window.child_window(**Lists.SnsDetailList)
        like_button=moments_window.child_window(control_type='Button',title='赞')
        comment_button=moments_window.child_window(control_type='Button',title='评论')
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
                    # comment_listitem=sns_detail_list.children(control_type='ListItem')[1]
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
        at_all:bool=False,clear:bool=None,
        send_delay:float=None,is_maximize:bool=None,close_weixin:bool=None)->None:
        '''
        该方法用于给单个好友或群聊发送信息
        Args:
            friend:好友或群聊备注。格式:friend="好友或群聊备注"
            messages:所有待发送消息列表。格式:message=["消息1","消息2"]
            at_members:群聊内所有需要@的群成员昵称列表(注意必须是群昵称)
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
        if clear is None:
            clear=GlobalConfig.clear
        if not messages:
            raise CantSendEmptyMessageError
        #先使用open_dialog_window打开对话框
        main_window=Navigator.open_dialog_window(friend=friend,is_maximize=is_maximize)
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
            SystemSettings.copy_text_to_windowsclipboard(friend)
            pyautogui.hotkey('ctrl','v')
            time.sleep(1)
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
        该方法用来检查一遍会话列表内的所有新消息具体内容
        '''
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if search_pages is None:
            search_pages=GlobalConfig.search_pages
        newMessages=[]
        main_window=Navigator.open_weixin(is_maximize=is_maximize)
        new_message_num=get_new_message_num(main_window)
        if not new_message_num:
            if close_weixin:
                main_window.close()
            print(f'未发现新消息')
            return {}
        else:
            new_message_dict=scan_for_new_messages(is_maximize=is_maximize,close_weixin=False)
            for friend,num in new_message_dict.items():
                message=Messages.pull_messages(friend=friend,number=num,close_weixin=False)
                newMessages.append(message)
            if close_weixin:
                main_window.close()
            return dict(zip(new_message_dict.keys(),newMessages))
    
    #session_pick_window中使用ui自动化选择2个以上好友时微信会莫名奇妙白屏卡死，所以先暂时不实现这个方法了
    @staticmethod
    def forward_message(friends:list[str],message:str,clear:bool=None,
        send_delay:float=None,is_maximize:bool=None,close_weixin:bool=None)->None:
     
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if send_delay is None:
            send_delay=GlobalConfig.send_delay
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if clear is None:
            clear=GlobalConfig.clear
        if len(friends)<2:
            raise ValueError(f'friends数量不足2,无法转发消息!')
        def session_picker():
            session_pick_window=main_window.child_window(**Windows.SessionPickerWindow)
            send_button=session_pick_window.child_window(control_type='Button',title='发送')
            checkbox=session_pick_window.child_window(control_type='CheckBox',found_index=0)
            rec=send_button.rectangle()
            x,y=rec.mid_point().x,rec.mid_point().y
            search_field=session_pick_window.child_window(control_type='Edit',found_index=0)
            search_field.click_input()
            for friend in friends[1:]:
                search_field.set_text(friend)
                checkbox.click_input()
                search_field.click_input()
                search_field.set_text('')
            pyautogui.click(x=x,y=y)
        main_window=Navigator.open_dialog_window(friend=friends[0],is_maximize=is_maximize)
        edit_area=main_window.child_window(**Edits.CurrentChatEdit)
        chat_list=main_window.child_window(**Lists.FriendChatList)
        if not edit_area.exists(timeout=0.1):
            raise NotFriendError(f'非正常好友,无法发送消息')
        if clear:
            edit_area.set_text('')
        if len(message)==0:
            main_window.close()
            raise CantSendEmptyMessageError
        if 0<len(message)<2000:
            edit_area.set_text(message)
            time.sleep(send_delay)
            pyautogui.hotkey('alt','s',_pause=False)
        elif len(message)>2000:#字数超过200字发送txt文件
            SystemSettings.convert_long_text_to_txt(message)
            pyautogui.hotkey('ctrl','v',_pause=False)
            time.sleep(send_delay)
            pyautogui.hotkey('alt','s',_pause=False)
            warn(message=f"微信消息字数上限为2000,超过2000字部分将被省略,该条长文本消息已为你转换为txt发送",category=LongTextWarning)
        if len(friends)>1:
            listItems=chat_list.children(control_type='ListItem')
            message_sent=listItems[-1]
            rect=message_sent.rectangle()
            mouse.right_click(coords=(rect.right-100,rect.mid_point().y))
            forward_item=main_window.child_window(**MenuItems.ForwardMenuItem)
            forward_item.click_input()
            session_picker()
        if close_weixin:
            main_window.close()

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
            msg=timestamp_pattern.sub(repl='',string=res).replace('已置顶 ','').replace('消息免打扰','')
            return msg
        
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
        timestamp_pattern=Regex_Patterns.Session_Timestamp_pattern
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
                listItems=message_list_pane.children(**ListItems.SessionListItem)
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
        def filter_sessions(listItems):
            listItems=[listItem for listItem in listItems if get_sending_time(listItem)]
            if chat_only:
                listItems=[listItem for listItem in listItems if get_latest_message(listItem)!='']
            return listItems
        
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
        timestamp_pattern=Regex_Patterns.Session_Timestamp_pattern
        main_window=Navigator.open_weixin(is_maximize=is_maximize)
        chats_button=main_window.child_window(**SideBar.Chats)
        session_list=main_window.child_window(**Main_window.ConversationList)
        if not session_list.exists():
            chats_button.click_input()
        if not session_list.is_visible():
            chats_button.click_input()
        scrollable=Tools.is_scrollable(session_list,back='end')
        if not scrollable:
            names=[get_name(listitem) for listitem in session_list.children(control_type='ListItem')]
            last_sending_times=[get_sending_time(listitem) for listitem in session_list.children(control_type='ListItem')]
            lastest_message=[get_latest_message(listitem) for listitem in session_list.children(control_type='ListItem')]
        if scrollable:
            time.sleep(0.5)
            last=session_list.children(control_type='ListItem')[-1].window_text()
            session_list.type_keys('{HOME}')
            time.sleep(0.5)
            while True:
                listItems=session_list.children(**ListItems.SessionListItem)
                listItems=filter_sessions(listItems)
                names.extend([get_name(listitem) for listitem in listItems])
                last_sending_times.extend([get_sending_time(listitem) for listitem in listItems])
                lastest_message.extend([get_latest_message(listitem) for listitem in listItems])
                session_list.type_keys('{PGDN}')
                if listItems[-1].window_text()==last:
                    break
            names.extend([get_name(listitem) for listitem in session_list.children(control_type='ListItem')])
            last_sending_times.extend([get_sending_time(listitem) for listitem in session_list.children(control_type='ListItem')])
            lastest_message.extend([get_latest_message(listitem) for listitem in session_list.children(control_type='ListItem')])
            session_list.type_keys('{HOME}')
        if close_weixin:
            main_window.close()
        #list zip为[(发送人,发送时间,最后一条消息)]
        sessions=list(zip(names,last_sending_times,lastest_message))
        #去重
        sessions=remove_duplicates(sessions)
        return sessions

    @staticmethod
    def pull_messages(friend:str,number:int,search_pages:int=None,is_maximize:bool=None,close_weixin:bool=None)->list[str]:
        '''
        该函数用来从聊天界面获取聊天消息,也可当做获取聊天记录
        Args:
            friend:好友名称
            number:获取的消息数量
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
        main_window=Navigator.open_dialog_window(friend=friend,is_maximize=is_maximize,search_pages=search_pages)
        chat_list=main_window.child_window(**Lists.FriendChatList)
        if not chat_list.exists(timeout=0.1):
            print(f'非正常好友或群聊,无法获取聊天信息！')
            return messages
        else:
            if not chat_list.children(control_type='ListItem'):
                warn(message=f"你与{friend}的聊天记录为空,无法获取聊天信息",category=NoChatHistoryWarning)
                return messages
            last_item=chat_list.children(control_type='ListItem')[-1]
            messages.append(last_item.window_text())
            Tools.activate_chatList(chat_list)
            while len(messages)<number:
                chat_list.type_keys('{UP}')
                selected=[listitem for listitem in chat_list.children(control_type='ListItem') if listitem.has_keyboard_focus()]
                if selected and selected[0].class_name()!='mmui::ChatItemView':
                    messages.append(selected[0].window_text())
                if not selected:
                    break
            chat_list.type_keys('{END}')
            messages=messages[-number:]
            if close_weixin:
                main_window.close()
        return messages

    @staticmethod
    def dump_chat_history(friend:str,number:int,capture_alia:bool=False,alias_folder:str=None,is_maximize:bool=None,close_weixin:bool=None)->tuple[list,list]:
        '''该函数用来获取一定数量的聊天记录
        Args:  
            friend:好友名称
            number:获取的消息数量
            capture_alia:是否截取聊天记录中聊天对象的昵称
            alias_folder:保存聊天对象昵称截图的文件夹
            is_maximize:微信界面是否全屏，默认不全屏
            close_weixin:任务结束后是否关闭微信，默认关闭
        Returns:
            (messages,timestamps):发送的消息(时间顺序从晚到早),每条消息对应的发送时间
        '''
        def is_at_bottom(chat_history_list,listitem):
            at_bottom=False
            pyautogui.press('down',presses=2,_pause=False)
            if Tools.get_next_item(chat_history_list,listitem) is None:
                at_bottom=True
            pyautogui.press('up',presses=2,_pause=False)
            return at_bottom
        
        if is_maximize is None:
            is_maximize=GlobalConfig.is_maximize
        if close_weixin is None:
            close_weixin=GlobalConfig.close_weixin
        if capture_alia and alias_folder is None:
            alias_folder=os.path.join(os.getcwd(),f'dump_chat_history好友昵称截图',f'{friend}')
            print(f'未传入文件夹路径,好友昵称截图将分别保存到{alias_folder}内')
            os.makedirs(alias_folder,exist_ok=True)
        messages=[]
        timestamp_pattern=Regex_Patterns.Chathistory_Timestamp_pattern
        chat_history_window=Navigator.open_chat_history(friend=friend,is_maximize=is_maximize,close_weixin=close_weixin)
        chat_history_list=chat_history_window.child_window(**Lists.ChatHistoryList)
        if not chat_history_list.exists(timeout=0.1):
            warn(message=f"你与{friend}的聊天记录为空,无法获取聊天记录",category=NoChatHistoryWarning)
            chat_history_window.close()
            return messages
        first_item=chat_history_list.children(control_type='ListItem')[0]
        Tools.activate_chatHistoryList(chat_history_list)
        messages.append(first_item.window_text())
        if capture_alia:
            path=os.path.join(alias_folder,f'与{friend}聊天记录_1.png')
            alia_image=Tools.capture_alias(first_item)
            alia_image.save(path)
        while len(messages)<number:
            pyautogui.press('down',presses=2,_pause=False)
            selected=[listitem for listitem in chat_history_list.children(control_type='ListItem') if listitem.has_keyboard_focus()]
            if selected:
                messages.append(selected[0].window_text())
                if capture_alia:
                    time.sleep(0.1)#必须等待0.2s以上才能截出指定数量的图，不然过快来不及截图
                    path=os.path.join(alias_folder,f'与{friend}聊天记录_{len(messages)}.png')
                    alia_image=Tools.capture_alias(selected[0])
                    alia_image.save(path)
                if is_at_bottom(chat_history_list,selected[0]):
                    break
               
        chat_history_list.type_keys('{HOME}')
        chat_history_window.close()
        messages=messages[:number]
        timestamps=[timestamp_pattern.search(message).group(0) if timestamp_pattern.search(message) else '微信红包或转账(时间戳为图片非文本无法获取)' for message in messages]
        messages=[timestamp_pattern.sub('',message) for message in messages]
        return messages,timestamps

class Monitor():
    '''监听消息的一些方法'''

    @staticmethod
    def listen_on_chat(dialog_window:WindowSpecification,duration:str,save_file:bool=False,save_photo:bool=False,target_folder:str=None,close_dialog_window:bool=True)->dict:
        '''
        该方法用来在指定时间内监听会话窗口内的新消息(可以配合多线程使用,一次监听多个会话内的消息)
        Args:
            dialog_window:好友单独的聊天窗口或主界面内的聊天窗口,可使用Navigator内的方法打开
            duraiton:监听持续时长,监听消息持续时长,格式:'s','min','h'单位:s/秒,min/分,h/小时
            save_file:是否保存文件,需开启自动下载文件并设置为1024MB,默认为False
            save_photo:是否保存图片,注意不要在多线程中设置为True,针对单个好友可以设置为True,默认为False
            capture_alia:是否截取发送消息的对象群昵称图片,包含完整群昵称(只能截取到其他群成员新消息的群昵称),截图时,dialog_window不能最小化
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

        def make_unique_id(listitem:ListItemWrapper):
            '''根据图片所在listitem的高度与runtime_id之和生成unique_id
            不能用宽度,所有的listitem宽度都一样,不同大小的图片listitem高度不一样
            内容一样的图片runtime_id一样,高度也一样,unique_id也一样
            '''
            height=listitem.rectangle().bottom-listitem.rectangle().top
            runtime_id=listitem.element_info.runtime_id
            unique_id=runtime_id[0]+runtime_id[1]+runtime_id[2]+height
            return unique_id
        
        def save_photos(chatList:ListViewWrapper):
            #必须全屏,不全屏图片被折叠
            win32gui.SendMessage(dialog_window.handle, win32con.WM_SYSCOMMAND, win32con.SC_MAXIMIZE,0)
            saved_image_count=0
            chatList.children()[-1].double_click_input()#点一下最后一个
            while saved_image_count!=image_count:
                selected=[listitem for listitem in chatList.children(control_type='ListItem',class_name='mmui::ChatBubbleReferItemView',title='图片') 
                if listitem.has_keyboard_focus()]   
                if selected:
                    unique_id=make_unique_id(selected[-1])
                    if image_ids[-1]==unique_id:
                        timestamp=time.strftime(f'%y-%m-%d-%H时%M分%S秒')
                        path=os.path.join(image_folder,f'{friend}_{timestamp}.png')#时间戳和好友名字做文件名保证不会重复
                        rectangle=selected[-1].rectangle()
                        side_x=rectangle.left+120
                        center_y=rectangle.mid_point().y
                        mouse.right_click(coords=(side_x,center_y))#不要直接right_click_input(),x方向应该是chatList左边界靠右一些,y方向是中心
                        copy_item.click_input()
                        SystemSettings.save_pasted_image(path)
                        saved_image_count+=1
                        image_ids.pop()#最后的元素即刚刚保存的图片的runtime_id从image_ids从尾部pop出去
                chatList.type_keys('{UP}',pause=0.15)
            win32gui.SendMessage(dialog_window.handle,win32con.WM_SYSCOMMAND,win32con.SC_MINIMIZE,0)

        duration=Tools.match_duration(duration)#将's','min','h'转换为秒
        if not duration:#不按照指定的时间格式输入,需要提前中断退出
            raise TimeNotCorrectError
        if (save_file or save_photo ) and target_folder is None:
            target_folder=os.path.join(os.getcwd(),f'{dialog_window.window_text()}_listen_on_chat聊天文件保存')
            print(f'未传入文件夹路径,文件,图片将分别保存到{target_folder}内的Files,Images文件夹下\n')
            os.makedirs(target_folder,exist_ok=True)
        if save_file:
            file_folder=os.path.join(target_folder,'Files')
            os.makedirs(file_folder,exist_ok=True)
        if save_photo:
            image_folder=os.path.join(target_folder,'Images')
            os.makedirs(image_folder,exist_ok=True)
       
        total=0
        link_count=0
        video_count=0
        image_count=0
        files=[]
        texts=[]
        image_ids=[]
        friend=dialog_window.window_text()
        file_pattern=Regex_Patterns.File_Pattern
        timestamp=time.strftime('%Y-%m')
        chatfile_folder=Tools.where_chatfile_folder()
        chatList=dialog_window.child_window(**Lists.FriendChatList)#聊天界面内存储所有信息的容器
        copy_item=dialog_window.child_window(**MenuItems.CopyMenuItem)
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
                    if newMessage.class_name()=='mmui::ChatBubbleItemView' and newMessage.window_text()[:2]=='[链接]':#
                        link_count+=1
                    if newMessage.class_name()=='mmui::ChatBubbleReferItemView' and newMessage.window_text()=='图片':
                        image_count+=1
                        unique_id=make_unique_id(newMessage)#把图片的runtime_id和其所处的listitem高度保存下来结合一下作为它的唯一可识别属性
                        image_ids.append(unique_id)
                        #只是依靠class_name,window_text还有数量筛选，假如结束时又新发了几张图片，内容会对不上         
                    if newMessage.class_name()=='mmui::ChatBubbleReferItemView' and '视频' in newMessage.window_text():
                        video_count+=1#视频需要下载直接右键复制不行,需要先点击,如果时间长,要等半天，不太方便
                    if newMessage.class_name()=='mmui::ChatBubbleItemView' and '文件' in newMessage.window_text():
                        filename=file_pattern.search(newMessage.window_text()).group(1)
                        filepath=os.path.join(chatfile_folder,timestamp,filename)
                        files.append(filepath)
                    initial_runtime_id=runtime_id
       
        SystemSettings.close_listening_mode()
        #最后结束时再批量复制到target_folder,不在循环里逐个复制是考虑到若文件过大(几百mb)没有自动下载完成移动不了
        if save_file and files:SystemSettings.copy_files(files,file_folder)#文件复制粘贴到target_folder/Files内
        if save_photo and image_count:save_photos(chatList)#保存图片到target_folder/Images内
        if close_dialog_window:dialog_window.close()
        details={'新消息总数':total,'文本数量':len(texts),'文件数量':len(files),'图片数量':image_count,'视频数量':video_count,'链接数量':link_count,'文本内容':texts}
        return details
    
    @staticmethod
    def grab_red_packet(dialog_window:WindowSpecification,duration:str,close_dialog_window:bool=True)->int:
        '''
        该函数用来点击领取好友发送的红包,群聊中的红包微信的设定是电脑端无法打开,因此无法使用
        Args:
            dialog_window:好友单独的聊天窗口,可使用Navigator内的方法打开
            duraiton:监听持续时长,监听消息持续时长,格式:'s','min','h'单位:s/秒,min/分,h/小时
            close_dialog_window:是否关闭dialog_window
        Returns:
            red_packet_count:该聊天窗口内抢到红包个数
        '''
        def open_redpacket(red_packet):
            red_packet.click_input()
            open_button=red_envelop_view.child_window(control_type='Button',title='拆开')
            open_button.click_input()
            red_envelop_detail.close()
        
        duration=Tools.match_duration(duration)#将's','min','h'转换为秒
        if not duration:#不按照指定的时间格式输入,需要提前中断退出
            raise TimeNotCorrectError
        red_packet_count=0
        chatList=dialog_window.child_window(**Lists.FriendChatList)#聊天界面内存储所有信息的容器
        chatList.type_keys('{END}')
        red_envelop_view=dialog_window.child_window(class_name='mmui::PayRedEnvelopeInfoView',title='',control_type='Group')#微信红包点击后弹出的界面
        red_envelop_detail=desktop.window(class_name='mmui::PayRedEnvelopDetailWindow',control_type='Window',title='微信')
        initial_message=chatList.children(control_type='ListItem')[-1]#刚打开聊天界面时的最后一条消息的listitem
        initial_runtime_id=initial_message.element_info.runtime_id
        end_timestamp=time.time()+duration#根据秒数计算截止时间
        SystemSettings.open_listening_mode(volume=False)
        while time.time()<end_timestamp:
            newMessage=chatList.children(control_type='ListItem')[-1]
            text=newMessage.window_text()
            class_name=newMessage.class_name()
            runtime_id=newMessage.element_info.runtime_id
            if runtime_id!=initial_runtime_id and '微信红包' in text  and class_name=='mmui::ChatBubbleItemView': 
                open_redpacket(newMessage)
                red_packet_count+=1
                initial_runtime_id=runtime_id
        SystemSettings.close_listening_mode()
        if close_dialog_window:dialog_window.close()
        return red_packet_count
