#!/bin/bash
# 统一的隔离会话环境（被其它脚本 source）。不触碰真实桌面 :0。
export HOME=/home/bot-for-imitoy
export DISPLAY=:99
export XDG_RUNTIME_DIR=/tmp/xdg-wx
export DBUS_SESSION_BUS_ADDRESS="unix:path=$XDG_RUNTIME_DIR/bus"
export QT_QPA_PLATFORM=xcb
export QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1
export NO_AT_BRIDGE=0
export XDG_SESSION_TYPE=x11
export XDG_CURRENT_DESKTOP=GNOME
