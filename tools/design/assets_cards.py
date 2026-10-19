import math
import random

from brand import Doc, orbit_mark, save, _n

W, H = 600, 320


def base(theme, eyebrow, title, desc):
    d = Doc(W, H, theme, title, desc)
    t = d.t
    cid = d.uid("c")
    pid = d.uid("p")
    gid = d.uid("g")
    d.d('<clipPath id="%s"><rect width="%d" height="%d" rx="18"/></clipPath>' % (cid, W, H))
    d.d('<pattern id="%s" width="30" height="30" patternUnits="userSpaceOnUse"><path d="M30 0H0V30" fill="none" stroke="%s" stroke-width="1"/></pattern>' % (pid, t["grid"]))
    d.d('<radialGradient id="%s" cx="0.85" cy="0.95" r="0.8"><stop offset="0" stop-color="%s" stop-opacity="%s"/><stop offset="1" stop-color="%s" stop-opacity="0"/></radialGradient>' % (gid, t["accent"], 0.22 if theme == "dark" else 0.16, t["accent"]))
    d.add('<rect width="%d" height="%d" rx="18" fill="%s"/>' % (W, H, t["bg"]))
    d.add('<g clip-path="url(#%s)"><rect width="%d" height="%d" fill="url(#%s)"/><rect width="%d" height="%d" fill="url(#%s)"/></g>' % (cid, W, H, pid, W, H, gid))
    d.text(24, 36, eyebrow, "mono", 14, t["accent"], weight=600, ls=3)
    orbit_mark(d, 566, 30, 11)
    return d


def finish(d, name):
    d.add('<rect x="0.5" y="0.5" width="%d" height="%d" rx="18" fill="none" stroke="%s"/>' % (W - 1, H - 1, d.t["border"]))
    return save(d, name)


def dash(d, x1, y1, x2, y2, color=None, w=2, dur=1.3):
    color = color or d.t["accent"]
    d.add(
        '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s" stroke-dasharray="4 6" stroke-linecap="round">'
        '<animate attributeName="stroke-dashoffset" from="20" to="0" dur="%ss" repeatCount="indefinite"/></line>'
        % (_n(x1), _n(y1), _n(x2), _n(y2), color, w, dur)
    )


def circ(d, cx, cy, r, fill="none", stroke=None, sw=1.5, extra=""):
    s = '<circle cx="%s" cy="%s" r="%s" fill="%s"' % (_n(cx), _n(cy), _n(r), fill)
    if stroke:
        s += ' stroke="%s" stroke-width="%s"' % (stroke, sw)
    d.add(s + (" " + extra if extra else "") + "/>")


def classiq(theme):
    d = base(theme, "EDGE AI  ·  EDTECH", "ClassIQ pipeline",
             "A Raspberry Pi records a lecture, speech-to-text and an LLM turn it into a quiz that appears on a student's phone.")
    t = d.t
    bx, by = 36, 108
    d.rect(bx, by, 150, 104, 10, fill=t["surface2"], stroke=t["accent"], sw=2)
    for i in range(14):
        circ(d, bx + 14 + i * 9.3, by + 12, 2, fill=t["dim"])
    d.rect(bx + 54, by + 34, 42, 42, 6, fill=t["border"], stroke=t["muted"], sw=1)
    d.rect(bx + 140, by + 30, 18, 16, 3, fill=t["muted"])
    d.rect(bx + 140, by + 58, 18, 16, 3, fill=t["muted"])
    d.text(bx + 75, by + 96, "PI 5", "mono", 13, t["muted"], weight=600, anchor="middle", ls=2)
    # waveform
    rnd = random.Random(4)
    for i in range(9):
        x = 210 + i * 10
        h1, h2 = rnd.randint(14, 52), rnd.randint(14, 52)
        d.add(
            '<rect x="%d" y="%s" width="5" height="%d" rx="2.5" fill="%s"><animate attributeName="height" values="%d;%d;%d" dur="%.1fs" repeatCount="indefinite"/>'
            '<animate attributeName="y" values="%s;%s;%s" dur="%.1fs" repeatCount="indefinite"/></rect>'
            % (x, _n(160 - h1 / 2), h1, t["accent2"], h1, h2, h1, 1.1 + i * 0.09, _n(160 - h1 / 2), _n(160 - h2 / 2), _n(160 - h1 / 2), 1.1 + i * 0.09)
        )
    dash(d, 304, 160, 330, 160)
    circ(d, 366, 160, 32, fill=t["surface"], stroke=t["accent"], sw=2)
    d.text(366, 170, "AI", "fr", 28, t["text"], weight=700, anchor="middle")
    d.text(366, 214, "STT + LLM", "mono", 13, t["muted"], weight=600, anchor="middle", ls=1)
    dash(d, 402, 160, 428, 160)
    d.rect(436, 70, 124, 196, 20, fill=t["surface2"], stroke=t["muted"], sw=2)
    d.rect(480, 80, 36, 6, 3, fill=t["border"])
    d.rect(452, 104, 92, 12, 6, fill=t["border"])
    for i, y in enumerate((130, 156, 182)):
        hl = i == 1
        d.rect(452, y, 92, 18, 9, fill=(t["accent"] if hl else "none"), stroke=(t["accent"] if hl else t["border"]), sw=1.5, extra=('fill-opacity="0.25"' if hl else ""))
        if hl:
            d.add('<path d="M526 %d l4 4 l8 -8" fill="none" stroke="%s" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>' % (y + 9, t["accent"]))
    d.text(498, 250, "QUIZ", "mono", 13, t["muted"], weight=600, anchor="middle", ls=2)
    d.text(24, 300, "lecture to quiz, in the classroom", "mono", 14, t["muted"], weight=500)
    return finish(d, "card-classiq")


