#!/usr/bin/env node
// vault.mjs — Secret management CLI
// Usage:
//   node vault.mjs set <key> <value> [--note "desc"]
//   node vault.mjs get <key>
//   node vault.mjs list
//   node vault.mjs del <key>

import { vaultSet, vaultGet, vaultList, vaultDel } from '../lib/vault.mjs';

const args = process.argv.slice(2);
const cmd = args[0];

function flag(name) {
  const i = args.indexOf('--' + name);
  return i !== -1 ? args[i + 1] : null;
}

try {
  if (cmd === 'set') {
    const key = args[1], value = args[2];
    if (!key || !value) { console.error('Usage: vault.mjs set <key> <value>'); process.exit(1); }
    vaultSet(key, value, flag('note') || '');
    console.log(`🔐 Stored: ${key}`);

  } else if (cmd === 'get') {
    const key = args[1];
    if (!key) { console.error('Usage: vault.mjs get <key>'); process.exit(1); }
    const val = vaultGet(key);
    if (val === null) { console.error(`Key "${key}" not found`); process.exit(1); }
    // Output raw value (for piping into env vars etc.)
    process.stdout.write(val);

  } else if (cmd === 'list') {
    const keys = vaultList();
    if (!keys.length) { console.log('(vault empty)'); process.exit(0); }
    console.log('Vault keys:');
    for (const k of keys) console.log(`  🔑 ${k.key} — ${k.note || '(no note)'} [rotated: ${k.rotated}]`);

  } else if (cmd === 'del') {
    const key = args[1];
    if (!key) { console.error('Usage: vault.mjs del <key>'); process.exit(1); }
    const result = vaultDel(key);
    if (result.ok) console.log(`🗑️ Deleted: ${key}`);
    else console.error(`Key "${key}" not found`);

  } else {
    console.log('Usage: vault.mjs <set|get|list|del> [args]');
  }
} catch (e) {
  console.error('❌', e.message);
  process.exit(1);
}
