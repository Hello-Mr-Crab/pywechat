'''
Uielements
---------
PC微信中的各种Ui-Object,我将其分成两大类\n
一类是按照属性分类,有Buttons,Edits,Texts,TabItems等,每一个类内基本包含了微信内\n
所有的control_type与类名一致的UI控件\n
另一类是按照其属的父级窗口,可分为Login_window(登录界面),Main_window(主界面)\n
Independent_window(独立窗口)这三类\n
使用时只需要:
```
from pywechat import Tools
from pywechat.Uielements import Edits
#返回值为kwargs字典,可以直接使用**解包给pywinauto的child_window或descendants方法
searchbar=Edits().SearchEdit
main_window=Tools.open_wechat()
main_window.child_window(**searchbar).type_keys('你好!')
```
即可获取到每个类别下的各个组件\n
使用时无需担心语言对UI控件的影响,导入Uielements时会自动根据微信的语言调整控件中的title属性\n
如果需要自行指定,language的取值为:'简体中文','繁体中文','英文'
'''
import winreg
from pywechat.Errors import NotInstalledError

def language_detector():
    """
    查询注册表来检测当前微信的语言版本
    """
    #微信3.9版本的一般注册表路径
    reg_path=r"Software\Tencent\WeChat"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
            value=winreg.QueryValueEx(key,"LANG_ID")[0]
            language_map={
                0x00000009: '英文',
                0x00000004: '简体中文',
                0x00000404: '繁体中文'
            }
            return language_map.get(value)
    except FileNotFoundError:
        raise NotInstalledError
language=language_detector()

class Buttons():
    '''
    微信主界面内所有类型为Button的UI控件\n
    '''
    def __init__(self,language=language):
        self.language=language
        if self.language=='简体中文':
            self.MySelfButton={'control_type':'Button','found_index':0}#主界面下的第一个按钮,也就是我自己的头像按钮，必须通过main_window.child_window(**Buttons.MyselfButton)使用!
            self.CheckMoreMessagesButton={'title':'查看更多消息','control_type':'Button','found_index':1}#好友聊天界面内的查看更多消息按钮
            self.OfficialAcountButton={'title':'公众号','control_type':'Button'}#搜一搜内公众号按钮                                                                                                                                
            self.SettingsAndOthersButton={'title':'设置及其他','control_type':'Button'}#设置及其他按钮
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
            self.ClearButton={'control_type':'Button','title':'确定'}#清楚聊天记录确定按钮
            self.MultiSelectButton={'control_type':'Button','title':'多选'}#转发消息或文件时的多选按钮
            self.HangUpButton={'control_type':'Button','title':'挂断'}#接听语音或视频电话按钮
            self.SendButton={'control_type':'Button','title':'发送'}#转发文件或消息按钮
            self.SendRespectivelyButton={'control_type':'Button','title_re':'分别发送'}#转发消息时分别发送按钮
            self.SettingsButton={'control_type':'Button','title':'设置'}#工具栏打开微信设置menu内的选项按钮
            self.ClearChatHistoryButton={'control_type':'Button','title':'清空聊天记录'}#清空好友或群聊聊天记录时的按钮
            self.RestoreDefaultSettingsButton={'control_type':'Button','title':'恢复默认设置'}#微信设置回复默认设置
            self.VoiceCallButton={'control_type':'Button','title':'语音聊天'}#给好友拨打语音电话按钮
            self.VideoCallButton={'control_type':'Button','title':'视频聊天'}#给好友拨打视频电话按钮
            self.CompleteButton={'control_type':'Button','title':'完成'}#完成按钮
            self.PinButton={'control_type':'Button','title':'置顶'}#将好友置顶按钮
            self.CancelPinButton={'control_type':'Button','title':'取消置顶'}#取消好友置顶按钮
            self.AddTagButton={'control_type':'Button','title':'点击编辑标签'}#好友没有标签
            self.TagEditButton={'control_type':'Button','found_index':0}#好友已经有标签需要修改时的编辑好友标签按钮
            self.ChatHistoryButton={'control_type':'Button','title':'聊天记录'}#获取聊天记录按钮
            self.ChangeGroupNameButton={'control_type':'Button','title':'群聊名称'}#修改群聊名称按钮
            self.MyAliasInGroupButton={'control_type':'Button','title':'我在本群的昵称'}#修改群内我的昵称按钮
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
            self.AddPhoneNumberButton={'control_type':'Button','found_index':1}#设置好友标签与备注界面内的第二个Button,添加电话号按钮
            self.AddPictureButton={'control_type':'Button','found_index':2}#设置好友标签与备注界面内的第三个Button,添加图片按钮
            self.SubscribeButton={'control_type':'Button','title':'关注'}#公众号界面内的关注按钮(未关注的情况下)
            self.SaveAsButton={'title_re':'另存为','control_type':'Button'}#图片preview窗口内的另存为按钮
            self.ReloadButton={'title':'重新加载','control_type':'Button'}#看一看界面里的重新加载按钮
            self.RotateButton={'title':'旋转','control_type':'Button'}#图片预览窗口里的旋转按钮,只有图片才有,视频没有可以用来判别是图片还是视频
            self.PreviousButton={'title':'上一张','control_type':'Button'}#图片预览窗口里的上一张按钮
            self.ShowAllButton={'title':'查看更多','control_type':'Button'}#群设置界面内的查看更多按钮
            self.LedgerButton={'title':'小账本','control_type':'Button'}#微信收款助手内的小账本按钮
            self.PaymentCodeButton={'title':'个人收款码','control_type':'Button','framework_id':'Chrome'}#微信收款助手内的个人收款码按钮
            self.InputButton={'title':'输入','control_type':'Button'}#公众号内最右侧的键盘图标形状的按钮,按下后可以向公众号发送消息
            self.ServiceButton={'title':'服务','control_type':'Button'}##公众号内最右侧的键盘图标形状的按钮,按下后转换为四个按钮
            self.CommentButton={'title':'评论','control_type':'Button'}#朋友圈内的评论按钮
            self.ImageButton={'title':'图片','control_type':'Button'}#朋友圈包含\d+图片窗口下的图片按钮,当且仅当好友的朋友圈内容含有图片时才有这个按钮
            self.ChannelButton={'title':'视频号','control_type':'Button'}#微信聊天记录界面里顶部的视频号Tabitem
            self.TransactionsButton={'title':'Transactions','control_type':'Button'}#微信支付界面内的我的账单按钮
        
        if self.language=='英文':
            self.MySelfButton={'control_type':'Button','found_index':0}#主界面下的第一个按钮,也就是我自己的头像按钮，必须通过main_window.child_window(**Buttons.MyselfButton)使用!
            self.CheckMoreMessagesButton={'title':'View more messages','control_type':'Button','found_index':1}#好友聊天界面内的查看更多消息按钮
            self.OfficialAcountButton={'title':'Official Accounts','control_type':'Button'}#搜一搜内公众号按钮                                                                                                                                
            self.SettingsAndOthersButton={'title':'Settings and Others','control_type':'Button'}#设置及其他按钮
            self.ConfirmQuitGroupButton={'title':'Leave','control_type':'Button'}#确认退出群聊按钮
            self.CerateNewNote={'title':'New Note','control_type':'Button'}#创建一个新笔记按钮
            self.CerateGroupChatButton={'title':"Start Group Chat",'control_type':"Button"}#创建新群聊按钮
            self.AddNewFriendButon={'title':'Add Friends','control_type':'Button'}#添加新朋友按钮
            self.AddToContactsButton={'control_type':'Button','title':'Add to Contacts'}#添加新朋友时的添加至通讯录内按钮
            self.AcceptButton={'control_type':'Button','title':'Accept'}#接听电话按钮
            self.ChatMessageButton={'title':'Chat Info','control_type':'Button'}#聊天信息按钮                   
            self.CloseAutoLoginButton={'control_type':'Button','title':'Disable'}#微信设置关闭自动登录按钮
            self.ConfirmButton={'control_type':'Button','title':'OK'}#确定操作按钮
            self.CancelButton={'control_type':'Button','title':'Cancel'}#取消操作按钮
            self.DeleteButton={'control_type':'Button','title':'Delete'}#删除好友或将群成员从群聊踢出时的按钮
            self.clearButton={'control_type':'Button','title':'Clear'}#删除好友按钮
            self.MultiSelectButton={'control_type':'Button','title':'Multiple'}#转发消息或文件时的多选按钮
            self.HangUpButton={'control_type':'Button','title':'Hang Up'}#接听语音或视频电话按钮
            self.SendButton={'control_type':'Button','title':'Send'}#转发文件或消息按钮
            self.SendRespectivelyButton={'control_type':'Button','title_re':'Send To'}#转发消息时分别发送按钮
            self.SettingsButton={'control_type':'Button','title':'Settings'}#工具栏打开微信设置menu内的选项按钮
            self.ClearChatHistoryButton={'control_type':'Button','title':'Clear Chat History'}#清空好友或群聊聊天记录时的按钮
            self.RestoreDefaultSettingsButton={'control_type':'Button','title':'Restore Defaults'}#微信设置回复默认设置
            self.VoiceCallButton={'control_type':'Button','title':'Voice Call'}#给好友拨打语音电话按钮
            self.VideoCallButton={'control_type':'Button','title':'Video Call'}#给好友拨打视频电话按钮
            self.CompleteButton={'control_type':'Button','title':'Done'}#完成按钮
            self.PinButton={'control_type':'Button','title':'Sticky on Top'}#将好友置顶按钮
            self.CancelPinButton={'control_type':'Button','title':'Sticky on Top cancelled'}#取消好友置顶按钮
            self.TagEditButton={'control_type':'Button','found_index':0}#编辑好友标签按钮
            self.ChatHistoryButton={'control_type':'Button','title':'Chat History'}#获取聊天记录按钮
            self.ChangeGroupNameButton={'control_type':'Button','title':'Group Name'}#修改群聊名称按钮
            self.MyAliasInGroupButton={'control_type':'Button','title':'My Alias in Group'}#修改群内我的昵称按钮
            self.RemarkButton={'control_type':'Button','title':'Remark'}#修改群聊备注时的按钮
            self.QuitGroupButton={'control_type':'Button','title':'Leave'}#退出某个群聊时的按钮
            self.EditButton={'control_type':'Button','title':'Edit'}#编辑群公告内已有内容时下方的按钮
            self.EditGroupNotificationButton={'control_type':'Button','title':'Click to edit group notice'}#编辑群公告按钮
            self.PublishButton={'control_type':'Button','title':'Post'}#编辑群公告完成后发布群公告的发布按钮
            self.ContactsManageButton={'title':'Manage Contacts','control_type':'Button'}#通讯录管理按钮
            self.ConfirmEmptyChatHistoryButon={'title':'Clear','control_type':'Button'}#点击清空聊天记录后弹出的query界面内的清空按钮
            self.MoreButton={'title':'More','control_type':'Button'}#打开微信好友设置界面更多按钮
            self.LogoutButton={'title':'Log Out','control_type':'Button'}#设置界面里退出登录按钮
            self.RefreshButton={'title':'Refresh','control_type':'Button'}#朋友圈的刷新按钮
            self.RectentGroupButton={'title':'Recent Group Chats','control_type':'Button'}#通讯录设置界面里的最近群聊按钮
            self.AddPhoneNumberButton={'control_type':'Button','found_index':1}#设置好友标签与备注界面内的第二个Button,添加电话号按钮
            self.AddPictureButton={'control_type':'Button','found_index':2}#设置好友标签与备注界面内的第三个Button,添加图片按钮
            self.SubscribeButton={'control_type':'Button','title':'关注'}#公众号界面内的关注按钮(未关注的情况下)
            self.SaveAsButton={'title_re':'Save as','control_type':'Button'}#图片preview窗口内的另存为按钮
            self.ReloadButton={'title':'重新加载','control_type':'Button'}#看一看界面里的重新加载按钮
            self.RotateButton={'title':'Rotate','control_type':'Button'}#图片预览窗口里的旋转按钮,只有图片才有,视频没有可以用来判别是图片还是视频
            self.PreviousButton={'title':'Previous','control_type':'Button'}#图片预览窗口里的上一张按钮
            self.ShowAllButton={'title':'Show All','control_type':'Button'}#群设置界面内的查看更多按钮
            self.LedgerButton={'title':'小账本','control_type':'Button'}#微信收款助手内的小账本按钮
            self.PaymentCodeButton={'title':'个人收款码','control_type':'Button','framework_id':'Chrome'}#微信收款助手内的个人收款码按钮
            self.InputButton={'title':'Enter','control_type':'Button'}#公众号内最右侧的键盘图标形状的按钮,按下后可以向公众号发送消息
            self.ServiceButton={'title':'Service','control_type':'Button'}##公众号内最右侧的键盘图标形状的按钮,按下后转换为四个按钮
            self.CommentButton={'title':'Comment','control_type':'Button'}#朋友圈内的评论按钮
            self.ImageButton={'title':'图片','control_type':'Button'}#朋友圈包含\d+图片窗口下的图片按钮,当且仅当好友的朋友圈内容含有图片时才有这个按钮
            self.ChannelButton={'title':'Channel','control_type':'Button'}#微信朋友圈有人转发视频号时的视频号按钮
            self.TransactionsButton={'title':'Transactions','control_type':'Button'}#微信支付界面内的我的账单按钮
        
        if self.language=='繁体中文':
            self.MySelfButton={'control_type':'Button','found_index':0}#主界面下的第一个按钮,也就是我自己的头像按钮，必须通过main_window.child_window(**Buttons.MyselfButton)使用!
            self.CheckMoreMessagesButton={'title':'查看更多訊息','control_type':'Button','found_index':1}#好友聊天界面内的查看更多消息按钮
            self.OfficialAcountButton={'title':'官方賬號','control_type':'Button'}#搜一搜内公众号按钮                                                                                                                                
            self.SettingsAndOthersButton={'title':'設定與其他','control_type':'Button'}#设置及其他按钮
            self.ConfirmQuitGroupButton={'title':'退出','control_type':'Button'}#确认退出群聊按钮
            self.CerateNewNote={'title':'新建筆記','control_type':'Button'}#创建一个新笔记按钮
            self.CerateGroupChatButton={'title':"建立群組",'control_type':"Button"}#创建新群聊按钮
            self.AddNewFriendButon={'title':'新增朋友','control_type':'Button'}#添加新朋友按钮
            self.AddToContactsButton={'control_type':'Button','title':'新增到通訊錄'}#添加新朋友时的添加至通讯录内按钮
            self.AcceptButton={'control_type':'Button','title':'接受'}#接听电话按钮
            self.ChatMessageButton={'title':'聊天資訊','control_type':'Button'}#好友设置右上角的三个点                   
            self.CloseAutoLoginButton={'control_type':'Button','title':'關閉'}#微信设置关闭自动登录按钮
            self.ConfirmButton={'control_type':'Button','title':'確定'}#确定操作按钮
            self.CancelButton={'control_type':'Button','title':'取消'}#取消操作按钮
            self.DeleteButton={'control_type':'Button','title':'刪除'}#删除好友按钮
            self.ClearButton={'control_type':'Button','title':'刪除'}#删除聊天记录的确定按钮
            self.MultiSelectButton={'control_type':'Button','title':'多選'}#转发消息或文件时的多选按钮
            self.HangUpButton={'control_type':'Button','title':'掛斷'}#接听语音或视频电话按钮
            self.SendButton={'control_type':'Button','title':'發送'}#转发文件或消息按钮
            self.SendRespectivelyButton={'control_type':'Button','title_re':'分別傳送'}#转发消息时分别发送按钮
            self.SettingsButton={'control_type':'Button','title':'設定'}#工具栏打开微信设置menu内的选项按钮
            self.ClearChatHistoryButton={'control_type':'Button','title':'刪除聊天記錄'}#清空好友或群聊聊天记录时的按钮
            self.RestoreDefaultSettingsButton={'control_type':'Button','title':'還原預設設定'}#微信设置回复默认设置
            self.VoiceCallButton={'control_type':'Button','title':'語音通話'}#给好友拨打语音电话按钮
            self.VideoCallButton={'control_type':'Button','title':'視訊通話'}#给好友拨打视频电话按钮
            self.CompleteButton={'control_type':'Button','title':'完成'}#完成按钮
            self.PinButton={'control_type':'Button','title':'置頂'}#将好友置顶按钮
            self.CancelPinButton={'control_type':'Button','title':'取消置頂'}#取消好友置顶按钮
            self.TagEditButton={'control_type':'Button','found_index':0}#好友已经有标签需要修改时的编辑好友标签按钮
            self.ChatHistoryButton={'control_type':'Button','title':'聊天記錄'}#获取聊天记录按钮
            self.ChangeGroupNameButton={'control_type':'Button','title':'群組名稱'}#修改群聊名称按钮
            self.MyAliasInGroupButton={'control_type':'Button','title':'我在群組的暱稱'}#修改群内我的昵称按钮
            self.RemarkButton={'control_type':'Button','title':'備註'}#修改群聊备注时的按钮
            self.QuitGroupButton={'control_type':'Button','title':'退出群組'}#退出某个群聊时的按钮
            self.EditButton={'control_type':'Button','title':'編輯'}#编辑群公告内已有内容时下方的按钮
            self.EditGroupNotificationButton={'control_type':'Button','title':'點擊編輯群組公告'}#编辑群公告按钮
            self.PublishButton={'control_type':'Button','title':'發佈'}#编辑群公告完成后发布群公告的发布按钮
            self.ContactsManageButton={'title':'通訊錄管理','control_type':'Button'}#通讯录管理按钮
            self.ConfirmEmptyChatHistoryButon={'title':'刪除','control_type':'Button'}#点击清空聊天记录后弹出的query界面内的清空按钮
            self.MoreButton={'title':'更多','control_type':'Button'}#打开微信好友设置界面更多按钮
            self.LogoutButton={'title':'登出','control_type':'Button'}#设置界面里退出登录按钮
            self.RefreshButton={'title':'重新整理','control_type':'Button'}#朋友圈的刷新按钮
            self.RectentGroupButton={'title':'最近群組','control_type':'Button'}#通讯录设置界面里的最近群聊按钮
            self.AddPhoneNumberButton={'control_type':'Button','found_index':1}#设置好友标签与备注界面内的第二个Button,添加电话号按钮
            self.AddPictureButton={'control_type':'Button','found_index':2}#设置好友标签与备注界面内的第三个Button,添加图片按钮
            self.SubscribeButton={'control_type':'Button','title':'关注'}#公众号界面内的关注按钮(未关注的情况下)
            self.SaveAsButton={'title_re':'另存為','control_type':'Button'}#图片preview窗口内的另存为按钮
            self.ReloadButton={'title':'重新加载','control_type':'Button'}#看一看界面里的重新加载按钮
            self.RotateButton={'title':'旋轉','control_type':'Button'}#图片预览窗口里的旋转按钮,只有图片才有,视频没有可以用来判别是图片还是视频
            self.PreviousButton={'title':'上一張','control_type':'Button'}#图片预览窗口里的上一张按钮
            self.ShowAllButton={'title':'查看更多','control_type':'Button'}#群设置界面内的查看更多按钮
            self.LedgerButton={'title':'小账本','control_type':'Button'}#微信收款助手内的小账本按钮
            self.PaymentCodeButton={'title':'个人收款码','control_type':'Button','framework_id':'Chrome'}#微信收款助手内的个人收款码按钮
            self.InputButton={'title':'输入','control_type':'Button'}#公众号内最右侧的键盘图标形状的按钮,按下后可以向公众号发送消息
            self.ServiceButton={'title':'服务','control_type':'Button'}##公众号内最右侧的键盘图标形状的按钮,按下后转换为四个按钮
            self.CommentButton={'title':'評論','control_type':'Button'}#朋友圈内的评论按钮
            self.ImageButton={'title':'图片','control_type':'Button'}#朋友圈包含\d+图片窗口下的图片按钮,当且仅当好友的朋友圈内容含有图片时才有这个按钮
            self.ChannelButton={'title':'影音號','control_type':'Button'}#微信朋友圈有人转发视频号时的视频号按钮
            self.TransactionsButton={'title':'我的账单','control_type':'Button'}#微信支付界面内的我的账单按钮