def solace(theme):
    d = base(theme, "RAG  ·  SEMANTIC MEMORY", "Solace constellation",
             "A journal page is embedded into a field of points; the question lights up the nearest memories.")
    t = d.t
    d.rect(34, 72, 128, 176, 10, fill=t["surface2"], stroke=t["border"], sw=1.5)
    d.rect(48, 90, 56, 7, 3.5, fill=t["accent"])
    for i, wd in enumerate((96, 84, 96, 70, 92, 60)):
        d.rect(48, 112 + i * 20, wd, 5, 2.5, fill=t["border"])
    dash(d, 166, 160, 214, 160)
    d.text(190, 148, "embed", "mono", 12, t["muted"], weight=600, anchor="middle")
    nodes = [(250, 92), (292, 142), (262, 204), (322, 240), (352, 100), (372, 172), (412, 120), (440, 222), (470, 88),
             (502, 162), (534, 112), (522, 236), (392, 252), (308, 66), (330, 176), (468, 200)]
    edges = [(0, 1), (1, 2), (2, 3), (1, 4), (4, 5), (5, 6), (6, 8), (8, 10), (10, 9), (9, 7), (7, 12), (3, 12), (1, 14), (14, 5),
             (5, 7), (13, 4), (0, 13), (9, 15), (15, 7), (10, 6)]
    for a, b in edges:
        d.add('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1" opacity="0.7"/>' % (*nodes[a], *nodes[b], t["border"]))
    hot = {5, 6, 7}
    qx, qy = 424, 166
    for i in hot:
        dash(d, qx, qy, nodes[i][0], nodes[i][1], w=1.8)
    for i, (x, y) in enumerate(nodes):
        if i in hot:
            circ(d, x, y, 7, fill=t["accent2"], stroke=t["accent"], sw=2)
        else:
            circ(d, x, y, 4, fill=t["dim"])
    d.add('<circle cx="%d" cy="%d" r="12" fill="%s"><animate attributeName="r" values="10;15;10" dur="2.6s" repeatCount="indefinite"/></circle>' % (qx, qy, t["accent"]))
    circ(d, qx, qy, 24, stroke=t["accent"], sw=1.2, extra='opacity="0.5"')
    d.text(qx, qy + 46, "question", "mono", 12, t["muted"], weight=600, anchor="middle", ls=1)
    d.text(570, 298, "pgvector  ·  cited answers", "mono", 13, t["muted"], weight=500, anchor="end")
    return finish(d, "card-solace")


