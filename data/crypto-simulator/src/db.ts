import fs from 'node:fs';
import path from 'node:path';
import DatabaseConstructor, { Database as BetterSqliteDatabase } from 'better-sqlite3';
import { CoinId, CoinPriceRow, StrategyName } from './types';

const DEFAULT_DB_PATH = path.resolve(process.cwd(), 'data', 'simulator.db');
const DB_PATH = process.env.SIMULATOR_DB_PATH
  ? path.resolve(process.env.SIMULATOR_DB_PATH)
  : DEFAULT_DB_PATH;

fs.mkdirSync(path.dirname(DB_PATH), { recursive: true });

const db: BetterSqliteDatabase = new DatabaseConstructor(DB_PATH);
db.pragma('journal_mode = WAL');

db.exec(`
  CREATE TABLE IF NOT EXISTS price_cache (
    coin TEXT NOT NULL,
    date TEXT NOT NULL,
    price REAL NOT NULL,
    fetched_at TEXT NOT NULL,
    PRIMARY KEY (coin, date)
  );

  CREATE TABLE IF NOT EXISTS simulation_portfolio (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    cash REAL NOT NULL,
    updated_at TEXT NOT NULL
  );

  CREATE TABLE IF NOT EXISTS simulation_positions (
    coin TEXT PRIMARY KEY,
    quantity REAL NOT NULL,
    avg_price REAL NOT NULL,
    updated_at TEXT NOT NULL
  );

  CREATE TABLE IF NOT EXISTS simulation_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    coin TEXT NOT NULL,
    price REAL NOT NULL,
    quantity REAL NOT NULL,
    notional REAL NOT NULL,
    created_at TEXT NOT NULL
  );

  CREATE TABLE IF NOT EXISTS backtest_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy TEXT NOT NULL,
    coin TEXT NOT NULL,
    initial_capital REAL NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    result_json TEXT NOT NULL,
    created_at TEXT NOT NULL
  );

  CREATE TABLE IF NOT EXISTS optimization_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    coin TEXT NOT NULL,
    strategy TEXT NOT NULL,
    initial_capital REAL NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    params_json TEXT NOT NULL,
    final_value REAL NOT NULL,
    total_return_pct REAL NOT NULL,
    max_drawdown_pct REAL NOT NULL,
    sharpe_ratio REAL NOT NULL,
    win_rate_pct REAL NOT NULL,
    trade_count INTEGER NOT NULL,
    score REAL NOT NULL,
    created_at TEXT NOT NULL
  );

  CREATE INDEX IF NOT EXISTS idx_optimization_results_score
    ON optimization_results (score DESC, total_return_pct DESC, sharpe_ratio DESC);
  CREATE INDEX IF NOT EXISTS idx_optimization_results_coin_strategy
    ON optimization_results (coin, strategy);
`);

export function getDb(): BetterSqliteDatabase {
  return db;
}

export function upsertPrices(coin: CoinId, prices: CoinPriceRow[]): void {
  if (prices.length === 0) {
    return;
  }

  const now = new Date().toISOString();
  const stmt = db.prepare(`
    INSERT INTO price_cache (coin, date, price, fetched_at)
    VALUES (@coin, @date, @price, @fetched_at)
    ON CONFLICT(coin, date) DO UPDATE SET
      price = excluded.price,
      fetched_at = excluded.fetched_at
  `);

  const tx = db.transaction((rows: CoinPriceRow[]) => {
    for (const row of rows) {
      stmt.run({ coin, date: row.date, price: row.price, fetched_at: now });
    }
  });

  tx(prices);
}

