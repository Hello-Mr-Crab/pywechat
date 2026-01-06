'''
Uielements
---------
PC微信中的各种Ui-Object,包括:
    - `Main_Window`: 主界面窗口内的一些Ui
    - `Login_Window`: 登录界面内的一些Ui
    - `Independent_Window`: 独立界面窗口
    - `SideBar`: SideBar类型Ui
    - `Buttons`: Button类型Ui
    - `Windows`: Window类型Ui
    - `Texts`: Text类型Ui
    - `Edits`: Edit类型Ui
    - `Lists`: List类型Ui
    - `Groups`: Group类型Ui
    - `ListItems`: ListItem类型Ui
    - `Customs`: 自定义类型Ui

    
Examples
--------
使用时只需要:
    
    >>> from pyweixin.Uielements import Edits
    >>> #返回值为kwargs字典,可以直接使用**解包
    >>> searchbar=Edits().SearchEdit
    
'''


language='简体中文'#目前只支持简体中文，还未增加其他语言扩展

class Buttons():
    '''
    微信主界面内所有类型为Button的UI控件
    '''
    def __init__(self):
        self.QuickActionsButton={'control_type':'Button','title':'快捷操作'}#主界面+号按钮
        self.OffLineButton={'title':'当前网络不可用','control_type':'Button'}#网络不好时,微信顶部的按钮
        self.WeixinButton={'control_type':'Button','found_index':0}#主界面下的第一个按钮,侧边栏的微信按钮
        self.SendButton={'control_type':'Button','title':'发送(S)'}#发送按钮
        self.ChatInfoButton={'control_type':'Button','title':'聊天信息'}#群聊/好友聊天主界面右上角的三个点
        self.CheckMoreMessagesButton={'title':'查看更多消息','control_type':'Button','found_index':1}#好友聊天界面内的查看更多消息按钮
        self.OfficialAcountButton={'title':'公众号','control_type':'Button'}#搜一搜内公众号按钮                                                                                                                                
        self.SettingsAndOthersButton={'title':'设置','control_type':'Button'}#设置按钮
        self.ConfirmQuitGroupButton={'title':'退出','control_type':'Button'}#确认退出群聊按钮
        self.CerateNewNote={'title':'新建笔记','control_type':'Button'}#创建一个新笔记按钮
        self.CerateGroupChatButton={'title':"发起群聊",'control_type':"Button"}#创建新群聊按钮
        self.AddNewFriendButon={'title':'添加朋友','control_type':'Button'}#添加新朋友按钮
        self.AddToContactsButton={'control_type':'Button','title':'添加到通讯录'}#添加新朋友时的添加至通讯录内按钮
        self.AcceptButton={'control_type':'Button','title':'接受'}#接听电话按钮
        self.ChatMessageButton={'title':'聊天信息','control_type':'Button'}#聊天信息按钮                   
        self.CloseAutoLoginButton={'control_type':'Button','title':'关闭自动登录'}#微信设置关闭自动登录按钮
        self.ConfirmButton={'control_type':'Button','title':'确定'}#确定操作按钮
        self.CancelButton={'control_type':'Button','title':'取消'}#取消操作按钮
        self.DeleteButton={'control_type':'Button','title':'确定'}#删除好友按钮
        self.ClearButton={'control_type':'Button','title':'确定'}#删除好友按钮
        self.MultiSelectButton={'control_type':'Button','title':'多选'}#转发消息或文件时的多选按钮
        self.HangUpButton={'control_type':'Button','title':'挂断'}#接听语音或视频电话按钮
        self.SendButton={'control_type':'Button','title':'发送'}#转发文件或消息按钮
        self.SendRespectivelyButton={'control_type':'Button','title_re':'分别发送'}#转发消息时分别发送按钮
        self.SettingsButton={'control_type':'Button','title':'设置','found_index':0}#工具栏打开微信设置menu内的选项按钮
        self.ChatFilesButton={'control_type':'Button','title':'聊天文件','found_index':0}#工具栏打开微信设置menu内的选项按钮
        self.ClearChatHistoryButton={'control_type':'Button','title':'清空聊天记录'}#清空好友或群聊聊天记录时的按钮
        self.RestoreDefaultSettingsButton={'control_type':'Button','title':'恢复默认设置'}#微信设置回复默认设置
        self.VoiceCallButton={'control_type':'Button','title':'语音聊天'}#给好友拨打语音电话按钮
        self.VideoCallButton={'control_type':'Button','title':'视频聊天'}#给好友拨打视频电话按钮
        self.CompleteButton={'control_type':'Button','title':'完成'}#完成按钮
        self.PinButton={'control_type':'Button','title':'置顶'}#将好友置顶按钮
        self.CancelPinButton={'control_type':'Button','title':'取消置顶'}#取消好友置顶按钮
        self.TagEditButton={'control_type':'Button','title':'点击编辑标签'}#编辑好友标签按钮
        self.ChatHistoryButton={'control_type':'Button','title':'聊天记录'}#获取聊天记录按钮
        self.ChangeGroupNameButton={'control_type':'Button','title':'群聊名称'}#修改群聊名称按钮
        self.MyNicknameInGroupButton={'control_type':'Button','title':'我在本群的昵称'}#修改群内我的昵称按钮
        self.RemarkButton={'control_type':'Button','title':'备注'}#修改群聊备注时的按钮
        self.QuitGroupButton={'control_type':'Button','title':'退出群聊'}#退出某个群聊时的按钮
        self.DeleteButton={'control_type':'Button','title':'删除'}#将好友从群聊删除时界面内的按钮
        self.EditButton={'control_type':'Button','title':'编辑'}#编辑群公告内已有内容时下方的按钮
        self.EditGroupNotificationButton={'control_type':'Button','title':'点击编辑群公告'}#编辑群公告按钮
        self.PublishButton={'control_type':'Button','title':'发布'}#编辑群公告完成后发布群公告的发布按钮
        self.ContactsManageButton={'title':'通讯录管理','control_type':'Button'}#通讯录管理按钮
        self.ConfirmEmptyChatHistoryButon={'title':'清空','control_type':'Button'}#点击清空聊天记录后弹出的query界面内的清空按钮
        self.MoreButton={'title':'更多','control_type':'Button'}#打开微信好友设置界面更多按钮
        self.LogoutButton={'title':'退出登录','control_type':'Button'}#设置界面里退出登录按钮
        self.RefreshButton={'title':'刷新','control_type':'Button'}#朋友圈的刷新按钮
        self.RectentGroupButton={'title':'最近群聊','control_type':'Button'}#通讯录设置界面里的最近群聊按钮
        self.MultiPersonCallButton={'title':'多人通话','control_type':'Button'}#群聊界面里的多人通话

