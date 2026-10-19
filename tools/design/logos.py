"""Brand logos (Simple Icons, CC0) drawn inside a Doc, with theme-aware colours and monogram fallbacks."""
import json
import os

from brand import _n

HERE = os.path.dirname(os.path.abspath(__file__))
ICON_DIR = os.path.join(HERE, "icons")
META = json.load(open(os.path.join(ICON_DIR, "meta.json"), encoding="utf-8"))

MONOGRAMS = {"SQL": "SQL", "pgvector": "pg", "BullMQ": "BQ", "RAG": "RAG", "Playwright": "PW", "LinkedIn": "in", "Speech-to-text": "STT"}


def _lum(hexs):
    r, g, b = (int(hexs[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def logo_color(doc, label):
    t = doc.t
    hexs = META[label]["hex"]
    lum = _lum(hexs)
    if doc.theme == "dark" and lum < 0.12:
        return t["text"]
    if doc.theme == "light" and lum > 0.75:
        return t["text"]
    return "#" + hexs


def has_logo(label):
    return label in META


def draw_logo(doc, label, x, y, size=22):
    """Draw the brand logo (or a monogram) with its top-left corner at x, y."""
    t = doc.t
    if label in META:
        path = open(os.path.join(ICON_DIR, META[label]["slug"] + ".path"), encoding="utf-8").read()
        doc.add('<path transform="translate(%s %s) scale(%s)" fill="%s" d="%s"/>' % (_n(x), _n(y), _n(round(size / 24, 4)), logo_color(doc, label), path))
        return
    mono = MONOGRAMS.get(label, label[:2])
    doc.rect(x, y, size, size, 6, fill="none", stroke=t["accent"], sw=1.6)
    fs = size * (0.34 if len(mono) >= 3 else 0.46)
    doc.text(x + size / 2, y + size / 2 + fs * 0.36, mono, "mono", fs, t["accent"], weight=700, anchor="middle")
