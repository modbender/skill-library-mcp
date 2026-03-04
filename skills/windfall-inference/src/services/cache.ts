/**
 * Semantic Cache
 *
 * Caches LLM responses by content hash. If the same (or very similar)
 * prompt is seen again within the TTL, return the cached response.
 *
 * Cache key = SHA256(normalized messages JSON + model + keyScope)
 * keyScope isolates caches per user: "key:{id}" | "wallet:{addr}" | "anon:{reqId}"
 * TTL = 1 hour (configurable)
 *
 * This is where serious savings accumulate — agents repeat themselves
 * constantly (same system prompts, similar queries).
 */

import Database from 'better-sqlite3';
import crypto from 'crypto';
import path from 'path';

const DB_PATH = path.resolve(__dirname, '../../windfall.db');
const DEFAULT_TTL_MS = 60 * 60 * 1000; // 1 hour

let db: Database.Database;

function getDb(): Database.Database {
  if (!db) {
    db = new Database(DB_PATH);
    db.pragma('journal_mode = WAL');
    db.exec(`
      CREATE TABLE IF NOT EXISTS response_cache (
        cache_key TEXT PRIMARY KEY,
        model TEXT NOT NULL,
        response_json TEXT NOT NULL,
        input_tokens INTEGER DEFAULT 0,
        output_tokens INTEGER DEFAULT 0,
        created_at INTEGER NOT NULL,
        expires_at INTEGER NOT NULL,
        hit_count INTEGER DEFAULT 0,
        last_hit_at INTEGER,
        saved_usd REAL DEFAULT 0
      )
    `);
    db.exec(`
      CREATE INDEX IF NOT EXISTS idx_cache_expires ON response_cache(expires_at)
    `);
  }
  return db;
}

interface CacheMessage {
  role: string;
  content: string;
}

/** Normalize messages for consistent hashing.
 *  Strips whitespace, lowercases role, sorts keys.
 */
function normalizeMessages(messages: CacheMessage[]): string {
  const normalized = messages.map(m => ({
    role: m.role.toLowerCase().trim(),
    content: m.content.trim(),
  }));
  return JSON.stringify(normalized);
}

/** Generate cache key from messages + model + key scope.
 *  keyScope ensures caches are isolated per API key / wallet / anonymous session.
 *  Format: "key:{id}" | "wallet:{address}" | "anon:{requestId}"
 */
function getCacheKey(messages: CacheMessage[], model: string, keyScope: string): string {
  const normalized = normalizeMessages(messages) + '|' + model.toLowerCase() + '|' + keyScope;
  return crypto.createHash('sha256').update(normalized).digest('hex');
}

export interface CachedResponse {
  response: any;           // The full OpenRouter response object
  cacheHit: true;
  cacheKey: string;
  originalRequestTimeMs: number; // How long the original request took
  savedUsd: number;              // Cumulative savings from this cache entry
}

/** Look up a cached response. Returns null if miss or expired. */
export function getCached(
  messages: CacheMessage[],
  model: string,
  keyScope: string,
): CachedResponse | null {
  const db = getDb();
  const cacheKey = getCacheKey(messages, model, keyScope);
  const now = Date.now();

  const row = db.prepare(
    'SELECT * FROM response_cache WHERE cache_key = ? AND expires_at > ?'
  ).get(cacheKey, now) as any;

  if (!row) return null;

  // Increment hit count
  db.prepare(
    'UPDATE response_cache SET hit_count = hit_count + 1, last_hit_at = ? WHERE cache_key = ?'
  ).run(now, cacheKey);

  const response = JSON.parse(row.response_json);

  return {
    response,
    cacheHit: true,
    cacheKey,
    originalRequestTimeMs: 0,
    savedUsd: row.saved_usd,
  };
}

/** Store a response in the cache. */
export function setCached(
  messages: CacheMessage[],
  model: string,
  keyScope: string,
  response: any,
  costUsd: number,
  ttlMs: number = DEFAULT_TTL_MS,
): string {
  const db = getDb();
  const cacheKey = getCacheKey(messages, model, keyScope);
  const now = Date.now();
  const expiresAt = now + ttlMs;

  const inputTokens = response.usage?.prompt_tokens || 0;
  const outputTokens = response.usage?.completion_tokens || 0;

  db.prepare(`
    INSERT OR REPLACE INTO response_cache
    (cache_key, model, response_json, input_tokens, output_tokens, created_at, expires_at, saved_usd)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `).run(
    cacheKey,
    model.toLowerCase(),
    JSON.stringify(response),
    inputTokens,
    outputTokens,
    now,
    expiresAt,
    costUsd,
  );

  return cacheKey;
}

/** Record savings when a cache hit avoids a paid request. */
export function recordCacheSavings(cacheKey: string, savedUsd: number): void {
  const db = getDb();
  db.prepare(
    'UPDATE response_cache SET saved_usd = saved_usd + ? WHERE cache_key = ?'
  ).run(savedUsd, cacheKey);
}

/** Get cache statistics. */
export function getCacheStats(): {
  totalEntries: number;
  totalHits: number;
  totalSavedUsd: number;
  hitRate: number;
  topCachedModels: Array<{ model: string; entries: number; hits: number }>;
} {
  const db = getDb();
  const now = Date.now();

  const total = (db.prepare(
    'SELECT COUNT(*) as count FROM response_cache WHERE expires_at > ?'
  ).get(now) as any).count;

  const hits = (db.prepare(
    'SELECT COALESCE(SUM(hit_count), 0) as total FROM response_cache'
  ).get() as any).total;

  const saved = (db.prepare(
    'SELECT COALESCE(SUM(saved_usd), 0) as total FROM response_cache'
  ).get() as any).total;

  const models = db.prepare(`
    SELECT model, COUNT(*) as entries, COALESCE(SUM(hit_count), 0) as hits
    FROM response_cache WHERE expires_at > ?
    GROUP BY model ORDER BY hits DESC LIMIT 5
  `).all(now) as any[];

  // Approximate hit rate
  const totalLookups = hits + total; // rough: entries ≈ misses
  const hitRate = totalLookups > 0 ? hits / totalLookups : 0;

  return {
    totalEntries: total,
    totalHits: hits,
    totalSavedUsd: saved,
    hitRate,
    topCachedModels: models,
  };
}

/** Purge expired entries. Run periodically. */
export function purgeExpired(): number {
  const db = getDb();
  const result = db.prepare('DELETE FROM response_cache WHERE expires_at < ?').run(Date.now());
  return result.changes;
}

/** Should we skip caching for this request? */
export function shouldBypassCache(headers: Record<string, string | string[] | undefined>): boolean {
  const cc = headers['cache-control'] || headers['Cache-Control'];
  if (!cc) return false;
  const ccStr = Array.isArray(cc) ? cc[0] : cc;
  return ccStr.includes('no-cache') || ccStr.includes('no-store');
}
