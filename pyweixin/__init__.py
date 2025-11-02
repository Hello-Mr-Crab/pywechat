
'''
pyweixin
========


pywechat下的微信4.0版本的自动化工具
    目前仅实现了简单的发送消息打电话等功能
    可前往 'https://github.com/Hello-Mr-Crab/pywechat' 查看详情


模块:
====


WechatTools:
------------
该模块中封装了一系列关于4.0版本微信的工具,主要包括:检测微信运行状态
打开微信主界面内绝大多数界面;打开指定公众号与微信小程序以及视频号


WechatAuto:
-----------
pywechat的主要模块,其内部包含:
    - `Messages`:发送消息功能包括:单人发消息,,多人发消息,转发消息
    - `Files`:发送文件功能包括:单人发文件,多人发文件,转发文件
    - `Call`:给某个好友打视频或语音电话,在群聊内发起语音电话

---------------------
Winsettings:一些修改windows系统设置的方法
----------------------
Uielements:微信主界面内UI的封装
-----------------
Clocks:用于实现pyweixin内所有方法定时操作的模块
-----------------
Warnings:一些可能触发的警告
-----------------------
支持版本
---------------
OS-Version:window10,windows11
----------------------------
Python-version:3.x,WechatVersion:>4.0.6\n
----------------------------------
Have fun in WechatAutomation (＾＿－)
====
'''
from pyweixin.WeChatAuto import *
from pyweixin.WeChatTools import *
from pyweixin.WinSettings import *
from pyweixin.Config import *
#Author:Hello-Mr-Crab
#version:1.9.6