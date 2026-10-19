// Builds the "live panel" for the profile README:
//   - assets/live/languages-{dark,light}.svg  (language share across public repos)
//   - the "Recently shipped" list between <!-- ACTIVITY:START --> / <!-- ACTIVITY:END -->
//   - the <picture> block between <!-- LANG:START --> / <!-- LANG:END -->
// Node 20+, built-ins only. Usage: GITHUB_TOKEN=... node tools/live/build-live.mjs
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const USER = 'NINJA981';
const SKIP_REPOS = new Set([USER.toLowerCase(), 'test', 'test-repo', 'leetcode-submissions']);
const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, '..', '..');
const README = join(ROOT, 'README.md');
const OUT_DIR = join(ROOT, 'assets', 'live');
const API = 'https://api.github.com';
const TOKEN = process.env.GITHUB_TOKEN || process.env.GH_TOKEN || '';

class RateLimitError extends Error {}

// ---------------------------------------------------------------- GitHub API
async function gh(path) {
  const url = path.startsWith('http') ? path : API + path;
  const headers = {
    Accept: 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28',
    'User-Agent': 'ninja981-live-panel',
  };
  if (TOKEN) headers.Authorization = `Bearer ${TOKEN}`;
  const res = await fetch(url, { headers });
  if (res.status === 429 || (res.status === 403 && res.headers.get('x-ratelimit-remaining') === '0')) {
    const reset = Number(res.headers.get('x-ratelimit-reset'));
    const when = reset ? new Date(reset * 1000).toISOString() : 'later';
    throw new RateLimitError(`GitHub API rate limit exceeded (resets ${when}). Set GITHUB_TOKEN to raise the limit.`);
  }
  if (!res.ok) throw new Error(`GET ${url} -> HTTP ${res.status}`);
  return res;
}

async function ghPaged(path) {
  const all = [];
  let url = path;
  for (let i = 0; i < 10 && url; i++) {
    const res = await gh(url);
    all.push(...(await res.json()));
    const m = /<([^>]+)>;\s*rel="next"/.exec(res.headers.get('link') || '');
    url = m ? m[1] : null;
  }
  return all;
}

// ---------------------------------------------------------------- languages
const PALETTE = {
  dark: {
    bg: '#12100c', border: '#2c2820', text: '#ece6d6', muted: '#9a9280', grid: '#241f18',
    ramp: ['#ff7a18', '#ffb347', '#d9a441', '#5bc0be', '#7a8fa6', '#b07d62', '#8f8672'],
    other: '#6d6757',
  },
  light: {
    bg: '#f4efe3', border: '#d9d0bb', text: '#16140f', muted: '#6b6455', grid: '#e6dfcd',
    ramp: ['#e0620a', '#e8982c', '#b8862a', '#2a9a97', '#5f748b', '#9a6548', '#756c5a'],
    other: '#a39a85',
  },
};

