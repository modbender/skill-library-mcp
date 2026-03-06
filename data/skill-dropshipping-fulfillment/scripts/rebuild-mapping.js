#!/usr/bin/env node
/**
 * Rebuild CJ supplier selection mapping + backfill WooCommerce SKUs
 *
 * Usage:
 *   node scripts/rebuild-mapping.js [--dry-run]
 *
 * What it does:
 *  1. Fetches all published WooCommerce products (excluding LUUCCO/FBA IDs)
 *  2. For each product with _cj_product_id meta, queries CJ for variant list
 *  3. Matches WooCommerce variations to CJ variants by attributes
 *  4. Backfills SKUs on WooCommerce products/variations if missing
 *  5. Writes ./cj-supplier-selection.json with proper mappings
 */

const axios = require('axios');
const fs = require('fs');

const WOO_API_PATH = process.env.WOO_API_PATH || '/home/aladdin/woo-api.json';
const CJ_API_PATH = process.env.CJ_API_PATH || '/home/aladdin/cj-api.json';
const SELECTION_PATH = process.env.CJ_SELECTION_PATH || '/home/aladdin/cj-supplier-selection.json';

const DRY_RUN = process.argv.includes('--dry-run');

// FBA/excluded product IDs — customize via env FBA_PRODUCT_IDS=id1,id2,...
const LUUCCO_IDS = new Set(
  (process.env.FBA_PRODUCT_IDS || '').split(',').map(s => parseInt(s.trim())).filter(Boolean)
);

function readJson(p) {
  if (!fs.existsSync(p)) return null;
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}

// ── WooCommerce helpers ────────────────────────────────────────────────────

function wooCreds() {
  const cfg = readJson(WOO_API_PATH);
  const base = cfg.url.replace(/\/$/, '') + '/wp-json/wc/v3';
  const auth = { username: cfg.consumerKey, password: cfg.consumerSecret };
  return { base, auth };
}

async function wooGet(path, params = {}) {
  const { base, auth } = wooCreds();
  const res = await axios.get(`${base}${path}`, { auth, params, timeout: 30000 });
  return res.data;
}

async function wooPut(path, data) {
  const { base, auth } = wooCreds();
  const res = await axios.put(`${base}${path}`, data, { auth, timeout: 30000 });
  return res.data;
}

async function getAllPublishedProducts() {
  let page = 1;
  const all = [];
  while (true) {
    const batch = await wooGet('/products', { status: 'publish', per_page: 100, page });
    if (!batch.length) break;
    all.push(...batch);
    if (batch.length < 100) break;
    page++;
  }
  return all;
}

async function getVariations(productId) {
  let page = 1;
  const all = [];
  while (true) {
    const batch = await wooGet(`/products/${productId}/variations`, { per_page: 100, page });
    if (!batch.length) break;
    all.push(...batch);
    if (batch.length < 100) break;
    page++;
  }
  return all;
}

function getMeta(product, key) {
  const m = (product.meta_data || []).find(x => x.key === key);
  return m ? m.value : null;
}

// ── CJ helpers ────────────────────────────────────────────────────────────

async function cjEnsureToken() {
  const cfg = readJson(CJ_API_PATH);
  const now = Date.now();
  const exp = Number(cfg.tokenExpiry || 0);
  if (cfg.accessToken && exp && now < exp - 10 * 60 * 1000) return cfg.accessToken;

  const baseUrl = (cfg.baseUrl || 'https://developers.cjdropshipping.com/api2.0/v1').replace(/\/$/, '');
  const res = await axios.post(`${baseUrl}/authentication/getAccessToken`, { apiKey: cfg.apiKey }, {
    headers: { 'Content-Type': 'application/json' }, timeout: 30000,
  });
  if (!res.data?.result) throw new Error(`CJ token refresh failed: ${JSON.stringify(res.data).slice(0, 200)}`);
  const token = res.data.data.accessToken;
  cfg.accessToken = token;
  cfg.tokenExpiry = now + 14 * 24 * 3600 * 1000;
  fs.writeFileSync(CJ_API_PATH, JSON.stringify(cfg, null, 2));
  return token;
}

async function cjGet(path, params = {}) {
  const cfg = readJson(CJ_API_PATH);
  const baseUrl = (cfg.baseUrl || 'https://developers.cjdropshipping.com/api2.0/v1').replace(/\/$/, '');
  const token = await cjEnsureToken();
  const res = await axios.get(`${baseUrl}${path}`, {
    headers: { 'CJ-Access-Token': token, 'Content-Type': 'application/json' },
    params,
    timeout: 30000,
  });
  return res.data;
}

async function getCjProductVariants(cjProductId) {
  try {
    const res = await cjGet('/product/variant/query', { pid: cjProductId });
    if (res.result && Array.isArray(res.data)) return res.data;
    // fallback: try as vid
    return [];
  } catch (e) {
    console.error(`  ⚠️  CJ variant query failed for ${cjProductId}: ${e.message}`);
    return [];
  }
}

async function getCjProductDetail(cjProductId) {
  try {
    const res = await cjGet('/product/query', { pid: cjProductId });
    if (res.result && res.data) return res.data;
    return null;
  } catch (e) {
    console.error(`  ⚠️  CJ product detail failed for ${cjProductId}: ${e.message}`);
    return null;
  }
}

// ── Attribute matching ────────────────────────────────────────────────────

/**
 * Given a WooCommerce variation (has attributes array) and a list of CJ variants,
 * try to find the best match by attribute values (case-insensitive).
 */
