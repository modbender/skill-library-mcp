import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { DatabaseSync } from 'node:sqlite';

const __dirname = dirname(fileURLToPath(import.meta.url));
const scriptPath = resolve(__dirname, '../scripts/paper_trading.ts');

function mkTmpDbPath(prefix = 'paper-trading-test-') {
  const dir = mkdtempSync(join(tmpdir(), prefix));
  return { dir, db: join(dir, 'paper.db') };
}

function runCli(args, dbPath) {
  const res = spawnSync(
    process.execPath,
    ['--experimental-strip-types', scriptPath, '--db', dbPath, ...args],
    { encoding: 'utf8' },
  );
  return {
    code: res.status ?? 1,
    stdout: res.stdout ?? '',
    stderr: res.stderr ?? '',
  };
}

function runOk(args, dbPath) {
  const out = runCli(args, dbPath);
  assert.equal(out.code, 0, `Expected success. stderr:\n${out.stderr}\nstdout:\n${out.stdout}`);
  return out;
}

function runFail(args, dbPath) {
  const out = runCli(args, dbPath);
  assert.notEqual(out.code, 0, `Expected failure. stdout:\n${out.stdout}`);
  return out;
}

function parseJsonStdout(stdout) {
  return JSON.parse(stdout.trim());
}

test('init creates account and duplicate init fails', () => {
  const { dir, db } = mkTmpDbPath();
  try {
    runOk(['init', '--account', 'main', '--starting-balance', '10000'], db);
    const dup = runFail(['init', '--account', 'main', '--starting-balance', '10000'], db);
    assert.match(dup.stderr, /already exists/);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('open requires symbol', () => {
  const { dir, db } = mkTmpDbPath();
  try {
    runOk(['init', '--starting-balance', '10000'], db);
    const out = runFail(['open', '--side', 'LONG', '--qty', '1', '--price', '10'], db);
    assert.match(out.stderr, /symbol is required/);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('symbol-only lifecycle computes realized and unrealized pnl', () => {
  const { dir, db } = mkTmpDbPath();
  try {
    runOk(['init', '--starting-balance', '10000'], db);
    runOk(['snapshot', '--symbol', 'BTC', '--price', '62000', '--source', 'test'], db);
    runOk(
      [
        'open',
        '--symbol',
        'BTC',
        '--side',
        'LONG',
        '--qty',
        '0.1',
        '--price',
        '62000',
        '--fee',
        '2',
        '--stop-price',
        '61000',
        '--max-risk-pct',
        '2',
      ],
      db,
    );
    runOk(['snapshot', '--symbol', 'BTC', '--price', '63000', '--source', 'test'], db);
    runOk(['close', '--symbol', 'BTC', '--side', 'LONG', '--qty', '0.05', '--price', '63100', '--fee', '1'], db);

    const status = runOk(['status', '--format', 'json', '--pretty'], db);
    const payload = parseJsonStdout(status.stdout);

    assert.equal(payload.summary.realizedPnl, 53);
    assert.equal(payload.summary.unrealizedPnl, 49);
    assert.equal(payload.summary.openPositions, 1);
    assert.equal(payload.positions[0].symbol, 'BTC');
    assert.equal(payload.positions[0].mint, null);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('mint is optional and separates same-symbol positions', () => {
  const { dir, db } = mkTmpDbPath();
  const mintA = 'MintA11111111111111111111111111111111111';
  const mintB = 'MintB22222222222222222222222222222222222';
  try {
    runOk(['init', '--starting-balance', '10000'], db);

    runOk(['snapshot', '--symbol', 'BTC', '--mint', mintA, '--price', '62000', '--source', 'test'], db);
    runOk(['snapshot', '--symbol', 'BTC', '--mint', mintB, '--price', '50000', '--source', 'test'], db);

    runOk(['open', '--symbol', 'BTC', '--mint', mintA, '--side', 'LONG', '--qty', '1', '--price', '62000'], db);
    runOk(['open', '--symbol', 'BTC', '--mint', mintB, '--side', 'LONG', '--qty', '1', '--price', '50000'], db);

    const status = runOk(['status', '--format', 'json'], db);
    const payload = parseJsonStdout(status.stdout);

    assert.equal(payload.summary.openPositions, 2);
    const byMint = new Map(payload.positions.map((p) => [p.mint, p]));
    assert.equal(byMint.get(mintA).mark, 62000);
    assert.equal(byMint.get(mintB).mark, 50000);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('close fails when mint does not match open position', () => {
  const { dir, db } = mkTmpDbPath();
  const mintA = 'MintA11111111111111111111111111111111111';
  const mintB = 'MintB22222222222222222222222222222222222';
  try {
    runOk(['init', '--starting-balance', '10000'], db);
    runOk(['open', '--symbol', 'BTC', '--mint', mintA, '--side', 'LONG', '--qty', '1', '--price', '62000'], db);
    const out = runFail(['close', '--symbol', 'BTC', '--mint', mintB, '--side', 'LONG', '--qty', '1', '--price', '62000'], db);
    assert.match(out.stderr, /no open LONG position for BTC/);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('set-levels updates levels for targeted symbol+mint position', () => {
  const { dir, db } = mkTmpDbPath();
  const mintA = 'MintA11111111111111111111111111111111111';
  try {
    runOk(['init', '--starting-balance', '10000'], db);
    runOk(['open', '--symbol', 'BTC', '--mint', mintA, '--side', 'LONG', '--qty', '1', '--price', '62000'], db);
    runOk(['set-levels', '--symbol', 'BTC', '--mint', mintA, '--side', 'LONG', '--stop-price', '61500', '--take-price', '64000'], db);

    const status = runOk(['status', '--format', 'json'], db);
    const payload = parseJsonStdout(status.stdout);
    assert.equal(payload.positions[0].stopPrice, 61500);
    assert.equal(payload.positions[0].takePrice, 64000);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('migrates legacy db without mint columns', () => {
  const { dir, db } = mkTmpDbPath();
  try {
    const legacy = new DatabaseSync(db);
    legacy.exec(`
      CREATE TABLE accounts (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        base_currency TEXT NOT NULL DEFAULT 'USD',
        starting_balance REAL NOT NULL,
        created_at TEXT NOT NULL
      );
      CREATE TABLE events (
        id TEXT PRIMARY KEY,
        account_id TEXT NOT NULL,
        type TEXT NOT NULL,
        symbol TEXT,
        side TEXT,
        qty REAL,
        price REAL,
        fee REAL NOT NULL DEFAULT 0,
        stop_price REAL,
        take_price REAL,
        note TEXT,
        meta_json TEXT,
        created_at TEXT NOT NULL
      );
      CREATE TABLE price_snapshots (
        id TEXT PRIMARY KEY,
        symbol TEXT NOT NULL,
        price REAL NOT NULL,
        source TEXT NOT NULL,
        captured_at TEXT NOT NULL
      );
    `);
    legacy.close();

    runOk(['init', '--starting-balance', '10000'], db);
    runOk(['snapshot', '--symbol', 'BTC', '--mint', 'MintLegacy3333333333333333333333333333333', '--price', '62000'], db);

    const verify = new DatabaseSync(db);
    const eventCols = verify.prepare('PRAGMA table_info(events)').all();
    const snapCols = verify.prepare('PRAGMA table_info(price_snapshots)').all();
    verify.close();

    assert.ok(eventCols.some((c) => c.name === 'mint'));
    assert.ok(snapCols.some((c) => c.name === 'mint'));
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});
