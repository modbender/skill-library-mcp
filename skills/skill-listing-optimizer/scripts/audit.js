#!/usr/bin/env node
/**
 * Amazon Listing Image Auditor
 * Detects non-square or undersized images across your listings.
 *
 * Usage:
 *   node audit.js --sku "MY-SKU"
 *   node audit.js --all
 *   node audit.js --all --out report.json
 */

const fs = require('fs');
const path = require('path');
const SellingPartnerAPI = require('amazon-sp-api');

const CREDS_PATH = process.env.AMAZON_SPAPI_PATH || './amazon-sp-api.json';
function getCfg() { return JSON.parse(fs.readFileSync(CREDS_PATH, 'utf8')); }
function getClient() {
  const creds = getCfg();
  return new SellingPartnerAPI({
    region: creds.region || 'eu',
    refresh_token: creds.refreshToken,
    credentials: {
      SELLING_PARTNER_APP_CLIENT_ID: creds.lwaClientId,
      SELLING_PARTNER_APP_CLIENT_SECRET: creds.lwaClientSecret,
    }
  });
}

const IMAGE_ATTRS = [
  'main_product_image_locator',
  ...Array.from({ length: 8 }, (_, i) => `other_product_image_locator_${i + 1}`)
];

const SLOT_NAMES = ['MAIN', 'PT01', 'PT02', 'PT03', 'PT04', 'PT05', 'PT06', 'PT07', 'PT08'];

async function getImageDimensions(url) {
  try {
    const res = await fetch(url, { method: 'HEAD' });
    // Parse dimensions from Amazon CDN URL pattern
    const match = url.match(/\/(\d+)x(\d+)\//);
    if (match) return { w: parseInt(match[1]), h: parseInt(match[2]) };
    // Fallback: download and check
    const buf = await fetch(url).then(r => r.arrayBuffer());
    const bytes = new Uint8Array(buf);
    // JPEG SOF0 marker
    for (let i = 0; i < bytes.length - 8; i++) {
      if (bytes[i] === 0xFF && (bytes[i+1] === 0xC0 || bytes[i+1] === 0xC2)) {
        return { w: (bytes[i+7] << 8) | bytes[i+8], h: (bytes[i+5] << 8) | bytes[i+6] };
      }
    }
  } catch (e) { return null; }
  return null;
}

async function auditSku(sp, sku) {
  const cfg = getCfg();
  const item = await sp.callAPI({
    operation: 'getListingsItem',
    endpoint: 'listingsItems',
    path: { sellerId: cfg.sellerId, sku },
    query: { marketplaceIds: cfg.marketplace, includedData: 'attributes' },
  });

  const issues = [];
  const attrs = item.attributes || {};

  for (let i = 0; i < IMAGE_ATTRS.length; i++) {
    const attr = IMAGE_ATTRS[i];
    const slot = SLOT_NAMES[i];
    const images = attrs[attr];
    if (!images || !images.length) continue;

    const url = images[0]?.media_location;
    if (!url) continue;

    const dims = await getImageDimensions(url);
    if (!dims) continue;

    const isSquare = dims.w === dims.h;
    const isTooSmall = dims.w < 1000 || dims.h < 1000;

    if (!isSquare || isTooSmall) {
      issues.push({ slot, attr, url, dims, isSquare, isTooSmall });
    }
  }

  return { sku, issues };
}

async function getAllSkus(sp) {
  const cfg = getCfg();
  const res = await sp.callAPI({
    operation: 'getInventorySummaries',
    endpoint: 'fbaInventory',
    query: {
      details: true,
      marketplaceIds: cfg.marketplace,
      granularityType: 'Marketplace',
      granularityId: cfg.marketplace,
    },
  });
  return (res.inventorySummaries || []).map(s => s.sellerSku);
}

function parseArgs() {
  const a = process.argv.slice(2);
  const out = { sku: null, all: false, out: null };
  for (let i = 0; i < a.length; i++) {
    if (a[i] === '--sku') out.sku = a[++i];
    else if (a[i] === '--all') out.all = true;
    else if (a[i] === '--out') out.out = a[++i];
  }
  return out;
}

async function main() {
  const args = parseArgs();
  if (!args.sku && !args.all) {
    console.log('Usage: node audit.js --sku "MY-SKU"');
    console.log('       node audit.js --all [--out report.json]');
    process.exit(0);
  }

  const sp = getClient();
  let skus = args.sku ? [args.sku] : await getAllSkus(sp);
  console.log(`\n🔍 Auditing ${skus.length} SKU(s)...\n`);

  const report = [];
  for (const sku of skus) {
    process.stdout.write(`  ${sku}... `);
    try {
      const result = await auditSku(sp, sku);
      if (result.issues.length === 0) {
        console.log('✅ all images OK');
      } else {
        console.log(`⚠️  ${result.issues.length} issue(s)`);
        result.issues.forEach(issue => {
          console.log(`    [${issue.slot}] ${issue.dims.w}x${issue.dims.h}${!issue.isSquare ? ' (non-square)' : ''}${issue.isTooSmall ? ' (too small)' : ''}`);
        });
      }
      report.push(result);
    } catch (e) {
      console.log(`❌ ${e.message.slice(0, 60)}`);
    }
  }

  const issues = report.filter(r => r.issues.length > 0);
  console.log(`\n📊 Summary: ${issues.length}/${report.length} SKUs have image issues\n`);

  if (args.out) {
    fs.writeFileSync(args.out, JSON.stringify({ auditedAt: new Date().toISOString(), report }, null, 2));
    console.log(`Saved to ${args.out}`);
  }
  return report;
}

main().catch(e => { console.error(e.message); process.exit(1); });
module.exports = { auditSku, getAllSkus };
