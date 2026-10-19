// Connect 4 for a GitHub profile README.
//
// A visitor opens an issue titled `c4|move|N`; a GitHub Action runs this script,
// which plays the visitor's disc, lets the bot answer, re-renders the board SVGs,
// rewrites the README block and writes the comment text for the issue.
//
// Zero dependencies: Node built-ins only.
//
// Security notes
//  * ISSUE_TITLE and ISSUE_AUTHOR are untrusted. The title is only ever matched
//    against two strict regexes and never echoed. The author is only used if it
//    matches a strict GitHub-login regex; otherwise it is treated as "anonymous"
//    and the raw value is never written anywhere.
//  * Nothing but validated logins and numbers ever reach a file.
//
// Coordinates: columns are 0..6 (left to right), rows are 0..5 (TOP to bottom).
// Anything shown to humans uses 1-based columns.

import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

export const ROWS = 6;
export const COLS = 7;
export const EMPTY = 0;
export const HUMAN = 1; // visitors, orange
export const BOT = 2; // the bot, cream (dark theme) / ink (light theme)

export const OWNER = 'NINJA981';
export const PROFILE_URL = `https://github.com/${OWNER}`;
export const ISSUE_NEW_URL = `${PROFILE_URL}/${OWNER}/issues/new`;

export const BOT_DEPTH = 5;
// Columns tried in this order: centre first. Ties in search keep the earliest.
const COLUMN_ORDER = [3, 2, 4, 1, 5, 0, 6];

const MOVE_RE = /^c4\|move\|([1-7])$/;
const NEW_RE = /^c4\|new$/;
const LOGIN_RE = /^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$/;

const START_MARK = '<!-- C4:START -->';
const END_MARK = '<!-- C4:END -->';

const STATUSES = ['playing', 'human_won', 'bot_won', 'draw'];

// ---------------------------------------------------------------------------
// Input validation
// ---------------------------------------------------------------------------

/**
 * Strictly parse an issue title.
 * @returns {{type:'move', col:number}|{type:'new'}|null} col is 0-based.
 */
export function parseTitle(title) {
  if (typeof title !== 'string') return null;
  const m = MOVE_RE.exec(title);
  if (m) return { type: 'move', col: Number(m[1]) - 1 };
  if (NEW_RE.test(title)) return { type: 'new' };
  return null;
}

/** Return the login if it is a valid, non-bot GitHub login, else null. */
export function parseLogin(raw) {
  if (typeof raw !== 'string') return null;
  if (!LOGIN_RE.test(raw)) return null;
  if (raw.toLowerCase().endsWith('[bot]')) return null; // defensive; regex already forbids it
  return raw;
}

/** Login or the literal 'anonymous'. */
export function sanitizeAuthor(raw) {
  return parseLogin(raw) ?? 'anonymous';
}

// ---------------------------------------------------------------------------
// Board primitives (grid[row][col], row 0 is the top)
// ---------------------------------------------------------------------------

export function emptyBoard() {
  return Array.from({ length: ROWS }, () => new Array(COLS).fill(EMPTY));
}

export function cloneBoard(board) {
  return board.map((row) => row.slice());
}

/** Row a disc dropped into `col` would land on, or -1 if the column is full/invalid. */
export function dropRow(board, col) {
  if (!Number.isInteger(col) || col < 0 || col >= COLS) return -1;
  for (let r = ROWS - 1; r >= 0; r--) if (board[r][col] === EMPTY) return r;
  return -1;
}

/** Drop a disc, returning a new board and the landing row (row -1 means refused). */
export function drop(board, col, player) {
  const row = dropRow(board, col);
  if (row < 0) return { board, row: -1 };
  const next = cloneBoard(board);
  next[row][col] = player;
  return { board: next, row };
}

export function isFull(board) {
  return board[0].every((c) => c !== EMPTY);
}

export function countDiscs(board) {
  let n = 0;
  for (const row of board) for (const c of row) if (c !== EMPTY) n++;
  return n;
}

const DIRECTIONS = [
  [0, 1], // horizontal
  [1, 0], // vertical
  [1, 1], // diagonal down-right
  [1, -1], // diagonal down-left
];

