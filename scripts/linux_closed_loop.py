#!/usr/bin/env python3
'''Linux 最小闭环实测:登录态 -> 打开会话 -> 发消息 -> 读回 -> 落证据。

只发「文件传输助手」(白名单内),不会碰任何真实联系人。
'''
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src'))
EVID = os.path.join(ROOT, 'evidence')
os.makedirs(EVID, exist_ok=True)

from pyweixin import linux_auto as wx
from pyweixin.linux_auto import RecipientNotAllowed, assert_allowed_recipient

def main() -> int:
    log = {'started_at': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'steps': []}

    def step(name, **kw):
        entry = {'step': name, 'ts': time.strftime('%H:%M:%S'), **kw}
        log['steps'].append(entry)
        print(f'[{"OK" if kw.get("ok", True) else "FAIL"}] {name}: '
              + json.dumps({k: v for k, v in kw.items() if k != "ok"}, ensure_ascii=False))

    bot = wx.client()
    ok = bot.is_logged_in()
    step('登录态检测', ok=ok, is_logged_in=ok)
    if not ok:
        return 1

    # 0) 白名单闸门:陌生人必须在触碰 UI 之前被拒
    try:
        assert_allowed_recipient('25王超越')
        step('白名单拦截', ok=False, note='竟然放行了!')
        return 1
    except RecipientNotAllowed as exc:
        step('白名单拦截', ok=True, rejected='25王超越', error=type(exc).__name__)

    text = f'[pyweixin][linux] 闭环测试 {time.strftime("%Y-%m-%d %H:%M:%S")}'
    bot.open_chat('文件传输助手')
    bot.screenshot(os.path.join(EVID, 'linux_01_chat_open.png'))
    step('打开会话', ok=True, friend='文件传输助手')

    rec = bot.send_message('文件传输助手', text)
    bot.screenshot(os.path.join(EVID, 'linux_02_after_send.png'))
    step('发送并回读', ok=True, sent=text, read_back=rec['content'],
         type=rec['type'])

    msgs = bot.read_messages(3)
    step('读取最近消息', ok=True, count=len(msgs),
         messages=[m['content'][:60] for m in msgs])

    log['finished_at'] = time.strftime('%Y-%m-%dT%H:%M:%S%z')
    log['result'] = 'PASS'
    with open(os.path.join(EVID, 'linux_closed_loop.json'), 'w', encoding='utf-8') as fh:
        json.dump(log, fh, ensure_ascii=False, indent=2)
    print('RESULT: PASS')
    return 0

if __name__ == '__main__':
    sys.exit(main())
