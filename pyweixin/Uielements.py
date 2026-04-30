'''
Uielements
---------
PC微信中的各种Ui-Object,使用于多语言,包括:
    - `Buttons`:Button类型Ui
    - `CheckBoxes`:复选框类型Ui
    - `Customs`:自定义类型Ui
    - `Edits`:编辑框类型Ui 
    - `Groups`:组类型Ui
    - `Independent_Window`:独立于微信界面需使用desktop.window定位的窗口
    - `Lists`:List类型Ui
    - `ListItems`:ListItem类型Ui
    - `Login_Window`:登录界面内内可直接.child_window定位的一级Ui
    - `Main_Window`:主界面窗口内可直接.child_window定位的一级Ui
    - `MenuItems`:MenuItem类型UI
    - `Menus`:Menu类型UI
    - `Texts`: 文本类型Ui
    - `TabItems`:TabItem类型Ui
    - `SideBar`:主界面导航栏内的所有Button
    - `Windows`:Window类型Ui
   
       
Examples
--------
使用时只需要:
    
    >>> from pyweixin.Uielements import Edits
    #返回值为kwargs字典,可以直接使用**解包传入到descendants,children,window,child_window内
    >>> searchbar=main_window.child_window(**Edits.SearchEdit)
    #或者,导入xx_control自行输入版本与语言然后使用
    >>> from pyweixin.Uielements import Button_Control
    >>> Buttons=Button_Control(Version='4.1.9.30',language='简体中文')
    >>> GlobalConfig.language='English'
    >>> print(Buttons.SendMessageButton)
    
'''
from.Config import GlobalConfig
language=GlobalConfig.language
Version=GlobalConfig.Version
class Button_Control():
    '''
    微信主界面内所有类型为Button的UI控件
    '''
    def __init__(self,language=language,Version=Version):
        self.language=language
        self.Version=Version
        self.WeixinButton={'control_type':'Button','found_index':0}#主界面下的第一个按钮,侧边栏的微信按钮
        self.SubScribeButton={'title':'关注','control_type':'Button'}#公众号窗口内的关注按钮
        self.HomePageButton={'title':'公众号主页','control_type':'Button'}#公众号主页内右上角的公众号主页按钮
        if self.language=='简体中文':
            self.AccountSettingsButton={'title':'账号设置','control_type':'Button'}#微信设置界面里左侧的账号设置
            self.SendAudioButon={'title_re':'发语音','control_type':'Button'}#微信底部发送语音按钮
            self.AddButton={'title':'添加','control_type':'Button'}#通讯录管理点击新建标签后右侧的添加按钮
            self.AddRemarkButton={'control_type':'Button','title':'添加备注名'}#通讯录好友详情面板没有备注时的添加备注名按钮
            self.AddPhoneNumButon={'control_type':'Button','title':'添加电话'}#修改好友备注内的添加电话按钮
            self.ClearPhoneNumButton={'control_type':'Button','title':'删除电话'}#修改好友备注内的删除电话按钮
            self.QuickActionsButton={'control_type':'Button','title':'快捷操作'}#主界面+号按钮
            self.OffLineButton={'title':'当前网络不可用','control_type':'Button'}#网络不好时,微信顶部的按钮
            self.SendButton={'control_type':'Button','title':'发送(S)'}#发送按钮
            self.EmptyButton={'control_type':'Button','title':'清空'}#清空按钮
            self.ChatInfoButton={'control_type':'Button','title':'聊天信息'}#群聊/好友聊天主界面右上角的三个点
            self.GeneralButton={'control_type':'Button','title':'通用'}#设置界面内的通用按钮
            self.CheckMoreMessagesButton={'title':'查看更多消息','control_type':'Button','found_index':1}#好友聊天界面内的查看更多消息按钮
            self.OfficialAcountButton={'title':'公众号','control_type':'Button'}#搜一搜内公众号按钮                                                                                                                                
            self.SettingsAndOthersButton={'title':'设置','control_type':'Button'}#设置按钮
            self.ConfirmQuitGroupButton={'title':'退出','control_type':'Button'}#确认退出群聊按钮
            self.CerateNewNoteButton={'title':'新建笔记','control_type':'Button'}#创建一个新笔记按钮
            self.CerateGroupChatButton={'title':"发起群聊",'control_type':"Button"}#创建新群聊按钮
            self.AddNewFriendButon={'title':'添加朋友','control_type':'Button'}#添加新朋友按钮
            self.AddToContactsButton={'control_type':'Button','title':'添加到通讯录'}#添加新朋友时的添加至通讯录内按钮
            self.AnswerButton={'control_type':'Button','title':'接听'}#接听电话按钮    
            self.DeclineButton={'control_type':'Button','title':'拒绝'}#挂断电话按钮             
            self.ConfirmButton={'control_type':'Button','title':'确定'}#确定操作按钮
            self.CancelButton={'control_type':'Button','title':'取消'}#取消操作按钮
            self.DeleteButton={'control_type':'Button','title':'删除'}#删除好友按钮
            self.SendButton={'control_type':'Button','title':'发送'}#转发文件或消息按钮
            self.SendRespectivelyButton={'control_type':'Button','title_re':'分别发送'}#转发消息时分别发送按钮
            self.SettingsButton={'control_type':'Button','title':'设置','found_index':0}#工具栏打开微信设置menu内的选项按钮
            self.ChatFilesButton={'control_type':'Button','title':'聊天文件','found_index':0}#工具栏打开微信设置menu内的选项按钮
            self.ClearChatHistoryButton={'control_type':'Button','title':'清空聊天记录'}#清空好友或群聊聊天记录时的按钮
            self.VoiceCallButton={'control_type':'Button','title':'语音聊天'}#给好友拨打语音电话按钮
            self.VideoCallButton={'control_type':'Button','title':'视频聊天'}#给好友拨打视频电话按钮
            self.CompleteButton={'title':'完成','control_type':'Button'}#完成按钮
            self.PinButton={'control_type':'Button','title':'置顶'}#微信窗口置顶按钮(右上角最小化按钮旁边)
            self.CancelPinButton={'control_type':'Button','title':'取消置顶'}#微信取消窗口置顶按钮(右上角最小化按钮旁边)
            self.ChatHistoryButton={'control_type':'Button','title':'聊天记录'}#获取聊天记录按钮
            self.ChangeGroupNameButton={'control_type':'Button','title':'群聊名称'}#修改群聊名称按钮
            self.ContactsManageButton={'title':'通讯录管理','control_type':'Button'}#通讯录管理按钮
            self.ConfirmEmptyChatHistoryButon={'title':'清空','control_type':'Button'}#点击清空聊天记录后弹出的query界面内的清空按钮
            self.MoreButton={'title':'更多','control_type':'Button'}#打开微信好友设置界面更多按钮
            self.LogOutButton={'title':'退出登录','control_type':'Button'}#设置界面里退出登录按钮
            self.RefreshButton={'title':'刷新','control_type':'Button'}#朋友圈的刷新按钮
            self.RectentGroupButton={'title':'最近群聊','control_type':'Button'}#通讯录设置界面里的最近群聊按钮
            self.PostButton={'title':'发表','control_type':'Button'}#微信朋友圈界面里的发表按钮
            self.BackButton={'title':'返回','control_type':'Button'}#微信朋友圈内的返回按钮
            self.SolitaireButton={'title':'发起接龙','control_type':'Button'}#接龙窗口内的发起接龙按钮
            self.CommonGroupButton={'title_re':r'\d+个','control_type':'Button'}#共同群聊后边的名称为\d+个的按钮
            self.NotificationButton={'title':'通知','control_type':'Button'}#微信设置里的通知按钮
            self.RotateButton={'title':'旋转','control_type':'Button'}#图片预览窗口内的旋转按钮
            self.JoinGroupButton={'title':'加入群聊','control_type':'Button'}#群聊邀请界面内的加入群聊按钮(点击群聊邀请链接后出现的窗口)
            self.LikeButton={'title':'赞','control_type':'Button'}#点击朋友圈单个内容下方的灰色省略号后弹出的点赞按钮
            self.CommentButton={'title':'评论','control_type':'Button'}#点击朋友圈单个内容下方的灰色省略号后弹出的评论按钮
            self.SendMessageButton={'title':'发消息','control_type':'Button'}#添加好友窗口里的发消息按钮
            self.VerifyNowButton={'title':'前往验证','control_type':'Button'}#通讯录新朋友界面中前往验证按钮
            self.MomentsButton={'title':'朋友圈','control_type':'Button','auto_id':'button'}#好友个人简介界面内的朋友圈按钮(不是主页左侧的)
        if self.language=='English':
            self.AccountSettingsButton={'title':'My Account','control_type':'Button'}#微信设置界面里左侧的账号设置
            self.SendAudioButon={'title_re':'Send Voice','control_type':'Button'}#微信底部发送语音按钮
            self.AddButton={'title':'Add','control_type':'Button'}#通讯录管理点击新建标签后右侧的添加按钮
            self.AddRemarkButton={'control_type':'Button','title':'添加备注名'}#通讯录好友详情面板没有备注时的添加备注名按钮
            self.AddPhoneNumButon={'control_type':'Button','title':'Add Mobile'}#修改好友备注内的添加电话按钮
            self.ClearPhoneNumButton={'control_type':'Button','title':'DeleteMobile'}#修改好友备注内的删除电话按钮
            self.QuickActionsButton={'control_type':'Button','title':'Shortcuts'}#主界面+号按钮
            self.OffLineButton={'title':'Network unavailable','control_type':'Button'}#网络不好时,微信顶部的按钮
            self.SendButton={'control_type':'Button','title':'send'}#发送按钮
            self.EmptyButton={'control_type':'Button','title':'Clear'}#清空按钮,清空聊天记录和聊天文件窗口搜索栏右侧x按钮
            self.ChatInfoButton={'control_type':'Button','title':'Chat Info'}#群聊/好友聊天主界面右上角的三个点
            self.GeneralButton={'control_type':'Button','title':'General'}#设置界面内的通用按钮
            self.CheckMoreMessagesButton={'title':'View more messages','control_type':'Button','found_index':1}#好友聊天界面内的查看更多消息按钮
            self.OfficialAcountButton={'title':'Official Accounts','control_type':'Button'}#搜一搜内公众号按钮                                                                                                                                
            self.CerateNewNoteButton={'title':'New Note','control_type':'Button'}#创建一个新笔记按钮
            self.CerateGroupChatButton={'title':"Start Group Chat",'control_type':"Button"}#创建新群聊按钮
            self.AddNewFriendButon={'title':'Add Contacts','control_type':'Button'}#添加新朋友按钮
            self.AddToContactsButton={'control_type':'Button','title':'Add to Contacts'}#添加新朋友时的添加至通讯录内按钮
            self.AnswerButton={'control_type':'Button','title':'Answer'}#接听电话按钮   
            self.AnswerButton={'control_type':'Button','title':'Decline'}#挂断电话按钮             
            self.ConfirmButton={'control_type':'Button','title':'OK'}#确定操作按钮
            self.CancelButton={'control_type':'Button','title':'Cancel'}#取消操作按钮
            self.DeleteButton={'control_type':'Button','title':'Delete'}#删除好友按钮
            self.SendButton={'control_type':'Button','title':'Send'}#转发文件或消息按钮
            self.SendRespectivelyButton={'control_type':'Button','title_re':'Send To'}#转发消息时分别发送按钮
            self.SettingsButton={'control_type':'Button','title':'Settings','found_index':0}#工具栏打开微信设置menu内的选项按钮
            self.ChatFilesButton={'control_type':'Button','title':'Chat Files','found_index':0}#工具栏打开微信设置menu内的选项按钮
            self.ClearChatHistoryButton={'control_type':'Button','title':'Clear Chat History'}#清空好友或群聊聊天记录时的按钮
            self.VoiceCallButton={'control_type':'Button','title':'Voice Call'}#给好友拨打语音电话按钮
            self.VideoCallButton={'control_type':'Button','title':'Video Call'}#给好友拨打视频电话按钮
            self.FinishButton={'title':'Finish','control_type':'Button'}#完成按钮
            self.PinButton={'control_type':'Button','title':'Sticky'}#微信窗口置顶按钮(右上角最小化按钮旁边)
            self.CancelPinButton={'control_type':'Button','title':'Remove Sticky'}#微信取消窗口置顶按钮(右上角最小化按钮旁边)
            self.ChatHistoryButton={'control_type':'Button','title':'Chat History'}#顶部聊天记录按钮
            self.ChangeGroupNameButton={'control_type':'Button','title':'Group Name'}#修改群聊名称按钮
            self.ContactsManageButton={'title':'Manage Contacts','control_type':'Button'}#通讯录管理按钮
            self.ConfirmEmptyChatHistoryButon={'title':'Clear','control_type':'Button'}#点击清空聊天记录后弹出的query界面内的清空按钮
            self.MoreButton={'title':'More','control_type':'Button'}#打开微信好友设置界面更多按钮
            self.LogOutButton={'title':'Log Out','control_type':'Button'}#设置界面里退出登录按钮
            self.RefreshButton={'title':'Refresh','control_type':'Button'}#朋友圈的刷新按钮
            self.RectentGroupButton={'title':'Recent Group Chats','control_type':'Button'}#通讯录设置界面里的最近群聊按钮
            self.PostButton={'title':'Post','control_type':'Button'}#微信朋友圈界面里的发表按钮
            self.BackButton={'title':'Back','control_type':'Button'}#微信朋友圈内的返回按钮
            self.SolitaireButton={'title':'Create Group Note','control_type':'Button'}#接龙窗口内的发起接龙按钮
            self.CommonGroupButton={'title_re':r'\d+个','control_type':'Button'}#共同群聊后边的名称为\d+个的按钮
            self.HomePageButton={'title':'Official Account homepage','control_type':'Button'}#公众号主页内右上角的公众号主页按钮
            self.NotificationButton={'title':'Notifications','control_type':'Button'}#微信设置里的通知按钮
            self.RotateButton={'title':'Rotate','control_type':'Button'}#图片预览窗口内的旋转按钮
            self.JoinGroupButton={'title':'Join Group','control_type':'Button'}#群聊邀请界面内的加入群聊按钮(点击群聊邀请链接后出现的窗口)
            self.LikeButton={'title':'Like','control_type':'Button'}#点击朋友圈单个内容下方的灰色省略号后弹出的点赞按钮
            self.CommentButton={'title':'Comment','control_type':'Button'}#点击朋友圈单个内容下方的灰色省略号后弹出的评论按钮
            self.SendMessageButton={'title':'Messages','control_type':'Button'}#搜索号码窗口里的发消息按钮
            self.VerifyNowButton={'title':'Verify Now','control_type':'Button'}#通讯录新朋友界面中前往验证按钮
            self.SolitaireButton={'title':'Create Group Note','control_type':'Button'}#接龙窗口内的发起接龙按钮
            self.MomentsButton={'title':'Moments','control_type':'Button','auto_id':'button'}#好友个人简介界面内的朋友圈按钮(不是主页左侧的)
        if self.language=='繁體中文':
            self.AccountSettingsButton={'title':'賬號與儲存','control_type':'Button'}#微信设置界面里左侧的账号设置
            self.SendAudioButon={'title_re':'傳送語音','control_type':'Button'}#微信底部发送语音按钮
            self.AddRemarkButton={'control_type':'Button','title':'新增備註名'}#通讯录好友详情面板没有备注时的添加备注名按钮
            self.AddPhoneNumButon={'control_type':'Button','title':'新增電話號碼'}#修改好友备注内的添加电话按钮
            self.ClearPhoneNumButton={'control_type':'Button','title':'刪除电话'}#修改好友备注内的删除电话按钮
            self.QuickActionsButton={'control_type':'Button','title':'快捷操作'}#主界面+号按钮
            self.OffLineButton={'title':'目前網路不可用','control_type':'Button'}#网络不好时,微信顶部的按钮
            self.SendButton={'control_type':'Button','title':'傳送'}#发送按钮
            self.EmptyButton={'control_type':'Button','title':'刪除'}#清空按钮
            self.ChatInfoButton={'control_type':'Button','title':'聊天資訊'}#群聊/好友聊天主界面右上角的三个点
            self.GeneralButton={'control_type':'Button','title':'一般'}#设置界面内的通用按钮
            self.CheckMoreMessagesButton={'title':'查看更多訊息','control_type':'Button','found_index':1}#好友聊天界面内的查看更多消息按钮
            self.OfficialAcountButton={'title':'官方賬號','control_type':'Button'}#搜一搜内公众号按钮                                                                                                                                
            self.ConfirmQuitGroupButton={'title':'確定','control_type':'Button'}#确认退出群聊按钮
            self.CerateNewNoteButton={'title':'新進筆記','control_type':'Button'}#创建一个新笔记按钮
            self.CerateGroupChatButton={'title':"建立群組",'control_type':"Button"}#创建新群聊按钮
            self.AddNewFriendButon={'title':'新增朋友','control_type':'Button'}#添加新朋友按钮
            self.AddToContactsButton={'control_type':'Button','title':'新增到通訊錄'}#添加新朋友时的添加至通讯录内按钮
            self.AnswerButton={'control_type':'Button','title':'接聽'}#接听电话按钮                  
            self.CloseAutoLoginButton={'control_type':'Button','title':'关闭自动登录'}#微信设置关闭自动登录按钮
            self.ConfirmButton={'control_type':'Button','title':'確定'}#确定操作按钮
            self.CancelButton={'control_type':'Button','title':'取消'}#取消操作按钮
            self.DeleteButton={'control_type':'Button','title':'刪除'}#删除好友按钮
            self.SendButton={'control_type':'Button','title':'傳送'}#转发文件或消息按钮
            self.SendRespectivelyButton={'control_type':'Button','title_re':'分別傳送'}#转发消息时分别发送按钮
            self.SettingsButton={'control_type':'Button','title':'設定','found_index':0}#工具栏打开微信设置menu内的选项按钮
            self.ChatFilesButton={'control_type':'Button','title':'微信檔案','found_index':0}#工具栏打开微信设置menu内的选项按钮
            self.ClearChatHistoryButton={'control_type':'Button','title':'刪除聊天記錄'}#清空好友或群聊聊天记录时的按钮
            self.VoiceCallButton={'control_type':'Button','title':'語音通話'}#给好友拨打语音电话按钮
            self.VideoCallButton={'control_type':'Button','title':'視訊通話'}#给好友拨打视频电话按钮
            self.FinishButton={'title':'完成','control_type':'Button'}#完成按钮
            self.PinButton={'control_type':'Button','title':'置頂'}#将窗口置顶按钮
            self.CancelPinButton={'control_type':'Button','title':'取消置頂'}#取消好友置顶按钮
            self.ChatHistoryButton={'control_type':'Button','title':'聊天記錄'}#获取聊天记录按钮
            self.ChangeGroupNameButton={'control_type':'Button','title':'群組名稱'}#修改群聊名称按钮
            self.ContactsManageButton={'title':'通訊錄管理','control_type':'Button'}#通讯录管理按钮
            self.ConfirmEmptyChatHistoryButon={'title':'刪除','control_type':'Button'}#点击清空聊天记录后弹出的query界面内的清空按钮
            self.MoreButton={'title':'更多','control_type':'Button'}#打开微信好友设置界面更多按钮
            self.LogOutButton={'title':'登出','control_type':'Button'}#设置界面里退出登录按钮
            self.RefreshButton={'title':'重新整理','control_type':'Button'}#朋友圈的刷新按钮
            self.RectentGroupButton={'title':'最近群組','control_type':'Button'}#通讯录设置界面里的最近群聊按钮
            self.PostButton={'title':'發佈','control_type':'Button'}#微信朋友圈界面里的发表按钮
            self.BackButton={'title':'返回','control_type':'Button'}#微信朋友圈内的返回按钮
            self.SolitaireButton={'title':'編輯接龍表格','control_type':'Button'}#接龙窗口内的发起接龙按钮
            self.CommonGroupButton={'title_re':r'\d+個','control_type':'Button'}#共同群聊后边的名称为\d+个的按钮
            self.NotificationButton={'title':'通知','control_type':'Button'}#微信设置里的通知按钮
            self.AddButton={'title':'新增','control_type':'Button'}#通讯录管理点击新建标签后右侧的添加按钮
            self.SendMessageButton={'title':'傳訊息','control_type':'Button'}#添加好友窗口里的发消息按钮
            self.RotateButton={'title':'旋轉','control_type':'Button'}#图片预览窗口内的旋转按钮
            self.LikeButton={'title':'按讚','control_type':'Button'}#点击朋友圈单个内容下方的灰色省略号后弹出的点赞按钮
            self.CommentButton={'title':'評論','control_type':'Button'}#点击朋友圈单个内容下方的灰色省略号后弹出的评论按钮
            self.JoinGroupButton={'title':'加入群組','control_type':'Button'}#群聊邀请界面内的加入群聊按钮(点击群聊邀请链接后出现的窗口)
            self.VerifyNowButton={'title':'前往驗證','control_type':'Button'}#通讯录新朋友界面中前往验证按钮
            self.SolitaireButton={'title':'發起接龍','control_type':'Button'}#接龙窗口内的发起接龙按钮
            self.MomentsButton={'title':'朋友圈','control_type':'Button','auto_id':'button'}#好友个人简介界面内的朋友圈按钮(不是主页左侧的)
        if '4.1.9' in self.Version:
            self.MomentsButton={'control_type':'Button','auto_id':
            "content_v_view.ProfileResizeVBoxView.detail_scroll_view.gradient_mask_stacked_view.default_scroll_area.qt_scrollarea_viewport.detail_content_host.detail_center_v_view.detail_derived_content_view.sns_container_view.wx_friend_sns.value_sns_view"}     
        if self.Version=='4.1.9.23':
            self.SendAudioButon={'title_re':'发语音','control_type':'Button'}#微信底部发送语音按钮
       
