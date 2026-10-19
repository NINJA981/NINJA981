from brand import Doc, orbit_mark, save, _n
from assets_cards import dash, circ

W, H = 1200, 440


def frame(theme, title, desc, eyebrow):
    d = Doc(W, H, theme, title, desc)
    t = d.t
    cid, pid = d.uid("c"), d.uid("p")
    d.d('<clipPath id="%s"><rect width="%d" height="%d" rx="24"/></clipPath>' % (cid, W, H))
    d.d('<pattern id="%s" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="%s" stroke-width="1"/></pattern>' % (pid, t["grid"]))
    d.add('<rect width="%d" height="%d" rx="24" fill="%s"/>' % (W, H, t["bg"]))
    d.add('<rect width="%d" height="%d" fill="url(#%s)" clip-path="url(#%s)"/>' % (W, H, pid, cid))
    d.text(50, 62, eyebrow, "mono", 18, t["accent"], weight=600, ls=4)
    orbit_mark(d, 1150, 56, 16)
    return d


def border(d):
    d.add('<rect x="0.5" y="0.5" width="%d" height="%d" rx="24" fill="none" stroke="%s"/>' % (W - 1, H - 1, d.t["border"]))


def arrow(d, x1, y1, x2, y2, w=2.4):
    t = d.t
    dash(d, x1, y1, x2 - 8 if x2 != x1 else x2, y2 - 8 if y2 != y1 and x2 == x1 else y2, w=w)
    if x2 != x1:
        d.add('<polygon points="%s,%s %s,%s %s,%s" fill="%s"/>' % (_n(x2), _n(y2), _n(x2 - 10), _n(y2 - 6), _n(x2 - 10), _n(y2 + 6), t["accent"]))
    else:
        d.add('<polygon points="%s,%s %s,%s %s,%s" fill="%s"/>' % (_n(x2), _n(y2), _n(x2 - 6), _n(y2 - 10), _n(x2 + 6), _n(y2 - 10), t["accent"]))


def node(d, x, y, w, h, title, sub, icon=None, title_size=22):
    t = d.t
    d.rect(x, y, w, h, 14, fill=t["surface"], stroke=t["border"], sw=1.5)
    cx = x + w / 2
    if icon:
        circ(d, cx, y + 46, 26, fill=t["surface2"], stroke=t["accent"], sw=1.8)
        icon(d, cx, y + 46)
    ty = y + (104 if icon else 50)
    d.text(cx, ty, title, "fr", title_size, t["text"], weight=600, anchor="middle")
    for i, line in enumerate(sub):
        d.text(cx, ty + 26 + i * 20, line, "mono", 13, t["muted"], weight=500, anchor="middle")


# --- icons (drawn around cx, cy) ----------------------------------------------
def ic_pi(d, cx, cy):
    t = d.t
    d.rect(cx - 13, cy - 9, 26, 18, 3, fill="none", stroke=t["accent2"], sw=1.8)
    for i in range(4):
        d.add('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1.6"/>' % (_n(cx - 8 + i * 5.3), cy - 9, _n(cx - 8 + i * 5.3), cy - 14, t["accent2"]))


def ic_api(d, cx, cy):
    d.text(cx, cy + 8, "{ }", "mono", 22, d.t["accent2"], weight=700, anchor="middle")


def ic_mic(d, cx, cy):
    t = d.t
    d.rect(cx - 6, cy - 14, 12, 20, 6, fill="none", stroke=t["accent2"], sw=1.8)
    d.add('<path d="M%s %s a11 11 0 0 0 22 0 M%s %s v8" fill="none" stroke="%s" stroke-width="1.8" stroke-linecap="round"/>' % (_n(cx - 11), cy + 2, _n(cx), cy + 13, t["accent2"]))


def ic_spark(d, cx, cy):
    d.add('<path d="M%s %s L%s %s L%s %s L%s %s L%s %s L%s %s L%s %s L%s %s Z" fill="%s"/>' % (
        _n(cx), cy - 15, _n(cx + 4), cy - 4, _n(cx + 15), cy, _n(cx + 4), cy + 4, _n(cx), cy + 15, _n(cx - 4), cy + 4, _n(cx - 15), cy, _n(cx - 4), cy - 4, d.t["accent2"]))