const inBounds = (r, c) => r >= 0 && r < ROWS && c >= 0 && c < COLS;

/** Does the disc at (r,c) belong to a line of 4+? (used inside the search) */
function winsAt(board, r, c) {
  const p = board[r][c];
  if (p === EMPTY) return false;
  for (const [dr, dc] of DIRECTIONS) {
    let n = 1;
    for (let rr = r + dr, cc = c + dc; inBounds(rr, cc) && board[rr][cc] === p; rr += dr, cc += dc) n++;
    for (let rr = r - dr, cc = c - dc; inBounds(rr, cc) && board[rr][cc] === p; rr -= dr, cc -= dc) n++;
    if (n >= 4) return true;
  }
  return false;
}

/**
 * Find a winning line anywhere on the board.
 * @returns {{player:number, cells:Array<[number,number]>}|null} cells is the whole
 *   contiguous run (4 or more) ordered from one end to the other.
 */
export function findWin(board) {
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      const p = board[r][c];
      if (p === EMPTY) continue;
      for (const [dr, dc] of DIRECTIONS) {
        // Only start at the beginning of a run so each run is reported once.
        if (inBounds(r - dr, c - dc) && board[r - dr][c - dc] === p) continue;
        const cells = [];
        for (let rr = r, cc = c; inBounds(rr, cc) && board[rr][cc] === p; rr += dr, cc += dc) cells.push([rr, cc]);
        if (cells.length >= 4) return { player: p, cells };
      }
    }
  }
  return null;
}

// ---------------------------------------------------------------------------
// Bot: immediate win / block, then minimax with alpha-beta (deterministic)
// ---------------------------------------------------------------------------

const WIN_SCORE = 1_000_000;

/** Heuristic score from the bot's point of view. */
function evaluate(board) {
  let score = 0;
  // Centre column preference.
  for (let r = 0; r < ROWS; r++) {
    if (board[r][3] === BOT) score += 3;
    else if (board[r][3] === HUMAN) score -= 3;
  }
  // Every window of four cells.
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      for (const [dr, dc] of DIRECTIONS) {
        const er = r + 3 * dr;
        const ec = c + 3 * dc;
        if (!inBounds(er, ec)) continue;
        let bot = 0;
        let human = 0;
        for (let i = 0; i < 4; i++) {
          const v = board[r + i * dr][c + i * dc];
          if (v === BOT) bot++;
          else if (v === HUMAN) human++;
        }
        if (bot && human) continue; // dead window
        if (bot === 3) score += 6;
        else if (bot === 2) score += 2;
        if (human === 3) score -= 7;
        else if (human === 2) score -= 2;
      }
    }
  }
  return score;
}

/**
 * Alpha-beta search. `player` is about to move. Mutates and restores `board`.
 * Returns a score from the bot's point of view.
 */
function search(board, depth, alpha, beta, player) {
  let any = false;
  const maximizing = player === BOT;
  let best = maximizing ? -Infinity : Infinity;
  for (const col of COLUMN_ORDER) {
    const row = dropRow(board, col);
    if (row < 0) continue;
    any = true;
    board[row][col] = player;
    let score;
    if (winsAt(board, row, col)) {
      // Prefer quicker wins / slower losses: more remaining depth = sooner.
      score = (maximizing ? 1 : -1) * (WIN_SCORE + depth);
    } else if (depth <= 1) {
      score = evaluate(board);
    } else {
      score = search(board, depth - 1, alpha, beta, maximizing ? HUMAN : BOT);
    }
    board[row][col] = EMPTY;
    if (maximizing) {
      if (score > best) best = score;
      if (best > alpha) alpha = best;
    } else {
      if (score < best) best = score;
      if (best < beta) beta = best;
    }
    if (alpha >= beta) break;
  }
  return any ? best : 0; // no legal move: board is full, a draw
}

/** Column (0-based) where `player` would win immediately, or -1. */
function immediateWin(board, player) {
  for (const col of COLUMN_ORDER) {
    const row = dropRow(board, col);
    if (row < 0) continue;
    board[row][col] = player;
    const win = winsAt(board, row, col);
    board[row][col] = EMPTY;
    if (win) return col;
  }
  return -1;
}