class CheckBox_Control():
    def __init__(self,language=language,Version=Version):
        self.language=language
        self.Version=Version
        if self.language=='简体中文':
            self.DontShowOthersCheckBox={'control_type':'CheckBox','title':'不让他（她）看'}#不让他看
            self.DontSeeOthersCheckBox={'control_type':'CheckBox','title':'不看他（她）'}#不看他
            self.OnScreenNamesCheckBox={'title':'显示群成员昵称','control_type':'CheckBox'}#显示群成员昵称
            self.MuteNotificationsCheckBox={'title':'消息免打扰','control_type':'CheckBox'}#消息免打扰
            self.PinChatCheckBox={'title':'置顶聊天','control_type':'CheckBox'}#置顶聊天
            self.FoldChatCheckBox={'title':'折叠聊天','control_type':'CheckBox'}#折叠聊天
            self.newMessageAlertCheckBox={'title':'新消息通知声音','control_type':'CheckBox'}#微信设置/通知界面内的新消息通知声音
            self.CallAlertCheckBox={'title':'语音和视频通话通知声音','control_type':'CheckBox'}#微信设置/通知界面内的语音和视频通话通知声音
            self.MomentsCheckBox={'title':'通知标记朋友圈','control_type':'CheckBox'}#微信设置/通知界面内的通知标记朋友圈
            self.GameCheckBox={'title':'通知标记游戏','control_type':'CheckBox'}#微信设置/通知界面内的通知标记游戏
            self.InteractionOnlyCheckBox={'title':'仅提醒朋友与我的互动','control_type':'CheckBox'}#微信设置/通知界面内的仅提醒朋友与我的互动
        if self.language=='English':
            self.DontShowOthersCheckBox={'control_type':'CheckBox','title':'Hide My Posts'}#不让他看
            self.DontSeeOthersCheckBox={'control_type':'CheckBox','title':'Hide Their Posts'}#不看他
            self.OnScreenNamesCheckBox={'title':'On-Screen Names','control_type':'CheckBox'}#显示群成员昵称
            self.MuteNotificationsCheckBox={'title':'Mure Notifications','control_type':'CheckBox'}#消息免打扰
            self.PinChatCheckBox={'title':'Sticky','control_type':'CheckBox'}#置顶聊天
            self.FoldChatCheckBox={'title':'Minimize Group','control_type':'CheckBox'}#折叠聊天
            self.newMessageAlertCheckBox={'title':'New Message Alert Sound','control_type':'CheckBox'}#微信设置/通知界面内的新消息通知声音
            self.CallAlertCheckBox={'title':'Voice and Video Calls Alert Sound','control_type':'CheckBox'}#微信设置/通知界面内的语音和视频通话通知声音
            self.MomentsCheckBox={'title':'Notification FlagMoments','control_type':'CheckBox'}#微信设置/通知界面内的通知标记朋友圈
            self.GameCheckBox={'title':'Notification FlagGame','control_type':'CheckBox'}#微信设置/通知界面内的通知标记游戏  
            self.InteractionOnlyCheckBox={'title':"Only notify friends' interactions with me",'control_type':'CheckBox'}#微信设置/通知界面内的仅提醒朋友与我的互动
        if self.language=='繁體中文':
            self.DontShowOthersCheckBox={'control_type':'CheckBox','title':'不让他（她）看'}#不让他看
            self.DontSeeOthersCheckBox={'control_type':'CheckBox','title':'不看他（她）'}#不看他
            self.OnScreenNamesCheckBox={'title':'顯示成員在群組的暱稱','control_type':'CheckBox'}#显示群成员昵称
            self.MuteNotificationsCheckBox={'title':'訊息免打擾','control_type':'CheckBox'}#消息免打扰
            self.PinChatCheckBox={'title':'置頂聊天','control_type':'CheckBox'}#置顶聊天
            self.FoldChatCheckBox={'title':'折疊此群組','control_type':'CheckBox'}#折叠聊天
            self.newMessageAlertCheckBox={'title':'新訊息通知聲音','control_type':'CheckBox'}#微信设置/通知界面内的新消息通知声音
            self.CallAlertCheckBox={'title':'語音和視訊通話通知聲音','control_type':'CheckBox'}#微信设置/通知界面内的语音和视频通话通知声音
            self.MomentsCheckBox={'title':'通知標記朋友圈','control_type':'CheckBox'}#微信设置/通知界面内的通知标记朋友圈
            self.GameCheckBox={'title':'通知標記游戏','control_type':'CheckBox'}#微信设置/通知界面内的通知标记游戏
            self.InteractionOnlyCheckBox={'title':'僅提醒朋友與我的互動','control_type':'CheckBox'}#微信设置/通知界面内的仅提醒朋友与我的互动

