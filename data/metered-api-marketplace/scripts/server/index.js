import 'dotenv/config';
import Fastify from 'fastify';
import rateLimit from '@fastify/rate-limit';
import crypto from 'node:crypto';
import pg from 'pg';
import { transformers, transformerNames } from './transformers/index.js';

const { Pool } = pg;

const env = (k, d) => process.env[k] ?? d;

const PORT = Number(env('PORT', '8787'));
const HOST = env('HOST', '0.0.0.0');
const DATABASE_URL = env('DATABASE_URL', '');
const MAX_BODY_BYTES = Number(env('MAX_BODY_BYTES', '200000'));
const MAX_SKEW_MS = Number(env('MAX_SKEW_MS', '300000'));

// Flat pricing (single price across all transformers for launch)
const COST_CENTS_PER_CALL = Number(env('COST_CENTS_PER_CALL', '250'));

const FEE_BPS = Number(env('FEE_BPS', '250')); // 250 bps = 2.5%
const FEE_ETH_ADDRESS = env('FEE_ETH_ADDRESS', '');
const FEE_BTC_ADDRESS = env('FEE_BTC_ADDRESS', '');

const WEBHOOK_SHARED_SECRET = env('WEBHOOK_SHARED_SECRET', '');
const ADMIN_TOKEN = env('ADMIN_TOKEN', '');

if (!DATABASE_URL) {
  throw new Error('Missing DATABASE_URL (Postgres connection string)');
}

const pool = new Pool({ connectionString: DATABASE_URL });

const nowMs = () => Date.now();
const sha256Hex = (buf) => crypto.createHash('sha256').update(buf).digest('hex');
const hmacHex = (secret, msg) => crypto.createHmac('sha256', secret).update(msg).digest('hex');
const id = (prefix) => `${prefix}_${crypto.randomBytes(12).toString('hex')}`;