def leetx(theme):
    d = base(theme, "BROWSER EXTENSION", "LeetX Squads streak grid",
             "A grid of daily solves with streak, freeze, duel and squad features.")
    t = d.t
    rnd = random.Random(21)
    cols, rows, cell, gap = 15, 6, 24, 4
    x0, y0 = 30, 82
    for c in range(cols):
        for r in range(rows):
            lvl = rnd.choices([0, 1, 2, 3, 4], weights=[3, 2, 3, 3, 3])[0]
            if c > 11 and r > 3:
                lvl = 0
            x, y = x0 + c * (cell + gap), y0 + r * (cell + gap)
            if lvl == 0:
                d.rect(x, y, cell, cell, 5, fill=t["surface2"], stroke=t["border"], sw=1)
            else:
                d.rect(x, y, cell, cell, 5, fill=t["accent"], extra='fill-opacity="%s"' % (0.2 + lvl * 0.2))
    # pulse on the latest solved cell
    d.add('<rect x="%d" y="%d" width="%d" height="%d" rx="5" fill="none" stroke="%s" stroke-width="2"><animate attributeName="opacity" values="1;0.2;1" dur="2s" repeatCount="indefinite"/></rect>' % (x0 + 11 * (cell + gap), y0 + 5 * (cell + gap), cell, cell, t["accent2"]))
    # flame
    d.add('<path d="M520 70 C 538 92 548 104 548 124 C 548 142 534 152 520 152 C 506 152 492 142 492 124 C 492 112 500 104 504 96 C 506 106 512 110 516 108 C 512 96 514 82 520 70 Z" fill="%s" opacity="0.95"/>' % t["accent"])
    d.add('<path d="M520 112 C 530 122 534 128 534 136 C 534 144 528 150 520 150 C 512 150 506 144 506 136 C 506 128 514 122 520 112 Z" fill="%s"/>' % t["accent2"])
    for i, lab in enumerate(("STREAK", "FREEZE", "DUEL", "SQUAD")):
        y = 176 + i * 30
        d.rect(480, y, 90, 22, 11, fill="none", stroke=t["border"], sw=1.2)
        d.text(525, y + 16, lab, "mono", 12, t["muted"], weight=600, anchor="middle", ls=1.5)
    d.text(24, 300, "daily habit, built with friends", "mono", 14, t["muted"], weight=500)
    return finish(d, "card-leetx")


def cryptotrace(theme):
    d = base(theme, "GRAPH  ·  FORENSICS", "CryptoTrace wallet graph",
             "Unknown wallets are traced through hops to the exchange that most likely holds them.")
    t = d.t
    src = [(60, 100), (60, 160), (60, 220)]
    mid = [(190, 80), (190, 140), (190, 200), (190, 256)]
    mid2 = [(330, 112), (330, 172), (330, 232)]
    tx, ty = 492, 168
    links = [(src[0], mid[0]), (src[0], mid[1]), (src[1], mid[1]), (src[1], mid[2]), (src[2], mid[2]), (src[2], mid[3]),
             (mid[0], mid2[0]), (mid[1], mid2[0]), (mid[1], mid2[1]), (mid[2], mid2[1]), (mid[2], mid2[2]), (mid[3], mid2[2])]
    for a, b in links:
        d.add('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1.4" opacity="0.8"/>' % (*a, *b, t["border"]))
    for a in mid2:
        d.add('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1.4" opacity="0.8"/>' % (*a, tx, ty, t["border"]))
    for a, b in [(src[1], mid[1]), (mid[1], mid2[1]), (mid2[1], (tx, ty))]:
        dash(d, a[0], a[1], b[0], b[1], w=2.4)
    for p in src:
        circ(d, p[0], p[1], 9, fill=t["surface2"], stroke=t["muted"], sw=1.6)
    for p in mid + mid2:
        circ(d, p[0], p[1], 7, fill=t["surface"], stroke=t["dim"], sw=1.6)
    d.add('<polygon points="%s" fill="%s" stroke="%s" stroke-width="2"/>' % (
        " ".join("%s,%s" % (_n(round(tx + 40 * math.cos(math.radians(a)), 1)), _n(round(ty + 40 * math.sin(math.radians(a)), 1))) for a in range(0, 360, 60)),
        t["surface"], t["accent"]))
    d.text(tx, ty + 5, "VASP", "mono", 15, t["accent2"], weight=700, anchor="middle", ls=1)
    d.text(60, 292, "UNKNOWN", "mono", 12, t["muted"], weight=600, anchor="middle", ls=1)
    d.text(260, 292, "HOPS", "mono", 12, t["muted"], weight=600, anchor="middle", ls=1)
    d.text(tx, 232, "EXCHANGE", "mono", 12, t["muted"], weight=600, anchor="middle", ls=1)
    for i in range(5):
        d.rect(430 + i * 14, 262, 10, 14, 2, fill=(t["accent"] if i < 4 else "none"), stroke=t["accent"], sw=1.2)
    d.text(430, 296, "5-FACTOR SCORE", "mono", 11, t["muted"], weight=600, ls=1)
    return finish(d, "card-cryptotrace")


