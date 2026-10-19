"""Client-work cards built from the real brand imagery of each store (cropped, compressed, embedded)."""
import base64
import io
import os

from PIL import Image

from brand import Doc, save, _n

SRC = os.environ.get("CLIENT_SRC", "X:/Projects")
W, H = 600, 320

NCS = os.path.join(SRC, "ncs", "ncs-santhanam", "public")
MET = os.path.join(SRC, "navin-business-source", "public")


def jpeg_uri(path, w, h, focus=(0.5, 0.5), q=70, scale=2, bg=(255, 255, 255)):
    """Cover-crop an image to w x h (rendered at `scale`x for sharpness) and return a data URI."""
    im = Image.open(path)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        base = Image.new("RGBA", im.size, bg + (255,))
        base.alpha_composite(im)
        im = base
    im = im.convert("RGB")
    tw, th = int(w * scale), int(h * scale)
    ratio = max(tw / im.width, th / im.height)
    im = im.resize((max(tw, round(im.width * ratio)), max(th, round(im.height * ratio))), Image.LANCZOS)
    left = round((im.width - tw) * focus[0])
    top = round((im.height - th) * focus[1])
    im = im.crop((left, top, left + tw, top + th))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=q, optimize=True, progressive=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def tile(d, uri, x, y, w, h, r=12, border=None):
    cid = d.uid("t")
    d.d('<clipPath id="%s"><rect x="%s" y="%s" width="%s" height="%s" rx="%s"/></clipPath>' % (cid, _n(x), _n(y), _n(w), _n(h), r))
    d.add('<image href="%s" x="%s" y="%s" width="%s" height="%s" preserveAspectRatio="xMidYMid slice" clip-path="url(#%s)"/>' % (uri, _n(x), _n(y), _n(w), _n(h), cid))
    if border:
        d.add('<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="none" stroke="%s" stroke-width="1.4"/>' % (_n(x), _n(y), _n(w), _n(h), r, border))


def _bg(d, c1, c2, accent):
    gid = d.uid("g")
    d.d('<linearGradient id="%s" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (gid, c1, c2))
    d.add('<rect width="%d" height="%d" rx="18" fill="url(#%s)"/>' % (W, H, gid))
    pid = d.uid("p")
    d.d('<pattern id="%s" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><path d="M0 0V14" stroke="%s" stroke-width="1" opacity="0.07"/></pattern>' % (pid, accent))
    d.add('<rect width="%d" height="%d" rx="18" fill="url(#%s)"/>' % (W, H, pid))


def ncs(theme):
    d = Doc(W, H, theme, "NCS Santhanam silk saree store",
            "Lookbook collage from the real NCS Santhanam store: the peacock logo and three silk saree photographs, with its collections Kanchipuram, soft silk and wedding.")
    gold = "#d4a84b"
    _bg(d, "#2b1456", "#150a2e", gold)
    logo = jpeg_uri(os.path.join(NCS, "logo1.jpg"), 176, 65, q=80)
    tile(d, logo, 24, 18, 176, 65, 8, border="#d4a84b55")
    d.text(576, 38, "CLIENT WORK  ·  SILK SAREES", "mono", 12, gold, weight=600, anchor="end", ls=2)
    d.text(576, 58, "STORE · ADMIN · WORKER", "mono", 11, "#b9a9d8", weight=500, anchor="end", ls=1.5)
    imgs = [
        ("images/hero/hero-main.png", (0.45, 0.4), 24, 100, 134, 196),
        ("images/collections/kanchipuram.png", (0.5, 0.5), 168, 86, 134, 196),
        ("images/products/p2.png", (0.55, 0.3), 312, 108, 134, 196),
    ]
    for rel, focus, x, y, w, h in imgs:
        tile(d, jpeg_uri(os.path.join(NCS, rel), w, h, focus), x, y, w, h, 12, border="#d4a84b66")
    for i, lab in enumerate(("KANCHIPURAM", "SOFT SILK", "WEDDING")):
        y = 130 + i * 44
        d.add('<line x1="462" y1="%d" x2="576" y2="%d" stroke="%s" stroke-width="1" opacity="0.5"/>' % (y - 16, y - 16, gold))
        d.text(462, y + 2, lab, "mono", 13, "#f1e6c8", weight=600, ls=1.5)
    d.text(462, 290, "RAZORPAY  ·  CI/CD", "mono", 10.5, "#b9a9d8", weight=500, ls=1)
    d.add('<rect x="0.5" y="0.5" width="%d" height="%d" rx="18" fill="none" stroke="#d4a84b55"/>' % (W - 1, H - 1))
    return save(d, "card-ncs")


def methagu(theme):
    d = Doc(W, H, theme, "Methagu Karuppatti palm jaggery store",
            "Collage from the real Methagu Karuppatti store: the Tamil and English logo, palm jaggery being boiled in a cauldron, a jaggery block and a palm grove at sunrise.")
    gold = "#c89b3c"
    _bg(d, "#3b1f14", "#1c0e09", gold)
    logo = jpeg_uri(os.path.join(MET, "logo-horizontal.png"), 193, 56, q=82, bg=(0, 0, 0))
    tile(d, logo, 24, 20, 193, 56, 8, border="#c89b3c55")
    d.text(576, 38, "CLIENT WORK  ·  PALM JAGGERY", "mono", 12, gold, weight=600, anchor="end", ls=2)
    d.text(576, 58, "ENGLISH + TAMIL STORE", "mono", 11, "#d7bfa5", weight=500, anchor="end", ls=1.5)
    tile(d, jpeg_uri(os.path.join(MET, "images/products/heritage-box.jpg"), 240, 196, (0.5, 0.5)), 24, 100, 240, 196, 12, border="#c89b3c66")
    tile(d, jpeg_uri(os.path.join(MET, "images/products/classic-karuppatti.jpg"), 160, 94, (0.55, 0.55)), 276, 100, 160, 94, 12, border="#c89b3c66")
    tile(d, jpeg_uri(os.path.join(MET, "images/products/palm-candy-crystals.jpg"), 160, 94, (0.5, 0.5)), 276, 202, 160, 94, 12, border="#c89b3c66")
    for i, lab in enumerate(("PALM JAGGERY", "PALM CANDY", "SPICED BLENDS")):
        y = 130 + i * 44
        d.add('<line x1="448" y1="%d" x2="576" y2="%d" stroke="%s" stroke-width="1" opacity="0.5"/>' % (y - 16, y - 16, gold))
        d.text(448, y + 2, lab, "mono", 13, "#f5e8cc", weight=600, ls=1.5)
    d.text(448, 290, "RAZORPAY  ·  COD", "mono", 10.5, "#d7bfa5", weight=500, ls=1)
    d.add('<rect x="0.5" y="0.5" width="%d" height="%d" rx="18" fill="none" stroke="#c89b3c55"/>' % (W - 1, H - 1))
    return save(d, "card-methagu")


def build_all():
    out = []
    for th in ("dark", "light"):
        out.append(ncs(th))
        out.append(methagu(th))
    return out
