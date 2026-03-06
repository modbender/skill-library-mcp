/**
 * @module interchange
 * Generate interchange .md files for the ecommerce skill.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { listProducts } from './products.js';
import { listOrders } from './orders.js';
import { listAlerts } from './alerts.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const interchangeDir = path.join(__dirname, '..', '..', 'interchange', 'ecommerce');

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

/**
 * Generate all interchange files.
 * @param {import('better-sqlite3').Database} db
 */
export function generateInterchange(db) {
  generateOps();
  generateState(db);
}

function generateOps() {
  const opsDir = path.join(interchangeDir, 'ops');
  ensureDir(opsDir);

  fs.writeFileSync(path.join(opsDir, 'capabilities.md'), `# E-commerce Capabilities

## Commands
- \`ecom watch add <name> --url <url> [--target <price>]\`
- \`ecom watch list\`
- \`ecom watch remove <id>\`
- \`ecom price history <id>\`
- \`ecom price update <id> <price>\`
- \`ecom order add <name> [--tracking <num>]\`
- \`ecom order list [--status <status>]\`
- \`ecom order update <id> [--status <s>] [--tracking <n>]\`
- \`ecom margin --cost <c> --sell <s> [--fees <pct>]\`
- \`ecom alert list [--pending]\`
- \`ecom alert ack <id>\`
- \`ecom refresh\`
`);
}

function generateState(db) {
  const stateDir = path.join(interchangeDir, 'state');
  ensureDir(stateDir);

  const products = listProducts(db);
  const productCount = products.length;
  const belowTarget = products.filter(p => p.current_price && p.target_price && p.current_price <= p.target_price).length;

  fs.writeFileSync(path.join(stateDir, 'summary.md'), `# E-commerce State

## Watchlist
- Products tracked: ${productCount}
- Below target price: ${belowTarget}

## Orders
- Active: ${listOrders(db, { status: 'ordered' }).length}
- Shipped: ${listOrders(db, { status: 'shipped' }).length}

## Alerts
- Pending: ${listAlerts(db, { pending: true }).length}
`);
}