export function getCachedPrices(
  coin: CoinId,
  startDate?: string,
  endDate?: string,
): CoinPriceRow[] {
  if (startDate && endDate) {
    const stmt = db.prepare(
      `SELECT coin, date, price FROM price_cache WHERE coin = ? AND date BETWEEN ? AND ? ORDER BY date ASC`,
    );
    return stmt.all(coin, startDate, endDate) as CoinPriceRow[];
  }

  if (startDate) {
    const stmt = db.prepare(
      `SELECT coin, date, price FROM price_cache WHERE coin = ? AND date >= ? ORDER BY date ASC`,
    );
    return stmt.all(coin, startDate) as CoinPriceRow[];
  }

  if (endDate) {
    const stmt = db.prepare(
      `SELECT coin, date, price FROM price_cache WHERE coin = ? AND date <= ? ORDER BY date ASC`,
    );
    return stmt.all(coin, endDate) as CoinPriceRow[];
  }

  const stmt = db.prepare(`SELECT coin, date, price FROM price_cache WHERE coin = ? ORDER BY date ASC`);
  return stmt.all(coin) as CoinPriceRow[];
}

export function getCachedPriceCount(coin: CoinId, startDate: string, endDate: string): number {
  const stmt = db.prepare(
    `SELECT COUNT(1) as count FROM price_cache WHERE coin = ? AND date BETWEEN ? AND ?`,
  );
  const row = stmt.get(coin, startDate, endDate) as { count: number };
  return row.count;
}

export function getLatestCachedPrice(coin: CoinId): CoinPriceRow | null {
  const stmt = db.prepare(
    `SELECT coin, date, price FROM price_cache WHERE coin = ? ORDER BY date DESC LIMIT 1`,
  );
  const row = stmt.get(coin) as CoinPriceRow | undefined;
  return row ?? null;
}

export function saveBacktestResult(
  strategy: string,
  coin: CoinId,
  initialCapital: number,
  startDate: string,
  endDate: string,
  resultJson: string,
): void {
  const stmt = db.prepare(`
    INSERT INTO backtest_results (
      strategy, coin, initial_capital, start_date, end_date, result_json, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
  `);
  stmt.run(strategy, coin, initialCapital, startDate, endDate, resultJson, new Date().toISOString());
}

export interface OptimizationResultInput {
  coin: CoinId;
  strategy: StrategyName;
  initial_capital: number;
  start_date: string;
  end_date: string;
  params_json: string;
  final_value: number;
  total_return_pct: number;
  max_drawdown_pct: number;
  sharpe_ratio: number;
  win_rate_pct: number;
  trade_count: number;
  score: number;
}

export interface OptimizationResultRow extends OptimizationResultInput {
  id: number;
  created_at: string;
}