function matchVariantByAttributes(wooVariation, cjVariants) {
  if (!cjVariants.length) return null;
  if (cjVariants.length === 1) return cjVariants[0];

  const wooAttrs = (wooVariation.attributes || []).map(a => a.option?.toLowerCase?.() || '');

  let best = null;
  let bestScore = -1;
  for (const v of cjVariants) {
    // CJ variant name typically looks like "Red,L" or "Blue"
    const vName = (v.variantKey || v.variantNameEn || v.sku || '').toLowerCase();
    let score = 0;
    for (const wa of wooAttrs) {
      if (wa && vName.includes(wa)) score++;
    }
    if (score > bestScore) {
      bestScore = score;
      best = v;
    }
  }
  return best;
}

// ── Main ──────────────────────────────────────────────────────────────────

async function main() {
  console.log(`\n🔧 CJ Mapping Rebuild — ${DRY_RUN ? 'DRY RUN' : 'LIVE'}\n`);

  // Ensure CJ token works
  console.log('🔑 Verifying CJ token...');
  await cjEnsureToken();
  console.log('✅ CJ token OK\n');

  console.log('📥 Fetching published WooCommerce products...');
  const allProducts = await getAllPublishedProducts();
  console.log(`   Found ${allProducts.length} published products\n`);

  const cjProducts = allProducts.filter(p => {
    if (LUUCCO_IDS.has(p.id)) return false;
    const cjId = getMeta(p, '_cj_product_id');
    return !!cjId;
  });

  const luuccoCount = allProducts.filter(p => LUUCCO_IDS.has(p.id)).length;
  const noCjMeta = allProducts.filter(p => !LUUCCO_IDS.has(p.id) && !getMeta(p, '_cj_product_id')).length;
  console.log(`📊 Breakdown:`);
  console.log(`   ${cjProducts.length} CJ dropship products`);
  console.log(`   ${luuccoCount} LUUCCO/FBA (skipped)`);
  console.log(`   ${noCjMeta} no CJ meta (skipped)\n`);

  const selectionEntries = [];
  let skuBackfillCount = 0;

  for (const product of cjProducts) {
    const cjProductId = getMeta(product, '_cj_product_id');
    console.log(`\n🛍️  Product #${product.id}: ${product.name.slice(0, 60)}`);
    console.log(`   CJ Product ID: ${cjProductId}`);

    // Fetch CJ product detail + variants
    const cjDetail = await getCjProductDetail(cjProductId);
    const cjVariants = await getCjProductVariants(cjProductId);

    console.log(`   CJ variants found: ${cjVariants.length}`);

    if (product.type === 'simple') {
      // Simple product — use first/only variant or product-level SKU
      const cjVariant = cjVariants[0] || null;
      const sku = cjVariant?.sku || cjDetail?.productSku || getMeta(product, '_cj_sku') || '';

      // Backfill WooCommerce SKU if missing
      if (!product.sku && sku && !DRY_RUN) {
        console.log(`   📝 Backfilling SKU: ${sku}`);
        await wooPut(`/products/${product.id}`, { sku });
        skuBackfillCount++;
      } else if (!product.sku && sku) {
        console.log(`   📝 [DRY RUN] Would set SKU: ${sku}`);
        skuBackfillCount++;
      }

      selectionEntries.push({
        wooProductId: product.id,
        wooVariationId: null,
        sku: sku || product.sku || '',
        cjProductId,
        variantId: cjVariant?.vid || cjVariant?.variantId || '',
        productName: product.name,
      });

    } else if (product.type === 'variable') {
      // Variable product — fetch each variation and match to CJ variant
      const variations = await getVariations(product.id);
      console.log(`   Woo variations: ${variations.length}`);

      for (const variation of variations) {
        const matched = matchVariantByAttributes(variation, cjVariants);
        const sku = matched?.sku || variation.sku || '';

        if (!variation.sku && sku && !DRY_RUN) {
          console.log(`   📝 Variation #${variation.id} — backfilling SKU: ${sku}`);
          await wooPut(`/products/${product.id}/variations/${variation.id}`, { sku });
          skuBackfillCount++;
        } else if (!variation.sku && sku) {
          const attrStr = (variation.attributes || []).map(a => a.option).join('/');
          console.log(`   📝 [DRY RUN] Variation #${variation.id} (${attrStr}) — would set SKU: ${sku}`);
          skuBackfillCount++;
        }

        const attrStr = (variation.attributes || []).map(a => a.option).join(' / ');
        selectionEntries.push({
          wooProductId: product.id,
          wooVariationId: variation.id,
          sku: sku,
          cjProductId,
          variantId: matched?.vid || matched?.variantId || '',
          productName: `${product.name} — ${attrStr}`,
        });
      }
    }

    // Small delay to avoid rate limits
    await new Promise(r => setTimeout(r, 200));
  }

  console.log(`\n\n✅ Mapping complete!`);
  console.log(`   Total selection entries: ${selectionEntries.length}`);
  console.log(`   SKUs to backfill: ${skuBackfillCount}`);

  if (!DRY_RUN) {
    fs.writeFileSync(SELECTION_PATH, JSON.stringify(selectionEntries, null, 2));
    console.log(`\n💾 Written to ${SELECTION_PATH}`);
  } else {
    console.log(`\n[DRY RUN] Would write ${selectionEntries.length} entries to ${SELECTION_PATH}`);
    console.log('\nSample entries:');
    console.log(JSON.stringify(selectionEntries.slice(0, 3), null, 2));
  }

  return selectionEntries;
}

main().catch(e => { console.error(e?.stack || String(e)); process.exit(1); });
