# Change Log

## Add

> - src\pyweixin\WeChatAuto.py\class AutoReply\auto_reply_messages:在会话列表内自动回复所有新消息
> - src\pyweixin\WeChatAuto.py\class Monitor\listen_on_sessionList:指定时间内监听会话列表内的新消息好友与数量
> - src\pyweixin\WeChatAuto.py\class Monitor\listen_on_newMessages:在listen_on_sessionList的基础上最后把新消息好友的消息全部导出

## Changed

> - 修改了`README.md`
> - 测试与修改了pyweixin内所有的自动化操作方法(WeChatTools与WeChatAuto),目前在作者本人电脑上均可正常运行
> - **更改了项目结构**:将源码移动到了src内,新增Skill与Mcp(还未开发),新增QuickStart.md使用说明
> - pyweixin操作手册:修改了内部一些方法的参数增加了目录

## ToDo

- 维护内部方法保证稳定性...
- 开发Mcp...
- 维护Skill..
- 增加日志模块(感觉不太适合,主要是一些静态方法，@staticmethod+@logging自定义装饰器,无法看到DocString🤔)
