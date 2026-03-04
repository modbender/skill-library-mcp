import { readRawBody } from '../../../../../lib/rawBody.js';
import { env } from '../../../../../lib/env.js';
import { hmacHex, id, timingSafeHexEqual } from '../../../../../lib/crypto.js';
import { pool, migrate } from '../../../../../lib/db.js';
import { getKeyOrThrow } from '../../../../../lib/auth.js';

function header(headers, name) {
  const v = headers[name.toLowerCase()];
  return Array.isArray(v) ? v[0] : v;
}

function parseJsonOrThrow(rawText) {
  try {
    return rawText ? JSON.parse(rawText) : {};
  } catch {
    const err = new Error('invalid_json');
    err.statusCode = 400;
    throw err;
  }
}

// Returns either:
// - { event_id, api_key, gross_cents, chain, txid }  (credit this)
// - null (ignore event but return 202)
function normalizeAndVerify(provider, headers, rawText) {
  const body = parseJsonOrThrow(rawText);

  if (provider === 'demo') {
    const sig = header(headers, 'x-webhook-signature');
    if (!sig) throw Object.assign(new Error('missing_webhook_signature'), { statusCode: 401 });

    const expected = hmacHex(env('WEBHOOK_SHARED_SECRET', ''), rawText);
    if (!timingSafeHexEqual(expected, sig)) throw Object.assign(new Error('bad_webhook_signature'), { statusCode: 403 });

    const { event_id, api_key, gross_cents, chain, txid } = body ?? {};
    if (!event_id || !api_key || !gross_cents) throw Object.assign(new Error('missing_fields'), { statusCode: 400 });
    return { event_id, api_key, gross_cents, chain, txid };
  }

  if (provider === 'coinbase-commerce') {
    // Coinbase Commerce: X-CC-Webhook-Signature = HMAC_SHA256(secret, rawBody) hex
    const sig = header(headers, 'x-cc-webhook-signature');
    if (!sig) throw Object.assign(new Error('missing_coinbase_signature'), { statusCode: 401 });

    const secret = env('COINBASE_COMMERCE_WEBHOOK_SECRET', '');
    if (!secret) throw Object.assign(new Error('missing_coinbase_secret'), { statusCode: 500 });

    const expected = hmacHex(secret, rawText);
    if (!timingSafeHexEqual(expected, sig)) throw Object.assign(new Error('bad_coinbase_signature'), { statusCode: 403 });

    const type = String(body?.event?.type ?? '');
    if (!['charge:confirmed', 'charge:resolved'].includes(type)) return null;

    const eventId = String(body?.event?.id ?? body?.id ?? '');
    const apiKey = body?.event?.data?.metadata?.api_key;

    const amountStr = body?.event?.data?.pricing?.local?.amount ?? body?.event?.data?.pricing?.local_amount?.amount;
    const currency = body?.event?.data?.pricing?.local?.currency ?? body?.event?.data?.pricing?.local_amount?.currency ?? 'USD';

    if (!eventId || !apiKey || !amountStr) throw Object.assign(new Error('missing_fields'), { statusCode: 400 });
    if (String(currency).toUpperCase() !== 'USD') throw Object.assign(new Error('unsupported_currency'), { statusCode: 400 });

    const grossCents = Math.round(Number(amountStr) * 100);
    const txid = body?.event?.data?.payments?.[0]?.transaction_id ?? null;

    return { event_id: eventId, api_key: String(apiKey), gross_cents: grossCents, chain: 'MULTI', txid };
  }

  if (provider === 'btcpay') {
    // BTCPay: BTCPay-Sig header often "sha256=<hex>".
    const sig = header(headers, 'btcpay-sig');
    if (!sig) throw Object.assign(new Error('missing_btcpay_signature'), { statusCode: 401 });

    const secret = env('BTCPAY_WEBHOOK_SECRET', '');
    if (!secret) throw Object.assign(new Error('missing_btcpay_secret'), { statusCode: 500 });

    const expected = hmacHex(secret, rawText);
    const provided = String(sig).includes('=') ? String(sig).split('=')[1] : String(sig);
    if (!timingSafeHexEqual(expected, provided)) throw Object.assign(new Error('bad_btcpay_signature'), { statusCode: 403 });

    const eventType = String(body?.type ?? body?.eventType ?? '');
    if (!['InvoiceSettled', 'InvoiceCompleted', 'InvoiceConfirmed'].includes(eventType)) return null;

    const eventId = String(body?.id ?? body?.eventId ?? '');
    const invoice = body?.invoice ?? body?.data ?? body;
    const apiKey = invoice?.metadata?.api_key;

    const amount = invoice?.amount ?? invoice?.price ?? invoice?.checkout?.amount;
    const currency = invoice?.currency ?? invoice?.checkout?.currency ?? 'USD';

    if (!eventId || !apiKey || amount == null) throw Object.assign(new Error('missing_fields'), { statusCode: 400 });
    if (String(currency).toUpperCase() !== 'USD') throw Object.assign(new Error('unsupported_currency'), { statusCode: 400 });

    const grossCents = Math.round(Number(amount) * 100);
    const txid = invoice?.payments?.[0]?.id ?? null;

    return { event_id: eventId, api_key: String(apiKey), gross_cents: grossCents, chain: 'BTC', txid };
  }

  throw Object.assign(new Error('unknown_provider'), { statusCode: 404 });
}

