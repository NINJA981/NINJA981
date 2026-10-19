from brand import Doc, blackhole, orbit_mark, stars, save, text_width, _n


def _frame(d, w, h, r=24):
    t = d.t
    cid = d.uid("c")
    d.d('<clipPath id="%s"><rect width="%d" height="%d" rx="%d"/></clipPath>' % (cid, w, h, r))
    d.add('<rect width="%d" height="%d" rx="%d" fill="%s"/>' % (w, h, r, t["bg"]))
    return cid


def _grid(d, w, h, cid, step=40):
    t = d.t
    pid = d.uid("p")
    d.d(
        '<pattern id="%s" width="%d" height="%d" patternUnits="userSpaceOnUse"><path d="M%d 0H0V%d" fill="none" stroke="%s" stroke-width="1"/></pattern>'
        % (pid, step, step, step, step, t["grid"])
    )
    d.add('<rect width="%d" height="%d" fill="url(#%s)" clip-path="url(#%s)" opacity="0.9"/>' % (w, h, pid, cid))


def hero(theme):
    w, h = 1200, 380
    d = Doc(w, h, theme, "Sai Charan, software and AI engineer",
            "Name and tagline beside an animated black hole with an orbiting dot. Software, AI systems and edge hardware.")
    t = d.t
    cid = _frame(d, w, h)
    _grid(d, w, h, cid)
    g = d.uid("sh")
    d.d('<linearGradient id="%s" x1="0" x2="1"><stop offset="0" stop-color="%s" stop-opacity="0.9"/><stop offset="0.55" stop-color="%s" stop-opacity="0"/></linearGradient>' % (g, t["bg"], t["bg"]))
    d.add('<g clip-path="url(#%s)">' % cid)
    stars(d, 480, 1190, 14, 366, 80, seed=11, twinkle=12)
    blackhole(d, 962, 190, 0.92)
    d.add('<rect width="760" height="%d" fill="url(#%s)"/>' % (h, g))
    d.add("</g>")
    d.text(64, 96, "SOFTWARE · AI SYSTEMS · EDGE HARDWARE", "mono", 19, t["accent"], weight=500, ls=4.5)
    d.text(60, 208, "Sai Charan", "fr", 112, t["text"], weight=800, ls=-2)
    d.text(64, 266, "I build AI products that real people use.", "fri", 34, t["text"], weight=400, opacity=0.92)
    d.rect(64, 292, 96, 3, 1.5, fill=t["accent"])
    d.text(64, 338, "CHENNAI  ·  CSE '29  ·  MACHINE LEARNING INTERN @ BENX", "mono", 17, t["muted"], weight=500, ls=2)
    d.add('<rect x="0.5" y="0.5" width="%d" height="%d" rx="24" fill="none" stroke="%s"/>' % (w - 1, h - 1, t["border"]))
    return save(d, "hero")


def numbers(theme):
    w, h = 1200, 188
    d = Doc(w, h, theme, "By the numbers",
            "5 products built, 2,500+ automated tests across projects, 5 podium finishes, 2 client stores.")
    t = d.t
    cid = _frame(d, w, h, 20)
    _grid(d, w, h, cid)
    items = [
        ("5", "PRODUCTS BUILT", "ClassIQ to JARVIS"),
        ("2,500+", "AUTOMATED TESTS", "across my projects"),
        ("5", "PODIUM FINISHES", "hackathons and contests"),
        ("2", "CLIENT STORES", "real businesses, real payments"),
    ]
    colw = w / 4
    for i, (num, lab, sub) in enumerate(items):
        cx = colw * i + colw / 2
        d.text(cx, 96, num, "fr", 70, t["text"], weight=700, anchor="middle", ls=-1)
        d.text(cx, 130, lab, "mono", 16, t["accent"], weight=600, anchor="middle", ls=3)
        d.text(cx, 158, sub, "sg", 17, t["muted"], weight=400, anchor="middle")
        if i:
            d.add('<line x1="%s" y1="36" x2="%s" y2="152" stroke="%s" stroke-width="1"/>' % (_n(colw * i), _n(colw * i), t["border"]))
    orbit_mark(d, 40, 34, 12)
    d.add('<rect x="0.5" y="0.5" width="%d" height="%d" rx="20" fill="none" stroke="%s"/>' % (w - 1, h - 1, t["border"]))
    return save(d, "numbers")