class Custom_Control():
    def __init__(self,language=language,Version=Version):
        self.language=language
        #版本
        self.Version=Version
        self.ContactCustom={'control_type':'Custom','auto_id':'MainView.main_window_main_splitter_view','class_name':'mmui::XSplitterView'}#微信切换到通讯录后通讯录整个界面
        self.ContactDetailCustom={'control_type':'Custom','class_name':'mmui::XSplitterView','found_index':1}#微信切换到通讯录界面后的右侧好友信息面板的上一级自定义
        if '4.1.9' in self.Version:
             self.ContactDetailCustom={'control_type':'Custom','class_name':'mmui::XSplitterView','auto_id':'MainView.main_window_corner_view.MainView.main_window_main_splitter_view'}#微信切换到通讯录界面后的右侧好友信息面板的上一级自定义


class Edit_Control():
    '''微信主界面内所有类型为Edit(不包含独立窗口)的UI控件'''
    def __init__(self,language=language,Version=Version):
        self.language=language
        self.Version=Version
        self.CurrentChatEdit={'control_type':'Edit','auto_id':'chat_input_field'}#微信主界面下当前的聊天窗口
        self.InputEdit={'control_type':'Edit','auto_id':'chat_input_field'}#好友独立聊天窗口内的文本编辑框
        self.SnsEdit={'title':'','control_type':'Edit','class_name':"mmui::XValidatorTextEdit"}#朋友圈发布界面内的文本编辑框
        self.NativeFileSaveEdit={'control_type':'Edit','framework_id':'Win32','top_level_only':False,'class_name':'Edit'}#windows本地选择文件夹窗口底部的编辑栏
        self.EditWnd={'control_type':'Edit','class_name':'EditWnd','framework_id':'Win32'}#通用的编辑框,主要出现在好友和群聊设置界面里
        if self.language=='简体中文':
            self.SearchEdit={'title':'搜索','control_type':'Edit','class_name':'mmui::XValidatorTextEdit'}#主界面顶部的搜索栏
            self.SearchNewFriendEdit={'title':'微信号/手机号','control_type':'Edit'}#添加新朋友界面里的搜
            self.RequestContentEdit={'title':'发送添加朋友申请','control_type':'Edit'}#添加好友时,发送请求时的内容
            self.SearchGroupMemeberEdit={'title':'搜索群成员','control_type':'Edit'}#添加或删除群成员时,在弹出的界面里顶部的搜索栏
            self.ChangeRemarkEdit={'control_type':'Edit','title':'修改备注'}#添加好友界面内的修改备注 
        if self.language=='English':
            self.SearchEdit={'title':'Search','control_type':'Edit','class_name':'mmui::XValidatorTextEdit'}#主界面顶部的搜索栏
            self.SearchNewFriendEdit={'title':'Search by ID/mobile','control_type':'Edit'}#添加新朋友界面里的搜
            self.RequestContentEdit={'title':'Send Friend Request','control_type':'Edit'}#添加好友时,发送请求时的内容
            self.SearchGroupMemeberEdit={'title':'Search','control_type':'Edit'}#添加或删除群成员时,在弹出的界面里顶部的搜索栏
            self.ChangeRemarkEdit={'control_type':'Edit','title':'ModifyRemark'}#添加好友界面内的修改备注
        if self.language=='繁體中文':
            self.SearchEdit={'title':'搜尋','control_type':'Edit','class_name':'mmui::XValidatorTextEdit'}#主界面顶部的搜索栏
            self.SearchNewFriendEdit={'title':'搜尋微信ID 或者手機號碼','control_type':'Edit'}#添加新朋友界面里的搜
            self.RequestContentEdit={'title':'傳送新增朋友邀請','control_type':'Edit'}#添加好友时,发送请求时的内容
            self.SearchGroupMemeberEdit={'title':'搜尋群組成員','control_type':'Edit'}#添加或删除群成员时,在弹出的界面里顶部的搜索栏
            self.ChangeRemarkEdit={'title':'修改備註','control_type':'Edit'}#添加好友界面内的修改备注 

