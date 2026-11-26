#!/usr/bin/env python3
'''对 pyweixin.platform(linux) 做一次只读冒烟:连 AT-SPI、找窗口、列控件。'''
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pyweixin import platform
from pyweixin.platform.linux import AtspiUnavailable

def main():
    be = platform.backend()
    print('backend =', be.name)
    d = be.desktop()
    print('applications =', d.applications())
    app = d.app_name()
    print('wechat app  =', app)

    snap = d.snapshot(force=True)
    print(f'snapshot: {len(snap.nodes)} nodes, scale={snap.scale}')

    win = be.main_window(timeout=2)
    if win is None:
        print('no main window'); return 1
    print('window =', win.resolve(), 'rect =', win.rectangle())
    print('is_logged_in =', be.is_logged_in())

    print('--- visible children ---')
    for c in win.children()[:12]:
        print('  ', c)
    print('--- visible buttons ---')
    for b in win.descendants(control_type='Button')[:15]:
        print('  ', b)
    print('--- lists ---')
    for l in win.descendants(control_type='List')[:10]:
        print('  ', l, 'children=', len(l.children()))
    return 0

if __name__ == '__main__':
    sys.exit(main())
