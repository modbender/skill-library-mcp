#!/usr/bin/env node
// merge.mjs — Merge two entities
// Usage: node merge.mjs --target X --source Y [--mode absorb|nest]

import { load, save, mergeNodes } from '../lib/graph.mjs';
const args = process.argv.slice(2);

function flag(name) {
  const i = args.indexOf('--' + name);
  return i !== -1 ? args[i + 1] : null;
}

try {
  const target = flag('target'), source = flag('source');
  if (!target || !source) { console.error('--target and --source required'); process.exit(1); }
  const mode = flag('mode') || 'absorb';
  const store = load();
  const result = mergeNodes(store, target, source, mode);
  save(store);
  console.log(`✅ Merge complete (${result.mode}): ${source} → ${target}`);
} catch (e) {
  console.error('❌', e.message);
  process.exit(1);
}
