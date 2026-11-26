# pyweixin 的 Windows 专有点清单

> 目的：把 `src/pyweixin/` 里所有"出了 Windows 就跑不了"的地方列清楚，
> 作为 Linux 移植的输入。统计基于 `main` @ `8348a91`。
>
> 结论先行：**真正无法跨平台的只有 4 类**——UIA 控件树、窗口句柄操作、
> 剪贴板拖放结构、注册表。其余（像素识别、键盘模拟、音频）都有等价物。

## 0. 总量

| 模块 | 行数 | 依赖 Windows 的行 |
|---|---|---|
| `WeChatAuto.py` | 4832 | 157 |
| `WeChatTools.py` | 1698 | 45 |
| `WinSettings.py` | 326 | 35 |
| `utils.py` | 512 | 22 |
| `Config.py` | 222 | 5 |
| `Uielements.py` | 1166 | 2 |

按 API 计：`win32clipboard` 36、`win32gui` 27、`pywinauto` 22、`win32con` 18、
`winreg` 9、`pyautogui` 161、`psutil` 9、`win32api` 4、`ctypes.windll` 3、
`comtypes`/`pycaw` 各 1。

## 1. UI 控件树（pywinauto / UIAutomation）——最大的一块

调用面（`WeChatAuto` + `WeChatTools` + `utils`）：

| 方法 | 次数 | 说明 |
|---|---|---|
| `child_window(**kwargs)` | 342 | 按 `control_type`/`title`/`class_name`/`auto_id` 定位 |
| `click_input()` | 224 | 鼠标点击控件中心 |
| `children()` | 148 | 直接子节点 |
| `window_text()` | 149 | 取控件文本（会话列表三行信息都在这里） |
| `type_keys()` | 106 | 键盘输入，含 `{ENTER}`/`{DOWN}`/`{HOME}`/`{PGDN}` |
| `set_text()` | 41 | 直接写编辑框 |
| `descendants()` | 21 | 递归找 |
| `class_name()` | 47 | **按内部类名判断消息类型**（`mmui::ChatTextItemView` 等） |
| `automation_id()` | 11 | `session_item_<id>` 取 wxid |
| `is_selected()` / `is_visible()` | 5 / 4 | 列表项状态 |
| `scroll()` | 3 | 列表滚动 |

三处全局实例：

```python
desktop = Desktop(backend='uia')          # WeChatAuto.py:82
desktop = Desktop(backend='uia')          # WeChatTools.py
desktop = Desktop(backend='uia')          # utils.py:21
iuia = IUIA().iuia                        # utils.py:22
```

`IUIA().iuia` 只用于一件事：`utils.get_focused_element()` →
`GetFocusedElement()`。`traverse_chatList` / `traverse_chatHistoryList` 靠它做
**"焦点游走"**读消息（焦点元素 + runtime_id 去重判到底/到顶）。

### 关键依赖的是"UIA 属性"，不只是 API

- `class_name`：区分文本/图片/语音/链接/小程序/红包……**AT-SPI 没有对应物**。
- `element_info.control_type`、`element_info.runtime_id`：判断到底/到顶、去重。
- `GetCurrentPropertyValue(30159)`：微信把"`N` 条新消息"放在 UIA 的
  `FullDescription` 里，只能按属性 ID 读。
- `framework_id='Win32'`：定位 `ToolbarWindow32` / `#32770` 这类原生控件。

## 2. 窗口句柄与窗口管理（win32gui / win32con / win32api）

| 用法 | 次数 | 用途 |
|---|---|---|
| `SendMessage(hwnd, WM_SYSCOMMAND, SC_MAXIMIZE/SC_RESTORE/SC_MINIMIZE)` | 9 | 最大化/还原/最小化（`main_window.maximize()` 不可靠，作者注释说明） |
| `SetWindowPos(..., HWND_TOPMOST)` | 3 | 置顶（防止被别的窗口挡住导致 UIA 树拿不到） |
| `MoveWindow` / `GetSystemMetrics(SM_CX/CYSCREEN)` | 2 / 4 | 窗口居中、按屏幕算尺寸 |
| `EnumWindows` + `GetClassName` + `GetWindowText` | 2 | 按类名 `mmui::MainWindow` 找主窗口 hwnd |
| `FindWindow('#32770')` | 3 | 系统"选择文件夹"对话框 |
| `IsWindowVisible` | 1 | 判断窗口是否可见 |