class Group_Control():
    def __init__(self,language=language,Version=Version):
        self.language=language
        #版本
        self.Version=Version
        self.ContactProfileGroup={'class_name':'mmui::XView','auto_id':"profile_view",'control_type':'Group'}#通讯录的好友详细信息所处面板
        self.SnsPublishGroup={'auto_id':'SnsPublishPanel','control_type':'Group'}#微信朋友圈后发布按钮点击后的面板
        self.ContactProfileViewGroup={'title':'','control_type':'Group','class_name':'mmui::ContactProfileView'}#添加好友界面内搜索微信号后弹出的好友信息(带有添加到通讯录按钮)组
        if '4.1.9' in self.Version:
             self.ContactProfileViewGroup={'title':'','control_type':'Group','class_name':'mmui::ProfileView'}#添加好友界面内搜索微信号后弹出的好友信息(带有添加到通讯录按钮)组
        if self.language=='简体中文':
            self.AtGroup={'title':'提醒谁看','class_name':'mmui::PublishComponent','control_type':'Group'}#发布微信朋友圈内的提醒谁看
            self.WhoCanSeeGroup={'title':'谁可以看','class_name':'mmui::PublishComponent','control_type':'Group'}#发布微信朋友圈内的谁可以看
            self.ChatOnlyGroup={'title':'仅聊天','control_type':'Group'}#好友权限内的仅聊天选项
            self.OpenPrivacyGroup={'title':'聊天、朋友圈、微信运动等','control_type':'Group'}#好友权限内的聊天、朋友圈、微信运动等选项
        if self.language=='English':
            self.AtGroup={'title':'Mention','class_name':'mmui::PublishComponent','control_type':'Group'}#发布微信朋友圈内的提醒谁看
            self.WhoCanSeeGroup={'title':'Visible To ','class_name':'mmui::PublishComponent','control_type':'Group'}#发布微信朋友圈内的谁可以看
            self.ChatOnlyGroup={'title':'Chats Only','control_type':'Group'}#好友权限内的仅聊天选项
            self.OpenPrivacyGroup={'title':'Chats, Moments, WeRun, etc.','control_type':'Group'}#好友权限内的聊天、朋友圈、微信运动等选项
        if self.language=='繁體中文':
            self.AtGroup={'title':'提醒誰瀏覽','class_name':'mmui::PublishComponent','control_type':'Group'}#微信朋友圈内的提醒谁看
            self.WhoCanSeeGroup={'title':'可瀏覽的聯絡人','class_name':'mmui::PublishComponent','control_type':'Group'}#微信朋友圈内的谁可以看
            self.ChatOnlyGroup={'title':'僅聊天','control_type':'Group'}#好友权限内的仅聊天选项
            self.OpenPrivacyGroup={'title':'聊天、朋友圈、WeRun 等','control_type':'Group'}#好友权限内的聊天、朋友圈、微信运动等选项
        

class Independent_window_Control():
    '''独立于微信主界面,将微信主界面关闭后仍能在桌面显示的窗口Ui'''
    def __init__(self,language=language,Version=Version):
        self.language=language
        self.Version=Version
        self.ChatHistoryWindow={'control_type':'Window','class_name':'mmui::SearchMsgUniqueChatWindow','framework_id':'Qt'}#聊天记录窗口
        if self.language=='简体中文':
            self.AddFriendWindow={'title':'添加朋友','class_name':"mmui::AddFriendWindow",'control_type':'Window'}#添加朋友窗口
            self.SettingsWindow={'title':'设置','class_name':"mmui::PreferenceWindow",'control_type':'Window','auto_id':"PreferenceWindow"}#微信设置窗口
            self.ContactManagerWindow={'title':'通讯录管理','class_name':"mmui::ContactsManagerWindow"}#通讯录管理窗口
            self.MomentsWindow={'title':'朋友圈','control_type':"Window",'class_name':"mmui::SNSWindow",'framework_id':'Qt'}#朋友圈窗口
            self.ChatFilesWindow={'title':'聊天文件','control_type':'Window','class_name':"mmui::FileManagerWindow"}#聊天文件窗口
            self.MiniProgramWindow={'title':'微信','control_type':'Pane','class_name':'Chrome_WidgetWin_0'}#小程序面板窗口
            self.SearchWindow={'title':'微信','class_name':'Chrome_WidgetWin_0','control_type':'Pane'}#搜一搜窗口
            self.ChannelsWindow={'title':'微信','class_name':'Chrome_WidgetWin_0','control_type':'Pane'}#视频号窗口
            self.NoteWindow={'title':'笔记','class_name':'FavNoteWnd','framework_id':"Win32"}#笔记窗口
            self.IncomingCallWindow={'title':'微信','class_name':'mmui::VOIPTrayWindow'}#微信来电(视频或语音)桌面右下角的托盘窗口
            self.VoipCallWindow={'title':'微信音视频通话','class_name':'mmui::VOIPWindow'}#接通语音或视频电话后的通话窗口
        if self.language=='English':
            self.AddFriendWindow={'title':'Add Contacts','class_name':'mmui::AddFriendWindow','control_type':'Window'}#添加朋友窗口
            self.SettingsWindow={'title':'Settings','class_name':"mmui::PreferenceWindow",'control_type':'Window','auto_id':'PreferenceWindow'}#微信设置窗口
            self.ContactManagerWindow={'title':'Manage Contacts','class_name':"mmui::ContactsManagerWindow"}#通讯录管理窗口
            self.MomentsWindow={'title':'Moments','control_type':"Window",'class_name':"mmui::SNSWindow",'framework_id':'Qt'}#朋友圈窗口
            self.ChatFilesWindow={'title':'Chat Files','control_type':'Window','class_name':"mmui::FileManagerWindow"}#聊天文件窗口
            self.MiniProgramWindow={'title':'WeChat','control_type':'Pane','class_name':'Chrome_WidgetWin_0'}#小程序面板窗口
            self.SearchWindow={'title':'WeChat','class_name':'Chrome_WidgetWin_0','control_type':'Pane'}#搜一搜窗口
            self.ChannelsWindow={'title':'WeChat','class_name':'Chrome_WidgetWin_0','control_type':'Pane'}#视频号窗口
            self.NoteWindow={'title':'Note','class_name':'FavNoteWnd','framework_id':"Win32"}#笔记窗口
            self.IncomingCallWindow={'title':'Weixin','class_name':'mmui::VOIPTrayWindow'}#微信来电(视频或语音)桌面右下角的托盘窗口
            self.VoipCallWindow={'title':'Weixin Voice & Video Calls','class_name':'mmui::VOIPWindow'}#接通语音或视频电话后的通话窗口
        if self.language=='繁體中文':
            self.AddFriendWindow={'title':'新增朋友','class_name':"mmui::AddFriendWindow",'control_type':'Window'}#添加朋友窗口
            self.SettingsWindow={'title':'設定','class_name':"mmui::PreferenceWindow",'control_type':'Window','auto_id':"PreferenceWindow"}#微信设置窗口
            self.ContactManagerWindow={'title':'通訊錄管理','class_name':"mmui::ContactsManagerWindow"}#通讯录管理窗口
            self.MomentsWindow={'title':'朋友圈','control_type':"Window",'class_name':"mmui::SNSWindow",'framework_id':'Qt'}#朋友圈窗口
            self.ChatFilesWindow={'title':'微信檔案','control_type':'Window','class_name':"mmui::FileManagerWindow"}#聊天文件窗口
            self.MiniProgramWindow={'title':'WeChat','control_type':'Pane','class_name':'Chrome_WidgetWin_0'}#小程序面板窗口
            self.SearchWindow={'title':'WeChat','class_name':'Chrome_WidgetWin_0','control_type':'Pane'}#搜一搜窗口
            self.ChannelsWindow={'title':'WeChat','class_name':'Chrome_WidgetWin_0','control_type':'Pane'}#视频号窗口
            self.NoteWindow={'title':'筆記','class_name':'FavNoteWnd','framework_id':"Win32"}#笔记窗口
            self.IncomingCallWindow={'title':'微信','class_name':'mmui::VOIPTrayWindow'}#微信来电(视频或语音)桌面右下角的托盘窗口
            self.VoipCallWindow={'title':'微信語音/視訊通話 ','class_name':'mmui::VOIPWindow'}#接通语音或视频电话后的通话窗口