class Edits():     
    '''微信主界面内所有类型为Edit(不包含独立窗口)的UI控件'''
    def __init__(self,language=language):
        self.language=language
        if self.language=='简体中文':
            self.SearchEdit={'title':'搜索','control_type':'Edit','found_index':0}#主界面和一些其他界面内通用的搜索框
            self.CurrentChatEdit={'control_type':'Edit','found_index':1}#微信主界面下当前的聊天窗口
            self.AddNewFriendSearchEdit={'title':'搜索','control_type':'Edit'}#添加新朋友界面里的搜索
            self.SearchNewFriendEdit={'title':'微信号/手机号','control_type':'Edit'}#添加新朋友界面里的搜
            self.RemarkEdit={'found_index':0,'control_type':'Edit'}#设置好友备注和标签界面内第一个属性为edit的修改好友备注编辑框
            self.TagEdit={'found_index':0,'control_type':'Edit'}#编辑好友或群聊标签
            self.DescriptionEdit={'found_index':1,'control_type':'Edit'}#设置好友备注和标签界面内第2个属性为edit的修改好友备注编辑框           
            self.RequestContentEdit={'control_type':'Edit','found_index':0}#添加好友(从群里或者是主页)时,发送请求时的内容
            self.SearchGroupMemeberEdit={'title':'搜索群成员','control_type':'Edit'}#添加或删除群成员时,在弹出的界面里顶部的搜索栏
            self.EditWnd={'control_type':'Edit','class_name':'EditWnd','framework_id':'Win32'}#通用的编辑框,主要出现在好友和群聊设置界面里

        if self.language=='英文':
            self.SearchEdit={'title':'Search','control_type':'Edit','found_index':0}#主界面和一些其他界面内通用的搜索框
            self.SearchNewFriendEdit={'title':'Weixin ID/Mobile','control_type':'Edit'}#微信主界面下当前的聊天窗口
            self.AddNewFriendSearchEdit={'title':'Search','control_type':'Edit'}#添加新朋友界面里的搜索
            self.CurrentChatEdit={'control_type':'Edit','found_index':1}#添加新朋友界面里的搜
            self.RemarkEdit={'found_index':0,'control_type':'Edit'}#设置好友备注和标签界面内第一个属性为edit的修改好友备注编辑框
            self.TagEdit={'found_index':0,'control_type':'Edit'}#编辑标签界面内的编辑好友或群聊标签
            self.DescriptionEdit={'found_index':1,'control_type':'Edit'}#设置好友备注和标签界面内第2个属性为edit的修改好友备注编辑框            
            self.RequestContentEdit={'control_type':'Edit','found_index':0}#添加好友(从群里或者是主页)时,发送请求时的内容
            self.SearchGroupMemeberEdit={'title':'Search','control_type':'Edit'}#添加或删除群成员时,在弹出的界面里顶部的搜索栏
            self.EditWnd={'control_type':'Edit','class_name':'EditWnd','framework_id':'Win32'}#通用的编辑框,主要出现在好友和群聊设置界面里

        if self.language=='繁体中文':
            self.SearchEdit={'title':'搜尋','control_type':'Edit','found_index':0}#主界面和一些其他界面内通用的搜索框
            self.CurrentChatEdit={'control_type':'Edit','found_index':1}#微信主界面下当前的聊天窗口
            self.AddNewFriendSearchEdit={'title':'搜尋','control_type':'Edit'}#添加新朋友界面里的搜索
            self.SearchNewFriendEdit={'title':'微信 ID/手機號碼','control_type':'Edit'}#添加新朋友界面里的搜
            self.TagEdit={'found_index':0,'control_type':'Edit'}#编辑好友或群聊标签
            self.RemarkEdit={'found_index':0,'control_type':'Edit'}#设置好友备注和标签界面内第一个属性为edit的修改好友备注编辑框
            self.DescriptionEdit={'found_index':1,'control_type':'Edit'}#设置好友备注和标签界面内第2个属性为edit的修改好友备注编辑框           
            self.RequestContentEdit={'control_type':'Edit','found_index':0}#添加好友(从群里或者是主页)时,发送请求时的内容
            self.SearchGroupMemeberEdit={'title':'搜尋','control_type':'Edit'}#添加或删除群成员时,在弹出的界面里顶部的搜索栏
            self.EditWnd={'control_type':'Edit','class_name':'EditWnd','framework_id':'Win32'}#通用的编辑框,主要出现在好友和群聊设置界面里

