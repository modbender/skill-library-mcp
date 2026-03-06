#!/usr/bin/env node

import { randomUUID } from "node:crypto";
import { mkdirSync } from "node:fs";
import { DatabaseSync } from "node:sqlite";
import { homedir } from "node:os";
import { dirname, resolve } from "node:path";

type Side = "LONG" | "SHORT";
type EventType = "OPEN" | "CLOSE" | "LEVELS" | "NOTE";

type CliMap = {
  _: string[];
  [key: string]: string | boolean | string[];
};

type Position = {
  symbol: string;
  mint: string | null;
  side: Side;
  qty: number;
  avgEntry: number;
  openFeesRemaining: number;
  stopPrice: number | null;
  takePrice: number | null;
};

type TradeMetrics = {
  realizedPnl: number;
  closedCount: number;
  wins: number;
  losses: number;
};

const DEFAULT_DB = `${homedir()}/.openclaw/paper-trading.db`;

function normalizeMint(v: unknown): string | undefined {
  if (typeof v !== "string") {
    return undefined;
  }
  const trimmed = v.trim();
  return trimmed ? trimmed : undefined;
}

function marketKey(symbol: string, mint?: string | null): string {
  return `${symbol.toUpperCase()}|${mint ?? ""}`;
}

function positionKey(symbol: string, side: Side, mint?: string | null): string {
  return `${symbol.toUpperCase()}:${side}:${mint ?? ""}`;
}

function ensureColumn(db: DatabaseSync, table: string, column: string, ddl: string): void {
  const cols = db.prepare(`PRAGMA table_info(${table})`).all() as Array<{ name: string }>;
  if (!cols.some((c) => c.name === column)) {
    db.exec(`ALTER TABLE ${table} ADD COLUMN ${column} ${ddl}`);
  }
}

function nowIso(): string {
  return new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
}

function parseArgs(argv: string[]): CliMap {
  const out: CliMap = { _: [] };
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith("--")) {
      out._.push(token);
      continue;
    }

    const key = token.slice(2);
    const next = argv[i + 1];
    if (!next || next.startsWith("--")) {
      out[key] = true;
      continue;
    }

    if (key === "tags") {
      const tags: string[] = [];
      let j = i + 1;
      while (j < argv.length && !argv[j].startsWith("--")) {
        tags.push(argv[j]);
        j += 1;
      }
      out[key] = tags;
      i = j - 1;
      continue;
    }

    out[key] = next;
    i += 1;
  }
  return out;
}

function asString(v: unknown, field: string): string {
  if (typeof v !== "string" || !v.trim()) {
    throw new Error(`${field} is required`);
  }
  return v.trim();
}

function asNumber(v: unknown, field: string): number {
  const n = Number(v);
  if (!Number.isFinite(n)) {
    throw new Error(`${field} must be a number`);
  }
  return n;
}

function parseSide(v: unknown): Side {
  const side = asString(v, "side").toUpperCase();
  if (side !== "LONG" && side !== "SHORT") {
    throw new Error("side must be LONG or SHORT");
  }
  return side;
}

