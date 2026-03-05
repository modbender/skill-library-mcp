#!/usr/bin/env node
/**
 * Amazon SP-API — Listings & Pricing
 * Usage:
 *   node listings.js --get <sku>
 *   node listings.js --update <sku> --price <amount> [--currency USD]
 */

const fs = require('fs');
const auth = require('./auth');

function parseArgs() {
  const a = process.argv.slice(2);
  const out = { command: null, sku: null, price: null, currency: 'USD', out: null };
  for (let i = 0; i < a.length; i++) {
    if (a[i] === '--get') { out.command = 'get'; out.sku = a[++i]; }
    else if (a[i] === '--update') { out.command = 'update'; out.sku = a[++i]; }
    else if (a[i] === '--price') out.price = a[++i];
    else if (a[i] === '--currency') out.currency = a[++i];
    else if (a[i] === '--out') out.out = a[++i];
  }
  return out;
}

async function getListing(sku) {
  const sp = auth.getClient();
  const cfg = auth.getCfg();
  return sp.callAPI({
    operation: 'getListingsItem',
    endpoint: 'listingsItems',
    path: { sellerId: cfg.sellerId, sku: encodeURIComponent(sku) },
    query: { marketplaceIds: cfg.marketplace, includedData: 'summaries,attributes,issues,offers,fulfillmentAvailability' },
  });
}

async function updatePrice(sku, price, currency) {
  const sp = auth.getClient();
  const cfg = auth.getCfg();
  return sp.callAPI({
    operation: 'patchListingsItem',
    endpoint: 'listingsItems',
    path: { sellerId: cfg.sellerId, sku: encodeURIComponent(sku) },
    query: { marketplaceIds: cfg.marketplace },
    body: {
      productType: 'PRODUCT',
      patches: [{
        op: 'replace',
        path: '/attributes/purchasable_offer',
        value: [{
          marketplace_id: cfg.marketplace,
          currency,
          our_price: [{ schedule: [{ value_with_tax: parseFloat(price) }] }],
        }],
      }],
    },
  });
}

async function main() {
  const args = parseArgs();
  if (!args.command) {
    console.log('Usage:');
    console.log('  node listings.js --get <sku>');
    console.log('  node listings.js --update <sku> --price <amount> [--currency USD]');
    process.exit(0);
  }
  if (args.command === 'get') {
    const listing = await getListing(args.sku);
    console.log(JSON.stringify(listing, null, 2));
    if (args.out) fs.writeFileSync(args.out, JSON.stringify(listing, null, 2));
  }
  if (args.command === 'update') {
    if (!args.price) { console.error('--price required'); process.exit(1); }
    const result = await updatePrice(args.sku, args.price, args.currency);
    console.log(JSON.stringify(result, null, 2));
  }
}

main().catch(e => { console.error(e?.response?.data || e.message); process.exit(1); });
module.exports = { getListing, updatePrice };
