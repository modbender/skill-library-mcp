import { readRawBody } from '../../../lib/rawBody.js';
import { requireSignedKey } from '../../../lib/auth.js';
import { transformerNames } from '../../../lib/transformers.js';
import { pool, migrate } from '../../../lib/db.js';
import { env } from '../../../lib/env.js';

export const config = { api: { bodyParser: false } };

let migrated = false;

export default async function handler(req, res) {
  if (req.method !== 'GET') return res.status(405).json({ ok: false, error: 'method_not_allowed' });

  if (!migrated) {
    await migrate();
    migrated = true;
  }

  const rawBody = await readRawBody(req, Number(env('MAX_BODY_BYTES', '200000')));

  try {
    const { apiKeyId } = await requireSignedKey({ headers: req.headers, rawBody });

    const { rows: balRows } = await pool().query('SELECT balance_cents FROM balances WHERE api_key_id=$1', [apiKeyId]);
    const balance = balRows[0] ? Number(balRows[0].balance_cents) : 0;

    const { rows: recent } = await pool().query(
      'SELECT id, transformer, cost_cents, created_at FROM usage WHERE api_key_id=$1 ORDER BY created_at DESC LIMIT 50',
      [apiKeyId]
    );

    return res.status(200).json({
      ok: true,
      api_key: apiKeyId,
      balance_cents: balance,
      flat_cost_cents_per_call: Number(env('COST_CENTS_PER_CALL', '25')),
      transformers: transformerNames,
      recent_usage: recent
    });
  } catch (e) {
    return res.status(e.statusCode ?? 500).json({ ok: false, error: e.message });
  }
}
