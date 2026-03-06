#!/usr/bin/env node
/**
 * Manage entity settings
 * 
 * Usage:
 *   node entity-settings.mjs list
 *   node entity-settings.mjs get <entity_id>
 *   node entity-settings.mjs set <entity_id> <key> <value>
 *   node entity-settings.mjs set-accrual <entity_id> --month-offset=1 --amortization=5833.50
 */

import { getDb } from './lib/db.js';
import { updateEntitySettings } from './lib/pnl.js';

const db = getDb();

// Ensure settings table exists
db.exec(`
  CREATE TABLE IF NOT EXISTS entity_settings (
    entity_id INTEGER PRIMARY KEY REFERENCES entities(id) ON DELETE CASCADE,
    stripe_fee_rate REAL DEFAULT 0.029,
    stripe_fee_fixed REAL DEFAULT 0.30,
    month_offset INTEGER DEFAULT 0,
    accounting_basis TEXT DEFAULT 'cash',
    amortization_monthly REAL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
  )
`);

function listEntities() {
  const entities = db.prepare(`
    SELECT e.id, e.name, e.type,
           es.stripe_fee_rate, es.month_offset, es.accounting_basis, es.amortization_monthly
    FROM entities e
    LEFT JOIN entity_settings es ON es.entity_id = e.id
  `).all();
  
  console.log('\nEntities and Settings:');
  console.log('='.repeat(100));
  console.log('ID | Name'.padEnd(30) + ' | Type'.padEnd(15) + ' | Stripe Fee | Offset | Basis   | Amort/mo');
  console.log('-'.repeat(100));
  
  for (const e of entities) {
    console.log(
      `${e.id}  | ${(e.name || '').slice(0, 25).padEnd(25)} | ${(e.type || '').padEnd(12)} | ` +
      `${((e.stripe_fee_rate || 0.029) * 100).toFixed(1)}%`.padStart(9) + ' | ' +
      `${e.month_offset || 0}`.padStart(6) + ' | ' +
      `${(e.accounting_basis || 'cash').padEnd(7)} | ` +
      `$${(e.amortization_monthly || 0).toFixed(2)}`
    );
  }
  console.log('');
}

function getEntity(entityId) {
  const entity = db.prepare(`
    SELECT e.*, es.*
    FROM entities e
    LEFT JOIN entity_settings es ON es.entity_id = e.id
    WHERE e.id = ?
  `).get(entityId);
  
  if (!entity) {
    console.error(`Entity ${entityId} not found`);
    return;
  }
  
  console.log('\nEntity Settings:');
  console.log('='.repeat(50));
  console.log(`ID:                ${entity.id}`);
  console.log(`Name:              ${entity.name}`);
  console.log(`Type:              ${entity.type || 'N/A'}`);
  console.log(`Stripe Fee Rate:   ${((entity.stripe_fee_rate || 0.029) * 100).toFixed(2)}%`);
  console.log(`Stripe Fee Fixed:  $${(entity.stripe_fee_fixed || 0.30).toFixed(2)}`);
  console.log(`Month Offset:      ${entity.month_offset || 0} month(s)`);
  console.log(`Accounting Basis:  ${entity.accounting_basis || 'cash'}`);
  console.log(`Amortization:      $${(entity.amortization_monthly || 0).toFixed(2)}/month`);
  console.log('');
}

function setEntitySetting(entityId, key, value) {
  const validKeys = ['stripe_fee_rate', 'stripe_fee_fixed', 'month_offset', 'accounting_basis', 'amortization_monthly'];
  
  if (!validKeys.includes(key)) {
    console.error(`Invalid key: ${key}`);
    console.error(`Valid keys: ${validKeys.join(', ')}`);
    return;
  }
  
  const settings = {};
  
  if (key === 'stripe_fee_rate') {
    settings.stripeFeeRate = parseFloat(value);
    if (settings.stripeFeeRate > 1) settings.stripeFeeRate /= 100; // Convert percentage
  } else if (key === 'stripe_fee_fixed') {
    settings.stripeFeeFixed = parseFloat(value);
  } else if (key === 'month_offset') {
    settings.monthOffset = parseInt(value);
  } else if (key === 'accounting_basis') {
    if (!['cash', 'accrual'].includes(value)) {
      console.error('Accounting basis must be "cash" or "accrual"');
      return;
    }
    settings.accountingBasis = value;
  } else if (key === 'amortization_monthly') {
    settings.amortizationMonthly = parseFloat(value);
  }
  
  updateEntitySettings(db, parseInt(entityId), settings);
  console.log(`Updated ${key} = ${value} for entity ${entityId}`);
  getEntity(entityId);
}

function setAccrualBasis(entityId, args) {
  const settings = {
    accountingBasis: 'accrual',
  };
  
  for (const arg of args) {
    if (arg.startsWith('--month-offset=')) {
      settings.monthOffset = parseInt(arg.split('=')[1]);
    } else if (arg.startsWith('--amortization=')) {
      settings.amortizationMonthly = parseFloat(arg.split('=')[1]);
    } else if (arg.startsWith('--stripe-rate=')) {
      settings.stripeFeeRate = parseFloat(arg.split('=')[1]);
      if (settings.stripeFeeRate > 1) settings.stripeFeeRate /= 100;
    }
  }
  
  updateEntitySettings(db, parseInt(entityId), settings);
  console.log(`Configured accrual basis for entity ${entityId}`);
  getEntity(entityId);
}

// Parse command line
const args = process.argv.slice(2);
const command = args[0];

switch (command) {
  case 'list':
    listEntities();
    break;
  case 'get':
    getEntity(args[1]);
    break;
  case 'set':
    setEntitySetting(args[1], args[2], args[3]);
    break;
  case 'set-accrual':
    setAccrualBasis(args[1], args.slice(2));
    break;
  default:
    console.log(`
Entity Settings Manager

Usage:
  node entity-settings.mjs list
  node entity-settings.mjs get <entity_id>
  node entity-settings.mjs set <entity_id> <key> <value>
  node entity-settings.mjs set-accrual <entity_id> [options]

Settings:
  stripe_fee_rate      Stripe percentage fee (default: 0.029 = 2.9%)
  stripe_fee_fixed     Stripe fixed fee per transaction (default: 0.30)
  month_offset         Months to offset for accrual basis (default: 0)
  accounting_basis     "cash" or "accrual" (default: cash)
  amortization_monthly Monthly amortization amount (default: 0)

Examples:
  node entity-settings.mjs set 1 accounting_basis accrual
  node entity-settings.mjs set 1 month_offset 1
  node entity-settings.mjs set 1 amortization_monthly 5833.50
  node entity-settings.mjs set-accrual 1 --month-offset=1 --amortization=5833.50
`);
}

db.close();
