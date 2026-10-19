"""Icon link buttons for the contact row."""
from brand import Doc, save, text_width, _n
from logos import draw_logo, META

BUTTONS = [
    ("email", "Email", "Gmail", "Email Sai Charan at saicharan312008@gmail.com"),
    ("linkedin", "LinkedIn", "LinkedIn", "Sai Charan on LinkedIn"),
    ("portfolio", "Portfolio", None, "Sai Charan's portfolio at charan.loopfound.in"),
    ("github", "GitHub", "GitHub", "Sai Charan on GitHub"),
    ("leetcode", "LeetCode", "LeetCode", "Sai Charan on LeetCode"),
    ("resume", "Resume", None, "Download Sai Charan's resume as a PDF"),
]


def _icon(d, key, label_logo, x, y, s=24):
    t = d.t
    if key == "linkedin":
        d.rect(x, y, s, s, 5, fill="#0A66C2")
        d.text(x + s / 2, y + s * 0.73, "in", "sg", s * 0.62, "#ffffff", weight=700, anchor="middle")
    elif key == "portfolio":
        cx, cy, r = x + s / 2, y + s / 2, s / 2 - 1
        d.add('<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (_n(cx), _n(cy), _n(r), t["accent"]))
        d.add('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (_n(cx), _n(cy), _n(r * 0.42), _n(r), t["accent"]))
        d.add('<path d="M%s %s h%s M%s %s h%s" stroke="%s" stroke-width="1.6" fill="none"/>' % (_n(cx - r), _n(cy), _n(2 * r), _n(cx - r * 0.86), _n(cy - r * 0.5), _n(r * 1.72), t["accent"]))
        d.add('<path d="M%s %s h%s" stroke="%s" stroke-width="1.6" fill="none"/>' % (_n(cx - r * 0.86), _n(cy + r * 0.5), _n(r * 1.72), t["accent"]))
    elif key == "resume":
        d.add('<path d="M%s %s h%s l%s %s v%s a2 2 0 0 1 -2 2 h-%s a2 2 0 0 1 -2 -2 z" fill="none" stroke="%s" stroke-width="1.8" stroke-linejoin="round"/>' % (_n(x + 3), _n(y + 1), _n(s * 0.46), _n(s * 0.36), _n(s * 0.36), _n(s * 0.74), _n(s * 0.72 + 0.0), t["accent"]))
        d.text(x + s / 2 + 0.5, y + s * 0.8, "PDF", "mono", s * 0.3, t["accent"], weight=700, anchor="middle")
    else:
        draw_logo(d, label_logo, x, y, s)


def build(theme, key, label, logo, alt):
    h, s = 56, 24
    w = round(18 + s + 10 + text_width("sg", label, 18, bold_factor=1.06) + 22)
    d = Doc(w, h, theme, label, alt)
    t = d.t
    d.rect(0.5, 0.5, w - 1, h - 1, 28, fill=t["surface"], stroke=t["border"], sw=1.4)
    _icon(d, key, logo, 18, (h - s) / 2, s)
    d.text(18 + s + 10, 34.5, label, "sg", 18, t["text"], weight=600)
    return save(d, "btn-" + key)


def build_all():
    out = []
    for th in ("dark", "light"):
        for key, label, logo, alt in BUTTONS:
            out.append(build(th, key, label, logo, alt))
    return out
