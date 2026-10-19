// Self-contained tests: `node game/test.mjs`
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import {
  ROWS, COLS, EMPTY, HUMAN, BOT,
  parseTitle, parseLogin, sanitizeAuthor,
  emptyBoard, dropRow, drop, isFull, findWin, chooseBotMove,
  initialState, loadState, serializeState, handleEvent,
  renderSvg, renderReadmeBlock, injectReadme, run,
} from './connect4.mjs';

let passed = 0;
let failed = 0;
function test(name, fn) {
  try {
    fn();
    passed++;
    console.log(`ok   - ${name}`);
  } catch (err) {
    failed++;
    console.log(`FAIL - ${name}\n${err.stack}`);
  }
}

/** Build a board from 6 strings (top row first): '.' empty, 'R' human, 'Y' bot. */
function boardFrom(rows) {
  assert.equal(rows.length, ROWS);
  return rows.map((line) => {
    assert.equal(line.length, COLS);
    return [...line].map((ch) => ({ '.': EMPTY, R: HUMAN, Y: BOT })[ch]);
  });
}

/** Place discs straight into a board (test helper, no gravity checks). */
function put(board, cells) {
  for (const [r, c, p] of cells) board[r][c] = p;
  return board;
}

const stateWith = (board, extra = {}) => ({ ...initialState(), board, ...extra });

// --- Drop / gravity --------------------------------------------------------

test('discs fall to the bottom and stack', () => {
  let b = emptyBoard();
  let r = drop(b, 3, HUMAN);
  assert.equal(r.row, 5);
  b = r.board;
  r = drop(b, 3, BOT);
  assert.equal(r.row, 4);
  assert.equal(r.board[5][3], HUMAN);
  assert.equal(r.board[4][3], BOT);
  assert.equal(b[4][3], EMPTY, 'drop() must not mutate its input');
});

test('a full column is rejected', () => {
  let b = emptyBoard();
  for (let i = 0; i < ROWS; i++) b = drop(b, 0, i % 2 ? BOT : HUMAN).board;
  assert.equal(dropRow(b, 0), -1);
  const r = drop(b, 0, HUMAN);
  assert.equal(r.row, -1);
  assert.equal(r.board, b);
  assert.equal(dropRow(b, -1), -1);
  assert.equal(dropRow(b, 7), -1);
  assert.equal(dropRow(b, 1.5), -1);
});

test('moving into a full column changes nothing and explains why', () => {
  let s = initialState();
  const b = emptyBoard();
  for (let i = 0; i < ROWS; i++) b[ROWS - 1 - i][6] = i % 2 ? BOT : HUMAN;
  s = stateWith(b);
  const res = handleEvent(s, { title: 'c4|move|7', author: 'alice' });
  assert.equal(res.changed, false);
  assert.equal(res.state, s);
  assert.match(res.comment, /column 7 is full/);
});

// --- Win detection ---------------------------------------------------------

test('horizontal win', () => {
  const b = put(emptyBoard(), [[5, 1, HUMAN], [5, 2, HUMAN], [5, 3, HUMAN], [5, 4, HUMAN]]);
  const w = findWin(b);
  assert.equal(w.player, HUMAN);
  assert.equal(w.cells.length, 4);
});

test('vertical win', () => {
  const b = put(emptyBoard(), [[5, 2, BOT], [4, 2, BOT], [3, 2, BOT], [2, 2, BOT]]);
  assert.equal(findWin(b).player, BOT);
});

test('diagonal win (down-right)', () => {
  const b = put(emptyBoard(), [[2, 0, HUMAN], [3, 1, HUMAN], [4, 2, HUMAN], [5, 3, HUMAN]]);
  assert.equal(findWin(b).player, HUMAN);
});

test('diagonal win (down-left)', () => {
  const b = put(emptyBoard(), [[2, 6, BOT], [3, 5, BOT], [4, 4, BOT], [5, 3, BOT]]);
  assert.equal(findWin(b).player, BOT);
});

test('three in a row, or four with a gap, is not a win', () => {
  const b = put(emptyBoard(), [[5, 0, HUMAN], [5, 1, HUMAN], [5, 2, HUMAN], [5, 4, HUMAN], [5, 5, BOT]]);
  assert.equal(findWin(b), null);
});

test('a longer run is reported end to end', () => {
  const b = put(emptyBoard(), [[5, 0, HUMAN], [5, 1, HUMAN], [5, 2, HUMAN], [5, 3, HUMAN], [5, 4, HUMAN]]);
  assert.equal(findWin(b).cells.length, 5);
});

