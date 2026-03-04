#!/usr/bin/env node
/**
 * config.mjs — KG configuration CLI
 *
 * Usage:
 *   node scripts/config.mjs                     # list all settings
 *   node scripts/config.mjs get <key>            # get a value
 *   node scripts/config.mjs set <key> <value>    # set a value
 *   node scripts/config.mjs reset <key>          # reset to default
 *   node scripts/config.mjs reset --all          # reset everything
 *   node scripts/config.mjs --json               # list all as JSON
 */

import { loadConfig, saveConfig, getConfigValue, setConfigValue, resetConfigValue, listConfig, getDefaults, CONFIG_PATH } from '../lib/config.mjs';
import { existsSync, unlinkSync } from 'fs';

const args = process.argv.slice(2);
const jsonMode = args.includes('--json');
const filteredArgs = args.filter(a => !a.startsWith('--'));

function parseValue(str) {
  if (str === 'true') return true;
  if (str === 'false') return false;
  if (str === 'null') return null;
  if (/^-?\d+$/.test(str)) return parseInt(str, 10);
  if (/^-?\d+\.\d+$/.test(str)) return parseFloat(str);
  return str;
}

function main() {
  const cmd = filteredArgs[0];

  if (cmd === 'get') {
    const key = filteredArgs[1];
    if (!key) { console.error('Usage: config.mjs get <key>'); process.exit(1); }
    const val = getConfigValue(key);
    if (val === undefined) {
      console.error(`❌ Unknown config key: ${key}`);
      process.exit(1);
    }
    if (typeof val === 'object') {
      console.log(JSON.stringify(val, null, 2));
    } else {
      console.log(val);
    }
    return;
  }

  if (cmd === 'set') {
    const key = filteredArgs[1];
    const rawVal = filteredArgs[2];
    if (!key || rawVal === undefined) {
      console.error('Usage: config.mjs set <key> <value>');
      process.exit(1);
    }
    const value = parseValue(rawVal);
    const saved = setConfigValue(key, value);
    console.log(`✅ Set ${key} = ${JSON.stringify(value)}`);
    if (Object.keys(saved).length === 0) {
      console.log('   (value matches default — no override stored)');
    }
    return;
  }

  if (cmd === 'reset') {
    const key = filteredArgs[1];
    if (args.includes('--all')) {
      if (existsSync(CONFIG_PATH)) {
        unlinkSync(CONFIG_PATH);
        console.log('✅ All config reset to defaults (kg-config.json removed)');
      } else {
        console.log('ℹ️  No custom config exists — already using defaults');
      }
      return;
    }
    if (!key) {
      console.error('Usage: config.mjs reset <key> | config.mjs reset --all');
      process.exit(1);
    }
    resetConfigValue(key);
    const defVal = getConfigValue(key);
    console.log(`✅ Reset ${key} → ${JSON.stringify(defVal)} (default)`);
    return;
  }

  // Default: list all config
  if (jsonMode) {
    console.log(JSON.stringify(loadConfig(), null, 2));
    return;
  }

  const entries = listConfig();
  const maxPath = Math.max(...entries.map(e => e.path.length));

  console.log('');
  console.log('  ⚙️  Knowledge Graph Configuration');
  console.log('  ─────────────────────────────────');

  let lastSection = '';
  for (const e of entries) {
    const section = e.path.split('.')[0];
    if (section !== lastSection) {
      console.log('');
      console.log(`  [${section}]`);
      lastSection = section;
    }
    const marker = e.overridden ? ' ✏️' : '';
    const valStr = e.value === null ? 'auto' : JSON.stringify(e.value);
    const defStr = e.default === null ? 'auto' : JSON.stringify(e.default);
    const shortPath = e.path.split('.').slice(1).join('.');
    const padding = ' '.repeat(Math.max(1, 30 - shortPath.length));
    if (e.overridden) {
      console.log(`    ${shortPath}${padding}${valStr}${marker}  (default: ${defStr})`);
    } else {
      console.log(`    ${shortPath}${padding}${valStr}`);
    }
  }
  console.log('');
  console.log('  ✏️ = user override  |  "auto" = null (auto-detected)');
  console.log(`  Config file: ${CONFIG_PATH}`);
  console.log('');
}

main();