def ic_db(d, cx, cy):
    t = d.t
    d.add('<ellipse cx="%s" cy="%s" rx="12" ry="5" fill="none" stroke="%s" stroke-width="1.8"/>' % (_n(cx), cy - 9, t["accent2"]))
    d.add('<path d="M%s %s v18 a12 5 0 0 0 24 0 v-18 M%s %s a12 5 0 0 0 24 0" fill="none" stroke="%s" stroke-width="1.8"/>' % (_n(cx - 12), cy - 9, _n(cx - 12), cy, t["accent2"]))


def ic_phone(d, cx, cy):
    t = d.t
    d.rect(cx - 9, cy - 15, 18, 30, 4, fill="none", stroke=t["accent2"], sw=1.8)
    circ(d, cx, cy + 10, 1.8, fill=t["accent2"])


def ic_shield(d, cx, cy):
    d.add('<path d="M%s %s l13 5 v9 c0 9 -6 14 -13 17 c-7 -3 -13 -8 -13 -17 v-9 z" fill="none" stroke="%s" stroke-width="1.9" stroke-linejoin="round"/>' % (_n(cx), cy - 16, d.t["accent2"]))
    d.add('<path d="M%s %s l5 5 l9 -10" fill="none" stroke="%s" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>' % (_n(cx - 7), cy + 1, d.t["accent2"]))


def ic_brain(d, cx, cy):
    d.text(cx, cy + 8, "J", "fr", 26, d.t["accent2"], weight=800, anchor="middle")


def ic_plug(d, cx, cy):
    t = d.t
    d.add('<path d="M%s %s v-9 M%s %s v-9 M%s %s h18 v6 a9 9 0 0 1 -18 0 z M%s %s v8" fill="none" stroke="%s" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/>' % (
        _n(cx - 5), cy - 3, _n(cx + 5), cy - 3, _n(cx - 9), cy - 3, _n(cx), cy + 11, t["accent2"]))


def classiq(theme):
    d = frame(theme, "ClassIQ architecture",
              "Pipeline: Raspberry Pi 5 recorder, Express 5 API with Socket.IO, speech-to-text for Indian languages, LLM bilingual quizzes, PostgreSQL with BullMQ jobs, Next.js PWA for admin, teacher and student.",
              "CLASSIQ  ·  FROM LECTURE TO QUIZ")
    t = d.t
    items = [
        ("Pi 5 recorder", ["lecture audio", "in the classroom"], ic_pi),
        ("API", ["Express 5", "Socket.IO"], ic_api),
        ("Speech to text", ["Indian", "languages"], ic_mic),
        ("LLM", ["bilingual", "quizzes"], ic_spark),
        ("Postgres", ["BullMQ", "job queue"], ic_db),
        ("Next.js PWA", ["admin, teacher", "and student"], ic_phone),
    ]
    x0, nw, gap, y, nh = 50, 150, 40, 112, 178
    for i, (title, sub, ic) in enumerate(items):
        x = x0 + i * (nw + gap)
        node(d, x, y, nw, nh, title, sub, ic, title_size=21)
        if i < len(items) - 1:
            arrow(d, x + nw + 4, y + 90, x + nw + gap - 2, y + 90)
    d.rect(50, 326, 1100, 70, 16, fill=t["surface"], stroke=t["border"], sw=1.5)
    d.text(600, 368, "TEAM OF 4   ·   500+ TESTS   ·   CI/CD   ·   DOCKER + COOLIFY", "mono", 18, t["muted"], weight=600, anchor="middle", ls=2)
    border(d)
    return save(d, "arch-classiq")