## 3. 剪贴板（win32clipboard）——36 处

- 文本：`CF_UNICODETEXT` + `EmptyClipboard`/`SetClipboardData`。
- **文件**：`CF_HDROP` + 手写 `DROPFILES` 结构（`pFiles`/`fWide`/UTF-16 双 `\0` 结尾）。
  发文件、导出文件都靠"复制到剪贴板 → 微信里 Ctrl+V"。
- 读：`GetClipboardData` 取图片（朋友圈保存图片）/ 取文本。

这是 Linux 上**最难 1:1 复刻**的一处：Linux 用 X11 selection 协议，
`text/uri-list` 可以传文件，但微信 Linux 版是否接受 `text/uri-list` 粘贴**未验证**。

## 4. 注册表（winreg）——9 处

| 键 | 用途 |
|---|---|
| `HKCU\Software\Tencent\Weixin\InstallPath` | 定位微信安装目录 |
| `HKCU\Software\Tencent\Weixin\Version` | 取版本号（`0xf254186b` → `4.1.x.y` 的位运算解码） |

## 5. 系统设置（ctypes / comtypes / pycaw / sounddevice）

- `ctypes.windll.kernel32.SetThreadExecutionState`：`open_listening_mode` 防息屏。
- `pycaw`：`IAudioEndpointVolume` 设主音量到 100%。
- `sounddevice`：取默认音频输出设备（判断是不是 virtual cable）。
- `ctypes.windll.user32.GetDpiForWindow` / `GetSystemMetricsForDpi`：按 DPI 算窗口尺寸。
- `GetDpiForWindow` 这类在 Linux 上对应 X11 的 DPI（`Xft.dpi` / `xdpyinfo`）。

## 6. 输入模拟（pyautogui）——161 处

| 用法 | 用途 |
|---|---|
| `pyautogui.press('down'/'up'/'backspace'/'enter')` | 列表遍历、@ 撤回 |
| `pyautogui.hotkey('ctrl','v')` | 粘贴 |
| `pyautogui.screenshot(region=...)` | 像素级找按钮 |
| `pyautogui.FAILSAFE=False` | 关掉"鼠标到角落就抛异常" |

像素识别（`ColorMatch`）：朋友圈评论的**绿色发送按钮**、**灰色省略号**，
用 RGB 启发式找中心点。这部分与平台无关（换截图后端即可）。

## 7. 多语言 / 版本选择器（Uielements）

`Uielements.py` 里 900+ 行的选择器表本身是**平台无关的 dict**，
只有两处 Windows 依赖：

1. `from pywinauto.controls.uia_controls import ListItemWrapper`（仅类型标注）；
2. `language` / `Version` 来自 `Config`（注册表 + `WechatAppEx` 进程命令行）。

已改为：`import` 可选、`Version` 在 Linux 上从二进制里扫 `4.x.y.z`、
`language` 继续用 `psutil` 读 `WechatAppEx --lang=`（本来就是跨平台的）。

## 8. 移植结论

| Windows 专有点 | Linux 替代 |
|---|---|
| pywinauto UIA 树 | AT-SPI2（`GetChildren`/`GetRoleName`/`GetName`/`GetExtents`） |
| `click_input` / `mouse.click` | XTest（`xdotool`）——**不能用 `Action.DoAction`，会崩** |
| `type_keys` / `set_text` | XTest keysym + X 剪贴板（中文走剪贴板） |
| `class_name` 判消息类型 | **不可用**——只能按 `name` 文本模式推断（跨版本反而更稳） |
| `runtime_id` 判到底 | 按列表项 `name` 序列去重 |
| `GetCurrentPropertyValue(30159)` | **不可用**——AT-SPI 无此属性；改用会话列表项文本里的"N条新消息" |
| `SendMessage` 最大化/置顶 | X11 `_NET_WM_STATE` / 直接 `xdotool windowsize` |
| `win32clipboard` CF_HDROP | X11 `text/uri-list`（待验证） |
| `winreg` InstallPath/Version | 固定路径 `/opt/wechat` + 扫二进制版本号 |
| `SetThreadExecutionState` | X11 `xset s off` / `DPMS`（无需 root） |
| `pycaw` 音量 | `pactl`（可选，非核心） |
| `pyautogui.screenshot` | `ffmpeg x11grab`（已装） |
| `PIL` | 可省；截图走 ffmpeg，像素分析用 Pillow（可选依赖） |