class Texts():
    '''微信主界面以及设置界面内所有类型为Text的UI控件\n'''
    def __init__(self,language=language):
        self.language=language
        if self.language=='简体中文':
            self.NetWorkError={'title':'网络不可用，请检查你的网络设置','control_type':'Text'}#微信没联网时顶部的红色文本
            self.SearchContactsResult={'title_re':'搜索','control_type':'Text'}#搜索联系人时的文本结果
            self.ChangeGroupNameWarnText={'title':'仅群主或管理员可以修改','control_type':'Text'}#修改群名时如果有这个文本，无权修改
            self.EditGroupNoticeWarnText={'title':'仅群主和管理员可编辑','control_type':'Text'}#编辑群公告或群名时，如果界面有这个文本，无权编辑
            self.SendMessageShortcutText={'title':'发送消息','control_type':'Text'}#发送消息快捷键文本,修改快捷键设置时要用到
            self.CptureScreenShortcutText={'title':'截取屏幕','control_type':'Text'}#截取屏幕快捷键文本,修改快捷键设置时要用到
            self.OpenWechatShortcutText={'title':'打开微信','control_type':'Text'}#打开微信快捷键文本,修改快捷键设置时要用到
            self.LockWechatShortcutText={'title':'锁定微信','control_type':'Text'}#锁定微信快捷键文本,修改快捷键设置时要用到
            self.LanguageText={'title':'语言','control_type':'Text'}#语言文本，修改微信语言时要用到
            self.GroupNameText={'title':'群聊名称','control_type':'Text'}#群聊设置界面内的群聊名称文本
            self.FileDeletedText={'title':'已被删除','control_type':'Text'}#聊天记录界面内文件过期,已被删除
            self.SaveText={'title':'保存','control_type':'Text'}#聊天记录窗口内选取多个文件,图片,链接,音乐后底部的保存文本
            self.DeleteText={'title':'删除','control_type':'Text'}#聊天记录窗口内选取多个文件,图片,链接,音乐后底部的删除文本
            self.FavoriteText={'title':'收藏','control_type':'Text'}#聊天记录窗口内选取多个文件,图片,链接,音乐后底部的收藏文本
            self.ForwardText={'title':'逐条转发','control_type':'Text'}#聊天记录窗口内多个选取多个文件,图片链接,音乐后底部的逐一转发文本
            self.CombineForwardText={'title':'合并转发','control_type':'Text'}#聊天记录窗口内多个选取多个文件,图片链接,音乐后底部的合并转发文本
            self.SendMessageText={'title':'发消息','control_type':'Text'}#公众号界面内的发消息按钮上的文本(其实不是按钮是Grouo组)
            self.ImageExpiredText={'title':'图片过期或已被清理','control_type':'Text'}#图片预览窗口内的图片过期或已被删除文本
            self.VideoExpiredText={'title':'视频过期或已被删除','control_type':'Text'}#图片预览窗口内的视频过期或已被删除文本
            self.EarliestOneText={'title':'已是第一张','control_type':'Text'}#图片预览窗口里的这是最早的一张图片文本
            self.ExpiredText={'title':'已过期','control_type':'Text'}#聊天记录列表里点击视频播放按钮后可能出现的过期按钮
            self.DeletedText={'title':'已被删除','control_type':'Text'}#聊天记录列表里点击视频播放按钮后可能出现的已被删除按钮
            self.OfficialAccountsText={'title':'公众号','control_type':'Text','found_index':2}#通讯录中点击公众号选项后右侧主界面的公众号文本
            self.SavePaymentCodeText={'title':'保存收款码','control_type':'Text'}#微信收款助手小账本内点击个人收款码后弹出的经营账户窗口内的保存收款码文本，点击后可以出发保存事件

        if self.language=='英文':
            self.NetWorkError={'title':'Network Disconnected. Check and try again.','control_type':'Text'}#微信没联网时顶部的红色文本
            self.SearchContactsResult={'title_re':'Search','control_type':'Text'}#搜索联系人时的文本结果
            self.SearchResultText={'title_re':'Search','control_type':'Text'}#修改群名时如果有这个文本，无权修改
            self.ChangeGroupNameWarnText={'title':'Only group owner and admin can modify','control_type':'Text'}#修改群名时如果有这个文本，无权修改
            self.EditGroupNoticeWarnText={'title':'Only group owner and admin can edit','control_type':'Text'}#编辑群公告或群名时，如果界面有这个文本，无权编辑
            self.SendMessageShortcutText={'title':'Send Message','control_type':'Text'}#发送消息快捷键文本,修改快捷键设置时要用到
            self.CptureScreenShortcutText={'title':'Take Screenshot','control_type':'Text'}#截取屏幕快捷键文本,修改快捷键设置时要用到
            self.OpenWechatShortcutText={'title':'Open Weixin','control_type':'Text'}#打开微信快捷键文本,修改快捷键设置时要用到
            self.LockWechatShortcutText={'title':'Lock Weixin','control_type':'Text'}#锁定微信快捷键文本,修改快捷键设置时要用到
            self.LanguageText={'title':'Language','control_type':'Text'}#语言文本，修改微信语言时要用到
            self.GroupNameText={'title':'Group Name','control_type':'Text'}#群聊设置界面内的群聊名称文本
            self.FileDeletedText={'title':'Deleted','control_type':'Text'}#聊天记录界面内文件过期,已被删除
            self.SaveText={'title':'Save','control_type':'Text'}#聊天记录窗口内选取多个文件,图片,链接,音乐后底部的保存文本
            self.DeleteText={'title':'Delete','control_type':'Text'}#聊天记录窗口内选取多个文件,图片,链接,音乐后底部的删除文本
            self.FavoriteText={'title':'Add to Favorites','control_type':'Text'}#聊天记录窗口内选取多个文件,图片,链接,音乐后底部的收藏文本
            self.ForwardText={'title':'One-by-One Forward','control_type':'Text'}#聊天记录窗口内多个选取多个文件,图片链接,音乐后底部的逐一转发文本
            self.CombineForwardText={'title':'Combine and Forward','control_type':'Text'}#聊天记录窗口内多个选取多个文件,图片链接,音乐后底部的合并转发文本
            self.SendMessageText={'title':'发消息','control_type':'Text'}#公众号界面内的发消息按钮上的文本(其实不是按钮是Grouo组)
            self.ImageExpiredText={'title':'Image expired or deleted','control_type':'Text'}#图片预览窗口内的图片过期或已被删除文本
            self.VideoExpiredText={'title':'Video expired or deleted.','control_type':'Text'}#图片预览窗口内的视频过期或已被删除文本
            self.EarliestOneText={'title':'This is the first one','control_type':'Text'}#图片预览窗口里的这是最早的一张图片文本
            self.ExpiredText={'title':'Expired','control_type':'Text'}#聊天记录列表里点击视频播放按钮后可能出现的过期按钮
            self.DeletedText={'title':'Deleted','control_type':'Text'}#聊天记录列表里点击视频播放按钮后可能出现的已被删除按钮
            self.OfficialAccountsText={'title':'Official Accounts','control_type':'Text','found_index':2}#通讯录中点击公众号选项后右侧主界面的公众号文本
            self.SavePaymentCodeText={'title':'保存收款码','control_type':'Text'}#微信收款助手小账本内点击个人收款码后弹出的经营账户窗口内的保存收款码文本，点击后可以出发保存事件

        if self.language=='繁体中文':
            self.NetWorkError={'title':'網絡不可用，請檢查你的網絡設定','control_type':'Text'}#微信没联网时顶部的红色文本
            self.SearchContactsResult={'title_re':'搜尋','control_type':'Text'}#搜索联系人时的文本结果
            self.ChangeGroupNameWarnText={'title':'僅群組建立者或管理員可以修改','control_type':'Text'}#修改群名时如果有这个文本，无权修改
            self.EditGroupNoticeWarnText={'title':'只有群組建立者及管理員可編輯','control_type':'Text'}#编辑群公告或群名时，如果界面有这个文本，无权编辑
            self.SendMessageShortcutText={'title':'傳送訊息','control_type':'Text'}#发送消息快捷键文本,修改快捷键设置时要用到
            self.CptureScreenShortcutText={'title':'螢幕截圖','control_type':'Text'}#截取屏幕快捷键文本,修改快捷键设置时要用到
            self.OpenWechatShortcutText={'title':'開啟微信','control_type':'Text'}#打开微信快捷键文本,修改快捷键设置时要用到
            self.LockWechatShortcutText={'title':'鎖定微信','control_type':'Text'}#锁定微信快捷键文本,修改快捷键设置时要用到
            self.LanguageText={'title':'語言','control_type':'Text'}#语言文本，修改微信语言时要用到
            self.GroupNameText={'title':'群組名稱','control_type':'Text'}#群聊设置界面内的群聊名称文本
            self.FileDeletedText={'title':'已被刪除','control_type':'Text'}#聊天记录界面内文件过期,已被删除
            self.SaveText={'title':'保存','control_type':'Text'}#聊天记录窗口内选取多个文件,图片,链接,音乐后底部的保存文本
            self.DeleteText={'title':'删除','control_type':'Text'}#聊天记录窗口内选取多个文件,图片,链接,音乐后底部的删除文本
            self.FavoriteText={'title':'收藏','control_type':'Text'}#聊天记录窗口内选取多个文件,图片,链接,音乐后底部的收藏文本
            self.ForwardText={'title':'逐一轉發','control_type':'Text'}#聊天记录窗口内多个选取多个文件,图片链接,音乐后底部的逐一转发文本
            self.CombineForwardText={'title':'合併轉發','control_type':'Text'}#聊天记录窗口内多个选取多个文件,图片链接,音乐后底部的合并转发文本
            self.SendMessageText={'title':'发消息','control_type':'Text'}#公众号界面内的发消息按钮上的文本(其实不是按钮是Grouo组)
            self.ImageExpiredText={'title':'圖片過期或已被刪除','control_type':'Text'}#图片预览窗口内的图片过期或已被删除文本
            self.VideoExpiredText={'title':'影片已逾期或已被刪除','control_type':'Text'}#图片预览窗口内的视频过期或已被删除文本
            self.EarliestOneText={'title':'已是第一張','control_type':'Text'}#图片预览窗口里的这是最早的一张图片文本
            self.ExpiredText={'title':'已過期','control_type':'Text'}#聊天记录列表里点击视频播放按钮后可能出现的过期按钮
            self.DeletedText={'title':'已被刪除','control_type':'Text'}#聊天记录列表里点击视频播放按钮后可能出现的已被删除按钮
            self.OfficialAccountsText={'title':'官方賬號','control_type':'Text','found_index':2}#通讯录中点击公众号选项后右侧主界面的公众号文本
            self.SavePaymentCodeText={'title':'保存收款码','control_type':'Text'}#微信收款助手小账本内点击个人收款码后弹出的经营账户窗口内的保存收款码文本，点击后可以出发保存事件