test('winning move ends the game, counts stats, and the bot does not reply', () => {
  const b = put(emptyBoard(), [[5, 0, HUMAN], [5, 1, HUMAN], [5, 2, HUMAN], [4, 0, BOT], [4, 1, BOT]]);
  const res = handleEvent(stateWith(b), { title: 'c4|move|4', author: 'alice' });
  assert.equal(res.changed, true);
  assert.equal(res.state.status, 'human_won');
  assert.equal(res.state.botMove, null);
  assert.equal(res.state.stats.games, 1);
  assert.equal(res.state.stats.humanWins, 1);
  assert.equal(res.state.moves, 6);
  assert.match(res.comment, /You win/);
});

test('a move that lets the bot win is recorded as a bot win', () => {
  // Bot has three on the bottom row at cols 0-2; human plays elsewhere.
  const b = put(emptyBoard(), [[5, 0, BOT], [5, 1, BOT], [5, 2, BOT], [4, 0, HUMAN], [4, 1, HUMAN]]);
  const res = handleEvent(stateWith(b), { title: 'c4|move|7', author: 'alice' });
  assert.equal(res.state.status, 'bot_won');
  assert.equal(res.state.botMove.col, 3);
  assert.equal(res.state.stats.botWins, 1);
});

// --- Draw -------------------------------------------------------------------

/** A full board with no four in a row, with one cell (top of col 6) left open. */
const DRAW_ROWS = [
  'RRYRRY.',
  'YYRYYRR',
  'RRYRRYY',
  'YYRYYRR',
  'RRYRRYY',
  'YYRYYRR',
];

test('draw: human fills the last cell with no win', () => {
  // Verify the fixture really has no line once the last cell is filled either way.
  for (const p of [HUMAN, BOT]) {
    const b = boardFrom(DRAW_ROWS);
    b[0][6] = p;
    assert.equal(findWin(b), null, 'fixture must be win-free');
    assert.ok(isFull(b));
  }
  const res = handleEvent(stateWith(boardFrom(DRAW_ROWS)), { title: 'c4|move|7', author: 'alice' });
  assert.equal(res.state.status, 'draw');
  assert.equal(res.state.stats.draws, 1);
  assert.equal(res.state.stats.games, 1);
  assert.equal(res.state.botMove, null);
});

test('draw: bot fills the last cell after the human move', () => {
  const rows = DRAW_ROWS.slice();
  rows[0] = 'RRYRR..'; // two top cells free: cols 5 and 6
  const b = boardFrom(rows);
  assert.equal(findWin(b), null);
  const res = handleEvent(stateWith(b), { title: 'c4|move|6', author: 'alice' });
  assert.equal(res.changed, true);
  assert.ok(['draw', 'bot_won', 'human_won'].includes(res.state.status));
  if (res.state.status === 'draw') assert.ok(isFull(res.state.board));
});

test('moves are refused once the game is over', () => {
  const s = stateWith(boardFrom(DRAW_ROWS), { status: 'draw' });
  const res = handleEvent({ ...s }, { title: 'c4|move|1', author: 'alice' });
  assert.equal(res.changed, false);
  assert.match(res.comment, /already over/);
});

// --- Bot --------------------------------------------------------------------

test('bot blocks an immediate human win (horizontal)', () => {
  const b = put(emptyBoard(), [[5, 0, HUMAN], [5, 1, HUMAN], [5, 2, HUMAN], [5, 6, BOT]]);
  assert.equal(chooseBotMove(b), 3);
});

test('bot blocks an immediate human win (vertical)', () => {
  const b = put(emptyBoard(), [[5, 5, HUMAN], [4, 5, HUMAN], [3, 5, HUMAN], [5, 0, BOT], [5, 1, BOT]]);
  assert.equal(chooseBotMove(b), 5);
});

test('bot takes its own immediate win rather than blocking', () => {
  const b = put(emptyBoard(), [
    [5, 0, HUMAN], [5, 1, HUMAN], [5, 2, HUMAN], // human threatens col 3
    [5, 6, BOT], [4, 6, BOT], [3, 6, BOT], // bot can win in col 6
  ]);
  assert.equal(chooseBotMove(b), 6);
});

test('bot is deterministic and does not mutate the board', () => {
  const b = put(emptyBoard(), [[5, 3, HUMAN], [5, 2, BOT], [4, 3, HUMAN]]);
  const snapshot = JSON.stringify(b);
  const first = chooseBotMove(b);
  assert.equal(chooseBotMove(b), first);
  assert.equal(JSON.stringify(b), snapshot);
});

