#!/usr/bin/env node
/**
 * CJ Fulfillment Engine
 *
 * Fetches WooCommerce "processing" orders, matches line items to CJ variants
 * via cj-supplier-selection.json, and submits orders to CJ Dropshipping.
 *
 * Usage:
 *   node fulfill.js [--dry-run] [--order <woo_order_id>]
 *
 * --dry-run   Preview what would be submitted without actually placing orders
 * --order ID  Process only a specific WooCommerce order ID
 */

const fs = require('fs');
const axios = require('axios');

const WOO_API_PATH = process.env.WOO_API_PATH || '/home/aladdin/woo-api.json';
const CJ_API_PATH = process.env.CJ_API_PATH || '/home/aladdin/cj-api.json';
const SELECTION_PATH = process.env.CJ_SELECTION_PATH || '/home/aladdin/cj-supplier-selection.json';
const LOG_PATH = process.env.FULFILL_LOG_PATH || '/home/aladdin/cj-fulfillment-log.json';
const REJECTION_LOG_PATH = process.env.REJECTION_LOG_PATH || '/home/aladdin/cj-rejection-log.json';

const args = process.argv.slice(2);
const DRY_RUN = args.includes('--dry-run');
const ORDER_FILTER = (() => {
  const i = args.indexOf('--order');
  return i >= 0 ? String(args[i + 1]) : null;
})();

// FBA/excluded product IDs — never fulfilled via CJ
// Set via env: FBA_PRODUCT_IDS=75927,75808,2382 or leave empty for none
const FBA_PRODUCT_IDS = new Set(
  (process.env.FBA_PRODUCT_IDS || '').split(',').map(s => parseInt(s.trim())).filter(Boolean)
);

// ── Utility ───────────────────────────────────────────────────────────────

function readJson(p) {
  if (!fs.existsSync(p)) return [];
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}

function appendLog(entry) {
  const log = readJson(LOG_PATH);
  const arr = Array.isArray(log) ? log : [];
  arr.push({ ...entry, timestamp: new Date().toISOString() });
  fs.writeFileSync(LOG_PATH, JSON.stringify(arr, null, 2));
}

function appendRejectionLog(entry) {
  const existing = readJson(REJECTION_LOG_PATH);
  const log = Array.isArray(existing) ? existing : [];
  log.unshift({ ...entry, timestamp: new Date().toISOString() });
  if (log.length > 500) log.splice(500);
  fs.writeFileSync(REJECTION_LOG_PATH, JSON.stringify(log, null, 2));
}

async function withRetry(fn, label, retries = 1) {
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      return await fn();
    } catch (err) {
      const isNetwork = err.code && ['ECONNRESET', 'ETIMEDOUT', 'ECONNREFUSED', 'ENOTFOUND'].includes(err.code);
      if (attempt < retries && isNetwork) {
        console.log(`  ⟳ Retrying ${label} (attempt ${attempt + 2})...`);
        await new Promise(r => setTimeout(r, 2000));
      } else {
        throw err;
      }
    }
  }
}

// ── WooCommerce ───────────────────────────────────────────────────────────

function wooCfg() {
  const cfg = JSON.parse(fs.readFileSync(WOO_API_PATH, 'utf8'));
  const base = cfg.url.replace(/\/$/, '') + '/wp-json/wc/v3';
  const auth = { username: cfg.consumerKey, password: cfg.consumerSecret };
  return { base, auth };
}

async function getOrders(status = 'processing', perPage = 50) {
  const { base, auth } = wooCfg();
  const res = await axios.get(`${base}/orders`, {
    auth,
    params: { status, per_page: perPage, orderby: 'date', order: 'asc' },
    timeout: 30000,
  });
  return res.data;
}

async function updateOrderStatus(orderId, status) {
  const { base, auth } = wooCfg();
  const res = await axios.put(`${base}/orders/${orderId}`, { status }, { auth, timeout: 30000 });
  return res.data;
}