class Edits():
    '''微信主界面内所有类型为Edit(不包含独立窗口)的UI控件'''
    def __init__(self):
        self.SearchEdit={'title':'搜索','control_type':'Edit','class_name':"mmui::XValidatorTextEdit"}#主界面顶部的搜索栏
        self.CurrentChatEdit={'control_type':'Edit','auto_id':"chat_input_field"}#微信主界面下当前的聊天窗口
        self.AddNewFriendSearchEdit={'title':'搜索','control_type':'Edit'}#添加新朋友界面里的搜索
        self.SearchNewFriendEdit={'title':'微信号/手机号','control_type':'Edit'}#添加新朋友界面里的搜
        self.TagEdit={'title':'设置标签','control_type':'Edit'}#编辑好友或群聊标签
        self.RequestContentEdit={'title_re':'我是','control_type':'Edit'}#添加好友(从群里或者是主页)时,发送请求时的内容
        self.SearchGroupMemeberEdit={'title':'搜索群成员','control_type':'Edit'}#添加或删除群成员时,在弹出的界面里顶部的搜索栏
        self.EditWnd={'control_type':'Edit','class_name':'EditWnd','framework_id':'Win32'}#通用的编辑框,主要出现在好友和群聊设置界面里

class ListItems():
    def __init__(self):
        '''微信主界面内所有类型为ListItem的UI控件'''
        self.SessionListItem={'control_type':'ListItem','class_name':'mmui::ChatSessionCell'}#微信会话列表中的聊天对象
        self.RecentUsedListItem={'control_type':'ListItem','class_name':'mmui::XTableCell','title':'最近使用'}#聊天文件中的最近使用
        self.FriendPrivacyListItem={'control_type':'ListItem','class_name':'mmui::ContactsManagerControlFolderCell','title':'朋友权限'}#通讯录管理界面中的朋友权限
        self.TagListItem={'control_type':'ListItem','class_name':'mmui::ContactsManagerControlFolderCell','title':'标签'}#通讯录管理界面中的标签
        self.RecentGroupListItem={'control_type':'ListItem','class_name':'mmui::ContactsManagerControlFolderCell','title':'最近群聊'}#通讯录管理界面中的最近群聊
        
