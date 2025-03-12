# pywechat🥇
![image](https://github.com/Hello-Mr-Crab/pywechat/blob/main/pics/introduction.jpg)
## 🍬🍬pywechat是一个基于pywinauto实现的Windows系统下PC微信自动化的Python项目。基本实现了PC微信内置的所有功能,支持单线程多任务轮流进行,完全模拟真人操作微信!!

### 微信版本:3.9.12.17
### 操作系统:🪟windows 10 🪟windows 11
### python版本🐍:3.x
### pywechat项目结构：
![image](https://github.com/Hello-Mr-Crab/pywechat/blob/main/pics/pywechat架构图.png)
<br>
 ### 注意，新版本pywechat内所有模块下的类或函数均可直接从pywechat导入，即
   ```
  from pywechat impot xx(class)
  from pywechat import xx(function)
  ```
<br>

##  你只需要将微信WeChat.exe文件地址传入pywechat各个函数，或直接添加到windows用户环境变量中即可实现从自动登录到自动回复的一系列微信自动化之旅。🗺️🗺️
### 注:pywechat最新版本已内置自动添加WeChat.exe为windows用户环境变量的方法。
这里建议将微信Wechat.exe文件路径添加到windows系统环境变量中，当微信未启动时pywechat默认使用windows环境变量中的Wechat.exe路径启动微信,此时调用其中的每个方法与函数无需传入wechat_path参数即可自动化操作微信。

<br>

### 获取方法:
#### 最新版本:1.8.6
```
pip install pywechat127==1.8.6
```
<br>

```
pip install --upgrade pywechat127
```
<br>

### 添加微信至windows用户环境变量:
#### pywechat已内置自动添加微信至用户环境变量的方法,运行下列代码即可自动添加微信路径至windows用户变量 :
```
from pywechat.WechatTools import Tools
Tools.set_wechat_as_environ_path()
```

#### 效果演示:
![Alt text](https://github.com/Hello-Mr-Crab/pywechat/blob/main/pics/演示效果.gif)
<br>

### WechatTools🌪️🌪️
#### 模块包括:
#### Tools:关于PC微信的一些工具,包括3个关于PC微信程序的方法和10个打开PC微信内各个界面的open系列方法。
#### API:打开指定微信小程序，指定公众号,打开视频号的功能，若有其他开发者想自动化操作上述程序可调用此API。
#### 函数:该模块内所有函数与方法一致。
<br>

### WechatAuto🛏️🛏️
#### 模块包括：
##### Messages: 5种类型的发送消息方法，包括:单人单条,单人多条,多人单条,多人多条,转发消息:多人同一条。 
##### Files: 5种类型的发送文件方法，包括:单人单个,单人多个,多人单个,多人多个,转发文件:多人同一个。发送多个文件时，你只需将所有文件放入文件夹内，将文件夹路径传入即可。
##### FriendSettings: 涵盖了PC微信针对某个好友的全部操作的方法。
##### GroupSettings: 涵盖了PC微信针对某个群聊的全部操作的方法。
##### Contacts: 获取3种类型通讯录好友的备注与昵称包括:微信好友,企业号微信,群聊名称与人数，数据返回格式为json。
##### Call: 给某个好友打视频或语音电话。
##### AutoReply:自动接听微信视频或语音电话,自动回复指定好友消息,自动回复所有好友消息。
#### 函数:该模块内所有函数与方法一致。  
<br>

### WinSettings🔹🔹
#### 模块包括：
#### Systemsettings:该模块中提供了7个修改windows系统设置和3个判断文件类型的方法。
#### 函数：该模块内所有函数与方法一致。
<br>

### 使用示例:
#### (注意，微信WeChat.exe路径已添加至windows系统环境变量,故当微信还未登录时,以下方法或函数无需传入wechat_path这一参数)
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

#### 自动接听语音视频电话:
```
from pywechat.WechatAuto import AutoReply
AutoReply.auto_answer_call(broadcast_content='您好，我目前不在线我的PC微信正在由我的微信机器人控制请稍后再试',message='您好，我目前不在线我的PC微信正在由我的微信机器人控制请稍后再试',duration='1h',times=1)
```
##### 或者
```
import pywechat.WechatAuto as wechat
wechat.auto_answer_call(broadcast_content='您好，我目前不在线我的PC微信正在由我的微信机器人控制请稍后再试',message='您好，我目前不在线我的PC微信正在由我的微信机器人控制请稍后再试',duration='1h',times=1)
```
### 多任务使用示例
#### 注意,微信不支持多线程，只支持单线程多任务轮流执行，pywechat也支持单线程多任务轮流执行，在运行多个实例时尽量请将所有函数与方法内的close_wechat参数设为False(默认为True)
#### 这样只需要打开一次微信，多个任务便可以共享资源,更加高效，否则，每个实例在运行时都会重启一次微信，较为低效。
<br>

```
from pywechat.WechatAuto import Messages,Files
Messages.send_messages_to_friend(friend='好友1',messages=['在测试','ok'],close_wechat=False)
Files.send_files_to_friend(friend='文件传输助手',folder_path=r"E:\OneDrive\Desktop\测试专用",with_messages=True,messages_first=True,messages=['在测试文件消息一起发，你应该先看到这条消息，后看到文件'],close_wechat=True)
```
#### 效果演示:
![Alt text](https://github.com/Hello-Mr-Crab/pywechat/blob/main/pics/效果演示.gif)

<br>

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

## 注意:
请勿将pywechat用于任何非法商业活动,因此造成的一切后果由使用者自行承担！
