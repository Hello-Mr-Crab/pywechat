# Change Log

## Add

- Uielements\ClickPos:所有涉及鼠标坐标定位点击的位置
- Contacts.get_friends_name:快速获取通讯录内好友的备注(去重后的结果,与实际可能有出入)
- Contacts.get_wecom_friends_name:快速获取通讯录内企业微信好友的备注(去重后的结果,与实际可能有出入)
- Contacts.get_serAcc_name:快速获取通讯录内服务号的备注(去重后的结果,与实际可能有出入)
- Contacts.get_offAcc_name:快速获取通讯录内公众号的备注(去重后的结果,与实际可能有出入)

## Changed

- Config.py/GlobalConfig:微信语言和版本自动识别
- Navigator.open_weixin:更换打开微信方法,速度更快
- Contacts.check_my_info:更换打开个人简介方法,获取个人信息速度更快
- Contacts.get_groupMembers_info:更换打开群成员列表方法,获取群成员昵称速度更快

## ToDo

- 维护内部方法保证稳定性
- 在此基础上开发skill
- 增加日志模块