test('bot answers an empty-ish board in a legal column, preferring the centre', () => {
  const b = put(emptyBoard(), [[5, 0, HUMAN]]);
  assert.equal(chooseBotMove(b), 3);
});

test('bot returns -1 on a full board', () => {
  const b = boardFrom(DRAW_ROWS);
  b[0][6] = HUMAN;
  assert.equal(chooseBotMove(b), -1);
});

test('bot sees a two-way threat coming (depth 5)', () => {
  // Human has 2 and 3 on the bottom with both ends open: playing col 1 or 4
  // would create an open three. Whatever the bot picks must not lose at once.
  const b = put(emptyBoard(), [[5, 2, HUMAN], [5, 3, HUMAN], [5, 6, BOT]]);
  const col = chooseBotMove(b);
  assert.ok([1, 4].includes(col), `expected to break the open pair, got ${col}`);
});

// --- Title parsing ----------------------------------------------------------

test('strict title parsing accepts only the two protocol forms', () => {
  for (let n = 1; n <= 7; n++) assert.deepEqual(parseTitle(`c4|move|${n}`), { type: 'move', col: n - 1 });
  assert.deepEqual(parseTitle('c4|new'), { type: 'new' });
  const bad = [
    'c4|move|8', 'c4|move|0', 'c4|move|1;rm', 'c4|move|10', 'c4|move|-1', 'c4|move|',
    'c4|move| 1', 'c4|move |1', ' c4|move|1', 'c4|move|1 ', 'c4| move|1', 'c4|new ', ' c4|new',
    'C4|move|1', 'c4|MOVE|1', 'c4|New', 'c4|move|1\n', 'c4|new\n', 'c4|move|1\nfoo',
    'c5|move|1', 'c4|play|1', 'c4|move|1|2', 'c4|new|x', 'c4', 'c4|', '', 'hello',
    'c4|move|１', 'c4|move|١',
  ];
  for (const t of bad) assert.equal(parseTitle(t), null, `should reject ${JSON.stringify(t)}`);
  for (const t of [undefined, null, 5, {}, ['c4|new']]) assert.equal(parseTitle(t), null);
});

test('unparseable titles change nothing and are never echoed', () => {
  const s = initialState();
  const evil = 'c4|move|1;rm -rf <script>';
  const res = handleEvent(s, { title: evil, author: 'alice' });
  assert.equal(res.changed, false);
  assert.equal(res.state, s);
  assert.ok(!res.comment.includes('rm -rf'));
  assert.ok(!res.comment.includes('<script>'));
});

// --- Author validation -------------------------------------------------------

test('author login validation', () => {
  for (const ok of ['a', 'NINJA981', 'octo-cat', 'x'.repeat(39), '0day']) assert.equal(parseLogin(ok), ok);
  const bad = [
    '', '-lead', 'x'.repeat(40), 'has space', 'semi;colon', 'dependabot[bot]', 'github-actions[bot]',
    'a[bot]', 'a/b', 'a\nb', '<img>', 'ünï', undefined, null, 42,
  ];
  for (const b of bad) assert.equal(parseLogin(b), null, `should reject ${JSON.stringify(b)}`);
  assert.equal(sanitizeAuthor('dependabot[bot]'), 'anonymous');
  assert.equal(sanitizeAuthor('alice'), 'alice');
});

test('invalid author still plays, but is never stored or echoed', () => {
  const raw = 'evil"><script>';
  const res = handleEvent(initialState(), { title: 'c4|move|4', author: raw });
  assert.equal(res.changed, true);
  assert.equal(res.state.lastMove.by, null);
  assert.deepEqual(res.state.recent, []);
  assert.ok(!res.comment.includes('evil'));
  assert.ok(!JSON.stringify(res.state).includes('evil'));
  assert.ok(!renderReadmeBlock(res.state).includes('Last move by'));
  assert.ok(!renderSvg(res.state, 'dark').includes('evil'));
});

test('recent list keeps the last 5 distinct valid logins, newest first', () => {
  let s = initialState();
  for (const who of ['a1', 'b2', 'c3', 'd4', 'e5', 'f6', 'c3']) {
    s = { ...s, status: 'playing' };
    const res = handleEvent(s, { title: 'c4|move|1', author: who });
    s = res.state;
    if (s.status !== 'playing') s = { ...initialState(s.stats, s.recent), rev: s.rev };
  }
  assert.deepEqual(s.recent, ['c3', 'f6', 'e5', 'd4', 'b2']);
  assert.equal(s.recent.length, 5);
});

