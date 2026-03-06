#!/usr/bin/env node
import { initSchema } from './lib/db.js';
import { mercuryRequest } from './lib/mercury-client.js';
import { normalizeCounterparty } from './lib/normalize.js';

const entityId = process.argv[2];
const startDate = process.argv[3];
const endDate = process.argv[4];

if (!entityId || !startDate || !endDate) {
  console.error('Usage: pull_transactions.mjs <entity_id> <start_date> <end_date>');
  console.error('Dates in YYYY-MM-DD format');
  process.exit(1);
}

const db = initSchema();

const connection = db.prepare('SELECT id, access_token FROM connections WHERE entity_id = ? AND status = ?').get(entityId, 'active');
if (!connection) { console.error('✗ No active connection for entity', entityId); process.exit(1); }

const accounts = db.prepare('SELECT id, external_id FROM accounts WHERE connection_id = ?').all(connection.id);
if (accounts.length === 0) { console.error('✗ No accounts found'); process.exit(1); }

const token = connection.access_token;
const limit = 500;
let total = 0;

const upsertTx = db.prepare(`
  INSERT INTO transactions (account_id, external_id, posted_at, external_created_at, amount, counterparty_name, counterparty_normalized, bank_description, kind, status, type, raw_data)
  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  ON CONFLICT(account_id, external_id) DO UPDATE SET
    posted_at=excluded.posted_at, amount=excluded.amount, counterparty_name=excluded.counterparty_name,
    counterparty_normalized=excluded.counterparty_normalized, bank_description=excluded.bank_description,
    status=excluded.status, updated_at=datetime('now')
`);

for (const acct of accounts) {
  let offset = 0;
  while (true) {
    const response = await mercuryRequest(token, `/account/${acct.external_id}/transactions`, {
      limit, offset, start: startDate, end: endDate,
    });
    const transactions = response?.transactions || [];
    const cleaned = transactions.filter(tx => !['cancelled', 'failed'].includes(tx.status));

    for (const tx of cleaned) {
      upsertTx.run(
        acct.id, tx.id,
        tx.postedAt ? tx.postedAt.slice(0, 10) : null,
        tx.createdAt, tx.amount, tx.counterpartyName,
        normalizeCounterparty(tx.counterpartyName),
        tx.bankDescription, tx.kind, tx.status,
        tx.amount < 0 ? 'debit' : 'credit',
        JSON.stringify(tx)
      );
    }
    total += cleaned.length;

    if (transactions.length < limit) break;
    offset += limit;
  }
}

db.prepare('UPDATE entities SET last_synced_at = datetime(?) WHERE id = ?').run(new Date().toISOString(), entityId);

console.log(`✓ Pulled ${total} transactions from ${accounts.length} accounts (${startDate} to ${endDate})`);
