import { readRawBody } from '../../../../lib/rawBody.js';
import { requireSignedKey } from '../../../../lib/auth.js';
import { transformers, transformerNames } from '../../../../lib/transformers.js';
import { sha256Hex, id } from '../../../../lib/crypto.js';
import { pool, migrate } from '../../../../lib/db.js';
import { env } from '../../../../lib/env.js';

export const config = { api: { bodyParser: false } };

let migrated = false;

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ ok: false, error: 'method_not_allowed' });

  if (!migrated) {
    await migrate();
    migrated = true;
  }

  const name = String(req.query.name);
  const fn = transformers[name];
  if (!fn) return res.status(404).json({ ok: false, error: 'unknown_transformer', available: transformerNames });

  const rawBody = await readRawBody(req, Number(env('MAX_BODY_BYTES', '200000')));
  let body;
  try {
    body = rawBody.length ? JSON.parse(rawBody.toString('utf8')) : {};
  } catch {
    return res.status(400).json({ ok: false, error: 'invalid_json' });
  }

  try {
    const { apiKeyId } = await requireSignedKey({ headers: req.headers, rawBody });

    const requestHash = sha256Hex(rawBody);
    const requestId = body?.request_id ? String(body.request_id) : null;
    const cost = BigInt(Number(env('COST_CENTS_PER_CALL', '25')));

    const client = await pool().connect();
    let before = 0n;
    let after = 0n;
    let usageId = null;

    try {
      await client.query('BEGIN');

      const balRes = await client.query('SELECT balance_cents FROM balances WHERE api_key_id=$1 FOR UPDATE', [apiKeyId]);
      before = balRes.rows[0] ? BigInt(balRes.rows[0].balance_cents) : 0n;

      if (before < cost) {
        await client.query('ROLLBACK');
        return res.status(402).json({ ok: false, error: 'insufficient_balance', details: { balance_cents: Number(before), cost_cents: Number(cost) } });
      }

      if (requestId) {
        const existing = await client.query(
          'SELECT id FROM usage WHERE api_key_id=$1 AND transformer=$2 AND request_id=$3',
          [apiKeyId, name, requestId]
        );
        if (existing.rows[0]) {
          usageId = existing.rows[0].id;
          after = before;
          await client.query('COMMIT');
        }
      }

      if (!usageId) {
        after = before - cost;
        await client.query(
          `INSERT INTO balances(api_key_id, balance_cents) VALUES($1, $2)
           ON CONFLICT (api_key_id) DO UPDATE SET balance_cents=EXCLUDED.balance_cents, updated_at=now()`,
          [apiKeyId, after]
        );

        usageId = id('use');
        await client.query(
          'INSERT INTO usage(id, api_key_id, route, transformer, request_hash, request_id, cost_cents) VALUES($1,$2,$3,$4,$5,$6,$7)',
          [usageId, apiKeyId, '/api/v1/transform/[name]', name, requestHash, requestId, cost]
        );

        await client.query('COMMIT');
      }
    } catch (e) {
      try { await client.query('ROLLBACK'); } catch {}
      return res.status(500).json({ ok: false, error: 'billing_failed' });
    } finally {
      client.release();
    }

    let data;
    try {
      data = fn(body ?? {});
    } catch {
      return res.status(500).json({ ok: false, error: 'transformer_failed' });
    }

    return res.status(200).json({
      ok: true,
      transformer: name,
      data,
      billing: {
        cost_cents: Number(cost),
        balance_before_cents: Number(before),
        balance_after_cents: Number(after),
        usage_id: usageId
      }
    });
  } catch (e) {
    return res.status(e.statusCode ?? 500).json({ ok: false, error: e.message });
  }
}
