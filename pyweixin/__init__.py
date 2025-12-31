
'''
pyweixin
========


pywechat下的微信4.0版本的自动化工具
    可前往 'https://github.com/Hello-Mr-Crab/pywechat' 查看详情


Modules
-------
    - `WechatTools`: 该模块中封装了Tools与Navigator两个静态类,主要用来辅助WeChatAuto实现其他自动化功能
    - `WechatAuto`: pyweixin的主要模块,其内部包含
    - `Winsettings`: 一些修改windows系统设置的方法
    - `Uielements`: 微信主界面内UI的封装
    - `Warnings`: 一些可能触发的警告


支持版本:
    - `操作系统`: window10,windows11
    - `Python版本`: 3.8+(需支持TypeHint)

    
Have fun in WechatAutomation (＾＿－)
====
'''
from pyweixin.WeChatAuto import *
from pyweixin.WeChatTools import *
from pyweixin.WinSettings import *
from pyweixin.Config import *
#Author:Hello-Mr-Crab
#version:1.9.7