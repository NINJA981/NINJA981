"""One-off generator for README.md (the README itself is the source afterwards; the
live-panel and Connect-4 workflows only rewrite the marked blocks inside it)."""
import os

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SITE = "https://charan.loopfound.in/"


def pic(name, alt, width="100%", folder="brand"):
    return (
        '<picture>\n'
        '  <source media="(prefers-color-scheme: dark)" srcset="./assets/%(f)s/%(n)s-dark.svg">\n'
        '  <source media="(prefers-color-scheme: light)" srcset="./assets/%(f)s/%(n)s-light.svg">\n'
        '  <img alt="%(a)s" src="./assets/%(f)s/%(n)s-light.svg" width="%(w)s">\n'
        '</picture>' % {"f": folder, "n": name, "a": alt, "w": width}
    )


def divider():
    return '<div align="center">\n' + pic("divider", "", "100%") + "\n</div>\n"


def card(name, alt, title, body, proof, tags, link):
    tag_html = " ".join("<code>%s</code>" % t for t in tags)
    return (
        '<td width="50%%" valign="top">\n'
        '<a href="%(link)s">\n%(pic)s\n</a>\n'
        "<p><b>%(title)s</b><br>%(body)s</p>\n"
        "<p><sub>%(proof)s</sub></p>\n"
        "<p>%(tags)s</p>\n"
        "</td>"
        % {"link": link, "pic": pic(name, alt), "title": title, "body": body, "proof": proof, "tags": tag_html}
    )


def row(*cells):
    return "<tr>\n%s\n</tr>" % "\n".join(cells)


work = [
    card("card-classiq", "ClassIQ: a Raspberry Pi records a lecture and a quiz appears on a student's phone",
         'ClassIQ <sup>BenX Solutions</sup>',
         "AI classroom platform. A Raspberry Pi records the lecture, speech-to-text for Indian languages and an LLM turn it into "
         "bilingual quizzes that run on students' phones. Multi-school admin, timed exams, AI grading help.",
         "<b>Team of 4 · 500+ tests · CI/CD · Docker + Coolify</b> · private repo, walkthrough on request",
         ["Express 5", "Socket.IO", "PostgreSQL", "BullMQ", "Next.js", "Raspberry Pi"], SITE),
    card("card-solace", "Solace: a journal page embedded into a field of points, with the closest memories lit up",
         'Solace <sup><a href="https://solace-diaries.vercel.app">live</a> · <a href="https://github.com/NINJA981/Solace-Diaries">code</a></sup>',
         "A private journal you can question. Semantic search with pgvector, and answers that cite the entries they came from. "
         "Entries are analysed in the background by a durable job queue.",
         "<b>About 330 tests · row-level security · hybrid vector + keyword search</b>",
         ["React 19", "Express 5", "Postgres + pgvector", "Gemini"], "https://github.com/NINJA981/Solace-Diaries"),
]
work2 = [
    card("card-leetx", "LeetX Squads: a streak grid with streak, freeze, duel and squad features",
         'LeetX Squads <sup><a href="https://github.com/NINJA981/LeetX">code</a></sup>',
         "Browser extension that turns LeetCode into a habit you keep with friends: streaks and freezes, spaced review, squads, "
         "1v1 duels and automatic GitHub backup of every accepted solution.",
         "<b>About 80 tests · Firebase rules tested on the emulator · CI-built Chrome and Firefox releases</b>",
         ["JavaScript (MV3)", "Firebase", "GitHub Actions"], "https://github.com/NINJA981/LeetX"),
    card("card-cryptotrace", "CryptoTrace: unknown wallets traced through hops to the exchange that likely holds them",
         'CryptoTrace <sup><a href="https://cryptotrace-sand.vercel.app">live</a> · <a href="https://github.com/NINJA981/cryptotrace">code</a></sup>',
         "Traces unknown crypto wallets through bounded transaction hops to the exchange that most likely holds them, with an "
         "explainable five-factor score and a requisition dossier.",
         "<b>Built solo for Smart India Hackathon · tested · documented limits</b>",
         ["FastAPI", "Next.js", "Etherscan / TronGrid"], "https://github.com/NINJA981/cryptotrace"),
]
work3 = [
    card("card-jarvis", "JARVIS: a supervisor in the middle with eight specialist agents around it",
         "JARVIS <sup>built with AI coding agents</sup>",
         "Voice-first AI layer for Windows. One router across Claude, OpenAI, Gemini and Ollama with failover and budgets, a "
         "supervisor with eight specialist agents, a permission gate on every action and 11 MCP tool servers.",
         "<b>1,100+ automated tests · Android companion</b> · private repo, demo on request",
         ["TypeScript", "Electron", "MCP", "Ollama"], SITE),
    card("card-visionnav", "VisionNav: a phone camera detects a pole and a car ahead of a walking path and speaks a warning",
         "VisionNav",
         "On-device Android navigation for blind and low-vision pedestrians: walking routes, live camera hazard detection and "
         "crossing awareness through voice and haptics. It never claims a road is safe.",
         "<b>500+ unit tests on the core</b> · field testing in progress",
         ["Kotlin", "CameraX", "YOLOv8n", "LiteRT"], SITE),
]
client = [
    card("card-methagu", "A bilingual English and Tamil palm jaggery store with checkout and admin",
         "Methagu Karuppatti <sup>client work</sup>",
         "Bilingual (English and Tamil) palm jaggery store. Razorpay and cash on delivery, coupons, refunds, GST invoices, "
         "admin analytics.",
         "<b>Playwright E2E with accessibility checks · CSP, CSRF, rate limiting</b>",
         ["Next.js", "Drizzle", "PostgreSQL", "Razorpay"], SITE),
]

