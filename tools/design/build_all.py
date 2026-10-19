"""Build every README graphic: python tools/design/build_all.py"""
import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

MODULES = ["assets_basic", "assets_cards", "assets_diagrams", "assets_panels"]

if __name__ == "__main__":
    only = sys.argv[1:]
    total = 0
    for m in MODULES:
        if only and m not in only:
            continue
        try:
            mod = importlib.import_module(m)
        except ModuleNotFoundError as e:
            if e.name == m:
                continue
            raise
        for path, size in mod.build_all():
            total += size
            flag = "  <-- over 100 KB" if size > 100_000 else ""
            print("%-34s %6.1f KB%s" % (os.path.basename(path), size / 1024, flag))
    print("total %.1f KB" % (total / 1024))
