import Database from 'better-sqlite3';
import path from 'path';

const DB_PATH = path.resolve(__dirname, '../../windfall.db');
const FREE_REQUESTS = 3;

let db: Database.Database;

function getDb(): Database.Database {
  if (!db) {
    db = new Database(DB_PATH);
    db.pragma('journal_mode = WAL');
    db.exec(`
      CREATE TABLE IF NOT EXISTS free_tier (
        wallet_address TEXT PRIMARY KEY,
        requests_used INTEGER DEFAULT 0,
        first_request_at TEXT,
        last_request_at TEXT
      )
    `);
    db.exec(`
      CREATE TABLE IF NOT EXISTS request_log (
        id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        wallet_address TEXT,
        node_id TEXT,
        model TEXT,
        mode TEXT,
        input_tokens INTEGER,
        output_tokens INTEGER,
        energy_price_kwh REAL,
        carbon_intensity REAL,
        cost_usd REAL,
        payment_method TEXT,
        response_time_ms INTEGER,
        attestation_uid TEXT
      )
    `);
    db.exec(`
      CREATE TABLE IF NOT EXISTS revenue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        wallet_address TEXT,
        amount_usd REAL,
        payment_method TEXT,
        tx_hash TEXT
      )
    `);
  }
  return db;
}

export function checkFreeTier(walletAddress: string): { allowed: boolean; remaining: number } {
  const db = getDb();
  const addr = walletAddress.toLowerCase();

  const row = db.prepare('SELECT requests_used FROM free_tier WHERE wallet_address = ?').get(addr) as
    | { requests_used: number }
    | undefined;

  if (!row) {
    return { allowed: true, remaining: FREE_REQUESTS };
  }

  const remaining = FREE_REQUESTS - row.requests_used;
  return { allowed: remaining > 0, remaining: Math.max(0, remaining) };
}

export function consumeFreeTier(walletAddress: string): void {
  const db = getDb();
  const addr = walletAddress.toLowerCase();
  const now = new Date().toISOString();

  const existing = db.prepare('SELECT requests_used FROM free_tier WHERE wallet_address = ?').get(addr);

  if (existing) {
    db.prepare('UPDATE free_tier SET requests_used = requests_used + 1, last_request_at = ? WHERE wallet_address = ?')
      .run(now, addr);
  } else {
    db.prepare('INSERT INTO free_tier (wallet_address, requests_used, first_request_at, last_request_at) VALUES (?, 1, ?, ?)')
      .run(addr, now, now);
  }
}

export function logRequest(log: {
  id: string;
  walletAddress: string;
  nodeId: string;
  model: string;
  mode: string;
  inputTokens: number;
  outputTokens: number;
  energyPriceKwh: number;
  carbonIntensity: number;
  costUsd: number;
  paymentMethod: string;
  responseTimeMs: number;
  attestationUid?: string;
}): void {
  const db = getDb();
  db.prepare(`
    INSERT INTO request_log (id, timestamp, wallet_address, node_id, model, mode, input_tokens, output_tokens, energy_price_kwh, carbon_intensity, cost_usd, payment_method, response_time_ms, attestation_uid)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).run(
    log.id,
    new Date().toISOString(),
    log.walletAddress.toLowerCase(),
    log.nodeId,
    log.model,
    log.mode,
    log.inputTokens,
    log.outputTokens,
    log.energyPriceKwh,
    log.carbonIntensity,
    log.costUsd,
    log.paymentMethod,
    log.responseTimeMs,
    log.attestationUid || null,
  );
}

export function logRevenue(walletAddress: string, amountUsd: number, paymentMethod: string, txHash?: string): void {
  const db = getDb();
  db.prepare(`
    INSERT INTO revenue (timestamp, wallet_address, amount_usd, payment_method, tx_hash)
    VALUES (?, ?, ?, ?, ?)
  `).run(new Date().toISOString(), walletAddress.toLowerCase(), amountUsd, paymentMethod, txHash || null);
}

// Stats queries for the command center
export function getStats() {
  const db = getDb();

  const totalRequests = (db.prepare('SELECT COUNT(*) as count FROM request_log').get() as any).count;
  const totalRevenue = (db.prepare('SELECT COALESCE(SUM(amount_usd), 0) as total FROM revenue').get() as any).total;
  const uniqueAgents = (db.prepare('SELECT COUNT(DISTINCT wallet_address) as count FROM request_log').get() as any).count;
  const freeAgents = (db.prepare('SELECT COUNT(*) as count FROM free_tier').get() as any).count;
  const paidAgents = (db.prepare("SELECT COUNT(DISTINCT wallet_address) as count FROM request_log WHERE payment_method != 'free_tier'").get() as any).count;

  // Last 24h
  const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
  const requests24h = (db.prepare('SELECT COUNT(*) as count FROM request_log WHERE timestamp > ?').get(oneDayAgo) as any).count;
  const revenue24h = (db.prepare('SELECT COALESCE(SUM(amount_usd), 0) as total FROM revenue WHERE timestamp > ?').get(oneDayAgo) as any).total;

  // By node
  const byNode = db.prepare('SELECT node_id, COUNT(*) as count FROM request_log GROUP BY node_id').all();

  // By model
  const byModel = db.prepare('SELECT model, COUNT(*) as count FROM request_log GROUP BY model ORDER BY count DESC LIMIT 10').all();

  // By mode
  const byMode = db.prepare('SELECT mode, COUNT(*) as count FROM request_log GROUP BY mode').all();

  // Recent requests
  const recentRequests = db.prepare('SELECT * FROM request_log ORDER BY timestamp DESC LIMIT 20').all();

  // Top agents
  const topAgents = db.prepare('SELECT wallet_address, COUNT(*) as count, SUM(cost_usd) as total_cost FROM request_log GROUP BY wallet_address ORDER BY count DESC LIMIT 10').all();

  return {
    totalRequests,
    totalRevenue,
    uniqueAgents,
    freeAgents,
    paidAgents,
    requests24h,
    revenue24h,
    byNode,
    byModel,
    byMode,
    recentRequests,
    topAgents,
  };
}

export function closeDb(): void {
  if (db) db.close();
}
