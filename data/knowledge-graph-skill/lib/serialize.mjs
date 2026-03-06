// serialize.mjs — JSON store → KGML v2 summary
// Purpose: Generate a compact INDEX of the KG that helps agents decide what to query.
// Budget-aware but optimized for discoverability over brevity.
//
// Strategy:
// - Auto-categorize top-level nodes by type (people, articles, orgs, etc.)
// - Show full tree up to depth 2 for small/medium KGs
// - For large KGs: show all top-level + their direct children (collapsed deeper)
// - Always show relation summary grouped by pattern
// - Token budget: ~2500 (lazy-loaded, not always in context)

import { load, loadAccess } from './graph.mjs';
import { loadConfig } from './config.mjs';

const TOKENS_PER_LINE = 8; // rough estimate

// Auto-category labels by entity type
const TYPE_CATEGORIES = {
  human:      '👤 People',
  ai:         '🤖 AI Agents',
  knowledge:  '📚 Articles & Knowledge',
  org:        '🏢 Organizations',
  project:    '🔨 Projects',
  platform:   '🌐 Platforms',
  device:     '💻 Devices',
  service:    '⚙️ Services',
  place:      '📍 Places',
  event:      '📅 Events',
  decision:   '⚖️ Decisions',
  concept:    '💡 Concepts',
  account:    '🔑 Accounts',
  credential: '🔐 Credentials',
  media:      '🎬 Media',
  product:    '📦 Products',
  routine:    '🔄 Routines',
  skill:      '🎯 Skills',
  network:    '🌐 Networks',
};

function getCategoryLabel(type) {
  return TYPE_CATEGORIES[type] || '📎 Other';
}

