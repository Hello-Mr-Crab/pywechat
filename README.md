# pywechat🥇

![image](/pics/wechat.png)

## 🍬🍬微信RPA工具,支持4.1+微信自动化

pywechat是一个基于pywinauto实现的Windows系统下PC微信自动化(pure uiautomation)的项目(**不涉及逆向Hook操作**)，可以用来收发消息和数据获取。
注意，本项目开发的初衷为使用UI自动化和分享UI自动化技术，请勿将该工具用于违反微信使用条例的操作！

### 适用环境

> 1. **微信版本**:3.9.12.x，4.1.6.x
> 2. **操作系统**:🪟7 🪟10 🪟11
> 3. **python版本**:3.10+(支持TypeHint)
> 4. **支持语言**:简体中文,English,繁體中文

### pyweixin 与 pywechat 项目结构(pywechat只能用于32位x86🪟10,32位x86🪟7)

![pyweixin结构](/pics/pyweixin结构.png "pyweixin结构")
</br>

### Skill

目前,可以使用的Skill的Agent主流平台:

<p align="center">
  <img src="/pics/支持Skill平台.png" alt="Skill主流平台" />
</p>

具体使用方法可见[QuickStart.md](/QuickStart.md)

<p align="center">
  <img src="/pics/openclaw评价.png" alt="openclaw评价" />
</p>

使用示例：

<p align="center">
  <img src="/pics/pyweixin-rpa测试.png" alt="pyweixin-rpa测试" />
</p>

实际效果:

<p align="center">
  <img src="/pics/openclaw测试案例.png" alt="openclaw测试案例" />
</p>

### 快速上手✌️

[点击查看QuickStart.md](/QuickStart.md)

### pyweixin模块介绍(适用于4.1+微信)

pyweixin内所有方法需要先导入模块下的类然后调用内部方法☸︎

```python
from pyweixin import xx(class)
xx(class).yy(method)
```

#### WechatTools🌪️🌪️

##### class包括

- `Tools`:关于PC微信的一些工具,微信路径,运行状态,以及内部一些UI相关的判别方法。
- `Navigator`:打开微信内部一切可以打开的界面。

#### WechatAuto🛏️🛏️

##### class(类) 包括

- `AutoReply`:自动回复操作。(一种简单的实现方式，如果对此感兴趣可以使用pyweixin内部的一些方法自行尝试)
- `Call`: 给某个好友打视频或语音电话。
- `Contacts`: 获取通讯录内各分区(联系人,企业微信联系人,公众号,服务号)好友的名称与详情。
- `Files`: 文件发送，聊天文件从本地导出等。
- `FriendSettings`: 针对某个好友的一些相关设置。
- `Messages`: 消息发送,聊天记录获取,聊天会话导出等。
- `Moments`:针对微信朋友圈的一些方法,包括朋友圈内容获取，发布朋友圈。
- `Monitor`:打开聊天窗口进行监听消息。

#### WinSettings🔹🔹

##### class(类)包括

- `SystemSettings`:该模块中提供了一些修改windows系统设置的方法(在自动化过程中)。

#### utils🍬🍬

##### 内部的一些函数主要用来二次开发,大部分传入的参数是main_window,pywinauto实例化的对象(使用Navigator.open_weixin打开)

##### class 包括

- `Regex_Patterns`:自动化过程中用到的正则pattern。
- `Special_Label`:微信内一些特殊的标签,比如:“消息已置顶”，这些标签随着微信的语言会变化。

##### func包括

- `At`:在群聊中At指定的一些好友
- `At_all`:在群聊中At所有人
- `auto_reply_to_friend_decorator`:自动回复好友装饰器
- `get_new_message_num`：获取新消息总数,微信按钮上的红色数字
- `scan_for_newMessages`：会话列表遍历一遍有新消息提示的对象,返回好友名称与数量
- `open_red_packet`: 点击打开好友发送的红包
- `language_detector`:微信当前使用语言检测(不能禁用WeChatAppex.exe(涉及到公众号,微信内置浏览器,视频号等功能),原理是查询WeChatAppex.exe命令行参数)

</br>

### pyweixin使用示例

所有自动化操作只需两行代码即可实现，即:

```python
from pyweixin import xxx
xxx.yy
```

#### 发送语音消息给好友

```python
'''
微信版本>=4.1.9,且配置过虚拟驱动,并且安装sounddevice与soundfile库,具体可见
https://mrcrab.blog.csdn.net/article/details/160481307?fromshare=blogdetail&sharetype=blogdetail&sharerId=160481307&sharerefer=PC&sharesource=weixin_73953650&sharefrom=from_link
''''
from pyweixin import Messages
Messages.send_audios_to_friend(friend='小号测试',audios=[r"E:\Desktop\录音.wav",r"E:\Desktop\音乐.mp3",r"E:\Desktop\音乐.ogg"])
```

#### 关于微信的基本信息输出

```python
from pyweixin import Tools
print(Tools.about_weixin())
```

