
# Pywechat(3.9+微信)

(x86平台才可使用!)

## WechatTools🌪️

## 类包括

- Tools:关于PC微信的一些工具,包括打开PC微信内各个界面的open系列方法

- API:打开指定微信小程序，指定公众号,打开视频号的功能，若有其他开发者想自动化操作上述程序可调用此API

函数:该模块内所有函数与方法一致

### WechatAuto🛏️

#### class

- `Messages`: 5种类型的发送消息方法，包括:单人单条,单人多条,多人单条,多人多条,转发消息:多人同一条。
- `Files`: 5种类型的发送文件方法，包括:单人单个,单人多个,多人单个,多人多个,转发文件:多人同一个。发送多个文件时，你只需将所有文件放入文件夹内，将文件夹路径传入即可。
- `FriendSettings`: 涵盖了PC微信针对某个好友的全部操作的方法。
- `GroupSettings`: 涵盖了PC微信针对某个群聊的全部操作的方法。
- `Contacts`: 获取3种类型通讯录好友的备注与昵称包括:微信好友,企业号微信,群聊名称与人数，数据返回格式为json。
- `Call`: 给某个好友打视频或语音电话。
- `AutoReply`:自动接听微信视频或语音电话,自动回复指定好友消息,自动回复所有好友消息。
- `Moments`:针对微信朋友圈的一些方法,包括数据获取，图片视频导出

##### 该模块内所有函数与方法一致

#### WinSettings🔹

##### 类

- Systemsettings:该模块中提供了一些修改windows系统设置的方法

##### 函数：该模块内所有函数与类内方法一致

### pywechat使用示例

#### 所有自动化操作只需两行代码即可实现

```python
from pywechat import xxx
xxx.yy

from pyweixin import xxx
xxx,yy
```

</br>

#### 在某个群聊自动回复(使用装饰器自定义回复内容)

```python
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

![decorator](/pics/decorator.png "decorator")
</br>

#### 监听某个群聊或好友的窗口(自动保存聊天文件与图片和视频)

```python
from pywechat import listen_on_chat
filesave_folder=r"E:\Desktop\保存文件"
mediasave_folder=r"E:\Desktop\聊天图片与视频保存"
contents,senders,types=listen_on_chat(friend='测试群',duration='10min',save_file=True,file_folder=filesave_folder,save_media=True,media_folder=mediasave_folder)
print(contents,senders,types)
```

#### 朋友圈数据获取

```python
from pywechat import dump_recent_moments
moments=dump_recent_moments(recent='Today',number=20,save_detail=True)
for dict in moments:
    print(dict)
```

![朋友圈数据获取](/pics/朋友圈数据获取.png "朋友圈")

注意，导出的结果为list[dict],每一条朋友圈对应一个dict,dict具体内容

{'好友备注':'','发布时间':'','文本内容':'','点赞者':'','评论内容':'','图片数量':'','视频数量':'','卡片链接':'','卡片链接内容':'','视频号':'','公众号链接内容':''}

</br>

#### 监听整个会话列表内所有好友的新消息(自动保存聊天文件)

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
