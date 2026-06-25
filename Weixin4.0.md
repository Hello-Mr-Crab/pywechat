# 微信4.1+ UI自动化说明

## UI可见方式

目前使用讲述人的方式来使UI树可见的方式已经失效,唯一可行的方法只有:

- 在本地电脑上登录一个UI树可见的账号使用
- 将无法看到ui树的账号在别的ui树可见的电脑上登录,然后再登回到自己的电脑上，之后UI树便会持续可见(可能是微信有相关缓存机制)

## 已经实现的一些方法(pyweixin内)

- WeChatTools.Navigator
- WeChatTools.Tools
- WeChatAuto.AutoReply
- WeChatAuto.Call
- WeChatAuto.Collections
- WeChatAuto.Contacts
- WeChatAuto.Files
- WeChatAuto.Messages
- WeChatAuto.Moments
- WeChatAuto.Monitor
- WeChatAuto.Settings
  
## 原理

Windows的可访问性API（UI Automation）在设计上必须向屏幕阅读器暴露所有UI元素的信息（包括隐藏、禁用元素）
这是为了确保视障用户能够通过讲述人完整了解界面结构，若应用程序直接阻止这种底层访问，会违反无障碍设计原则。

## 特例

该方法对隔壁的企业微信无用，意味着企业微信相较于微信对UI自动化的限制更严格，也意味着微信可能会采取同样的策略(目前还没发现)
但再整体考虑到微信与企业微信的受众群众来说，微信可能短时间内还不会采取这种极端策略。当然，这也与企业微信要推广自己家的API有关。

## 关于微信更新后UI树突然消失

有不少人反映，自己的微信版本更新后便无法获取到UI树了,无论是运行讲述人还是修改讲述人注册表都无济于事。不过，在切换不同账号后又会可见并可以继续使用。这个可能是微信针对账号的使用情况进行了一定的评估，限制了其UIAutomation功能。这边建议合理适度地使用UIAutomation工具，不要作出频繁添加好友,发送骚扰信息等这些违反微信用户条例的操作

## 说明

此方法若稳定且不会被修复的话，后续将持续更新，目前可用功能已全部在Pyweixin内。

## 使用方式

参考[QuickStart.md](/QuickStart.md)
