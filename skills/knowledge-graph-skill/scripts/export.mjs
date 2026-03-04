#!/usr/bin/env node
// export.mjs — Export KG data for other agents to read
// Usage:
//   node scripts/export.mjs                         # KGML to stdout
//   node scripts/export.mjs --format json           # Full JSON to stdout
//   node scripts/export.mjs --format kgml           # KGML to stdout
//   node scripts/export.mjs --target /path/out.kgml # Write to file
//   node scripts/export.mjs --target /tmp/kg.json --format json
//   node scripts/export.mjs --summary               # Also write kg-summary.md (shortcut for summarize.mjs)

import { writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { load } from '../lib/graph.mjs';
import { toKGMLAsync } from '../lib/serialize.mjs';

const __dirname = dirname(fileURLToPath(import.meta.url));

function flag(name) {
  const args = process.argv.slice(2);
  const i = args.indexOf('--' + name);
  return i !== -1 ? args[i + 1] : null;
}
function hasFlag(name) {
  return process.argv.includes('--' + name);
}

const format = flag('format') || 'kgml';
const target = flag('target') || null;
const doSummary = hasFlag('summary');

async function exportKGML() {
  const content = await toKGMLAsync({ maxTokens: 9999 }); // full, no token limit for export
  return content;
}

function exportJSON() {
  const store = load();
  // Strip internal vault data but keep everything else
  return JSON.stringify(store, null, 2) + '\n';
}

function buildMinimalJSON() {
  // Minimal read-only export: just nodes+edges, no meta internals
  const store = load();
  const nodes = Object.values(store.nodes).map(n => ({
    id: n.id,
    alias: n.alias,
    type: n.type,
    label: n.label,
    parent: n.parent,
    tags: n.tags,
    attrs: n.attrs,
    created: n.created,
    updated: n.updated,
    ...(n.confidence !== undefined ? { confidence: n.confidence } : {})
  }));
  return JSON.stringify({
    version: store.version,
    meta: store.meta,
    nodes,
    edges: store.edges,
    categories: store.categories
  }, null, 2) + '\n';
}

async function main() {
  let content;

  if (format === 'json') {
    content = buildMinimalJSON();
  } else if (format === 'kgml') {
    content = await exportKGML();
  } else {
    console.error(`❌ Unknown format: "${format}". Use kgml or json.`);
    process.exit(1);
  }

  if (target) {
    writeFileSync(target, content);
    const store = load();
    const nodeCount = Object.keys(store.nodes).length;
    const edgeCount = store.edges.length;
    console.error(`✅ Exported ${nodeCount} entities, ${edgeCount} edges → ${target} (${format})`);
  } else {
    process.stdout.write(content);
  }

  // Also regenerate the summary file if --summary flag set
  if (doSummary) {
    const summaryPath = join(__dirname, '..', 'data', 'kg-summary.md');
    const summaryContent = await toKGMLAsync({ maxTokens: 1500 });
    writeFileSync(summaryPath, summaryContent);
    console.error(`✅ Summary regenerated: ${summaryPath}`);
  }
}

main().catch(e => {
  console.error('❌', e.message);
  process.exit(1);
});
