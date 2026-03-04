#!/usr/bin/env node
import { initSchema } from './lib/db.js';
import { mercuryRequest } from './lib/mercury-client.js';

const token = process.argv[2];
const entityName = process.argv[3];

if (!token) {
  console.error('Usage: connect_mercury.mjs <mercury_api_token> [entity_name]');
  process.exit(1);
}

const db = initSchema();

try {
  const accountsResponse = await mercuryRequest(token, '/accounts');
  const accounts = accountsResponse?.accounts ?? [];

  let orgName = entityName;
  if (!orgName) {
    try {
      const org = await mercuryRequest(token, '/organization');
      orgName = org?.organization?.legalBusinessName || org?.organization?.name || org?.legalBusinessName || org?.name || 'Mercury Entity';
    } catch { orgName = 'Mercury Entity'; }
  }

  // Create entity
  const entityResult = db.prepare('INSERT INTO entities (name, type) VALUES (?, ?) RETURNING id').get(orgName, 'LLC');
  const entityId = entityResult.id;

  // Create connection (store token as-is locally — no encryption needed for local SQLite)
  const connResult = db.prepare('INSERT INTO connections (entity_id, provider, access_token) VALUES (?, ?, ?) RETURNING id').get(entityId, 'mercury', token);
  const connectionId = connResult.id;

  // Store accounts
  const insertAccount = db.prepare('INSERT OR REPLACE INTO accounts (connection_id, external_id, name, status, account_type, currency, raw_data) VALUES (?, ?, ?, ?, ?, ?, ?)');
  for (const acct of accounts) {
    insertAccount.run(connectionId, acct.id, acct.name, acct.status, acct.type, acct.currency, JSON.stringify(acct));
  }

  console.log(`✓ Connected to Mercury`);
  console.log(`  Entity: ${orgName} (id: ${entityId})`);
  console.log(`  Connection: ${connectionId}`);
  console.log(`  Accounts: ${accounts.length}`);
  for (const acct of accounts) {
    console.log(`    - ${acct.name} (${acct.type}, ${acct.status})`);
  }
} catch (err) {
  console.error('✗ Failed to connect:', err.message);
  process.exit(1);
}