/**
 * Choose the bot's column (0-based), or -1 if the board is full. Never mutates
 * the board passed in.
 */
export function chooseBotMove(input, depth = BOT_DEPTH) {
  const board = cloneBoard(input);
  const legal = COLUMN_ORDER.filter((c) => dropRow(board, c) >= 0);
  if (legal.length === 0) return -1;

  const win = immediateWin(board, BOT);
  if (win >= 0) return win;
  const block = immediateWin(board, HUMAN);
  if (block >= 0) return block;

  let bestCol = legal[0];
  let bestScore = -Infinity;
  for (const col of legal) {
    const row = dropRow(board, col);
    board[row][col] = BOT;
    const score = search(board, depth - 1, bestScore, Infinity, HUMAN);
    board[row][col] = EMPTY;
    if (score > bestScore) {
      bestScore = score;
      bestCol = col;
    }
  }
  return bestCol;
}

// ---------------------------------------------------------------------------
// State: creation, (de)serialisation, validation
// ---------------------------------------------------------------------------

const CELL_CHAR = { [EMPTY]: '.', [HUMAN]: 'R', [BOT]: 'Y' };
const CHAR_CELL = { '.': EMPTY, R: HUMAN, Y: BOT };

export function initialState(stats = null, recent = []) {
  return {
    version: 1,
    rev: 0, // bumped on every state change; drives the ?v= cache-buster
    status: 'playing',
    turn: 'human',
    moves: 0, // discs in the current game
    board: emptyBoard(),
    lastMove: null, // {col, row, by} the visitor's disc; by is a validated login or null
    botMove: null, // {col, row} the bot's reply, if any
    stats: stats ? { ...stats } : { games: 0, humanWins: 0, botWins: 0, draws: 0 },
    recent: [...recent],
  };
}

/** JSON text for state.json: board rows stay on one line each so diffs are readable. */
export function serializeState(state) {
  const rows = state.board.map((row) => '    ' + JSON.stringify(row.map((c) => CELL_CHAR[c]).join('')));
  const rest = { ...state };
  delete rest.board;
  const json = JSON.stringify(rest, null, 2);
  // Splice the board in after "turn"/"moves" to keep a stable, readable layout.
  const marker = '"moves": ' + state.moves + ',';
  const at = json.indexOf(marker);
  if (at < 0) throw new Error('serializeState: layout marker missing');
  const insertAt = at + marker.length;
  return json.slice(0, insertAt) + '\n  "board": [\n' + rows.join(',\n') + '\n  ],' + json.slice(insertAt) + '\n';
}

const isCount = (n) => Number.isInteger(n) && n >= 0 && n <= 1_000_000_000;

function validCell(cell) {
  return (
    cell === null ||
    (cell && Number.isInteger(cell.col) && cell.col >= 0 && cell.col < COLS && Number.isInteger(cell.row) && cell.row >= 0 && cell.row < ROWS)
  );
}

