import { getDb } from './lib/db.js';

const db = getDb();
const entities = db.prepare(`
  SELECT e.id, e.name, e.type,
    (SELECT COUNT(*) FROM connections WHERE entity_id = e.id) as connections,
    (SELECT COUNT(*) FROM transactions t JOIN accounts a ON a.id = t.account_id JOIN connections c ON c.id = a.connection_id WHERE c.entity_id = e.id) as transactions
  FROM entities e ORDER BY e.id
`).all();

if (entities.length === 0) { console.log('No entities found. Use connect_mercury.sh to add one.'); process.exit(0); }

console.log('Entities:\n');
for (const e of entities) {
  console.log(`  [${e.id}] ${e.name}${e.type ? ` (${e.type})` : ''} — ${e.connections} connection(s), ${e.transactions} transaction(s)`);
}