def jarvis(theme):
    d = base(theme, "VOICE  ·  AGENTS  ·  MCP", "JARVIS agent hub",
             "A voice command reaches a supervisor that delegates to eight specialist agents.")
    t = d.t
    cx, cy = 300, 166
    names = ["OPR", "NAV", "RES", "ENG", "COU", "PIL", "LIB", "CRI"]
    for i, n in enumerate(names):
        a = math.radians(i * 45 - 90)
        x, y = cx + math.cos(a) * 168, cy + math.sin(a) * 104
        dash(d, cx, cy, x, y, w=1.6, dur=1.5 + i * 0.1)
    d.add('<ellipse cx="%d" cy="%d" rx="170" ry="106" fill="none" stroke="%s" stroke-width="1" opacity="0.5"/>' % (cx, cy, t["border"]))
    for i, n in enumerate(names):
        a = math.radians(i * 45 - 90)
        x, y = cx + math.cos(a) * 168, cy + math.sin(a) * 104
        circ(d, x, y, 21, fill=t["surface"], stroke=t["accent"] if i % 2 == 0 else t["muted"], sw=1.8)
        d.text(x, y + 4.5, n, "mono", 12, t["text"], weight=600, anchor="middle")
    d.add('<circle cx="%d" cy="%d" r="46" fill="%s" opacity="0.18"><animate attributeName="r" values="42;54;42" dur="3.4s" repeatCount="indefinite"/></circle>' % (cx, cy, t["accent"]))
    circ(d, cx, cy, 30, fill="#000" if theme == "dark" else t["text"], stroke=t["accent2"], sw=2.5)
    d.text(cx, cy + 5, "J", "fr", 26, t["accent2"], weight=800, anchor="middle")
    # wake word waveform
    rnd = random.Random(8)
    for i in range(7):
        h1, h2 = rnd.randint(8, 34), rnd.randint(8, 34)
        x = 30 + i * 9
        d.add('<rect x="%d" y="%s" width="4" height="%d" rx="2" fill="%s"><animate attributeName="height" values="%d;%d;%d" dur="%.1fs" repeatCount="indefinite"/><animate attributeName="y" values="%s;%s;%s" dur="%.1fs" repeatCount="indefinite"/></rect>'
              % (x, _n(166 - h1 / 2), h1, t["accent2"], h1, h2, h1, 1.0 + i * 0.1, _n(166 - h1 / 2), _n(166 - h2 / 2), _n(166 - h1 / 2), 1.0 + i * 0.1))
    d.text(30, 216, "WAKE WORD", "mono", 11, t["muted"], weight=600, ls=1)
    d.text(570, 216, "11 MCP", "mono", 12, t["accent"], weight=700, anchor="end", ls=1)
    d.text(570, 232, "SERVERS", "mono", 11, t["muted"], weight=600, anchor="end", ls=1)
    d.text(24, 300, "one voice, many agents", "mono", 14, t["muted"], weight=500)
    return finish(d, "card-jarvis")


def visionnav(theme):
    d = base(theme, "ON-DEVICE  ·  ASSISTIVE", "VisionNav scene",
             "A phone camera detects hazards ahead of a walking path and speaks a short warning.")
    t = d.t
    # crosswalk band
    for i in range(7):
        d.rect(40 + i * 24, 96, 14, 44, 2, fill=t["muted"], extra='fill-opacity="0.35"')
    # camera cone
    cid = d.uid("cn")
    d.d('<linearGradient id="%s" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="%s" stop-opacity="0.5"/><stop offset="1" stop-color="%s" stop-opacity="0"/></linearGradient>' % (cid, t["accent"], t["accent"]))
    d.add('<polygon points="130,286 40,70 220,70" fill="url(#%s)"/>' % cid)
    dash(d, 130, 286, 130, 70, w=2.4)
    circ(d, 130, 292, 9, fill=t["accent"])
    # detections
    d.add('<rect x="64" y="160" width="62" height="40" rx="4" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="6 4"><animate attributeName="stroke-dashoffset" from="20" to="0" dur="1.6s" repeatCount="indefinite"/></rect>' % t["accent2"])
    d.text(64, 154, "POLE", "mono", 11, t["accent2"], weight=700, ls=1)
    d.add('<rect x="146" y="196" width="76" height="44" rx="4" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="6 4"><animate attributeName="stroke-dashoffset" from="20" to="0" dur="1.6s" repeatCount="indefinite"/></rect>' % t["accent2"])
    d.text(146, 190, "CAR", "mono", 11, t["accent2"], weight=700, ls=1)
    d.text(40, 88, "CROSSWALK", "mono", 11, t["muted"], weight=700, ls=1)
    # voice card
    d.rect(318, 118, 246, 128, 16, fill=t["surface2"], stroke=t["border"], sw=1.5)
    d.text(338, 156, "SPOKEN", "mono", 12, t["accent"], weight=600, ls=2)
    d.text(338, 188, "Crosswalk ahead.", "fr", 26, t["text"], weight=600)
    d.text(338, 214, "Vehicle on your right.", "sg", 17, t["muted"])
    rnd = random.Random(2)
    for i in range(8):
        h1, h2 = rnd.randint(6, 22), rnd.randint(6, 22)
        x = 460 + i * 11
        d.add('<rect x="%d" y="%s" width="5" height="%d" rx="2.5" fill="%s"><animate attributeName="height" values="%d;%d;%d" dur="%.1fs" repeatCount="indefinite"/><animate attributeName="y" values="%s;%s;%s" dur="%.1fs" repeatCount="indefinite"/></rect>'
              % (x, _n(150 - h1 / 2), h1, t["accent2"], h1, h2, h1, 1.0 + i * 0.1, _n(150 - h1 / 2), _n(150 - h2 / 2), _n(150 - h1 / 2), 1.0 + i * 0.1))
    d.text(318, 276, "VOICE  +  HAPTIC", "mono", 12, t["muted"], weight=600, ls=2)
    return finish(d, "card-visionnav")


