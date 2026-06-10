# Change Log

## Add

> - Mcp:开发ing...
> - Skill\openclaw\pyweixin-rpa:适用于openclaw的pyweixi kill目前已于clawhub发布，名称为pyweixin-rpa
> - Skill\otherplatforms\pyweixin-rpa:适用于其他平台的pyweixin skill(codex,claude,cursor..)
> - [QuickStart.md](/QuickStart.md):对上手使用pyweixin的说明

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
