#!/usr/bin/env python3
"""AT-SPI 探测：列出桌面上的应用与窗口，可选打印子树。"""
import os, sys, argparse

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--depth", type=int, default=4)
    ap.add_argument("--app", default=None, help="只展开名字包含该串的应用")
    ap.add_argument("--address", default=None)
    args = ap.parse_args()

    addr = args.address or os.environ.get("AT_SPI_BUS_ADDRESS")
    if addr:
        os.environ["DBUS_SESSION_BUS_ADDRESS"] = addr

    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    Atspi.init()
    desktop = Atspi.get_desktop(0)
    print(f"desktop children = {desktop.get_child_count()}")

    def walk(node, depth, maxdepth, indent=0):
        try:
            role = node.get_role_name()
            name = (node.get_name() or "").replace("\n", "\\n")
            iface = []
            try:
                ex = node.get_extents(Atspi.CoordType.SCREEN)
                ext = f"@{ex.x},{ex.y} {ex.width}x{ex.height}"
            except Exception:
                ext = ""
            print(f"{'  '*indent}[{role}] {name!r} {ext}")
        except Exception as e:
            print(f"{'  '*indent}<err {e}>")
            return
        if depth >= maxdepth:
            return
        try:
            n = node.get_child_count()
        except Exception:
            return
        for i in range(n):
            try:
                walk(node.get_child_at_index(i), depth+1, maxdepth, indent+1)
            except Exception:
                pass

    for i in range(desktop.get_child_count()):
        app = desktop.get_child_at_index(i)
        nm = app.get_name()
        print(f"\n=== APP[{i}] {nm!r} ===")
        if args.app and args.app.lower() not in (nm or "").lower():
            continue
        walk(app, 0, args.depth)

if __name__ == "__main__":
    main()
