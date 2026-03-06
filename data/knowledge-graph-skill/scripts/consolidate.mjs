#!/usr/bin/env node
// consolidate.mjs — Auto-optimize KG structure
// Finds auto-nest candidates, orphans, merge suggestions

import { load, save, getEdges, getChildren } from '../lib/graph.mjs';
import { loadConfig } from '../lib/config.mjs';

try {
  const store = load();
  const cfg = loadConfig();
  const cc = cfg.consolidation;
  const nodes = Object.values(store.nodes);
  const report = { nested: [], orphans: [], mergeSuggestions: [], pruned: 0 };

  // 1. Auto-nest: entities with only 1 relation to another entity → become child
  if (!cc.autoNest) {
    console.log('⏭️  Auto-nest disabled by config');
  }
  for (const n of nodes) {
    if (!cc.autoNest) break;
    if (n.parent) continue; // already nested
    const edges = getEdges(store, n.id);
    const children = getChildren(store, n.id);
    if (children.length > 0) continue; // has children, likely a parent
    if (edges.length !== 1) continue; // must have exactly 1 relation

    const e = edges[0];
    const otherId = e.from === n.id ? e.to : e.from;
    const rel = e.rel;
    // nest if relation implies containment
    const nestRels = ['runs', 'runs_on', 'contains', 'part_of', 'has', 'instance_of', 'belongs_to'];
    if (nestRels.includes(rel)) {
      const parentId = ['runs_on', 'part_of', 'belongs_to', 'instance_of'].includes(rel) ? otherId : 
                       e.from === n.id ? e.to : e.from;
      report.nested.push({ id: n.id, newParent: parentId, viaRel: rel });
      // Actually nest
      n.parent = parentId;
      n.updated = new Date().toISOString().slice(0, 10);
      // Remove the edge (now implied by hierarchy)
      store.edges = store.edges.filter(x => !(
        (x.from === e.from && x.to === e.to && x.rel === e.rel)
      ));
    }
  }

  // 2. Orphans: no relations, no children, no parent
  for (const n of Object.values(store.nodes)) {
    if (n.parent) continue;
    const edges = store.edges.filter(e => e.from === n.id || e.to === n.id);
    const children = Object.values(store.nodes).filter(c => c.parent === n.id);
    if (edges.length === 0 && children.length === 0) {
      report.orphans.push(n.id);
    }
  }

  // 3. Merge suggestions: same type + similar labels
  if (cc.mergeSuggestions) {
    const byType = {};
    for (const n of Object.values(store.nodes)) {
      if (!byType[n.type]) byType[n.type] = [];
      byType[n.type].push(n);
    }
    for (const [type, group] of Object.entries(byType)) {
      for (let i = 0; i < group.length; i++) {
        for (let j = i + 1; j < group.length; j++) {
          const a = group[i], b = group[j];
          const la = a.label.toLowerCase(), lb = b.label.toLowerCase();
          if (la.includes(lb) || lb.includes(la) || levenshtein(la, lb) <= cc.levenshteinThreshold) {
            report.mergeSuggestions.push({ a: a.id, b: b.id, reason: 'similar labels' });
          }
        }
      }
    }
  } else {
    console.log('⏭️  Merge suggestions disabled by config');
  }

  // 4. Prune empty attrs
  if (cc.pruneEmptyAttrs) {
    for (const n of Object.values(store.nodes)) {
      for (const [k, v] of Object.entries(n.attrs)) {
        if (v === '' || v === null || v === undefined) {
          delete n.attrs[k];
          report.pruned++;
        }
      }
    }
  }

  store.meta.lastConsolidated = new Date().toISOString().slice(0, 10);
  save(store);

  console.log('🔧 Consolidation Report:');
  console.log(`  Auto-nested: ${report.nested.length}`);
  for (const n of report.nested) console.log(`    ${n.id} → child of ${n.newParent} (was ${n.viaRel})`);
  console.log(`  Orphans found: ${report.orphans.length}`);
  for (const o of report.orphans) console.log(`    ${o}`);
  console.log(`  Merge suggestions: ${report.mergeSuggestions.length}`);
  for (const m of report.mergeSuggestions) console.log(`    ${m.a} ↔ ${m.b} (${m.reason})`);
  console.log(`  Attrs pruned: ${report.pruned}`);

} catch (e) {
  console.error('❌', e.message);
  process.exit(1);
}

// Simple Levenshtein
function levenshtein(a, b) {
  const m = a.length, n = b.length;
  const d = Array.from({ length: m + 1 }, (_, i) => [i]);
  for (let j = 1; j <= n; j++) d[0][j] = j;
  for (let i = 1; i <= m; i++)
    for (let j = 1; j <= n; j++)
      d[i][j] = Math.min(d[i-1][j]+1, d[i][j-1]+1, d[i-1][j-1]+(a[i-1]!==b[j-1]?1:0));
  return d[m][n];
}