readme = """<div align="center">

%(hero)s

<b>Open to on-site internships · Chennai</b><br>
B.E. CSE '29 at Sathyabama (CGPA 8.76) · Machine Learning Intern at BenX Solutions · Back End Developer at <a href="https://www.loopfound.in/">LoopFound</a>

<a href="#selected-work">Selected work</a> · <a href="#how-it-works">How it works</a> · <a href="#client-work">Client work</a> · <a href="#stack">Stack</a> · <a href="#wins">Wins</a> · <a href="#live">Live</a> · <a href="#contact">Contact</a>

%(numbers)s

</div>

## About

I build software that gets used: a classroom that writes its own quizzes from the lecture, a journal that remembers, a browser extension people keep their streaks in. TypeScript and Postgres by default, Python or Kotlin when the problem needs them. I use AI coding agents heavily. Architecture, tests and review are mine.

Currently looking for an **on-site software, backend or AI internship in Chennai**. Portfolio at [charan.loopfound.in](%(site)s).

%(div)s
## Selected work

<table>
%(w1)s
%(w2)s
%(w3)s
</table>

%(div)s
## How it works

<details open>
<summary><b>ClassIQ: from a lecture to a quiz</b></summary>
<br>
%(arch1)s
</details>

<details>
<summary><b>JARVIS: one voice command, many agents</b></summary>
<br>
%(arch2)s
</details>

%(div)s
## Client work

A production store built for a real business, with real payments:

<table>
%(c1)s
</table>

**Also built:** [VADA](https://github.com/NINJA981/vada) (voice RAG with hybrid retrieval, benchmarked) · SafeCanteen (canteen pre-ordering, money and capacity rules in the database) · [ResponSync](https://github.com/NINJA981/RS) (flood-response digital twin, I built the backend) · OpenShield (dependency and licence risk scanner with SBOM export).

%(div)s
## Stack

<div align="center">
%(stack)s
</div>

%(div)s
## Wins

<div align="center">
%(timeline)s
</div>

<details>
<summary>The list, in text</summary>

- 1st: Hack the Vibe · Code in the Dark
- 2nd: ProtoTech · PromptCraft (TechnoSummit)
- 3rd: Aurora · 4th: Hack The Planet · 5th: VIT HackCrate
- Special Mention at Rush Hour, with an internship offer
- Luminary Award: sole all-rounder of the first-year batch
- Instructor (n8n workshop), speaker (WebXplore), organiser (CodeStorm, Crackathon), started the Forge developer community

</details>

%(div)s
## Live

<div align="center">

<!-- LANG:START -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/live/languages-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/live/languages-light.svg">
  <img alt="Language share across my public repositories" src="./assets/live/languages-light.svg" width="100%%">
</picture>
<!-- LANG:END -->

</div>

**Recently shipped** (public repositories, refreshed automatically)

<!-- ACTIVITY:START -->
_Updating soon._
<!-- ACTIVITY:END -->

<details>
<summary><b>Play Connect-4 against my bot</b></summary>
<br>

<!-- C4:START -->
<!-- C4:END -->

</details>

%(div)s
## Contact

<div align="center">
%(contact)s

<a href="mailto:saicharan312008@gmail.com">Email</a> · <a href="https://www.linkedin.com/in/sai-charan111/">LinkedIn</a> · <a href="%(site)s">Portfolio</a> · <a href="https://leetcode.com/NINJA981/">LeetCode</a> · <a href="%(site)sSai_Charan_CV.pdf">Resume (PDF)</a>

%(footer)s
</div>
""" % {
    "hero": pic("hero", "Sai Charan, software and AI engineer in Chennai. Software, AI systems, edge hardware."),
    "numbers": pic("numbers", "5 products built, 2,500+ automated tests across projects, 5 podium finishes, 1 client store."),
    "site": SITE,
    "div": divider(),
    "w1": row(*work),
    "w2": row(*work2),
    "w3": row(*work3),
    "c1": row(*client),
    "arch1": pic("arch-classiq", "ClassIQ pipeline: Raspberry Pi 5 recorder, Express 5 API with Socket.IO, speech-to-text for Indian languages, LLM bilingual quizzes, PostgreSQL with BullMQ jobs, Next.js PWA."),
    "arch2": pic("arch-jarvis", "JARVIS: wake word and speech recognition feed a supervisor that delegates to eight specialist agents, every action passes a permission gate, then 11 MCP servers act on the Windows PC. A model router connects Claude, OpenAI, Gemini and Ollama."),
    "stack": pic("stack", "Languages: TypeScript, Python, Java, Kotlin, SQL, C. Web: React, Next.js, Node.js, Express, Fastify, Tailwind. Data: PostgreSQL, pgvector, Redis, BullMQ, Supabase, SQLite, Firebase. AI: OpenAI, Gemini, Claude, Ollama, RAG, speech-to-text, MCP, n8n. Infra: Docker, GitHub Actions, Cloudflare, Vercel, Raspberry Pi, Linux."),
    "timeline": pic("timeline", "Wins timeline from October 2025 to September 2026: Code in the Dark 1st, VIT HackCrate 5th, Luminary Award, Hack The Planet 4th, Rush Hour special mention, Aurora 3rd, ProtoTech 2nd, PromptCraft 2nd."),
    "contact": pic("contact", "Let's talk. Open to on-site internships in Chennai for software, backend and AI work. Email saicharan312008@gmail.com."),
    "footer": pic("footer", ""),
}

with open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8", newline="\n") as f:
    f.write(readme)
print("README.md written,", len(readme), "chars")