class Texts():
    '''微信主界面以及设置界面内所有类型为Text的UI控件'''
    def __init__(self):
         self.CurrentChatText={'auto_id':"content_view.top_content_view.title_h_view.left_v_view.left_content_v_view.left_ui_.big_title_line_h_view.current_chat_name_label",
        'control_type':"Text"}#主界面右侧顶部的好友名称
        self.NetWorkError={'title':'网络不可用，请检查你的网络设置','control_type':'Text'}#微信没联网时顶部的红色文本
        self.OutLineText={'title':'外观','control_type':'Text'}#设置界面内的外观文本
        self.LanguageText={'title':'语言','control_type':'Text'}#设置界面内的语言文本
        self.SearchContactsResult={'title_re':'搜索','control_type':'Text'}#搜索联系人时的文本结果
        self.ChangeGroupNameWarnText={'title':'仅群主或管理员可以修改','control_type':'Text'}#修改群名时如果有这个文本，无权修改
        self.EditGroupNoticeWarnText={'title':'仅群主和管理员可编辑','control_type':'Text'}#编辑群公告或群名时，如果界面有这个文本，无权编辑
        self.SendMessageShortcutText={'title':'发送消息','control_type':'Text'}#发送消息快捷键文本,修改快捷键设置时要用到
        self.CptureScreenShortcutText={'title':'截取屏幕','control_type':'Text'}#截取屏幕快捷键文本,修改快捷键设置时要用到
        self.OpenWechatShortcutText={'title':'打开微信','control_type':'Text'}#打开微信快捷键文本,修改快捷键设置时要用到
        self.LockWechatShortcutText={'title':'锁定微信','control_type':'Text'}#锁定微信快捷键文本,修改快捷键设置时要用到
        self.LanguageText={'title':'语言','control_type':'Text'}#语言文本，修改微信语言时要用到
        self.GroupNameText={'title':'群聊名称','control_type':'Text'}#群聊设置界面内的群聊名称文本

class TabItems():
    def __init__(self):
        self.ShortCutTabItem={'title':'快捷键','control_type':'TabItem'}#微信设置界面里左侧的快捷键Tabitem
        self.GeneralTabItem={'title':'通用设置','control_type':'TabItem'}#微信设置界面里左侧的通用设置Tabitem
        self.MyAccountTabItem={'title':'账号设置','control_type':'TabItem'}#微信设置界面里左侧的账号设置Tabitem
        self.NotificationsTabItem={'title':'消息通知','control_type':'TabItem'}#微信设置界面里左侧的消息通知Tabitem
        self.FileTabItem={'title':'文件','control_type':'TabItem'}#微信聊天记录界面里顶部的文件Tabitem
        self.PhotoAndVideoTabItem={'title':'图片与视频','control_type':'TabItem','class_name':'mmui::XButton','framework_id':'Qt'}#微信聊天记录界面里顶部的照片和视频Tabitem
        self.LinkTabItem={'title':'链接','control_type':'TabItem','class_name':'mmui::XButton','framework_id':'Qt'}#微信聊天记录界面里顶部的链接Tabitem
        self.MiniProgramTabItem={'title':'小程序','control_type':'TabItem','class_name':'mmui::XButton','framework_id':'Qt'}#微信聊天记录界面里顶部的小程序Tabitem
        self.MusicTabItem={'title':'音乐与音频','control_type':'TabItem','class_name':'mmui::XButton','framework_id':'Qt'}#微信聊天记录界面里顶部的音乐Tabitem
        self.ChannelTabItem={'title':'视频号','control_type':'TabItem','class_name':'mmui::XButton','framework_id':'Qt'}#微信聊天记录界面里顶部的视频号Tabitem
        self.DateTabItem={'title':'日期','control_type':'TabItem'}#微信聊天记录界面里顶部的日期TabitemW
        