export const config = { api: { bodyParser: false } };

let migrated = false;

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ ok: false, error: 'method_not_allowed' });

  if (!migrated) {
    await migrate();
    migrated = true;
  }

  const provider = String(req.query.provider);
  const rawBody = await readRawBody(req, Number(env('MAX_BODY_BYTES', '200000')));
  const rawText = rawBody.toString('utf8');

  let normalized;
  try {
    normalized = normalizeAndVerify(provider, req.headers, rawText);
  } catch (e) {
    return res.status(e.statusCode ?? 400).json({ ok: false, error: e.message });
  }

  if (normalized === null) {
    return res.status(202).json({ ok: true, provider, ignored: true });
  }

  const { event_id, api_key, gross_cents, chain, txid } = normalized;

  try {
    await getKeyOrThrow(String(api_key));
  } catch (e) {
    return res.status(e.statusCode ?? 400).json({ ok: false, error: e.message });
  }

  const gross = BigInt(Math.floor(Number(gross_cents)));
  if (gross <= 0n) return res.status(400).json({ ok: false, error: 'bad_gross_cents' });

  const FEE_BPS = BigInt(Number(env('FEE_BPS', '250')));
  const fee = (gross * FEE_BPS + 5000n) / 10000n;
  const net = gross - fee;

  const FEE_ETH_ADDRESS = env('FEE_ETH_ADDRESS', '');
  const FEE_BTC_ADDRESS = env('FEE_BTC_ADDRESS', '');

  const client = await pool().connect();
  try {
    await client.query('BEGIN');

    const exists = await client.query('SELECT id FROM credits WHERE provider=$1 AND event_id=$2', [provider, String(event_id)]);
    if (exists.rows[0]) {
      await client.query('COMMIT');
      return res.status(200).json({
        ok: true,
        provider,
        fee: { bps: Number(FEE_BPS), fee_cents: Number(fee), fee_eth_address: FEE_ETH_ADDRESS, fee_btc_address: FEE_BTC_ADDRESS },
        idempotent: true,
        credited_cents: 0
      });
    }

    const balRes = await client.query('SELECT balance_cents FROM balances WHERE api_key_id=$1 FOR UPDATE', [String(api_key)]);
    const before = balRes.rows[0] ? BigInt(balRes.rows[0].balance_cents) : 0n;
    const after = before + net;

    await client.query(
      `INSERT INTO balances(api_key_id, balance_cents) VALUES($1, $2)
       ON CONFLICT (api_key_id) DO UPDATE SET balance_cents=EXCLUDED.balance_cents, updated_at=now()`,
      [String(api_key), after]
    );

    const creditId = id('cr');
    await client.query(
      'INSERT INTO credits(id, api_key_id, provider, event_id, gross_cents, fee_cents, net_cents, chain, txid) VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9)',
      [creditId, String(api_key), provider, String(event_id), gross, fee, net, chain ? String(chain) : null, txid ? String(txid) : null]
    );

    await client.query('COMMIT');

    return res.status(200).json({
      ok: true,
      provider,
      fee: { bps: Number(FEE_BPS), fee_cents: Number(fee), fee_eth_address: FEE_ETH_ADDRESS, fee_btc_address: FEE_BTC_ADDRESS },
      idempotent: false,
      credited_cents: Number(net)
    });
  } catch {
    try { await client.query('ROLLBACK'); } catch {}
    return res.status(500).json({ ok: false, error: 'credit_failed' });
  } finally {
    client.release();
  }
}
