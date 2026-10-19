"""One-off helper: subset the brand fonts to printable ASCII + middle dot and
write tools/live/fonts.json ({"mono": b64, "sg": b64}) for build-live.mjs.
Run: python tools/live/make_fonts.py
"""
import base64
import io
import json
import os

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.normpath(os.path.join(HERE, "..", "design", "fonts"))
FILES = {"mono": "JetBrainsMono.woff2", "sg": "SpaceGrotesk.woff2"}
TEXT = "".join(chr(c) for c in range(0x20, 0x7F)) + "\u00b7"


def subset_b64(path):
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga", "calt", "ccmp", "locl", "mark", "mkmk"]
    opts.name_IDs = [1, 2]
    opts.hinting = False
    opts.notdef_outline = False
    opts.drop_tables += ["DSIG"]
    font = TTFont(path)
    if "fvar" in font:  # pin the variable weight axis to 500 to keep the file small
        font = instancer.instantiateVariableFont(font, {"wght": 500})
    sub = subset.Subsetter(opts)
    sub.populate(text=TEXT)
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def main():
    out = {k: subset_b64(os.path.join(FONT_DIR, f)) for k, f in FILES.items()}
    with open(os.path.join(HERE, "fonts.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh)
    print({k: len(v) for k, v in out.items()})


if __name__ == "__main__":
    main()
