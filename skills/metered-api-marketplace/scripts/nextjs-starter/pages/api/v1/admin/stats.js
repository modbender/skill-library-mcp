import { readRawBody } from '../../../../lib/rawBody.js';
import { env } from '../../../../lib/env.js';
import { pool, migrate } from '../../../../lib/db.js';

export const config = { api: { bodyParser: false } };

let migrated = false;

export default async function handler(req, res) {
  if (req.method !== 'GET') return res.status(405).json({ ok: false, error: 'method_not_allowed' });

  if (!migrated) {
    await migrate();
    migrated = true;
  }

  const token = (req.headers['authorization'] || '').replace(/^Bearer\s+/i, '');
  if (!env('ADMIN_TOKEN', '') || token !== env('ADMIN_TOKEN', '')) return res.status(403).json({ ok: false, error: 'forbidden' });

  // still consume body for signing consistency (empty on GET typically)
  await readRawBody(req, Number(env('MAX_BODY_BYTES', '200000')));

  const days = Math.max(1, Math.min(30, Number(req.query.days ?? 7)));

  const { rows: usageRows } = await pool().query(
    `select
      date_trunc('day', created_at) as day,
      count(*)::bigint as calls,
      sum(cost_cents)::bigint as billed_cents
     from usage
     where created_at >= now() - ($1::text || ' days')::interval
     group by 1
     order by 1 desc`,
    [String(days)]
  );

  const { rows: topKeys } = await pool().query(
    `select api_key_id, count(*)::bigint as calls, sum(cost_cents)::bigint as billed_cents
     from usage
     where created_at >= now() - ($1::text || ' days')::interval
     group by api_key_id
     order by calls desc
     limit 20`,
    [String(days)]
  );

  return res.status(200).json({ ok: true, window_days: days, usage_by_day: usageRows, top_api_keys: topKeys });
}
