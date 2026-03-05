#!/usr/bin/env node
// query.mjs — Search & traverse the KG
// Usage:
//   node query.mjs find <text>           Search all layers
//   node query.mjs children <id>         Direct children
//   node query.mjs rels <id>             All relations of entity
//   node query.mjs traverse <id> [--depth N]
//   node query.mjs type <type>           Filter by type
//   node query.mjs cat <category>        Filter by category
//   node query.mjs orphans               Unconnected entities
//   node query.mjs stats                 Graph statistics
//   node query.mjs recent [--days N]     Entities created/updated in last N days (default 7)
//   node query.mjs timeline [--from DATE] [--to DATE]  Entities sorted by date
//   node query.mjs changed               Entities updated after creation
//   node query.mjs uncertain             Entities with confidence < 0.5

import { search, findByType, findByCategory, traverse, reverseRels, stats, orphans } from '../lib/query.mjs';
import { load, getChildren, getEdges } from '../lib/graph.mjs';

const args = process.argv.slice(2);
const cmd = args[0];

function flag(name) {
  const i = args.indexOf('--' + name);
  return i !== -1 ? args[i + 1] : null;
}

function printNodes(nodes) {
  if (!nodes.length) return console.log('(no results)');
  for (const n of nodes) {
    const score = n._score ? ` [score:${n._score}]` : '';
    const depth = n._depth !== undefined ? ` [depth:${n._depth}]` : '';
    const parent = n.parent ? ` ←${n.parent}` : '';
    console.log(`  ${n.id} (${n.alias}) :${n.type} "${n.label}"${parent}${score}${depth}`);
    if (n.tags?.length) console.log(`    tags: ${n.tags.join(', ')}`);
    if (Object.keys(n.attrs || {}).length) console.log(`    attrs: ${JSON.stringify(n.attrs)}`);
  }
}

try {
  if (cmd === 'find') {
    const q = args.slice(1).join(' ');
    if (!q) { console.error('Usage: query.mjs find <text>'); process.exit(1); }
    const results = search(q, { limit: parseInt(flag('limit') || '10') });
    console.log(`Found ${results.length} results for "${q}":`);
    printNodes(results);

  } else if (cmd === 'children') {
    const store = load();
    const children = getChildren(store, args[1]);
    console.log(`Children of ${args[1]}:`);
    printNodes(children);

  } else if (cmd === 'rels') {
    const store = load();
    const edges = getEdges(store, args[1]);
    const rev = reverseRels(args[1]);
    console.log(`Relations of ${args[1]}:`);
    for (const e of edges) {
      const dir = e.from === args[1] ? '→' : '←';
      const other = e.from === args[1] ? e.to : e.from;
      console.log(`  ${dir} ${e.rel} ${other}`);
    }

  } else if (cmd === 'traverse') {
    const depth = parseInt(flag('depth') || '3');
    const results = traverse(args[1], { depth });
    console.log(`Traverse from ${args[1]} (depth ${depth}):`);
    printNodes(results);

  } else if (cmd === 'type') {
    const results = findByType(args[1]);
    console.log(`Entities of type "${args[1]}":`);
    printNodes(results);

  } else if (cmd === 'cat') {
    const results = findByCategory(args[1]);
    console.log(`Category "${args[1]}":`);
    printNodes(results);

  } else if (cmd === 'orphans') {
    const results = orphans();
    console.log(`Orphan entities (no relations, no children):`);
    printNodes(results);

  } else if (cmd === 'stats') {
    const s = stats();
    console.log('Knowledge Graph Statistics:');
    console.log(`  Entities: ${s.entities} (${s.topLevel} top-level)`);
    console.log(`  Edges: ${s.edges}`);
    console.log(`  Max depth: ${s.maxDepth}`);
    console.log(`  Categories: ${s.categories}`);
    console.log(`  Types: ${JSON.stringify(s.types)}`);
    console.log(`  Relations: ${JSON.stringify(s.relations)}`);
    console.log(`  Last consolidated: ${s.lastConsolidated || 'never'}`);

  } else if (cmd === 'recent') {
    const days = parseInt(flag('days') || '7');
    const store = load();
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - days);
    const cutoffStr = cutoff.toISOString().slice(0, 10);
    const nodes = Object.values(store.nodes).filter(n =>
      (n.created >= cutoffStr) || (n.updated >= cutoffStr)
    );
    nodes.sort((a, b) => {
      const da = a.updated > a.created ? a.updated : a.created;
      const db = b.updated > b.created ? b.updated : b.created;
      return db.localeCompare(da);
    });
    console.log(`Entities created/updated in last ${days} days (since ${cutoffStr}):`);
    printNodes(nodes);

  } else if (cmd === 'timeline') {
    const store = load();
    const fromDate = flag('from') || null;
    const toDate = flag('to') || null;
    let nodes = Object.values(store.nodes);
    if (fromDate) nodes = nodes.filter(n => n.created >= fromDate || n.updated >= fromDate);
    if (toDate) nodes = nodes.filter(n => n.created <= toDate);
    // Sort by most recent activity (updated, then created)
    nodes.sort((a, b) => {
      const da = a.updated > a.created ? a.updated : a.created;
      const db = b.updated > b.created ? b.updated : b.created;
      return da.localeCompare(db); // ascending
    });
    const range = [fromDate, toDate].filter(Boolean).join(' → ') || 'all time';
    console.log(`Timeline (${range}), ${nodes.length} entities:`);
    for (const n of nodes) {
      const activity = n.updated > n.created ? `upd:${n.updated}` : `cre:${n.created}`;
      console.log(`  [${activity}] ${n.id} (${n.alias}) :${n.type} "${n.label}"`);
    }

  } else if (cmd === 'changed') {
    const store = load();
    const nodes = Object.values(store.nodes).filter(n => n.updated && n.updated !== n.created);
    nodes.sort((a, b) => b.updated.localeCompare(a.updated));
    console.log(`Entities modified after creation (${nodes.length}):`);
    for (const n of nodes) {
      console.log(`  ${n.id} (${n.alias}) :${n.type} — created:${n.created} updated:${n.updated}`);
    }
    if (!nodes.length) console.log('  (none)');

  } else if (cmd === 'uncertain') {
    const store = load();
    const nodes = Object.values(store.nodes).filter(n =>
      n.confidence !== undefined && n.confidence < 0.5
    );
    nodes.sort((a, b) => a.confidence - b.confidence);
    console.log(`Low-confidence entities (< 0.5), ${nodes.length} found:`);
    for (const n of nodes) {
      console.log(`  ${n.id} (${n.alias}) :${n.type} "${n.label}" — confidence:${n.confidence}`);
    }
    if (!nodes.length) console.log('  (none — all entities are high confidence or unset)');

  } else {
    console.log('Usage: query.mjs <find|children|rels|traverse|type|cat|orphans|stats|recent|timeline|changed|uncertain>');
  }
} catch (e) {
  console.error('❌', e.message);
  process.exit(1);
}