#### 多线性监听聊天窗口消息

```python
from concurrent.futures import ThreadPoolExecutor
from pyweixin import Navigator,Monitor
#先打开所有好友的独立窗口
dialog_windows=[]
friends=['Hello,Mr Crab','Pywechat测试群']
durations=['1min']*len(friends)
for friend in friends:
    dialog_window=Navigator.open_seperate_dialog_window(friend=friend,window_minimize=True,close_weixin=True)
    dialog_windows.append(dialog_window)
with ThreadPoolExecutor() as pool:
    results=pool.map(lambda args: Monitor.listen_on_chat(*args),list(zip(dialog_windows,durations)))
for friend,result in zip(friends,results):
    print(friend,result)
#返回值 {'新消息总数':x,'文本数量':x,'文件数量':x,'图片数量':x,'视频数量':x,'链接数量':x,'文本内容':x,'消息发送人':x}
```

![listen_on_chat](/pics/listen_on_chat多线程.png "listen_on_chat")
</br>

#### 多线程监听消息并自动回复

```python

```python
from pywechat import check_new_message
filesave_folder=r"E:\Desktop\文件保存"
newMessages=check_new_message(duration='5min',save_file=True,target_folder=filesave_folder)
#newMessages是[{'好友名称':'路人甲','好友类型':'群聊,好友或公众号','新消息条数':xx,'消息内容':[],'消息类型':[]}]
#格式的list[dict]
```

#### 转发与某个好友的一定数量文件给其他好友

```python
 #注意:微信转发消息单次上线为9,pywechat内转发消息,文件,链接,小程序等支持多个好友按9个为一组分批发送
 from pywechat import forward_files
 others=['路人甲','路人乙','路人丙','路人丁']
 forward_files(friend='测试群',others=others,number=20)
```

#### 保存指定数量聊天文件到本地

```python
from pywechat import save_files
folder_path=r'E:\Desktop\新建文件夹'
save_files(friend='测试群',number=20,folder_path=folder_path)
```

#### 群聊内自动回复(被@时触发)

```python
from pywechat import auto_reply_to_group
auto_reply_to_group(group_name='测试群',duration='20min',content='我被@了',at_only=True,at_others=True)
```

![群聊自动回复](/pics/auto_reply_to_group.png "群聊自动回复")
</br>

#### 给某个好友发送多条信息

```python
from pywechat.WechatAuto import Messages
Messages.send_messages_to_friend(friend="文件传输助手",messages=['你好','我正在使用pywechat操控微信给你发消息','收到请回复'])
```

### 多任务使用示例

注意,微信不支持多线程，只支持单线程多任务轮流执行，pywechat也支持单线程多任务轮流执行，在运行多个实例时尽量请将所有函数与方法内的close_wechat参数设为False(默认为True)
这样只需要打开一次微信，多个任务便可以共享资源,更加高效，否则，每个实例在运行时都会重启一次微信，较为低效
多个线程同时操作一个微信界面,必然产生死锁,会导致界面卡死

### 检查新消息示例

```python
from pywechat import check_new_message
print(check_new_message())
```

![检查新消息](/pics/check_new_message.gif "检查新消息")

## 注意

> 👎👎请勿将pywechat用于任何非法商业活动,因此造成的一切后果由使用者自行承担！

## 本项目相关博客

> - [pywinauto使用教程](https://mrcrab.blog.csdn.net/article/details/157546162?fromshare=blogdetail&sharetype=blogdetail&sharerId=157546162&sharerefer=PC&sharesource=weixin_73953650&sharefrom=from_link)
> - [python正则表达式](https://mrcrab.blog.csdn.net/article/details/151123336?fromshare=blogdetail&sharetype=blogdetail&sharerId=151123336&sharerefer=PC&sharesource=weixin_73953650&sharefrom=from_link)
> - [shutil文件移动](https://mrcrab.blog.csdn.net/article/details/148735930?fromshare=blogdetail&sharetype=blogdetail&sharerId=148735930&sharerefer=PC&sharesource=weixin_73953650&sharefrom=from_link)
> - [os.path文件路径](https://mrcrab.blog.csdn.net/article/details/147304200?fromshare=blogdetail&sharetype=blogdetail&sharerId=147304200&sharerefer=PC&sharesource=weixin_73953650&sharefrom=from_link)
> - [x86Win10虚拟机安装问题](https://mrcrab.blog.csdn.net/article/details/158418985?fromshare=blogdetail&sharetype=blogdetail&sharerId=158418985&sharerefer=PC&sharesource=weixin_73953650&sharefrom=from_link)
> - [使用微信语音发送指定的音频给好友](https://mrcrab.blog.csdn.net/article/details/160481307?fromshare=blogdetail&sharetype=blogdetail&sharerId=160481307&sharerefer=PC&sharesource=weixin_73953650&sharefrom=from_link)

</br>

### 作者CSDN主页:[Hello,Mr Crab](https://blog.csdn.net/weixin_73953650?spm=1011.2415.3001.5343)