class Lists():
    def __init__(self):
        self.QuickActionsList={'title':'快捷操作','control_type':'List'}#主界面点击+号后弹出的快捷操作列表
        self.ChatHistoryList={'title':'聊天记录','control_type':'List'}#聊天记录窗口中的存放聊天消息的列表
        self.ContactsList={'title':'通讯录','control_type':'List'}#通讯录中的通讯录列表
        self.ConversationList={'title':'会话','control_type':'List'}#主界面左侧的好友聊天会话列表
        self.FriendChatList={'title':'消息','control_type':'List'}#聊天界面内的消息列表
        self.FileList={'title':'文件','control_type':'List'}#聊天记录窗口中选择文件后的文件列表
        self.PhotoAndVideoList={'title':'照片和视频','control_type':'List'}#微信聊天记录窗口中选择图片与视频后的列表 
        self.LinkList={'title':'链接','control_type':'List'}#微信聊天记录窗口中选择链接后的列表
        self.MiniProgramList={'title':'小程序','control_type':'List'}#微信聊天记录窗口中选择小程序后的列表
        self.MusicList={'title':'音乐与音频','control_type':'List'}#微信聊天记录窗口中选择音乐与音频后的列表
        self.ChannelList={'title':'视频号','control_type':'List'}#微信聊天记录窗口中选择视频号后的列表
        self.SideList={'control_type':'List','class_name':"mmui::ContactsManagerControlView"}#通讯录管理界面左侧侧边栏
        self.ContactsManageList={'control_type':'List','class_name':'mmui::ContactsManagerControlView'}#通讯录管理界面左侧列表

class Panes():
    def __init__(self):
        self.ContactsManagePane={'title':'全部','control_type':'Pane'}#通讯录管理界面内的全部Pane,之所以用到它是为了获取这个Pane下的总人数
        self.ConfirmPane={'title':'','class_name':'WeUIDialog','control_type':'Pane'}#通用的确认框
        self.ChangeShortcutPane={'title':'','control_type':'Pane','class_name':'SetAcceleratorWnd'}#修改快捷键时弹出的框
        self.MomentsPane={'title':'朋友圈','control_type':'Pane','class_name':'sg_ichat_main_wnd'}#好友朋友圈窗口

class Menus():
    def __init__(self):
        self.RightClickMenu={'title':'','control_type':'Menu','class_name':'CMenuWnd','framework_id':'Win32'}#微信界面内右键后弹出的菜单


class MenuItems():
    def __init__(self):
        self.ForwardMenuItem={'title':'转发...','control_type':'MenuItem'}#右键后的转发消息MenuItem
        self.SetPrivacyMenuItem={'title':'设置朋友权限','control_type':'MenuItem'}#好友设置菜单栏里的设置朋友权限
        self.StarMenuItem={'title':'设为星标朋友','control_type':'MenuItem'}#好友设置菜单栏里的设为星标朋友
        self.BlockMenuItem={'title':'加入黑名单','control_type':'MenuItem'}#好友设置菜单栏里的加入黑名单
        self.EditContactMenuItem={'title':'设置备注和标签','control_type':'MenuItem'}#好友设置菜单栏里的设置备注和标签
        self.ShareContactMenuItem={'title_re':'推荐给朋友','control_type':'MenuItem'}#好友设置菜单栏里的推荐给朋友，这里使用title_re因为实际上中文版中微信是会根据性别来决定这个控件名称
        self.DeleteMenuItem={'title':'删除联系人','control_type':'MenuItem'}#好友设置菜单栏里的删除好友
        self.UnBlockMenuItem={'title':'移出黑名单','control_type':'MenuItem'}#好友设置菜单栏里的移出黑名单
        self.UnStarMenuItem={'title':'不再设为星标朋友','control_type':'MenuItem'}#好友设置菜单栏里的不再设为星标朋友
        self.Tickle={'title':'拍一拍','control_type':'MenuItem'}#拍一拍好友
        self.CopyMenuItem={'title':'复制','control_type':'MenuItem'}#右键菜单里的复制消息
        self.SaveMenuItem={'title':'另存为','control_type':'MenuItem'}#右键图片视频或文件时菜单里的另存为
        self.ForwardMenuItem={'title':'转发...','control_type':'MenuItem'}#右键后的转发消息
        self.AddToFavoritesMenuItem={'title':'收藏','control_type':'MenuItem'}#添加到收藏夹
        self.TranslateMenuItem={'title':'翻译','control_type':'MenuItem'}#右键文本消息后的翻译选项
        self.EditMenuItem={'title':'编辑','control_type':'MenuItem'}#右键图片后的编辑选项
        self.DeleteMenuItem={'title':'删除','control_type':'MenuItem'}#右键消息后的删除选项
        self.SearchMenuItem={'title':'搜一搜','control_type':'MenuItem'}#右键消息后的搜索选项
        self.QuoteMeunItem={'title':'引用','control_type':'MenuItem'}#右键消息后的引用选项
        self.SelectMenuItem={'title':'多选','control_type':'MenuItem'}#右键消息后的多选选项
        self.EnlargeMeunItem={'title':'放大阅读','control_type':'MenuItem'}#右键消息后的放大选项
        self.FindInChatMenuItem={'title':'定位到聊天位置','control_type':'MenuItem'}#聊天记录页面内右键消息后的Find in chat选项
        self.OpenWithDefaultBrowser={'title':'使用默认浏览器打开','control_type':'MenuItem'}#聊天记录页面内Link类型的消息后的使用默认浏览器打开