// --- Reset rules ---------------------------------------------------------------

test('c4|new refused mid-game for visitors, allowed for the owner', () => {
  const mid = handleEvent(initialState(), { title: 'c4|move|4', author: 'alice' }).state;
  assert.equal(mid.status, 'playing');
  const refused = handleEvent(mid, { title: 'c4|new', author: 'alice' });
  assert.equal(refused.changed, false);
  assert.equal(refused.state, mid);
  const anon = handleEvent(mid, { title: 'c4|new', author: 'bad login!' });
  assert.equal(anon.changed, false);
  const owner = handleEvent(mid, { title: 'c4|new', author: 'NINJA981' });
  assert.equal(owner.changed, true);
  assert.equal(owner.state.moves, 0);
  assert.equal(owner.state.status, 'playing');
  assert.ok(owner.state.rev > mid.rev);
  assert.deepEqual(owner.state.recent, mid.recent, 'recent players survive a reset');
});

test('c4|new allowed for anyone once the game is over; stats survive', () => {
  const over = stateWith(boardFrom(DRAW_ROWS), {
    status: 'draw',
    stats: { games: 3, humanWins: 1, botWins: 1, draws: 1 },
  });
  const res = handleEvent(over, { title: 'c4|new', author: 'alice' });
  assert.equal(res.changed, true);
  assert.equal(res.state.status, 'playing');
  assert.equal(res.state.moves, 0);
  assert.deepEqual(res.state.stats, over.stats);
  assert.equal(findWin(res.state.board), null);
  assert.ok(res.state.board.every((row) => row.every((c) => c === EMPTY)));
});

// --- State, rendering, README ---------------------------------------------------

test('state round-trips through serialize/load and is validated', () => {
  let s = initialState();
  s = handleEvent(s, { title: 'c4|move|4', author: 'alice' }).state;
  s = handleEvent(s, { title: 'c4|move|3', author: 'bob' }).state;
  const again = loadState(JSON.parse(serializeState(s)));
  assert.deepEqual(again, s);

  const good = JSON.parse(serializeState(initialState()));
  const corrupt = [
    (x) => { x.board[0] = 'RRRRRRR'; },
    (x) => { x.board[5] = '......'; },
    (x) => { x.board[0] = '..R....'; }, // floating disc
    (x) => { x.status = 'nope'; },
    (x) => { x.status = 'human_won'; },
    (x) => { x.stats.games = -1; },
    (x) => { x.board = 'x'; },
  ];
  for (const mutate of corrupt) {
    const x = JSON.parse(JSON.stringify(good));
    mutate(x);
    assert.throws(() => loadState(x));
  }
  // Tampered logins are dropped, not trusted.
  const x = JSON.parse(JSON.stringify(good));
  x.recent = ['ok-user', '<b>x</b>', 'bad[bot]'];
  assert.deepEqual(loadState(x).recent, ['ok-user']);
});

