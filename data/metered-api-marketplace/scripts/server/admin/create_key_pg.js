import 'dotenv/config';
import crypto from 'node:crypto';
import pg from 'pg';

const { Pool } = pg;

const DATABASE_URL = process.env.DATABASE_URL;
if (!DATABASE_URL) {
  console.error('Missing DATABASE_URL');
  process.exit(1);
}

const starting = Number(process.argv[2] ?? '0');

const pool = new Pool({ connectionString: DATABASE_URL });

const id = (prefix) => `${prefix}_${crypto.randomBytes(12).toString('hex')}`;

const apiKeyId = id('key');
const secret = crypto.randomBytes(24).toString('hex');

const client = await pool.connect();
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
  `);

  await client.query('INSERT INTO api_keys(id, secret, disabled_at) VALUES($1, $2, NULL)', [apiKeyId, secret]);
  await client.query(
    `INSERT INTO balances(api_key_id, balance_cents) VALUES($1, $2)
     ON CONFLICT (api_key_id) DO UPDATE SET balance_cents=EXCLUDED.balance_cents, updated_at=now()`,
    [apiKeyId, BigInt(Math.max(0, Math.floor(starting)))]
  );

  await client.query('COMMIT');

  console.log(JSON.stringify({ api_key: apiKeyId, api_secret: secret, starting_balance_cents: starting }, null, 2));
} catch (e) {
  await client.query('ROLLBACK');
  console.error(e);
  process.exit(1);
} finally {
  client.release();
  await pool.end();
}
