from brand import Doc, orbit_mark, save, text_width, _n
from assets_cards import circ

W = 1200

STACK = [
    ("LANGUAGES", ["TypeScript", "Python", "Java", "Kotlin", "SQL", "C"]),
    ("WEB", ["React", "Next.js", "Node.js", "Express", "Fastify", "Tailwind"]),
    ("DATA", ["PostgreSQL", "pgvector", "Redis", "BullMQ", "Supabase", "SQLite", "Firebase"]),
    ("AI", ["OpenAI", "Gemini", "Claude", "Ollama", "RAG", "Speech-to-text", "MCP", "n8n"]),
    ("INFRA", ["Docker", "GitHub Actions", "Cloudflare", "Vercel", "Raspberry Pi", "Linux"]),
]


def stack(theme):
    # layout first to know the height
    label_w, x_start, x_end, chip_h, gap = 190, 230, 1160, 40, 12
    rows = []
    for label, items in STACK:
        lines, cur, x = [], [], x_start
        for it in items:
            w = text_width("sg", it, 18, bold_factor=1.04) + 34
            if x + w > x_end and cur:
                lines.append(cur)
                cur, x = [], x_start
            cur.append((it, w))
            x += w + gap
        lines.append(cur)
        rows.append((label, lines))
    total_lines = sum(len(l) for _, l in rows)
    H = 110 + total_lines * (chip_h + gap) + len(rows) * 22 + 20
    d = Doc(W, H, theme, "Tech stack",
            "Languages: " + ", ".join(STACK[0][1]) + ". Web: " + ", ".join(STACK[1][1]) + ". Data: " + ", ".join(STACK[2][1])
            + ". AI: " + ", ".join(STACK[3][1]) + ". Infra: " + ", ".join(STACK[4][1]) + ".")
    t = d.t
    cid, pid = d.uid("c"), d.uid("p")
    d.d('<clipPath id="%s"><rect width="%d" height="%d" rx="24"/></clipPath>' % (cid, W, H))
    d.d('<pattern id="%s" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="%s" stroke-width="1"/></pattern>' % (pid, t["grid"]))
    d.add('<rect width="%d" height="%d" rx="24" fill="%s"/>' % (W, H, t["bg"]))
    d.add('<rect width="%d" height="%d" fill="url(#%s)" clip-path="url(#%s)"/>' % (W, H, pid, cid))
    d.text(50, 62, "STACK", "mono", 18, t["accent"], weight=600, ls=4)
    orbit_mark(d, 1150, 56, 16)
    y = 100
    for label, lines in rows:
        d.text(50, y + 26, label, "mono", 15, t["muted"], weight=600, ls=3)
        for line in lines:
            x = x_start
            for it, w in line:
                d.rect(x, y, w, chip_h, 20, fill=t["surface"], stroke=t["border"], sw=1.4)
                d.text(x + w / 2, y + 26, it, "sg", 18, t["text"], weight=500, anchor="middle")
                x += w + gap
            y += chip_h + gap
        y += 22
        d.add('<line x1="50" y1="%s" x2="1150" y2="%s" stroke="%s" stroke-width="1" opacity="0.6"/>' % (_n(y - 17), _n(y - 17), t["border"]))
    d.add('<rect x="0.5" y="0.5" width="%d" height="%d" rx="24" fill="none" stroke="%s"/>' % (W - 1, H - 1, t["border"]))
    return save(d, "stack")


EVENTS = [
    ("OCT 2025", "Code in the Dark", ["1st place"], "gold"),
    ("MAR 2026", "VIT HackCrate", ["5th place"], "plain"),
    ("APR 2026", "Luminary Award", ["sole first-year", "all-rounder"], "accent"),
    ("JUL 2026", "Hack The Planet", ["4th place"], "plain"),
    ("JUL 2026", "Rush Hour", ["special mention", "+ internship offer"], "accent"),
    ("AUG 2026", "Aurora", ["3rd place"], "bronze"),
    ("SEP 2026", "ProtoTech", ["2nd place"], "silver"),
    ("SEP 2026", "PromptCraft", ["2nd place"], "silver"),
]
MEDALS = {
    "dark": {"gold": "#e0b341", "silver": "#b9bec7", "bronze": "#c2773c"},
    "light": {"gold": "#a67c00", "silver": "#5f6773", "bronze": "#a35a1f"},
}