test('SVGs are small, accessible, self-contained and animate the last disc', () => {
  let s = handleEvent(initialState(), { title: 'c4|move|4', author: 'alice' }).state;
  for (const theme of ['dark', 'light']) {
    const svg = renderSvg(s, theme);
    assert.ok(svg.length < 15 * 1024, `${theme} svg is ${svg.length} bytes`);
    assert.match(svg, /<title id="t">/);
    assert.match(svg, /<desc id="d">/);
    assert.match(svg, /<animate attributeName="opacity"/);
    assert.ok(!/https?:\/\/(?!www\.w3\.org)/.test(svg), 'no external resources');
    assert.ok(!/<text|<image|<script|href=/.test(svg));
    assert.equal(svg, renderSvg(s, theme), 'deterministic');
  }
  assert.match(renderSvg(s, 'dark'), /#ff7a18/);
  assert.match(renderSvg(s, 'light'), /#d9600a/);
  assert.throws(() => renderSvg(s, 'blue'));

  // Winning line only when someone has won.
  assert.ok(!renderSvg(s, 'dark').includes('<line'));
  const b = put(emptyBoard(), [[5, 0, HUMAN], [5, 1, HUMAN], [5, 2, HUMAN], [4, 0, BOT], [4, 1, BOT]]);
  const won = handleEvent(stateWith(b), { title: 'c4|move|4', author: 'alice' }).state;
  assert.match(renderSvg(won, 'dark'), /<line/);
});

test('README block: playing state has 7 links with exact URLs and cache-buster', () => {
  const s = handleEvent(initialState(), { title: 'c4|move|4', author: 'alice' }).state;
  const block = renderReadmeBlock(s);
  assert.ok(block.includes(`./assets/game/board-dark.svg?v=${s.rev}`));
  assert.ok(block.includes(`./assets/game/board-light.svg?v=${s.rev}`));
  assert.ok(block.includes('prefers-color-scheme: dark'));
  assert.ok(block.includes('prefers-color-scheme: light'));
  for (let n = 1; n <= 7; n++) {
    const link = `[${n}](https://github.com/NINJA981/NINJA981/issues/new?title=c4%7Cmove%7C${n}&body=Just+press+%22Submit+new+issue%22.+The+move+is+played+automatically.)`;
    assert.ok(block.includes(link), `missing link ${n}`);
  }
  assert.ok(block.includes('Last move by @alice'));
  assert.ok(block.includes('Games played 0'));
  assert.ok(!block.includes('Start a new game'));
});

test('README block: finished game shows result and a single new-game link', () => {
  const s = stateWith(boardFrom(DRAW_ROWS), { status: 'draw' });
  const block = renderReadmeBlock(s);
  assert.ok(block.includes('[Start a new game](https://github.com/NINJA981/NINJA981/issues/new?title=c4%7Cnew&body=Just+press+%22Submit+new+issue%22.)'));
  assert.ok(!block.includes('title=c4%7Cmove'));
});

test('README injection: replaces only the block, skips when markers are absent', () => {
  const doc = 'before\n<!-- C4:START -->\nold\n<!-- C4:END -->\nafter\n';
  const out = injectReadme(doc, 'NEW');
  assert.equal(out, 'before\n<!-- C4:START -->\nNEW\n<!-- C4:END -->\nafter\n');
  assert.equal(injectReadme(out, 'NEW'), out, 'idempotent');
  assert.equal(injectReadme('no markers here', 'X'), null);
  assert.equal(injectReadme('<!-- C4:START --> only start', 'X'), null);
  assert.equal(injectReadme('<!-- C4:END --> <!-- C4:START -->', 'X'), null);
});

test('end to end through run(): files written, README untouched without markers', () => {
  const root = mkdtempSync(join(tmpdir(), 'c4-'));
  try {
    mkdirSync(join(root, 'game'));
    writeFileSync(join(root, 'game', 'state.json'), serializeState(initialState()));
    writeFileSync(join(root, 'README.md'), '# hi\n');
    let res = run({ title: 'c4|move|4', author: 'alice', root });
    assert.equal(res.changed, true);
    assert.equal(res.readmeUpdated, false);
    assert.equal(readFileSync(join(root, 'README.md'), 'utf8'), '# hi\n');
    assert.match(readFileSync(join(root, 'game', 'out.md'), 'utf8'), /github\.com\/NINJA981/);
    assert.ok(readFileSync(join(root, 'assets', 'game', 'board-dark.svg'), 'utf8').startsWith('<svg'));

    writeFileSync(join(root, 'README.md'), 'x\n<!-- C4:START -->\n<!-- C4:END -->\ny\n');
    const before = readFileSync(join(root, 'game', 'state.json'), 'utf8');
    res = run({ title: 'garbage', author: 'alice', root });
    assert.equal(res.changed, false);
    assert.equal(res.readmeUpdated, true);
    assert.equal(readFileSync(join(root, 'game', 'state.json'), 'utf8'), before);
    const readme = readFileSync(join(root, 'README.md'), 'utf8');
    assert.ok(readme.startsWith('x\n<!-- C4:START -->\n<div align="center">'));
    assert.ok(readme.endsWith('<!-- C4:END -->\ny\n'));
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('a full random game always ends in a legal terminal state', () => {
  let s = initialState();
  let seed = 12345;
  const rnd = () => (seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648;
  for (let i = 0; i < 60 && s.status === 'playing'; i++) {
    const open = [...Array(COLS).keys()].filter((c) => dropRow(s.board, c) >= 0);
    const col = open[Math.floor(rnd() * open.length)];
    const res = handleEvent(s, { title: `c4|move|${col + 1}`, author: 'player' });
    assert.equal(res.changed, true);
    s = res.state;
    assert.deepEqual(loadState(JSON.parse(serializeState(s))), s);
  }
  assert.notEqual(s.status, 'playing');
  assert.equal(s.stats.games, 1);
});

console.log(`\n${passed} passed, ${failed} failed`);
if (failed) process.exit(1);