async function addOrderNote(orderId, note, customerNote = false) {
  const { base, auth } = wooCfg();
  const res = await axios.post(`${base}/orders/${orderId}/notes`, {
    note,
    customer_note: customerNote,
  }, { auth, timeout: 30000 });
  return res.data;
}

// ── CJ API ────────────────────────────────────────────────────────────────

function cjCfg() {
  return JSON.parse(fs.readFileSync(CJ_API_PATH, 'utf8'));
}

async function cjEnsureToken() {
  const cfg = cjCfg();
  const now = Date.now();
  const exp = Number(cfg.tokenExpiry || 0);
  if (cfg.accessToken && exp && now < exp - 10 * 60 * 1000) return cfg.accessToken;

  console.log('  🔑 Refreshing CJ access token...');
  const baseUrl = (cfg.baseUrl || 'https://developers.cjdropshipping.com/api2.0/v1').replace(/\/$/, '');
  const res = await axios.post(`${baseUrl}/authentication/getAccessToken`, { apiKey: cfg.apiKey }, {
    headers: { 'Content-Type': 'application/json' }, timeout: 30000,
  });
  if (!res.data?.result) throw new Error(`CJ token refresh failed: ${JSON.stringify(res.data).slice(0, 200)}`);
  const token = res.data.data.accessToken;
  cfg.accessToken = token;
  cfg.tokenExpiry = now + 14 * 24 * 3600 * 1000;
  fs.writeFileSync(CJ_API_PATH, JSON.stringify(cfg, null, 2));
  console.log('  ✅ CJ token refreshed');
  return token;
}

function cjBaseUrl() {
  return (cjCfg().baseUrl || 'https://developers.cjdropshipping.com/api2.0/v1').replace(/\/$/, '');
}

async function cjHeaders() {
  return { 'CJ-Access-Token': await cjEnsureToken(), 'Content-Type': 'application/json' };
}

async function createCjOrder(orderData) {
  const res = await axios.post(`${cjBaseUrl()}/shopping/order/createOrder`, orderData, {
    headers: await cjHeaders(),
    timeout: 60000,
  });
  return res.data;
}

// ── Selection / SKU map ───────────────────────────────────────────────────

/**
 * Build lookup maps from cj-supplier-selection.json:
 * - by SKU (uppercase)
 * - by wooProductId + wooVariationId
 * - by wooProductId alone (for simple products with wooVariationId === null)
 */
function buildMaps(selection) {
  const bySkU = {};
  const byWooId = {};  // key: "productId:variationId" or "productId:null"

  for (const item of selection) {
    if (item.sku) bySkU[item.sku.toUpperCase()] = item;
    const key = `${item.wooProductId}:${item.wooVariationId ?? 'null'}`;
    byWooId[key] = item;
  }

  return { bySkU, byWooId };
}

function findMatch(lineItem, maps) {
  // 1. Match by SKU first
  const sku = (lineItem.sku || '').toUpperCase();
  if (sku && maps.bySkU[sku]) return maps.bySkU[sku];

  // 2. Fall back to wooProductId + variationId
  const varId = lineItem.variation_id || null;
  const prodId = lineItem.product_id;
  const key = `${prodId}:${varId || 'null'}`;
  if (maps.byWooId[key]) return maps.byWooId[key];

  // 3. Try product ID with null variation (simple product)
  const simpleKey = `${prodId}:null`;
  if (maps.byWooId[simpleKey]) return maps.byWooId[simpleKey];

  return null;
}

// ── Order mapping ─────────────────────────────────────────────────────────

