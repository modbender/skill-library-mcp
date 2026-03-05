import pg from 'pg';
import { env } from './env.js';

const { Pool } = pg;

let _pool;

export function pool() {
  if (_pool) return _pool;
  const DATABASE_URL = env('DATABASE_URL', '');
  if (!DATABASE_URL) throw new Error('Missing DATABASE_URL');

  // For serverless, use Supabase Transaction Pooler connection string.
  _pool = new Pool({ connectionString: DATABASE_URL });
  return _pool;
}

export async function migrate() {
  const p = pool();
  const client = await p.connect();
  try {
    await client.query('BEGIN');
    await client.query(`
      CREATE TABLE IF NOT EXISTS api_keys (
        id TEXT PRIMARY KEY,
        secret TEXT NOT NULL,
        disabled_at TIMESTAMPTZ
      );

      CREATE TABLE IF NOT EXISTS balances (
        api_key_id TEXT PRIMARY KEY REFERENCES api_keys(id),
        balance_cents BIGINT NOT NULL,
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
      );

      CREATE TABLE IF NOT EXISTS usage (
        id TEXT PRIMARY KEY,
        api_key_id TEXT NOT NULL REFERENCES api_keys(id),
        route TEXT NOT NULL,
        transformer TEXT NOT NULL,
        request_hash TEXT NOT NULL,
        request_id TEXT,
        cost_cents BIGINT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
      );
      CREATE UNIQUE INDEX IF NOT EXISTS usage_dedupe ON usage(api_key_id, transformer, request_id) WHERE request_id IS NOT NULL;

      CREATE TABLE IF NOT EXISTS credits (
        id TEXT PRIMARY KEY,
        api_key_id TEXT NOT NULL REFERENCES api_keys(id),
        provider TEXT NOT NULL,
        event_id TEXT NOT NULL,
        gross_cents BIGINT NOT NULL,
        fee_cents BIGINT NOT NULL,
        net_cents BIGINT NOT NULL,
        chain TEXT,
        txid TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
      );
      CREATE UNIQUE INDEX IF NOT EXISTS credits_dedupe ON credits(provider, event_id);
    `);
    await client.query('COMMIT');
  } catch (e) {
    await client.query('ROLLBACK');
    throw e;
  } finally {
    client.release();
  }
}