/** Validate a parsed state.json and return a normalised copy. Throws on corruption. */
export function loadState(raw) {
  if (!raw || typeof raw !== 'object') throw new Error('state is not an object');
  if (!Array.isArray(raw.board) || raw.board.length !== ROWS) throw new Error('bad board');
  const board = raw.board.map((line) => {
    if (typeof line !== 'string' || line.length !== COLS) throw new Error('bad board row');
    return [...line].map((ch) => {
      if (!(ch in CHAR_CELL)) throw new Error('bad board cell');
      return CHAR_CELL[ch];
    });
  });
  // Gravity: no disc may float above an empty cell.
  for (let c = 0; c < COLS; c++) {
    for (let r = 0; r < ROWS - 1; r++) {
      if (board[r][c] !== EMPTY && board[r + 1][c] === EMPTY) throw new Error('floating disc');
    }
  }
  if (!STATUSES.includes(raw.status)) throw new Error('bad status');
  const win = findWin(board);
  if (raw.status === 'playing' && (win || isFull(board))) throw new Error('status contradicts board');
  if (raw.status === 'human_won' && win?.player !== HUMAN) throw new Error('status contradicts board');
  if (raw.status === 'bot_won' && win?.player !== BOT) throw new Error('status contradicts board');
  if (raw.status === 'draw' && !(isFull(board) && !win)) throw new Error('status contradicts board');

  const s = raw.stats ?? {};
  for (const k of ['games', 'humanWins', 'botWins', 'draws']) if (!isCount(s[k])) throw new Error('bad stats');
  if (!validCell(raw.lastMove ?? null) || !validCell(raw.botMove ?? null)) throw new Error('bad last move');

  const lastMove = raw.lastMove
    ? { col: raw.lastMove.col, row: raw.lastMove.row, by: parseLogin(raw.lastMove.by) }
    : null;
  const recent = (Array.isArray(raw.recent) ? raw.recent : []).map(parseLogin).filter(Boolean).slice(0, 5);

  return {
    version: 1,
    rev: isCount(raw.rev) ? raw.rev : 0,
    status: raw.status,
    turn: 'human',
    moves: countDiscs(board),
    board,
    lastMove,
    botMove: raw.botMove ? { col: raw.botMove.col, row: raw.botMove.row } : null,
    stats: { games: s.games, humanWins: s.humanWins, botWins: s.botWins, draws: s.draws },
    recent,
  };
}

// ---------------------------------------------------------------------------
// Game flow: one issue event in, new state + comment text out
// ---------------------------------------------------------------------------

const colName = (col) => `column ${col + 1}`;

function resultSentence(status) {
  if (status === 'human_won') return 'The visitors won this round!';
  if (status === 'bot_won') return 'The bot won this round.';
  if (status === 'draw') return 'The board is full: it is a draw.';
  return 'The game is on.';
}

function refusal(state, why) {
  return {
    changed: false,
    state,
    comment:
      `${why}\n\n` +
      `Nothing was changed. You can play from the board on my profile: ${PROFILE_URL}\n`,
  };
}

/**
 * Apply one issue to the game.
 * @param {object} state a state returned by initialState()/loadState()
 * @param {{title:string, author:string}} event raw (untrusted) issue data
 * @returns {{changed:boolean, state:object, comment:string}}
 */
export function handleEvent(state, event) {
  const action = parseTitle(event?.title);
  const login = parseLogin(event?.author); // null when invalid
  const isOwner = login !== null && login.toLowerCase() === OWNER.toLowerCase();
  const thanks = login ? `Thanks @${login}! ` : 'Thanks for playing! ';

  if (!action) {
    return refusal(
      state,
      'Hi! That issue title is not one I understand, so I left the game alone. ' +
        'Please use one of the column links under the board on my profile; they fill in the title for you.',
    );
  }

  if (action.type === 'new') {
    if (state.status === 'playing' && !isOwner) {
      return refusal(state, 'A game is still in progress, so a new one cannot be started yet. Finish this one first!');
    }
    const fresh = initialState(state.stats, state.recent);
    fresh.rev = state.rev + 1;
    return {
      changed: true,
      state: fresh,
      comment:
        `${thanks}A fresh game is ready: the board is empty and you are orange. ` +
        `Your move!\n\nPlay on my profile: ${PROFILE_URL}\n`,
    };
  }

  // action.type === 'move'
  if (state.status !== 'playing') {
    return refusal(state, `This game is already over (${resultSentence(state.status)}) Use "Start a new game" on my profile to play again.`);
  }
  if (dropRow(state.board, action.col) < 0) {
    return refusal(state, `${colName(action.col)} is full. Pick another column and try again.`);
  }

  const next = initialState(state.stats, state.recent);
  next.rev = state.rev + 1;
  next.board = cloneBoard(state.board);

  // Visitor's disc.
  const mine = drop(next.board, action.col, HUMAN);
  next.board = mine.board;
  next.lastMove = { col: action.col, row: mine.row, by: login };
  next.botMove = null;
  if (login) next.recent = [login, ...state.recent.filter((l) => l !== login)].slice(0, 5);

  let sentence = `${thanks}You dropped an orange disc in ${colName(action.col)}`;
  if (winsAt(next.board, mine.row, action.col)) {
    next.status = 'human_won';
    next.stats.games++;
    next.stats.humanWins++;
    sentence += ' and that makes four in a row. You win!';
  } else if (isFull(next.board)) {
    next.status = 'draw';
    next.stats.games++;
    next.stats.draws++;
    sentence += ' and that filled the board. It is a draw.';
  } else {
    // Bot reply.
    const botCol = chooseBotMove(next.board);
    const reply = drop(next.board, botCol, BOT);
    next.board = reply.board;
    next.botMove = { col: botCol, row: reply.row };
    sentence += ` and the bot answered in ${colName(botCol)}.`;
    if (winsAt(next.board, reply.row, botCol)) {
      next.status = 'bot_won';
      next.stats.games++;
      next.stats.botWins++;
      sentence += ' That is four in a row for the bot, so it takes this round.';
    } else if (isFull(next.board)) {
      next.status = 'draw';
      next.stats.games++;
      next.stats.draws++;
      sentence += ' That filled the board: it is a draw.';
    } else {
      sentence += ' The game is still on and it is your move.';
    }
  }
  next.moves = countDiscs(next.board);

  const over = next.status !== 'playing';
  const tail = over
    ? 'The game is over. Anyone can start a new one from the board on my profile.'
    : 'Come back and play again whenever you like.';
  return { changed: true, state: next, comment: `${sentence}\n\n${tail}\n\nSee the board: ${PROFILE_URL}\n` };
}