def store(theme, key, eyebrow, title, desc, swatches, lang_chip, pay_chip):
    d = base(theme, eyebrow, title, desc)
    t = d.t
    d.rect(34, 58, 532, 26, 8, fill=t["surface2"], stroke=t["border"])
    circ(d, 52, 71, 6, fill=t["accent"])
    d.rect(68, 66, 70, 10, 5, fill=t["border"])
    d.rect(300, 66, 36, 10, 5, fill=t["border"])
    d.rect(346, 66, 36, 10, 5, fill=t["border"])
    cw = 44 if len(lang_chip) <= 2 else 70
    d.rect(512 - cw, 62, cw, 18, 9, fill="none", stroke=t["accent"], sw=1.2)
    d.text(512 - cw / 2, 75, lang_chip, "mono", 10, t["accent"], weight=700, anchor="middle", ls=1)
    d.add('<path d="M532 66 h14 l-2 10 h-10 z" fill="none" stroke="%s" stroke-width="1.6"/>' % t["muted"])
    circ(d, 548, 64, 5, fill=t["accent"])
    # banner
    gid = d.uid("b")
    d.d('<linearGradient id="%s" x1="0" x2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (gid, swatches[0], swatches[1]))
    d.add('<rect x="34" y="96" width="532" height="58" rx="10" fill="url(#%s)" opacity="0.9"/>' % gid)
    d.rect(52, 112, 150, 12, 6, fill="#ffffff", extra='fill-opacity="0.85"')
    d.rect(52, 132, 96, 8, 4, fill="#ffffff", extra='fill-opacity="0.5"')
    # product grid
    for i in range(4):
        x = 34 + i * 138
        d.rect(x, 168, 122, 112, 10, fill=t["surface2"], stroke=t["border"])
        d.rect(x + 8, 176, 106, 58, 6, fill=swatches[(i + 1) % len(swatches)], extra='fill-opacity="0.85"')
        d.rect(x + 8, 242, 70, 7, 3.5, fill=t["border"])
        d.rect(x + 8, 256, 40, 7, 3.5, fill=t["muted"], extra='fill-opacity="0.6"')
        d.rect(x + 82, 252, 32, 16, 8, fill=t["accent"], extra='fill-opacity="0.25"', stroke=t["accent"], sw=1)
    pw = 96 if len(pay_chip) <= 8 else 150
    d.rect(34, 290, pw, 22, 11, fill="none", stroke=t["border"], sw=1.2)
    d.text(34 + pw / 2, 305, pay_chip, "mono", 11, t["muted"], weight=700, anchor="middle", ls=1)
    d.text(566, 305, "CHECKOUT  ·  ADMIN  ·  WORKER", "mono", 11, t["muted"], weight=600, anchor="end", ls=1)
    return finish(d, key)


def ncs(theme):
    return store(theme, "card-ncs", "CLIENT  ·  COMMERCE", "NCS Santhanam store",
                 "A silk saree storefront with products, cart, checkout and admin.",
                 ["#b3202f", "#d9a441", "#1f6f6a", "#3b2a78", "#2f7d4f"], "EN", "RAZORPAY")


def methagu(theme):
    return store(theme, "card-methagu", "CLIENT  ·  COMMERCE", "Methagu Karuppatti store",
                 "A bilingual English and Tamil palm jaggery store with checkout and admin.",
                 ["#8a5a2b", "#d7a24a", "#5b3a1e", "#b87a36", "#6b8f3a"], "EN | TA", "RAZORPAY  +  COD")


def build_all():
    out = []
    for th in ("dark", "light"):
        for fn in (classiq, solace, leetx, cryptotrace, jarvis, visionnav):
            out.append(fn(th))
    return out
