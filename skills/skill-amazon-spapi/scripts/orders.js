#!/usr/bin/env node
/**
 * Amazon SP-API — Orders
 * Usage:
 *   node orders.js --list [--days 7] [--status Unshipped] [--out orders.json]
 *   node orders.js --get <orderId>
 */

const fs = require('fs');
const auth = require('./auth');

function parseArgs() {
  const a = process.argv.slice(2);
  const out = { command: null, orderId: null, days: 7, status: null, out: null };
  for (let i = 0; i < a.length; i++) {
    if (a[i] === '--list') out.command = 'list';
    else if (a[i] === '--get') { out.command = 'get'; out.orderId = a[++i]; }
    else if (a[i] === '--days') out.days = Number(a[++i]);
    else if (a[i] === '--status') out.status = a[++i];
    else if (a[i] === '--out') out.out = a[++i];
  }
  return out;
}

async function listOrders(days = 7, status = null) {
  const sp = auth.getClient();
  const cfg = auth.getCfg();
  const createdAfter = new Date(Date.now() - days * 24 * 3600 * 1000).toISOString();
  const query = { MarketplaceIds: [cfg.marketplace], CreatedAfter: createdAfter };
  if (status) query.OrderStatuses = [status];
  const res = await sp.callAPI({ operation: 'getOrders', endpoint: 'orders', query });
  return res.Orders || [];
}

async function getOrder(orderId) {
  const sp = auth.getClient();
  return sp.callAPI({ operation: 'getOrder', endpoint: 'orders', path: { orderId } });
}

async function getOrderItems(orderId) {
  const sp = auth.getClient();
  const res = await sp.callAPI({ operation: 'getOrderItems', endpoint: 'orders', path: { orderId } });
  return res.OrderItems || [];
}

async function main() {
  const args = parseArgs();
  if (!args.command) {
    console.log('Usage: node orders.js --list [--days 7] [--status Unshipped] [--out file.json]');
    console.log('       node orders.js --get <orderId>');
    process.exit(0);
  }

  if (args.command === 'list') {
    const orders = await listOrders(args.days, args.status);
    const summary = orders.map(o => ({
      orderId: o.AmazonOrderId,
      status: o.OrderStatus,
      total: `${o.OrderTotal?.Amount} ${o.OrderTotal?.CurrencyCode}`,
      date: o.PurchaseDate,
    }));
    console.log(`\nFound ${summary.length} orders (last ${args.days} days):\n`);
    summary.forEach(o => console.log(`  ${o.orderId} | ${o.status} | ${o.total} | ${o.date?.slice(0, 10)}`));
    if (args.out) fs.writeFileSync(args.out, JSON.stringify({ fetchedAt: new Date().toISOString(), count: summary.length, orders: summary }, null, 2));
    return summary;
  }

  if (args.command === 'get') {
    const order = await getOrder(args.orderId);
    const items = await getOrderItems(args.orderId);
    const result = { order, items };
    console.log(JSON.stringify(result, null, 2));
    if (args.out) fs.writeFileSync(args.out, JSON.stringify(result, null, 2));
    return result;
  }
}

main().catch(e => { console.error(e?.response?.data || e.message || e); process.exit(1); });
module.exports = { listOrders, getOrder, getOrderItems };