class TabItems():
    def __init__(self,language=language):
        self.language=language
        if self.language=='简体中文':
            self.ShortCutTabItem={'title':'快捷键','control_type':'TabItem'}#微信设置界面里左侧的快捷键Tabitem
            self.GeneralTabItem={'title':'通用设置','control_type':'TabItem'}#微信设置界面里左侧的通用设置Tabitem
            self.MyAccountTabItem={'title':'账号设置','control_type':'TabItem'}#微信设置界面里左侧的账号设置Tabitem
            self.NotificationsTabItem={'title':'消息通知','control_type':'TabItem'}#微信设置界面里左侧的消息通知Tabitem
            self.FileTabItem={'title':'文件','control_type':'TabItem'}#微信聊天记录界面里顶部的文件Tabitem
            self.PhotoAndVideoTabItem={'title':'图片与视频','control_type':'TabItem'}#微信聊天记录界面里顶部的照片和视频Tabitem
            self.LinkTabItem={'title':'链接','control_type':'TabItem'}#微信聊天记录界面里顶部的链接Tabitem
            self.MiniProgramTabItem={'title':'小程序','control_type':'TabItem'}#微信聊天记录界面里顶部的小程序Tabitem
            self.MusicTabItem={'title':'音乐与音频','control_type':'TabItem'}#微信聊天记录界面里顶部的音乐Tabitem
            self.ChannelTabItem={'title':'视频号','control_type':'TabItem'}#微信聊天记录界面里顶部的视频号Tabitem
            self.DateTabItem={'title':'日期','control_type':'TabItem'}#微信聊天记录界面里顶部的日期TabitemW

        if self.language=='英文':
            self.ShortCutTabItem={'title':'Shortcuts','control_type':'TabItem'}#微信设置界面里左侧的快捷键Tabitem
            self.GeneralTabItem={'title':'General','control_type':'TabItem'}#微信设置界面里左侧的通用设置Tabitem
            self.MyAccountTabItem={'title':'My Account','control_type':'TabItem'}#微信设置界面里左侧的账号设置Tabitem
            self.NotificationsTabItem={'title':'Notifications','control_type':'TabItem'}#微信设置界面里左侧的通知Tabitem
            self.FileTabItem={'title':'Files','control_type':'TabItem'}#微信聊天记录界面里顶部的文件Tabitem
            self.PhotoAndVideoTabItem={'title':'Photos & Videos','control_type':'TabItem'}#微信聊天记录界面里顶部的照片和视频Tabitem
            self.LinkTabItem={'title':'Links','control_type':'TabItem'}#微信聊天记录界面里顶部的链接Tabitem
            self.MiniProgramTabItem={'title':'Mini Programs','control_type':'TabItem'}#微信聊天记录界面里顶部的小程序Tabitem
            self.MusicTabItem={'title':'Music & Audio','control_type':'TabItem'}#微信聊天记录界面里顶部的音乐Tabitem
            self.ChannelTabItem={'title':'Channels','control_type':'TabItem'}#微信聊天记录界面里顶部的视频号Tabitem
            self.DateTabItem={'title':'Date','control_type':'TabItem'}#微信聊天记录界面里顶部的日期TabitemW

        if self.language=='繁体中文':
            self.ShortCutTabItem={'title':'快捷鍵','control_type':'TabItem'}#微信设置界面里左侧的快捷键Tabitem
            self.GeneralTabItem={'title':'一般設定','control_type':'TabItem'}#微信设置界面里左侧的通用设置Tabitem
            self.MyAccountTabItem={'title':'賬號設定','control_type':'TabItem'}#微信设置界面里左侧的账号设置Tabitem
            self.NotificationsTabItem={'title':'訊息通知','control_type':'TabItem'}#微信设置界面里左侧的消息通知Tabitem
            self.FileTabItem={'title':'檔案','control_type':'TabItem'}#微信聊天记录界面里顶部的文件Tabitem
            self.PhotoAndVideoTabItem={'title':'圖片與影片','control_type':'TabItem'}#微信聊天记录界面里顶部的照片和视频Tabitem
            self.LinkTabItem={'title':'連結','control_type':'TabItem'}#微信聊天记录界面里顶部的链接Tabitem
            self.MiniProgramTabItem={'title':'小程式','control_type':'TabItem'}#微信聊天记录界面里顶部的小程序Tabitem
            self.ChannelTabItem={'title':'影音號','control_type':'TabItem'}#微信聊天记录界面里顶部的视频号Tabitem
            self.MusicTabItem={'title':'音樂與音訊','control_type':'TabItem'}#微信聊天记录界面里顶部的音乐Tabitem
            self.DateTabItem={'title':'日期','control_type':'TabItem'}#微信聊天记录界面里顶部的日期Tabitem



class Lists():
    def __init__(self,language=language):
        self.language=language
        if self.language=='简体中文':
            self.ChatHistoryList={'title':'全部','control_type':'List'}#聊天记录窗口中的存放聊天消息的列表
            self.ContactsList={'title':'联系人','control_type':'List'}#通讯录中的联系人列表
            self.ConversationList={'title':'会话','control_type':'List'}#主界面左侧的好友聊天会话列表
            self.FriendChatList={'title':'消息','control_type':'List'}#聊天界面内的消息列表
            self.FileList={'title':'文件','control_type':'List'}#聊天记录窗口中选择文件后的文件列表
            self.PhotoAndVideoList={'title':'图片与视频','control_type':'List'}#微信聊天记录窗口中选择图片与视频后的列表 
            self.LinkList={'title':'链接','control_type':'List'}#微信聊天记录窗口中选择链接后的列表
            self.MiniProgramList={'title':'小程序','control_type':'List'}#微信聊天记录窗口中选择小程序后的列表
            self.MusicList={'title':'音乐','control_type':'List'}#微信聊天记录窗口中选择音乐与音频后的列表
            self.ChannelList={'title':'视频号','control_type':'List'}#微信聊天记录窗口中选择视频号后的列表
            self.SelectContactToAddList={'title':'请勾选需要添加的联系人','control_type':'List'}#微信群聊拉人转发消息界面内搜索好友后的结果列表
            self.ChatList={'title':'聊天成员','control_type':'List'}#群聊设置界面内的聊天成员列表
            self.MomentsList={'title':'朋友圈','control_type':'List'}#朋友圈列表
            self.CommentList={'title':'评论','control_type':'List'}#朋友圈评论列表
        
        if self.language=='英文':
            self.ChatHistoryList={'title':'All','control_type':'List'}#聊天记录页面中的存放聊天消息的列表
            self.ContactsList={'title':'Contacts','control_type':'List'}#通讯录中的联系人列表
            self.ConversationList={'title':'会话','control_type':'List'}#主界面左侧的好友聊天会话列表
            self.FriendChatList={'title':'消息','control_type':'List'}#聊天界面内的消息列表
            self.FileList={'title':'Files','control_type':'List'}#聊天记录窗口中选择文件后的文件列表
            self.PhotoAndVideoList={'title':'Photos & Videos','control_type':'List'}#微信聊天记录窗口中选择图片与视频后的列表 
            self.LinkList={'title':'Links','control_type':'List'}#微信聊天记录窗口中选择链接后的列表
            self.MiniProgramList={'title':'Mini Programs','control_type':'List'}#微信聊天记录窗口中选择小程序后的列表
            self.MusicList={'title':'Music','control_type':'List'}#微信聊天记录窗口中选择音乐与音频后的列表
            self.ChannelList={'title':'Channels','control_type':'List'}#微信聊天记录窗口中选择视频号后的列表 
            self.SelectContactToAddList={'title':'Select contacts to add','control_type':'List'}#微信群聊拉人转发消息界面内搜索好友后的结果列表
            self.ChatList={'title':'Members','control_type':'List'}#群聊设置界面内的聊天成员列表
            self.MomentsList={'title':'Moments','control_type':'List'}#朋友圈列表
            self.CommentList={'title':'Comment','control_type':'List'}#朋友圈评论列表

        if self.language=='繁体中文':
            self.ChatHistoryList={'title':'全部','control_type':'List'}#聊天记录页面中的存放聊天消息的列表
            self.ContactsList={'title':'聯絡人','control_type':'List'}#通讯录中的联系人列表
            self.ConversationList={'title':'会话','control_type':'List'}#主界面左侧的好友聊天会话列表
            self.FriendChatList={'title':'消息','control_type':'List'}#聊天界面内的消息列表
            self.FileList={'title':'檔案','control_type':'List'}#聊天记录窗口中选择文件后的文件列表
            self.PhotoAndVideoList={'title':'圖片與影片','control_type':'List'}#微信聊天记录窗口中选择图片与视频后的列表 
            self.LinkList={'title':'連結','control_type':'List'}#微信聊天记录窗口中选择链接后的列表
            self.MiniProgramList={'title':'小程式','control_type':'List'}#微信聊天记录窗口中选择小程序后的列表
            self.MusicList={'title':'音樂','control_type':'List'}#微信聊天记录窗口中选择音乐与音频后的列表
            self.ChannelList={'title':'影音號','control_type':'List'}#微信聊天记录窗口中选择视频号后的列表
            self.SelectContactToAddList={'title':'請勾選需要新增的聯絡人','control_type':'List'}#微信群聊拉人转发消息界面内搜索好友后的结果列表
            self.ChatList={'title':'聊天室成員','control_type':'List'}#群聊设置界面内的聊天成员列表
            self.MomentsList={'title':'朋友圈','control_type':'List'}#朋友圈列表
            self.CommentList={'title':'評論','control_type':'List'}#朋友圈评论列表

class Panes():
    def __init__(self,language=language):
        self.language=language
        if self.language=='简体中文':
            self.FriendProfilePane={'class_name':'ContactProfileWnd','control_type':'Pane','framework_id':'Win32'}#好友设置界面里点击头像后出现的个人简介界面
            self.ApprovalPane={'title':'新建标签','class_name':'WeUIDialog','control_type':'Pane'}#群主开启邀请好友须通过群主或管理员同意的验证消息框
            self.ContactsManagePane={'title':'全部','control_type':'Pane'}#通讯录管理界面内的全部Pane,之所以用到它是为了获取这个Pane下的总人数
            self.ConfirmPane={'title':'','class_name':'WeUIDialog','control_type':'Pane'}#通用的确认框
            self.ChangeShortcutPane={'title':'','control_type':'Pane','class_name':'SetAcceleratorWnd'}#修改快捷键时弹出的框
            self.ChatContaceMenuPane={'title':'ChatContactMenu','class_name':'ChatContactMenu','control_type':'Pane','framework_id':'Win32'}#群聊输入@+好友名字时弹出的选择聊天记录的列表
            self.VideoPlayerPane={'title':'player video','control_type':'Pane'}#图片预览窗口内的视频播放器pane
            self.VideoPane={'title':'视频','control_type':'Pane'}#朋友圈视频窗格,只有好友朋友圈内容是视频才有这个窗格
        
        if self.language=='英文':
            self.FriendProfilePane={'class_name':'ContactProfileWnd','control_type':'Pane','framework_id':'Win32'}#好友设置界面里点击头像后出现的个人简介界面
            self.ApprovalPane={'title':'New Tag','class_name':'WeUIDialog','control_type':'Pane'}#群主开启邀请好友须通过群主或管理员同意的验证消息框
            self.ContactsManagePane={'title':'All','control_type':'Pane'}#通讯录管理界面内的全部Pane,之所以用到它是为了获取这个Pane下的总人数
            self.ConfirmPane={'title':'','class_name':'WeUIDialog','control_type':'Pane'}#通用的确认框
            self.ChangeShortcutPane={'title':'','control_type':'Pane','class_name':'SetAcceleratorWnd'}#修改快捷键时弹出的框
            self.ChatContaceMenuPane={'title':'ChatContactMenu','class_name':'ChatContactMenu','control_type':'Pane','framework_id':'Win32'}#群聊输入@+好友名字时弹出的选择聊天记录的列表
            self.VideoPlayerPane={'title':'player video','control_type':'Pane'}#图片预览窗口内的视频播放器pane
            self.VideoPane={'title':'video call','control_type':'Pane'}#朋友圈视频窗格,只有好友朋友圈内容是视频才有这个窗格

        if self.language=='繁体中文':
            self.FriendProfilePane={'class_name':'ContactProfileWnd','control_type':'Pane','framework_id':'Win32'}#好友设置界面里点击头像后出现的个人简介界面
            self.ApprovalPane={'title':'新建標籤','class_name':'WeUIDialog','control_type':'Pane'}#群主开启邀请好友须通过群主或管理员同意的验证消息框
            self.ContactsManagePane={'title':'全部','control_type':'Pane'}#通讯录管理界面内的全部Pane,之所以用到它是为了获取这个Pane下的总人数
            self.ConfirmPane={'title':'','class_name':'WeUIDialog','control_type':'Pane'}#通用的确认框
            self.ChangeShortcutPane={'title':'','control_type':'Pane','class_name':'SetAcceleratorWnd'}#修改快捷键时弹出的框
            self.ChatContaceMenuPane={'title':'ChatContactMenu','class_name':'ChatContactMenu','control_type':'Pane','framework_id':'Win32'}#群聊输入@+好友名字时弹出的选择聊天记录的列表
            self.VideoPlayerPane={'title':'player video','control_type':'Pane'}#图片预览窗口内的视频播放器pane
            self.VideoPane={'title':'影片','control_type':'Pane'}#朋友圈视频窗格,只有好友朋友圈内容是视频才有这个窗格


