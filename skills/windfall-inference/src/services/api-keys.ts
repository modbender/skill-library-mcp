import Database from 'better-sqlite3';
import crypto from 'crypto';
import path from 'path';

const DB_PATH = path.resolve(__dirname, '../../windfall.db');
const DEFAULT_FREE_REQUESTS = 25; // Anonymous tier — overridden by identity check

let db: Database.Database;

function getDb(): Database.Database {
  if (!db) {
    db = new Database(DB_PATH);
    db.pragma('journal_mode = WAL');
    db.exec(`
      CREATE TABLE IF NOT EXISTS api_keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key_prefix TEXT NOT NULL,
        key_hash TEXT NOT NULL UNIQUE,
        wallet_address TEXT,
        label TEXT,
        balance_usd REAL DEFAULT 0,
        identity_tier TEXT DEFAULT 'anonymous',
        free_requests_remaining INTEGER DEFAULT ${DEFAULT_FREE_REQUESTS},
        total_requests INTEGER DEFAULT 0,
        total_spent_usd REAL DEFAULT 0,
        total_saved_usd REAL DEFAULT 0,
        created_at TEXT NOT NULL,
        last_used_at TEXT
      )
    `);
    // Migration: add identity_tier column if missing (existing DBs)
    try {
      db.exec(`ALTER TABLE api_keys ADD COLUMN identity_tier TEXT DEFAULT 'anonymous'`);
    } catch { /* column already exists */ }
  }
  return db;
}

function hashKey(key: string): string {
  return crypto.createHash('sha256').update(key).digest('hex');
}

function generateKey(): string {
  const random = crypto.randomBytes(32).toString('base64url');
  return `wf_${random}`;
}

export interface ApiKeyInfo {
  id: number;
  keyPrefix: string;
  walletAddress: string | null;
  label: string | null;
  identityTier: string;
  balanceUsd: number;
  freeRequestsRemaining: number;
  totalRequests: number;
  totalSpentUsd: number;
  totalSavedUsd: number;
  createdAt: string;
  lastUsedAt: string | null;
}

export interface AuthResult {
  authenticated: boolean;
  keyId?: number;
  method: 'api_key' | 'wallet' | 'none';
  walletAddress?: string;
  freeRemaining?: number;
  balanceUsd?: number;
}

/** Create a new API key. Returns the full key (only shown once). */
export function createApiKey(
  walletAddress?: string,
  label?: string,
  identityTier?: string,
  freeRequests?: number,
): { key: string; info: ApiKeyInfo } {
  const db = getDb();
  const key = generateKey();
  const keyHash = hashKey(key);
  const keyPrefix = key.slice(0, 12) + '...';
  const now = new Date().toISOString();
  const tier = identityTier || 'anonymous';
  const free = freeRequests ?? DEFAULT_FREE_REQUESTS;

  db.prepare(`
    INSERT INTO api_keys (key_prefix, key_hash, wallet_address, label, identity_tier, free_requests_remaining, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `).run(keyPrefix, keyHash, walletAddress?.toLowerCase() || null, label || null, tier, free, now);

  const row = db.prepare('SELECT * FROM api_keys WHERE key_hash = ?').get(keyHash) as any;

  return {
    key,
    info: rowToInfo(row),
  };
}

/** Validate an API key and return auth info. */
export function validateApiKey(key: string): AuthResult {
  if (!key || !key.startsWith('wf_')) {
    return { authenticated: false, method: 'none' };
  }

  const db = getDb();
  const keyHash = hashKey(key);
  const row = db.prepare('SELECT * FROM api_keys WHERE key_hash = ?').get(keyHash) as any;

  if (!row) {
    return { authenticated: false, method: 'none' };
  }

  // Update last_used_at
  db.prepare('UPDATE api_keys SET last_used_at = ? WHERE id = ?')
    .run(new Date().toISOString(), row.id);

  return {
    authenticated: true,
    keyId: row.id,
    method: 'api_key',
    walletAddress: row.wallet_address || undefined,
    freeRemaining: row.free_requests_remaining,
    balanceUsd: row.balance_usd,
  };
}

/** Check if this key can make a request (has free tier or balance). */
export function canMakeRequest(keyId: number, costUsd: number): { allowed: boolean; paymentMethod: string; reason?: string } {
  const db = getDb();
  const row = db.prepare('SELECT free_requests_remaining, balance_usd FROM api_keys WHERE id = ?').get(keyId) as any;

  if (!row) return { allowed: false, paymentMethod: 'none', reason: 'Key not found' };

  if (row.free_requests_remaining > 0) {
    return { allowed: true, paymentMethod: 'free_tier' };
  }

  if (row.balance_usd >= costUsd) {
    return { allowed: true, paymentMethod: 'api_key_balance' };
  }

  return {
    allowed: false,
    paymentMethod: 'none',
    reason: `Insufficient balance. Free tier exhausted. Balance: $${row.balance_usd.toFixed(4)}, cost: $${costUsd.toFixed(4)}`,
  };
}

