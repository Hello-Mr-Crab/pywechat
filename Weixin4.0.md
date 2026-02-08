# 微信4.1+ UI自动化说明

## UI可见方式
讲述人模式先于微信登录前运行，持续一段时间后(5min以上)关闭讲述人。
有大佬反应，开启讲述人模式后微信的UI便可以一览无余，经过测试发现的确如此，但要保证讲述人模式先于微信登录前运行，然后持续一段时间(5min以上)再关闭讲述人，就可以进行正常的自动化了。
同时，在实际使用时发现,使用次数若比较频繁(经常在微信登录前打开讲述人)，那么后续微信的UI屏蔽将不在存在，可以直接看到内部UI结构，且此状态会一直持续(可能是微信有相关缓存机制)。

## 已经实现的一些方法(pyweixin内)
- WeChatTools.Navigator
- WechatTools.Tools
- WeChatAuto.Messages
- WeChatAuto.Files
- WeChatAuto.Call
- WeChatAuto.Monitor
- WeChatAuto.Moments
- WeChatAuto.AutoReply
- WeChatAuto.Contacts
  
## 原理:
Windows的可访问性API（UI Automation）在设计上必须向屏幕阅读器暴露所有UI元素的信息（包括隐藏、禁用元素）
这是为了确保视障用户能够通过讲述人完整了解界面结构，若应用程序直接阻止这种底层访问，会违反无障碍设计原则。

## 特例:
该方法对隔壁的企业微信无用，意味着企业微信相较于微信对UI自动化的限制更严格，也意味着微信可能会采取同样的策略(目前还没发现)
但再整体考虑到微信与企业微信的受众群众来说，微信可能短时间内还不会采取这种极端策略。当然，这也与企业微信要推广自己家的API有关。

## 说明
此方法若稳定且不会被修复的话，后续将持续更新，目前可用功能已全部在Pyweixin内。

## 使用方式
由于UI框架更换，完全替换原代码需要一定时间，现将已经实现的部分代码分享出来，可以先pip install -r requirements.txt后将pyweixin git到本地后可直接使用
随时欢迎大家在pyweixin源码基础上改进和增加新功能，随时欢迎大家pr！
