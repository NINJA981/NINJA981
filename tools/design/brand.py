"""Brand library for the profile README graphics.

Black-hole editorial look (matches the portfolio): ink, cream, orange accretion ring.
Every graphic is built twice (dark, light). Fonts are subset per SVG and embedded as
base64 woff2 so they render inside GitHub's image proxy. No external resources.
"""
import base64
import io
import math
import os
import random

from fontTools import subset
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")
OUT_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "assets", "brand"))

FONT_FILES = {
    "fr": "Fraunces.woff2",
    "fri": "FrauncesItalic.woff2",
    "mono": "JetBrainsMono.woff2",
    "sg": "SpaceGrotesk.woff2",
}
FAMILY = {"fr": "SC Fraunces", "fri": "SC Fraunces It", "mono": "SC Mono", "sg": "SC Grotesk"}
FALLBACK = {
    "fr": "Georgia, 'Times New Roman', serif",
    "fri": "Georgia, 'Times New Roman', serif",
    "mono": "ui-monospace, SFMono-Regular, Consolas, 'Courier New', monospace",
    "sg": "'Segoe UI', Helvetica, Arial, sans-serif",
}
WEIGHT_RANGE = {"fr": "100 900", "fri": "100 900", "mono": "100 800", "sg": "300 700"}
FONT_STYLE = {"fr": "normal", "fri": "italic", "mono": "normal", "sg": "normal"}

THEMES = {
    "dark": dict(
        name="dark", bg="#12100c", bg2="#1a1712", surface="#1a1712", surface2="#221e17",
        border="#2c2820", text="#ece6d6", muted="#9a9280", dim="#6d6757",
        accent="#ff7a18", accent2="#ffb347", cool="#5bc0be", star="#ece6d6",
        glow=0.55, grid="#241f18", ok="#7bc47f",
    ),
    "light": dict(
        name="light", bg="#f4efe3", bg2="#fffaf0", surface="#fffaf0", surface2="#efe8d8",
        border="#d9d0bb", text="#16140f", muted="#6b6455", dim="#8f8672",
        accent="#d9600a", accent2="#ff7a18", cool="#1f8a87", star="#16140f",
        glow=0.30, grid="#e6dfcd", ok="#2f7d34",
    ),
}

_font_cache = {}


def _font(fam):
    if fam not in _font_cache:
        _font_cache[fam] = TTFont(os.path.join(FONT_DIR, FONT_FILES[fam]))
    return _font_cache[fam]


def text_width(fam, s, size, ls=0.0, bold_factor=1.0):
    """Approximate advance width (px) of s in a font at the given size."""
    f = _font(fam)
    upm = f["head"].unitsPerEm
    cmap = f.getBestCmap()
    hmtx = f["hmtx"]
    total = 0
    for ch in s:
        g = cmap.get(ord(ch))
        total += (hmtx[g][0] / upm if g else 0.55) * size
    return total * bold_factor + ls * len(s)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _embed(fam, chars):
    chars = set(chars) | {" "}
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga", "calt", "ccmp", "locl", "mark", "mkmk"]
    opts.name_IDs = [1, 2]
    opts.hinting = False
    opts.notdef_outline = False
    opts.drop_tables += ["DSIG"]
    font = TTFont(os.path.join(FONT_DIR, FONT_FILES[fam]))
    sub = subset.Subsetter(opts)
    sub.populate(text="".join(sorted(chars)))
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return (
        "@font-face{font-family:'%s';src:url(data:font/woff2;base64,%s) format('woff2');"
        "font-weight:%s;font-style:%s;font-display:swap;}" % (FAMILY[fam], b64, WEIGHT_RANGE[fam], FONT_STYLE[fam])
    )


