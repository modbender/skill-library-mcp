#!/usr/bin/env node
import { initSchema } from './lib/db.js';
import { getBalanceTransactions } from './lib/stripe-client.js';

const [,, entityIdArg, startDate, endDate] = process.argv;

if (!entityIdArg || !startDate || !endDate) {
  console.error('Usage: pull_stripe_revenue.mjs <entity_id> <start_date> <end_date>');
  console.error('  Dates in YYYY-MM-DD format');
  process.exit(1);
}

const entityId = Number(entityIdArg);
const db = initSchema();

// Get Stripe connection
const conn = db.prepare('SELECT access_token FROM connections WHERE entity_id = ? AND provider = ?').get(entityId, 'stripe');
if (!conn) {
  console.error(`✗ No Stripe connection found for entity ${entityId}. Run connect_stripe.mjs first.`);
  process.exit(1);
}

const token = conn.access_token;

// Generate month boundaries
const months = [];
const cursor = new Date(startDate + "T00:00:00Z");
cursor.setUTCDate(1);
const endD = new Date(endDate + "T00:00:00Z");

while (cursor <= endD) {
  const y = cursor.getUTCFullYear();
  const m = cursor.getUTCMonth() + 1;
  const monthStr = `${y}-${String(m).padStart(2, '0')}`;
  
  const monthStart = `${y}-${String(m).padStart(2, '0')}-01`;
  const nextM = m === 12 ? 1 : m + 1;
  const nextY = m === 12 ? y + 1 : y;
  const monthEnd = `${nextY}-${String(nextM).padStart(2, '0')}-01`;
  
  months.push({ monthStr, monthStart, monthEnd });
  cursor.setUTCMonth(cursor.getUTCMonth() + 1);
}

console.log(`Pulling Stripe revenue for entity ${entityId}: ${startDate} to ${endDate}`);
console.log(`  ${months.length} months to process\n`);

const upsert = db.prepare(`
  INSERT INTO stripe_monthly_revenue (entity_id, month, gross_revenue, refunds, net_revenue, stripe_fees, transaction_count)
  VALUES (?, ?, ?, ?, ?, ?, ?)
  ON CONFLICT(entity_id, month) DO UPDATE SET
    gross_revenue = excluded.gross_revenue,
    refunds = excluded.refunds,
    net_revenue = excluded.net_revenue,
    stripe_fees = excluded.stripe_fees,
    transaction_count = excluded.transaction_count,
    created_at = datetime('now')
`);

try {
  for (const { monthStr, monthStart, monthEnd } of months) {
    const result = await getBalanceTransactions(token, monthStart, monthEnd);
    
    upsert.run(
      entityId,
      monthStr,
      result.grossRevenue,
      result.totalRefunds,
      result.netRevenue,
      result.fees,
      result.charges.length + result.refunds.length
    );

    console.log(`  ${monthStr}: gross=$${result.grossRevenue.toFixed(2)} refunds=$${result.totalRefunds.toFixed(2)} fees=$${result.fees.toFixed(2)} net=$${result.netRevenue.toFixed(2)} (${result.charges.length} charges, ${result.refunds.length} refunds)`);
  }

  console.log(`\n✓ Stored ${months.length} months of Stripe revenue data`);
} catch (err) {
  console.error('✗ Failed:', err.message);
  process.exit(1);
}