class Menus():
    def __init__(self,language=language):
        self.language=language
        if self.language=='简体中文':
            self.RightClickMenu={'title':'','control_type':'Menu','class_name':'CMenuWnd','framework_id':'Win32'}#微信聊天界面和聊天记录窗口内右键后弹出的菜单
            self.FriendProfileMenu={'title':'','control_type':'Menu','class_name':'CMenuWnd','framework_id':'Win32'}#好友个人简介界面内点击三个点之后弹出的菜单
        if self.language=='英文':
            self.RightClickMenu={'title':'','control_type':'Menu','class_name':'CMenuWnd','framework_id':'Win32'}#微信聊天界面和聊天记录窗口内右键后弹出的菜单
            self.FriendProfileMenu={'title':'','control_type':'Menu','class_name':'CMenuWnd','framework_id':'Win32'}#好友个人简介界面内点击三个点之后弹出的菜单
        if self.language=='繁体中文':
            self.RightClickMenu={'title':'','control_type':'Menu','class_name':'CMenuWnd','framework_id':'Win32'}#微信聊天界面和聊天记录窗口内右键后弹出的菜单
            self.FriendProfileMenu={'title':'','control_type':'Menu','class_name':'CMenuWnd','framework_id':'Win32'}#好友个人简介界面内点击三个点之后弹出的菜单
           


class MenuItems():
    def __init__(self,language=language):
        self.language=language
        if self.language=='简体中文':
            self.ForwardMenuItem={'title':'转发...','control_type':'MenuItem'}#右键后的转发消息MenuItem
            self.SetPrivacyMenuItem={'title':'设置朋友权限','control_type':'MenuItem'}#好友设置菜单栏里的设置朋友权限
            self.StarMenuItem={'title':'设为星标朋友','control_type':'MenuItem'}#好友设置菜单栏里的设为星标朋友
            self.BlockMenuItem={'title':'加入黑名单','control_type':'MenuItem'}#好友设置菜单栏里的加入黑名单
            self.EditContactMenuItem={'title':'设置备注和标签','control_type':'MenuItem'}#好友设置菜单栏里的设置备注和标签
            self.ShareContactMenuItem={'found_index':2,'control_type':'MenuItem'}#好友设置菜单栏里的推荐给朋友，这里使用title_re因为实际上中文版中微信是会根据性别来决定这个控件名称
            self.DeleteContactMenuItem={'title':'删除联系人','control_type':'MenuItem'}#好友设置菜单栏里的删除好友
            self.UnBlockMenuItem={'title':'移出黑名单','control_type':'MenuItem'}#好友设置菜单栏里的移出黑名单
            self.UnStarMenuItem={'title':'不再设为星标朋友','control_type':'MenuItem'}#好友设置菜单栏里的不再设为星标朋友
            self.Tickle={'title':'拍一拍','control_type':'MenuItem'}#拍一拍好友
            self.CopyMenuItem={'title':'复制','control_type':'MenuItem'}#右键菜单里的复制消息
            self.SaveMenuItem={'title_re':'另存为','control_type':'MenuItem'}#右键图片视频或文件时菜单里的另存为
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
            self.ShowInFolderMenuItem={'title':'在文件夹中显示','control_type':'MenuItem'}#邮件消息文件消息后的在文件夹中显示
            self.EnterLedgerMenuItem={'title':'进入小账本','control_type':'MenuItem'}
            self.PaymentRecordsMenuItem={'title':'收款记录','control_type':'MenuItem'}


        if self.language=='英文':
            self.SetPrivacyMenuItem={'title':'Set Privacy','control_type':'MenuItem'}#好友设置菜单栏里的设置朋友权限
            self.StarMenuItem={'title':'Star','control_type':'MenuItem'}#好友设置菜单栏里的设为星标朋友
            self.BlockMenuItem={'title':'Block','control_type':'MenuItem'}#好友设置菜单栏里的加入黑名单
            self.EditContactMenuItem={'title':'Edit Contact','control_type':'MenuItem'}#好友设置菜单栏里的设置备注和标签
            self.ShareContactMenuItem={'found_index':2,'control_type':'MenuItem'}#好友设置菜单栏里的推荐给朋友，这里使用title_re因为实际上中文版中微信是会根据性别来决定这个控件名称
            self.DeleteContactMenuItem={'title':'Delete Contact','control_type':'MenuItem'}#好友设置菜单栏里的删除好友
            self.UnBlockMenuItem={'title':'Unblock','control_type':'MenuItem'}#好友设置菜单栏里的移出黑名单
            self.UnStarMenuItem={'title':'Unstar','control_type':'MenuItem'}#好友设置菜单栏里的不再设为星标朋友
            self.Tickle={'title':'Tickle','control_type':'MenuItem'}#拍一拍好友
            self.CopyMenuItem={'title':'Copy','control_type':'MenuItem'}#右键菜单里的复制消息
            self.SaveMenuItem={'title_re':'Save as','control_type':'MenuItem'}#右键图片视频或文件后菜单里的另存为
            self.ForwardMenuItem={'title':'Forward...','control_type':'MenuItem'}#右键消息后的转发选项
            self.AddToFavoritesMenuItem={'title':'Add to Favorites','control_type':'MenuItem'}#右键消息后的添加到收藏夹选项
            self.TranslateMenuItem={'title':'Translate','control_type':'MenuItem'}#右键文本消息后的翻译选项
            self.EditMenuItem={'title':'Edit','control_type':'MenuItem'}#右键图片后的编辑选项
            self.DeleteMenuItem={'title':'Delete','control_type':'MenuItem'}#右键消息后的删除选项
            self.SearchMenuItem={'title':'Search','control_type':'MenuItem'}#右键消息后的搜索选项
            self.QuoteMeunItem={'title':'Quote','control_type':'MenuItem'}#右键消息后的引用选项
            self.SelectMenuItem={'title':'Select...','control_type':'MenuItem'}#右键消息后的多选选项
            self.EnlargeMeunItem={'title':'Enlarge','control_type':'MenuItem'}#右键消息后的放大选项
            self.FindInChatMenuItem={'title':'Find in Chat','control_type':'MenuItem'}#聊天记录页面内右键消息后的Find in chat选项
            self.OpenWithDefaultBrowser={'title':'OpenWithDefaultBrowser','control_type':'MenuItem'}#聊天记录页面内Link类型的消息后的使用默认浏览器打开
            self.ShowInFolderMenuItem={'title':'Show in folder','control_type':'MenuItem'}#右键消息文件消息后的在文件夹中显示
            self.EnterLedgerMenuItem={'title':'进入小账本','control_type':'MenuItem'}
            self.PaymentRecordsMenuItem={'title':'收款记录','control_type':'MenuItem'}

        if self.language=='繁体中文':
            self.SetPrivacyMenuItem={'title':'設定朋友權限','control_type':'MenuItem'}#好友设置菜单栏里的设置朋友权限
            self.StarMenuItem={'title':'設為超級好友','control_type':'MenuItem'}#好友设置菜单栏里的设为星标朋友
            self.BlockMenuItem={'title':'加入黑名單','control_type':'MenuItem'}#好友设置菜单栏里的加入黑名单
            self.EditContactMenuItem={'title':'設定備註和標籤','control_type':'MenuItem'}#好友设置菜单栏里的设置备注和标签
            self.ShareContactMenuItem={'found_index':2,'control_type':'MenuItem'}#好友设置菜单栏里的推荐给朋友，这里使用title_re因为实际上中文版中微信是会根据性别来决定这个控件名称
            self.DeleteContactMenuItem={'title':'刪除聯絡人','control_type':'MenuItem'}#好友设置菜单栏里的删除好友
            self.UnBlockMenuItem={'title':'移除黑名單','control_type':'MenuItem'}#好友设置菜单栏里的移出黑名单
            self.UnStarMenuItem={'title':'不再設為超級好友','control_type':'MenuItem'}#好友设置菜单栏里的不再设为星标朋友
            self.Tickle={'title':'拍一拍','control_type':'MenuItem'}#拍一拍好友
            self.CopyMenuItem={'title':'複製','control_type':'MenuItem'}#右键菜单里的复制消息
            self.SaveMenuItem={'title_re':'另存為','control_type':'MenuItem'}#右键图片视频或文件时菜单里的另存为
            self.ForwardMenuItem={'title':'轉發...','control_type':'MenuItem'}#右键后的转发消息
            self.AddToFavoritesMenuItem={'title':'收藏','control_type':'MenuItem'}#添加到收藏夹
            self.TranslateMenuItem={'title':'翻譯','control_type':'MenuItem'}#右键文本消息后的翻译选项
            self.EditMenuItem={'title':'編輯','control_type':'MenuItem'}#右键图片后的编辑选项
            self.DeleteMenuItem={'title':'刪除','control_type':'MenuItem'}#右键消息后的删除选项
            self.SearchMenuItem={'title':'搜一搜','control_type':'MenuItem'}#右键消息后的搜索选项
            self.QuoteMeunItem={'title':'引用','control_type':'MenuItem'}#右键消息后的引用选项
            self.SelectMenuItem={'title':'多選','control_type':'MenuItem'}#右键消息后的多选选项
            self.EnlargeMeunItem={'title':'放大閱讀','control_type':'MenuItem'}#右键消息后的放大选项
            self.FindInChatMenuItem={'title':'定位到聊天位置','control_type':'MenuItem'}#聊天记录页面内右键消息后的Find in chat选项
            self.OpenWithDefaultBrowser={'title':'使用預設瀏覽器開啟','control_type':'MenuItem'}#聊天记录页面内Link类型的消息后的使用默认浏览器打开
            self.ShowInFolderMenuItem={'title':'在資料夾中顯示','control_type':'MenuItem'}#右键消息文件后的在文件夹中显示选项
            self.EnterLedgerMenuItem={'title':'进入小账本','control_type':'MenuItem'}
            self.PaymentRecordsMenuItem={'title':'收款记录','control_type':'MenuItem'}

class CheckBoxes():
    def __init__(self,language=language):
        self.language=language
        if self.language=='简体中文':
            self.ChatsOnlyCheckBox={'found_index':1,'control_type':'CheckBox'}#修改好友权限时的仅聊天选项
            self.OpenChatCheckBox={'found_index':0,'control_type':'CheckBox'}#修改好友权限时的聊天、朋友圈、微信运动等选项
            self.HideMyPostsCheckBox={'title':'','control_type':'CheckBox','found_index':0}#修改好友权限时的不给他看选项
            self.HideTheirPostsCheckBox={'title':'','control_type':'CheckBox','found_index':1}#修改好友权限时的不看他选项
            self.OnScreenNamesCheckBox={'title':'显示群成员昵称','control_type':'CheckBox'}#显示群成员昵称
            self.MuteNotificationsCheckBox={'title':'消息免打扰','control_type':'CheckBox'}#消息免打扰
            self.StickyonTopCheckBox={'title':'置顶聊天','control_type':'CheckBox'}#置顶聊天
            self.SavetoContactsCheckBox={'title':'保存到通讯录','control_type':'CheckBox'}#保存至通讯录

        if self.language=='英文':
            self.ChatsOnlyCheckBox={'found_index':1,'control_type':'CheckBox'}#修改好友权限时的仅聊天选项
            self.OpenChatCheckBox={'found_index':0,'control_type':'CheckBox'}#修改好友权限时的聊天、朋友圈、微信运动等选项
            self.OnScreenNamesCheckBox={'title':'On-Screen Names','control_type':'CheckBox'}#显示裙成员昵称
            self.MuteNotificationsCheckBox={'title':'Mute Notifications','control_type':'CheckBox'}#消息免打扰
            self.StickyonTopCheckBox={'title':'Sticky on Top','control_type':'CheckBox'}#置顶聊天
            self.SavetoContactsCheckBox={'title':'Save to Contacts','control_type':'CheckBox'}#保存至通讯录
            self.HideMyPostsCheckBox={'title':'','control_type':'CheckBox','found_index':0}#修改好友权限时的不给他看选项
            self.HideTheirPostsCheckBox={'title':'','control_type':'CheckBox','found_index':1}#修改好友权限时的不看他选项

        if self.language=='繁体中文':
            self.ChatsOnlyCheckBox={'found_index':1,'control_type':'CheckBox'}#修改好友权限时的仅聊天选项
            self.OpenChatCheckBox={'found_index':0,'control_type':'CheckBox'}#修改好友权限时的聊天、朋友圈、微信运动等选项
            self.HideMyPostsCheckBox={'title':'','control_type':'CheckBox','found_index':0}#修改好友权限时的不给他看选项
            self.HideTheirPostsCheckBox={'title':'','control_type':'CheckBox','found_index':1}#修改好友权限时的不看他选项
            self.OnScreenNamesCheckBox={'title':'顯示成員在群組的暱稱','control_type':'CheckBox'}#显示群成员昵称
            self.MuteNotificationsCheckBox={'title':'消息免打擾','control_type':'CheckBox'}#消息免打扰
            self.StickyonTopCheckBox={'title':'置頂聊天','control_type':'CheckBox'}#置顶聊天
            self.SavetoContactsCheckBox={'title':'保存到通訊錄','control_type':'CheckBox'}#保存至通讯录