class Doc:
    def __init__(self, w, h, theme, title, desc):
        self.w, self.h = w, h
        self.t = THEMES[theme]
        self.theme = theme
        self.title, self.desc = title, desc
        self.parts, self.defs = [], []
        self.chars = {k: set() for k in FAMILY}
        self._uid = 0

    # --- helpers -------------------------------------------------------
    def uid(self, p="i"):
        self._uid += 1
        return "%s%d" % (p, self._uid)

    def add(self, s):
        self.parts.append(s)

    def d(self, s):
        self.defs.append(s)

    def text(self, x, y, s, fam, size, fill, weight=400, anchor="start", ls=0, opacity=None, extra=""):
        self.chars[fam].update(s)
        attrs = [
            'x="%s"' % _n(x), 'y="%s"' % _n(y),
            'font-family="\'%s\', %s"' % (FAMILY[fam], FALLBACK[fam]),
            'font-size="%s"' % _n(size), 'font-weight="%s"' % weight, 'fill="%s"' % fill,
        ]
        if anchor != "start":
            attrs.append('text-anchor="%s"' % anchor)
        if ls:
            attrs.append('letter-spacing="%s"' % _n(ls))
        if opacity is not None:
            attrs.append('opacity="%s"' % opacity)
        if extra:
            attrs.append(extra)
        self.add("<text %s>%s</text>" % (" ".join(attrs), esc(s)))

    def rect(self, x, y, w, h, r=0, fill="none", stroke=None, sw=1, extra=""):
        a = 'x="%s" y="%s" width="%s" height="%s"' % (_n(x), _n(y), _n(w), _n(h))
        if r:
            a += ' rx="%s"' % _n(r)
        a += ' fill="%s"' % fill
        if stroke:
            a += ' stroke="%s" stroke-width="%s"' % (stroke, _n(sw))
        if extra:
            a += " " + extra
        self.add("<rect %s/>" % a)

    def render(self):
        css = "".join(_embed(f, c) for f, c in self.chars.items() if c)
        head = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
            'role="img" aria-labelledby="t d">' % (self.w, self.h, self.w, self.h)
        )
        return (
            head
            + '<title id="t">%s</title><desc id="d">%s</desc>' % (esc(self.title), esc(self.desc))
            + "<defs><style>%s</style>%s</defs>" % (css, "".join(self.defs))
            + "".join(self.parts)
            + "</svg>"
        )


def _n(v):
    if isinstance(v, float):
        return ("%.2f" % v).rstrip("0").rstrip(".")
    return str(v)


# --- shared drawing pieces ---------------------------------------------------
def stars(doc, x0, x1, y0, y1, n, seed=7, twinkle=10):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        r = rnd.choice([0.7, 0.9, 1.1, 1.4])
        op = rnd.choice([0.25, 0.4, 0.55, 0.7]) * (1.0 if doc.theme == "dark" else 0.6)
        if i < twinkle:
            dur = rnd.uniform(3, 7)
            out.append(
                '<circle cx="%s" cy="%s" r="%s" fill="%s" opacity="%s"><animate attributeName="opacity" '
                'values="%s;%s;%s" dur="%.1fs" repeatCount="indefinite"/></circle>'
                % (_n(round(x, 1)), _n(round(y, 1)), r, doc.t["star"], op, op, round(op * 0.25, 2), op, dur)
            )
        else:
            out.append(
                '<circle cx="%s" cy="%s" r="%s" fill="%s" opacity="%s"/>'
                % (_n(round(x, 1)), _n(round(y, 1)), r, doc.t["star"], op)
            )
    doc.add("".join(out))


