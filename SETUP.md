# NINJA981 profile repository

This repository powers the GitHub profile README for **Sai Charan (`NINJA981`)**. Portfolio: https://charan.loopfound.in

## How it is built
- `README.md` is the source of truth. Two automated blocks inside it are rewritten by workflows: `<!-- ACTIVITY:START/END -->`, `<!-- LANG:START/END -->` (live panel) and `<!-- C4:START/END -->` (Connect-4 board). Do not edit between those markers by hand.
- `tools/design/` generates every graphic in `assets/brand/` (light and dark SVGs, fonts embedded as base64, no external resources). Rebuild with `python tools/design/build_all.py` (needs Python 3 with `fonttools` and `brotli`). Brand tokens (palette, motif, fonts) live in `tools/design/brand.py`; page copy for the assets lives in the `assets_*.py` modules.
- `tools/live/build-live.mjs` builds `assets/live/languages-*.svg` and the "Recently shipped" list from the GitHub API (public repositories only). Run by `.github/workflows/activity.yml` every 12 hours: `GITHUB_TOKEN=$(gh auth token) node tools/live/build-live.mjs` runs it locally. To include private repositories, add a fine-grained personal access token as a repository secret and use it instead of the default token.
- `game/` is the Connect-4 game (engine, bot, tests). A visitor opens an issue titled `c4|move|N` (`N` is 1 to 7) or `c4|new`; `.github/workflows/connect4.yml` plays the move, redraws the board, commits it, replies and closes the issue. Run the tests with `node game/test.mjs`. To switch the game off, disable the "Connect 4" workflow in the Actions tab.
- `assets/` also contains older hand-made SVGs that are no longer referenced.

## Design system
Black-hole editorial look to match the portfolio: ink `#12100c` / cream `#f4efe3`, accent orange `#ff7a18`. Fraunces (display), JetBrains Mono (labels), Space Grotesk (body), all OFL licensed.

## Domain changes
The portfolio lives in the repository `NINJA981/saicharan.dev` (Cloudflare Pages). If the domain changes again, update `index.html`, `public/sitemap.xml`, `public/robots.txt` and `functions/_middleware.js` there, then every link in this README.
