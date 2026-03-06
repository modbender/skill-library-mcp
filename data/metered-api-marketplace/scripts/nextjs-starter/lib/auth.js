import { env } from './env.js';
import { hmacHex, nowMs, timingSafeHexEqual } from './crypto.js';
import { pool } from './db.js';

export async function getKeyOrThrow(apiKeyId) {
  const { rows } = await pool().query('SELECT id, secret, disabled_at FROM api_keys WHERE id=$1', [apiKeyId]);
  const row = rows[0];
  if (!row) throw Object.assign(new Error('invalid_api_key'), { statusCode: 401 });
  if (row.disabled_at) throw Object.assign(new Error('api_key_disabled'), { statusCode: 403 });
  return row;
}

export async function requireSignedKey({ headers, rawBody }) {
  const apiKeyId = headers['x-api-key'];
  const ts = headers['x-timestamp'];
  const sig = headers['x-signature'];

  if (!apiKeyId || !ts || !sig) throw Object.assign(new Error('missing_auth_headers'), { statusCode: 401 });

  const tsNum = Number(ts);
  if (!Number.isFinite(tsNum)) throw Object.assign(new Error('bad_timestamp'), { statusCode: 401 });

  const MAX_SKEW_MS = Number(env('MAX_SKEW_MS', '300000'));
  if (Math.abs(nowMs() - tsNum) > MAX_SKEW_MS) throw Object.assign(new Error('timestamp_skew'), { statusCode: 401 });

  const key = await getKeyOrThrow(String(apiKeyId));
  const msg = `${ts}.${rawBody.toString('utf8')}`;
  const expected = hmacHex(key.secret, msg);
  if (!timingSafeHexEqual(expected, sig)) throw Object.assign(new Error('bad_signature'), { statusCode: 403 });

  return { apiKeyId: key.id };
}
