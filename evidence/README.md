# evidence —— Linux 移植的证据链

## 登录阶段

| 文件 | 内容 |
|---|---|
| `01_wechat_launch.png` | 微信在裸 Xvfb(:99) 上启动后的首屏 |
| `02_after_login_click*.png` | 点击「登录」后提示"需在手机上完成登录" |
| `03_login_state*.png` | 登录窗口截图 |
| `08_restart_state.png` | 重启微信后回到扫码登录态 |

> 二维码截图（`qr_login.png`、`qr_window.png`）**含登录凭据，已在 `.gitignore` 中排除，不入库。**

## 最小闭环实测（2026-11-26 20:27）

| 文件 | 内容 |
|---|---|
| `linux_01_chat_open.png` | 打开「文件传输助手」会话后的全屏 |
| `linux_02_after_send.png` | 发送测试消息后的全屏（自己发出的绿气泡） |
| `linux_02_after_send_crop.png` | 上面的窗口区域裁剪，便于查看 |
| `linux_closed_loop.json` | 闭环每一步的时间戳与结果（PASS） |

## 环境

Xvfb `:99` 1600x1000 **`-dpi 96`** + 私有 D-Bus 会话 + `at-spi-bus-launcher`，
微信 `wechat-bin 4.1.13.29`，`QT_QPA_PLATFORM=xcb`、`QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1`。

复现脚本：`scripts/env.sh`、`scripts/session_up.sh`、`scripts/wechat_up.sh`、
`scripts/linux_closed_loop.py`。