async function migrate() {
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

async function getKeyOrThrow(apiKeyId) {
  const { rows } = await pool.query('SELECT id, secret, disabled_at FROM api_keys WHERE id = $1', [apiKeyId]);
  const row = rows[0];
  if (!row) throw Object.assign(new Error('invalid_api_key'), { statusCode: 401 });
  if (row.disabled_at) throw Object.assign(new Error('api_key_disabled'), { statusCode: 403 });
  return row;
}

async function getBalanceCents(client, apiKeyId, forUpdate = false) {
  const q = `SELECT balance_cents FROM balances WHERE api_key_id=$1 ${forUpdate ? 'FOR UPDATE' : ''}`;
  const { rows } = await client.query(q, [apiKeyId]);
  return rows[0] ? BigInt(rows[0].balance_cents) : 0n;
}

async function upsertBalanceCents(client, apiKeyId, balanceCents) {
  await client.query(
    `INSERT INTO balances(api_key_id, balance_cents) VALUES($1, $2)
     ON CONFLICT (api_key_id) DO UPDATE SET balance_cents=EXCLUDED.balance_cents, updated_at=now()`,
    [apiKeyId, balanceCents]
  );
}

async function requireSignedKey(req) {
  const apiKeyId = req.headers['x-api-key'];
  const ts = req.headers['x-timestamp'];
  const sig = req.headers['x-signature'];

  if (!apiKeyId || !ts || !sig) throw Object.assign(new Error('missing_auth_headers'), { statusCode: 401 });
  const tsNum = Number(ts);
  if (!Number.isFinite(tsNum)) throw Object.assign(new Error('bad_timestamp'), { statusCode: 401 });
  if (Math.abs(nowMs() - tsNum) > MAX_SKEW_MS) throw Object.assign(new Error('timestamp_skew'), { statusCode: 401 });

  const key = await getKeyOrThrow(String(apiKeyId));
  const rawBody = req.rawBody ?? Buffer.from('');
  const msg = `${ts}.${rawBody.toString('utf8')}`;
  const expected = hmacHex(key.secret, msg);

  // timingSafeEqual requires same length buffers
  const expBuf = Buffer.from(expected, 'hex');
  const gotBuf = Buffer.from(String(sig), 'hex');
  if (expBuf.length !== gotBuf.length || !crypto.timingSafeEqual(expBuf, gotBuf)) {
    throw Object.assign(new Error('bad_signature'), { statusCode: 403 });
  }
  return { apiKeyId: key.id };
}

const app = Fastify({
  logger: true,
  bodyLimit: MAX_BODY_BYTES
});

// Capture raw body for signing
app.addContentTypeParser('application/json', { parseAs: 'buffer' }, function (req, body, done) {
  req.rawBody = body;
  try {
    const json = JSON.parse(body.toString('utf8'));
    done(null, json);
  } catch (e) {
    done(Object.assign(new Error('invalid_json'), { statusCode: 400 }));
  }
});

await app.register(rateLimit, { global: false });

app.get('/health', async () => ({ ok: true }));

app.get('/v1/balance', { config: { rateLimit: { max: 60, timeWindow: '1 minute' } } }, async (req, reply) => {
  const { apiKeyId } = await requireSignedKey(req);
  const client = await pool.connect();
  try {
    const bal = await getBalanceCents(client, apiKeyId, false);
    const { rows: recent } = await client.query(
      'SELECT id, transformer, cost_cents, created_at FROM usage WHERE api_key_id=$1 ORDER BY created_at DESC LIMIT 50',
      [apiKeyId]
    );

    return {
      ok: true,
      api_key: apiKeyId,
      balance_cents: Number(bal),
      flat_cost_cents_per_call: COST_CENTS_PER_CALL,
      transformers: transformerNames,
      recent_usage: recent
    };
  } finally {
    client.release();
  }
});

app.post('/v1/transform/:name', { config: { rateLimit: { max: 60, timeWindow: '1 minute' } } }, async (req, reply) => {
  const name = String(req.params.name);
  const fn = transformers[name];
  if (!fn) return reply.code(404).send({ ok: false, error: 'unknown_transformer', available: transformerNames });

  const { apiKeyId } = await requireSignedKey(req);

  const requestHash = sha256Hex(req.rawBody ?? Buffer.from(''));
  const requestId = req.body?.request_id ? String(req.body.request_id) : null;

  const cost = BigInt(COST_CENTS_PER_CALL);
  const client = await pool.connect();
  let before = 0n;
  let after = 0n;
  let usageId = null;

  try {
    await client.query('BEGIN');

    before = await getBalanceCents(client, apiKeyId, true);

    if (before < cost) {
      await client.query('ROLLBACK');
      return reply.code(402).send({ ok: false, error: 'insufficient_balance', details: { balance_cents: Number(before), cost_cents: Number(cost) } });
    }

    if (requestId) {
      const { rows } = await client.query(
        'SELECT id, cost_cents FROM usage WHERE api_key_id=$1 AND transformer=$2 AND request_id=$3',
        [apiKeyId, name, requestId]
      );
      if (rows[0]) {
        await client.query('COMMIT');
        // idempotent: do not charge again
        after = before;
        usageId = rows[0].id;
      }
    }

    if (!usageId) {
      after = before - cost;
      await upsertBalanceCents(client, apiKeyId, after);

      usageId = id('use');
      await client.query(
        'INSERT INTO usage(id, api_key_id, route, transformer, request_hash, request_id, cost_cents) VALUES($1,$2,$3,$4,$5,$6,$7)',
        [usageId, apiKeyId, '/v1/transform/:name', name, requestHash, requestId, cost]
      );

      await client.query('COMMIT');
    }
  } catch (e) {
    try { await client.query('ROLLBACK'); } catch {}
    return reply.code(500).send({ ok: false, error: 'billing_failed' });
  } finally {
    client.release();
  }

  // Pure-function transform (no external calls, no storage)
  let data;
  try {
    data = fn(req.body ?? {});
  } catch (e) {
    return reply.code(500).send({ ok: false, error: 'transformer_failed' });
  }

  return {
    ok: true,
    transformer: name,
    data,
    billing: {
      cost_cents: Number(cost),
      balance_before_cents: Number(before),
      balance_after_cents: Number(after),
      usage_id: usageId
    }
  };
});

// Webhook: demo provider style (shared secret + normalized payload)
app.post('/v1/payments/webhook/:provider', async (req, reply) => {
  const provider = String(req.params.provider);

  const sig = req.headers['x-webhook-signature'];
  if (!sig) return reply.code(401).send({ ok: false, error: 'missing_webhook_signature' });

  const raw = req.rawBody ?? Buffer.from('');
  const expected = hmacHex(WEBHOOK_SHARED_SECRET, raw.toString('utf8'));
  const expBuf = Buffer.from(expected, 'hex');
  const gotBuf = Buffer.from(String(sig), 'hex');
  if (expBuf.length !== gotBuf.length || !crypto.timingSafeEqual(expBuf, gotBuf)) {
    return reply.code(403).send({ ok: false, error: 'bad_webhook_signature' });
  }

  const { event_id, api_key, gross_cents, chain, txid } = req.body ?? {};
  if (!event_id || !api_key || !gross_cents) return reply.code(400).send({ ok: false, error: 'missing_fields' });

  // Ensure key exists
  try {
    await getKeyOrThrow(String(api_key));
  } catch (e) {
    return reply.code(e.statusCode ?? 400).send({ ok: false, error: e.message });
  }

  const gross = BigInt(Math.floor(Number(gross_cents)));
  if (gross <= 0n) return reply.code(400).send({ ok: false, error: 'bad_gross_cents' });

  const fee = (gross * BigInt(FEE_BPS) + 5000n) / 10000n; // rounded
  const net = gross - fee;

  const client = await pool.connect();
  try {
    await client.query('BEGIN');

    // idempotency
    const exists = await client.query('SELECT id FROM credits WHERE provider=$1 AND event_id=$2', [provider, String(event_id)]);
    if (exists.rows[0]) {
      await client.query('COMMIT');
      return {
        ok: true,
        provider,
        fee: {
          bps: FEE_BPS,
          fee_cents: Number(fee),
          fee_eth_address: FEE_ETH_ADDRESS,
          fee_btc_address: FEE_BTC_ADDRESS
        },
        idempotent: true,
        credited_cents: 0
      };
    }

    const before = await getBalanceCents(client, String(api_key), true);
    const after = before + net;
    await upsertBalanceCents(client, String(api_key), after);

    const creditId = id('cr');
    await client.query(
      'INSERT INTO credits(id, api_key_id, provider, event_id, gross_cents, fee_cents, net_cents, chain, txid) VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9)',
      [creditId, String(api_key), provider, String(event_id), gross, fee, net, chain ? String(chain) : null, txid ? String(txid) : null]
    );

    await client.query('COMMIT');

    return {
      ok: true,
      provider,
      fee: {
        bps: FEE_BPS,
        fee_cents: Number(fee),
        fee_eth_address: FEE_ETH_ADDRESS,
        fee_btc_address: FEE_BTC_ADDRESS
      },
      idempotent: false,
      credited_cents: Number(net)
    };
  } catch (e) {
    try { await client.query('ROLLBACK'); } catch {}
    return reply.code(500).send({ ok: false, error: 'credit_failed' });
  } finally {
    client.release();
  }
});

// Admin: create key quickly
app.post('/v1/admin/create-key', async (req, reply) => {
  const token = req.headers['authorization']?.replace(/^Bearer\s+/i, '');
  if (!ADMIN_TOKEN || token !== ADMIN_TOKEN) return reply.code(403).send({ ok: false, error: 'forbidden' });

  const starting = BigInt(Math.floor(Number(req.body?.starting_balance_cents ?? 0)));
  const apiKeyId = id('key');
  const secret = crypto.randomBytes(24).toString('hex');

  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    await client.query('INSERT INTO api_keys(id, secret, disabled_at) VALUES($1,$2,NULL)', [apiKeyId, secret]);
    await upsertBalanceCents(client, apiKeyId, starting);
    await client.query('COMMIT');

    return { ok: true, api_key: apiKeyId, api_secret: secret, starting_balance_cents: Number(starting) };
  } catch (e) {
    try { await client.query('ROLLBACK'); } catch {}
    return reply.code(500).send({ ok: false, error: 'admin_create_key_failed' });
  } finally {
    client.release();
  }
});

app.setErrorHandler((err, req, reply) => {
  const status = err.statusCode ?? 500;
  reply.code(status).send({ ok: false, error: err.message });
});

await migrate();
app.listen({ port: PORT, host: HOST });
