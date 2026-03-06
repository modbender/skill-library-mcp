#!/usr/bin/env node

import { Command } from 'commander';
import { getDb } from './db.js';
import { addProduct, getProduct, listProducts, removeProduct, updateCurrentPrice, getPriceHistory } from './products.js';
import { addOrder, getOrder, listOrders, updateOrder } from './orders.js';
import { calculateMargin } from './margin.js';
import { listAlerts, acknowledgeAlert } from './alerts.js';
import { generateInterchange } from './interchange.js';

const db = getDb();
const program = new Command();
program.name('ecom').description('E-commerce Price Monitoring').version('1.0.0');

// --- Watch commands ---
const watch = program.command('watch').description('Product watchlist');

watch.command('add')
  .description('Add product to watchlist')
  .argument('<name>', 'Product name')
  .requiredOption('--url <url>', 'Product URL')
  .option('--target <price>', 'Target price')
  .action((name, opts) => {
    const id = addProduct(db, { name, url: opts.url, target_price: opts.target ? parseFloat(opts.target) : null });
    console.log(`Added product ${id}`);
  });

watch.command('list')
  .description('List watchlist')
  .action(() => {
    const products = listProducts(db);
    console.table(products);
  });

watch.command('remove')
  .description('Remove product')
  .argument('<id>', 'Product ID')
  .action((id) => {
    console.log(removeProduct(db, parseInt(id)) ? 'Removed' : 'Not found');
  });

// --- Price commands ---
const price = program.command('price').description('Price tracking');

price.command('history')
  .description('Price history for a product')
  .argument('<id>', 'Product ID')
  .action((id) => {
    const history = getPriceHistory(db, parseInt(id));
    console.table(history);
  });

price.command('update')
  .description('Manually update current price')
  .argument('<id>', 'Product ID')
  .argument('<price>', 'New price')
  .action((id, p) => {
    updateCurrentPrice(db, parseInt(id), parseFloat(p));
    console.log('Price updated');
  });

// --- Order commands ---
const order = program.command('order').description('Order tracking');

order.command('add')
  .description('Add order')
  .argument('<name>', 'Product name')
  .option('--tracking <num>', 'Tracking number')
  .action((name, opts) => {
    const id = addOrder(db, { product_name: name, tracking_number: opts.tracking });
    console.log(`Added order ${id}`);
  });

order.command('list')
  .description('List orders')
  .option('--status <status>', 'Filter by status')
  .action((opts) => {
    const orders = listOrders(db, opts.status ? { status: opts.status } : {});
    console.table(orders);
  });

order.command('update')
  .description('Update order')
  .argument('<id>', 'Order ID')
  .option('--status <status>', 'New status')
  .option('--tracking <num>', 'Tracking number')
  .action((id, opts) => {
    const updates = {};
    if (opts.status) updates.status = opts.status;
    if (opts.tracking) updates.tracking_number = opts.tracking;
    console.log(updateOrder(db, parseInt(id), updates) ? 'Updated' : 'Not found');
  });

// --- Margin ---
program.command('margin')
  .description('Calculate margin')
  .requiredOption('--cost <cost>', 'Cost price')
  .requiredOption('--sell <sell>', 'Sell price')
  .option('--fees <pct>', 'Fees percentage', '0')
  .action((opts) => {
    const r = calculateMargin(parseFloat(opts.cost), parseFloat(opts.sell), parseFloat(opts.fees));
    console.log(`Profit: $${r.profit.toFixed(2)} | Margin: ${r.margin.toFixed(1)}% | Fees: $${r.fees.toFixed(2)}`);
  });

// --- Alert commands ---
const alert = program.command('alert').description('Price alerts');

alert.command('list')
  .description('List alerts')
  .option('--pending', 'Pending only')
  .action((opts) => {
    const alerts = listAlerts(db, { pending: opts.pending });
    console.table(alerts);
  });

alert.command('ack')
  .description('Acknowledge alert')
  .argument('<id>', 'Alert ID')
  .action((id) => {
    console.log(acknowledgeAlert(db, parseInt(id)) ? 'Acknowledged' : 'Not found');
  });

// --- Utilities ---
program.command('refresh')
  .description('Refresh interchange files')
  .action(() => {
    generateInterchange(db);
    console.log('Interchange refreshed');
  });

program.parse();
