# pywechat🥇
![image](https://github.com/Hello-Mr-Crab/pywechat/blob/main/pics/wechat.png)
## 🍬🍬微信RPA工具,现支持4.1+部分功能具体使用方法见：

https://github.com/Hello-Mr-Crab/pywechat/blob/main/Weixin4.0.md

### pywechat是一个基于pywinauto实现的Windows系统下PC微信自动化(pure uiautomation)的Python项目(不涉及逆向Hook操作),实现了PC微信内置的大部分功能。

### 微信版本:3.9+,4.1.6+
### 操作系统:🪟windows 7 🪟windows 10 🪟windows 11
### python版本🐍:3.9+(支持TypeHint)
### 支持语言:简体中文,English,繁体中文
### pyweixin 与 pywechat 项目结构(pywechat只能用于32位x86🪟10,32位x86🪟7)：
![image](https://github.com/Hello-Mr-Crab/pywechat/blob/main/pics/pyweixin结构.png)
<br>

## pyweixin内所有方法需要先导入模块下的类然后调用内部方法🗺️🗺️
```
from pyweixin import xx(class)
xx(class).yy(method)
```
<br>

### 获取方法（4.1+微信）:
```
git clone https://github.com/Hello-Mr-Crab/pywechat.git
```
<br>

### 获取方法（3.9+微信）:
#### 最新版本:1.9.7
```
pip install pywechat127==1.9.7
```
<br>

```
pip install --upgrade pywechat127
```
<br>

```
git clone https://github.com/Hello-Mr-Crab/pywechat.git
```
<br>

### pyweixin模块介绍(适用于4.1+微信)
#### WechatTools🌪️🌪️
##### class包括:
- `Tools`:关于PC微信的一些工具,微信路径,运行状态,以及内部一些UI相关的判别方法。
- `Navigator`:打开微信内部一切可以打开的界面。
<br>

#### WechatAuto🛏️🛏️
##### class包括：
- `AutoReply`:自动回复操作
- `Call`: 给某个好友打视频或语音电话。
- `Contacts`: 获取通讯录内各分区(联系人,企业微信联系人,公众号,服务号)好友的信息,获取共同群聊名称,获取好友个人简介
- `Files`: 文件发送，聊天文件从本地导出等。
- `FriendSettings`: PC微信针对某个好友的一些相关设置。
- `Messages`: 消息发送,聊天记录获取,聊天会话导出等条。
- `Moments`:针对微信朋友圈的一些方法,包括朋友圈界面内容获取，发布朋友圈
- `Monitor`:打开聊天窗口进行监听消息
<br>

#### WinSettings🔹🔹
##### class包括：
- `SystemSettings`:该模块中提供了一些修改windows系统设置的方法(在自动化过程中)。
<br>

#### utils🍬🍬
##### 内部的一些函数主要用来二次开发,大部分传入的参数是main_window,pywinauto实例化的对象(使用Navigator.open_weixin打开)
##### class包括：
- `Regex_Patterns`:自动化过程中用到的正则pattern。
##### func包括:
- `At`:在群聊中At指定的一些好友
- `At_all`:在群聊中At所有人
- `auto_reply_to_friend_decorator`:自动回复好友装饰器
- `get_new_message_num`：获取新消息总数,微信按钮上的红色数字
- `scan_for_newMessages`：会话列表遍历一遍有新消息提示的对象,返回好友名称与数量
- `open_red_packet`: 点击打开好友发送的红包
- `language_detector`:微信当前使用语言检测(不能禁用WeChatAppex.exe(涉及到公众号,微信内置浏览器,视频号等功能),原理是查询WeChatAppex.exe命令行参数)
<br>

### pyweixin使用示例:
#### 所有自动化操作只需两行代码即可实现，即：
```
from pyweixin import xxx
xxx.yy
```
<br>


#### 多线程监听消息
```
#多线程打开多个好友窗口进行消息监听
from concurrent.futures import ThreadPoolExecutor
from pyweixin import Navigator,Monitor
#先打开所有好友的独立窗口
dialog_windows=[]
friends=['Hello,Mr Crab','Pywechat测试群',]
durations=['1min']*len(friends)
#不添加其他参数Monitor.listen_on_chat,比如save_photos,该操作涉及键鼠,无法多线程，只是监听消息，获取文本内容,移动保存文件还是可以的
for friend in friends:
dialog_window=Navigator.open_seperate_dialog_window(friend=friend,window_minimize=True,close_weixin=True)#window_minimize独立窗口最小化
    dialog_windows.append(dialog_window)
with ThreadPoolExecutor(max_workers=len(friends)) as pool:
    results=pool.map(lambda args: Monitor.listen_on_chat(*args),list(zip(dialog_windows,durations)))
for friend,result in zip(friends,results):
    print(friend,result)
```
<br>

![image](https://github.com/Hello-Mr-Crab/pywechat/blob/main/pics/listen_on_chat多线程.png)

<br>

#### 多线程监听消息并自动回复
```
from pyweixin import Navigator
from concurrent.futures import ThreadPoolExecutor
from pyweixin import Navigator,AutoReply
#自动回复函数传入参数是字符串和字符串列表(消息列表内所有可见的文本,可作为上下文),返回值须为字符串类型
def reply_func1(newMessage:str,contexts:list[str]):
    if '你好' in newMessage:
        return '你好,有什么可以帮您的吗[呲牙]?'
    if '在吗' in message:
        return '在的[旺柴]'
    return '自动回复[微信机器人]:您好,我当前不在,请您稍后再试'

def reply_func2(newMessage:str,contexts:list[str]):
    return '自动回复[微信机器人]:您好,我当前不在,请您稍后再试'

#先打开所有好友的独立窗口
dialog_windows=[]
friends=['abcdefghijklmnopqrstuvwxyz123456','Pywechat测试群']
for friend in friends:
    dialog_window=Navigator.open_seperate_dialog_window(friend=friend,window_minimize=True,close_weixin=True)
    dialog_windows.append(dialog_window)
durations=['1min','1min']
callbacks=[reply_func1,reply_func2]
with ThreadPoolExecutor() as pool:
    results=pool.map(lambda args: AutoReply.auto_reply_to_friend(*args),list(zip(dialog_windows,durations,callbacks)))
for friend,result in zip(friends,results):
    print(friend,result)
```
![image](https://github.com/Hello-Mr-Crab/pywechat/blob/main/pics/自动回复.png)

<br>

#### 监听单个聊天窗口消息
```
from pyweixin import Navigator,Monitor
dialog_window=Navigator.open_seperate_dialog_window(friend='啦啦啦')
result=Monitor.listen_on_chat(dialog_window=dialog_window,duration='30s')
print(result)#返回值 {'新消息总数':x,'文本数量':x,'文件数量':x,'图片数量':x,'视频数量':x,'链接数量':x,'文本内容':x}
```

<br>

#### 朋友圈数据获取
```
from pyweixin import Moments
posts=Moments.dump_recent_posts(recent='Today')
for dic in posts:
    print(dic)
```
![image](https://github.com/Hello-Mr-Crab/pywechat/blob/main/pics/朋友圈数据获取.png)

<br>

#### 发布朋友圈
```
from pyweixin import Moments
Moments.post_moments(texts='''发布朋友圈测试[旺柴]''',medias=[r"E:\Desktop\test0.png",r"E:\Desktop\test1.png"])
```
![image](https://github.com/Hello-Mr-Crab/pywechat/blob/main/pics/发朋友圈.png)

<br>

#### 好友朋友圈内容导出
```
from pyweixin import Moments
Moments.dump_friend_posts(friend='xxx',number=3,save_detail=True,target_folder=r"E:\Desktop\好友朋友圈内容导出")
```
![image](https://github.com/Hello-Mr-Crab/pywechat/blob/main/pics/好友朋友圈内容导出.png)
![image](https://github.com/Hello-Mr-Crab/pywechat/blob/main/pics/好友朋友圈内容.png)

<br>

#### 好友朋友圈自定义评论
```
from pyweixin import Moments
def comment_func(content):
    if 'xxx' in content:
        return 'yyy'
    return 'zzz'
Moments.like_friend_posts(friend='xxx',number=20,callback=comment_func,use_green_send=True)
```

<br>

#### 此外pyweixin内所有方法及函数的一些位置参数支持全局设定,be like:
```
from pyweixin import Navigator,GlobalConfig
GlobalConfig.load_delay=2.5
GlobalConfig.is_maximize=True
GlobalConfig.close_weixin=False
Navigator.search_channels(search_content='微信4.0')
Navigator.search_miniprogram(name='问卷星')
Navigator.search_official_account(name='微信')
```
<br>

#### 公众号文章url获取
```
from pyweixin import Collections
Collections.collect_offAcc_articles(name='新华社',number=10)
urls=Collections.cardLink_to_url(number=10)
for url,text in urls.items():
    print(f'{text}\n{url}')
```
![image](https://github.com/Hello-Mr-Crab/pywechat/blob/main/pics/公众号文章url获取.png)

<br>

#### 其他类内method使用方法可见代码中详细的文档注释以及pyweixin操作手册.docx
<br>

### Pywechat模块介绍
### (3.9+微信)
#### WechatTools🌪️🌪️
##### 模块包括:
##### Tools:关于PC微信的一些工具,包括打开PC微信内各个界面的open系列方法。
##### API:打开指定微信小程序，指定公众号,打开视频号的功能，若有其他开发者想自动化操作上述程序可调用此API。
##### 函数:该模块内所有函数与方法一致。
<br>

#### WechatAuto🛏️🛏️
##### 模块包括：
- `Messages`: 5种类型的发送消息方法，包括:单人单条,单人多条,多人单条,多人多条,转发消息:多人同一条。 
- `Files`: 5种类型的发送文件方法，包括:单人单个,单人多个,多人单个,多人多个,转发文件:多人同一个。发送多个文件时，你只需将所有文件放入文件夹内，将文件夹路径传入即可。
- `FriendSettings`: 涵盖了PC微信针对某个好友的全部操作的方法。
- `GroupSettings`: 涵盖了PC微信针对某个群聊的全部操作的方法。
- `Contacts`: 获取3种类型通讯录好友的备注与昵称包括:微信好友,企业号微信,群聊名称与人数，数据返回格式为json。
- `Call`: 给某个好友打视频或语音电话。
- `AutoReply`:自动接听微信视频或语音电话,自动回复指定好友消息,自动回复所有好友消息。
- `Moments`:针对微信朋友圈的一些方法,包括数据获取，图片视频导出
##### 函数:该模块内所有函数与方法一致。  
<br>

#### WinSettings🔹🔹
##### 模块包括：
##### Systemsettings:该模块中提供了一些修改windows系统设置的方法。
##### 函数：该模块内所有函数与方法一致。
<br>

### pywechat使用示例:
#### 所有自动化操作只需两行代码即可实现，即：
```
from pywechat import xxx
xxx.yy

from pyweixin import xxx
xxx,yy
```

<br>

#### 在某个群聊自动回复(使用装饰器自定义回复内容)
```
from pywechat.utils import auto_reply_to_group_decorator
@auto_reply_to_group_decorator(duration='2min',group_name='Pywechat测试群',at_only=True,at_other=True)
def reply_func(newMessage):
    if '你好' in newMessage:
        return '你好,请问有什么可以帮您的吗?'
    if '在吗' in newMessage:
        return '在的,请问有什么可以帮您的吗?'
    if '售后' in newMessage:
        return '''您好，您可以点击下方链接申请售后:
        https://github.com/Hello-Mr-Crab/pywechat'''
    if '算了' in newMessage or '不需要了' in newMessage:
        return '不好意思.未能为您提供满意的服务,欢迎下次光临'
    return '不好意思，未能理解您的需求'#最后总是要返回一个值，不要出现newMessage不在列举的情况,返回None
reply_func()
```
![image](https://github.com/Hello-Mr-Crab/pywechat/blob/main/pics/decorator.png)
<br>

#### 监听某个群聊或好友的窗口(自动保存聊天文件与图片和视频)
```
from pywechat import listen_on_chat
filesave_folder=r"E:\Desktop\保存文件"
mediasave_folder=r"E:\Desktop\聊天图片与视频保存"
contents,senders,types=listen_on_chat(friend='测试群',duration='10min',save_file=True,file_folder=filesave_folder,save_media=True,media_folder=mediasave_folder)
print(contents,senders,types)
```

#### 朋友圈数据获取
```
from pywechat import dump_recent_moments
moments=dump_recent_moments(recent='Today')
for dict in moments:
    print(dict)
```

![image](https://github.com/Hello-Mr-Crab/pywechat/blob/main/pics/dump_moments.png)
<br>
##### 注意，导出的结果为list[dict],每一条朋友圈对应一个dict,dict具体内容为:
{'好友备注':'','发布时间':'','文本内容':'','点赞者':'','评论内容':'','图片数量':'','视频数量':'','卡片链接':'','卡片链接内容':'','视频号':'','公众号链接内容':''}

<br>

#### 监听整个会话列表内所有好友的新消息(自动保存聊天文件)
```
from pywechat import check_new_message
filesave_folder=r"E:\Desktop\文件保存"
newMessages=check_new_message(duration='5min',save_file=True,target_folder=filesave_folder)
#newMessages是[{'好友名称':'路人甲','好友类型':'群聊,好友或公众号','新消息条数':xx,'消息内容':[],'消息类型':[]}]
#格式的list[dict]
```

#### 转发与某个好友的一定数量文件给其他好友
 ```
 #注意:微信转发消息单次上线为9,pywechat内转发消息,文件,链接,小程序等支持多个好友按9个为一组分批发送
 from pywechat import forward_files
 others=['路人甲','路人乙','路人丙','路人丁']
 forward_files(friend='测试群',others=others,number=20)
 ```
#### 保存指定数量聊天文件到本地]
```
from pywechat import save_files
folder_path=r'E:\Desktop\新建文件夹'
save_files(friend='测试群',number=20,folder_path=folder_path)
```
#### 群聊内自动回复(被@时触发)
```
from pywechat import auto_reply_to_group
auto_reply_to_group(group_name='测试群',duration='20min',content='我被@了',at_only=True,at_others=True)
```

![image](https://github.com/Hello-Mr-Crab/pywechat/blob/main/pics/auto_reply_to_group.png)

<br>

#### 给某个好友发送多条信息：
```
from pywechat.WechatAuto import Messages
Messages.send_messages_to_friend(friend="文件传输助手",messages=['你好','我正在使用pywechat操控微信给你发消息','收到请回复'])
```
##### 或者
```
import pywechat.WechatAuto as wechat
wechat.send_messages_to_friend(friend="文件传输助手",messages=['你好','我正在使用pywechat操控微信给你发消息','收到请回复'])
```

<br>

### 多任务使用示例
#### 注意,微信不支持多线程，只支持单线程多任务轮流执行，pywechat也支持单线程多任务轮流执行，在运行多个实例时尽量请将所有函数与方法内的close_wechat参数设为False(默认为True)
#### 这样只需要打开一次微信，多个任务便可以共享资源,更加高效，否则，每个实例在运行时都会重启一次微信，较为低效。
#### 注意,不要对pywechat内函数或方法使用多线程,因为微信只能打开一个,多个线程同时操作一个微信界面,必然产生死锁,会导致界面卡死!
<br>

```
from pywechat.WechatAuto import Messages,Files
Messages.send_messages_to_friend(friend='好友1',messages=['在测试','ok'],close_wechat=False)
Files.send_files_to_friend(friend='文件传输助手',folder_path=r"E:\OneDrive\Desktop\测试专用",with_messages=True,messages_first=True,messages=['在测试文件消息一起发，你应该先看到这条消息，后看到文件'],close_wechat=True)
```


##### 自动回复效果:

![Alt text](https://github.com/Hello-Mr-Crab/pywechat/blob/main/pics/Ai接入实例.png)

### 检查新消息示例
<br>

```
from pywechat import check_new_message
print(check_new_message())
```

##### 检查新消息效果：

![Alt text](https://github.com/Hello-Mr-Crab/pywechat/blob/main/pics/check_new_message.gif)

##### 若你开启了语音自动转消息功能后,新消息中含有语音消息的话,可以将其转换结果一并记录。（1.9.7版本支持此功能）
## 注意:
👎👎请勿将pywechat用于任何非法商业活动,因此造成的一切后果由使用者自行承担！ 

##### 本项目相关博客
- `pywinauto使用教程`:https://mrcrab.blog.csdn.net/article/details/157546162?fromshare=blogdetail&sharetype=blogdetail&sharerId=157546162&sharerefer=PC&sharesource=weixin_73953650&sharefrom=from_link
- `python正则表达式`:https://mrcrab.blog.csdn.net/article/details/151123336?fromshare=blogdetail&sharetype=blogdetail&sharerId=151123336&sharerefer=PC&sharesource=weixin_73953650&sharefrom=from_link
- `shutil文件移动`:https://mrcrab.blog.csdn.net/article/details/148735930?fromshare=blogdetail&sharetype=blogdetail&sharerId=148735930&sharerefer=PC&sharesource=weixin_73953650&sharefrom=from_link
- `os.path文件路径`:https://mrcrab.blog.csdn.net/article/details/147304200?fromshare=blogdetail&sharetype=blogdetail&sharerId=147304200&sharerefer=PC&sharesource=weixin_73953650&sharefrom=from_link
- `x86虚拟机安装问题`:https://mrcrab.blog.csdn.net/article/details/158418985?fromshare=blogdetail&sharetype=blogdetail&sharerId=158418985&sharerefer=PC&sharesource=weixin_73953650&sharefrom=from_link 
<br>

###### 作者CSDN主页:https://blog.csdn.net/weixin_73953650?spm=1011.2415.3001.5343