// ---------------------------------------------------------------------------
// Rendering: text description, SVG, README block
// ---------------------------------------------------------------------------

const cellWord = (v) => (v === HUMAN ? 'visitor' : 'bot');

/** Plain-words description of the position (used for SVG <desc> and image alt text). */
export function describe(state) {
  const parts = [
    'Connect 4 board with 7 columns and 6 rows. Visitors play orange and the bot plays the other colour.',
    `${state.moves} ${state.moves === 1 ? 'disc has' : 'discs have'} been played.`,
  ];
  const lastDisc = state.botMove ?? state.lastMove;
  if (lastDisc) parts.push(`The last disc went into ${colName(lastDisc.col)}.`);
  const cols = [];
  for (let c = 0; c < COLS; c++) {
    const stack = [];
    for (let r = ROWS - 1; r >= 0; r--) if (state.board[r][c] !== EMPTY) stack.push(cellWord(state.board[r][c]));
    cols.push(`${colName(c)}: ${stack.length ? stack.join(', ') : 'empty'}`);
  }
  parts.push(`From bottom to top, ${cols.join('; ')}.`);
  parts.push(
    state.status === 'playing'
      ? 'The game is in progress and it is the visitors\' turn.'
      : `${resultSentence(state.status)} The game is over.`,
  );
  return parts.join(' ');
}

const THEMES = {
  dark: {
    board: '#1a1712', border: '#2c2820', empty: '#12100c',
    human: '#ff7a18', humanRim: '#ffb347',
    bot: '#ece6d6', botRim: '#b9b09a',
    ring: '#ffb347', winLine: '#fffaf0', winCasing: '#12100c',
  },
  light: {
    board: '#fffaf0', border: '#d9d0bb', empty: '#efe8d8',
    human: '#d9600a', humanRim: '#f08a3c',
    bot: '#16140f', botRim: '#4a4538',
    ring: '#d9600a', winLine: '#16140f', winCasing: '#fffaf0',
  },
};

const PAD = 30;
const CELL = 100;
const SVG_W = PAD * 2 + COLS * CELL; // 760
const SVG_H = PAD * 2 + ROWS * CELL; // 660
const cx = (c) => PAD + CELL / 2 + c * CELL;
const cy = (r) => PAD + CELL / 2 + r * CELL;

const xmlEscape = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

function svgTitle(state) {
  if (state.status === 'human_won') return 'Connect 4: visitors won';
  if (state.status === 'bot_won') return 'Connect 4: the bot won';
  if (state.status === 'draw') return 'Connect 4: draw';
  return state.moves === 0 ? 'Connect 4: new game' : 'Connect 4: game in progress';
}

