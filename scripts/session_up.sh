#!/bin/bash
# 启动隔离的 Xvfb(-dpi 96) + D-Bus 会话 + AT-SPI 无障碍总线。
set -u
source "$(dirname "$0")/env.sh"
mkdir -p "$XDG_RUNTIME_DIR"; chmod 700 "$XDG_RUNTIME_DIR"

# 1) Xvfb：-dpi 96 让 AT-SPI 坐标与物理像素 1:1（Xvfb 默认按屏幕 mm 算出 100 DPI，
#    会导致 AT-SPI 上报的逻辑坐标 = 物理 * 96/dpi）
if ! pgrep -f "[X]vfb $DISPLAY" >/dev/null; then
  Xvfb $DISPLAY -screen 0 1600x1000x24 -dpi 96 -nolisten tcp -ac >/tmp/xvfb.log 2>&1 &
  sleep 1.5
fi

# 2) 私有 D-Bus 会话总线
if [ ! -S "$XDG_RUNTIME_DIR/bus" ] || ! dbus-send --session --print-reply \
     --dest=org.freedesktop.DBus / org.freedesktop.DBus.Peer.Ping >/dev/null 2>&1; then
  rm -f "$XDG_RUNTIME_DIR/bus"
  dbus-daemon --session --address="unix:path=$XDG_RUNTIME_DIR/bus" --fork \
    --print-pid >"$XDG_RUNTIME_DIR/bus.pid" 2>/dev/null
  sleep 0.5
fi

# 3) AT-SPI 总线（at-spi-bus-launcher 顺带拉起 registryd）
if ! dbus-send --session --print-reply --dest=org.freedesktop.DBus / \
      org.freedesktop.DBus.ListNames 2>/dev/null | grep -q 'org.a11y.Bus'; then
  /usr/lib/at-spi-bus-launcher >/tmp/atspi-bus.log 2>&1 &
  sleep 1.5
fi