def divider(theme):
    w, h = 1200, 44
    d = Doc(w, h, theme, "Divider", "A thin line with an orbiting dot at its centre.")
    t = d.t
    g = d.uid("g")
    d.d('<linearGradient id="%s" x1="0" x2="1"><stop offset="0" stop-color="%s" stop-opacity="0"/><stop offset="0.5" stop-color="%s"/><stop offset="1" stop-color="%s" stop-opacity="0"/></linearGradient>' % (g, t["accent"], t["accent"], t["accent"]))
    d.add('<rect x="40" y="21.5" width="1120" height="1.4" fill="url(#%s)" opacity="0.55"/>' % g)
    orbit_mark(d, 600, 22, 15)
    return save(d, "divider")


def footer(theme):
    w, h = 1200, 214
    d = Doc(w, h, theme, "Sai Charan", "Concentric orbit rings rising from the bottom edge with a name and location.")
    t = d.t
    cid = d.uid("c")
    d.d('<clipPath id="%s"><rect width="%d" height="%d" rx="24"/></clipPath>' % (cid, w, h))
    d.add('<g clip-path="url(#%s)">' % cid)
    d.add('<rect width="%d" height="%d" fill="%s"/>' % (w, h, t["bg"]))
    stars(d, 0, 1200, 8, 120, 46, seed=5, twinkle=6)
    for i, (rx, ry, op) in enumerate([(560, 120, 0.55), (430, 88, 0.4), (300, 58, 0.28)]):
        d.add('<ellipse cx="600" cy="262" rx="%d" ry="%d" fill="none" stroke="%s" stroke-width="%s" opacity="%s"/>' % (rx, ry, t["accent"], 2 if i == 0 else 1.5, op))
    d.add('<circle r="5" fill="#ffe2ae"><animateMotion dur="20s" repeatCount="indefinite" path="M 40 262 A 560 120 0 1 1 1160 262 A 560 120 0 1 1 40 262"/></circle>')
    d.add("</g>")
    d.text(600, 84, "Sai Charan", "fr", 40, t["text"], weight=700, anchor="middle", ls=-0.5)
    d.text(600, 118, "CHENNAI  ·  OPEN TO ON-SITE INTERNSHIPS", "mono", 15, t["muted"], weight=500, anchor="middle", ls=3)
    d.add('<rect x="0.5" y="0.5" width="%d" height="%d" rx="24" fill="none" stroke="%s"/>' % (w - 1, h - 1, t["border"]))
    return save(d, "footer")


def contact(theme):
    w, h = 1200, 240
    d = Doc(w, h, theme, "Let's talk",
            "Contact card: open to on-site internships in Chennai for software, backend and AI work. Email saicharan312008@gmail.com.")
    t = d.t
    cid = _frame(d, w, h)
    _grid(d, w, h, cid)
    d.add('<g clip-path="url(#%s)">' % cid)
    stars(d, 700, 1190, 10, 230, 40, seed=3, twinkle=6)
    blackhole(d, 1010, 120, 0.56)
    d.add("</g>")
    d.text(64, 70, "LET'S TALK", "mono", 17, t["accent"], weight=600, ls=4.5)
    d.text(62, 134, "Building something that ships?", "fr", 52, t["text"], weight=700, ls=-1)
    d.text(64, 178, "saicharan312008@gmail.com", "mono", 24, t["accent2"], weight=500)
    d.text(64, 210, "On-site internships in Chennai  ·  software, backend, AI", "sg", 18, t["muted"])
    d.add('<rect x="0.5" y="0.5" width="%d" height="%d" rx="24" fill="none" stroke="%s"/>' % (w - 1, h - 1, t["border"]))
    return save(d, "contact")


def build_all():
    out = []
    for th in ("dark", "light"):
        for fn in (hero, numbers, divider, footer, contact):
            out.append(fn(th))
    return out