/** Render the board as a self-contained SVG string for the given theme. */
export function renderSvg(state, themeName) {
  const t = THEMES[themeName];
  if (!t) throw new Error(`unknown theme ${themeName}`);
  const win = findWin(state.board);
  const lastDisc = state.botMove ?? state.lastMove;

  const out = [];
  out.push(`<svg xmlns="http://www.w3.org/2000/svg" width="${SVG_W}" height="${SVG_H}" viewBox="0 0 ${SVG_W} ${SVG_H}" role="img" aria-labelledby="t d">`);
  out.push(`<title id="t">${xmlEscape(svgTitle(state))}</title>`);
  out.push(`<desc id="d">${xmlEscape(describe(state))}</desc>`);
  out.push(
    `<style>.e{fill:${t.empty}}` +
      `.h{fill:${t.human};stroke:${t.humanRim};stroke-width:4}` +
      `.b{fill:${t.bot};stroke:${t.botRim};stroke-width:4}` +
      `.i{fill:none;stroke-width:3;stroke-opacity:.45}` +
      `.h+.i{stroke:${t.humanRim}}.b+.i{stroke:${t.botRim}}</style>`,
  );
  out.push(`<rect x="4" y="4" width="${SVG_W - 8}" height="${SVG_H - 8}" rx="28" fill="${t.board}" stroke="${t.border}" stroke-width="4"/>`);
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      const v = state.board[r][c];
      if (v === EMPTY) {
        out.push(`<circle class="e" cx="${cx(c)}" cy="${cy(r)}" r="40"/>`);
      } else {
        const cls = v === HUMAN ? 'h' : 'b';
        out.push(`<circle class="e" cx="${cx(c)}" cy="${cy(r)}" r="40"/>`);
        out.push(`<circle class="${cls}" cx="${cx(c)}" cy="${cy(r)}" r="38"/>`);
        out.push(`<circle class="i" cx="${cx(c)}" cy="${cy(r)}" r="25"/>`);
      }
    }
  }
  if (lastDisc) {
    out.push(
      `<circle cx="${cx(lastDisc.col)}" cy="${cy(lastDisc.row)}" r="45" fill="none" stroke="${t.ring}" stroke-width="3">` +
        `<animate attributeName="opacity" values="1;0.25;1" dur="2.4s" repeatCount="indefinite"/></circle>`,
    );
  }
  if (win) {
    const [r1, c1] = win.cells[0];
    const [r2, c2] = win.cells[win.cells.length - 1];
    const coords = `x1="${cx(c1)}" y1="${cy(r1)}" x2="${cx(c2)}" y2="${cy(r2)}" stroke-linecap="round"`;
    out.push(`<line ${coords} stroke="${t.winCasing}" stroke-width="10" stroke-opacity=".7"/>`);
    out.push(`<line ${coords} stroke="${t.winLine}" stroke-width="5"/>`);
  }
  out.push('</svg>');
  return out.join('\n') + '\n';
}

/** Cache-buster for the README image URLs. rev rises with every move and every new game. */
export const cacheBuster = (state) => state.rev;

function moveUrl(n) {
  return (
    `${ISSUE_NEW_URL}?title=c4%7Cmove%7C${n}` +
    '&body=Just+press+%22Submit+new+issue%22.+The+move+is+played+automatically.'
  );
}
const NEW_GAME_URL = `${ISSUE_NEW_URL}?title=c4%7Cnew&body=Just+press+%22Submit+new+issue%22.`;