class ListItem_Control():
    def __init__(self,language=language,Version=Version):
        self.language=language
        self.Version=Version
        '''微信主界面内所有类型为ListItem的UI控件'''
        self.SessionListItem={'control_type':'ListItem','class_name':'mmui::ChatSessionCell'}#微信会话列表中的聊天对象
        self.SnsContentListItem={'control_type':'ListItem','class_name':'mmui::TimeLineContentCell'}#朋友圈内容ListItem
        if self.language=='简体中文':
            self.GroupLabelListItem={'title':'群聊','control_type':'ListItem','class_name':'mmui::XTableCell'}#微信顶部搜索内容后搜索结果中的群聊标签(分隔符)
            self.NewFriendListItem={'control_type':'ListItem','title':r'新的朋友','class_name':'mmui::ContactsCellGroupView'}#主界面切换至通讯录后，通讯录列表内的新的朋友项目
            self.SavedGroupsListIte={'control_type':'ListItem','title_re':r'群聊\d+','class_name':'mmui::ContactsCellGroupView'}#主界面切换至通讯录后，通讯录列表内的群聊项目
            self.OfficialAccountsListItem={'control_type':'ListItem','title_re':r'公众号\d+','class_name':'mmui::ContactsCellGroupView'}#主界面切换至通讯录后，通讯录列表内的公众号项目
            self.ServiceAccountsListItem={'control_type':'ListItem','title_re':r'服务号\d+','class_name':'mmui::ContactsCellGroupView'}#主界面切换至通讯录后，通讯录列表内的服务号项目
            self.WeComContactsListItems={'control_type':'ListItem','title_re':r'企业微信联系人\d+','class_name':'mmui::ContactsCellGroupView'}#主界面切换至通讯录后，通讯录列表内的企业微信联系人项目
            self.MyEnterPriseListItems={'control_type':'ListItem','title_re':r'我的企业\d+','class_name':'mmui::ContactsCellGroupView'}#主界面切换至通讯录后，通讯录列表内的我的企业项目
            self.ContactsListItem={'control_type':'ListItem','title_re':r'联系人\d+','class_name':'mmui::ContactsCellGroupView'}#主界面切换至通讯录后，通讯录列表内的联系人项目
            self.ChatHistoryListItem={'control_type':'ListItem','title':'聊天记录','class_name':'mmui::XTableCell'}#在微信顶部搜索搜索结果中时弹出的聊天记录分区
            self.RecentUsedListItem={'control_type':'ListItem','class_name':'mmui::XTableCell','title':'最近使用'}#聊天文件中的最近使用
            self.FriendPrivacyListItem={'control_type':'ListItem','class_name':'mmui::ContactsManagerControlFolderCell','title':'朋友权限'}#通讯录管理界面中的朋友权限
            self.TagListItem={'control_type':'ListItem','class_name':'mmui::ContactsManagerControlFolderCell','title':'标签'}#通讯录管理界面中的标签
            self.RecentGroupListItem={'control_type':'ListItem','class_name':'mmui::ContactsManagerControlFolderCell','title':'最近群聊'}#通讯录管理界面中的最近群聊
            self.AllListItem={'title':'全部','control_type':'ListItem','class_name':'mmui::XTableCell'}#聊天文件界面中的全部
            self.LinkListItem={'control_type':'ListItem','title':'链接'}#微信收藏界面组边链接分组
            self.CreateLabelListItem={'control_type':'ListItem','title':'新建标签','class_name':'mmui::ContactsManagerControlCreateLabelCell'}#通讯录管理界面中的新建标签
            self.MobileSearchListItem={'title':'网络查找手机/QQ号：','control_type':'ListItem'}#在顶部搜索的是数字组合时出现的查找手机号qq好
        if self.language=='English':
            self.GroupLabelListItem={'title':'Group Chats','control_type':'ListItem','class_name':'mmui::XTableCell'}#微信顶部搜索内容后搜索结果中的群聊标签(分隔符)
            self.NewFriendListItem={'control_type':'ListItem','title':r'New Friends','class_name':'mmui::ContactsCellGroupView'}#主界面切换至通讯录后，通讯录列表内的新的朋友项目
            self.SavedGroupsListIte={'control_type':'ListItem','title_re':r'Saved Groups\d+','class_name':'mmui::ContactsCellGroupView'}#主界面切换至通讯录后，通讯录列表内的群聊项目
            self.OfficialAccountsListItem={'control_type':'ListItem','title_re':r'Official Accounts\d+','class_name':'mmui::ContactsCellGroupView'}#主界面切换至通讯录后，通讯录列表内的公众号项目
            self.ServiceAccountsListItem={'control_type':'ListItem','title_re':r'Service Accounts\d+','class_name':'mmui::ContactsCellGroupView'}#主界面切换至通讯录后，通讯录列表内的服务号项目
            self.WeComContactsListItems={'control_type':'ListItem','title_re':r'WeCom Contacts\d+','class_name':'mmui::ContactsCellGroupView'}#主界面切换至通讯录后，通讯录列表内的企业微信联系人项目
            self.MyEnterPriseListItems={'control_type':'ListItem','title_re':r'My Enterprise\d+','class_name':'mmui::ContactsCellGroupView'}#主界面切换至通讯录后，通讯录列表内的我的企业项目
            self.ContactsListItem={'control_type':'ListItem','title_re':r'Contacts\d+','class_name':'mmui::ContactsCellGroupView'}#主界面切换至通讯录后，通讯录列表内的联系人项目
            self.ChatHistoryListItem={'control_type':'ListItem','title':'Chat History','class_name':'mmui::XTableCell'}#在微信顶部搜索搜索结果中时弹出的聊天记录分区
            self.RecentUsedListItem={'control_type':'ListItem','class_name':'mmui::XTableCell','title':'Recent'}#聊天文件中的最近使用
            self.FriendPrivacyListItem={'control_type':'ListItem','class_name':'mmui::ContactsManagerControlFolderCell','title':'Privacy'}#通讯录管理界面中的朋友权限
            self.TagListItem={'control_type':'ListItem','class_name':'mmui::ContactsManagerControlFolderCell','title':'Tags'}#通讯录管理界面中的标签
            self.RecentGroupListItem={'control_type':'ListItem','class_name':'mmui::ContactsManagerControlFolderCell','title':'Recent Group Chats'}#通讯录管理界面中的最近群聊
            self.AllListItem={'title':'All','control_type':'ListItem','class_name':'mmui::XTableCell'}#聊天文件界面中的全部
            self.LinkListItem={'control_type':'ListItem','title':'Links'}#微信收藏界面组边链接分组
            self.CreateLabelListItem={'title':'Add Tag','control_type':'ListItem','class_name':'mmui::ContactsManagerControlCreateLabelCell'}#通讯录管理界面中的新建标签
            self.MobileSearchListItem={'title':'Search mobile/QQ ID:','control_type':'ListItem'}#在顶部搜索的是数字组合时出现的查找手机号qq好
        if self.language=='繁體中文':
            self.GroupLabelListItem={'title':'群組','control_type':'ListItem','class_name':'mmui::XTableCell'}#微信顶部搜索内容后搜索结果中的群聊标签(分隔符)
            self.NewFriendListItem={'control_type':'ListItem','title':r'新的朋友','class_name':'mmui::ContactsCellGroupView'}#主界面切换至通讯录后，通讯录列表内的新的朋友项目
            self.SavedGroupsListIte={'control_type':'ListItem','title_re':r'群聊\d+','class_name':'mmui::ContactsCellGroupView'}#主界面切换至通讯录后，通讯录列表内的群聊项目
            self.OfficialAccountsListItem={'control_type':'ListItem','title_re':r'官方賬號\d+','class_name':'mmui::ContactsCellGroupView'}#主界面切换至通讯录后，通讯录列表内的公众号项目
            self.ServiceAccountsListItem={'control_type':'ListItem','title_re':r'服務賬號\d+','class_name':'mmui::ContactsCellGroupView'}#主界面切换至通讯录后，通讯录列表内的服务号项目
            self.WeComContactsListItems={'control_type':'ListItem','title_re':r'WeCom 聯絡人\d+','class_name':'mmui::ContactsCellGroupView'}#主界面切换至通讯录后，通讯录列表内的企业微信联系人项目
            self.MyEnterPriseListItems={'control_type':'ListItem','title_re':r'我的企業\d+','class_name':'mmui::ContactsCellGroupView'}#主界面切换至通讯录后，通讯录列表内的我的企业项目
            self.ContactsListItem={'control_type':'ListItem','title_re':r'聯絡人\d+','class_name':'mmui::ContactsCellGroupView'}#主界面切换至通讯录后，通讯录列表内的联系人项目
            self.ChatHistoryListItem={'control_type':'ListItem','title':'聊天記錄','class_name':'mmui::XTableCell'}#在微信顶部搜索搜索结果中时弹出的聊天记录分区
            self.RecentUsedListItem={'control_type':'ListItem','class_name':'mmui::XTableCell','title':'最近使用'}#聊天文件中的最近使用
            self.FriendPrivacyListItem={'control_type':'ListItem','class_name':'mmui::ContactsManagerControlFolderCell','title':'朋友權限'}#通讯录管理界面中的朋友权限
            self.TagListItem={'control_type':'ListItem','class_name':'mmui::ContactsManagerControlFolderCell','title':'標籤'}#通讯录管理界面中的标签
            self.RecentGroupListItem={'control_type':'ListItem','class_name':'mmui::ContactsManagerControlFolderCell','title':'最近群組'}#通讯录管理界面中的最近群聊
            self.AllListItem={'title':'全部','control_type':'ListItem','class_name':'mmui::XTableCell'}#聊天文件界面中的全部
            self.LinkListItem={'control_type':'ListItem','title':'連結'}#微信收藏界面组边链接分组
            self.CreateLabelListItem={'control_type':'ListItem','title':'建立標簽','class_name':'mmui::ContactsManagerControlCreateLabelCell'}#通讯录管理界面中的新建标签
            self.MobileSearchListItem={'title':'網路搜尋手機/QQ 號碼：','control_type':'ListItem'}#在顶部搜索的是数字组合时出现的查找手机号qq好

class List_Control():
    def __init__(self,language=language,Version=Version):
        self.language=language
        self.Version=Version
        self.ContactsList={'auto_id':'primary_table_.contact_list','control_type':'List'}#通讯录中的通讯录列表
        self.SideList={'control_type':'List','class_name':'mmui::ContactsManagerControlView'}#通讯录管理界面左侧侧边栏
        self.ContactsManageList={'control_type':'List','class_name':'mmui::ContactsManagerControlView'}#通讯录管理界面左侧列表
        self.FileList={'control_type':'List','auto_id':'file_list','class_name':'mmui::XRecyclerTableView'}#聊天文件右侧的文件列表
        self.MomentsList={'control_type':'List','auto_id':'sns_list','found_index':0}#朋友圈列表
        self.SnsDetailList={'control_type':'List','auto_id':'sns_detail_list'}#好友的朋友圈内点开一个项目后内部的列表
        self.SolitaireList={'control_type':'List','auto_id':'solitaire_list'}#群聊接龙界面内的接龙列表
        self.CommonGroupList={'control_type':'List','auto_id':'same_chat_room_contact_list'}#共同群聊列表
        self.SearchResult={'title':'','control_type':'List','auto_id':'search_list'}#主界面顶部搜索栏搜索内容的结果列表
        self.CollectionList={'auto_id':'fav_category_list','control_type':'List'}#收藏界面左侧的列表
        self.LinkList={'auto_id':'fav_detail_list','control_type':'List'}#收藏界面内的链接列表
        if self.language=='简体中文':
            self.QuickActionsList={'title':'快捷操作','control_type':'List'}#主界面点击+号后弹出的快捷操作列表
            self.ChatHistoryList={'title':'聊天记录','control_type':'List'}#聊天记录窗口中的存放聊天消息的列表
            self.ConversationList={'title':'会话','control_type':'List'}#主界面左侧的好友聊天会话列表
            self.FriendChatList={'title':'消息','control_type':'List'}#聊天界面内的消息列表
        if self.language=='English':
            self.QuickActionsList={'title':'Shortcuts','control_type':'List'}#主界面点击+号后弹出的快捷操作列表
            self.ChatHistoryList={'title':'Chat History','control_type':'List'}#聊天记录窗口中的存放聊天消息的列表
            self.ConversationList={'title':'Chats','control_type':'List'}#主界面左侧的好友聊天会话列表
            self.FriendChatList={'title':'Messages','control_type':'List'}#聊天界面内的消息列表
        if self.language=='繁體中文':
            self.QuickActionsList={'title':'快捷操作','control_type':'List'}#主界面点击+号后弹出的快捷操作列表
            self.ChatHistoryList={'title':'聊天記錄','control_type':'List'}#聊天记录窗口中的存放聊天消息的列表
            self.ConversationList={'title':'對話','control_type':'List'}#主界面左侧的好友聊天会话列表
            self.FriendChatList={'title':'訊息','control_type':'List'}#聊天界面内的消息列表

class Login_window_Control():
    '''登录界面内的第一级ui'''
    def __init__(self,language=language,Version=Version):
        self.language=language
        self.Version=Version
        self.LoginWindow={'class_name':'mmui::LoginWindow'}#登录微信界面
        if self.language=='简体中文':
            self.LoginButton={'control_type':'Button','title':'进入微信'}#进入微信按钮
            self.SwitchText={'control_type':'Text','title':'切换账号'}#切换账号按钮
        if self.language=='English':
            self.LoginButton={'control_type':'Button','title':'Enter Weixin'}#进入微信按钮
            self.SwitchText={'control_type':'Text','title':'Switch Account'}#切换账号按钮
        if self.language=='繁體中文':
            self.LoginButton={'control_type':'Button','title':'進入微信'}#进入微信按钮
            self.SwitchText={'control_type':'Text','title':'切換賬號'}#切换账号按钮