/** Deduct a request from the key (free tier or balance). */
export function deductRequest(keyId: number, costUsd: number, savedUsd: number, paymentMethod: string): void {
  const db = getDb();
  const now = new Date().toISOString();

  if (paymentMethod === 'free_tier') {
    db.prepare(`
      UPDATE api_keys SET
        free_requests_remaining = free_requests_remaining - 1,
        total_requests = total_requests + 1,
        total_saved_usd = total_saved_usd + ?,
        last_used_at = ?
      WHERE id = ?
    `).run(savedUsd, now, keyId);
  } else {
    db.prepare(`
      UPDATE api_keys SET
        balance_usd = balance_usd - ?,
        total_requests = total_requests + 1,
        total_spent_usd = total_spent_usd + ?,
        total_saved_usd = total_saved_usd + ?,
        last_used_at = ?
      WHERE id = ?
    `).run(costUsd, costUsd, savedUsd, now, keyId);
  }
}

/** Add balance to a key (from ETH/USDC top-up). */
export function addBalance(keyId: number, amountUsd: number): void {
  const db = getDb();
  db.prepare('UPDATE api_keys SET balance_usd = balance_usd + ? WHERE id = ?')
    .run(amountUsd, keyId);
}

/** Get key info by key string. */
export function getKeyInfo(key: string): ApiKeyInfo | null {
  const db = getDb();
  const keyHash = hashKey(key);
  const row = db.prepare('SELECT * FROM api_keys WHERE key_hash = ?').get(keyHash) as any;
  return row ? rowToInfo(row) : null;
}

/** Get key info by ID. */
export function getKeyInfoById(keyId: number): ApiKeyInfo | null {
  const db = getDb();
  const row = db.prepare('SELECT * FROM api_keys WHERE id = ?').get(keyId) as any;
  return row ? rowToInfo(row) : null;
}

/** Delete an API key by its raw key string. Returns true if a row was deleted. */
export function deleteApiKey(key: string): boolean {
  if (!key || !key.startsWith('wf_')) return false;
  const db = getDb();
  const keyHash = hashKey(key);
  const result = db.prepare('DELETE FROM api_keys WHERE key_hash = ?').run(keyHash);
  return result.changes > 0;
}

/** Delete API keys inactive for 12+ months. Returns number of keys deleted. */
export function purgeInactiveKeys(): number {
  const db = getDb();
  const twelveMonthsAgo = new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString();
  const result = db.prepare(`
    DELETE FROM api_keys
    WHERE (last_used_at IS NOT NULL AND last_used_at < ?)
       OR (last_used_at IS NULL AND created_at < ?)
  `).run(twelveMonthsAgo, twelveMonthsAgo);
  return result.changes;
}

/** Anonymize wallet addresses in request_log older than 30 days. Returns number of rows updated. */
export function anonymizeOldRequests(): number {
  const db = getDb();
  const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString();
  const result = db.prepare(`
    UPDATE request_log
    SET wallet_address = 'anonymized'
    WHERE timestamp < ? AND wallet_address != 'anonymized'
  `).run(thirtyDaysAgo);
  return result.changes;
}

/** Extract API key from Authorization header. */
export function extractApiKey(headers: Record<string, string | string[] | undefined>): string | null {
  const auth = headers['authorization'] || headers['Authorization'];
  if (!auth) return null;
  const authStr = Array.isArray(auth) ? auth[0] : auth;
  if (authStr.startsWith('Bearer wf_')) {
    return authStr.slice(7); // Remove "Bearer "
  }
  return null;
}

/** Get all keys for a wallet address. */
export function getKeysByWallet(walletAddress: string): ApiKeyInfo[] {
  const db = getDb();
  const rows = db.prepare('SELECT * FROM api_keys WHERE wallet_address = ? ORDER BY created_at DESC').all(walletAddress.toLowerCase()) as any[];
  return rows.map(rowToInfo);
}

function rowToInfo(row: any): ApiKeyInfo {
  return {
    id: row.id,
    keyPrefix: row.key_prefix,
    walletAddress: row.wallet_address,
    label: row.label,
    identityTier: row.identity_tier || 'anonymous',
    balanceUsd: row.balance_usd,
    freeRequestsRemaining: row.free_requests_remaining,
    totalRequests: row.total_requests,
    totalSpentUsd: row.total_spent_usd,
    totalSavedUsd: row.total_saved_usd,
    createdAt: row.created_at,
    lastUsedAt: row.last_used_at,
  };
}
