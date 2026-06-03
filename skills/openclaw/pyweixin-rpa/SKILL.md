---
name: pyweixin-rpa
description: "基于 pywinauto 的 Windows PC 微信 UI 自动化工具，支持消息、文件、朋友圈、联系人等操作，无需 Hook 注入。"
---

# pyweixin RPA

## Overview

Python 微信 RPA 工具，基于 `pywinauto` 实现，**纯 UI 自动化，无 Hook 注入**。

**核心原则：所有方法均为静态方法，无需实例化类。**

> 仅支持 Windows 平台。如果运行环境不是 Windows，则应输出：
> `This tool requires Windows. Aborting.`

---

## Resources

- **scripts/requirements.txt** — 依赖清单
- **scripts/check_requirements.py** — 依赖检查脚本
- **scripts/check_visibility.py** — 微信 UI 可见性检查脚本
- **scripts/check_running_state.py** — 微信运行状态检查脚本
- **scripts/Weixin4.0.md** — 微信 4.0+ UI 树可见性说明
- **scripts/pyweixin/** — 微信 4.0+ 自动化源码
- **references/api_reference.md** — 方法签名速查（推荐优先阅读）
- **references/pywixin操作手册.pdf** — 必要时将该文件发送给用户

---

## Check Requirements

首次调用该 Skill 时需要在仓库根目录（即 `skills/pyweixin-rpa/`）使用系统 Python 运行以下命令。注意：只有在当前系统中**首次**运行该 Skill 时才需要执行此步骤，后续不再需要。

```bash
python scripts/check_requirements.py
```

- 输出结果：JSON 对象 `{"missing_package": list}`
- 如果脚本退出码非零、输出无法解析为 JSON、或缺少 `missing_package` 键，则视为缺少依赖。
- 如果输出可解析且返回的 JSON 字符串中 `missing_package` 键对应的列表为空，则视为不缺少相关依赖。

**处理：**

1. 如果缺少相关依赖，输出：`缺乏相关依赖，正在安装相关依赖`，并在仓库根目录使用系统 Python 运行：

```bash
pip install -r scripts/requirements.txt
```

2. 如果不缺少相关依赖，可以继续进行其他操作。

---

## Check Visibility

该 Skill 每次被调用时都需要经过这一阶段。在仓库根目录使用系统 Python 运行：

```bash
python scripts/check_visibility.py
```

- 输出结果：JSON 对象 `{"visibility": bool}`
- 如果脚本退出码非零、输出无法解析为 JSON、或缺少 `visibility` 键，则 `visibility` 视为 `False`。

1. 如果 `visibility == False`，继续运行：

```bash
python scripts/check_running_state.py
```

- 输出结果：JSON 对象 `{"is_running": bool}`
- 如果 `is_running == false`，输出：`微信未启动，请自行启动并登录后再尝试进行相关自动化操作！`
- 如果 `is_running == true`，告知用户微信 UI 树不可见，无法执行自动化操作。在控制台输出一份中文摘要：
  - 3-5 条要点
  - 最多 150 字
  - 来源：`references/Weixin4.0.md`

2. 如果 `visibility == True`，可以继续进行其他操作。

---

## Import List

| 模块 | 类 | 说明 |
| --- | --- | --- |
| `WeChatAuto` | `Messages` | 消息发送、拉取、导出会话、导出聊天记录 |
| | `Files` | 文件发送、保存、导出 |
| | `Call` | 语音/视频通话 |
| | `Contacts` | 联系人、群聊、公众号信息获取 |
| | `FriendSettings` | 好友管理（备注、标签、拉黑、删除等） |
| | `Monitor` | 消息监听 |
| | `Moments` | 朋友圈操作 |
| | `Settings` | 微信设置 |
| | `AutoReply` | 自动回复 |
| | `Collections` | 收藏操作 |
| `WeChatTools` | `Tools` | 微信路径查询、状态检测、消息解析 |
| | `Navigator` | 打开微信内部一切可以打开的窗口 |
| `WinSettings` | `SystemSettings` | Windows 系统操作（剪贴板、输入法等） |
| `utils` | | 扫描新消息 `scan_for_new_messages` |

```python
# 所有可用类的具体导入方式（需要先 sys.path.insert）
from pyweixin import AutoReply, Collections, Call, Contacts, Files, FriendSettings, Messages, Moments, Monitor, Settings
from pyweixin import Tools, Navigator
from pyweixin import SystemSettings
from pyweixin.Config import GlobalConfig
```

---

## Scripting Guidelines

### 原则一：导入前务必 `sys.path.insert(0, 'scripts')`

`scripts/pyweixin/` 是本工具的本地源码目录。如果你的 Python 环境中安装了同名的第三方 `pyweixin` pip 包，`from pyweixin import Messages` 会优先加载 pip 包而非本地模块，导致报错（如 `AttributeError: type object 'Messages' has no attribute 'dump_chat_history'`）。

```python
import sys
sys.path.insert(0, 'scripts')

from pyweixin import Messages, Files  # 现在会加载本地模块
```

> **注意：** `scripts/check_visibility.py` 等检查脚本内部已处理路径，直接运行不受影响。仅在编写自定义脚本时需要关注。

### 原则二：`dump_chat_history` 返回 `list[dict]`，不要解包为两个变量

```python
# ❌ 错误：返回值是 list[dict]，不是 tuple
messages, times = Messages.dump_chat_history(friend='xxx', number=5)

# ✅ 正确：直接拿 dict 列表
result = Messages.dump_chat_history(friend='xxx', number=5, close_weixin=False)
for msg in result:
    print(msg['消息发送人'], msg['消息内容'])
```

### 原则三：返回值以 API Reference 为准，无需探针

`references/api_reference.md` 中每个方法都已标注准确的返回类型和结构，这些标注直接从源码提取。

```python
# ✅ 正确：查文档比跑探针更可靠
# api_reference.md 中：
# Messages.dump_chat_history(...) -> list[dict]
# 每个 dict 键: '消息发送人', '消息内容', '消息类型', '消息发送时间'

result = Messages.dump_chat_history(friend='xxx', number=5, close_weixin=False)
for msg in result:
    print(msg.get('消息内容'))  # 直接使用，无需 type() 探测
```

> **例外：** 如果你修改了源码或使用了源码中未覆盖的方法，才需要探针验证。日常使用以文档为准。

### 原则四：已拉取的数据不要重复拉取

如果已经调用了一次 `dump_chat_history`（或其他拉取方法）拿到了数据，后续的处理步骤（如生成报告、分析、转发）应该**接收现有数据**，而不是再调一次拉取方法。

```python
# ❌ 错误：拉取 + 报告各拉一次 = 两次 UI 自动化操作
result = Messages.dump_chat_history(friend='xxx', number=200, close_weixin=False)
# ... 然后又在一个新脚本里调了一次 dump_chat_history ...

# ✅ 正确：只拉一次，把结果传给下游
result = Messages.dump_chat_history(friend='xxx', number=200, close_weixin=False)
report = build_report(result)    # 复用数据，不再调用 dump_chat_history
send(report)
```

如果确实需要自包含的独立脚本（比如一次性工具），可以在脚本内部加一个**已拉取检查**，或者用全局配置控制只拉一次。

> **经验：** 每条 `dump_chat_history` 调用 = 一次聊天窗口滚动操作。跑两次就是两次滚动操作，纯属浪费。拿到 `list[dict]` 后你想怎么处理都行，不需要重新拉。

> **💡 只读消息用 `pull_messages`，别用 `dump_chat_history`：** `pull_messages` 只拉取已有聊天区域内的消息记录，不滚动窗口，比 `dump_chat_history` 轻量得多。验证、检查最新消息、确认发送结果，都应该用 `pull_messages`。需要翻历史记录时（消息数量超过当前可视区域），才用 `dump_chat_history`。

---

## Send Messages

在发送消息时，注意消息中是否有文件（如图片、视频等）：

- 如果发送的内容只是**文本字符串**，使用 `Messages` 内的 send 操作即可。
- 如果消息中**包含文件**，使用 `Files` 内的 send 操作，且 `with_messages` 参数设置为 `True`。

---

## Handle Exception

在自动化过程中，`scripts/pyweixin` 内代码可能引发的异常分为以下类别。对于所有异常，**不要自动重试，直接结束相关自动化任务，是否重试由用户本人决定**。

### 异常分类与处理

| 异常 | 原因 | 处理方式 |
| --- | --- | --- |
| `ComError` | 自动化窗口中 top_window 被手动关闭 | 出现该异常后不要重试，直接结束相关自动化任务，返回：`本次自动化操作中顶部窗口被意外关闭，自动化任务终止。` |
| `ElementNotFindError` | 源码中某一处控件未在微信相关窗口中定位到 | 出现该异常后不要重试，直接结束相关自动化任务。总结异常信息，将未定位到的 UI 控件具体位置返回（`scripts/pyweixin/Uielements`），并建议用户使用 `inspect.exe` 等工具查看未定位到的控件信息，将信息反馈后修改定位逻辑。 |
| `TimeoutError` | 源码中某一处控件未在微信相关窗口中定位到，且可能使用了 pywinauto 的 wait 机制 | 出现该异常后不要重试，直接结束相关自动化任务。处理逻辑与 `ElementNotFoundError` 一致。 |

### 关于 ClickPos 坐标异常

如果异常的源代码中涉及到了 `ClickPos` 类，导致本次异常的原因大概率是点击坐标有偏差，未弹出期望窗口或控件。**出现该异常后可以尝试在 `scripts/Uielements/ClickPos` 类中直接修改点击坐标。**

涉及 `ClickPos` 的方法：

| 位置 | 具体坐标 |
| --- | --- |
| `WeChatTools\Navigator\open_my_profile` | `ClickPos(weixin_button).AvatarPos` |
| `WeChatTools\Tools\select_chatList` | `ClickPos(selected[0]).ChatListSelectPos` |
| `WeChatTools\Tools\select_chatHistoryList` | `ClickPos(selected[0]).ChatHistorySelectPos` |
| `WeChatAuto\Moments\post_notes` | `ClickPos(container).MoreButtonPos` |
| `WeChatAuto\Moments\like_posts` | `ClickPos(content_listitem).PostImagePos` |
| `WeChatAuto\Moments\like_posts` | `ClickPos(content_listitem).EllipsisPos` |
| `WeChatAuto\Moments\dump_recent_posts` | `ClickPos(content_listitem).PostNamePos` |
| `WeChatAuto\Moments\dump_friend_posts` | `ClickPos(content_listitem).PostDetailVideoPos` |
| `WeChatAuto\Moments\dump_friend_posts` | `ClickPos(content_listitem).PostDetailVideoClickPos` |
| `WeChatAuto\Moments\dump_friend_posts` | `ClickPos(content_listitem).PostDetailImagePos` |
| `WeChatAuto\Moments\dump_friend_posts` | `ClickPos(content_listitem).PostDetailImageClickPos` |
| `WeChatAuto\Messages\send_audios_to_friend` | `ClickPos(send_audio_button).AudioButtonPos` |
| `WeChatAuto\Messages\send_audios_to_friend` | `ClickPos(main_window).MainWindowPos` |
| `WeChatAuto\Messages\message_chain` | `ClickPos(AddContentText).SolitairePos` |
| `WeChatAuto\Messages\search_chat_history` | `ClickPos(next_item).SearchChatPos` |
| `WeChatAuto\Collections\collect_offAcc_articles` | `ClickPos(offAcc_window).CardLinkPos` |
| `WeChatAuto\Collections\cardLink_to_url` | `ClickPos(offAcc_window).CardLinkPos` |

---

## Scheduled Tasks：用 OpenClaw cron 触发脚本，不要在代码里写定时逻辑

如果需要「在某个时间点自动给好友发消息」之类的定时操作，**不要**在 Python 脚本里写 `time.sleep`、`schedule` 库或任何自身定时逻辑。而是：

1. **写一个纯干活脚本**（只做一件事，不含时间判断）。
2. **用 OpenClaw 的 cron 设定触发时间**，通过 `systemEvent` 在主 session 执行。

### 正确做法

**Step 1：写脚本**（只干活）

```python
import sys
sys.path.insert(0, 'scripts')
from pyweixin import Messages
Messages.send_messages_to_friend(
    friend='文件传输助手',
    messages=['你好，这是定时消息'],
    close_weixin=False
)
```

**Step 2：设 cron 任务**（用 OpenClaw 的定时能力触发）

```bash
# 在 OpenClaw 中创建定时任务
# 09:51 时触发主 session 执行脚本
```

对应的 cron 参数：

| 字段 | 值 | 说明 |
| --- | --- | --- |
| `schedule` | `{"kind": "at", "at": "2026-06-02T09:51:00+08:00"}` | 触发时间 |
| `payload.kind` | `systemEvent` | 在主 session 中注入事件 |
| `payload.text` | `执行脚本：python scripts/cron_send_msg.py` | 告诉 agent 做什么 |
| `sessionTarget` | `main` | 在主 session 执行（能看到上下文） |
| `delivery` | 不设 | 不需要回传 |

### ❌ 不要这样做

```python
# 错误：在脚本里自己控制时间
import time
time.sleep(120)  # ❌ 脚本挂起，阻塞
Messages.send_messages_to_friend(...)
```

```python
# 错误：用 external scheduler 轮询
import schedule  # ❌ 引入额外依赖
schedule.every().day.at("09:51").do(send_msg)
```

### 为什么？

- OpenClaw cron 本身就是一个成熟的调度器，支持 `at`（一次性）、`every`（间隔）、`cron`（cron 表达式）三种模式。
- 脚本只负责**干活**，时间控制完全解耦，脚本可以被随时手动执行、调试。
- `sessionTarget="main"` 让主 session 收到定时事件后直接 exec 脚本，不需要 isolated session 去猜上下文。

---

## Execution

Check Visibility 阶段没有任何问题后，便可以在 Windows 环境下运行相关自动化操作。通过阅读 `references/api_reference.md` 来获取各方法的完整签名、参数说明来生成对应的 Python 脚本。

---

## Guide Book

当用户想要详细了解 pyweixin-rpa 操作细节时，输出一行文件指令让用户客户端收到附件：

```
FILE: references/pyweixin操作手册.pdf
```