class Main_window_Control():
    '''主界面下所有的第一级Ui'''
    def __init__(self,language=language,Version=Version):
        self.language=language
        self.Version=Version
        self.CurrentChatWindow={'control_type':'Edit','title':'Edit'}#主界面右侧的聊天窗口
        self.EditArea={'control_type':'Edit','class_name':"mmui::ChatInputField"}#好友主界面的聊天编辑区域
        self.SearchResult={'title':'','control_type':'List','auto_id':'search_list'}#主界面顶部搜索栏搜索内容的结果列表
        self.ChatToolBar={'title':'','found_index':0,'control_type':'ToolBar'}#主界面右侧聊天窗口内的工具栏(语音视频按钮在其中)
        self.ContactsList={'control_type':'List','class_name':"mmui::StickyHeaderRecyclerListView"}#主界面切换至联系人后的通讯录列表
        if self.language=='简体中文':
            self.MainWindow={'title':'微信','class_name':'mmui::MainWindow','framework_id':'Qt'}#微信主界面
            self.Toolbar={'title':'导航','control_type':'ToolBar'}#主界面左侧的侧边栏
            self.SessionList={'title':'会话','control_type':'List','framework_id':'Qt'}#主界面左侧会话列表
            self.Search={'title':'搜索','control_type':'Edit','class_name':"mmui::XValidatorTextEdit"}#主界面顶部的搜索栏
            self.SearchNewFriendBar={'title':'微信号/手机号','control_type':'Edit'}#添加好友时顶部搜索栏名称
            self.FriendChatList={'title':'消息','control_type':'List'}#主界面右侧聊天区域内与好友的消息列表
        if self.language=='English':
            self.MainWindow={'title':'Weixin','class_name':'mmui::MainWindow','framework_id':'Qt'}#微信主界面
            self.Toolbar={'title':'Navigation','control_type':'ToolBar'}#主界面左侧的侧边栏
            self.SessionList={'title':'Chats','control_type':'List','framework_id':'Qt'}#主界面左侧会话列表
            self.Search={'title':'Search','control_type':'Edit','class_name':"mmui::XValidatorTextEdit"}#主界面顶部的搜索栏
            self.FriendChatList={'title':'Messages','control_type':'List'}#主界面右侧聊天区域内与好友的消息列表
        if self.language=='繁體中文':
            self.MainWindow={'title':'微信','class_name':'mmui::MainWindow','framework_id':'Qt'}#微信主界面
            self.Toolbar={'title':'導航','control_type':'ToolBar'}#主界面左侧的侧边栏
            self.SessionList={'title':'對話','control_type':'List','framework_id':'Qt'}#主界面左侧会话列表
            self.Search={'title':'搜尋','control_type':'Edit','class_name':"mmui::XValidatorTextEdit"}#主界面顶部的搜索栏
            self.FriendChatList={'title':'訊息','control_type':'List'}#主界面右侧聊天区域内与好友的消息列表

class MenuItem_Control():
    def __init__(self,language=language,Version=Version):
        self.language=language
        self.Version=Version
        if self.language=='简体中文':
            self.ForwardMenuItem={'title':'转发...','control_type':'MenuItem'}#右键后的转发消息MenuItem
            self.CopyMenuItem={'title':'复制','control_type':'MenuItem'}#右键菜单里的复制消息
            self.SaveMenuItem={'title':'另存为...','control_type':'MenuItem'}#右键图片视频或文件时菜单里的另存为
            self.AddToFavoritesMenuItem={'title':'收藏','control_type':'MenuItem'}#添加到收藏夹
            self.TranslateMenuItem={'title':'翻译','control_type':'MenuItem'}#右键文本消息后的翻译选项
            self.EditMenuItem={'title':'编辑','control_type':'MenuItem'}#右键图片后的编辑选项
            self.DeleteMenuItem={'title':'删除','control_type':'MenuItem','auto_id':'XMenuItem'}#右键消息后的删除选项
            self.SearchMenuItem={'title':'搜一搜','control_type':'MenuItem'}#右键消息后的搜索选项
            self.QuoteMeunItem={'title':'引用','control_type':'MenuItem'}#右键消息后的引用选项
            self.SelectMenuItem={'title':'多选','control_type':'MenuItem'}#右键消息后的多选选项
            self.EnlargeMeunItem={'title':'放大阅读','control_type':'MenuItem'}#右键消息后的放大选项
            self.FindInChatMenuItem={'title':'定位到聊天位置','control_type':'MenuItem'}#聊天记录页面内右键消息后的Find in chat选项
            self.CopyLinkMenuItem={'title':'复制链接','auto_id':'XMenuItem','control_type':'MenuItem'}#在收藏界面右键菜单里的复制链接选项目
        if self.language=='English':
            self.ForwardMenuItem={'title':'Forward...','control_type':'MenuItem'}#右键后的转发消息MenuItem
            self.CopyMenuItem={'title':'Copy','control_type':'MenuItem'}#右键菜单里的复制消息
            self.SaveMenuItem={'title':'Save as...','control_type':'MenuItem'}#右键图片视频或文件时菜单里的另存为
            self.AddToFavoritesMenuItem={'title':'Add to Favorites','control_type':'MenuItem'}#添加到收藏夹
            self.TranslateMenuItem={'title':'Translate','control_type':'MenuItem'}#右键文本消息后的翻译选项
            self.EditMenuItem={'title':'Edit','control_type':'MenuItem'}#右键图片后的编辑选项
            self.DeleteMenuItem={'title':'Delete','control_type':'MenuItem','auto_id':'XMenuItem'}#右键消息后的删除选项
            self.SearchMenuItem={'title':'Search','control_type':'MenuItem'}#右键消息后的搜索选项
            self.QuoteMeunItem={'title':'Quote','control_type':'MenuItem'}#右键消息后的引用选项
            self.SelectMenuItem={'title':'Select...','control_type':'MenuItem'}#右键消息后的多选选项
            self.EnlargeMeunItem={'title':'Enlarge','control_type':'MenuItem'}#右键消息后的放大选项
            self.FindInChatMenuItem={'title':'Find in Chat','control_type':'MenuItem'}#聊天记录页面内右键消息后的Find in chat选项
            self.CopyLinkMenuItem={'title':'Copy URL','auto_id':'XMenuItem','control_type':'MenuItem'}#在收藏界面右键菜单里的复制链接选项目
        if self.language=='繁體中文':
            self.ForwardMenuItem={'title':'轉發...','control_type':'MenuItem'}#右键后的转发消息MenuItem
            self.CopyMenuItem={'title':'複製','control_type':'MenuItem'}#右键菜单里的复制消息
            self.SaveMenuItem={'title':'另存為...','control_type':'MenuItem'}#右键图片视频或文件时菜单里的另存为
            self.AddToFavoritesMenuItem={'title':'收藏','control_type':'MenuItem'}#添加到收藏夹
            self.TranslateMenuItem={'title':'翻譯','control_type':'MenuItem'}#右键文本消息后的翻译选项
            self.EditMenuItem={'title':'编辑','control_type':'MenuItem'}#右键图片后的编辑选项
            self.DeleteMenuItem={'title':'刪除','control_type':'MenuItem','auto_id':'XMenuItem'}#右键消息后的删除选项
            self.SearchMenuItem={'title':'搜一搜','control_type':'MenuItem'}#右键消息后的搜索选项
            self.QuoteMeunItem={'title':'引用','control_type':'MenuItem'}#右键消息后的引用选项
            self.SelectMenuItem={'title':'多選','control_type':'MenuItem'}#右键消息后的多选选项
            self.EnlargeMeunItem={'title':'放大閱讀','control_type':'MenuItem'}#右键消息后的放大选项
            self.FindInChatMenuItem={'title':'定位到聊天位置','control_type':'MenuItem'}#聊天记录页面内右键消息后的Find in chat选项
            self.CopyLinkMenuItem={'title':'複製連結','auto_id':'XMenuItem','control_type':'MenuItem'}#在收藏界面右键菜单里的复制链接选项目

class Menu_Control():
    def __init__(self,language=language,Version=Version):
        self.Version=Version
        self.language=language
        self.RightClickMenu={'title':'','control_type':'Menu','class_name':'CMenuWnd','framework_id':'Win32'}#微信界面内右键后弹出的菜单

class Pane_Control():
    def __init__(self,language=language,Version=Version):
        self.language=language
        self.Version=Version
        self.ConfirmPane={'title':'','class_name':'WeUIDialog','control_type':'Pane'}#通用的确认框
        self.GroupInvitationPane={'control_type':'Pane','class_name':'Chrome_WidgetWin_0','title':''}#群聊邀请卡片链接(40人以上群聊拉人时触发)点击后弹出的pane
        self.OfficialAccountPane={'title':'公众号','control_type':'Pane','class_name':'Chrome_WidgetWin_0','framework_id':'Win32'}#公众号窗口

class SideBar_Control():
    '''主界面侧导航栏下的所有Ui'''
    def __init__(self,language=language,Version=Version):
        self.language=language
        self.Version=Version
        if self.language=='简体中文':
            self.Weixin={'title':'微信','control_type':'Button','class_name':"mmui::XTabBarItem"}#主界面左侧的微信按钮
            self.Contacts={'title':'通讯录','control_type':'Button'}#主界面左侧的通讯录按钮
            self.Collections={'title':'收藏','control_type':'Button','class_name':"mmui::XTabBarItem"}#主界面左侧的收藏按钮
            self.Moments={'title':'朋友圈','control_type':'Button','class_name':"mmui::XTabBarItem"}#主界面左侧的朋友圈按钮
            self.Search={'title':'搜一搜','control_type':'Button','class_name':"mmui::XTabBarItem"}#主界面左侧的搜一搜按钮
            self.Channels={'title':'视频号','control_type':'Button','class_name':"mmui::XTabBarItem"}#主界面左侧的视频号按钮
            self.MiniProgram={'title':'小程序面板','control_type':'Button','class_name':"mmui::XTabBarItem"}#主界面左侧的小程序面板按钮
            self.Discovery={'title':'发现','control_type':'Button'}#主界面左侧的发现按钮
            self.More={'title':'更多','control_type':'Button','found_index':0}#主界面左侧的更多按钮 
        if self.language=='English':
            self.Weixin={'title':'Weixin','control_type':'Button','class_name':"mmui::XTabBarItem"}#主界面左侧的微信按钮
            self.Contacts={'title':'Contacts','control_type':'Button'}#主界面左侧的通讯录按钮
            self.Collections={'title':'Favorites','control_type':'Button','class_name':"mmui::XTabBarItem"}#主界面左侧的收藏按钮
            self.Moments={'title':'Moments','control_type':'Button','class_name':"mmui::XTabBarItem"}#主界面左侧的朋友圈按钮
            self.Search={'title':'Search','control_type':'Button','class_name':"mmui::XTabBarItem"}#主界面左侧的搜一搜按钮
            self.Channels={'title':'Channels','control_type':'Button','class_name':"mmui::XTabBarItem"}#主界面左侧的视频号按钮
            self.MiniProgram={'title':'Mini Programs Panel','control_type':'Button','class_name':"mmui::XTabBarItem"}#主界面左侧的小程序面板按钮
            self.Discovery={'title':'Discovery','control_type':'Button'}#主界面左侧的发现按钮
            self.More={'title':'More','control_type':'Button','found_index':0}#主界面左侧的更多按钮 
        if self.language=='繁體中文':
            self.Weixin={'title':'微信','control_type':'Button','class_name':"mmui::XTabBarItem"}#主界面左侧的微信按钮
            self.Contacts={'title':'通訊錄','control_type':'Button'}#主界面左侧的通讯录按钮
            self.Collections={'title':'收藏','control_type':'Button','class_name':"mmui::XTabBarItem"}#主界面左侧的收藏按钮
            self.Moments={'title':'朋友圈','control_type':'Button','class_name':"mmui::XTabBarItem"}#主界面左侧的朋友圈按钮
            self.Search={'title':'搜一搜','control_type':'Button','class_name':"mmui::XTabBarItem"}#主界面左侧的搜一搜按钮
            self.Channels={'title':'影音號','control_type':'Button','class_name':"mmui::XTabBarItem"}#主界面左侧的视频号按钮
            self.MiniProgram={'title':'小程式面板','control_type':'Button','class_name':"mmui::XTabBarItem"}#主界面左侧的小程序面板按钮
            self.Discovery={'title':'发现','control_type':'Button'}#主界面左侧的发现按钮
            self.More={'title':'更多','control_type':'Button','found_index':0}#主界面左侧的更多按钮 

