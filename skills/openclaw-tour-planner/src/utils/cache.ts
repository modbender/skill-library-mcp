import Database from 'better-sqlite3';
import path from 'path';
import fs from 'fs';
import { CacheEntry } from '../types';

/** Default TTLs in milliseconds */
export const TTL = {
  GEOCODING:   30 * 24 * 60 * 60 * 1000, // 30 days
  WIKIVOYAGE:   7 * 24 * 60 * 60 * 1000, // 7 days
  WEATHER:          60 * 60 * 1000,       // 1 hour
  SHORT:             5 * 60 * 1000,       // 5 minutes
} as const;

/**
 * SQLite-backed cache for API responses.
 * DB is stored at ~/.openclaw/cache/tour-planner.db
 */
export class Cache {
  private db: Database.Database;

  constructor(dbPath?: string) {
    const defaultPath = path.join(
      process.env.HOME ?? '/root',
      '.openclaw', 'cache', 'tour-planner.db',
    );
    // Allow override via env var (documented in SECURITY.md)
    const resolvedPath = dbPath ?? process.env.TOUR_PLANNER_CACHE_PATH ?? defaultPath;

    // Ensure directory exists
    fs.mkdirSync(path.dirname(resolvedPath), { recursive: true });

    this.db = new Database(resolvedPath);
    this.init();
  }

  private init(): void {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS cache (
        key        TEXT PRIMARY KEY,
        data       TEXT NOT NULL,
        expires_at INTEGER NOT NULL,
        created_at INTEGER NOT NULL
      );
      CREATE INDEX IF NOT EXISTS idx_expires ON cache(expires_at);
    `);
    // Purge expired entries on startup
    this.purgeExpired();
  }

  get<T>(key: string): T | null {
    const row = this.db
      .prepare('SELECT data, expires_at FROM cache WHERE key = ?')
      .get(key) as { data: string; expires_at: number } | undefined;

    if (!row) return null;
    if (Date.now() > row.expires_at) {
      this.delete(key);
      return null;
    }

    try {
      return JSON.parse(row.data) as T;
    } catch {
      return null;
    }
  }

  set<T>(key: string, data: T, ttlMs: number): void {
    const now = Date.now();
    this.db
      .prepare(`
        INSERT OR REPLACE INTO cache (key, data, expires_at, created_at)
        VALUES (?, ?, ?, ?)
      `)
      .run(key, JSON.stringify(data), now + ttlMs, now);
  }

  delete(key: string): void {
    this.db.prepare('DELETE FROM cache WHERE key = ?').run(key);
  }

  clear(): void {
    this.db.exec('DELETE FROM cache');
  }

  private purgeExpired(): void {
    this.db
      .prepare('DELETE FROM cache WHERE expires_at < ?')
      .run(Date.now());
  }
}

// Singleton instance
export const cache = new Cache();
