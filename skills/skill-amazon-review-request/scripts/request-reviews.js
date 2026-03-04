#!/usr/bin/env node
/**
 * request-reviews.js
 * Hardened Amazon Review Request script (skill version)
 *
 * Enhancements over original:
 *   - Eligibility window: only orders 5–30 days old (Amazon's allowed window)
 *   - Deduplication: skips orders already logged as 'sent'
 *   - Retry logic: up to 3 attempts with 5s delay on failure
 *   - Tracking: persists results to data/review-requests-log.json
 *   - Dry-run: --dry-run flag shows what would be sent without sending
 *   - Summary: sent / skipped / failed / dry-run counts
 *
 * Usage:
 *   node request-reviews.js              # Live run
 *   node request-reviews.js --dry-run    # Dry run
 *
 * Credentials loaded from ~/amazon-sp-api.json (or SP_API_PATH env):
 *   { refreshToken, clientId, clientSecret, marketplaceId }
 *
 * Or set env vars:
 *   SP_API_REFRESH_TOKEN, SP_API_CLIENT_ID, SP_API_CLIENT_SECRET, SP_API_MARKETPLACE_ID
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// ── Config ──────────────────────────────────────────────────────────────────
const DRY_RUN = process.argv.includes('--dry-run');
const RATE_LIMIT_MS = 1100;        // 1 req/sec (safe margin)
const RETRY_MAX = 3;
const RETRY_DELAY_MS = 5000;
const ELIGIBILITY_MIN_DAYS = 5;
const ELIGIBILITY_MAX_DAYS = 30;

const CREDS_FILE = process.env.SP_API_PATH || require('os').homedir() + '/amazon-sp-api.json';
const LOG_FILE = path.join(__dirname, '../../data/review-requests-log.json');
const TEXT_LOG = path.join(__dirname, '../../data/review-requests.log');

// ── Load credentials ─────────────────────────────────────────────────────────
let creds = {};
if (fs.existsSync(CREDS_FILE)) {
  creds = JSON.parse(fs.readFileSync(CREDS_FILE, 'utf8'));
}

const SP_API_REFRESH_TOKEN  = process.env.SP_API_REFRESH_TOKEN  || creds.refreshToken;
const SP_API_CLIENT_ID      = process.env.SP_API_CLIENT_ID      || creds.clientId;
const SP_API_CLIENT_SECRET  = process.env.SP_API_CLIENT_SECRET  || creds.clientSecret;
const SP_API_MARKETPLACE_ID = process.env.SP_API_MARKETPLACE_ID || creds.marketplaceId;

// ── Supabase ──────────────────────────────────────────────────────────────────
const SUPABASE_CREDS_FILE = process.env.SUPABASE_API_PATH || require('os').homedir() + '/supabase-api.json';
let supabaseCfg = null;
try {
  supabaseCfg = JSON.parse(fs.readFileSync(SUPABASE_CREDS_FILE, 'utf8'));
} catch {
  // Supabase optional — fall back to local JSON log only
}

async function supabaseInsert(table, row) {
  if (!supabaseCfg) return;
  const { url, key } = supabaseCfg;
  const apiUrl = new URL(`/rest/v1/${table}`, url);
  return new Promise((resolve) => {
    const body = JSON.stringify(row);
    const req = require('https').request({
      hostname: apiUrl.hostname,
      path: apiUrl.pathname + apiUrl.search,
      method: 'POST',
      headers: {
        apikey: key,
        Authorization: `Bearer ${key}`,
        'Content-Type': 'application/json',
        Prefer: 'return=minimal',
        'Content-Length': Buffer.byteLength(body),
      },
    }, (res) => {
      res.resume();
      resolve(res.statusCode);
    });
    req.on('error', () => resolve(null));
    req.write(body);
    req.end();
  });
}

async function supabaseAlreadySent(orderId) {
  if (!supabaseCfg) return false;
  const { url, key } = supabaseCfg;
  const apiUrl = new URL(`/rest/v1/review_requests?order_id=eq.${orderId}&status=eq.sent&select=order_id`, url);
  return new Promise((resolve) => {
    const req = require('https').request({
      hostname: apiUrl.hostname,
      path: apiUrl.pathname + apiUrl.search,
      method: 'GET',
      headers: {
        apikey: key,
        Authorization: `Bearer ${key}`,
        Accept: 'application/json',
      },
    }, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try {
          const rows = JSON.parse(data);
          resolve(Array.isArray(rows) && rows.length > 0);
        } catch {
          resolve(false);
        }
      });
    });
    req.on('error', () => resolve(false));
    req.end();
  });
}

async function logToSupabase(orderId, asin, status, error = null) {
  await supabaseInsert('review_requests', {
    order_id: orderId,
    asin: asin || null,
    status,
    attempted_at: new Date().toISOString(),
    error: error || null,
  });
}

// ── Logging ──────────────────────────────────────────────────────────────────
function log(msg) {
  const line = `[${new Date().toISOString()}] ${msg}`;
  console.log(line);
  fs.appendFileSync(TEXT_LOG, line + '\n');
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ── JSON tracking log ────────────────────────────────────────────────────────
function loadLog() {
  if (!fs.existsSync(LOG_FILE)) return [];
  try {
    return JSON.parse(fs.readFileSync(LOG_FILE, 'utf8'));
  } catch {
    return [];
  }
}

function saveLog(entries) {
  fs.mkdirSync(path.dirname(LOG_FILE), { recursive: true });
  fs.writeFileSync(LOG_FILE, JSON.stringify(entries, null, 2));
}

function isAlreadySent(entries, orderId) {
  return entries.some(e => e.orderId === orderId && e.status === 'sent');
}

function upsertEntry(entries, entry) {
  const idx = entries.findIndex(e => e.orderId === entry.orderId);
  if (idx >= 0) entries[idx] = entry;
  else entries.push(entry);
}

// ── Eligibility window ───────────────────────────────────────────────────────
function isEligible(order) {
  const purchaseDate = new Date(order.PurchaseDate);
  const now = Date.now();
  const ageMs = now - purchaseDate.getTime();
  const ageDays = ageMs / (1000 * 60 * 60 * 24);
  return ageDays >= ELIGIBILITY_MIN_DAYS && ageDays <= ELIGIBILITY_MAX_DAYS;
}

// ── HTTP helper ──────────────────────────────────────────────────────────────
function httpsRequest(options, body = null) {
  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve({ status: res.statusCode, body: data ? JSON.parse(data) : {} });
        } catch {
          resolve({ status: res.statusCode, body: data });
        }
      });
    });
    req.on('error', reject);
    if (body !== null) req.write(JSON.stringify(body));
    req.end();
  });
}

// ── SP-API: access token ─────────────────────────────────────────────────────
async function getAccessToken() {
  const body = new URLSearchParams({
    grant_type: 'refresh_token',
    refresh_token: SP_API_REFRESH_TOKEN,
    client_id: SP_API_CLIENT_ID,
    client_secret: SP_API_CLIENT_SECRET,
  }).toString();

  return new Promise((resolve, reject) => {
    const req = https.request({
      hostname: 'api.amazon.com',
      path: '/auth/o2/token',
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': Buffer.byteLength(body),
      },
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        const parsed = JSON.parse(data);
        if (parsed.access_token) resolve(parsed.access_token);
        else reject(new Error(`Token error: ${data}`));
      });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

// ── SP-API: fetch orders ─────────────────────────────────────────────────────
async function getShippedOrders(accessToken) {
  const createdAfter = new Date(Date.now() - ELIGIBILITY_MAX_DAYS * 24 * 60 * 60 * 1000).toISOString();
  const query = new URLSearchParams({
    MarketplaceIds: SP_API_MARKETPLACE_ID,
    OrderStatuses: 'Shipped',
    CreatedAfter: createdAfter,
  });

  const result = await httpsRequest({
    hostname: 'sellingpartnerapi-eu.amazon.com',
    path: `/orders/v0/orders?${query.toString()}`,
    method: 'GET',
    headers: {
      'x-amz-access-token': accessToken,
      'Content-Type': 'application/json',
    },
  });

  if (result.status !== 200) throw new Error(`Orders fetch failed: ${JSON.stringify(result.body)}`);
  return result.body?.payload?.Orders || [];
}

// ── SP-API: request review (single attempt) ──────────────────────────────────
async function requestReviewOnce(accessToken, orderId) {
  return httpsRequest({
    hostname: 'sellingpartnerapi-eu.amazon.com',
    path: `/messaging/v1/orders/${orderId}/messages/requestReview?marketplaceIds=${SP_API_MARKETPLACE_ID}`,
    method: 'POST',
    headers: {
      'x-amz-access-token': accessToken,
      'Content-Type': 'application/json',
    },
  }, {});
}

// ── SP-API: request review with retry ───────────────────────────────────────
async function requestReviewWithRetry(accessToken, orderId) {
  let lastError = null;
  for (let attempt = 1; attempt <= RETRY_MAX; attempt++) {
    try {
      const result = await requestReviewOnce(accessToken, orderId);
      // 4xx (except 429) are permanent — don't retry
      if (result.status === 429 || result.status >= 500) {
        log(`  ⚠️  Attempt ${attempt}/${RETRY_MAX} failed (${result.status}) for ${orderId}. Retrying in ${RETRY_DELAY_MS / 1000}s…`);
        lastError = result;
        if (attempt < RETRY_MAX) await sleep(RETRY_DELAY_MS);
        continue;
      }
      return { result, attempts: attempt };
    } catch (err) {
      log(`  ⚠️  Attempt ${attempt}/${RETRY_MAX} threw for ${orderId}: ${err.message}`);
      lastError = err;
      if (attempt < RETRY_MAX) await sleep(RETRY_DELAY_MS);
    }
  }
  throw lastError instanceof Error ? lastError : new Error(`HTTP ${lastError?.status}: ${JSON.stringify(lastError?.body)}`);
}

// ── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  log(`=== Amazon Review Request START${DRY_RUN ? ' [DRY RUN]' : ''} ===`);

  if (!SP_API_REFRESH_TOKEN || !SP_API_CLIENT_ID || !SP_API_CLIENT_SECRET || !SP_API_MARKETPLACE_ID) {
    log('ERROR: Missing credentials. Provide ~/amazon-sp-api.json or set SP_API_PATH / env vars.');
    process.exit(1);
  }

  // Load existing log for deduplication
  const logEntries = loadLog();
  log(`Loaded ${logEntries.length} existing log entries.`);

  // Get access token
  log('Fetching access token…');
  const accessToken = await getAccessToken();
  log('Access token obtained.');

  // Fetch orders
  log(`Fetching Shipped orders (last ${ELIGIBILITY_MAX_DAYS} days)…`);
  const orders = await getShippedOrders(accessToken);
  log(`Found ${orders.length} shipped orders.`);

  let sent = 0, failed = 0, skipped = 0, dryRun = 0;

  for (const order of orders) {
    const orderId = order.AmazonOrderId;
    await sleep(RATE_LIMIT_MS);

    // Deduplication — check Supabase first, then local log
    const inSupabase = await supabaseAlreadySent(orderId);
    if (inSupabase || isAlreadySent(logEntries, orderId)) {
      log(`⏭️  Skip (already sent): ${orderId}`);
      skipped++;
      continue;
    }

    // Eligibility window
    if (!isEligible(order)) {
      const purchaseDate = new Date(order.PurchaseDate);
      const ageDays = ((Date.now() - purchaseDate.getTime()) / 86400000).toFixed(1);
      log(`⏭️  Skip (age ${ageDays}d, outside 5–30d window): ${orderId}`);
      skipped++;
      continue;
    }

    // Dry-run
    if (DRY_RUN) {
      log(`[DRY RUN] Would send review request for: ${orderId}`);
      dryRun++;
      continue;
    }

    // Send with retry
    try {
      const { result, attempts } = await requestReviewWithRetry(accessToken, orderId);

      const asin = order.OrderItems?.[0]?.ASIN || null;
      if (result.status === 201 || result.status === 200) {
        log(`✅ Sent (${attempts} attempt${attempts > 1 ? 's' : ''}): ${orderId}`);
        upsertEntry(logEntries, { orderId, sentAt: new Date().toISOString(), status: 'sent', attempts });
        await logToSupabase(orderId, asin, 'sent');
        sent++;
      } else if (result.status === 400 || result.status === 403) {
        const reason = `HTTP ${result.status}`;
        log(`⚠️  Skipped ${orderId} (${result.status}): ${JSON.stringify(result.body)}`);
        upsertEntry(logEntries, { orderId, sentAt: new Date().toISOString(), status: 'skipped', attempts: 1, reason });
        await logToSupabase(orderId, asin, 'skipped', reason);
        skipped++;
      } else {
        const reason = `HTTP ${result.status}`;
        log(`❌ Failed ${orderId} (${result.status}): ${JSON.stringify(result.body)}`);
        upsertEntry(logEntries, { orderId, sentAt: new Date().toISOString(), status: 'failed', attempts: RETRY_MAX, reason });
        await logToSupabase(orderId, asin, 'failed', reason);
        failed++;
      }
    } catch (err) {
      log(`❌ Error for ${orderId}: ${err.message}`);
      upsertEntry(logEntries, { orderId, sentAt: new Date().toISOString(), status: 'failed', attempts: RETRY_MAX, reason: err.message });
      await logToSupabase(orderId, null, 'failed', err.message);
      failed++;
    }

    // Persist after each order (safe against mid-run crashes)
    saveLog(logEntries);
  }

  // Final summary
  if (DRY_RUN) {
    log(`=== DONE [DRY RUN] | Would send: ${dryRun} | Skipped: ${skipped} ===`);
  } else {
    log(`=== DONE | Sent: ${sent} | Skipped: ${skipped} | Failed: ${failed} ===`);
  }
}

main().catch(err => {
  log(`FATAL: ${err.message}`);
  process.exit(1);
});
