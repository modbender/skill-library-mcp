import crypto from 'node:crypto';
import { readRawBody } from '../../../../lib/rawBody.js';
import { env } from '../../../../lib/env.js';
import { pool, migrate } from '../../../../lib/db.js';

export const config = { api: { bodyParser: false } };

let migrated = false;

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ ok: false, error: 'method_not_allowed' });

  if (!migrated) {
    await migrate();
    migrated = true;
  }

  const token = (req.headers['authorization'] || '').replace(/^Bearer\s+/i, '');
  if (!env('ADMIN_TOKEN', '') || token !== env('ADMIN_TOKEN', '')) return res.status(403).json({ ok: false, error: 'forbidden' });

  const rawBody = await readRawBody(req, Number(env('MAX_BODY_BYTES', '200000')));
  let body;
  try {
    body = rawBody.length ? JSON.parse(rawBody.toString('utf8')) : {};
  } catch {
    return res.status(400).json({ ok: false, error: 'invalid_json' });
  }

  const starting = BigInt(Math.floor(Number(body?.starting_balance_cents ?? 0)));
  const apiKeyId = `key_${crypto.randomBytes(12).toString('hex')}`;
  const secret = crypto.randomBytes(24).toString('hex');

  const client = await pool().connect();
  try {
    await client.query('BEGIN');
    await client.query('INSERT INTO api_keys(id, secret, disabled_at) VALUES($1,$2,NULL)', [apiKeyId, secret]);
    await client.query(
      `INSERT INTO balances(api_key_id, balance_cents) VALUES($1, $2)
       ON CONFLICT (api_key_id) DO UPDATE SET balance_cents=EXCLUDED.balance_cents, updated_at=now()`,
      [apiKeyId, starting]
    );
    await client.query('COMMIT');

    return res.status(200).json({ ok: true, api_key: apiKeyId, api_secret: secret, starting_balance_cents: Number(starting) });
  } catch (e) {
    try { await client.query('ROLLBACK'); } catch {}
    return res.status(500).json({ ok: false, error: 'admin_create_key_failed' });
  } finally {
    client.release();
  }
}