class Text_Control():
    '''微信主界面以及设置界面内所有类型为Text的UI控件'''
    def __init__(self,language=language,Version=Version):
        self.language=language
        self.Version=Version
        self.CurrentChatNameText={'auto_id':"content_view.top_content_view.title_h_view.left_v_view.left_content_v_view.left_ui_.big_title_line_h_view.current_chat_name_label",
        'control_type':"Text"}#当前
        self.GroupLabelText={'auto_id':"content_view.top_content_view.title_h_view.left_v_view.left_content_v_view.left_ui_.big_title_line_h_view.current_chat_count_label",'control_type':'Text'}#聊天界面是群聊时顶部才会出现的文本
        if self.language=='简体中文':
            self.SharedGroupsText={'title':'共同群聊','control_type':'Text'}#好友profile内的共同群聊文本，可能没有
            self.OutLineText={'title':'外观','control_type':'Text'}#设置界面内的外观文本
            self.LanguageText={'title':'语言','control_type':'Text'}#设置界面内的语言文本
            self.FontSizeText={'title':'字体大小','control_type':'Text'}#设置界面内的字体大小文本
            self.GroupNameText={'title':'群聊名称','control_type':'Text'}#群聊设置界面内的群聊名称文本
            self.AddContentText={'title':'添加补充内容','control_type':'Text'}#群聊接龙界面内的添加补充内容文本
            self.ImageExpiredText={'control_type':'Text','title':'图片已过期或被清理','class_name':'mmui::XTextView'}#图片预览窗口过期的图片
            self.VideoExpiredText={'title':'视频过期或已被删除','control_type':'Text'}#图片预览窗口内的视频过期或已被删除文本
            self.EarliestOneText={'title':'已是第一张','control_type':'Text'}#图片预览窗口里的这是最早的一张图片文本
            self.InvitationSentText={'title':'该群聊邀请已发送','control_type':'Text'}#群聊邀请窗口内的群聊邀请文本,如果出现,说明该群聊自己发出并且已加入
            self.InvitationExpiredText={'title':'该群聊邀请已过期','control_type':'Text'}#群聊邀请窗口内的群聊邀请过期文本
        if self.language=='English':
            self.SharedGroupsText={'title':'Shared Groups','control_type':'Text'}#好友profile内的共同群聊文本，可能没有
            self.OutLineText={'title':'Appearance','control_type':'Text'}#设置界面内的外观文本
            self.LanguageText={'title':'Language','control_type':'Text'}#设置界面内的语言文本
            self.FontSizeText={'title':'Font Size','control_type':'Text'}#设置界面内的字体大小文本
            self.GroupNameText={'title':'Group Name','control_type':'Text'}#群聊设置界面内的群聊名称文本
            self.AddContentText={'title':'Add additional content','control_type':'Text'}#群聊接龙界面内的添加补充内容文本
            self.ImageExpiredText={'control_type':'Text','title':'ImagesExpired or deleted','class_name':'mmui::XTextView'}#图片预览窗口过期的图片
            self.VideoExpiredText={'title':'Video expired or deleted.','control_type':'Text'}#图片预览窗口内的视频过期或已被删除文本
            self.EarliestOneText={'title':'This is the first one','control_type':'Text'}#图片预览窗口里的这是最早的一张图片文本
            self.InvitationSentText={'title':'Group invitation sent','control_type':'Text'}#群聊邀请窗口内的群聊邀请文本,如果出现,说明该群聊自己发出并且已加入
            self.InvitationExpiredText={'title':'Group invitation expired','control_type':'Text'}#群聊邀请窗口内的群聊邀请过期文本
        if self.language=='繁體中文':
            self.SharedGroupsText={'title':'共同群組','control_type':'Text'}#好友profile内的共同群聊文本，可能没有
            self.OutLineText={'title':'外觀','control_type':'Text'}#设置界面内的外观文本
            self.FontSizeText={'title':'字體大小','control_type':'Text'}#设置界面内的字体大小文本
            self.LanguageText={'title':'語言','control_type':'Text'}#语言文本，修改微信语言时要用到
            self.GroupNameText={'title':'群組名稱','control_type':'Text'}#群聊设置界面内的群聊名称文本
            self.AddContentText={'title':'新增補充內容','control_type':'Text'}#群聊接龙界面内的添加补充内容文本
            self.ImageExpiredText={'control_type':'Text','title':'圖片已過期或被清除'}#图片预览窗口过期的图片
            self.VideoExpiredText={'title':'影片已過期或被清除','control_type':'Text'}#图片预览窗口内的视频过期或已被删除文本
            self.EarliestOneText={'title':'已是第一張','control_type':'Text'}#图片预览窗口里的这是最早的一张图片文本
            self.InvitationSentText={'title':'此群組邀請已傳送','control_type':'Text'}#群聊邀请窗口内的群聊邀请文本,如果出现,说明该群聊自己发出并且已加入
            self.InvitationExpiredText={'title':'该群聊邀请已过期','control_type':'Text'}#群聊邀请窗口内的群聊邀请过期文本
            

class TabItem_Control():
    def __init__(self,language=language,Version=Version):
        self.language=language
        self.Version=Version
        if self.language=='简体中文':
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
        if self.language=='English':
            self.GeneralTabItem={'title':'General','control_type':'TabItem'}#微信设置界面里左侧的通用设置Tabitem
            self.MyAccountTabItem={'title':'My Account','control_type':'TabItem'}#微信设置界面里左侧的账号设置Tabitem
            self.NotificationsTabItem={'title':'Notifications','control_type':'TabItem'}#微信设置界面里左侧的消息通知Tabitem
            self.FileTabItem={'title':'Files','control_type':'TabItem'}#微信聊天记录界面里顶部的文件Tabitem
            self.PhotoAndVideoTabItem={'title':'Media','control_type':'TabItem','class_name':'mmui::XButton','framework_id':'Qt'}#微信聊天记录界面里顶部的照片和视频Tabitem
            self.LinkTabItem={'title':'Link','control_type':'TabItem','class_name':'mmui::XButton','framework_id':'Qt'}#微信聊天记录界面里顶部的链接Tabitem
            self.MiniProgramTabItem={'title':'Mini Programs','control_type':'TabItem','class_name':'mmui::XButton','framework_id':'Qt'}#微信聊天记录界面里顶部的小程序Tabitem
            self.MusicTabItem={'title':'Music','control_type':'TabItem','class_name':'mmui::XButton','framework_id':'Qt'}#微信聊天记录界面里顶部的音乐Tabitem
            self.ChannelTabItem={'title':'Channels','control_type':'TabItem','class_name':'mmui::XButton','framework_id':'Qt'}#微信聊天记录界面里顶部的视频号Tabitem
            self.DateTabItem={'title':'Date','control_type':'TabItem'}#微信聊天记录界面里顶部的日期Tabitem
        if self.language=='繁體中文':
            self.GeneralTabItem={'title':'一般','control_type':'TabItem'}#微信设置界面里左侧的通用设置Tabitem
            self.MyAccountTabItem={'title':'賬號與儲存','control_type':'TabItem'}#微信设置界面里左侧的账号设置Tabitem
            self.NotificationsTabItem={'title':'通知','control_type':'TabItem'}#微信设置界面里左侧的消息通知Tabitem
            self.FileTabItem={'title':'檔案','control_type':'TabItem'}#微信聊天记录界面里顶部的文件Tabitem
            self.PhotoAndVideoTabItem={'title':'圖片與影片','control_type':'TabItem','class_name':'mmui::XButton','framework_id':'Qt'}#微信聊天记录界面里顶部的照片和视频Tabitem
            self.LinkTabItem={'title':'連結','control_type':'TabItem','class_name':'mmui::XButton','framework_id':'Qt'}#微信聊天记录界面里顶部的链接Tabitem
            self.MiniProgramTabItem={'title':'小程式','control_type':'TabItem','class_name':'mmui::XButton','framework_id':'Qt'}#微信聊天记录界面里顶部的小程序Tabitem
            self.MusicTabItem={'title':'音樂','control_type':'TabItem','class_name':'mmui::XButton','framework_id':'Qt'}#微信聊天记录界面里顶部的音乐Tabitem
            self.ChannelTabItem={'title':'影音號','control_type':'TabItem','class_name':'mmui::XButton','framework_id':'Qt'}#微信聊天记录界面里顶部的视频号Tabitem
            self.DateTabItem={'title':'日期','control_type':'TabItem'}#微信聊天记录界面里顶部的日期Tabitem