def jarvis(theme):
    d = frame(theme, "JARVIS architecture",
              "A wake word and speech recognition feed a supervisor that delegates to eight specialist agents. Every action passes a permission gate before 11 MCP servers act on the Windows PC. A model router connects Claude, OpenAI, Gemini and Ollama.",
              "JARVIS  ·  ONE VOICE, MANY AGENTS")
    t = d.t
    # model router bar
    d.rect(250, 86, 700, 46, 14, fill=t["surface"], stroke=t["accent"], sw=1.6)
    d.text(600, 115, "MODEL ROUTER  ·  CLAUDE  OPENAI  GEMINI  OLLAMA  ·  FAILOVER", "mono", 15, t["text"], weight=600, anchor="middle", ls=1.5)
    dash(d, 335, 132, 335, 176, w=2)
    # columns
    node(d, 40, 180, 170, 168, "Wake word", ["Hey Jarvis", "streaming STT"], ic_mic, title_size=21)
    arrow(d, 214, 255, 248, 255)
    node(d, 252, 180, 170, 168, "Supervisor", ["plans and", "delegates"], ic_brain, title_size=21)
    arrow(d, 426, 255, 468, 255)
    # agents block
    d.rect(472, 150, 262, 210, 16, fill=t["surface"], stroke=t["border"], sw=1.5)
    d.text(603, 178, "EIGHT SPECIALISTS", "mono", 13, t["accent"], weight=600, anchor="middle", ls=2)
    names = ["Operator", "Navigator", "Researcher", "Engineer", "Courier", "Pilot", "Librarian", "Critic"]
    for i, n in enumerate(names):
        cx = 488 + (i % 2) * 120
        cy = 192 + (i // 2) * 40
        d.rect(cx, cy, 108, 32, 16, fill=t["surface2"], stroke=t["border"], sw=1.2)
        d.text(cx + 54, cy + 21, n, "sg", 16, t["text"], weight=500, anchor="middle")
    arrow(d, 738, 255, 782, 255)
    node(d, 786, 180, 150, 168, "Permission gate", ["every action", "checked"], ic_shield, title_size=19)
    arrow(d, 940, 255, 982, 255)
    node(d, 986, 180, 174, 168, "11 MCP servers", ["system, files,", "browser, apps"], ic_plug, title_size=20)
    dash(d, 1073, 352, 1073, 366, w=2)
    d.rect(250, 368, 910, 44, 14, fill=t["surface"], stroke=t["border"], sw=1.5)
    d.text(705, 396, "YOUR WINDOWS PC  ·  SIGNED REQUESTS  ·  DELETES GO TO THE RECYCLE BIN", "mono", 14, t["muted"], weight=600, anchor="middle", ls=1.5)
    d.text(40, 396, "built with AI agents", "mono", 14, t["dim"], weight=500)
    d.text(40, 416, "1,100+ tests", "mono", 14, t["accent"], weight=600)
    border(d)
    return save(d, "arch-jarvis")


def payments(theme):
    d = frame(theme, "How a payment stays safe",
              "A buyer checks out, stock is reserved with a conditional update, Razorpay takes the payment, a signed and idempotent webhook confirms the order. If the payment never arrives, a BullMQ job releases the stock.",
              "CLIENT WORK  ·  A PAYMENT THAT CANNOT BE CHARGED TWICE")
    t = d.t
    items = [
        ("Checkout", ["cart to", "order"], ic_phone),
        ("Reserve stock", ["conditional UPDATE", "+ CHECK constraint"], ic_db),
        ("Razorpay", ["pays the", "order"], ic_plug),
        ("Webhook", ["signature checked,", "idempotent"], ic_shield),
        ("Confirmed", ["retries cannot", "confirm it twice"], ic_api),
    ]
    x0, nw, gap, y, nh = 50, 170, 62.5, 98, 178
    for i, (title, sub, ic) in enumerate(items):
        x = x0 + i * (nw + gap)
        node(d, x, y, nw, nh, title, sub, ic, title_size=20)
        if i < len(items) - 1:
            arrow(d, x + nw + 4, y + 90, x + nw + gap - 2, y + 90)
    d.rect(50, 306, 1100, 92, 16, fill=t["surface"], stroke=t["border"], sw=1.5)
    d.text(80, 340, "IF THE PAYMENT NEVER ARRIVES", "mono", 15, t["accent"], weight=600, ls=2)
    d.text(80, 374, "BullMQ worker  ·  payment-hold expiry job  ·  stock goes back on the shelf", "sg", 20, t["text"], weight=500)
    d.text(1120, 340, "TWO BUYERS, ONE LAST SAREE", "mono", 13, t["muted"], weight=600, anchor="end", ls=2)
    d.text(1120, 374, "only one wins", "fr", 22, t["text"], weight=600, anchor="end")
    border(d)
    return save(d, "arch-payments")


def build_all():
    out = []
    for th in ("dark", "light"):
        for fn in (classiq, jarvis, payments):
            out.append(fn(th))
    return out