def timeline(theme):
    H = 470
    d = Doc(W, H, theme, "Wins timeline",
            "Results from October 2025 to September 2026: " + "; ".join("%s %s %s" % (e[0], e[1], " ".join(e[2])) for e in EVENTS) + ". Plus 1st at Hack the Vibe.")
    t = d.t
    cid, pid = d.uid("c"), d.uid("p")
    d.d('<clipPath id="%s"><rect width="%d" height="%d" rx="24"/></clipPath>' % (cid, W, H))
    d.d('<pattern id="%s" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="%s" stroke-width="1"/></pattern>' % (pid, t["grid"]))
    d.add('<rect width="%d" height="%d" rx="24" fill="%s"/>' % (W, H, t["bg"]))
    d.add('<rect width="%d" height="%d" fill="url(#%s)" clip-path="url(#%s)"/>' % (W, H, pid, cid))
    d.text(50, 62, "WINS  ·  OCT 2025 TO SEP 2026", "mono", 18, t["accent"], weight=600, ls=4)
    orbit_mark(d, 1150, 56, 16)
    ay = 250
    lg = d.uid("l")
    d.d('<linearGradient id="%s" x1="0" x2="1"><stop offset="0" stop-color="%s" stop-opacity="0.2"/><stop offset="0.5" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (lg, t["accent"], t["accent"], t["accent2"]))
    d.add('<rect x="50" y="%d" width="1100" height="3" rx="1.5" fill="url(#%s)"/>' % (ay - 1, lg))
    d.add('<polygon points="1160,%d 1144,%d 1144,%d" fill="%s"/>' % (ay + 0.5, ay - 8, ay + 9, t["accent2"]))
    n = len(EVENTS)
    step = 940 / (n - 1)
    for i, (date, title, sub, kind) in enumerate(EVENTS):
        x = 130 + i * step
        up = i % 2 == 0
        col = MEDALS[theme].get(kind, t["accent"] if kind == "accent" else t["muted"])
        stem = 54
        y1, y2 = (ay - stem, ay) if up else (ay, ay + stem)
        d.add('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1.5" opacity="0.8"/>' % (_n(x), y1, _n(x), y2, col))
        circ(d, x, ay, 11, fill=t["bg"], stroke=col, sw=3)
        circ(d, x, ay, 4.5, fill=col)
        if up:
            base = ay - stem - 14
            d.text(x, base, sub[-1] if len(sub) == 1 else sub[-1], "mono", 15, t["muted"], weight=500, anchor="middle")
            yy = base
            if len(sub) == 2:
                d.text(x, base - 20, sub[0], "mono", 15, t["muted"], weight=500, anchor="middle")
                yy = base - 20
            d.text(x, yy - 26, title, "fr", 24, t["text"], weight=600, anchor="middle")
            d.text(x, yy - 56, date, "mono", 14, col, weight=700, anchor="middle", ls=2)
        else:
            base = ay + stem + 22
            d.text(x, base, date, "mono", 14, col, weight=700, anchor="middle", ls=2)
            d.text(x, base + 30, title, "fr", 24, t["text"], weight=600, anchor="middle")
            for j, s in enumerate(sub):
                d.text(x, base + 56 + j * 20, s, "mono", 15, t["muted"], weight=500, anchor="middle")
    d.text(50, H - 26, "also  ·  1st place at Hack the Vibe", "mono", 15, t["dim"], weight=500)
    d.add('<rect x="0.5" y="0.5" width="%d" height="%d" rx="24" fill="none" stroke="%s"/>' % (W - 1, H - 1, t["border"]))
    return save(d, "timeline")


def build_all():
    out = []
    for th in ("dark", "light"):
        for fn in (stack, timeline):
            out.append(fn(th))
    return out