function shareList(totals, topN = 7) {
  const entries = [...totals.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
  const sum = entries.reduce((s, [, v]) => s + v, 0);
  if (!sum) return [];
  const top = entries.slice(0, topN).map(([name, bytes]) => ({ name, bytes, other: false }));
  const rest = entries.slice(topN).reduce((s, [, v]) => s + v, 0);
  if (rest > 0) top.push({ name: 'Other', bytes: rest, other: true });
  // Largest-remainder rounding to 0.1% so the shown figures add up to exactly 100.0.
  const raw = top.map((t) => (t.bytes / sum) * 1000);
  const floor = raw.map(Math.floor);
  let left = 1000 - floor.reduce((a, b) => a + b, 0);
  raw.map((r, i) => [r - floor[i], i]).sort((a, b) => b[0] - a[0]).forEach(([, i]) => { if (left-- > 0) floor[i]++; });
  top.forEach((t, i) => { t.pct = floor[i] / 10; t.frac = t.bytes / sum; });
  return top;
}

const xmlEsc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const n1 = (v) => (Math.round(v * 100) / 100).toString();

function renderSvg(theme, shares, repoCount, fonts) {
  const P = PALETTE[theme];
  const W = 1200, H = 240, PAD = 48;
  const barX = PAD, barY = 84, barW = W - PAD * 2, barH = 22, GAP = 4;
  const pctWords = shares.map((s) => `${s.name} ${s.pct.toFixed(1)} percent`).join(', ');
  const title = 'Languages across public repositories';
  const desc = `Share of code by language across ${repoCount} public repositories: ${pctWords}.`;

  // Segment geometry: proportional widths, minus gaps, with a minimum visible width.
  const usable = barW - GAP * (shares.length - 1);
  const MIN = 6;
  let widths = shares.map((s) => Math.max(MIN, s.frac * usable));
  const scale = usable / widths.reduce((a, b) => a + b, 0);
  widths = widths.map((w) => w * scale);
  let x = barX;
  const segs = shares.map((s, i) => {
    const color = s.other ? P.other : P.ramp[i];
    const r = `<rect x="${n1(x)}" y="${barY}" width="${n1(widths[i])}" height="${barH}" fill="${color}"/>`;
    x += widths[i] + GAP;
    return r;
  }).join('');

  const COLS = 4, colW = (W - PAD * 2) / COLS, rowY = [154, 198];
  const legend = shares.map((s, i) => {
    const col = i % COLS, row = Math.floor(i / COLS);
    const lx = PAD + col * colW, ly = rowY[row];
    const color = s.other ? P.other : P.ramp[i];
    const name = s.name.length > 20 ? s.name.slice(0, 19) + '.' : s.name;
    return `<circle cx="${n1(lx + 7)}" cy="${ly - 6}" r="6" fill="${color}"/>` +
      `<text x="${n1(lx + 24)}" y="${ly}" class="nm">${xmlEsc(name)}</text>` +
      `<text x="${n1(lx + colW - 28)}" y="${ly}" class="pc" text-anchor="end">${s.pct.toFixed(1)}%</text>`;
  }).join('');

  const css =
    `@font-face{font-family:'SC Mono';src:url(data:font/woff2;base64,${fonts.mono}) format('woff2');font-weight:500;font-style:normal;font-display:swap;}` +
    `@font-face{font-family:'SC Grotesk';src:url(data:font/woff2;base64,${fonts.sg}) format('woff2');font-weight:500;font-style:normal;font-display:swap;}` +
    `.hd{font-family:'SC Mono',ui-monospace,Consolas,monospace;font-weight:500;font-size:14px;letter-spacing:3px;fill:${P.text};white-space:pre}` +
    `.ct{font-family:'SC Mono',ui-monospace,Consolas,monospace;font-weight:500;font-size:12px;letter-spacing:2px;fill:${P.muted};white-space:pre}` +
    `.nm{font-family:'SC Grotesk','Segoe UI',Arial,sans-serif;font-weight:500;font-size:18px;fill:${P.text}}` +
    `.pc{font-family:'SC Mono',ui-monospace,Consolas,monospace;font-weight:500;font-size:15px;fill:${P.muted}}`;

  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img" aria-labelledby="t d">` +
    `<title id="t">${xmlEsc(title)}</title><desc id="d">${xmlEsc(desc)}</desc>` +
    `<defs><style>${css}</style><clipPath id="bar"><rect x="${barX}" y="${barY}" width="${barW}" height="${barH}" rx="${barH / 2}"/></clipPath></defs>` +
    `<rect x="0.5" y="0.5" width="${W - 1}" height="${H - 1}" rx="18" fill="${P.bg}" stroke="${P.border}"/>` +
    `<line x1="${PAD}" y1="68" x2="${W - PAD}" y2="68" stroke="${P.grid}" stroke-width="1"/>` +
    `<line x1="${PAD}" y1="126" x2="${W - PAD}" y2="126" stroke="${P.grid}" stroke-width="1"/>` +
    `<text x="${PAD}" y="50" class="hd">LANGUAGES  \u00b7  PUBLIC REPOS</text>` +
    `<text x="${W - PAD}" y="50" class="ct" text-anchor="end">${repoCount} ${repoCount === 1 ? 'REPO' : 'REPOS'}</text>` +
    `<g clip-path="url(#bar)">${segs}</g>` +
    legend +
    `</svg>\n`;
}

// ---------------------------------------------------------------- activity
function clean(s, max = 90) {
  let t = String(s ?? '').replace(/[\r\n\t\u2028\u2029]+/g, ' ').replace(/[\u0000-\u001f\u007f]/g, '').replace(/\s+/g, ' ').trim();
  if (t.length > max) t = t.slice(0, max - 1).trimEnd() + '\u2026';
  return t
    .replace(/&/g, '&amp;')
    .replace(/[\\|<>\[\]`*_~#!]/g, (c) => ({ '<': '&lt;', '>': '&gt;', '|': '&#124;' }[c] || '\\' + c))
    .replace(/@/g, '&#64;');
}

function relDate(iso, now = new Date()) {
  const days = Math.floor((now - new Date(iso)) / 86400000);
  if (days <= 0) return 'today';
  if (days === 1) return 'yesterday';
  if (days < 14) return `${days} days ago`;
  if (days < 60) return `${Math.floor(days / 7)} weeks ago`;
  const months = Math.floor(days / 30);
  return months < 12 ? `${months} months ago` : `${Math.floor(days / 365)} years ago`;
}

const isIgnoredRepo = (name) => {
  const n = name.toLowerCase();
  return SKIP_REPOS.has(n) || n.startsWith('test');
};

async function buildActivity(repos, now) {
  const events = (await (await gh(`/users/${USER}/events/public?per_page=100`)).json()) || [];
  const descByName = new Map(repos.map((r) => [r.name.toLowerCase(), r.description || '']));
  const groups = new Map(); // lower name -> {name, events: [...] newest first}
  for (const ev of events) {
    const [owner, name] = String(ev.repo?.name || '').split('/');
    if (!name || owner.toLowerCase() !== USER.toLowerCase() || isIgnoredRepo(name)) continue;
    const ok = ev.type === 'PushEvent' || ev.type === 'ReleaseEvent' ||
      (ev.type === 'CreateEvent' && ev.payload?.ref_type === 'repository');
    if (!ok) continue;
    const key = name.toLowerCase();
    if (!groups.has(key)) groups.set(key, { name, events: [] });
    groups.get(key).events.push(ev);
  }
  const items = [];
  for (const g of [...groups.values()].slice(0, 5)) { // events arrive newest first
    let msg = '';
    for (const ev of g.events) {
      if (ev.type === 'PushEvent') {
        const commits = ev.payload?.commits || [];
        const last = commits[commits.length - 1];
        if (last?.message) {
          msg = last.message.split('\n')[0];
        } else if (ev.payload?.head) {
          try {
            const c = await (await gh(`/repos/${USER}/${g.name}/commits/${ev.payload.head}`)).json();
            msg = (c.commit?.message || '').split('\n')[0];
          } catch (e) { if (e instanceof RateLimitError) throw e; }
        }
      } else if (ev.type === 'ReleaseEvent') {
        const rel = ev.payload?.release;
        const label = rel?.name || rel?.tag_name;
        if (label) msg = `Released ${label}`;
      }
      if (msg) break;
    }
    if (!msg) msg = descByName.get(g.name.toLowerCase()) || 'New repository';
    items.push({
      name: g.name,
      url: `https://github.com/${USER}/${encodeURIComponent(g.name)}`,
      msg,
      when: relDate(g.events[0].created_at, now),
    });
  }
  return items;
}