class Window_Control():
    def __init__(self,language=language,Version=Version):
        self.language=language
        self.Version=Version
        self.ChatHistoryWindow={'control_type':'Window','class_name':'mmui::SearchMsgUniqueChatWindow','framework_id':'Qt'}#聊天记录窗口
        self.SettingsMenu={'class_name':'SetMenuWnd','control_type':'Window'}#设置与其他按钮按下后的菜单栏
        self.PopUpProfileWindow={'title':'Weixin','control_type':'Window','class_name':'mmui::ProfileUniquePop'}#好友设置界面点击头像后弹出的个人简介窗口
        self.NativeChooseFileWindow={'control_type':'Window','framework_id':'Win32','top_level_only':False,'found_index':0}#windows本地选择文件夹窗口
        self.MentionPopOverWindow={'control_type':'Window','auto_id':'MentionPopover','found_index':0}#群聊输入@后弹出的群成员选择界面
        self.PopOverWindow={'control_type':'Window','class_name':'mmui::XPopover'}#当微信窗口足够小的时候,会收起一部分侧边栏按钮到这个窗口内,此时需要点击...后在这个界面内点击
        self.SolitaireWindow={'control_type':'Window','class_name':'mmui::SolitaireWindow'}#群接龙窗口
        self.ImagePreviewWindow={'control_type':'Window','class_name':'mmui::PreviewWindow'}#微信点击图片或视频后桌面弹出的图片与视频窗口
        self.AddfriendWindow={'control_type':'Window','class_name':'mmui::AddFriendWindow'}#添加好友窗口
        self.SearchChatHistoryWindow={'control_type':'Window','auto_id':'GlobalSearchMsgWindow'}#聊天记录搜索窗口
        self.SnsPublishWindow={'auto_id':'SnsPublishPanel','control_type':'Window'}#微信朋友圈后发布按钮点击后的面板
        if self.language=='简体中文':
            self.MomentsWindow={'title':'朋友圈','control_type':'Window','class_name':'mmui::SNSWindow'}#好友朋友圈窗口
            self.SessionPickerWindow={'control_type':'Window','title':'微信发送给','class_name':'mmui::SessionPickerWindow'}#转发消息的session_picker_window
            self.VerifyFriendWindow={'control_type':'Window','title':'申请添加朋友','class_name':'mmui::VerifyFriendWindow'}#添加新朋友时的申请添加朋友界面
            self.EditContactWindow={'control_type':'Window','title':'设置备注和标签','class_name':'mmui::ProfileUniquePop'}#修改好友备注时的界面
            self.VerifyFriendWindow2={'title':'通过朋友验证','control_type':'Window','class_name':'mmui::VerifyFriendWindow'}#通讯录新的朋友中右侧前往验证按钮点击后弹出的通过朋友验证窗口
            self.AddFriendWindow={'title':'添加朋友','class_name':"mmui::AddFriendWindow",'control_type':'Window'}#添加朋友窗口
            self.SettingsWindow={'title':'设置','class_name':"mmui::PreferenceWindow",'control_type':'Window','auto_id':"PreferenceWindow"}#微信设置窗口
            self.ContactManagerWindow={'title':'通讯录管理','class_name':"mmui::ContactsManagerWindow"}#通讯录管理窗口
            self.MomentsWindow={'title':'朋友圈','control_type':"Window",'class_name':"mmui::SNSWindow",'framework_id':'Qt'}#朋友圈窗口
            self.ChatFilesWindow={'title':'聊天文件','control_type':'Window','class_name':"mmui::FileManagerWindow"}#聊天文件窗口
            self.MiniProgramWindow={'title':'微信','control_type':'Pane','class_name':'Chrome_WidgetWin_0'}#小程序面板窗口
            self.SearchWindow={'title':'微信','class_name':'Chrome_WidgetWin_0','control_type':'Pane'}#搜一搜窗口
            self.ChannelsWindow={'title':'微信','class_name':'Chrome_WidgetWin_0','control_type':'Pane'}#视频号窗口
            self.NoteWindow={'title':'笔记','framework_id':"Win32"}#笔记窗口
            self.IncomingCallWindow={'title':'微信','class_name':'mmui::VOIPTrayWindow'}#微信来电(视频或语音)桌面右下角的托盘窗口
            self.VoipCallWindow={'title':'微信音视频通话','class_name':'mmui::VOIPWindow'}#接通语音或视频电话后的通话窗口
            self.PrivacyWindow={'title':'朋友权限','class_name':'mmui::ProfileUniquePop'}#好友权限窗口,4.1.9点击好友权限后弹出的窗口独立于桌面了
        if self.language=='English':
            self.MomentsWindow={'title':'Moments','control_type':'Window','class_name':'mmui::SNSWindow'}#好友朋友圈窗口
            self.SessionPickerWindow={'control_type':'Window','title':'WeixinSend To','class_name':'mmui::SessionPickerWindow'}#转发消息的session_picker_window
            self.VerifyFriendWindow={'control_type':'Window','title':'Send Friend Request','class_name':'mmui::VerifyFriendWindow'}#添加新朋友时的申请添加朋友界面
            self.EditContactWindow={'control_type':'Window','title':'Edit Contact','class_name':'mmui::ProfileUniquePop'}#修改好友备注时的界面
            self.VerifyFriendWindow2={'title':'Confirm Friend Request','control_type':'Window','class_name':'mmui::VerifyFriendWindow'}#通讯录新的朋友中右侧前往验证按钮点击后弹出的通过朋友验证窗口
            self.AddFriendWindow={'title':'Add Contacts','class_name':'mmui::AddFriendWindow','control_type':'Window'}#添加朋友窗口
            self.SettingsWindow={'title':'Settings','class_name':"mmui::PreferenceWindow",'control_type':'Window','auto_id':'PreferenceWindow'}#微信设置窗口
            self.ContactManagerWindow={'title':'Manage Contacts','class_name':"mmui::ContactsManagerWindow"}#通讯录管理窗口
            self.MomentsWindow={'title':'Moments','control_type':"Window",'class_name':"mmui::SNSWindow",'framework_id':'Qt'}#朋友圈窗口
            self.ChatFilesWindow={'title':'Chat Files','control_type':'Window','class_name':"mmui::FileManagerWindow"}#聊天文件窗口
            self.MiniProgramWindow={'title':'WeChat','control_type':'Pane','class_name':'Chrome_WidgetWin_0'}#小程序面板窗口
            self.SearchWindow={'title':'WeChat','class_name':'Chrome_WidgetWin_0','control_type':'Pane'}#搜一搜窗口
            self.ChannelsWindow={'title':'WeChat','class_name':'Chrome_WidgetWin_0','control_type':'Pane'}#视频号窗口
            self.NoteWindow={'title':'Note','framework_id':"Win32"}#笔记窗口
            self.IncomingCallWindow={'title':'Weixin','class_name':'mmui::VOIPTrayWindow'}#微信来电(视频或语音)桌面右下角的托盘窗口
            self.VoipCallWindow={'title':'Weixin Voice & Video Calls','class_name':'mmui::VOIPWindow'}#接通语音或视频电话后的通话窗口
        if self.language=='繁體中文':
            self.MomentsWindow={'title':'朋友圈','control_type':'Window','class_name':'mmui::SNSWindow'}#好友朋友圈窗口
            self.SessionPickerWindow={'control_type':'Window','title':'微信傳送给','class_name':'mmui::SessionPickerWindow'}#转发消息的session_picker_window
            self.VerifyFriendWindow={'control_type':'Window','title':'申請新增朋友','class_name':'mmui::VerifyFriendWindow'}#添加新朋友时的申请添加朋友界面
            self.EditContactWindow={'control_type':'Window','title':'設定備註和標籤','class_name':'mmui::ProfileUniquePop'}#修改好友备注时的界面
            self.VerifyFriendWindow2={'title':'通過朋友驗證','control_type':'Window','class_name':'mmui::VerifyFriendWindow'}#通讯录新的朋友中右侧前往验证按钮点击后弹出的通过朋友验证窗口
            self.AddFriendWindow={'title':'新增朋友','class_name':"mmui::AddFriendWindow",'control_type':'Window'}#添加朋友窗口
            self.SettingsWindow={'title':'設定','class_name':"mmui::PreferenceWindow",'control_type':'Window','auto_id':"PreferenceWindow"}#微信设置窗口
            self.ContactManagerWindow={'title':'通訊錄管理','class_name':"mmui::ContactsManagerWindow"}#通讯录管理窗口
            self.MomentsWindow={'title':'朋友圈','control_type':"Window",'class_name':"mmui::SNSWindow",'framework_id':'Qt'}#朋友圈窗口
            self.ChatFilesWindow={'title':'微信檔案','control_type':'Window','class_name':"mmui::FileManagerWindow"}#聊天文件窗口
            self.MiniProgramWindow={'title':'WeChat','control_type':'Pane','class_name':'Chrome_WidgetWin_0'}#小程序面板窗口
            self.SearchWindow={'title':'WeChat','class_name':'Chrome_WidgetWin_0','control_type':'Pane'}#搜一搜窗口
            self.ChannelsWindow={'title':'WeChat','class_name':'Chrome_WidgetWin_0','control_type':'Pane'}#视频号窗口
            self.NoteWindow={'title':'筆記','framework_id':"Win32"}#笔记窗口
            self.IncomingCallWindow={'title':'微信','class_name':'mmui::VOIPTrayWindow'}#微信来电(视频或语音)桌面右下角的托盘窗口
            self.VoipCallWindow={'title':'微信語音/視訊通話 ','class_name':'mmui::VOIPWindow'}#接通语音或视频电话后的通话窗口
            self.PrivacyWindow={'title':'朋友權限','class_name':'mmui::ProfileUniquePop'}#好友权限窗口,4.1.9点击好友权限后弹出的窗口独立于桌面了

Main_window=Main_window_Control(language=language,Version=Version)#主界面UI
Login_window=Login_window_Control(language=language,Version=ValueError)#登录界面UI
Independent_window=Independent_window_Control(language=language,Version=Version)#独立主界面UI
SideBar=SideBar_Control(language=language,Version=Version)#侧边栏UI
Buttons=Button_Control(language=language,Version=Version)#所有Button类型UI
Edits=Edit_Control(language=language,Version=Version)#所有Edit类型UI
Texts=Text_Control(language=language,Version=Version)#所有Text类型UI
TabItems=TabItem_Control(language=language,Version=Version)#所有TabIem类型UI
Lists=List_Control(language=language,Version=Version)#所有列表类型UI
Panes=Pane_Control(language=language,Version=Version)#所有Pane类型UI
Windows=Window_Control(language=language,Version=Version)#所有Window类型UI
CheckBoxes=CheckBox_Control(language=language,Version=Version)#所有CheckBox类型UI
MenuItems=MenuItem_Control(language=language,Version=Version)#所有MenuItem类型UI
Menus=Menu_Control(language=language,Version=Version)#所有Menu类型UI
Groups=Group_Control(language=language,Version=Version)#所有Group类型UI
Customs=Custom_Control(language=language,Version=Version)#所有Custom类型UI
ListItems=ListItem_Control(language=language,Version=Version)#所有ListItems类型UI