export function saveOptimizationResult(result: OptimizationResultInput): void {
  const stmt = db.prepare(`
    INSERT INTO optimization_results (
      coin,
      strategy,
      initial_capital,
      start_date,
      end_date,
      params_json,
      final_value,
      total_return_pct,
      max_drawdown_pct,
      sharpe_ratio,
      win_rate_pct,
      trade_count,
      score,
      created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);

  stmt.run(
    result.coin,
    result.strategy,
    result.initial_capital,
    result.start_date,
    result.end_date,
    result.params_json,
    result.final_value,
    result.total_return_pct,
    result.max_drawdown_pct,
    result.sharpe_ratio,
    result.win_rate_pct,
    result.trade_count,
    result.score,
    new Date().toISOString(),
  );
}

export interface OptimizationResultQuery {
  coin?: CoinId;
  strategy?: StrategyName;
  limit?: number;
}

export function listOptimizationResults(query: OptimizationResultQuery = {}): OptimizationResultRow[] {
  const where: string[] = [];
  const values: unknown[] = [];

  if (query.coin) {
    where.push('coin = ?');
    values.push(query.coin);
  }
  if (query.strategy) {
    where.push('strategy = ?');
    values.push(query.strategy);
  }

  const limit = Math.max(1, Math.floor(query.limit ?? 50));
  const sql = `
    SELECT
      id,
      coin,
      strategy,
      initial_capital,
      start_date,
      end_date,
      params_json,
      final_value,
      total_return_pct,
      max_drawdown_pct,
      sharpe_ratio,
      win_rate_pct,
      trade_count,
      score,
      created_at
    FROM optimization_results
    ${where.length > 0 ? `WHERE ${where.join(' AND ')}` : ''}
    ORDER BY score DESC, total_return_pct DESC, sharpe_ratio DESC, id DESC
    LIMIT ?
  `;

  values.push(limit);
  return db.prepare(sql).all(...values) as OptimizationResultRow[];
}

export function ensurePortfolio(initialCapital: number): void {
  const row = db.prepare(`SELECT cash FROM simulation_portfolio WHERE id = 1`).get() as
    | { cash: number }
    | undefined;

  if (!row) {
    db.prepare(`INSERT INTO simulation_portfolio (id, cash, updated_at) VALUES (1, ?, ?)`).run(
      initialCapital,
      new Date().toISOString(),
    );
  }
}

export function getPortfolioCash(): number {
  const row = db.prepare(`SELECT cash FROM simulation_portfolio WHERE id = 1`).get() as
    | { cash: number }
    | undefined;
  if (!row) {
    return 0;
  }
  return row.cash;
}

export function setPortfolioCash(cash: number): void {
  db.prepare(`UPDATE simulation_portfolio SET cash = ?, updated_at = ? WHERE id = 1`).run(
    cash,
    new Date().toISOString(),
  );
}

export function getPosition(coin: CoinId): { coin: CoinId; quantity: number; avg_price: number } | null {
  const row = db
    .prepare(`SELECT coin, quantity, avg_price FROM simulation_positions WHERE coin = ?`)
    .get(coin) as { coin: CoinId; quantity: number; avg_price: number } | undefined;

  return row ?? null;
}

export function setPosition(coin: CoinId, quantity: number, avgPrice: number): void {
  if (quantity <= 0) {
    db.prepare(`DELETE FROM simulation_positions WHERE coin = ?`).run(coin);
    return;
  }

  db.prepare(`
    INSERT INTO simulation_positions (coin, quantity, avg_price, updated_at)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(coin) DO UPDATE SET
      quantity = excluded.quantity,
      avg_price = excluded.avg_price,
      updated_at = excluded.updated_at
  `).run(coin, quantity, avgPrice, new Date().toISOString());
}

export function listPositions(): Array<{ coin: CoinId; quantity: number; avg_price: number }> {
  return db
    .prepare(`SELECT coin, quantity, avg_price FROM simulation_positions ORDER BY coin ASC`)
    .all() as Array<{ coin: CoinId; quantity: number; avg_price: number }>;
}

export function insertSimulationTrade(trade: {
  action: 'buy' | 'sell';
  coin: CoinId;
  price: number;
  quantity: number;
  notional: number;
  createdAt: string;
}): number {
  const info = db
    .prepare(
      `INSERT INTO simulation_trades (action, coin, price, quantity, notional, created_at)
       VALUES (?, ?, ?, ?, ?, ?)`,
    )
    .run(trade.action, trade.coin, trade.price, trade.quantity, trade.notional, trade.createdAt);

  return Number(info.lastInsertRowid);
}

export function listSimulationTrades(limit = 100): Array<{
  id: number;
  action: 'buy' | 'sell';
  coin: CoinId;
  price: number;
  quantity: number;
  notional: number;
  created_at: string;
}> {
  return db
    .prepare(
      `SELECT id, action, coin, price, quantity, notional, created_at
       FROM simulation_trades
       ORDER BY datetime(created_at) DESC
       LIMIT ?`,
    )
    .all(limit) as Array<{
    id: number;
    action: 'buy' | 'sell';
    coin: CoinId;
    price: number;
    quantity: number;
    notional: number;
    created_at: string;
  }>;
}

export function clearAllSimulationData(): void {
  db.exec(`
    DELETE FROM simulation_trades;
    DELETE FROM simulation_positions;
    DELETE FROM simulation_portfolio;
  `);
}