def blackhole(doc, cx, cy, k=1.0, tilt=-16, dot=True):
    """Accretion disc, lensing ring, event horizon and a slow orbiting dot."""
    t = doc.t
    g, dk, bl, bl2 = doc.uid("g"), doc.uid("dk"), doc.uid("bl"), doc.uid("bs")
    doc.d(
        '<radialGradient id="%s"><stop offset="0" stop-color="%s" stop-opacity="%s"/>'
        '<stop offset="0.45" stop-color="%s" stop-opacity="%s"/><stop offset="1" stop-color="%s" stop-opacity="0"/></radialGradient>'
        % (g, t["accent"], t["glow"], t["accent"], round(t["glow"] * 0.32, 3), t["accent"])
    )
    doc.d(
        '<linearGradient id="%s" x1="0" x2="1"><stop offset="0" stop-color="%s" stop-opacity="0"/>'
        '<stop offset="0.22" stop-color="%s"/><stop offset="0.5" stop-color="#fff1d0"/>'
        '<stop offset="0.78" stop-color="%s"/><stop offset="1" stop-color="%s" stop-opacity="0"/></linearGradient>'
        % (dk, t["accent2"], t["accent2"], t["accent"], t["accent"])
    )
    doc.d('<filter id="%s" x="-30%%" y="-60%%" width="160%%" height="220%%"><feGaussianBlur stdDeviation="%s"/></filter>' % (bl, _n(6 * k)))
    doc.d('<filter id="%s" x="-30%%" y="-30%%" width="160%%" height="160%%"><feGaussianBlur stdDeviation="%s"/></filter>' % (bl2, _n(2.2 * k)))
    rx, ry, hr = 250 * k, 56 * k, 80 * k
    parts = [
        '<g transform="translate(%s %s)">' % (_n(cx), _n(cy)),
        '<circle r="%s" fill="url(#%s)"/>' % (_n(270 * k), g),
        '<g transform="rotate(%s)">' % tilt,
        '<ellipse rx="%s" ry="%s" fill="none" stroke="url(#%s)" stroke-width="%s" filter="url(#%s)" opacity="0.85"/>' % (_n(rx), _n(ry), dk, _n(18 * k), bl),
        '<ellipse rx="%s" ry="%s" fill="none" stroke="url(#%s)" stroke-width="%s" opacity="0.55"/>' % (_n(rx), _n(ry), dk, _n(3 * k)),
        "</g>",
        # lensed halo over the top and under the bottom of the horizon
        '<circle r="%s" fill="none" stroke="%s" stroke-width="%s" opacity="0.85" filter="url(#%s)"/>' % (_n(hr + 6 * k), t["accent2"], _n(5 * k), bl2),
        '<circle r="%s" fill="%s"/>' % (_n(hr), "#000"),
        '<circle r="%s" fill="none" stroke="%s" stroke-width="%s" opacity="0.9"/>' % (_n(hr + 1.5 * k), t["accent2"], _n(1.6 * k)),
        # front half of the disc passes in front of the horizon
        '<g transform="rotate(%s)"><path d="M %s 0 A %s %s 0 0 0 %s 0" fill="none" stroke="url(#%s)" stroke-width="%s" stroke-linecap="round"/>'
        % (tilt, _n(-rx), _n(rx), _n(ry), _n(rx), dk, _n(7 * k)),
    ]
    if dot:
        parts.append(
            '<circle r="%s" fill="#ffe2ae"><animateMotion dur="16s" repeatCount="indefinite" '
            'path="M %s 0 A %s %s 0 1 1 %s 0 A %s %s 0 1 1 %s 0"/></circle>'
            % (_n(5 * k), _n(-rx), _n(rx), _n(ry), _n(rx), _n(rx), _n(ry), _n(-rx))
        )
    parts += ["</g>", "</g>"]
    doc.add("".join(parts))


def orbit_mark(doc, cx, cy, r=14, dur=9):
    """Tiny orbit glyph used as a recurring accent."""
    t = doc.t
    doc.add(
        '<g transform="translate(%s %s)"><ellipse rx="%s" ry="%s" fill="none" stroke="%s" stroke-width="1.4" '
        'transform="rotate(-20)" opacity="0.8"/><circle r="%s" fill="%s"/><circle r="2" fill="%s">'
        '<animateMotion dur="%ss" repeatCount="indefinite" path="M %s 0 A %s %s 0 1 1 %s 0 A %s %s 0 1 1 %s 0" rotate="auto"/></circle></g>'
        % (_n(cx), _n(cy), _n(r), _n(r * 0.38), t["accent"], _n(r * 0.28), "#000" if doc.theme == "dark" else t["text"], t["accent2"], dur,
           _n(-r), _n(r), _n(r * 0.38), _n(r), _n(r), _n(r * 0.38), _n(-r))
    )


def save(doc, name):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, "%s-%s.svg" % (name, doc.theme))
    data = doc.render()
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(data)
    return path, len(data)
