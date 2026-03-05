import { getDb } from './lib/db.js';

const [,, entityId] = process.argv;
if (!entityId) { console.error('Usage: status.mjs <entity_id>'); process.exit(1); }

const db = getDb();
const entity = db.prepare('SELECT * FROM entities WHERE id = ?').get(Number(entityId));
if (!entity) { console.error(`Entity ${entityId} not found`); process.exit(1); }

const accounts = db.prepare(`
  SELECT a.id, a.name, a.status, a.account_type FROM accounts a
  JOIN connections c ON c.id = a.connection_id WHERE c.entity_id = ?
`).all(Number(entityId));

const accountIds = accounts.map(a => a.id);
let txCount = 0, catCount = 0;
if (accountIds.length > 0) {
  const ph = accountIds.map(() => '?').join(',');
  txCount = db.prepare(`SELECT COUNT(*) as c FROM transactions WHERE account_id IN (${ph})`).get(...accountIds).c;
  catCount = db.prepare(`SELECT COUNT(*) as c FROM categorized_transactions ct JOIN transactions t ON t.id = ct.transaction_id WHERE t.account_id IN (${ph})`).get(...accountIds).c;
}

console.log(`Entity: ${entity.name} (ID: ${entity.id})`);
console.log(`Type: ${entity.type || 'N/A'}`);
console.log(`Last synced: ${entity.last_synced_at || 'Never'}`);
console.log(`\nAccounts (${accounts.length}):`);
for (const a of accounts) console.log(`  - ${a.name || 'Unnamed'} (${a.account_type || 'unknown'}, ${a.status || 'unknown'})`);
console.log(`\nTransactions: ${txCount}`);
console.log(`Categorized: ${catCount}`);
console.log(`Uncategorized: ${txCount - catCount}`);
