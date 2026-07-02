# Change Log

## Add

> - src\pyweixin\WeChatAuto.py\class AutoReply\auto_reply_messages:在会话列表内自动回复所有新消息
> - src\pyweixin\WeChatAuto.py\class Monitor\listen_on_sessionList:指定时间内监听会话列表内的新消息好友与数量
> - src\pyweixin\WeChatAuto.py\class Monitor\listen_on_newMessages:在listen_on_sessionList的基础上最后把新消息好友的消息全部导出
> - src\pyweixin\WeChatAuto.py\class Collections\save_files:把收藏内的文件导出到本地

## Changed

> - 修改了`README.md`
> - 修改了src\pyweixin\WeChatAuto.py\class Collections\save_notes逻辑
> - 修改了src\pyweixin\WeChatAuto.py\class Collections\cardLink_to_url逻辑

## ToDo

- 维护内部方法保证稳定性...
- 开发Mcp...
- 维护Skill..
- 增加日志模块(感觉不太适合,主要是一些静态方法，@staticmethod+@logging自定义装饰器,无法看到DocString🤔)