/** The markdown/HTML that lives between the C4 markers (markers excluded). */
export function renderReadmeBlock(state) {
  const v = cacheBuster(state);
  const alt = xmlEscape(describe(state));
  const lines = [];
  lines.push('<div align="center">', '');
  lines.push('<picture>');
  lines.push(`  <source media="(prefers-color-scheme: dark)" srcset="./assets/game/board-dark.svg?v=${v}">`);
  lines.push(`  <source media="(prefers-color-scheme: light)" srcset="./assets/game/board-light.svg?v=${v}">`);
  lines.push(`  <img alt="${alt}" src="./assets/game/board-light.svg?v=${v}" width="420">`);
  lines.push('</picture>', '');

  if (state.status === 'playing') {
    lines.push(state.moves === 0
      ? '**Your move!** You are orange and you go first. Pick a column to drop a disc.'
      : '**Your move!** You are orange. Pick a column to drop your disc.');
    lines.push('');
    const links = [];
    for (let c = 0; c < COLS; c++) {
      links.push(dropRow(state.board, c) >= 0 ? `[${c + 1}](${moveUrl(c + 1)})` : `${c + 1}`);
    }
    lines.push(links.join(' &nbsp;·&nbsp; '));
  } else {
    const result =
      state.status === 'human_won' ? '**Visitors win!** Four in a row for orange.'
        : state.status === 'bot_won' ? '**The bot wins this round.** Four in a row.'
          : '**It is a draw.** The board is full.';
    lines.push(result);
    lines.push('');
    lines.push(`[Start a new game](${NEW_GAME_URL})`);
  }
  lines.push('');

  const s = state.stats;
  let sub = `Games played ${s.games} · Visitor wins ${s.humanWins} · Bot wins ${s.botWins} · Draws ${s.draws}`;
  if (state.lastMove?.by) sub += ` · Last move by @${state.lastMove.by}`;
  lines.push(`<sub>${sub}</sub>`, '');
  lines.push('</div>');
  return lines.join('\n');
}

/**
 * Replace the block between the C4 markers. Returns the new text, or null when
 * the markers are missing or out of order (caller skips the update).
 */
export function injectReadme(readme, block) {
  const a = readme.indexOf(START_MARK);
  if (a < 0) return null;
  const b = readme.indexOf(END_MARK, a + START_MARK.length);
  if (b < 0) return null;
  return readme.slice(0, a + START_MARK.length) + '\n' + block + '\n' + readme.slice(b);
}

// ---------------------------------------------------------------------------
// CLI / file IO
// ---------------------------------------------------------------------------

/**
 * Run one event against the files under `root` (the repo root).
 * Writes game/state.json, assets/game/board-{dark,light}.svg, README.md (if it
 * has markers) and game/out.md.
 */
export function run({ title, author, root }) {
  const statePath = join(root, 'game', 'state.json');
  const outPath = join(root, 'game', 'out.md');
  const readmePath = join(root, 'README.md');
  const svgDir = join(root, 'assets', 'game');

  const state = loadState(JSON.parse(readFileSync(statePath, 'utf8')));
  const result = handleEvent(state, { title, author });

  const final = result.state;
  // Write everything derived from the (possibly unchanged) state; output is
  // deterministic so unchanged state produces no git diff.
  mkdirSync(svgDir, { recursive: true });
  writeFileSync(join(svgDir, 'board-dark.svg'), renderSvg(final, 'dark'));
  writeFileSync(join(svgDir, 'board-light.svg'), renderSvg(final, 'light'));

  let readmeUpdated = false;
  if (existsSync(readmePath)) {
    const current = readFileSync(readmePath, 'utf8');
    const updated = injectReadme(current, renderReadmeBlock(final));
    if (updated !== null) {
      if (updated !== current) writeFileSync(readmePath, updated);
      readmeUpdated = true;
    }
  }

  if (result.changed) writeFileSync(statePath, serializeState(final));
  writeFileSync(outPath, result.comment);
  return { changed: result.changed, readmeUpdated, comment: result.comment, state: final };
}

function main() {
  const here = dirname(fileURLToPath(import.meta.url));
  const root = resolve(process.env.C4_ROOT || join(here, '..'));
  try {
    const res = run({
      title: process.env.ISSUE_TITLE ?? '',
      author: process.env.ISSUE_AUTHOR ?? '',
      root,
    });
    // Only safe, fixed-format facts go to the log.
    console.log(`connect4: changed=${res.changed} status=${res.state.status} moves=${res.state.moves} readme=${res.readmeUpdated}`);
  } catch (err) {
    console.error(`connect4: failed: ${err?.message ?? 'unknown error'}`);
    try {
      writeFileSync(
        join(root, 'game', 'out.md'),
        `Sorry, something went wrong while playing that move, and the game was not changed. Please try again in a moment.\n\n${PROFILE_URL}\n`,
      );
    } catch {
      /* nothing more we can do */
    }
    process.exitCode = 1;
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main();
