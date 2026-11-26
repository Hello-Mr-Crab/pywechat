# Linux 支持

> 上游 issue：[Hello-Mr-Crab/pywechat#303 是否考虑 Linux 支持](https://github.com/Hello-Mr-Crab/pywechat/issues/303)
>
> 本文描述 pyweixin 的 Linux 后端：**读 UI 树走 AT-SPI2，写操作走 XTest，截图走 ffmpeg**，
> 不注入微信进程、不改注册表、不逆向闭源二进制。

## 1. 现状

| 能力 | Windows | Linux |
|---|---|---|
| 启动/附着主窗口 | ✅ | ✅ |
| 登录态检测 | ✅ | ✅ |
| 登录二维码截图 | ✅ | ✅ |
| 按名字打开会话（会话列表） | ✅ | ✅ |
| 按搜索打开会话（兜底） | ✅ | ⚠️ 已实现未实测 |
| 发送文本消息 | ✅ | ✅ |
| 读取最近 N 条消息（文本/类型推断） | ✅ | ✅ |
| 发送文件 / 图片 / 语音 | ✅ | ❌ 未实现 |
| 朋友圈 / 收藏 / 小程序 / 视频号 | ✅ | ❌ 未实现 |
| 通讯录增删好友、群管理 | ✅ | ❌ 未实现 |
| 监听新消息（轮询） | ✅ | ❌ 未实现 |
| @群成员 | ✅ | ❌ 未实现 |
| 修改系统音量 / 防息屏 | ✅ | ❌ 未实现（非核心） |

**结论**：Linux 侧目前是**最小可用闭环**（登录 → 打开会话 → 发文本 → 读消息），
不是功能对齐。`WeChatAuto` / `WeChatTools` / `utils` 仍然是 Windows 专用，
在 Linux 上导入它们会得到一条明确的 `NotImplementedError`，而不是莫名其妙地崩在 `win32gui`。

## 2. 为什么 Linux 能拿到 UI 树

Windows 上 pyweixin 走 UIAutomation，Linux 上走 AT-SPI2。两者拿到的其实是**同一棵树**：

* 微信 4.x 两端都是 **Qt**（Windows 的窗口类是 `Qt51514QWindowIcon`，UIA 里 `framework_id='Qt'`）；
* Qt 的 `QAccessible` 抽象层在 Windows 上桥接到 UIA，在 Linux 上桥接到 AT-SPI2；
* 所以控件角色/名称/坐标一一对应，差别只在**没有 `class_name`**。

AT-SPI 在一条独立于会话总线的 D-Bus 上：

```bash
busctl --user call org.a11y.Bus /org/a11y/bus org.a11y.Bus.GetAddress
# → s "unix:path=/run/user/1000/at-spi/bus_1"
```

## 3. 架构分层

```
pyweixin/
├── platform/                 ← 新增：平台抽象层
│   ├── base.py               Rect / Point / UIElement 协议 / PlatformNotSupported
│   ├── selector.py           UIA 选择器 → AT-SPI 判据（control_type→role、class_name 兼容表）
│   ├── windows.py            透传 pywinauto，Windows 行为零改动
│   └── linux/
│       ├── atspi.py          会话 + 全量快照（Node/Snapshot/find）
│       ├── element.py        LinuxElement + LinuxWindowSpecification（惰性定位）
│       ├── x11.py            xdotool / xclip / ffmpeg
│       └── driver.py         找应用、启动、主窗口、调窗口尺寸
├── linux_auto.py             ← 新增：Linux 最小闭环 API + 收件人白名单
├── Config.py                 ← 改：版本号/语言在 Linux 上也能探测
├── Uielements.py             ← 改：选择器表在 Linux 上可复用（仅 1 处 import 兜底）
└── __init__.py               ← 改：非 Windows 平台不再 import pywinauto 系模块
```

### 3.1 惰性定位器

`LinuxWindowSpecification` 刻意做成 pywinauto `WindowSpecification` 的**同形替身**：

```python
win.child_window(control_type='List', title='会话')   # 只记"怎么找"
   .children()[0].click_input()                        # 用时才解析
```

每次解析都重新遍历一次无障碍树（AT-SPI 的对象路径会随 UI 重建而失效，不能缓存）。
一次全量遍历 1124 个节点约 **0.3–0.5 秒**，会话内有 300 ms 快照缓存。

**收益**：`Uielements.py` 里 900 多行选择器表（纯 dict）可以直接复用，
`control_type='List' / title='会话'` 在 AT-SPI 上就是 `role='list' / name='会话'`。

### 3.2 选择器翻译

| pywinauto | AT-SPI | 说明 |
|---|---|---|
| `control_type='List'` | `role='list'` | 一一对应 |
| `control_type='Edit'` | `role ∈ {text, entry, password text}` | Qt 的 QLineEdit/QTextEdit |
| `control_type='Button'` | `role ∈ {push button, button, toggle button}` | |
| `title='会话'` | `name='会话'` | 一一对应 |
| `title=''` | `name=''` | pywinauto 的 `''` 表示"名字为空"，不是通配 |
| `title='^会.*$'` | 正则匹配 `name` | |
| `class_name='mmui::ChatInputField'` | 人工标定的角色集合 | **启发式**，见 `CLASS_NAME_ROLES` |
| `auto_id='chat_input_field'` | ❌ 无对应物 | 会被忽略并记录 |
| `class_name`（未收录） | ❌ 直接抛 `UnsupportedSelector` | 宁可报错，不猜 |

## 4. 快速开始

### 4.1 依赖

```bash
# Arch
sudo pacman -S python-gobject at-spi2-core xdotool xclip ffmpeg xorg-server-xvfb
# Debian/Ubuntu
sudo apt install python3-gi gir1.2-atspi-2.0 at-spi2-core xdotool xclip ffmpeg xvfb
```

都是普通用户权限可用的组件，**不需要 root 常驻**。

### 4.2 启动环境

无头服务器上需要一个 X 显示。**必须加 `-dpi 96`**（见 §7.1）：

```bash
Xvfb :99 -screen 0 1600x1000x24 -dpi 96 &
export DISPLAY=:99
```

还需要一个 D-Bus 会话总线 + AT-SPI 总线：

```bash
export XDG_RUNTIME_DIR=/tmp/xdg-wx
mkdir -p "$XDG_RUNTIME_DIR" && chmod 700 "$XDG_RUNTIME_DIR"
dbus-daemon --session --address="unix:path=$XDG_RUNTIME_DIR/bus" --fork
export DBUS_SESSION_BUS_ADDRESS="unix:path=$XDG_RUNTIME_DIR/bus"
/usr/lib/at-spi-bus-launcher &
```

然后带无障碍开关启动微信：

```bash
export QT_QPA_PLATFORM=xcb
export QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1     # 关键：无头环境下没有 gsettings
/opt/wechat/wechat &
```

> `QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1` 是 Qt 官方开关。桌面环境下也可以改用
> `gsettings set org.gnome.desktop.interface toolkit-accessibility true`。
> 没有这个开关，微信进程根本不会注册到 a11y 总线，`Atspi.get_desktop()` 里看不到它。

一键复现脚本见 `scripts/session_up.sh`、`scripts/wechat_up.sh`、`scripts/env.sh`。

### 4.3 用法

```python
from pyweixin import linux_auto as wx

wx.is_logged_in()                       # True / False
wx.capture_login_qrcode('qr.png')       # 没登录时保存二维码，人工扫码
wx.open_chat('文件传输助手')             # 幂等
wx.send_message('文件传输助手', 'hello') # 发送 + 回读校验，失败自动重试一次
wx.read_messages(5)                     # [{'content','type','sender','role'}, ...]
wx.screenshot('shot.png')
```

也可以直接用平台层做更细的操作：

```python
from pyweixin import platform

be = platform.backend()                 # LinuxBackend
win = be.main_window()
chat = win.child_window(control_type='List', title='会话')
print([c.window_text().split('\n')[0] for c in chat.children()])
```

### 4.4 收件人白名单（硬规则）

`linux_auto.ALLOWED_RECIPIENTS` **只允许**向两个会话发送任何内容：

```python
ALLOWED_RECIPIENTS = frozenset({'文件传输助手', '依依'})
```

其它收件人在**触碰 UI 之前**就抛 `RecipientNotAllowed`：

```python
>>> wx.send_message('某个好友', 'hi')
RecipientNotAllowed: 拒绝向 '某个好友' 发送:收件人不在白名单 ['依依', '文件传输助手'] 内。
```

这是硬编码的，**不提供运行时覆盖入口**；放宽必须改代码并同步改
`tests/test_recipient_whitelist.py`。测试里用一个"碰一下就炸"的假后端证明
拒绝发生在任何 UI 动作之前。

## 5. 与 Windows 实现的差异

| 能力 | Windows 做法 | Linux 做法 | 风险 |
|---|---|---|---|
| 定位控件 | `child_window(control_type, title, class_name, auto_id)` | 只有 `role` + `name` | 依赖 `class_name` 的代码不可移植 |
| 点击 | `click_input()`（UIA 层） | XTest（`xdotool`） | 需要控件在屏幕上真实可见、未被遮挡 |
| 输入文本 | `type_keys` / `set_text` | 剪贴板 + `Ctrl+V` | 依赖 X 剪贴板所有者存活 |
| 判断消息类型 | `class_name`（`mmui::ChatTextItemView`…） | `name` 文本前缀推断 | 见 §6 |
| 判断列表到底/到顶 | `runtime_id` 重复 | 列表项 `name` 序列重复 | 同名消息相邻时可能误判 |
| 未读数 | `GetCurrentPropertyValue(30159)`（FullDescription） | ❌ 无对应物 | 需改用会话项文本里的"N条新消息" |
| 打开会话 | 点会话项 / 顶部搜索 | 同（会话项名字首行精确匹配） | 会话项 name 含换行，需 split |
| 最大化 | `SendMessage(WM_SYSCOMMAND)` | `xdotool windowsize` | 裸 Xvfb 无窗口管理器，需手动摆位 |
| 剪贴板发文件 | `CF_HDROP` | X11 `text/uri-list` | **未实现、未验证** |

## 6. 消息类型只有文本推断

Windows 上靠 `class_name` 精确区分文本/图片/语音/链接。Linux 侧 AT-SPI **没有类名**，
只能按 `name` 的文本前缀推断：

```python
('[图片]', '图片'), ('[文件]', '文件'), ('[链接]', '链接'), ('[语音]', '语音'), ...
```

这是有意的取舍：不依赖内部类名意味着**跨微信版本更稳**，但对"看起来像前缀"的
普通文本会误判（例如用户真的发了一条以 `[图片]` 开头的文字）。

另外，**无法从树里区分消息的发送者**（自己 vs 对方），`read_messages()` 统一返回
`sender=None`。判断"是不是我发的"需要上层按业务逻辑处理。

## 7. 已知坑（都踩过）

### 7.1 AT-SPI 坐标是 96 DPI 的逻辑像素

AT-SPI 的 `Component.GetExtents` 以 96 DPI 为基准，而 Xvfb 不给 `-dpi` 时按屏幕
毫米数算出 100 DPI，于是出现 **1.0417 的比例误差**：

```
物理窗口 200,150 / 292x396   →   AT-SPI 上报 192,144 / 280x380
```

按 AT-SPI 坐标直接点击会系统性偏左上。两种解法：

* 启动 Xvfb 时加 `-dpi 96`（推荐，坐标 1:1）；
* 或设 `PYWEIXIN_ATSPI_SCALE=1.0417` 让后端换算。

### 7.2 `Action.DoAction` 会让微信 SIGSEGV

微信的侧边栏、会话列表项是 Qt 自绘控件：只有 role，没有实现
`QAccessibleActionInterface`。对它们调 `DoAction` 会让 Qt 的 Action adaptor
解引用空指针，**主进程直接 core dump**。

所以本后端**只读 AT-SPI**，所有"写"操作走 XTest。`platform/linux/` 里没有任何
`DoAction` 调用。

### 7.3 聊天区是独立的顶层 frame

微信 4.x 在 Linux 上把每个已打开的会话渲染成一个**独立的顶层 frame**，名字就是会话标题：

```
[application] 'wechat'
  [frame] '微信'                 ← 主窗口
    [list] '会话' ...
  [frame] '文件传输助手'          ← 会话窗口(与主窗口平级!)
    [list] '消息'
    [text] '输入'
```

因此**从主窗口 `child_window` 往下找消息列表永远找不到**——必须从会话 frame 定位。
`linux_auto._chat_spec()` 就是干这个的。当前打开的是哪个会话，也靠这些 frame 的名字判断。

### 7.4 模态弹窗会让整棵树"不可见"

微信弹出「发送失败 / 我知道了」时，其余所有节点都会丢掉 `SHOWING` 状态。
此时任何 `visible_only=True` 的查找都会失败。所以发送后必须**先关弹窗、再回读**。

### 7.5 输入框的 `name` 不固定

聊天输入框的 AT-SPI `name` 可能是会话标题（`文件传输助手`），也可能是占位符
（`输入`）。不能靠 `name` 定位，只能靠"下半屏 + 面积最大的 text 角色"。

### 7.6 `xclip` 会挂死 `subprocess.run`

`xclip -selection clipboard -in` 会 fork 一个常驻子进程持有剪贴板。子进程继承了
父进程的 stdout/stderr，用 `subprocess.run(..., stdout=PIPE)` 会一直等 EOF →
**永久挂起**。必须用 `Popen` + `DEVNULL`，且不能 `wait()`。

### 7.7 中文必须走剪贴板

`xdotool type` 对 Unicode 是"临时映射 keysym"，不经过输入法；在中文环境下容易
变成候选词或丢字。本后端统一用 `xclip` + `Ctrl+V`。

### 7.8 消息列表会混入时间行

`[list] '消息'` 的子项里混着 `20:20` / `昨天 08:08` / `2026年11月26日` 这类时间分割行，
不是消息。`read_messages()` 用正则把它们滤掉。

## 8. 实测记录

环境：

| 项 | 值 |
|---|---|
| 发行版 | Arch Linux |
| 微信 | `wechat-bin 4.1.13.29`，`/opt/wechat/wechat` |
| 显示 | Xvfb `:99` 1600×1000×24，`-dpi 96` |
| 会话总线 | 私有 `dbus-daemon` + `/usr/lib/at-spi-bus-launcher` |
| 微信环境 | `QT_QPA_PLATFORM=xcb`、`QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1` |
| UI 框架 | Qt 5.15.14（静态链接），AT-SPI2 原生注册 |

测量：

| 指标 | 值 |
|---|---|
| 登录窗口节点数 | 169（可见 20，全部带坐标） |
| 主窗口节点数 | 1120–1124 |
| 全量遍历耗时 | 0.06 s（登录窗）/ 0.3–0.5 s（主窗口） |
| 角色分布（主窗口） | `filler 580 / button 297 / label 185 / list item 13 / list 5 / text 4 / frame 1` |
| 会话列表项 name 格式 | `备注\n最后一条消息\n时间`（免打扰多一行 `消息免打扰`） |
| 本地 IPC | **无**：无监听 TCP 端口、无 D-Bus 服务名、无 unix socket |

闭环测试（`scripts/linux_closed_loop.py`，2026-11-26 20:27）：

```
[OK] 登录态检测: {"is_logged_in": true}
[OK] 白名单拦截: {"rejected": "25王超越", "error": "RecipientNotAllowed"}
[OK] 打开会话: {"friend": "文件传输助手"}
[OK] 发送并回读: {"sent": "[pyweixin][linux] 闭环测试 2026-11-26 20:27:59",
                 "read_back": "[pyweixin][linux] 闭环测试 2026-11-26 20:27:59", "type": "文本"}
[OK] 读取最近消息: {"count": 3}
RESULT: PASS
```

证据：`evidence/linux_01_chat_open.png`、`evidence/linux_02_after_send.png`、
`evidence/linux_closed_loop.json`。

单元测试：`python3 -m unittest discover -s tests` → **57 项通过**
（选择器翻译 21 + 快照/定位/动作 26 + 收件人白名单 10）。

## 9. Windows 侧怎么保证没被改坏

改动都发生在平台边界上，Windows 路径**行为不变**：

* `platform/windows.py` 只是把 pywinauto 包了一层，`attach()` 返回的仍然是原生
  `WindowSpecification`，`WeChatAuto` 里 300+ 处 `child_window` / `click_input` 不用改；
* `__init__.py` 在 Windows 上走的还是原来的 `from pyweixin.WeChatAuto import ...`；
* `Config.py` 的注册表分支保留，只在 `IS_WINDOWS` 为假时才走 Linux 分支；
* `Uielements.py` 只把 `ListItemWrapper` 的 import 变成可选（它本来只用于类型标注）。

没有 Windows 机器，所以回归靠 **mock 单测**（`tests/test_linux_tree.py` 里的
`FakeSession` / `FakeX11` 就是为此设计的）+ 接口一致性检查，而不是实机跑。

## 10. 下一步

1. 发送文件/图片（X11 `text/uri-list` 是否被微信接受，待验证）；
2. 轮询监听新消息（会话列表项 name 变化 + 未读数解析）；
3. 把 `WeChatAuto` 里真正平台无关的部分（消息解析、时间戳正则、`ColorMatch`）
   抽到 `platform` 之上，逐步扩大 Linux 可复用面；
4. Wayland 支持（`ydotool` / `wl-clipboard`，且需要 `QT_QPA_PLATFORM=wayland` 下的
   AT-SPI 行为验证）；
5. CI：用 `xvfb-run` + 假微信窗口跑一遍 `platform` 层集成测试。