class CheckBoxes():
    def __init__(self):
        self.ChatsOnlyCheckBox={'title':'仅聊天','control_type':'CheckBox'}#修改好友权限时的仅聊天选项
        self.OpenChatCheckBox={'title':'聊天、朋友圈、微信运动等','control_type':'CheckBox'}#修改好友权限时的聊天、朋友圈、微信运动等选项
        self.OnScreenNamesCheckBox={'title':'显示群成员昵称','control_type':'CheckBox'}#显示群成员昵称
        self.MuteNotificationsCheckBox={'title':'消息免打扰','control_type':'CheckBox'}#消息免打扰
        self.StickyonTopCheckBox={'title':'置顶聊天','control_type':'CheckBox'}#置顶聊天
        self.SavetoContactsCheckBox={'title':'保存到通讯录','control_type':'CheckBox'}#保存至通讯录

class Customs():
    def __init__(self):
        self.ContactCustom={'control_type':'Custom','auto_id':'main_window_sub_splitter_view','class_name':'mmui::XSplitterView'}#微信切换到通讯录界面后的右侧好友信息面板的上一级自定义

class Windows():
    def __init__(self):
        self.EditPrivacyWindow={'title':'朋友权限','class_name':'WeUIDialog','framework_id':'Win32'}#设置好友权限窗口
        self.EditContactWindow={'title':'设置备注和标签','class_name':'WeUIDialog','framework_id':'Win32'}#设置好友备注和标签的窗口
        self.SettingsMenu={'class_name':'SetMenuWnd','control_type':'Window'}#设置与其他按钮按下后的菜单栏
        self.DeleteMemberWindow={'title':'DeleteMemberWnd','control_type':'Window','framework_id':'Win32'}#群聊踢人面板
        self.AddMemberWindow={'title':'AddMemberWnd','control_type':'Window','framework_id':'Win32'}#群聊拉人面板
        self.SelectContactWindow={'title':'','control_type':'Window','class_name':'SelectContactWnd','framework_id':'Win32'}#转发消息时或推荐名片时的选择好友面板
        self.PopUpProfileWindow={'title':'Weixin','control_type':'Window','class_name':'mmui::ProfileUniquePop'}#好友设置界面点击头像后弹出的个人简介窗口
        self.MomentsWindow={'title':'朋友圈','control_type':'Window','class_name':"mmui::SNSWindow"}#好友朋友圈窗口

class Login_window():
    '''登录界面要用到的唯二的两个Ui:登录界面与进入微信按钮'''
    def __init__(self):
        self.LoginWindow={'title':'微信','class_name':'mmui::LoginWindow'}#登录微信界面
        self.LoginButton={'control_type':'Button','title':'进入微信'}#进入微信按钮