export async function toKGMLAsync(opts = {}) {
  const store = load();
  const cfg = loadConfig();
  const sc = cfg.summary; // summary config
  const maxTokens = opts.maxTokens || sc.tokenBudget;
  const allNodes = Object.values(store.nodes);
  const totalEntities = allNodes.length;
  const totalEdges = store.edges.length;
  const d = store.meta;
  const today = new Date().toISOString().slice(0, 10);

  // Determine rendering strategy based on size (configurable thresholds)
  let maxChildDepth = sc.maxChildDepth; // null = auto
  let maxAttrLen = sc.maxAttrLen;
  let showAllRelations = true;

  if (maxChildDepth === null) {
    // Auto strategy
    if (totalEntities > sc.compactThreshold) {
      maxChildDepth = 1;
      maxAttrLen = Math.min(maxAttrLen, 25);
      showAllRelations = false;
    } else if (totalEntities > sc.mediumThreshold) {
      maxChildDepth = 2;
      maxAttrLen = Math.min(maxAttrLen, 30);
    } else {
      maxChildDepth = 3;
    }
  }

  // Deduplicate aliases
  const aliasMap = new Map();
  const resolvedAlias = new Map();
  for (const n of allNodes) {
    const base = n.alias || n.id.slice(0, 3).toUpperCase();
    if (!aliasMap.has(base)) {
      aliasMap.set(base, n.id);
      resolvedAlias.set(n.id, base);
    } else {
      let alt = base + n.id.charAt(0).toUpperCase();
      let i = 2;
      while (aliasMap.has(alt) && i < 5) { alt = base + i; i++; }
      aliasMap.set(alt, n.id);
      resolvedAlias.set(n.id, alt);
    }
  }

  const lines = [];
  lines.push(`#KGML v2 | ${d.entityCount}e ${d.edgeCount}r | depth:${d.maxDepth} | ${today}`);

  // ── Auto-categorize top-level nodes by type ──
  const topLevel = allNodes.filter(n => !n.parent);
  const categories = new Map(); // categoryLabel → [node, ...]

  for (const n of topLevel) {
    // Use explicit category if set, otherwise auto-categorize by type
    let catLabel;
    let found = false;
    for (const [cat, ids] of Object.entries(store.categories)) {
      if (ids.includes(n.id)) {
        catLabel = cat;
        found = true;
        break;
      }
    }
    if (!found) catLabel = getCategoryLabel(n.type);

    if (!categories.has(catLabel)) categories.set(catLabel, []);
    categories.get(catLabel).push(n);
  }

  // Sort categories: People first, then Articles, then rest alphabetically
  const catOrder = ['👤 People', '🤖 AI Agents', '📚 Articles & Knowledge', '🏢 Organizations',
    '🌐 Platforms', '📅 Events', '🔑 Accounts'];
  const sortedCats = [...categories.keys()].sort((a, b) => {
    const ai = catOrder.indexOf(a), bi = catOrder.indexOf(b);
    if (ai !== -1 && bi !== -1) return ai - bi;
    if (ai !== -1) return -1;
    if (bi !== -1) return 1;
    return a.localeCompare(b);
  });

  // ── Render each category ──
  function renderNode(node, indent, currentDepth) {
    const prefix = '  '.repeat(indent);
    const displayAlias = resolvedAlias.get(node.id) || '';
    const alias = displayAlias ? `(${displayAlias})` : '';

    // Format attrs — show key highlights
    const attrStr = Object.entries(node.attrs || {})
      .filter(([k]) => !k.startsWith('vault'))
      .map(([k, v]) => {
        const sv = String(v);
        if (sv.length > maxAttrLen || !sv) return '';
        return `${k}:${sv}`;
      })
      .filter(Boolean)
      .join(', ');

    const confMarker = (node.confidence !== undefined && node.confidence < 0.7) ? '?' : '';
    let line = prefix + node.label + confMarker + alias + ':' + node.type;
    if (attrStr) line += ' — ' + attrStr;
    lines.push(line);

    // Children
    const children = allNodes.filter(c => c.parent === node.id);
    if (children.length === 0) return;

    if (currentDepth < maxChildDepth) {
      children.sort((a, b) => a.label.localeCompare(b.label));
      for (const child of children) {
        renderNode(child, indent + 1, currentDepth + 1);
      }
    } else {
      // Collapse — show count + types summary
      const typeCounts = {};
      children.forEach(c => { typeCounts[c.type] = (typeCounts[c.type] || 0) + 1; });
      const typeSummary = Object.entries(typeCounts)
        .map(([t, c]) => `${c} ${t}`)
        .join(', ');
      lines.push(prefix + `  ↳ ${children.length} children (${typeSummary})`);
    }
  }

  for (const catLabel of sortedCats) {
    const catNodes = categories.get(catLabel);
    lines.push('');
    lines.push(`[${catLabel}]`);
    catNodes.sort((a, b) => a.label.localeCompare(b.label));
    for (const n of catNodes) {
      renderNode(n, 0, 0);
    }
  }

  // ── Relations section ──
  if (totalEdges > 0) {
    lines.push('');

    // Helper: find root ancestor of a node
    function getRoot(nodeId) {
      let cur = store.nodes[nodeId];
      while (cur?.parent && store.nodes[cur.parent]) cur = store.nodes[cur.parent];
      return cur?.id;
    }

    // Relation type summary
    lines.push('%rel-summary');
    const relTypes = {};
    for (const e of store.edges) relTypes[e.rel] = (relTypes[e.rel] || 0) + 1;
    lines.push(Object.entries(relTypes).sort((a, b) => b[1] - a[1]).map(([r, c]) => `${r}(${c})`).join(' '));

    // Group ALL relations by root subtree, show top N from each
    const byRootLabel = new Map(); // rootLabel → [edge, ...]
    for (const e of store.edges) {
      const rootId = getRoot(e.from);
      const rootNode = store.nodes[rootId];
      const label = rootNode?.label || rootId;
      if (!byRootLabel.has(label)) byRootLabel.set(label, []);
      byRootLabel.get(label).push(e);
    }

    lines.push('%key-relations');
    const maxPerRoot = sc.maxPerRoot;
    for (const [rootLabel, edges] of byRootLabel) {
      // Prioritize: non-self relations, diverse rel types, cross-branch first
      const sorted = edges.sort((a, b) => {
        const aCross = getRoot(a.from) !== getRoot(a.to) ? 1 : 0;
        const bCross = getRoot(b.from) !== getRoot(b.to) ? 1 : 0;
        return bCross - aCross; // cross-branch first
      });
      const shown = sorted.slice(0, maxPerRoot);
      const remaining = edges.length - shown.length;
      lines.push(`  [${rootLabel}]`);
      for (const e of shown) {
        const fromNode = store.nodes[e.from];
        const toNode = store.nodes[e.to];
        lines.push(`    ${fromNode?.label || e.from} >${e.rel}> ${toNode?.label || e.to}`);
      }
      if (remaining > 0) lines.push(`    ... +${remaining} more`);
    }
  }

  // ── Quick stats footer ──
  lines.push('');
  const typeCounts = {};
  allNodes.forEach(n => { typeCounts[n.type] = (typeCounts[n.type] || 0) + 1; });
  const typeStr = Object.entries(typeCounts)
    .sort((a, b) => b[1] - a[1])
    .map(([t, c]) => `${t}:${c}`)
    .join(' ');
  lines.push(`%types ${typeStr}`);

  // Vault keys
  try {
    const { vaultList } = await import('./vault.mjs');
    const vkeys = vaultList();
    if (vkeys.length) {
      lines.push(`%vault ${vkeys.map(v => v.key).join(',')}`);
    }
  } catch { /* no vault */ }

  return lines.join('\n') + '\n';
}

// Sync wrapper
export function toKGML(opts = {}) {
  let result = '';
  const p = toKGMLAsync(opts).then(r => { result = r; });
  return result || '(use toKGMLAsync() for full output)\n';
}