function activityMarkdown(items) {
  if (!items.length) return '_No public activity yet this month._';
  return items.map((i) => `- **[${clean(i.name, 60)}](${i.url})**: ${clean(i.msg)} \u00b7 ${i.when}`).join('\n');
}

// ---------------------------------------------------------------- README + files
function replaceBlock(text, startMarker, endMarker, body) {
  const s = text.indexOf(startMarker), e = text.indexOf(endMarker);
  if (s === -1 || e === -1 || e < s) return null;
  const eol = text.includes('\r\n') ? '\r\n' : '\n';
  return text.slice(0, s + startMarker.length) + eol + body.replace(/\n/g, eol) + eol + text.slice(e);
}

function writeIfChanged(file, content) {
  if (existsSync(file) && readFileSync(file, 'utf8') === content) return false;
  mkdirSync(dirname(file), { recursive: true });
  writeFileSync(file, content);
  return true;
}

async function main() {
  const now = new Date();
  const fonts = JSON.parse(readFileSync(join(HERE, 'fonts.json'), 'utf8'));
  const report = [];

  // 1. repos + languages
  const all = await ghPaged(`/users/${USER}/repos?per_page=100&type=owner`);
  const repos = all.filter((r) => !r.fork && !r.archived && !r.private && !SKIP_REPOS.has(r.name.toLowerCase()));
  const totals = new Map();
  let used = 0, langFailures = 0;
  for (const r of repos) {
    try {
      const langs = await (await gh(`/repos/${r.full_name}/languages`)).json();
      let any = false;
      for (const [k, v] of Object.entries(langs)) { totals.set(k, (totals.get(k) || 0) + v); any = true; }
      if (any) used++;
    } catch (e) {
      if (e instanceof RateLimitError) throw e;
      langFailures++;
      console.warn(`warn: languages for ${r.full_name}: ${e.message}`);
    }
  }
  const shares = shareList(totals);
  if (!shares.length) throw new Error('no language data found for any repository');
  const changed = [];
  for (const theme of ['dark', 'light']) {
    const f = join(OUT_DIR, `languages-${theme}.svg`);
    if (writeIfChanged(f, renderSvg(theme, shares, used, fonts))) changed.push(`languages-${theme}.svg`);
  }
  report.push(`languages: ${shares.map((s) => `${s.name} ${s.pct.toFixed(1)}%`).join(', ')}`);
  report.push(`repos used: ${used} of ${repos.length} eligible${langFailures ? ` (${langFailures} language lookups failed)` : ''}`);

  // 2. activity (a failure here must not clobber the existing list)
  let items = null;
  try { items = await buildActivity(repos, now); }
  catch (e) {
    if (e instanceof RateLimitError) throw e;
    console.warn(`warn: activity feed unavailable, leaving it untouched: ${e.message}`);
  }
  if (items) {
    report.push('activity:');
    for (const l of (items.length ? activityMarkdown(items) : '(none)').split('\n')) report.push('  ' + l);
  }

  // 3. README
  let readmeChanged = false;
  if (existsSync(README)) {
    const orig = readFileSync(README, 'utf8');
    let text = orig;
    if (items) {
      const r = replaceBlock(text, '<!-- ACTIVITY:START -->', '<!-- ACTIVITY:END -->', activityMarkdown(items));
      if (r !== null) text = r;
    }
    const v = createHash('sha1').update(JSON.stringify(shares)).digest('hex').slice(0, 8);
    const alt = xmlEsc(`Language share across public repos: ${shares.map((s) => `${s.name} ${s.pct.toFixed(1)}%`).join(', ')}`);
    const picture = [
      '<picture>',
      `  <source media="(prefers-color-scheme: dark)" srcset="./assets/live/languages-dark.svg?v=${v}">`,
      `  <source media="(prefers-color-scheme: light)" srcset="./assets/live/languages-light.svg?v=${v}">`,
      `  <img alt="${alt}" src="./assets/live/languages-light.svg?v=${v}" width="100%">`,
      '</picture>',
    ].join('\n');
    const r2 = replaceBlock(text, '<!-- LANG:START -->', '<!-- LANG:END -->', picture);
    if (r2 !== null) text = r2;
    if (text !== orig) { writeFileSync(README, text); readmeChanged = true; }
  }
  report.push(`files written: ${changed.length ? changed.join(', ') : 'none (unchanged)'}`);
  report.push(`README.md changed: ${readmeChanged ? 'yes' : 'no'}`);
  console.log(report.join('\n'));
}

main().catch((e) => {
  console.error(e instanceof RateLimitError ? `RATE LIMIT: ${e.message}` : `error: ${e.message}`);
  process.exit(1);
});