class SideBar():
    '''主界面侧边栏下的所有Ui'''
    def __init__(self):
        self.Chats={'title':'微信','control_type':'Button','class_name':"mmui::XTabBarItem"}#主界面左侧的聊天按钮
        self.Contacts={'title':'通讯录','control_type':'Button'}#主界面左侧的通讯录按钮
        self.Collections={'title':'收藏','control_type':'Button','class_name':"mmui::XTabBarItem"}#主界面左侧的收藏按钮
        self.Moments={'title':'朋友圈','control_type':'Button','class_name':"mmui::XTabBarItem"}#主界面左侧的朋友圈按钮
        self.Search={'title':'搜一搜','control_type':'Button','class_name':"mmui::XTabBarItem"}#主界面左侧的搜一搜按钮
        self.Channels={'title':'视频号','control_type':'Button','class_name':"mmui::XTabBarItem"}#主界面左侧的视频号按钮
        self.MiniProgram={'title':'小程序面板','control_type':'Button','class_name':"mmui::XTabBarItem"}#主界面左侧的小程序面板按钮
        self.Discovery={'title':'发现','control_type':'Button'}#主界面左侧的发现按钮
        self.More={'title':'更多','control_type':'Button','found_index':0} #主界面左侧的更多按钮 

    
class Main_window():
    '''主界面下所有的第一级Ui'''
    def __init__(self):
        self.MainWindow={'title':'微信','class_name':'mmui::MainWindow','framework_id':'Qt'}#微信主界面
        self.MySelfButton={'control_type':'Button','found_index':0}#主界面下的第一个按钮,也就是我自己的头像按钮，必须通过main_window.child_window(**Main_window().MySelfButton)使用!
        self.AddTalkMemberWindow={'title':'微信选择成员','control_type':'Window','class_name':"mmui::SessionPickerWindow",'framework_id':'Qt'}#添加新朋友时弹出的窗口
        self.MainWindow={'title':'微信','class_name':'mmui::MainWindow'}#微信主界面
        self.Toolbar={'title':'导航','control_type':'ToolBar'}#主界面左侧的侧边栏
        self.ConversationList={'title':'会话','control_type':'List','framework_id':'Qt'}#主界面左侧会话列表
        self.Search={'title':'搜索','control_type':'Edit','class_name':"mmui::XValidatorTextEdit"}#主界面顶部的搜索栏
        self.SearchResult={'title':"",'control_type':'List','auto_id':'search_list'}#主界面顶部搜索栏搜索内容的结果列表
        self.ChatToolBar={'title':'','found_index':0,'control_type':'ToolBar'}#主界面右侧聊天窗口内的工具栏(语音视频按钮在其中)
        self.CurrentChatWindow={'control_type':'Edit','title':'Edit'}#主界面右侧的聊天窗口
        self.ProfileWindow={'class_name':"ContactProfileWnd",'control_type':'Pane','framework_id':'Win32'}#从聊天区域打开的好友信息面板
        self.FriendMenu={'control_type':'Menu','title':'','class_name':'CMenuWnd','framework_id':'Win32'}#从聊天区域打开的好友信息面板内右上角三个点点击后的菜单栏
        self.FriendSettingsWindow={'class_name':'SessionChatRoomDetailWnd','control_type':'Pane','framework_id':'Win32'}#好友设置界面
        self.GroupSettingsWindow={'title':'SessionChatRoomDetailWnd','control_type':'Pane','framework_id':'Win32'}#群聊设置界面    
        self.SettingsMenu={'class_name':'SetMenuWnd','control_type':'Window'}#设置与其他按钮按下后的菜单栏
        self.ContactsList={'control_type':'List','class_name':"mmui::StickyHeaderRecyclerListView"}#主界面切换至联系人后的通讯录列表
        self.SearchNewFriendBar={'title':'微信号/手机号','control_type':'Edit'}#添加好友时顶部搜索栏名称
        self.SearchNewFriendResult={'title_re':'@str:IDS_FAV_SEARCH_RESULT','control_type':'List'}#添加新朋友时的搜索结果
        self.AddFriendRequestWindow={'title':'添加朋友请求','class_name':'WeUIDialog','control_type':'Window','framework_id':'Win32'}#添加朋友请求窗口
        self.AddMemberWindow={'title':'AddMemberWnd','control_type':'Window','framework_id':'Win32'}#群聊拉人面板
        self.DeleteMemberWindow={'title':'DeleteMemberWnd','control_type':'Window','framework_id':'Win32'}#群聊踢人面板
        self.Tickle={'title':'拍一拍','control_type':'MenuItem'}#拍一拍好友
        self.SelectContactWindow={'title':'','control_type':'Window','class_name':'SelectContactWnd','framework_id':'Win32'}#转发消息时或推荐名片时的选择好友面板
        self.SetTag={'title':'设置标签','framework_id':'Win32','class_name':'StandardConfirmDialog'}#设置好友标签窗口
        self.FriendChatList={'title':'消息','control_type':'List'}#主界面右侧聊天区域内与好友的消息列表
        self.SearchContactsResult={'title_re':'搜索','control_type':'Text'}#推荐好友面板内搜索结果
        self.EditArea={'control_type':'Edit','class_name':"mmui::ChatInputField"}#好友主界面的聊天区域

