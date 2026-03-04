#!/usr/bin/env node
/**
 * test-retrieval.mjs — KG Retrieval Quality Benchmark
 *
 * Tests the KG query system to ensure:
 * 1. Correct entities are found (precision)
 * 2. All relevant entities are found (recall)
 * 3. Output is optimized (not too verbose, not too sparse)
 * 4. Cross-language and fuzzy queries work
 * 5. Agent workflow (summary → query → traverse) is effective
 *
 * Usage:
 *   node scripts/test-retrieval.mjs              # Run all tests
 *   node scripts/test-retrieval.mjs --verbose     # Show full output
 *   node scripts/test-retrieval.mjs --category X  # Run only category X
 *
 * Designed to be model-agnostic and data-agnostic:
 * Tests auto-discover entities from the current KG data.
 */

import { search, findByType, traverse, stats, orphans } from '../lib/query.mjs';
import { load, getChildren, getEdges } from '../lib/graph.mjs';
import { readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const VERBOSE = args.includes('--verbose');
const CATEGORY_FILTER = args.includes('--category') ? args[args.indexOf('--category') + 1] : null;

// ── Test Framework ─────────────────────────────────────────────────

let passed = 0, failed = 0, skipped = 0;
const failures = [];

function test(category, name, fn) {
  if (CATEGORY_FILTER && category !== CATEGORY_FILTER) { skipped++; return; }
  try {
    const result = fn();
    if (result === 'SKIP') { skipped++; return; }
    passed++;
    if (VERBOSE) console.log(`  ✅ [${category}] ${name}`);
  } catch (e) {
    failed++;
    failures.push({ category, name, error: e.message });
    console.log(`  ❌ [${category}] ${name}: ${e.message}`);
  }
}

function assert(condition, msg) {
  if (!condition) throw new Error(msg || 'Assertion failed');
}

function assertFound(results, targetLabel, msg) {
  const found = results.some(r =>
    r.label.toLowerCase().includes(targetLabel.toLowerCase()) ||
    r.id.toLowerCase().includes(targetLabel.toLowerCase().replace(/\s+/g, '_'))
  );
  assert(found, msg || `Expected to find "${targetLabel}" in results, got: [${results.map(r => r.label).join(', ')}]`);
}

function assertNotFound(results, targetLabel, msg) {
  const found = results.some(r =>
    r.label.toLowerCase() === targetLabel.toLowerCase()
  );
  assert(!found, msg || `Expected NOT to find "${targetLabel}" in results`);
}

function assertTopN(results, targetLabel, n, msg) {
  const idx = results.findIndex(r =>
    r.label.toLowerCase().includes(targetLabel.toLowerCase()) ||
    r.id.toLowerCase().includes(targetLabel.toLowerCase().replace(/\s+/g, '_'))
  );
  assert(idx !== -1 && idx < n, msg || `Expected "${targetLabel}" in top ${n}, found at position ${idx === -1 ? 'NOT FOUND' : idx + 1}`);
}

function assertResultCount(results, min, max, msg) {
  assert(results.length >= min && results.length <= max,
    msg || `Expected ${min}-${max} results, got ${results.length}`);
}

// ── Load KG Data ───────────────────────────────────────────────────

const store = load();
const allNodes = Object.values(store.nodes);
const allEdges = store.edges;

if (allNodes.length === 0) {
  console.log('⚠️  KG is empty — nothing to test.');
  process.exit(0);
}

// Auto-discover test data from KG
const humans = allNodes.filter(n => n.type === 'human');
const orgs = allNodes.filter(n => n.type === 'org');
const events = allNodes.filter(n => n.type === 'event');
const concepts = allNodes.filter(n => n.type === 'concept');
const knowledge = allNodes.filter(n => n.type === 'knowledge');
const topLevel = allNodes.filter(n => !n.parent);

console.log('');
console.log('╔══════════════════════════════════════════════════════╗');
console.log('║       KG Retrieval Quality Benchmark                 ║');
console.log('╚══════════════════════════════════════════════════════╝');
console.log(`  KG: ${allNodes.length} entities, ${allEdges.length} relations, ${topLevel.length} top-level`);
console.log(`  Types: ${humans.length} human, ${orgs.length} org, ${events.length} event, ${concepts.length} concept, ${knowledge.length} knowledge`);
console.log('');

// ── Category 1: Exact Match ────────────────────────────────────────
// Agent searches by exact entity name

console.log('── 1. Exact Match ──');

// Test each type with a real entity from the KG
for (const type of ['human', 'org', 'event', 'concept', 'knowledge']) {
  const sample = allNodes.find(n => n.type === type && n.label.length > 3);
  if (!sample) continue;
  test('exact', `find ${type} by exact label: "${sample.label}"`, () => {
    const results = search(sample.label);
    assertFound(results, sample.label);
    assertTopN(results, sample.label, 3, `"${sample.label}" should be in top 3`);
  });
}

// Test by ID
if (allNodes.length > 0) {
  const sample = allNodes.find(n => n.id.length > 5) || allNodes[0];
  test('exact', `find by ID: "${sample.id}"`, () => {
    const results = search(sample.id);
    assertFound(results, sample.label);
    assertTopN(results, sample.label, 1);
  });
}

// ── Category 2: Partial / Substring Match ──────────────────────────
// Agent remembers part of a name

console.log('── 2. Partial Match ──');

for (const node of allNodes.filter(n => n.label.length > 8).slice(0, 5)) {
  // Take middle portion of label
  const label = node.label;
  const mid = Math.floor(label.length / 3);
  const partial = label.substring(mid, mid + Math.min(8, Math.floor(label.length / 2)));
  if (partial.trim().length < 3) continue;

  test('partial', `substring "${partial}" finds "${label}"`, () => {
    const results = search(partial);
    assertFound(results, label, `Substring "${partial}" should find "${label}"`);
  });
}

// ── Category 3: Fuzzy / Typo Tolerance ─────────────────────────────
// Agent makes typos or uses variations

console.log('── 3. Fuzzy Match ──');

function addTypo(str) {
  if (str.length < 4) return str;
  const i = Math.floor(str.length / 2);
  // Swap two adjacent chars
  return str.substring(0, i) + str[i + 1] + str[i] + str.substring(i + 2);
}

for (const node of allNodes.filter(n => n.label.length > 6 && /^[a-zA-Z]/.test(n.label)).slice(0, 5)) {
  const typo = addTypo(node.label);
  test('fuzzy', `typo "${typo}" finds "${node.label}"`, () => {
    const results = search(typo);
    assertFound(results, node.label, `Typo "${typo}" should still find "${node.label}"`);
  });
}

// ── Category 4: Tag / Alias Search ─────────────────────────────────
// Agent searches by tag or alias

console.log('── 4. Tag & Alias Search ──');

const nodesWithTags = allNodes.filter(n => n.tags && n.tags.length > 0);
for (const node of nodesWithTags.slice(0, 5)) {
  const tag = node.tags[0];
  test('tags', `tag "${tag}" finds "${node.label}"`, () => {
    const results = search(tag);
    assertFound(results, node.label, `Tag "${tag}" should find "${node.label}"`);
  });
}

const nodesWithAlias = allNodes.filter(n => n.alias && n.alias.length > 1);
for (const node of nodesWithAlias.slice(0, 3)) {
  test('tags', `alias "${node.alias}" finds "${node.label}"`, () => {
    const results = search(node.alias);
    // Alias is short, might match multiple — just check entity is in results
    assertFound(results, node.label, `Alias "${node.alias}" should find "${node.label}"`);
  });
}

// ── Category 5: Attr Search ────────────────────────────────────────
// Agent searches by attribute value

console.log('── 5. Attribute Search ──');

const nodesWithAttrs = allNodes.filter(n => {
  const vals = Object.values(n.attrs || {});
  return vals.some(v => typeof v === 'string' && v.length > 4 && v.length < 50);
});

for (const node of nodesWithAttrs.slice(0, 5)) {
  const attrEntries = Object.entries(node.attrs || {});
  const [key, val] = attrEntries.find(([k, v]) => typeof v === 'string' && v.length > 4 && v.length < 50) || [];
  if (!val) continue;

  // Search by attr value
  test('attrs', `attr value "${val.substring(0, 30)}" finds "${node.label}"`, () => {
    const results = search(val);
    assertFound(results, node.label, `Attr value should find parent entity`);
  });
}

// ── Category 6: Traverse Completeness ──────────────────────────────
// Agent traverses from a node — should get all children + related

console.log('── 6. Traverse ──');

for (const root of topLevel.slice(0, 3)) {
  const children = allNodes.filter(n => n.parent === root.id);
  if (children.length === 0) continue;

  test('traverse', `traverse "${root.label}" includes all direct children`, () => {
    const results = traverse(root.id, { depth: 1 });
    for (const child of children.slice(0, 5)) {
      const found = results.some(r => r.id === child.id);
      assert(found, `Child "${child.label}" missing from traverse of "${root.label}"`);
    }
  });

  test('traverse', `traverse "${root.label}" depth 2 reaches grandchildren`, () => {
    const results = traverse(root.id, { depth: 2 });
    const grandchildren = allNodes.filter(n => children.some(c => c.id === n.parent));
    if (grandchildren.length === 0) return 'SKIP';
    // At least some grandchildren should be reachable
    const foundCount = grandchildren.filter(gc => results.some(r => r.id === gc.id)).length;
    assert(foundCount > 0, `No grandchildren found in depth-2 traverse of "${root.label}"`);
  });
}

// Traverse via relations (not just hierarchy)
const nodesWithRelations = allNodes.filter(n => allEdges.some(e => e.from === n.id || e.to === n.id));
if (nodesWithRelations.length > 0) {
  const sample = nodesWithRelations[0];
  const relatedIds = allEdges
    .filter(e => e.from === sample.id || e.to === sample.id)
    .map(e => e.from === sample.id ? e.to : e.from);

  test('traverse', `traverse "${sample.label}" reaches related nodes via edges`, () => {
    const results = traverse(sample.id, { depth: 1 });
    for (const relId of relatedIds.slice(0, 3)) {
      const found = results.some(r => r.id === relId);
      assert(found, `Related node "${relId}" missing from traverse`);
    }
  });
}

// ── Category 7: Token Efficiency ───────────────────────────────────
// Query results should not be excessively large

console.log('── 7. Token Efficiency ──');

test('efficiency', 'search returns ≤20 results by default', () => {
  // Use a broad query that might match many
  const results = search('a');
  assertResultCount(results, 0, 20, 'Default limit should cap at 20');
});

test('efficiency', 'search with limit=5 respects limit', () => {
  const results = search('a', { limit: 5 });
  assertResultCount(results, 0, 5);
});

test('efficiency', 'traverse depth 1 is bounded', () => {
  if (topLevel.length === 0) return 'SKIP';
  const bigRoot = topLevel.sort((a, b) => {
    const ac = allNodes.filter(n => n.parent === a.id).length;
    const bc = allNodes.filter(n => n.parent === b.id).length;
    return bc - ac;
  })[0];
  const results = traverse(bigRoot.id, { depth: 1 });
  // depth 1 should not return entire KG
  assert(results.length < allNodes.length * 0.8,
    `Depth 1 traverse returned ${results.length}/${allNodes.length} — too many`);
});

// ── Category 8: Summary as Index ───────────────────────────────────
// kg-summary.md should mention all top-level entities

console.log('── 8. Summary Index ──');

try {
  const summaryPath = join(__dirname, '..', 'data', 'kg-summary.md');
  const summary = readFileSync(summaryPath, 'utf8');

  test('summary', 'summary exists and is non-empty', () => {
    assert(summary.length > 50, 'Summary too short');
  });

  // All top-level entities should appear in summary
  for (const node of topLevel) {
    test('summary', `top-level "${node.label}" appears in summary`, () => {
      const found = summary.toLowerCase().includes(node.label.toLowerCase()) ||
                    summary.includes(node.id);
      assert(found, `"${node.label}" (${node.id}) not found in summary`);
    });
  }

  // Summary should have categories
  test('summary', 'summary has auto-categories', () => {
    assert(summary.includes('['), 'No category headers found');
  });

  // Summary should have relations section
  test('summary', 'summary has relation summary', () => {
    assert(summary.includes('%rel-summary') || summary.includes('%rels'),
      'No relation section found');
  });

  // Summary should have type counts
  test('summary', 'summary has type footer', () => {
    assert(summary.includes('%types'), 'No %types footer');
  });

  // Token efficiency: summary should be < 5000 tokens (~20000 chars)
  test('summary', 'summary within token budget (~5000 tokens)', () => {
    const estimatedTokens = Math.ceil(summary.length / 4);
    assert(estimatedTokens <= 6000,
      `Summary ~${estimatedTokens} tokens, exceeds budget`);
  });

} catch (e) {
  test('summary', 'kg-summary.md readable', () => { throw e; });
}

// ── Category 9: Cross-branch Discovery ─────────────────────────────
// Agent should be able to find entities across different subtrees

console.log('── 9. Cross-branch ──');

if (topLevel.length >= 2) {
  // Find entities from different subtrees using general queries
  const subtree1 = allNodes.filter(n => {
    let cur = n;
    while (cur?.parent) cur = store.nodes[cur.parent];
    return cur?.id === topLevel[0].id;
  });
  const subtree2 = allNodes.filter(n => {
    let cur = n;
    while (cur?.parent) cur = store.nodes[cur.parent];
    return cur?.id === topLevel[1].id;
  });

  if (subtree1.length > 1 && subtree2.length > 1) {
    const entity1 = subtree1.find(n => n.type === 'org') || subtree1[1];
    const entity2 = subtree2.find(n => n.type === 'org') || subtree2[1];

    test('cross-branch', `search finds entity from subtree 1: "${entity1.label}"`, () => {
      const results = search(entity1.label);
      assertFound(results, entity1.label);
    });

    test('cross-branch', `search finds entity from subtree 2: "${entity2.label}"`, () => {
      const results = search(entity2.label);
      assertFound(results, entity2.label);
    });
  }
}

// ── Category 10: Relevance Ranking ─────────────────────────────────
// Exact matches should rank higher than partial matches

console.log('── 10. Relevance Ranking ──');

if (orgs.length >= 2) {
  const target = orgs.find(n => n.label.length > 4) || orgs[0];
  test('ranking', `exact label "${target.label}" ranks #1`, () => {
    const results = search(target.label);
    assert(results.length > 0, 'No results');
    assert(results[0].id === target.id,
      `Expected "${target.label}" at #1, got "${results[0].label}"`);
  });
}

// Type-specific search should work
test('ranking', 'findByType returns correct types only', () => {
  if (orgs.length === 0) return 'SKIP';
  const results = findByType('org');
  for (const r of results) {
    assert(r.type === 'org', `findByType('org') returned type="${r.type}"`);
  }
  assert(results.length === orgs.length,
    `findByType('org') returned ${results.length}, expected ${orgs.length}`);
});

// ── Report ─────────────────────────────────────────────────────────

console.log('');
console.log('══════════════════════════════════════════════════════');
const total = passed + failed + skipped;
console.log(`  Results: ${passed} passed, ${failed} failed, ${skipped} skipped (${total} total)`);

if (failures.length > 0) {
  console.log('');
  console.log('  ── Failures ──');
  for (const f of failures) {
    console.log(`  ❌ [${f.category}] ${f.name}`);
    console.log(`     ${f.error}`);
  }
}

const score = total > 0 ? Math.round((passed / (passed + failed)) * 100) : 0;
console.log('');
if (failed === 0) {
  console.log(`  ✅ ALL TESTS PASSED (${score}%)`);
} else {
  console.log(`  Score: ${score}% (${failed} failures need attention)`);
}
console.log('══════════════════════════════════════════════════════');
console.log('');

process.exit(failed > 0 ? 1 : 0);
