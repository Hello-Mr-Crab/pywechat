
'''
pyweixin
========


pywechat下的微信4.0版本的自动化工具
    可前往 'https://github.com/Hello-Mr-Crab/pywechat' 查看详情


Modules
-------
    - `WeChatTools`:  该模块中封装了Tools与Navigator两个静态类,主要用来辅助WeChatAuto实现其他自动化功能
    - `WeChatAuto`:  pyweixin的主要模块,其内部包含消息,通讯录,文件,好友设置,朋友圈,自动回复,消息监控,微信设置这几个功能对应的静态类
    - `WinSettings`:  一些修改windows系统设置的方法
    - `Uielements`:  微信主界面内各种UI元素的POM封装(kwargs格式,适用于pywinauto的window,child_window,descendants,children四种定位元素方法)
    - `utils.py`:  内置一些配合WeChatAuto实现自动化的函数,比如@好友,遍历会话列表扫描新消息等
    - `Warnings`:  一些可能触发的警告
 
Examples:
--------

使用pyweixin时,你可以:

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


支持版本:
--------
    - `操作系统`:  window10,windows11
    - `Python版本`: 3.10+(需支持TypeHint)
    - `微信版本`:  4.1+

    
注意:
-----
    使用pyweixin时要保证微信已经登录!

    
Have fun in WechatAutomation (＾＿－)
====
'''
from pyweixin.WeChatAuto import AutoReply,Collections,Call,Contacts,Files,FriendSettings,Messages,Moments,Monitor,Settings
from pyweixin.WeChatTools import Tools,Navigator
from pyweixin.WinSettings import SystemSettings
from pyweixin.Config import GlobalConfig
#@Author:Hello-Mr-Crab,
#@Contributor:Chanpoe,ImViper,clen1,mrhan1993,nmhjklnm,guanjt3
#@version:1.9.8