class Windows():
    def __init__(self,language=language):
        self.language=language
        if self.language=='简体中文':
            self.EditPrivacyWindow={'title':'朋友权限','class_name':'WeUIDialog','framework_id':'Win32'}#设置好友权限窗口
            self.OfficialAccountWindow={'title':'公众号','class_name':'H5SubscriptionProfileWnd','control_type':'Window'}#公众号窗口
            self.LargeGroupInvitationApprovalWindow={'class_name':'ConfirmDialog','control_type':'Window','framework_id':'Win32'}#群聊人数较多拉好友进群时需要确认的窗口
            self.OfficialAccountChatWindow={'class_name':'ChatWnd','control_type':'Window','framework_id':'Win32'}#公众号聊天窗口
            self.EditContactWindow={'title':'设置备注和标签','class_name':'WeUIDialog','framework_id':'Win32'}#设置好友备注和标签的窗口
            self.SettingsMenu={'class_name':'SetMenuWnd','control_type':'Window'}#设置与其他按钮按下后的菜单栏
            self.DeleteMemberWindow={'title':'DeleteMemberWnd','control_type':'Window','framework_id':'Win32'}#群聊踢人面板
            self.AddMemberWindow={'title':'AddMemberWnd','control_type':'Window','framework_id':'Win32'}#群聊拉人面板
            self.SelectContactWindow={'title':'','control_type':'Window','class_name':'SelectContactWnd','framework_id':'Win32'}#转发消息时或推荐名片时的选择好友面板
            self.NativeSaveFileWindow={'title_re':'另存为','control_type':'Window','framework_id':'Win32','top_level_only':False}#保存文件时的窗口
            self.FileSaveConfirmWindow={'class_name':'FileSaveConfirmWnd','control_type':'Window'}#在聊天记录窗口里多选图片并点击保存后弹出的确认窗口
            self.NativeChooseFolderWindow={'control_type':'Window','framework_id':'Win32','top_level_only':False,'found_index':0}#在聊天记录窗口里点击保存并确认后弹出的windows本地选择文件夹窗口
            self.ImagePreviewWindow={'control_type':'Window','class_name':'ImagePreviewWnd','framework_id':'Win32'}#图片预览窗口

        if self.language=='英文':
            self.EditPrivacyWindow={'title':'Privacy','class_name':'WeUIDialog','framework_id':'Win32'}#设置好友权限窗口
            self.EditContactWindow={'title':'Edit Contact','class_name':'WeUIDialog','framework_id':'Win32'}#设置好友备注和标签的窗口
            self.OfficialAccountWindow={'title':'Official Accounts','class_name':'H5SubscriptionProfileWnd','control_type':'Window'}#公众号窗口
            self.OfficialAccountChatWindow={'class_name':'ChatWnd','control_type':'Window','framework_id':'Win32'}#公众号聊天窗口
            self.LargeGroupInvitationApprovalWindow={'class_name':'ConfirmDialog','control_type':'Window','framework_id':'Win32'}#群聊人数较多拉好友进群时需要确认的窗口
            self.SettingsMenu={'class_name':'SetMenuWnd','control_type':'Window'}#设置与其他按钮按下后的菜单栏
            self.DeleteMemberWindow={'title':'DeleteMemberWnd','control_type':'Window','framework_id':'Win32'}#群聊踢人面板
            self.AddMemberWindow={'title':'AddMemberWnd','control_type':'Window','framework_id':'Win32'}#群聊拉人面板
            self.SelectContactWindow={'title':'','control_type':'Window','class_name':'SelectContactWnd','framework_id':'Win32'}#转发消息时或推荐名片时的选择好友面板
            self.NativeSaveFileWindow={'title_re':'Save as','control_type':'Window','framework_id':'Win32','top_level_only':False}#保存文件时的窗口
            self.FileSaveConfirmWindow={'class_name':'FileSaveConfirmWnd','control_type':'Window'}#在聊天记录窗口里多选图片并点击保存后弹出的确认窗口
            self.NativeChooseFolderWindow={'control_type':'Window','framework_id':'Win32','top_level_only':False,'found_index':0}#在聊天记录窗口里点击保存并确认后弹出的windows本地选择文件夹窗口
            self.ImagePreviewWindow={'control_type':'Window','class_name':'ImagePreviewWnd','framework_id':'Win32'}#图片预览窗口

        if self.language=='繁体中文':
            self.EditPrivacyWindow={'title':'修改權限','class_name':'WeUIDialog','framework_id':'Win32'}#设置好友权限窗口
            self.EditContactWindow={'title':'設定備註和標籤','class_name':'WeUIDialog','framework_id':'Win32'}#设置好友备注和标签的窗口
            self.OfficialAccountWindow={'title':'官方賬號','class_name':'H5SubscriptionProfileWnd','control_type':'Window'}#公众号窗口
            self.OfficialAccountChatWindow={'class_name':'ChatWnd','control_type':'Window','framework_id':'Win32'}#公众号聊天窗口
            self.LargeGroupInvitationApprovalWindow={'class_name':'ConfirmDialog','control_type':'Window','framework_id':'Win32'}#群聊人数较多拉好友进群时需要确认的窗口
            self.SettingsMenu={'class_name':'SetMenuWnd','control_type':'Window'}#设置与其他按钮按下后的菜单栏
            self.DeleteMemberWindow={'title':'DeleteMemberWnd','control_type':'Window','framework_id':'Win32'}#群聊踢人面板
            self.AddMemberWindow={'title':'AddMemberWnd','control_type':'Window','framework_id':'Win32'}#群聊拉人面板
            self.SelectContactWindow={'title':'','control_type':'Window','class_name':'SelectContactWnd','framework_id':'Win32'}#转发消息时或推荐名片时的选择好友面板
            self.NativeSaveFileWindow={'title_re':'另存為','control_type':'Window','framework_id':'Win32','top_level_only':False}#保存文件时的窗口
            self.FileSaveConfirmWindow={'class_name':'FileSaveConfirmWnd','control_type':'Window'}#在聊天记录窗口里多选图片并点击保存后弹出的确认窗口
            self.NativeChooseFolderWindow={'control_type':'Window','framework_id':'Win32','top_level_only':False,'found_index':0}#在聊天记录窗口里点击保存并确认后弹出的windows本地选择文件夹窗口
            self.ImagePreviewWindow={'control_type':'Window','class_name':'ImagePreviewWnd','framework_id':'Win32'}#图片预览窗口



class ListItems():
    def __init__(self,language=language):
        self.language=language
        if self.language=='简体中文':
            self.MentionAllListItem={'title':'所有人','control_type':'ListItem'}#@所有人时出现的所有人选项
            self.AddListItem={'title':'添加','control_type':'ListItem'}#群聊设置界面内的添加按钮，只有群主和管理员可以看到
            self.RemoveListItem={'title':'移除','control_type':'ListItem'}#群聊设置界面内的移除按钮，只有群主和管理员可以看到
            self.OfficialAccountsListItem={'title':'公众号','control_type':'ListItem'}#通讯录列表里的公众号选项
            self.NewFriendsListItem={'title':'新的朋友','control_type':'ListItem'}#通讯录列表内新的朋友选项

        if self.language=='繁体中文': 
            self.MentionAllListItem={'title':'所有人','control_type':'ListItem'}
            self.AddListItem={'title':'新增','control_type':'ListItem'}#群聊设置界面内的添加按钮，只有群主和管理员可以看到
            self.RemoveListItem={'title':'移出','control_type':'ListItem'}#群聊设置界面内的移除按钮，只有群主和管理员可以看到
            self.OfficialAccountsListItem={'title':'官方賬號','control_type':'ListItem'}#通讯录列表里的公众号选项
            self.NewFriendsListItem={'title':'新的朋友','control_type':'ListItem'}#通讯录列表内新的朋友选项

        if self.language=='英文':
            self.MentionAllListItem={'title':'Mention All','control_type':'ListItem'} 
            self.AddListItem={'title':'Add','control_type':'ListItem'}#群聊设置界面内的添加按钮，只有群主和管理员可以看到
            self.RemoveListItem={'title':'Remove','control_type':'ListItem'}#群聊设置界面内的移除按钮，只有群主和管理员可以看到
            self.OfficialAccountsListItem={'title':'Official Accounts','control_type':'ListItem'}#通讯录列表里的公众号选项
            self.NewFriendsListItem={'title':'New Friends','control_type':'ListItem'}#通讯录列表内新的朋友选项


class Login_window():
    '''登录界面要用到的唯二的两个Ui:登录界面与进入微信按钮\n'''
    def __init__(self,language=language):
        self.language=language
        if self.language=='简体中文':
            self.LoginWindow={'title':'微信','class_name':'WeChatLoginWndForPC','visible_only':False}#登录微信界面
            self.LoginButton={'control_type':'Button','title':'进入微信'}#进入微信按钮

        if self.language=='英文':
            self.LoginWindow={'title':'Weixin','class_name':'WeChatLoginWndForPC','visible_only':False}#登录微信界面
            self.LoginButton={'control_type':'Button','title':'Enter Weixin'}#进入微信按钮

        if self.language=='繁体中文':
            self.LoginWindow={'title':'微信','class_name':'WeChatLoginWndForPC','visible_only':False}#登录微信界面
            self.LoginButton={'control_type':'Button','title':'進入微信'}#进入微信按钮