function mapOrder(order, maps) {
  const shipping = order.shipping || {};
  const billing = order.billing || {};

  const products = [];
  const unmatched = [];
  const fbaItems = [];

  for (const item of order.line_items || []) {
    const prodId = item.product_id;

    // FBA/LUUCCO exclusion
    if (FBA_PRODUCT_IDS.has(prodId)) {
      fbaItems.push({ id: item.id, name: item.name, productId: prodId });
      continue;
    }

    const match = findMatch(item, maps);
    if (!match) {
      unmatched.push({ id: item.id, name: item.name, sku: item.sku, productId: prodId, variationId: item.variation_id });
      continue;
    }

    products.push({
      vid: match.variantId || match.cjProductId,
      quantity: item.quantity,
      productName: item.name,
      matchedSku: match.sku,
    });
  }

  return {
    orderId: order.id,
    orderNumber: `WOO-${order.id}`,
    matched: products,
    unmatched,
    fbaItems,
    shippingName: `${shipping.first_name || ''} ${shipping.last_name || ''}`.trim()
      || `${billing.first_name || ''} ${billing.last_name || ''}`.trim(),
    shippingEmail: billing.email || '',
    shippingPhone: billing.phone || shipping.phone || '',
    shippingAddress: [shipping.address_1, shipping.address_2].filter(Boolean).join(', '),
    shippingCity: shipping.city || '',
    shippingProvince: shipping.state || '',
    shippingZip: shipping.postcode || '',
    shippingCountry: shipping.country || '',
  };
}

// ── Main ──────────────────────────────────────────────────────────────────

