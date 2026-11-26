#!/bin/bash
set -u
source "$(dirname "$0")/env.sh"
cd /opt/wechat
nohup /opt/wechat/wechat "$@" >/tmp/wechat-run.log 2>&1 &
echo "wechat pid=$!"