class Main_window():
    '''主界面下所有的第一级Ui\n'''
    def __init__(self,language=language):
        self.language=language
        if self.language=='简体中文':
            self.MySelfButton={'control_type':'Button','found_index':0}#主界面下的第一个按钮,也就是我自己的头像按钮，必须通过main_window.child_window(**Main_window().MySelfButton)使用!
            self.AddTalkMemberWindow={'title':'AddTalkMemberWnd','control_type':'Window','class_name':'AddTalkMemberWnd','framework_id':'Win32'}#添加新朋友时弹出的窗口
            self.MainWindow={'title':'微信','class_name':'WeChatMainWndForPC'}#微信主界面
            self.Toolbar={'title':'导航','control_type':'ToolBar'}#主界面左侧的侧边栏
            self.ConversationList={'title':'会话','control_type':'List'}#主界面左侧会话列表
            self.Search={'title':'搜索','control_type':'Edit','found_index':0}#主界面顶部的搜索栏
            self.SearchResult={'title_re':"@str:IDS_FAV_SEARCH_RESULT",'control_type':'List'}#主界面顶部搜索栏搜索内容的结果列表
            self.ChatToolBar={'title':'','found_index':0,'control_type':'ToolBar'}#主界面右侧聊天窗口内的工具栏(语音视频按钮在其中)
            self.CurrentChatWindow={'control_type':'Edit','found_index':1}#主界面右侧的聊天窗口
            self.ProfileWindow={'class_name':"ContactProfileWnd",'control_type':'Pane','framework_id':'Win32'}#从聊天区域打开的好友信息面板
            self.FriendMenu={'control_type':'Menu','title':'','class_name':'CMenuWnd','framework_id':'Win32'}#从聊天区域打开的好友信息面板内右上角三个点点击后的菜单栏
            self.FriendSettingsWindow={'class_name':'SessionChatRoomDetailWnd','control_type':'Pane','framework_id':'Win32'}#好友设置界面
            self.GroupSettingsWindow={'class_name':'SessionChatRoomDetailWnd','control_type':'Pane','framework_id':'Win32'}#群聊设置界面    
            self.SettingsMenu={'class_name':'SetMenuWnd','control_type':'Window'}#设置与其他按钮按下后的菜单栏
            self.ContactsList={'title':'联系人','control_type':'List'}#主界面切换至联系人后的联系人列表
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

        if self.language=='英文':
            self.MySelfButton={'control_type':'Button','found_index':0}#主界面下的第一个按钮,也就是我自己的头像按钮，必须通过main_window.child_window(**Main_window().MySelfButton)使用!
            self.AddTalkMemberWindow={'title':'AddTalkMemberWnd','control_type':'Window','class_name':'AddTalkMemberWnd','framework_id':'Win32'}#添加新朋友时弹出的窗口
            self.MainWindow={'title':'Weixin','class_name':'WeChatMainWndForPC'}#微信主界面
            self.Toolbar={'title':'Navigation','control_type':'ToolBar'}#主界面左侧侧边栏
            self.ConversationList={'title':'会话','control_type':'List'}#主界面左侧会话列表
            self.Search={'title':'Search','control_type':'Edit','found_index':0}#主界面顶部的搜索栏
            self.SearchResult={'title_re':"@str:IDS_FAV_SEARCH_RESULT",'control_type':'List'}#主界面顶部搜索栏搜索内容的结果列表
            self.ChatToolBar={'title':'','found_index':0,'control_type':'ToolBar'}#主界面右侧聊天窗口内的工具栏(语音视频按钮在其中)
            self.CurrentChatWindow={'control_type':'Edit','found_index':1}#主界面右侧的聊天窗口
            self.ProfileWindow={'class_name':"ContactProfileWnd",'control_type':'Pane','framework_id':'Win32'}#从聊天区域打开的好友信息面板
            self.FriendMenu={'control_type':'Menu','title':'','class_name':'CMenuWnd','framework_id':'Win32'}#从聊天区域打开的好友信息面板内右上角三个点点击后的菜单栏
            self.FriendSettingsWindow={'class_name':'SessionChatRoomDetailWnd','control_type':'Pane','framework_id':'Win32'}#好友设置界面
            self.GroupSettingsWindow={'class_name':'SessionChatRoomDetailWnd','control_type':'Pane','framework_id':'Win32'}#群聊设置界面 
            self.SettingsMenu={'class_name':'SetMenuWnd','control_type':'Window'}#设置与其他按钮按下后的菜单栏
            self.ContactsList={'title':'Contacts','control_type':'List'}#主界面切换至联系人后的联系人列表
            self.SearchNewFriendBar={'title':'Weixin ID/Mobile','control_type':'Edit'}#添加好友时顶部搜索栏名称
            self.SearchNewFriendResult={'title_re':'@str:IDS_FAV_SEARCH_RESULT','control_type':'List'}#添加新朋友时的搜索结果
            self.AddFriendRequestWindow={'title':'Friend Request','class_name':'WeUIDialog','control_type':'Window','framework_id':'Win32'}#添加朋友请求窗口
            self.AddMemberWindow={'title':'AddMemberWnd','control_type':'Window','framework_id':'Win32'}#群聊拉人面板
            self.DeleteMemberWindow={'title':'DeleteMemberWnd','control_type':'Window','framework_id':'Win32'}#群聊踢人面板
            self.Tickle={'title':'Tickle','control_type':'MenuItem'}#拍一拍好友
            self.SelectContactWindow={'title':'','control_type':'Window','class_name':'SelectContactWnd','framework_id':'Win32'}#转发消息时或推荐名片时的选择好友面板
            self.SetTag={'title':'Tag','framework_id':'Win32','class_name':'StandardConfirmDialog'}#设置好友标签窗口
            self.FriendChatList={'title':'消息','control_type':'List'}#主界面内右侧聊天区域内与好友的消息列表
            self.SearchContactsResult={'title_re':'Search','control_type':'Text'}#推荐好友面板内搜索结果

        if self.language=='繁体中文':
            self.MySelfButton={'control_type':'Button','found_index':0}#主界面下的第一个按钮,也就是我自己的头像按钮，必须通过main_window.child_window(**Main_window().MySelfButton)使用!
            self.AddTalkMemberWindow={'title':'AddTalkMemberWnd','control_type':'Window','class_name':'AddTalkMemberWnd','framework_id':'Win32'}#添加新朋友时弹出的窗口
            self.MainWindow={'title':'微信','class_name':'WeChatMainWndForPC'}#微信主界面
            self.Toolbar={'title':'導航','control_type':'ToolBar'}#主界面左侧的侧边栏
            self.ConversationList={'title':'会话','control_type':'List'}#主界面左侧会话列表
            self.Search={'title':'搜尋','control_type':'Edit','found_index':0}#主界面顶部的搜索栏
            self.SearchResult={'title_re':"@str:IDS_FAV_SEARCH_RESULT",'control_type':'List'}#主界面顶部搜索栏搜索内容的结果列表
            self.ChatToolBar={'title':'','found_index':0,'control_type':'ToolBar'}#主界面右侧聊天窗口内的工具栏(语音视频按钮在其中)
            self.CurrentChatWindow={'control_type':'Edit','found_index':1}#主界面右侧的聊天窗口
            self.ProfileWindow={'class_name':"ContactProfileWnd",'control_type':'Pane','framework_id':'Win32'}#从聊天区域打开的好友信息面板
            self.FriendMenu={'control_type':'Menu','title':'','class_name':'CMenuWnd','framework_id':'Win32'}#从聊天区域打开的好友信息面板内右上角三个点点击后的菜单栏
            self.FriendSettingsWindow={'class_name':'SessionChatRoomDetailWnd','control_type':'Pane','framework_id':'Win32'}#好友设置界面
            self.GroupSettingsWindow={'class_name':'SessionChatRoomDetailWnd','control_type':'Pane','framework_id':'Win32'}#群聊设置界面    
            self.SettingsMenu={'class_name':'SetMenuWnd','control_type':'Window'}#设置与其他按钮按下后的菜单栏
            self.ContactsList={'title':'聯絡人','control_type':'List'}#主界面切换至联系人后的联系人列表
            self.SearchNewFriendBar={'title':'微信 ID/手機號碼','control_type':'Edit'}#添加好友时顶部搜索栏名称
            self.SearchNewFriendResult={'title_re':'@str:IDS_FAV_SEARCH_RESULT','control_type':'List'}#添加新朋友时的搜索结果
            self.AddFriendRequestWindow={'title':'添加朋友请求','class_name':'WeUIDialog','control_type':'Window','framework_id':'Win32'}#添加朋友请求窗口
            self.AddMemberWindow={'title':'AddMemberWnd','control_type':'Window','framework_id':'Win32'}#群聊拉人面板
            self.DeleteMemberWindow={'title':'DeleteMemberWnd','control_type':'Window','framework_id':'Win32'}#群聊踢人面板
            self.Tickle={'title':'拍一拍','control_type':'MenuItem'}#拍一拍好友
            self.SelectContactWindow={'title':'','control_type':'Window','class_name':'SelectContactWnd','framework_id':'Win32'}#转发消息时或推荐名片时的选择好友面板
            self.SetTag={'title':'設定標籤','framework_id':'Win32','class_name':'StandardConfirmDialog'}#设置好友标签窗口
            self.FriendChatList={'title':'消息','control_type':'List'}#主界面右侧聊天区域内与好友的消息列表
            self.SearchContactsResult={'title_re':'搜尋','control_type':'Text'}#推荐好友面板内搜索结果



class SideBar():
    '''主界面侧边栏下的所有Ui'''
    def __init__(self,language=language):
        self.language=language
        if self.language=='简体中文':
            self.Chats={'title':'聊天','control_type':'Button'}#主界面左侧的聊天按钮
            self.Contacts={'title':'通讯录','control_type':'Button'}#主界面左侧的通讯录按钮
            self.Collections={'title':'收藏','control_type':'Button'}#主界面左侧的收藏按钮
            self.ChatFiles={'title':'聊天文件','control_type':'Button'}#主界面左侧的聊天文件按钮
            self.Moments={'title':'朋友圈','control_type':'Button'}#主界面左侧的朋友圈按钮
            self.Channel={'found_index':6,'control_type':'Button'}#主界面左侧的视频号按钮,z之所以用found_index是因为视频号的新消息提示会覆盖掉视频号按钮的名字
            self.Topstories={'title':'看一看','control_type':'Button'}#主界面左侧的看一看按钮
            self.Search={'title':'搜一搜','control_type':'Button'}#主界面左侧的搜一搜按钮
            self.Miniprogram_pane={'title':'小程序面板','control_type':'Button'}#主界面左侧的小程序面板按钮
            self.SettingsAndOthers={'title':'设置及其他','control_type':'Button'} #主界面左侧的设置及其他按钮 

        if self.language=='英文':
            self.Chats={'title':'Chats','control_type':'Button'}#主界面左侧的聊天按钮
            self.Contacts={'title':'Contacts','control_type':'Button'}#主界面左侧的通讯录按钮
            self.Collections={'title':'Favorites','control_type':'Button'}#主界面左侧的收藏按钮
            self.ChatFiles={'title':'Chat Files','control_type':'Button'}#主界面左侧的聊天文件按钮
            self.Moments={'title':'Moments','control_type':'Button'}#主界面左侧的朋友圈按钮
            self.Channel={'found_index':6,'control_type':'Button'}#主界面左侧的视频号按钮,z之所以用found_index是因为视频号的新消息提示会覆盖掉视频号按钮的名字
            self.Topstories={'title':'Top Stories','control_type':'Button'}#主界面左侧的看一看按钮
            self.Search={'title':'Search','control_type':'Button'}#主界面左侧的搜一搜按钮
            self.Miniprogram_pane={'title':'Mini Programs Panel','control_type':'Button'}#主界面左侧的小程序面板按钮
            self.SettingsAndOthers={'title':'Settings and Others','control_type':'Button'} #主界面左侧的设置及其他按钮

        if self.language=='繁体中文':
            self.Chats={'title':'聊天','control_type':'Button'}#主界面左侧的聊天按钮
            self.Contacts={'title':'通訊錄','control_type':'Button'}#主界面左侧的通讯录按钮
            self.Collections={'title':'收藏','control_type':'Button'}#主界面左侧的收藏按钮
            self.ChatFiles={'title':'聊天室檔案','control_type':'Button'}#主界面左侧的聊天文件按钮
            self.Moments={'title':'朋友圈','control_type':'Button'}#主界面左侧的朋友圈按钮
            self.Channel={'found_index':6,'control_type':'Button'}#主界面左侧的视频号按钮,z之所以用found_index是因为视频号的新消息提示会覆盖掉视频号按钮的名字
            self.Topstories={'title':'看一看','control_type':'Button'}#主界面左侧的看一看按钮
            self.Search={'title':'搜一搜','control_type':'Button'}#主界面左侧的搜一搜按钮
            self.Miniprogram_pane={'title':'小程式面板','control_type':'Button'}#主界面左侧的小程序面板按钮
            self.SettingsAndOthers={'title':'設定與其他','control_type':'Button'} #主界面左侧的设置及其他按钮 