class Independent_window():
    '''独立于微信主界面,将微信主界面关闭后仍能在桌面显示的窗口Ui'''
    def __init__(self):
        self.Desktop={'backend':'uia'}#windows桌面
        self.AddFriendWindow={'title':'添加朋友','class_name':"mmui::AddFriendWindow",'control_type':'Window'}#添加朋友窗口
        self.SettingWindow={'title':'设置','class_name':"mmui::PreferenceWindow",'control_type':'Window','auto_id':"PreferenceWindow"}#微信设置窗口
        self.ContactManagerWindow={'title':'通讯录管理','class_name':"mmui::ContactsManagerWindow"}#通讯录管理窗口
        self.MomentsWindow={'title':'朋友圈','control_type':"Window",'class_name':"mmui::SNSWindow",'framework_id':'Qt'}#朋友圈窗口
        self.ChatFilesWindow={'title':'聊天文件','control_type':'Window','class_name':"mmui::FileManagerWindow"}#聊天文件窗口
        self.MiniProgramWindow={'title':'微信','control_type':'Pane','class_name':'Chrome_WidgetWin_0'}#小程序面板窗口
        self.SearchWindow={'title':'微信','class_name':'Chrome_WidgetWin_0','control_type':'Pane'}#搜一搜窗口
        self.ChannelsWindow={'title':'微信','class_name':'Chrome_WidgetWin_0','control_type':'Pane'}#视频号窗口
        self.ContactProfileWindow={'title':'微信','class_name':'ContactProfileWnd','framework_id':'Win32','control_type':'Pane'}#添加新好友时的添加到通讯录窗口
        self.ChatHistoryWindow={'control_type':'Window','class_name':'mmui::SearchMsgUniqueChatWindow','framework_id':'Qt'}#聊天记录窗口
        self.GroupAnnouncementWindow={'title':'群公告','framework_id':'Win32','class_name':'ChatRoomAnnouncementWnd'}#群公告窗口
        self.NoteWindow={'title':'笔记','class_name':'FavNoteWnd','framework_id':"Win32"}#笔记窗口
        self.OldIncomingCallWindow={'class_name':'VoipTrayWnd','title':'微信'}#旧版本来电(视频或语音)窗口
        self.NewIncomingCallWindow={'class_name':'ILinkVoipTrayWnd','title':'微信'}#旧版本来电(视频或语音)窗口
        self.OldVoiceCallWindow={'title':'微信','class_name':'AudioWnd'}#旧版本接通语音电话后通话窗口
        self.NewVoiceCallWindow={'title':'微信','class_name':'ILinkAudioWnd'}#新版本接通语音电话后通话窗口
        self.OldVideoCallWindow={'title':'微信','class_name':'VoipWnd'}#新版本接通语音电话后通话窗口
        self.NewVideoCallWindow={'title':'微信','class_name':'ILinkVoipWnd'}#新版本接通视频电话后通话窗口
        self.OfficialAccountWindow={'title':'公众号','control_type':'Window','class_name':'H5SubscriptionProfileWnd'}#公众号窗口

class Groups():
    def __init__(self):

        self.ContactProfileGroup={'class_name':'mmui::XView','auto_id':"contact_profile_view",'control_type':'Group'}#通讯录的好友详细信息所处面板