async function run() {
  console.log(`\n⚡ CJ Fulfillment Engine — ${DRY_RUN ? 'DRY RUN' : 'LIVE'}\n`);

  // Ensure CJ token is valid before processing
  await cjEnsureToken();

  const selection = readJson(SELECTION_PATH);
  if (!Array.isArray(selection) || !selection.length) {
    console.error(`❌ No products in selection file: ${SELECTION_PATH}`);
    console.error(`   Run: node scripts/rebuild-mapping.js`);
    process.exit(1);
  }
  const maps = buildMaps(selection);
  console.log(`✅ Loaded ${selection.length} entries from selection file`);

  // Fetch processing orders
  let orders = await withRetry(() => getOrders('processing', 50), 'fetch orders');
  if (ORDER_FILTER) {
    orders = orders.filter(o => String(o.id) === ORDER_FILTER);
    if (!orders.length) {
      console.log(`No processing order found with ID: ${ORDER_FILTER}`);
      process.exit(0);
    }
  }

  console.log(`📦 Found ${orders.length} processing order(s)\n`);

  if (!orders.length) {
    appendRejectionLog({
      type: 'no_orders',
      reason: 'zero_processing_orders',
      evaluated: { filter: ORDER_FILTER || 'all' },
      note: 'Engine ran successfully but found no processing orders to fulfill.',
    });
    return;
  }

  let submitted = 0;
  let skipped = 0;
  let failed = 0;

  for (const order of orders) {
    const mapped = mapOrder(order, maps);

    console.log(`\n--- Order #${mapped.orderId} ---`);
    console.log(`  Customer: ${mapped.shippingName} <${mapped.shippingEmail}>`);
    console.log(`  Address: ${mapped.shippingAddress}, ${mapped.shippingCity}, ${mapped.shippingCountry} ${mapped.shippingZip}`);

    // Log FBA items
    if (mapped.fbaItems.length) {
      console.log(`  🏷️  FBA items (manual fulfillment required):`);
      for (const f of mapped.fbaItems) {
        console.log(`       - ${f.name} (product #${f.productId}) — FBA product, manual fulfillment required`);
      }
    }

    console.log(`  Matched CJ items: ${mapped.matched.length}`);
    if (mapped.matched.length) {
      for (const m of mapped.matched) {
        console.log(`       ✓ ${m.productName} × ${m.quantity} (SKU: ${m.matchedSku}, vid: ${m.vid})`);
      }
    }

    if (mapped.unmatched.length) {
      console.log(`  ⚠️  Unmatched items:`);
      for (const u of mapped.unmatched) {
        console.log(`       - ${u.name} (SKU: ${u.sku || 'n/a'}, product #${u.productId})`);
      }
    }

    // Skip if no CJ items to fulfill
    if (!mapped.matched.length) {
      const reason = mapped.fbaItems.length && !mapped.unmatched.length
        ? 'all_items_fba'
        : 'no_matched_cj_items';
      console.log(`  ⏭️  Skipping — ${reason}`);
      skipped++;
      appendLog({ orderId: mapped.orderId, status: 'skipped', reason });
      appendRejectionLog({
        type: 'order_skipped',
        orderId: mapped.orderId,
        reason,
        evaluated: {
          totalLineItems: (order.line_items || []).length,
          fbaItems: mapped.fbaItems.map(f => ({ name: f.name, productId: f.productId })),
          unmatchedItems: mapped.unmatched.map(u => ({ name: u.name, sku: u.sku })),
        },
      });
      continue;
    }

    // Log partial matches
    if (mapped.unmatched.length > 0 || mapped.fbaItems.length > 0) {
      appendRejectionLog({
        type: 'partial_match',
        orderId: mapped.orderId,
        reason: 'some_items_not_cj',
        evaluated: {
          totalLineItems: (order.line_items || []).length,
          matchedCount: mapped.matched.length,
          unmatchedCount: mapped.unmatched.length,
          fbaCount: mapped.fbaItems.length,
        },
      });
    }

    const payload = {
      orderNumber: mapped.orderNumber,
      shippingZip: mapped.shippingZip,
      shippingCountry: mapped.shippingCountry,
      shippingCountryCode: mapped.shippingCountry,
      shippingProvince: mapped.shippingProvince,
      shippingCity: mapped.shippingCity,
      shippingAddress: mapped.shippingAddress,
      shippingPhone: mapped.shippingPhone,
      shippingCustomerName: mapped.shippingName,
      shippingEmail: mapped.shippingEmail,
      products: mapped.matched.map(p => ({ vid: p.vid, quantity: p.quantity })),
    };

    if (DRY_RUN) {
      console.log(`\n  🔍 DRY RUN — would submit payload:`);
      console.log('  ' + JSON.stringify(payload, null, 2).split('\n').join('\n  '));
      submitted++;
      continue;
    }

    try {
      const result = await withRetry(() => createCjOrder(payload), `create CJ order for #${mapped.orderId}`);
      if (result?.result) {
        const cjOrderId = result?.data?.orderId || 'unknown';
        console.log(`  ✅ CJ order created: ${cjOrderId}`);
        await withRetry(() => updateOrderStatus(mapped.orderId, 'on-hold'), 'update woo status');
        await withRetry(() => addOrderNote(mapped.orderId, `✅ CJ order submitted: ${cjOrderId}`), 'add order note');
        appendLog({ orderId: mapped.orderId, status: 'submitted', cjOrderId });
        submitted++;
      } else {
        const errDetail = JSON.stringify(result).slice(0, 300);
        console.error(`  ❌ CJ rejected: ${errDetail}`);
        appendLog({ orderId: mapped.orderId, status: 'failed', error: errDetail });
        appendRejectionLog({
          type: 'cj_api_rejection',
          orderId: mapped.orderId,
          reason: 'cj_api_returned_failure',
          evaluated: { payload, cjResponse: errDetail },
        });
        failed++;
      }
    } catch (err) {
      const errMsg = err.response
        ? `HTTP ${err.response.status}: ${JSON.stringify(err.response.data).slice(0, 200)}`
        : err.message;
      console.error(`  ❌ Error: ${errMsg}`);
      appendLog({ orderId: mapped.orderId, status: 'error', error: errMsg });
      appendRejectionLog({
        type: 'submission_error',
        orderId: mapped.orderId,
        reason: 'exception_thrown',
        evaluated: { errorMessage: errMsg },
      });
      failed++;
    }
  }

  console.log(`\n📊 Summary: ${submitted} submitted, ${skipped} skipped, ${failed} failed\n`);
}

run().catch(e => { console.error(e?.stack || String(e)); process.exit(1); });