class Independent_window():
    '''独立于微信主界面,将微信主界面关闭后仍能在桌面显示的窗口Ui\n'''
    def __init__(self,language=language):
        self.language=language
        if self.language=='简体中文':
            self.Desktop={'backend':'uia'}#windows桌面
            self.SettingWindow={'title':'设置','class_name':"SettingWnd",'control_type':'Window'}#微信设置窗口
            self.ContactManagerWindow={'title':'通讯录管理','class_name':'ContactManagerWindow'}#通讯录管理窗口
            self.MomentsWindow={'title':'朋友圈','control_type':"Window",'class_name':"SnsWnd"}#朋友圈窗口
            self.ChatFilesWindow={'title':'聊天文件','control_type':'Window','class_name':'FileListMgrWnd'}#聊天文件窗口
            self.MiniProgramWindow={'title':'微信','control_type':'Pane','class_name':'Chrome_WidgetWin_0'}#小程序面板窗口
            self.SearchWindow={'title':'微信','class_name':'Chrome_WidgetWin_0','control_type':'Pane'}#搜一搜窗口
            self.ChannelWindow={'title':'微信','class_name':'Chrome_WidgetWin_0','control_type':'Pane'}#视频号窗口
            self.ContactProfileWindow={'title':'微信','class_name':'ContactProfileWnd','framework_id':'Win32','control_type':'Pane'}#添加新好友时的添加到通讯录窗口
            self.TopStoriesWindow={'title':'微信','class_name':'Chrome_WidgetWin_0','control_type':'Pane'}#看一看窗口
            self.ChatHistoryWindow={'control_type':'Window','class_name':'FileManagerWnd','framework_id':'Win32'}#聊天记录窗口
            self.GroupAnnouncementWindow={'title':'群公告','framework_id':'Win32','class_name':'ChatRoomAnnouncementWnd'}#群公告窗口
            self.NoteWindow={'title':'笔记','class_name':'FavNoteWnd','framework_id':"Win32"}#笔记窗口
            self.OldIncomingCallWindow={'class_name':'VoipTrayWnd','title':'微信'}#旧版本来电(视频或语音)窗口
            self.NewIncomingCallWindow={'class_name':'ILinkVoipTrayWnd','title':'微信'}#旧版本来电(视频或语音)窗口
            self.OldVoiceCallWindow={'title':'微信','class_name':'AudioWnd'}#旧版本接通语音电话后通话窗口
            self.NewVoiceCallWindow={'title':'微信','class_name':'ILinkAudioWnd'}#新版本接通语音电话后通话窗口
            self.OldVideoCallWindow={'title':'微信','class_name':'VoipWnd'}#新版本接通语音电话后通话窗口
            self.NewVideoCallWindow={'title':'微信','class_name':'ILinkVoipWnd'}#新版本接通视频电话后通话窗口
            self.OfficialAccountWindow={'title':'公众号','control_type':'Window','class_name':'H5SubscriptionProfileWnd'}#公众号窗口
            self.OfficialAccountChatWindow={'class_name':'ChatWnd','control_type':'Window','framework_id':'Win32'}#公众号聊天窗口
            self.ReadMessageWindow={'title':'消息阅读','control_type':'Window','class_name':'CommonPreviewWnd'}#放大阅读后的阅读窗口
            self.ReceiptLedgerWindow={'title':'收款小账本','control_type':'Pane','class_name':'Chrome_WidgetWin_0','framework_id':'Win32'}#收款小账本窗口
            self.PaymentCodeWindow={'title':'经营账户','control_type':'Pane','class_name':'Chrome_WidgetWin_0','framework_id':'Win32'}#收款码窗口
            self.MyBillsAndServiceWindow={'title':'我的账单与服务','control_type':'Pane','class_name':'Chrome_WidgetWin_0','framework_id':'Win32'}#微信支付我的账单与服务窗口
            self.MyBillsWindow={'title':'微信记账本','control_type':'Pane','class_name':'Chrome_WidgetWin_0','framework_id':'Win32'}#微信支付我的账单窗口

        if self.language=='英文':
            self.Desktop={'backend':'uia'}#windows桌面
            self.SettingWindow={'title':'Settings','class_name':"SettingWnd",'control_type':'Window'}#微信设置窗口
            self.ContactManagerWindow={'title':'Manage Contacts','class_name':'ContactManagerWindow'}#通讯录管理窗口
            self.MomentsWindow={'title':'Moments','control_type':"Window",'class_name':"SnsWnd"}#朋友圈窗口
            self.ChatFilesWindow={'title':'Chat Files','control_type':'Window','class_name':'FileListMgrWnd'}#聊天文件窗口
            self.MiniProgramWindow={'title':'微信','control_type':'Pane','class_name':'Chrome_WidgetWin_0'}#小程序面板窗口
            self.SearchWindow={'title':'微信','class_name':'Chrome_WidgetWin_0','control_type':'Pane'}#搜一搜窗口
            self.ChannelWindow={'title':'微信','class_name':'Chrome_WidgetWin_0','control_type':'Pane'}#视频号窗口
            self.ContactProfileWindow={'title':'Weixin','class_name':'ContactProfileWnd','framework_id':'Win32','control_type':'Pane'}#添加新好友时的添加到通讯录窗口
            self.TopStoriesWindow={'title':'微信','class_name':'Chrome_WidgetWin_0','control_type':'Pane'}#看一看窗口
            self.ChatHistoryWindow={'control_type':'Window','class_name':'FileManagerWnd','framework_id':'Win32'}#聊天记录窗口
            self.GroupAnnouncementWindow={'title':'Group Notice','framework_id':'Win32','class_name':'ChatRoomAnnouncementWnd'}#群公告窗口
            self.NoteWindow={'title':'Notes','class_name':'FavNoteWnd','framework_id':"Win32"}#笔记窗口
            self.OldIncomingCallWindow={'class_name':'VoipTrayWnd','title':'Weixin'}#旧版本来电(视频或语音)窗口
            self.NewIncomingCallWindow={'class_name':'ILinkVoipTrayWnd','title':'Weixin'}#旧版本来电(视频或语音)窗口
            self.OldVoiceCallWindow={'title':'Weixin','class_name':'AudioWnd'}#旧版本接通语音电话后通话窗口
            self.NewVoiceCallWindow={'title':'Weixin','class_name':'ILinkAudioWnd'}#新版本接通语音电话后通话窗口
            self.OldVideoCallWindow={'title':'Weixin','class_name':'VoipWnd'}#新版本接通语音电话后通话窗口
            self.NewVideoCallWindow={'title':'Weixin','class_name':'ILinkVoipWnd'}#新版本接通视频电话后通话窗口
            self.OfficialAccountWindow={'title':'Official Accounts','control_type':'Window','class_name':'H5SubscriptionProfileWnd'}#在搜一搜中搜出来的公众号窗口
            self.OfficialAccountChatWindow={'class_name':'ChatWnd','control_type':'Window','framework_id':'Win32'}#公众号聊天窗口
            self.ReadMessageWindow={'title':'Read messages','control_type':'Window','class_name':'CommonPreviewWnd'}#放大阅读后的阅读窗口
            self.ReceiptLedgerWindow={'title':'收款小账本','control_type':'Pane','class_name':'Chrome_WidgetWin_0','framework_id':'Win32'}#收款小账本窗口
            self.PaymentCodeWindow={'title':'经营账户','control_type':'Pane','class_name':'Chrome_WidgetWin_0','framework_id':'Win32'}#收款码窗口
            self.MyBillsAndServiceWindow={'title':'我的账单与服务','control_type':'Pane','class_name':'Chrome_WidgetWin_0','framework_id':'Win32'}#微信支付我的账单与服务窗口
            self.MyBillsWindow={'title':'微信记账本','control_type':'Pane','class_name':'Chrome_WidgetWin_0','framework_id':'Win32'}#微信支付我的账单窗口

        if self.language=='繁体中文':
            self.Desktop={'backend':'uia'}#windows桌面
            self.SettingWindow={'title':'設定','class_name':"SettingWnd",'control_type':'Window'}#微信设置窗口
            self.ContactManagerWindow={'title':'通訊錄管理','class_name':'ContactManagerWindow'}#通讯录管理窗口
            self.MomentsWindow={'title':'朋友圈','control_type':"Window",'class_name':"SnsWnd"}#朋友圈窗口
            self.ChatFilesWindow={'title':'聊天文件','control_type':'Window','class_name':'FileListMgrWnd'}#聊天文件窗口
            self.MiniProgramWindow={'title':'微信','control_type':'Pane','class_name':'Chrome_WidgetWin_0'}#小程序面板窗口
            self.SearchWindow={'title':'微信','class_name':'Chrome_WidgetWin_0','control_type':'Pane'}#搜一搜窗口
            self.ChannelWindow={'title':'微信','class_name':'Chrome_WidgetWin_0','control_type':'Pane'}#视频号窗口
            self.ContactProfileWindow={'title':'微信','class_name':'ContactProfileWnd','framework_id':'Win32','control_type':'Pane'}#添加新好友时的添加到通讯录窗口
            self.TopStoriesWindow={'title':'微信','class_name':'Chrome_WidgetWin_0','control_type':'Pane'}#看一看窗口
            self.ChatHistoryWindow={'control_type':'Window','class_name':'FileManagerWnd','framework_id':'Win32'}#聊天记录窗口
            self.GroupAnnouncementWindow={'title':'群組公告','framework_id':'Win32','class_name':'ChatRoomAnnouncementWnd'}#群公告窗口
            self.NoteWindow={'title':'筆記','class_name':'FavNoteWnd','framework_id':"Win32"}#笔记窗口
            self.OldIncomingCallWindow={'class_name':'VoipTrayWnd','title':'微信'}#旧版本来电(视频或语音)窗口
            self.NewIncomingCallWindow={'class_name':'ILinkVoipTrayWnd','title':'微信'}#旧版本来电(视频或语音)窗口
            self.OldVoiceCallWindow={'title':'微信','class_name':'AudioWnd'}#旧版本接通语音电话后通话窗口
            self.NewVoiceCallWindow={'title':'微信','class_name':'ILinkAudioWnd'}#新版本接通语音电话后通话窗口
            self.OldVideoCallWindow={'title':'微信','class_name':'VoipWnd'}#新版本接通语音电话后通话窗口
            self.NewVideoCallWindow={'title':'微信','class_name':'ILinkVoipWnd'}#新版本接通视频电话后通话窗口
            self.OfficialAccountWindow={'title':'官方賬號','control_type':'Window','class_name':'H5SubscriptionProfileWnd'}#搜一搜里边搜索点击打开的公众号窗口
            self.OfficialAccountChatWindow={'class_name':'ChatWnd','control_type':'Window','framework_id':'Win32'}#公众号聊天窗口
            self.ReadMessageWindow={'title':'訊息閱讀','control_type':'Window','class_name':'CommonPreviewWnd'}#放大阅读后的阅读窗口
            self.ReceiptLedgerWindow={'title':'收款小账本','control_type':'Pane','class_name':'Chrome_WidgetWin_0','framework_id':'Win32'}#收款小账本窗口
            self.PaymentCodeWindow={'title':'经营账户','control_type':'Pane','class_name':'Chrome_WidgetWin_0','framework_id':'Win32'}#收款码窗口
            self.MyBillsAndServiceWindow={'title':'我的账单与服务','control_type':'Pane','class_name':'Chrome_WidgetWin_0','framework_id':'Win32'}#微信支付我的账单与服务窗口
            self.MyBillsWindow={'title':'微信记账本','control_type':'Pane','class_name':'Chrome_WidgetWin_0','framework_id':'Win32'}#微信支付我的账单窗口

class SpecialMessages():
    '''特殊消息的Ui元素,如图片、视频、语音、视频号等\n
    这些消息的ListItem的widow_text()属性名为[图片],[视频]等\n
    为了方便使用,将这些消息的widow_text()属性名定义为常量\n
    AudioPattern是正则提取语音消息时的pattern\n'''
    def __init__(self,language=language):
        self.language=language
        if self.language=='简体中文':
            self.PhotoMessage={'title':'[图片]','control_type':'ListItem'}
            self.VideoMessage={'title':'[视频]','control_type':'ListItem'}
            self.StickerMessage={'title':'[动画表情]','control_type':'ListItem'}
            self.ChannelMessage={'title':'[视频号]','control_type':'ListItem'}
            self.FileMessage={'title':'[文件]','control_type':'ListItem'}
            self.ChatHistoryMessage={'title':'[聊天记录]','control_type':'ListItem'}
            self.AudioPattern=r'\[语音\]\d+秒'

        if self.language=='英文':
            self.PhotoMessage={'title':'[Photo]','control_type':'ListItem'}
            self.VideoMessage={'title':'[Video]','control_type':'ListItem'}
            self.StickerMessage={'title':'[Sticker]','control_type':'ListItem'}
            self.ChannelMessage={'title':'[Channel]','control_type':'ListItem'}
            self.FileMessage={'title':'[File]','control_type':'ListItem'}
            self.ChatHistoryMessage={'title':'[Chat History]','control_type':'ListItem'}
            self.AudioPattern=r'\[Audio\]\d+s'
            
        if self.language=='繁体中文':
            self.PhotoMessage={'title':'[圖片]','control_type':'ListItem'}
            self.VideoMessage={'title':'[影片]','control_type':'ListItem'}
            self.StickerMessage={'title':'[動態貼圖]','control_type':'ListItem'}
            self.ChannelMessage={'title':'[影音號]','control_type':'ListItem'}
            self.FileMessage={'title':'[檔案]','control_type':'ListItem'}
            self.ChatHistoryMessage={'title':'[聊天記錄]','control_type':'ListItem'}
            self.AudioPattern=r'\[語音\]\d+秒'