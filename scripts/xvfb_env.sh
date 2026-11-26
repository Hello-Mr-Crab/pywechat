#!/bin/bash
# 私有 Xvfb 会话环境（不污染真实桌面 :0）
export DISPLAY=:99
export XDG_RUNTIME_DIR=/tmp/xdg-pywechat-runtime
export HOME=/home/bot-for-imitoy
mkdir -p "$XDG_RUNTIME_DIR"
chmod 700 "$XDG_RUNTIME_DIR"
export QT_QPA_PLATFORM=xcb
export QT_LOGGING_RULES='qt.qpa.*=false'
export NO_AT_BRIDGE=0
export GTK_MODULES=
export GDK_BACKEND=x11
export XDG_SESSION_TYPE=x11
export XDG_CURRENT_DESKTOP=GNOME
export WECHAT_LOGS_DIR=/tmp/wechat-logs
