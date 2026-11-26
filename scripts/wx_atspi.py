#!/usr/bin/env python3
"""微信 Linux AT-SPI 探针 / 动作工具（研究用）。

用法:
  wx_atspi.py tree  [--depth N] [--role R] [--visible]
  wx_atspi.py find  --name 登录 [--role button]
  wx_atspi.py click --name 登录
"""
import argparse
import os
import subprocess
import sys
import time

def atspi():
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi
    Atspi.init()
    return Atspi

def norm(s):
    return (s or "").replace("\n", "\\n")

def children(node):
    out = []
    try:
        n = node.get_child_count()
    except Exception:
        return out
    for i in range(n):
        try:
            c = node.get_child_at_index(i)
            if c is not None:
                out.append(c)
        except Exception:
            pass
    return out

def extents(node, Atspi):
    try:
        e = node.get_extents(Atspi.CoordType.SCREEN)
        return (e.x, e.y, e.width, e.height)
    except Exception:
        return (0, 0, 0, 0)

def walk(node, Atspi, maxdepth, indent=0, out=None, visible_only=False):
    if out is None:
        out = []
    try:
        role = node.get_role_name() or ""
    except Exception:
        return out
    x, y, w, h = extents(node, Atspi)
    if visible_only and indent > 0 and (w == 0 or h == 0):
        return out
    out.append((indent, role, norm(node.get_name()), (x, y, w, h)))
    if indent >= maxdepth:
        return out
    for c in children(node):
        walk(c, Atspi, maxdepth, indent + 1, out, visible_only)
    return out

def wechat_app(Atspi):
    d = Atspi.get_desktop(0)
    for i in range(d.get_child_count()):
        a = d.get_child_at_index(i)
        if (a.get_name() or "").lower() == "wechat":
            return a
    return None

def find_all(node, Atspi, pred, depth=0, maxdepth=40):
    res = []
    try:
        if pred(node):
            res.append(node)
    except Exception:
        pass
    if depth < maxdepth:
        for c in children(node):
            res.extend(find_all(c, Atspi, pred, depth + 1, maxdepth))
    return res

def cmd_tree(Atspi, args):
    app = wechat_app(Atspi)
    if app is None:
        print("wechat application not found on a11y bus")
        return 1
    for indent, role, name, (x, y, w, h) in walk(app, Atspi, args.depth, visible_only=args.visible):
        if args.role and args.role.lower() not in role.lower():
            continue
        print(f"{'  '*indent}[{role}] {name!r} @{x},{y} {w}x{h}")
    return 0

def cmd_find(Atspi, args):
    app = wechat_app(Atspi)
    if app is None:
        print("wechat application not found")
        return 1
    def pred(n):
        try:
            nm = n.get_name() or ""
            rl = n.get_role_name() or ""
        except Exception:
            return False
        if args.name and args.name not in nm:
            return False
        if args.role and args.role.lower() not in rl.lower():
            return False
        return True
    hits = find_all(app, Atspi, pred)
    for h in hits:
        x, y, w, hh = extents(h, Atspi)
        print(f"[{h.get_role_name()}] {norm(h.get_name())!r} @{x},{y} {w}x{hh}")
    print(f"-- {len(hits)} hit(s)")
    return 0

def cmd_click(Atspi, args):
    app = wechat_app(Atspi)
    if app is None:
        print("wechat application not found")
        return 1
    def pred(n):
        try:
            if args.name and args.name not in (n.get_name() or ""):
                return False
            if args.role and args.role.lower() not in (n.get_role_name() or "").lower():
                return False
            x, y, w, h = extents(n, Atspi)
            return w > 0 and h > 0
        except Exception:
            return False
    hits = find_all(app, Atspi, pred)
    if not hits:
        print("no visible match")
        return 1
    h = hits[0]
    x, y, w, hh = extents(h, Atspi)
    cx, cy = x + w // 2, y + hh // 2
    print(f"click [{h.get_role_name()}] {norm(h.get_name())!r} at ({cx},{cy})")
    subprocess.run(["xdotool", "mousemove", str(cx), str(cy)], check=True)
    time.sleep(0.2)
    subprocess.run(["xdotool", "click", "1"], check=True)
    return 0

def main():
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["tree", "find", "click"])
    p.add_argument("--depth", type=int, default=8)
    p.add_argument("--role", default=None)
    p.add_argument("--name", default=None)
    p.add_argument("--visible", action="store_true")
    args = p.parse_args()
    Atspi = atspi()
    return {"tree": cmd_tree, "find": cmd_find, "click": cmd_click}[args.cmd](Atspi, args)

if __name__ == "__main__":
    sys.exit(main())
