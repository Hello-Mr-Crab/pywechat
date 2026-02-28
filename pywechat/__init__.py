
'''
pywechat
========

一个windows系统下的PC微信自动化工具
可前往 'https://github.com/Hello-Mr-Crab/pywechat' 获取操作文档

模块:
====

WeChatTools:
------------
该模块中封装了一系列关于PC微信的工具与Tools这个静态类内,主要用来:检测微信运行状态;
打开微信主界面内绝大多数界面;打开指定公众号与微信小程序以及视频号

WeChatAuto:
-----------
pywechat的主要模块,其内部包含了:
-   AutoReply:包含类似QQ的自动回复指定好友与群聊消息
-   Call:给某个好友打视频或语音电话,在群聊内发起语音电话
-   Contacts:获取微信所有好友详细信息(昵称,备注,地区，标签,个性签名,共同群聊,微信号,来源),获取群聊信息(群聊名称与人数),获取群聊内所有群成员的群昵称
-   Files:发送文件和导出文件功能
-   FriendSettings:涵盖了PC微信针对某个好友的全部操作
-   GroupSettings:涵盖了PC微信针对某个群聊的全部操作
-   Messages:5种类型的发送消息功能包括:单人单条,单人多条,多人单条,多人多条,转发消息:多人同一条消息
-   Monitor:微信消息小窗监听
-   Monments:针对微信朋友圈的一些操作
-   Settings:用于修改PC微信设置

WinSettings:
----------------------
一些修改windows系统设置的方法

Uielements:
-----------------
微信主界面内UI的封装

Warnings:
-----------------------
一些可能触发的警告

Errors:
-----------------------
一些可能触发的错误

支持版本
---------------
-   OS-Version:windows7,window10(x86)
-   Python-version:3.9+(win7最高支持版本)
-   WeChatVersion:3.9.12.5x

----------------------------------
Have fun in WechatAutomation (＾＿－)
====
'''
import sys
from.WeChatAuto import AutoReply,Call,Contacts,Files,FriendSettings,GroupSettings,Messages,Monitor,Moments,Settings
from.WeChatTools import Tools,Navigator
from.Errors import NotInstalledError
if sys.maxsize==2**63-1:#64位操作系统
    raise ImportError(f'3.9版本微信已无法在64位Windows系统上使用,使用32位Window系统才可以导入使用pywechat!')
if not Tools.is_wechat_installed():
    raise NotInstalledError
#Author:Hello-Mr-Crab
#Contributor:Chanpoe,mrhan1993
#version:1.9.8