function getDbPath(args: CliMap): string {
  const raw = (args.db as string | undefined) ?? DEFAULT_DB;
  return resolve(raw.replace(/^~\//, `${homedir()}/`));
}

function openDb(path: string): DatabaseSync {
  mkdirSync(dirname(path), { recursive: true });
  const db = new DatabaseSync(path);
  db.exec("PRAGMA foreign_keys = ON;");
  db.exec(`
    CREATE TABLE IF NOT EXISTS accounts (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      base_currency TEXT NOT NULL DEFAULT 'USD',
      starting_balance REAL NOT NULL,
      created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS events (
      id TEXT PRIMARY KEY,
      account_id TEXT NOT NULL,
      type TEXT NOT NULL,
      symbol TEXT,
      mint TEXT,
      side TEXT,
      qty REAL,
      price REAL,
      fee REAL NOT NULL DEFAULT 0,
      stop_price REAL,
      take_price REAL,
      note TEXT,
      meta_json TEXT,
      created_at TEXT NOT NULL,
      FOREIGN KEY(account_id) REFERENCES accounts(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_events_account_time ON events(account_id, created_at);

    CREATE TABLE IF NOT EXISTS price_snapshots (
      id TEXT PRIMARY KEY,
      symbol TEXT NOT NULL,
      mint TEXT,
      price REAL NOT NULL,
      source TEXT NOT NULL,
      captured_at TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_snapshots_symbol_time ON price_snapshots(symbol, captured_at DESC);
  `);
  ensureColumn(db, "events", "mint", "TEXT");
  ensureColumn(db, "price_snapshots", "mint", "TEXT");
  db.exec(
    "CREATE INDEX IF NOT EXISTS idx_snapshots_symbol_mint_time ON price_snapshots(symbol, mint, captured_at DESC)"
  );
  return db;
}

function requireAccount(
  db: DatabaseSync,
  accountId: string,
): { id: string; name: string; base_currency: string; starting_balance: number; created_at: string } {
  const row = db
    .prepare("SELECT id, name, base_currency, starting_balance, created_at FROM accounts WHERE id = ?")
    .get(accountId) as
    | { id: string; name: string; base_currency: string; starting_balance: number; created_at: string }
    | undefined;

  if (!row) {
    throw new Error(`account '${accountId}' not found; run init first`);
  }
  return row;
}

function addEvent(
  db: DatabaseSync,
  params: {
    accountId: string;
    type: EventType;
    symbol?: string;
    mint?: string;
    side?: Side;
    qty?: number;
    price?: number;
    fee?: number;
    stopPrice?: number | null;
    takePrice?: number | null;
    note?: string;
    meta?: Record<string, unknown>;
  },
): string {
  const id = randomUUID();
  db.prepare(
    `INSERT INTO events (
      id, account_id, type, symbol, mint, side, qty, price, fee, stop_price, take_price, note, meta_json, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
  ).run(
    id,
    params.accountId,
    params.type,
    params.symbol ? params.symbol.toUpperCase() : null,
    params.mint ?? null,
    params.side ?? null,
    params.qty ?? null,
    params.price ?? null,
    params.fee ?? 0,
    params.stopPrice ?? null,
    params.takePrice ?? null,
    params.note ?? null,
    params.meta ? JSON.stringify(params.meta) : null,
    nowIso(),
  );
  return id;
}

function replay(db: DatabaseSync, accountId: string): { positions: Map<string, Position>; metrics: TradeMetrics } {
  const events = db
    .prepare(
      "SELECT type, symbol, mint, side, qty, price, fee, stop_price, take_price FROM events WHERE account_id = ? ORDER BY created_at ASC, rowid ASC",
    )
    .all(accountId) as Array<{
    type: EventType;
    symbol: string | null;
    mint: string | null;
    side: Side | null;
    qty: number | null;
    price: number | null;
    fee: number | null;
    stop_price: number | null;
    take_price: number | null;
  }>;

  const positions = new Map<string, Position>();
  const metrics: TradeMetrics = { realizedPnl: 0, closedCount: 0, wins: 0, losses: 0 };

  for (const e of events) {
    const symbol = (e.symbol ?? "").toUpperCase();
    const side = e.side;
    if (!symbol || (side !== "LONG" && side !== "SHORT")) {
      continue;
    }

    const key = positionKey(symbol, side, e.mint);

    if (e.type === "OPEN") {
      const qty = Number(e.qty ?? 0);
      const price = Number(e.price ?? 0);
      const fee = Number(e.fee ?? 0);
      if (qty <= 0 || price <= 0) {
        continue;
      }

      const existing = positions.get(key);
      if (!existing) {
        positions.set(key, {
          symbol,
          mint: e.mint,
          side,
          qty,
          avgEntry: price,
          openFeesRemaining: fee,
          stopPrice: e.stop_price,
          takePrice: e.take_price,
        });
        continue;
      }

      const nextQty = existing.qty + qty;
      existing.avgEntry = (existing.avgEntry * existing.qty + price * qty) / nextQty;
      existing.qty = nextQty;
      existing.openFeesRemaining += fee;
      if (e.stop_price != null) {
        existing.stopPrice = e.stop_price;
      }
      if (e.take_price != null) {
        existing.takePrice = e.take_price;
      }
      continue;
    }

    if (e.type === "LEVELS") {
      const pos = positions.get(key);
      if (!pos) {
        continue;
      }
      if (e.stop_price != null) {
        pos.stopPrice = e.stop_price;
      }
      if (e.take_price != null) {
        pos.takePrice = e.take_price;
      }
      continue;
    }

    if (e.type === "CLOSE") {
      const pos = positions.get(key);
      if (!pos) {
        continue;
      }

      const qty = Number(e.qty ?? 0);
      const price = Number(e.price ?? 0);
      const closeFee = Number(e.fee ?? 0);
      if (qty <= 0 || price <= 0 || pos.qty <= 0) {
        continue;
      }

      const closeQty = Math.min(qty, pos.qty);
      if (closeQty <= 0) {
        continue;
      }

      let feeAlloc = 0;
      if (pos.openFeesRemaining > 0 && pos.qty > 0) {
        feeAlloc = pos.openFeesRemaining * (closeQty / pos.qty);
        pos.openFeesRemaining -= feeAlloc;
      }

      const pnl =
        side === "LONG"
          ? (price - pos.avgEntry) * closeQty - feeAlloc - closeFee
          : (pos.avgEntry - price) * closeQty - feeAlloc - closeFee;

      metrics.realizedPnl += pnl;
      metrics.closedCount += 1;
      if (pnl > 0) {
        metrics.wins += 1;
      } else if (pnl < 0) {
        metrics.losses += 1;
      }

      pos.qty -= closeQty;
      if (pos.qty <= 1e-12) {
        positions.delete(key);
      }
    }
  }

  return { positions, metrics };
}

function latestPrices(db: DatabaseSync): Map<string, number> {
  const rows = db
    .prepare(`
      SELECT p.symbol, p.mint, p.price
      FROM price_snapshots p
      JOIN (
        SELECT symbol, mint, MAX(captured_at) AS max_captured
        FROM price_snapshots
        GROUP BY symbol, mint
      ) latest
        ON latest.symbol = p.symbol
       AND latest.mint IS p.mint
       AND latest.max_captured = p.captured_at
    `)
    .all() as Array<{ symbol: string; mint: string | null; price: number }>;

  const out = new Map<string, number>();
  for (const row of rows) {
    out.set(marketKey(row.symbol, row.mint), Number(row.price));
  }
  return out;
}

function unrealizedPnl(positions: Map<string, Position>, marks: Map<string, number>): number {
  let total = 0;
  for (const p of positions.values()) {
    const mark = marks.get(marketKey(p.symbol, p.mint));
    if (mark == null) {
      continue;
    }
    total +=
      p.side === "LONG"
        ? (mark - p.avgEntry) * p.qty - p.openFeesRemaining
        : (p.avgEntry - mark) * p.qty - p.openFeesRemaining;
  }
  return total;
}

function validateTrade(symbol: string, side: Side, qty: number, price: number, fee: number): void {
  if (!symbol.trim()) {
    throw new Error("symbol is required");
  }
  if (side !== "LONG" && side !== "SHORT") {
    throw new Error("side must be LONG or SHORT");
  }
  if (!Number.isFinite(qty) || qty <= 0) {
    throw new Error("qty must be > 0");
  }
  if (!Number.isFinite(price) || price <= 0) {
    throw new Error("price must be > 0");
  }
  if (!Number.isFinite(fee) || fee < 0) {
    throw new Error("fee must be >= 0");
  }
}

function riskCheck(params: {
  maxRiskPct?: number;
  stopPrice?: number;
  side: Side;
  qty: number;
  entryPrice: number;
  fee: number;
  equity: number;
}): void {
  if (params.maxRiskPct == null) {
    return;
  }
  if (params.equity <= 0) {
    throw new Error("cannot apply risk guard with non-positive equity");
  }
  if (params.stopPrice == null) {
    throw new Error("--stop-price is required when --max-risk-pct is set");
  }

  const perUnitRisk =
    params.side === "LONG"
      ? params.entryPrice - params.stopPrice
      : params.stopPrice - params.entryPrice;
  if (perUnitRisk < 0) {
    throw new Error("stop price invalid for side/entry");
  }

  const totalRisk = perUnitRisk * params.qty + params.fee;
  const pct = (totalRisk / params.equity) * 100;
  if (pct > params.maxRiskPct) {
    throw new Error(`risk ${pct.toFixed(2)}% exceeds max ${params.maxRiskPct.toFixed(2)}%`);
  }
}

function cmdInit(db: DatabaseSync, args: CliMap): void {
  const account = (args.account as string) ?? "main";
  const name = (args.name as string) ?? "Main Paper Account";
  const baseCurrency = ((args["base-currency"] as string) ?? "USD").toUpperCase();
  const startingBalance = asNumber(args["starting-balance"], "starting-balance");

  const exists = db.prepare("SELECT 1 AS ok FROM accounts WHERE id = ?").get(account) as
    | { ok: 1 }
    | undefined;
  if (exists) {
    throw new Error(`account '${account}' already exists`);
  }

  db.prepare(
    "INSERT INTO accounts (id, name, base_currency, starting_balance, created_at) VALUES (?, ?, ?, ?, ?)"
  ).run(account, name, baseCurrency, startingBalance, nowIso());

  console.log(`initialized account=${account}`);
}

function cmdOpen(db: DatabaseSync, args: CliMap): void {
  const accountId = (args.account as string) ?? "main";
  const symbol = asString(args.symbol, "symbol").toUpperCase();
  const mint = normalizeMint(args.mint);
  const side = parseSide(args.side);
  const qty = asNumber(args.qty, "qty");
  const price = asNumber(args.price, "price");
  const fee = asNumber(args.fee ?? 0, "fee");
  const stopPrice = args["stop-price"] == null ? undefined : asNumber(args["stop-price"], "stop-price");
  const takePrice = args["take-price"] == null ? undefined : asNumber(args["take-price"], "take-price");
  const maxRiskPct =
    args["max-risk-pct"] == null ? undefined : asNumber(args["max-risk-pct"], "max-risk-pct");
  const note = typeof args.note === "string" ? args.note : undefined;

  validateTrade(symbol, side, qty, price, fee);

  const account = requireAccount(db, accountId);
  const { positions, metrics } = replay(db, accountId);
  const marks = latestPrices(db);
  const equity = Number(account.starting_balance) + metrics.realizedPnl + unrealizedPnl(positions, marks);

  riskCheck({
    maxRiskPct,
    stopPrice,
    side,
    qty,
    entryPrice: price,
    fee,
    equity,
  });

  const id = addEvent(db, {
    accountId,
    type: "OPEN",
    symbol,
    mint,
    side,
    qty,
    price,
    fee,
    stopPrice: stopPrice ?? null,
    takePrice: takePrice ?? null,
    note,
    meta: { command: "open" },
  });

  const mintSuffix = mint ? ` mint=${mint}` : "";
  console.log(`opened event=${id} ${side} ${qty} ${symbol}${mintSuffix} @ ${price}`);
}

function cmdClose(db: DatabaseSync, args: CliMap): void {
  const accountId = (args.account as string) ?? "main";
  const symbol = asString(args.symbol, "symbol").toUpperCase();
  const mint = normalizeMint(args.mint);
  const side = parseSide(args.side);
  const qty = asNumber(args.qty, "qty");
  const price = asNumber(args.price, "price");
  const fee = asNumber(args.fee ?? 0, "fee");
  const note = typeof args.note === "string" ? args.note : undefined;

  validateTrade(symbol, side, qty, price, fee);
  requireAccount(db, accountId);

  const { positions } = replay(db, accountId);
  const existing = positions.get(positionKey(symbol, side, mint));
  if (!existing || existing.qty <= 0) {
    throw new Error(`no open ${side} position for ${symbol}`);
  }

  const id = addEvent(db, {
    accountId,
    type: "CLOSE",
    symbol,
    mint,
    side,
    qty,
    price,
    fee,
    note,
    meta: { command: "close" },
  });

  const mintSuffix = mint ? ` mint=${mint}` : "";
  console.log(`closed event=${id} ${side} ${qty} ${symbol}${mintSuffix} @ ${price}`);
}

function cmdSetLevels(db: DatabaseSync, args: CliMap): void {
  const accountId = (args.account as string) ?? "main";
  const symbol = asString(args.symbol, "symbol").toUpperCase();
  const mint = normalizeMint(args.mint);
  const side = parseSide(args.side);
  const stopPrice = args["stop-price"] == null ? undefined : asNumber(args["stop-price"], "stop-price");
  const takePrice = args["take-price"] == null ? undefined : asNumber(args["take-price"], "take-price");
  const note = typeof args.note === "string" ? args.note : undefined;

  if (stopPrice == null && takePrice == null) {
    throw new Error("set-levels requires --stop-price and/or --take-price");
  }

  requireAccount(db, accountId);
  const { positions } = replay(db, accountId);
  if (!positions.has(positionKey(symbol, side, mint))) {
    throw new Error(`no open ${side} position for ${symbol}`);
  }

  const id = addEvent(db, {
    accountId,
    type: "LEVELS",
    symbol,
    mint,
    side,
    stopPrice: stopPrice ?? null,
    takePrice: takePrice ?? null,
    note,
    meta: { command: "set-levels" },
  });

  const mintSuffix = mint ? ` mint=${mint}` : "";
  console.log(`updated levels event=${id} ${side} ${symbol}${mintSuffix}`);
}

function cmdNote(db: DatabaseSync, args: CliMap): void {
  const accountId = (args.account as string) ?? "main";
  const note = asString(args.note, "note");
  const symbol = typeof args.symbol === "string" ? args.symbol.toUpperCase() : undefined;
  const mint = normalizeMint(args.mint);
  const side = args.side ? parseSide(args.side) : undefined;
  const tags = Array.isArray(args.tags) ? args.tags : [];

  requireAccount(db, accountId);
  const id = addEvent(db, {
    accountId,
    type: "NOTE",
    symbol,
    mint,
    side,
    note,
    meta: { command: "note", tags },
  });

  console.log(`saved note event=${id}`);
}

function cmdSnapshot(db: DatabaseSync, args: CliMap): void {
  const symbol = asString(args.symbol, "symbol").toUpperCase();
  const mint = normalizeMint(args.mint);
  const price = asNumber(args.price, "price");
  const source = (args.source as string) ?? "manual";

  db.prepare("INSERT INTO price_snapshots (id, symbol, mint, price, source, captured_at) VALUES (?, ?, ?, ?, ?, ?)").run(
    randomUUID(),
    symbol,
    mint ?? null,
    price,
    source,
    nowIso(),
  );

  const mintSuffix = mint ? ` mint=${mint}` : "";
  console.log(`snapshot ${symbol}${mintSuffix}=${price} source=${source}`);
}

function buildStatus(db: DatabaseSync, accountId: string) {
  const account = requireAccount(db, accountId);
  const { positions, metrics } = replay(db, accountId);
  const marks = latestPrices(db);
  const unrealized = unrealizedPnl(positions, marks);
  const starting = Number(account.starting_balance);
  const equity = starting + metrics.realizedPnl + unrealized;
  const winRate = metrics.closedCount > 0 ? (metrics.wins / metrics.closedCount) * 100 : null;

  const rows = [...positions.values()]
    .sort((a, b) => `${a.symbol}:${a.side}:${a.mint ?? ""}`.localeCompare(`${b.symbol}:${b.side}:${b.mint ?? ""}`))
    .map((p) => {
      const mark = marks.get(marketKey(p.symbol, p.mint)) ?? null;
      const unreal =
        mark == null
          ? null
          : p.side === "LONG"
            ? (mark - p.avgEntry) * p.qty - p.openFeesRemaining
            : (p.avgEntry - mark) * p.qty - p.openFeesRemaining;

      return {
        symbol: p.symbol,
        mint: p.mint,
        side: p.side,
        qty: p.qty,
        avgEntry: p.avgEntry,
        mark,
        stopPrice: p.stopPrice,
        takePrice: p.takePrice,
        openFeesRemaining: p.openFeesRemaining,
        unrealizedPnl: unreal,
      };
    });

  return {
    account: {
      id: account.id,
      name: account.name,
      baseCurrency: account.base_currency,
      startingBalance: starting,
      createdAt: account.created_at,
    },
    summary: {
      realizedPnl: metrics.realizedPnl,
      unrealizedPnl: unrealized,
      equity,
      openPositions: rows.length,
      closedTrades: metrics.closedCount,
      wins: metrics.wins,
      losses: metrics.losses,
      winRate,
    },
    positions: rows,
  };
}

function cmdStatus(db: DatabaseSync, args: CliMap): void {
  const accountId = (args.account as string) ?? "main";
  const format = (args.format as string) ?? "text";
  const pretty = Boolean(args.pretty);
  const payload = buildStatus(db, accountId);

  if (format === "json") {
    console.log(JSON.stringify(payload, null, pretty ? 2 : undefined));
    return;
  }

  const s = payload.summary;
  console.log(`account=${payload.account.id} equity=${s.equity.toFixed(2)}`);
  console.log(
    `realized=${s.realizedPnl.toFixed(2)} unrealized=${s.unrealizedPnl.toFixed(2)} open=${s.openPositions} closed=${s.closedTrades}`,
  );
  if (s.winRate != null) {
    console.log(`win_rate=${s.winRate.toFixed(2)}% (${s.wins}/${s.closedTrades})`);
  }
  if (payload.positions.length > 0) {
    console.log("positions:");
    for (const p of payload.positions) {
      const mark = p.mark == null ? "n/a" : p.mark.toFixed(4);
      const unreal = p.unrealizedPnl == null ? "n/a" : p.unrealizedPnl.toFixed(2);
      const stop = p.stopPrice == null ? "n/a" : p.stopPrice.toFixed(4);
      const take = p.takePrice == null ? "n/a" : p.takePrice.toFixed(4);
      const mintSuffix = p.mint ? ` mint=${p.mint}` : "";
      console.log(
        `- ${p.symbol}${mintSuffix} ${p.side} qty=${p.qty.toFixed(6)} avg=${p.avgEntry.toFixed(4)} mark=${mark} unreal=${unreal} stop=${stop} take=${take}`,
      );
    }
  }
}

function cmdReview(db: DatabaseSync, args: CliMap): void {
  const accountId = (args.account as string) ?? "main";
  const limit = Number(args["note-limit"] ?? 10);
  const format = (args.format as string) ?? "text";
  const pretty = Boolean(args.pretty);

  const payload = buildStatus(db, accountId);
  const notes = db
    .prepare(
      "SELECT note, created_at, symbol, side FROM events WHERE account_id = ? AND type = 'NOTE' ORDER BY created_at DESC LIMIT ?",
    )
    .all(accountId, limit) as Array<{ note: string; created_at: string; symbol: string | null; side: Side | null }>;

  const expectancy =
    payload.summary.closedTrades > 0 ? payload.summary.realizedPnl / payload.summary.closedTrades : 0;

  const out = {
    summary: payload.summary,
    expectancyPerTrade: expectancy,
    recentNotes: notes.map((n) => ({
      createdAt: n.created_at,
      symbol: n.symbol,
      side: n.side,
      note: n.note,
    })),
  };

  if (format === "json") {
    console.log(JSON.stringify(out, null, pretty ? 2 : undefined));
    return;
  }

  console.log(`closed_trades=${payload.summary.closedTrades} realized=${payload.summary.realizedPnl.toFixed(2)}`);
  console.log(`expectancy_per_trade=${expectancy.toFixed(2)}`);
  if (payload.summary.winRate != null) {
    console.log(
      `win_rate=${payload.summary.winRate.toFixed(2)}% wins=${payload.summary.wins} losses=${payload.summary.losses}`,
    );
  }
  if (out.recentNotes.length > 0) {
    console.log("recent_notes:");
    for (const n of out.recentNotes) {
      console.log(`- ${n.createdAt} ${n.symbol ?? "-"} ${n.side ?? "-"}: ${n.note}`);
    }
  }
}

function printHelp(): void {
  console.log(`paper_trading.ts - SQLite-backed paper trading CLI\n
Usage:
  node --experimental-strip-types paper_trading.ts [--db <path>] <command> [options]

Commands:
  init --starting-balance <n> [--account main] [--name <name>] [--base-currency USD]
  snapshot --symbol <sym> [--mint <address>] --price <n> [--source manual]
  open --symbol <sym> [--mint <address>] --side LONG|SHORT --qty <n> --price <n> [--fee 0] [--stop-price <n>] [--take-price <n>] [--max-risk-pct <n>] [--note <text>] [--account main]
  close --symbol <sym> [--mint <address>] --side LONG|SHORT --qty <n> --price <n> [--fee 0] [--note <text>] [--account main]
  set-levels --symbol <sym> [--mint <address>] --side LONG|SHORT [--stop-price <n>] [--take-price <n>] [--note <text>] [--account main]
  note --note <text> [--symbol <sym>] [--mint <address>] [--side LONG|SHORT] [--tags t1 t2 ...] [--account main]
  status [--account main] [--format text|json] [--pretty]
  review [--account main] [--note-limit 10] [--format text|json] [--pretty]
`);
}

function main(): void {
  const args = parseArgs(process.argv.slice(2));
  const command = args._[0];

  if (!command || command === "help" || command === "--help") {
    printHelp();
    return;
  }

  const db = openDb(getDbPath(args));
  try {
    switch (command) {
      case "init":
        cmdInit(db, args);
        break;
      case "open":
        cmdOpen(db, args);
        break;
      case "close":
        cmdClose(db, args);
        break;
      case "set-levels":
        cmdSetLevels(db, args);
        break;
      case "note":
        cmdNote(db, args);
        break;
      case "snapshot":
        cmdSnapshot(db, args);
        break;
      case "status":
        cmdStatus(db, args);
        break;
      case "review":
        cmdReview(db, args);
        break;
      default:
        throw new Error(`unknown command: ${command}`);
    }
  } finally {
    db.close();
  }
}

try {
  main();
} catch (error) {
  const msg = error instanceof Error ? error.message : String(error);
  console.error(`error: ${msg}`);
  process.exit(1);
}
