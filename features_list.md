# Fix Log

## Add

- Contacts.get_groupMembers_info:获取群成员昵称
- Contacts.get_friends_name:快速获取通讯录内好友的备注(去重后的结果,与实际可能有出入)
- Navigator.capture_Login_QRCode:截图并保存登录二维码
- Moments.dump_recent_posts:增加with_name参数,是否获取朋友圈发布人默认为False,save_detail设置
为True支持导出朋友圈的详细数据:内容.txt,图片或视频,单条朋友圈的截图到本地,save_detail设置为True时,with_name自动设置为True，save_detrail默认为False
- Messages.pull_messages:返回值中增加了消息类型
- Messages.dump_chat_history:返回值中增加了消息类型,save_detail支持保存图片视频文件到本地,支持获取转发的聊天记录内容
- Moments.like_posts:增加with_name参数,是否获取朋友圈发布人
- Moments.post_notes:支持在朋友圈发布笔记(笔记内可以粘贴放置图片视频文件等内容,但单个大小不能超过100Mb)
- Monitor.grab_red_packet:在指定时间内监听红包事件并点击打开(可以用来抢红包...)
- utils\parse_chat_history:解析私聊聊天记录
- utils\parse_group_chat_history:解析群聊聊天记录(群聊的发送人与个人获取方式不同)

## Changed

- pyweixin操作手册.docx:更新了pyweixin操作手册.docx
- Regex_Pattern,Special_label,TimeStamp三个类移动到Uielements内
- Navigator.open_weixin:无法识别定位到微信主界面时自动打开讲述人
- Tools.language_detector:对wechatappex.exe命令行增加限制,防止语言获取失败
- Call.voice_call:增加wait参数(默认为False),可以等待60s直到对方接通(微信自动挂断时长限制60s),接通后返回音视频通话窗口的WindowSpecification对象
- Call.video_call:增加wait参数(默认为False),可以等待60s直到对方接通(微信自动挂断时长限制60s),接通后返回音视频通话窗口的WindowSpecification对象
- Navigator.open_friend_moments:修改打开好友朋友圈逻辑：先定位朋友圈文本的父控件再定位内部按钮点击。这样可以避免查找朋友圈按钮失败
- Moments.dump_friend_posts():修改了post_time的查找逻辑,使用re.findall()[-1],保证内容本身可能含有的时间戳对真正的时间戳定位不受影响(真正的时间戳一定在最后)
- Moments.dump_recent_posts:修改了post_time的查找逻辑,使用re.findall()[-1],保证内容本身可能含有的时间戳对真正的时间戳定位不受影响(真正的时间戳一定在最后)
- Moments.like_posts:修改了post_time的查找逻辑,使用re.findall()[-1],保证内容本身可能含有的时间戳对真正的时间戳定位不受影响(真正的时间戳一定在最后)
- Moments.like_friend_posts:修改了post_time的查找逻辑,使用re.findall()[-1],保证内容本身可能含有的时间戳对真正的时间戳定位不受影响(真正的时间戳一定在最后)
- Messages.search_chat_history:增加数量限制
