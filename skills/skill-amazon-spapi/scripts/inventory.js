#!/usr/bin/env node
/**
 * Amazon SP-API — FBA Inventory
 * Usage:
 *   node inventory.js [--sku "MY-SKU"] [--out inventory.json]
 */

const fs = require('fs');
const auth = require('./auth');

function parseArgs() {
  const a = process.argv.slice(2);
  const out = { sku: null, out: null };
  for (let i = 0; i < a.length; i++) {
    if (a[i] === '--sku') out.sku = a[++i];
    else if (a[i] === '--out') out.out = a[++i];
  }
  return out;
}

async function getInventory(sellerSku = null) {
  const sp = auth.getClient();
  const cfg = auth.getCfg();
  const marketplace = cfg.marketplace;
  const query = {
    details: true,
    marketplaceIds: marketplace,
    granularityType: 'Marketplace',
    granularityId: marketplace,
  };
  if (sellerSku) query.sellerSkus = sellerSku;
  const res = await sp.callAPI({ operation: 'getInventorySummaries', endpoint: 'fbaInventory', query });
  return res.inventorySummaries || [];
}

async function main() {
  const args = parseArgs();
  const inventory = await getInventory(args.sku);
  console.log(`\nInventory (${inventory.length} SKUs):\n`);
  inventory.forEach(item => {
    const qty = item.inventoryDetails?.fulfillableQuantity ?? item.totalQuantity ?? 'N/A';
    console.log(`  ${item.sellerSku} | ASIN: ${item.asin} | Fulfillable: ${qty} | Condition: ${item.condition}`);
  });
  if (args.out) {
    fs.writeFileSync(args.out, JSON.stringify({ fetchedAt: new Date().toISOString(), count: inventory.length, inventory }, null, 2));
    console.log(`\nSaved to ${args.out}`);
  }
  return inventory;
}

main().catch(e => { console.error(e?.response?.data || e.message); process.exit(1); });
module.exports = { getInventory };
