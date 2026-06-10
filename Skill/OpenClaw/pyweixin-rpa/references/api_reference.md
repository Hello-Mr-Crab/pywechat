# pyweixin RPA API Reference

> **用途**: 调用 `pyweixin` 中的静态方法时，阅读此文档以获取完整的方法签名、参数说明、返回值和 Python 代码示例。
>
> **核心原则**: 所有方法均为 **静态方法**，无需实例化类。直接 `ClassName.method()` 调用。

---

## 目录

- [模块导入](#模块导入)
- [全局配置 GlobalConfig](#全局配置-globalconfig)
- [WeChatAuto — 自动化主模块](#wechatauto--自动化主模块)
  - [Messages — 消息操作](#1-messages--消息操作)
  - [Files — 文件操作](#2-files--文件操作)
  - [Contacts — 联系人信息](#3-contacts--联系人信息)
  - [FriendSettings — 好友管理](#4-friendsettings--好友管理)
  - [AutoReply — 自动回复](#5-autoreply--自动回复)
  - [Monitor — 消息监听](#6-monitor--消息监听)
  - [Collections — 收藏操作](#7-collections--收藏操作)
  - [Call — 语音/视频通话](#8-call--语音视频通话)
  - [Moments — 朋友圈操作](#9-moments--朋友圈操作)
  - [Settings — 微信设置](#10-settings--微信设置)
- [WeChatTools — 辅助工具模块](#wechattools--辅助工具模块)
  - [Navigator — 界面导航](#1-navigator--界面导航)
  - [Tools — 路径查询与工具](#2-tools--路径查询与工具)
- [WinSettings — Windows 系统设置](#winsettings--windows-系统设置)
- [utils — 工具函数](#utils--工具函数)
- [注意事项](#注意事项)

---

## 模块导入

> ⚠️ **自定义脚本五要素**
>
> 1. 导入前必须 `sys.path.insert(0, 'scripts')`（避免 pip 包冲突）
> 2. `dump_chat_history` 返回 `list[dict]`，**不要解包为两个变量**（不是 `tuple[list, list]`）
> 3. 返回值以本 API Reference 文档为准，**不需要也不建议先跑探针**——文档已从源码提取每个方法的准确返回类型和结构
> 4. **已拉取的数据不要重复拉取**：拿到 `list[dict]` 后传给下游函数处理，不要再调用一次 `dump_chat_history`
> 5. **定时任务用 OpenClaw cron 触发，脚本里不写任何定时逻辑**：`sessionTarget="main"` + `payload.kind="systemEvent"` 让主 session 到点执行脚本

```python
import sys
sys.path.insert(0, 'scripts')

from pyweixin import Messages, Files, Contacts
from pyweixin import FriendSettings, AutoReply, Monitor, Collections, Call
from pyweixin import Moments, Settings
from pyweixin import Tools, Navigator
from pyweixin import SystemSettings
from pyweixin.Config import GlobalConfig
```

**通用参数说明**（以下参数在多方法中共享，实际默认值均为 `None`，全局配置见 GlobalConfig）：

| 参数 | 类型 | 默认值 | 说明 |
| ------ | ------ | -------- | ------- |
| `is_maximize` | `bool` | `None` | 微信主界面是否全屏，未设置时默认不改变 |
| `close_weixin` | `bool` | `None` | 任务结束后是否关闭微信，未设置时默认不关闭 |
| `search_pages` | `int` | `None` | 在会话列表中查找好友的页数（1页≈5-12人）；设为 `0` 时直接从顶部搜索栏搜索 |
| `send_delay` | `float` | `None` | 输入后停顿秒数再发送，未设置时使用 GlobalConfig 默认值 0.2 |

> ⚠️ 大部分方法的 `is_maximize`、`close_weixin`、`search_pages`、`send_delay`、`clear` 实际默认值均为 `None`，
> 表示不覆盖全局配置 `GlobalConfig` 中的对应值。设 `None`（不传）即可保持与全局一致。
> 这与文档示例中的 `False` / `True` / `0.2` 不同——示例仅作演示，实际调用时建议使用 `GlobalConfig` 统一配置。

---

## 全局配置 GlobalConfig

```python
from pyweixin.Config import GlobalConfig
```

通过 `GlobalConfig` 可以设置全局位置参数，省去在每个方法中重复传入相同参数。

| 属性 | 类型 | 默认值 | 说明 |
| ------ | ------ | -------- | ------ |
| `is_maximize` | `bool` | `False` | 微信主界面全屏 |
| `close_weixin` | `bool` | `False` | 任务结束关闭微信 |
| `load_delay` | `float` | `3.5` | 打开小程序/视频号/公众号的加载等待时长 |
| `search_pages` | `int` | `5` | 会话列表搜索页数 |
| `window_maximize` | `bool` | `False` | 独立窗口全屏 |
| `send_delay` | `float` | `0.2` | 发送消息间隔 |
| `audio_length` | `int` | `60` | 语音消息长度(秒)，微信4.1.9+可用 |
| `clear` | `bool` | `True` | 发送前是否清空输入框 |
| `window_size` | `tuple` | `(1000, 1000)` | 主界面尺寸 |
| `language` | `str` | 自动检测 | 微信语言: `简体中文` / `English` / `繁體中文` |
| `Version` | `str` | 自动获取 | 微信版本号 |

```python
# 示例：全局配置
GlobalConfig.language = 'English'
GlobalConfig.load_delay = 3.5
GlobalConfig.is_maximize = True
GlobalConfig.close_weixin = False

Navigator.search_channels(search_content='微信4.0')
```

---

## WeChatAuto — 自动化主模块

### 1. Messages — 消息操作

#### `Messages.send_messages_to_friend()`

给 **单个好友** 发送消息。

```python
Messages.send_messages_to_friend(
    friend: str,
    messages: list[str],
    at_members: list[str] = [],        # [群聊] @的群成员
    at_all: bool = False,              # [群聊] @所有人
    search_pages: bool = None,
    clear: bool = None,
    send_delay: float = None,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> None
```

**返回值**: 无

```python
# 示例
from pyweixin import Messages

Messages.send_messages_to_friend(
    friend='文件传输助手',
    messages=['你好', '发消息测试'],
    close_weixin=False
)
```

---

#### `Messages.send_messages_to_friends()`

给 **多个好友** 分别发送消息。

```python
Messages.send_messages_to_friends(
    friends: list[str],
    messages: list[list[str]],        # 每个好友对应一组消息
    clear: bool = None,
    send_delay: float = None,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> None
```

**返回值**: 无

```python
# 示例
Messages.send_messages_to_friends(
    friends=['文件传输助手', 'Hello,Mr Crab'],
    messages=[['你好', '发消息测试'], ['你好', '发消息测试']]
)
```

---

#### `Messages.check_new_messages()`

检查所有 **带新消息提示** 的好友，逐个打开并获取消息内容。

```python
Messages.check_new_messages(
    is_maximize: bool = None,
    search_pages: int = None,
    close_weixin: bool = None
) -> dict[str, list[dict]]
```

**返回值**: `dict[str, list[dict]]` — `{好友备注: [消息列表], ...}`

消息列表的每项格式同 `pull_messages`：`{'消息发送人', '消息内容', '消息类型', '消息发送时间'}`

```python
# 示例
new = Messages.check_new_messages(search_pages=0)
for friend, msgs in new.items():
    print(f'{friend}: {len(msgs)} 条新消息')
```

---

#### `Messages.dump_recent_sessions()`

导出 **最近聊天对象** 的名称和摘要。

```python
Messages.dump_recent_sessions(
    recent: Literal['Today', 'Yesterday', 'Week', 'Month', 'Year'] = 'Today',
    chat_only: bool = False,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> list[tuple]
```

**返回值**: `list[tuple]` — `[('发送人', '最后聊天时间', '最后聊天内容'), ...]`

```python
# 示例
sessions = Messages.dump_recent_session(recent='Week')
print(sessions)
```

---

#### `Messages.dump_sessions()`

导出 **所有聊天对象** 名称。

```python
Messages.dump_sessions(
    chat_only: bool = False,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> list[tuple]
```

**返回值**: `list[tuple]` — `[('发送人', '最后聊天时间', '最后聊天内容'), ...]`

```python
# 示例
sessions = Messages.dump_sessions()
```

---

#### `Messages.dump_chat_history()`

导出 **与指定好友的聊天记录**。

```python
Messages.dump_chat_history(
    friend: str,
    number: int,
    search_content: str = None,    # 按内容过滤
    groupMembers: list[str]=[]     # 群成员列表。获取的是群聊的聊天记录时如果传入了该参数不需要遍历两次来获取发送人
    is_json: bool = False,        # 返回值为list[dict]格式的JSON字符串
    save_detail: bool = False,     # 保存详细信息到文件
    target_folder: str = None,     # 保存目录
    search_pages: int = None,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> list[dict]
```

**返回值**: `list[dict]` — 每条消息一个字典，键如下：

| 键 | 类型 | 示例 |
| ------ | ------ | ------- |
| `消息发送人` | `str` | `'Hello,Mr Crab'` |
| `消息内容` | `str` | `'你好'` / `'图片'` / `'文件\nxxx.zip\n1.2M\n微信电脑版'` |
| `消息类型` | `str` | `'文本'` / `'图片'` / `'文件'` / `'视频号'` / `'链接'` / `'微信礼物'` |
| `消息发送时间` | `str` | `'2026年6月2日 09:24'` |

```python
# 示例
result = Messages.dump_chat_history(friend='文件传输助手', number=5, close_weixin=False)
for msg in result:
    print(f"[{msg['消息发送时间']}] {msg['消息发送人']}: {msg['消息内容']}")
```

---

#### `Messages.search_chat_history()`

按 **关键字** 搜索所有聊天记录。

```python
Messages.search_chat_history(
    keyword: str,
    number: int = None,
    with_content: bool = False
    is_maximize: bool = None,
    close_weixin: bool = None
) -> dict[str, (int|list[str])]
```

**返回值**: `dict[str, (int|list[str])]` — `{好友备注: (聊天记录数量|[匹配的聊天内容列表].}`,返回值字典中键的类型由采纳数

**with_content**参数说明：

- 当with_content为True时,自动化过程中获取每一个好友名下的聊天记录具体内容
- 当with_content为False时,自动化过程中只获取具体数量
`with_content参数默认为False`,使用该函数前及得询问用户是否要获取具体的聊天记录内容

```python
# 示例
results = Messages.search_chat_history(keyword='你好', number=5)
for friend, msgs in results.items():
    print(f'{friend}:')
    for m in msgs:
        print(f'  {m}')
```

---

#### `Messages.pull_messages()`

拉取指定好友的聊天消息（只读当前可视区域，不滚动窗口，比 `dump_chat_history` 更轻量）。

```python
Messages.pull_messages(
    friend: str,
    number: int,
    groupMembers: list[str] = []
    is_json: bool = False,
    search_pages: int = None,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> list[dict]
```

**groupMembers参数说明**: 参数groupMembers是群成员列表，当friend为群聊时如果传入了该参数不需要遍历两次来获取发送人

**返回值**: `list[dict]` — 同 `dump_chat_history` 格式（`消息发送人`、`消息内容`、`消息类型`）

```python
# 示例
msgs = Messages.pull_messages(friend='文件传输助手', number=3, close_weixin=False)
for m in msgs:
    print(f"[{m['消息发送人']}: {m['消息内容']}")
```

---

#### `Messages.save_media()`

**保存** 好友聊天中的媒体文件（图片/视频/文件）。

```python
Messages.save_media(
    friend: str,
    number: int,
    target_folder: str = None,
    is_maximize: bool = None,
    close_weixin: bool = None,
    search_pages: int = None
) -> None
```

**返回值**: 无（文件直接保存到目标目录）

```python
# 示例
Messages.save_media(friend='文件传输助手', number=5)
```

---

#### `Messages.send_audios_to_friend()`

给 **单个好友** 发送音频/语音文件。

```python
Messages.send_audios_to_friend(
    friend: str,
    audios: list[str],
    audio_length: int = None,        # 语音长度(秒)，微信 4.1.9+ 可用
    clear: bool = None,
    send_delay: int = None,
    search_pages: int = None,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> None
```

**返回值**: 无

```python
# 示例
Messages.send_audios_to_friend(
    friend='文件传输助手',
    audios=[r"E:\Desktop\music.mp3"],
    close_weixin=False
)
```

---

#### `Messages.message_chain()`

**消息接龙** 操作（在群聊中发起或参与消息接龙）。

```python
Messages.message_chain(
    group: str,
    content: str = None,
    theme: str = None,
    example: str = None,
    description: str = None,
    search_pages: int = None,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> None
```

**返回值**: 无

```python
# 示例
Messages.message_chain(group='Pywechat 测试群', content='接龙内容', close_weixin=False)
```

---

#### `Messages.accept_group_invitation()`

**接受群聊邀请**。

```python
Messages.accept_group_invitation(
    friend: str,
    number: int,
    max_num: int = 100,
    is_maximize: bool = None,
    close_weixin: bool = None,
    search_pages: int = None
) -> list[list[str]] | str
```

**返回值**: 混合类型

- `list[list[str]]` — `[成员列表, 群名额列表]` 正常返回
- `str` — 错误描述（如 `'网络异常,未能正确打开群聊邀请界面'`）

```python
# 示例
result = Messages.accept_group_invitation(friend='Pywechat 测试群', number=5, close_weixin=False)
if isinstance(result, str):
    print(f'邀请失败: {result}')
else:
    members, slots = result
    print(f'新成员: {members}, 群名额: {slots}')
```

---

### 2. Files — 文件操作

#### `Files.send_files_to_friend()`

给 **单个好友** 发送文件。

```python
Files.send_files_to_friend(
    friend: str,
    files: list[str],
    with_messages: bool = False,
    messages: list[str] | None = None,
    messages_first: bool = False,
    clear: bool = None,
    send_delay: float = None,
    search_pages: int | bool = None,      # ⚠️ 实际类型为 bool
    is_maximize: bool = None,
    close_weixin: bool = None
) -> None
```

**返回值**: 无

```python
# 示例
Files.send_files_to_friend(
    friend='文件传输助手',
    files=[r"E:\Desktop\背景1.png", r"E:\Desktop\android.py"],
    close_weixin=False
)
```

> ⚠️ `files` 参数是文件路径列表，不是文件夹路径。需自己遍历目录构造路径列表。

---

#### `Files.send_files_to_friends()`

给 **多个好友** 分别发送文件。

```python
Files.send_files_to_friends(
    friends: list[str],
    files_list: list[list[str]],           # 每个好友对应一组文件路径
    with_messages: bool = False,
    messages_list: list[list[str]] = [],
    messages_first: bool = False,
    clear: bool = None,
    send_delay: float = None,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> None
```

**返回值**: 无

```python
# 示例
Files.send_files_to_friends(
    friends=['文件传输助手', 'Hello,Mr Crab'],
    files_list=[
        [r"E:\Desktop\背景1.png", r"E:\Desktop\android.py"],
        [r"E:\Desktop\背景1.png", r"E:\Desktop\android.py"]
    ]
)
```

---

#### `Files.save_chatfiles()`

**保存** 好友聊天中的文件到本地。

```python
Files.save_chatfiles(
    friend: str,
    number: int,
    target_folder: str = None,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> tuple[str, str] | tuple[list[str], list[str]]
```

**返回值**: `(filenames, timestamps_folder)` — `(文件名列表, 对应年月文件夹列表)`

```python
# 示例
filenames, folders = Files.save_chatfiles(friend='文件传输助手', number=10)
print(f'保存了 {len(filenames)} 个文件到 {folders}')
```

---

#### `Files.export_wxfiles()`

导出微信按 **年月存储** 的聊天文件。

```python
Files.export_wxfiles(
    year: str | None = None,               # 默认当年
    month: str | None = None,              # 默认当月
    target_folder: str | None = None
) -> list[str]
```

**返回值**: `list[str]` — 导出的文件路径列表

```python
# 示例
exported = Files.export_wxfiles(year='2024', month='10')
print(exported)
```

---

#### `Files.export_videos()`

导出微信按 **年月存储** 的聊天视频。

```python
Files.export_videos(
    year: str | None = None,
    month: str | None = None,
    target_folder: str | None = None
) -> list[str]
```

**返回值**: `list[str]` — 导出的视频文件路径列表

```python
# 示例
exported = Files.export_videos(year='2024', month='10')
print(exported)
```

---

#### `Files.export_recent_files()`

导出 **最近使用** 的聊天文件。

```python
Files.export_recent_files(
    target_folder: str | None = None,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> list[str]
```

**返回值**: `list[str]` — 导出的文件路径列表

```python
# 示例
exported = Files.export_recent_files()
print(exported)
```

---

### 3. Contacts — 联系人信息

#### `Contacts.get_friends_detail()`

获取 **所有好友** 的详细信息。

```python
Contacts.get_friends_detail(
    is_maximize: bool = None,
    close_weixin: bool = None,
    is_json: bool = False
) -> list[dict] | str
```

**返回值**: `list[dict]` — 每个好友的详细资料（微信号、昵称、备注、手机号等）；`is_json=True` 时返回 JSON 字符串。

```python
# 示例
friends = Contacts.get_friends_detail()
for f in friends:
    print(f['昵称'], '-', f.get('备注', ''))
```

---

#### `Contacts.check_my_info()`

获取 **自己的个人资料**。

```python
Contacts.check_my_info(
    is_maximize: bool = None,
    close_weixin: bool = None
) -> dict
```

**返回值**: `dict` — `{'昵称', '微信号', '地区', 'wxid'}`

```python
# 示例
my_info = Contacts.check_my_info()
print(f"昵称: {my_info['昵称']}, wxid: {my_info['wxid']}")
```

---

#### `Contacts.check_new_friends()`

**检查新朋友** 申请。

```python
Contacts.check_new_friends(
    verify: bool = False,
    limit: int = 8,
    clear: bool = False,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> bool | list[str]
```

**返回值**: `bool` — 有/无新朋友申请；`verify=True` 时自动通过并返回 `list[str]`

```python
# 示例
result = Contacts.check_new_friends(verify=True)
print(result)
```

---

#### `Contacts.get_groups_info()`

获取所有已加入 **群聊** 的名称列表。

```python
Contacts.get_groups_info(
    is_maximize: bool = None,
    close_weixin: bool = None
) -> list[str]
```

**返回值**: `list[str]` — 群聊名称列表

```python
# 示例
groups = Contacts.get_groups_info()
print(groups)
```

---

#### `Contacts.get_wecom_friends_detail()`

获取所有 **企业微信好友** 信息。

```python
Contacts.get_wecom_friends_detail(
    is_maximize: bool = None,
    close_weixin: bool = None,
    is_json: bool = False
) -> list[dict] | str
```

**返回值**: `list[dict]` — 同 `get_friends_detail` 格式

```python
# 示例
details = Contacts.get_wecom_friends_detail()
```

---

#### `Contacts.get_wecom_friends_info()`

获取所有 **企业微信好友备注**。

```python
Contacts.get_wecom_friends_info(
    is_maximize: bool = None,
    close_weixin: bool = None
) -> list[str]
```

**返回值**: `list[str]` — 企业微信好友备注列表

```python
# 示例
names = Contacts.get_wecom_friends_info()
```

---

#### `Contacts.get_common_groups()`

获取与指定好友的 **共同群聊**。

```python
Contacts.get_common_groups(
    friend: str,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> list[str]
```

**返回值**: `list[str]` — 共同群聊名称列表

```python
# 示例
common_groups = Contacts.get_common_groups(friend='Hello,Mr Crab')
for g in common_groups:
    print(g)
```

---

#### `Contacts.get_serAcc_detail()`

获取所有 **服务号** 信息。

```python
Contacts.get_serAcc_detail(
    is_maximize: bool = None,
    close_weixin: bool = None,
    is_json: bool = False
) -> list[dict] | str
```

**返回值**: `list[dict]` — 服务号详情

```python
# 示例
services = Contacts.get_serAcc_detail()
```

---

#### `Contacts.get_serAcc_info()`

获取所有 **服务号名称**。

```python
Contacts.get_serAcc_info(
    is_maximize: bool = None,
    close_weixin: bool = None
) -> list[str]
```

**返回值**: `list[str]` — 服务号名称列表

```python
# 示例
names = Contacts.get_serAcc_info()
```

---

#### `Contacts.get_offAcc_detail()`

获取所有 **公众号** 信息。

```python
Contacts.get_offAcc_detail(
    is_maximize: bool = None,
    close_weixin: bool = None,
    is_json: bool = False
) -> list[dict] | str
```

**返回值**: `list[dict]` — 公众号详情

```python
# 示例
offacc = Contacts.get_offAcc_detail()
```

---

#### `Contacts.get_offAcc_info()`

获取所有 **公众号名称**。

```python
Contacts.get_offAcc_info(
    is_maximize: bool = None,
    close_weixin: bool = None
) -> list[str]
```

**返回值**: `list[str]` — 公众号名称列表

```python
# 示例
names = Contacts.get_offAcc_info()
```

---

#### `Contacts.get_friend_profile()`

获取 **指定好友** 的个人简介。

```python
Contacts.get_friend_profile(
    friend: str,
    search_pages: int = None,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> dict
```

**返回值**: `dict` — `{'昵称', '微信号', '地区', '备注', '电话', '手机'}`

```python
# 示例
profile = Contacts.get_friend_profile(friend='Hello,Mr Crab')
print(profile['备注'], profile['地区'])
```

---

#### `Contacts.get_recent_groups()`

获取 **最近活跃群聊** 信息。

```python
Contacts.get_recent_groups(
    is_maximize: bool = None,
    close_weixin: bool = None
) -> list[tuple[str, str]]
```

**返回值**: `list[tuple[str, str]]` — `[(群聊名, 群成员数), ...]`

```python
# 示例
recent = Contacts.get_recent_groups()
for name, num in recent:
    print(f'{name}: {num} 人')
```

---

#### `Contacts.get_groupMembers_info()`

获取指定群聊的 **群成员** 名称列表。

```python
Contacts.get_groupMembers_info(
    group: str,
    is_maximize: bool = None,
    search_pages: int = None,
    close_weixin: bool = None
) -> list[str]
```

**返回值**: `list[str]` — 群成员昵称列表

```python
# 示例
members = Contacts.get_groupMembers_info(group='Pywechat 测试群')
print(f'共 {len(members)} 名群成员')
```

---

#### `Contacts.get_friends_info()`

快速获取 **所有好友备注**。

```python
Contacts.get_friends_name(
    is_maximize: bool = None,
    close_weixin: bool = None
) -> list[str]
```

**返回值**: `list[str]` — 好友备注列表

```python
# 示例
names = Contacts.get_friends_info()
print(f'共 {len(names)} 个好友')
```

---

### 4. FriendSettings — 好友管理

所有 `FriendSettings` 方法返回值均为 `None`。

---

#### `FriendSettings.add_new_friend()`

**添加新朋友**。

```python
FriendSettings.add_new_friend(
    number: str,                    # 微信号
    greetings: str = None,          # 打招呼用语
    remark: str = None,             # 备注
    chat_only: bool = False,        # 仅聊天权限
    is_maximize: bool = None,
    close_weixin: bool = None
) -> None
```

**返回值**: 无

```python
# 示例
FriendSettings.add_new_friend(
    number='10086',
    greetings='你好,我是xxx',
    remark='新朋友'
)
```

---

#### `FriendSettings.block_friend()`

设置/取消将好友加入 **黑名单**。

```python
FriendSettings.block_friend(
    friend: str,
    state: int = 0,              # 0=取消黑名单, 1=加入黑名单
    search_pages: int = None,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> None
```

**返回值**: 无

```python
# 示例
FriendSettings.block_friend(friend='好友备注', state=1)   # 拉黑
FriendSettings.block_friend(friend='好友备注', state=0)   # 解除
```

---

#### `FriendSettings.pin_chat()`

设置/取消好友 **会话置顶**。

```python
FriendSettings.pin_chat(
    friend: str,
    state: int = 0,                # 1=置顶, 0=取消置顶
    search_pages: int = None,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> None
```

**返回值**: 无

```python
# 示例：置顶
FriendSettings.pin_chat(friend='测试ing', state=1)
```

---

#### `FriendSettings.star_friend()`

设置/取消 **星标朋友**。

```python
FriendSettings.star_friend(
    friend: str,
    state: int = 1,                # 1=设为星标, 0=取消星标
    search_pages: int = None,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> None
```

**返回值**: 无

```python
# 示例
FriendSettings.star_friend(friend='测试ing', state=1)
```

---

#### `FriendSettings.clear_chat_history()`

**清空** 与好友的聊天记录。

```python
FriendSettings.clear_chat_history(
    friend: str,
    search_pages: int = None,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> None
```

**返回值**: 无

```python
# 示例
FriendSettings.clear_chat_history(friend='测试ing')
```

---

#### `FriendSettings.mute_notification()`

设置/取消好友 **消息免打扰** 和 **折叠该聊**。

```python
FriendSettings.mute_notification(
    friend: str,
    mute: int = 0,               # 0=关闭免打扰, 1=开启免打扰
    fold_chat: int = 0,          # 0=不折叠, 1=折叠该聊
    search_pages: int = None,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> None
```

**返回值**: 无

```python
# 示例：开启免打扰
FriendSettings.mute_notification(friend='测试ing', mute=1)
```

---

#### `FriendSettings.change_remark()`

修改好友的 **备注、描述和电话**。

```python
FriendSettings.change_remark(
    friend: str,
    remark: str,                    # 新的备注名
    description: str = None,
    phoneNum: str = None,
    clear_phoneNum: bool = False,
    search_pages: int = None,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> None
```

**返回值**: 无

```python
# 示例
FriendSettings.change_remark(
    friend='测试ing',
    remark='起个破名想半天了'
)
```

---

#### `FriendSettings.change_privacy()`

修改好友 **权限**。

```python
FriendSettings.change_privacy(
    friend: str,
    chat_privacy: int = 1,          # 0=仅聊天, 1=聊天+朋友圈+微信运动
    sns_privacy: int = 0,           # 0=关闭, 1=不给他看, 2=不看他
    search_pages: int = None,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> None
```

**返回值**: 无

```python
# 示例
FriendSettings.change_privacy(
    friend='测试ing',
    chat_privacy=1,
    sns_privacy=0
)
```

---

### 5. AutoReply — 自动回复

#### `AutoReply.auto_reply_to_friend()`

**自动回复** 指定好友的消息。

```python
AutoReply.auto_reply_to_friend(
    dialog_window: WindowSpecification,     # 好友独立聊天窗口
    duration: str,                          # 持续时间: '1min', '5min', '1h', '30s'
    callback: Callable[[str, list[str]], str],  # 回复函数：接收 (新消息, 上下文列表) 返回 str
    contexts: list[str] = [],               # 上下文列表，可传入历史消息辅助回复
    save_file: bool = False,
    save_media: bool = False,
    target_folder: str = None,
    close_dialog_window: bool = True
) -> dict
```

**返回值**: `dict` — `{'新消息总数': x, '文本数量': x, '文件数量': x, '图片数量': x, '视频数量': x, '链接数量': x, '文本内容': x}`

```python
# 示例：先打开独立窗口，再设置自动回复
from pyweixin import AutoReply, Navigator

def reply_func(newMessage: str) -> str:
    if '你好' in newMessage:
        return '你好'
    if '在吗' in newMessage:
        return '你好,在的'
    return newMessage

dialog_window = Navigator.open_seperate_dialog_window(friend='测试ing')
result = AutoReply.auto_reply_to_friend(
    dialog_window=dialog_window,
    duration='1min',
    callback=reply_func
)
print(result)
```

---

### 6. Monitor — 消息监听

#### `Monitor.listen_on_chat()`

**监听** 聊天窗口的新消息。

```python
Monitor.listen_on_chat(
    dialog_window: WindowSpecification,
    duration: str,                    # '1min', '5min', '30s', '1h'
    groupMembers: list = [],
    save_file: bool = False,
    save_media: bool = False,
    target_folder: str = None,
    close_dialog_window: bool = True
) -> dict
```

**返回值**: `dict` — `{'新消息总数': x, '文本数量': x, '文件数量': x, '图片数量': x, '视频数量': x, '链接数量': x, '文本内容': x}`

```python
# 示例：多线程监听多个好友
from concurrent.futures import ThreadPoolExecutor
from pyweixin import Navigator, Monitor

friends = ['Hello,Mr Crab', 'Pywechat 测试群', '一家人']
durations = ['1min'] * len(friends)
dialog_windows = []

for friend in friends:
    dw = Navigator.open_seperate_dialog_window(
        friend=friend,
        window_minimize=True,
        close_weixin=True
    )
    dialog_windows.append(dw)

with ThreadPoolExecutor(max_workers=len(friends)) as pool:
    results = pool.map(
        Monitor.listen_on_chat,
        list(zip(dialog_windows, durations))
    )
    for friend, result in zip(friends, results):
        print(friend, result)
```

---

#### `Monitor.listen_on_newMemberJoin()`

**监听** 群聊的新成员入群通知。

```python
Monitor.listen_on_newMemberJoin(
    dialog_window: WindowSpecification,
    duration: str,
    close_dialog_window: bool = True
) -> list[str]
```

**返回值**: `list[str]` — 新加入的群成员名称列表

```python
# 示例
dialog = Navigator.open_seperate_dialog_window(friend='Pywechat 测试群')
new_members = Monitor.listen_on_newMemberJoin(
    dialog_window=dialog,
    duration='5min'
)
print(f'新加入成员: {new_members}')
```

---

#### `Monitor.grab_red_packet()`

**自动抢红包**。

```python
Monitor.grab_red_packet(
    dialog_window: WindowSpecification,
    duration: str,
    close_dialog_window: bool = True
) -> int
```

**返回值**: `int` — 已抢到的红包数量

```python
# 示例
dialog = Navigator.open_seperate_dialog_window(friend='一家人')
count = Monitor.grab_red_packet(
    dialog_window=dialog,
    duration='1h'
)
print(f'已抢到 {count} 个红包')
```

---

### 7. Collections — 收藏操作

#### `Collections.cardLink_to_url()`

将收藏中的 **卡片链接转换为 URL**。

```python
Collections.cardLink_to_url(
    number: int,
    delete: bool = False,
    delay: float = 0.5,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> dict[str, str]
```

**返回值**: `dict` — `{'卡片链接文本': url, ...}`

```python
# 示例
results = Collections.cardLink_to_url(number=10)
print(results)
```

---

#### `Collections.collect_offAcc_articles()`

收藏指定 **公众号的文章**。

```python
Collections.collect_offAcc_articles(
    name: str,
    number: int,
    delay: float = 0.3,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> int
```

**返回值**: `int` — 已收藏的文章数量

```python
# 示例
collected = Collections.collect_offAcc_articles(name='新华社', number=10)
print(f'收藏了 {collected} 篇文章')
```

---

### 8. Call — 语音/视频通话

#### `Call.voice_call()`

与好友进行 **语音通话**。

```python
Call.voice_call(
    friend: str,
    wait: bool = False,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> WindowSpecification | None
```

**返回值**: `WindowSpecification`（通话窗口）或 `None`（失败）

```python
# 示例
window = Call.voice_call(friend='测试ing', wait=True)
```

---

#### `Collections.take_notes()`

**记笔记** 到收藏，可附带文件和同步到朋友圈。

```python
Collections.take_notes(
    text: str,
    files: list[str] = [],
    share_moments: bool = False,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> None
```

**返回值**: 无

```python
# 示例
Collections.take_notes(
    text='测试收藏内容',
    files=[r'E:\Desktop\test0.png']
)
```

---

#### `Call.video_call()`

与好友进行 **视频通话**。

```python
Call.video_call(
    friend: str,
    wait: bool = False,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> WindowSpecification | None
```

```python
# 示例
Call.video_call(friend='测试ing')
```

---

### 9. Moments — 朋友圈操作

#### `Moments.dump_recent_posts()`

导出 **最近朋友圈** 内容。

```python
Moments.dump_recent_posts(
    recent: Literal['Today', 'Yesterday', 'Week', 'Month'] = 'Today',
    number: int = None,
    with_name: bool = False,
    save_detail: bool = False,
    target_folder: str = None,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> list[dict]
```

**返回值**: `[{'内容': xx, '图片数量': xx, '视频数量': xx, '发布时间': xx}, ...]`

```python
# 示例
posts = Moments.dump_recent_posts(recent='Today', save_detail=True, number=10)
print(posts)
```

---

#### `Moments.dump_friend_posts()`

导出 **指定好友** 的朋友圈内容。

```python
Moments.dump_friend_posts(
    friend: str,
    number: int,
    save_detail: bool = False,
    target_folder: str = None,
    search_pages: int = None,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> list[dict]
```

**返回值**: `list[dict]` — `[{'内容', '图片数量', '视频数量', '发布时间'}, ...]`

```python
# 示例
posts = Moments.dump_friend_posts(friend='测试ing', number=20, save_detail=True)
for p in posts:
    print(p['内容'][:40], p['发布时间'])
```

---

#### `Moments.post_moments()`

**发布朋友圈**。

```python
Moments.post_moments(
    text: str = '',
    medias: list[str] = [],
    is_maximize: bool = None,
    close_weixin: bool = None
)
```

**返回值**: 无

```python
# 示例
Moments.post_moments(
    texts='发布朋友圈测试',
    medias=[r"E:\Desktop\test0.png"]
)
```

---

#### `Moments.post_notes()`

发布 **笔记** 至朋友圈。

```python
Moments.post_notes(
    content: str = None,
    text: str = None,
    files: list[str] = [],
    is_maximize: bool = None,
    close_weixin: bool = None
) -> None
```

**返回值**: 无

```python
# 示例
Moments.post_notes(
    text='笔记发布朋友圈测试',
    files=[r"E:\Desktop\test0.png"]
)
```

---

#### `Moments.like_posts()`

**朋友圈点赞**（给首页朋友圈内容点赞）。

```python
Moments.like_posts(
    recent: Literal['Today', 'Yesterday', 'Week', 'Month'] = 'Today',
    with_name: bool = False,
    number: int = None,
    callback: Callable[[str], str] = None,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> list[dict]
```

**返回值**: `list[dict]` — 已点赞/评论的朋友圈内容详情

```python
# 示例
results = Moments.like_posts(recent='Today', number=20)
print(f'已点赞 {len(results)} 条')
```

---

#### `Moments.like_friend_posts()`

给 **指定好友** 朋友圈点赞（可附带评论）。

```python
Moments.like_friend_posts(
    friend: str,
    number: int,
    callback: Callable[[str], str] = None,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> list[dict]
```

**返回值**: `list[dict]` — 已点赞/评论的朋友圈内容详情

```python
# 示例
def comment_func(content: str) -> str:
    if 'xxx' in content:
        return 'yyy'
    return 'zzz'

Moments.like_friend_posts(
    friend='测试ing',
    number=20,
    callback=comment_func,
    use_green_send=True
)
```

---

### 10. Settings — 微信设置

#### `Settings.change_style()`

修改微信 **主题样式**。

```python
Settings.change_style(
    style: int,                              # 0=跟随系统, 1=浅色模式, 2=深色模式
    is_maximize: bool = None,
    close_weixin: bool = None
) -> None
```

**返回值**: 无

```python
# 示例：浅色模式
Settings.change_style(1)
```

---

#### `Settings.change_language()`

修改微信 **语言**。

```python
Settings.change_language(
    language: int,                           # 0=跟随系统, 1=简体中文, 2=English, 3=繁體中文
    is_maximize: bool = None,
    close_weixin: bool = None
) -> None
```

**返回值**: 无

```python
# 示例
Settings.change_language(1)
```

---

#### `Settings.change_fontsize()`

修改微信 **字体大小**。

```python
Settings.change_fontsize(
    value: int,                              # 1~9, 2=标准
    is_maximize: bool = None,
    close_weixin: bool = None
) -> None
```

**返回值**: 无

```python
# 示例：标准字体
Settings.change_fontsize(value=2)
```

---

#### `Settings.auto_download_size()`

设置微信 **自动下载文件大小**。

```python
Settings.auto_download_size(
    size: int,                               # 1~1024 MB
    state: bool = True,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> None
```

**返回值**: 无

```python
# 示例
Settings.auto_download_size(size=500)
```

---

#### `Settings.notification_alert()`

修改微信设置中的 **通知或声音标记**。

```python
Settings.notification_alert(
    alert_map: dict,
    is_maximize: bool = None,
    close_weixin: bool = None
) -> None
```

**返回值**: 无

`alert_map` 格式:

```python
{
    'newMessage': True,       # 新消息通知
    'Call': True,             # 语音/视频通话提醒
    'Moments': True,          # 朋友圈更新
    'Game': False,            # 游戏通知
    'Interaction_only': False # 仅被@时通知
}
```

```python
# 示例
Settings.notification_alert(alert_map={
    'newMessage': True,
    'Call': True,
    'Moments': True,
    'Game': False,
    'Interaction_only': False
})
```

---

## WeChatTools — 辅助工具模块

### 1. Navigator — 界面导航

所有 Navigator 方法返回均为 `pywinauto.WindowSpecification` 类型，可继续调用 pywinauto 原生方法。

#### `Navigator.open_weixin()`

**打开** 微信主窗口。

```python
Navigator.open_weixin(
    is_maximize: bool = None
) -> WindowSpecification
```

**返回值**: `WindowSpecification` — 微信主窗口对象

```python
# 示例
main_window = Navigator.open_weixin()
```

---

#### `Navigator.open_settings()`

**打开** 微信设置界面。

```python
Navigator.open_settings(
    is_maximize: bool = None,
    close_weixin: bool = None
) -> WindowSpecification
```

**返回值**: `WindowSpecification` — 设置窗口对象

```python
# 示例
settings_window = Navigator.open_settings()
```

---

#### `Navigator.open_contacts()`

**打开** 通讯录。

```python
Navigator.open_contacts(
    is_maximize: bool = False
) -> WindowSpecification
```

```python
# 示例
Navigator.open_contacts()
```

**返回值**: `WindowSpecification` — 通讯录窗口

---

#### `Navigator.open_contacts_manage()`

**打开** 通讯录管理界面。

```python
Navigator.open_contacts_manage(
    is_maximize: bool = False,
    window_maximize: bool = False,
    close_weixin: bool = True
) -> WindowSpecification
```

```python
# 示例
Navigator.open_contacts_manage()
```

**返回值**: `WindowSpecification` — 通讯录管理窗口

---

#### `Navigator.open_collections()`

**打开** 收藏界面。

```python
Navigator.open_collections(
    is_maximize: bool = False
) -> WindowSpecification
```

```python
# 示例
Navigator.open_collections()
```

**返回值**: `WindowSpecification` — 收藏界面窗口

---

#### `Navigator.open_moments()`

**打开** 朋友圈界面。

```python
Navigator.open_moments(
    is_maximize: bool = False,
    close_weixin: bool = True
) -> WindowSpecification
```

```python
# 示例
Navigator.open_moments()
```

**返回值**: `WindowSpecification` — 朋友圈窗口

---

#### `Navigator.open_chatfiles()`

**打开** 聊天文件界面。

```python
Navigator.open_chatfiles(
    is_maximize: bool = False,
    window_maximize: bool = False,
    close_weixin: bool = True
) -> WindowSpecification
```

```python
# 示例
Navigator.open_chatfiles()
```

**返回值**: `WindowSpecification` — 聊天文件窗口

---

#### `Navigator.open_search()`

**打开** 搜一搜界面。

```python
Navigator.open_search(
    is_maximize: bool = False,
    window_maximize: bool = False,
    close_weixin: bool = True
) -> WindowSpecification
```

```python
# 示例
Navigator.open_search()
```

**返回值**: `WindowSpecification` — 搜一搜窗口

---

#### `Navigator.open_channels()`

**打开** 视频号界面。

```python
Navigator.open_channels(
    close_weixin: bool = True,
    is_maximize: bool = False,
    window_maximize: bool = False
) -> WindowSpecification
```

```python
# 示例
Navigator.open_channels()
```

**返回值**: `WindowSpecification` — 视频号窗口

---

#### `Navigator.open_miniprogram_pane()`

**打开** 小程序面板。

```python
Navigator.open_miniprogram_pane(
    window_maximize: bool = True,
    close_weixin: bool = True,
    is_maximize: bool = False
) -> WindowSpecification
```

```python
# 示例
Navigator.open_miniprogram_pane()
```

**返回值**: `WindowSpecification` — 小程序面板窗口

---

#### `Navigator.open_dialog_window()`

**打开** 与好友或群聊的聊天界面（嵌入在主窗口中）。

```python
Navigator.open_dialog_window(
    friend: str,
    is_maximize: bool = True,
    search_pages: int | None = None
) -> WindowSpecification
```

```python
# 示例
Navigator.open_dialog_window(friend='文件传输助手')
```

**返回值**: `WindowSpecification` — 聊天界面窗口对象

---

#### `Navigator.open_seperate_dialog_window()`

**打开** 与好友或群聊的 **独立** 聊天窗口。

> **重要**: 此方法返回的 `dialog_window` 是许多自动化操作的入口（如 AutoReply、Monitor）。

```python
Navigator.open_seperate_dialog_window(
    friend: str,
    is_maximize: bool = True,
    window_minimize: bool = False,     # 最小化窗口（便于后台监听）
    search_pages: int | None = None
) -> WindowSpecification
```

```python
# 示例
dialog_window = Navigator.open_seperate_dialog_window(friend='文件传输助手')
```

**返回值**: `WindowSpecification` — 独立聊天窗口对象

---

#### `Navigator.open_chat_history()`

**打开** 与好友或群聊的聊天记录界面。

```python
Navigator.open_chat_history(
    friend: str,
    TabItem: str | None = None,        # 分区: '文件','图片与视频','链接','音乐与音频','小程序','视频号','日期'
    is_maximize: bool = True,
    search_pages: int | None = None
) -> WindowSpecification
```

```python
# 示例：打开文件分区
Navigator.open_chat_history(friend='文件传输助手', TabItem='文件')
```

**返回值**: `WindowSpecification` — 聊天记录窗口

---

#### `Navigator.open_chatinfo()`

**打开** 好友的聊天信息界面（右侧面板）。

```python
Navigator.open_chatinfo(
    friend: str,
    close_weixin: bool = True,
    is_maximize: bool = False,
    search_pages: int | None = None
) -> WindowSpecification
```

```python
# 示例
Navigator.open_chatinfo(friend='测试ing')
```

**返回值**: `WindowSpecification` — 聊天信息面板

---

#### `Navigator.open_friend_profile()`

**打开** 好友个人简介面板。

```python
Navigator.open_friend_profile(
    friend: str,
    close_weixin: bool = False,
    is_maximize: bool = True
) -> WindowSpecification
```

```python
# 示例
Navigator.open_friend_profile(friend='测试ing')
```

**返回值**: `WindowSpecification` — 好友简介面板

---

#### `Navigator.open_friend_moments()`

**打开** 好友的朋友圈。

```python
Navigator.open_friend_moments(
    friend: str,
    close_weixin: bool = True,
    is_maximize: bool = True,
    search_pages: int | None = None
) -> WindowSpecification
```

```python
# 示例
Navigator.open_friend_moments(friend='测试ing')
```

**返回值**: `WindowSpecification` — 好友朋友圈窗口

---

#### `Navigator.open_chat_search_window()`

**打开** 聊天记录搜索窗口。

```python
Navigator.open_chat_search_window(
    keyword: str,
    is_maximize: bool = True,
    close_weixin: bool = True
) -> tuple[WindowSpecification, WindowSpecification]
```

**返回值**: `(chat_history_window, main_window)`

```python
# 示例
chat_window, main_window = Navigator.open_chat_search_window(keyword='你好')
print(chat_window.dump_tree())
```

---

#### `Navigator.open_add_friend_pane()`

**打开** 添加好友界面。

```python
Navigator.open_add_friend_pane(
    is_maximize: bool = True
) -> WindowSpecification
```

```python
# 示例
Navigator.open_add_friend_pane()
```

**返回值**: `WindowSpecification` — 添加好友界面

---

#### `Navigator.search_miniprogram()`

搜索并 **打开小程序**。

```python
Navigator.search_miniprogram(
    name: str,
    load_delay: float | None = None,
    is_maximize: bool = True,
    close_weixin: bool = True
) -> WindowSpecification
```

```python
# 示例
Navigator.search_miniprogram(name='跳一跳')
```

**返回值**: `WindowSpecification` — 小程序窗口

---

#### `Navigator.search_channels()`

搜索并 **打开视频号**。

```python
Navigator.search_channels(
    search_content: str,
    load_delay: float | None = None,
    is_maximize: bool = True,
    window_maximize: bool = False,
    close_weixin: bool = True
) -> WindowSpecification
```

```python
# 示例
Navigator.search_channels(search_content='微信4.0')
```

**返回值**: `WindowSpecification` — 视频号窗口

---

#### `Navigator.search_official_account()`

搜索并 **打开公众号**。

```python
Navigator.search_official_account(
    name: str,
    load_delay: float | None = None,
    is_maximize: bool = True,
    close_weixin: bool = True
) -> WindowSpecification
```

```python
# 示例
Navigator.search_official_account(name='微信团队')
```

**返回值**: `WindowSpecification` — 公众号窗口

---

#### `Navigator.capture_Login_QRCode()`

**保存** 微信登录二维码到本地。

```python
Navigator.capture_Login_QRCode(
    img_path: str
) -> bool
```

```python
# 示例
Navigator.capture_Login_QRCode(img_path='test.png')
```

---

### 2. Tools — 路径查询与工具

#### `Tools.where_weixin()`

获取微信 `.exe` 程序路径。

```python
Tools.where_weixin() -> str
```

```python
# 示例
path = Tools.where_weixin()
print(path)
```

---

#### `Tools.where_msg_folder()`

获取微信 **msg 文件夹** 路径。

```python
Tools.where_msg_folder(
    open_folder: bool = False      # 是否同时打开文件夹
) -> str
```

```python
# 示例
path = Tools.where_msg_folder(open_folder=True)
print(path)
```

---

#### `Tools.where_wxid_folder()`

获取微信 **wxid 文件夹** 路径。

```python
Tools.where_wxid_folder(
    open_folder: bool = False
) -> str
```

```python
# 示例
path = Tools.where_wxid_folder()
```

---

#### `Tools.where_chatfile_folder()`

获取微信 **聊天文件文件夹** 路径。

```python
Tools.where_chatfile_folder(
    open_folder: bool = False
) -> str
```

```python
# 示例
path = Tools.where_chatfile_folder()
```

---

#### `Tools.where_video_folder()`

获取微信 **视频文件文件夹** 路径。

```python
Tools.where_video_folder(
    open_folder: bool = False
) -> str
```

```python
# 示例
path = Tools.where_video_folder()
```

---

#### `Tools.where_db_folder()`

获取微信 **数据库文件夹** 路径。

```python
Tools.where_db_folder(
    open_folder: bool = False
) -> str
```

```python
# 示例
path = Tools.where_db_folder()
```

---

#### `Tools.where_userlib_folder()`

获取微信 **用户配置目录** 路径。

```python
Tools.where_userlib_folder(
    open_folder: bool = False
) -> str
```

```python
# 示例
path = Tools.where_userlib_folder()
```

---

#### `Tools.about_weixin()`

获取关于微信的 **基本信息** 字典。

```python
Tools.about_weixin() -> dict
```

**返回值**: `dict` — `{'exe路径', '版本', '语言', 'wxid', 'wxid目录', '微信配置目录', '聊天文件目录'}`

无需传入参数，直接获取当前微信的版本和目录信息。

```python
# 示例
info = Tools.about_weixin()
print(info)
```

---

## WinSettings — Windows 系统设置

```python
from pyweixin import SystemSettings
# 或
from pyweixin.WinSettings import SystemSettings
```

辅助 `pyweixin` 进行微信自动化的 Windows 系统级操作（剪贴板、输入法等）。

（具体方法签名待补充源码）

---

## utils — 工具函数

```python
from pyweixin import utils
# 或
from pyweixin.utils import scan_for_new_messages
```

主要函数：

- `scan_for_new_messages()` — 扫描并获取微信中的新消息，配合 Monitor 使用

（详见源码 `scripts/pyweixin/utils.py`）

---

## 注意事项

### 1. 通用执行流程

调用任何自动化方法前，Agent 需要确保：

1. **运行环境是 Windows** — 若不是，输出 `This tool requires Windows. Aborting.`
2. **检查依赖** — 首次调用时运行 `check_requirements.py`；缺少则 `pip install -r requirements.txt`
3. **检查微信 UI 可见性** — 每次调用运行 `check_visibility.py`
   - 若不可见 → 运行 `check_running_state.py` 判断微信是否已启动
   - 微信未启动 → 提示用户自行启动并登录
   - 微信已启动但 UI 不可见 → 提示用户启用"讲述人"(Narrator)模式
4. **执行自动化操作** — 用正确的 import 路径和方法签名生成 Python 脚本

### 2. 关于"讲述人"模式（Narrator）

微信 4.1+ 默认屏蔽 UI 自动化访问。解决方法：

1. 登录微信 **前**，先开启 Windows 讲述人（Win+Ctrl+Enter）
2. 等待 **5分钟以上**
3. （可选）关闭讲述人
4. 正常使用 `pyweixin`
5. 频繁使用后，微信可能会"记住"此状态，后续不再需要重复操作

**原理**: Windows UI Automation API 必须向屏幕阅读器暴露所有 UI 元素（含隐藏元素），不能违反无障碍设计原则。

### 3. 关于负载控制

- 操作过于频繁 → 微信会自动退出登录（正常检测机制）
- 适当调整各方法的 `delay` 参数（如 `send_delay=0.5` 或更高）
- 高频率的大量操作可能触发微信风控

### 4. 二次开发

- 使用 `Navigator` 打开各种界面，返回 `pywinauto.WindowSpecification`
- 配合 `pywinauto` 原生方法进行更复杂的操作
