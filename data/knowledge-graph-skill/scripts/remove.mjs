#!/usr/bin/env node
// remove.mjs — Remove entity or relation
// Usage:
//   node remove.mjs entity --id X [--no-cascade]
//   node remove.mjs rel --from X --to Y [--rel R]

import { load, save, removeNode, removeEdge } from '../lib/graph.mjs';
const args = process.argv.slice(2);
const cmd = args[0];

function flag(name) {
  const i = args.indexOf('--' + name);
  return i !== -1 ? args[i + 1] : null;
}

try {
  const store = load();

  if (cmd === 'entity') {
    const id = flag('id');
    if (!id) { console.error('--id required'); process.exit(1); }
    const cascade = !args.includes('--no-cascade');
    removeNode(store, id, cascade);
    save(store);
    console.log(`✅ Removed entity: ${id}${cascade ? ' (+ children)' : ''}`);

  } else if (cmd === 'rel') {
    const from = flag('from'), to = flag('to'), rel = flag('rel');
    if (!from || !to) { console.error('--from, --to required'); process.exit(1); }
    const count = removeEdge(store, { from, to, rel });
    save(store);
    console.log(`✅ Removed ${count} relation(s)`);

  } else {
    console.log('Usage: remove.mjs <entity|rel> [options]');
  }
} catch (e) {
  console.error('❌', e.message);
  process.exit(1);
}
