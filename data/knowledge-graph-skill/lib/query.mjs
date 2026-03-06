// query.mjs — Hybrid search (exact + trigram fuzzy + BM25) + traversal

import { load, bumpAccess } from './graph.mjs';

// ── Text normalization ──────────────────────────────────────────────

function normalize(s) {
  return (s || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim();
}

function tokenize(s) {
  return normalize(s).split(/[\s_\-./,;:!?()[\]{}'"]+/).filter(t => t.length > 0);
}

// ── Trigram fuzzy matching ──────────────────────────────────────────

function trigrams(s) {
  const n = normalize(s);
  if (n.length < 3) return new Set([n]);
  const set = new Set();
  for (let i = 0; i <= n.length - 3; i++) set.add(n.slice(i, i + 3));
  return set;
}

/** Sørensen–Dice coefficient over trigram sets: 0..1
 *  Very short strings (<4 chars) get penalized to reduce false positives. */
function trigramSimilarity(a, b) {
  const na = normalize(a);
  const nb = normalize(b);
  const ta = trigrams(a);
  const tb = trigrams(b);
  if (ta.size === 0 && tb.size === 0) return 1;
  if (ta.size === 0 || tb.size === 0) return 0;
  let overlap = 0;
  for (const t of ta) if (tb.has(t)) overlap++;
  let sim = (2 * overlap) / (ta.size + tb.size);
  // Penalize when query is very short (1 trigram = high false positive rate)
  // e.g. "pho" matches "phone" at 0.5 which is misleading
  const minLen = Math.min(na.length, nb.length);
  if (minLen < 4) sim *= 0.5;
  return sim;
}

/** Best trigram match of query against a list of candidate strings.
 *  Tries both full-string match and per-token match for multi-word queries. */
function bestTrigramMatch(query, candidates) {
  let best = 0;
  const qTokens = tokenize(query);
  for (const c of candidates) {
    // Full string match
    const full = trigramSimilarity(query, c);
    if (full > best) best = full;
    // Per-token: each query token vs each candidate
    for (const qt of qTokens) {
      const sim = trigramSimilarity(qt, c);
      if (sim > best) best = sim;
    }
  }
  return best;
}

/** Per-token trigram: for each query token, find best match in candidate tokens */
function tokenTrigramScore(queryTokens, candidateTokens) {
  if (queryTokens.length === 0 || candidateTokens.length === 0) return 0;
  let totalSim = 0;
  for (const qt of queryTokens) {
    let bestSim = 0;
    for (const ct of candidateTokens) {
      const sim = trigramSimilarity(qt, ct);
      if (sim > bestSim) bestSim = sim;
    }
    totalSim += bestSim;
  }
  return totalSim / queryTokens.length;
}

// ── BM25 scoring ────────────────────────────────────────────────────

const BM25_K1 = 1.2;
const BM25_B = 0.75;

function buildBM25Index(docs) {
  // docs: [{ id, tokens: string[] }]
  const N = docs.length;
  // Document frequency per term
  const df = new Map();
  let totalLen = 0;
  for (const doc of docs) {
    totalLen += doc.tokens.length;
    const seen = new Set(doc.tokens);
    for (const t of seen) df.set(t, (df.get(t) || 0) + 1);
  }
  const avgdl = totalLen / (N || 1);

  // IDF: log((N - df + 0.5) / (df + 0.5) + 1)
  const idf = new Map();
  for (const [term, freq] of df) {
    idf.set(term, Math.log((N - freq + 0.5) / (freq + 0.5) + 1));
  }

  return { N, avgdl, idf, df };
}

function bm25Score(queryTokens, docTokens, index) {
  const dl = docTokens.length;
  if (dl === 0) return 0;
  // Term frequency in this doc
  const tf = new Map();
  for (const t of docTokens) tf.set(t, (tf.get(t) || 0) + 1);

  let score = 0;
  for (const qt of queryTokens) {
    const termIdf = index.idf.get(qt);
    if (termIdf === undefined) continue; // term not in corpus
    const termTf = tf.get(qt) || 0;
    if (termTf === 0) continue;
    const num = termTf * (BM25_K1 + 1);
    const denom = termTf + BM25_K1 * (1 - BM25_B + BM25_B * (dl / index.avgdl));
    score += termIdf * (num / denom);
  }
  return score;
}

// ── Gather all searchable text for a node ───────────────────────────

function nodeSearchTokens(node) {
  const parts = [
    node.id, node.label, node.alias,
    ...(node.tags || []),
    ...Object.values(node.attrs || {}).map(String),
  ];
  return tokenize(parts.join(' '));
}

function nodeSearchStrings(node) {
  return [
    node.id, node.label, node.alias,
    ...(node.tags || []),
    ...Object.values(node.attrs || {}).map(String),
  ].filter(Boolean);
}

// ── Hybrid scoring ──────────────────────────────────────────────────

const EXACT_BOOST   = 100;
const TRIGRAM_BOOST  = 60;
const BM25_BOOST     = 40;
const TRIGRAM_THRESHOLD = 0.35; // minimum trigram similarity to count

function hybridScoreNode(node, queryTokens, queryRaw, bm25Index) {
  let score = 0;
  const nq = normalize(queryRaw);

  // ── Layer 1: Exact & substring match (fast, high confidence) ──
  const exactFields = [
    { val: node.id,    exactW: 100, partialW: 50 },
    { val: node.alias, exactW: 90,  partialW: 45 },
    { val: node.label, exactW: 80,  partialW: 40 },
  ];
  for (const f of exactFields) {
    const nv = normalize(f.val || '');
    if (!nv) continue;
    if (nv === nq) score += f.exactW;
    else if (nv.includes(nq) || nq.includes(nv)) score += f.partialW;
  }
  // Exact tag match
  for (const t of node.tags || []) {
    const nt = normalize(t);
    if (nt === nq) { score += 60; break; }
    if (nt.includes(nq) || nq.includes(nt)) { score += 30; break; }
  }

  // ── Layer 2: Trigram fuzzy match ──
  const candidates = nodeSearchStrings(node);
  const candidateTokens = tokenize(candidates.join(' '));
  
  // Full-string trigram (catches "raspi" ~ "raspberry")
  const fullTrigram = bestTrigramMatch(queryRaw, candidates);
  if (fullTrigram >= TRIGRAM_THRESHOLD) {
    score += Math.round(fullTrigram * TRIGRAM_BOOST);
  }

  // Token-level trigram (catches multi-word fuzzy: "knowlege graf" ~ "knowledge graph")
  const tokenTrigram = tokenTrigramScore(queryTokens, candidateTokens);
  if (tokenTrigram >= TRIGRAM_THRESHOLD) {
    score += Math.round(tokenTrigram * TRIGRAM_BOOST * 0.8);
  }

  // ── Layer 3: BM25 (term importance weighting) ──
  const docTokens = nodeSearchTokens(node);
  const bm25 = bm25Score(queryTokens, docTokens, bm25Index);
  if (bm25 > 0) {
    score += Math.round(bm25 * BM25_BOOST);
  }

  return score;
}

// ── Public API ──────────────────────────────────────────────────────

export function search(query, opts = {}) {
  const store = load();
  const nodes = Object.values(store.nodes);
  if (nodes.length === 0) return [];

  const queryTokens = tokenize(query);

  // Build BM25 index over all entities
  const docs = nodes.map(n => ({ id: n.id, tokens: nodeSearchTokens(n) }));
  const bm25Index = buildBM25Index(docs);

  const results = [];
  for (const node of nodes) {
    const score = hybridScoreNode(node, queryTokens, query, bm25Index);
    if (score > 0) results.push({ ...node, _score: score });
  }
  results.sort((a, b) => b._score - a._score);
  const top = results.slice(0, opts.limit || 20);
  // Track access for search hits
  if (top.length) {
    try { bumpAccess(top.map(r => r.id)); } catch {}
  }
  return top;
}

export function findByType(type) {
  const store = load();
  return Object.values(store.nodes).filter(n => n.type === type);
}

export function findByCategory(cat) {
  const store = load();
  const ids = store.categories[cat] || [];
  return ids.map(id => store.nodes[id]).filter(Boolean);
}

export function traverse(startId, opts = {}) {
  const store = load();
  const maxDepth = opts.depth || 3;
  const visited = new Set();
  const result = [];

  function walk(id, depth) {
    if (depth > maxDepth || visited.has(id)) return;
    visited.add(id);
    const node = store.nodes[id];
    if (!node) return;
    result.push({ ...node, _depth: depth });
    // children (hierarchy)
    for (const n of Object.values(store.nodes)) {
      if (n.parent === id) walk(n.id, depth + 1);
    }
    // edges
    for (const e of store.edges) {
      if (e.from === id) walk(e.to, depth + 1);
      if (e.to === id) walk(e.from, depth + 1);
    }
  }

  walk(startId, 0);
  // Track access for traversed nodes
  if (result.length) {
    try { bumpAccess(result.map(r => r.id)); } catch {}
  }
  return result;
}

export function reverseRels(nodeId) {
  const store = load();
  return store.edges
    .filter(e => e.to === nodeId)
    .map(e => ({ ...e, sourceNode: store.nodes[e.from] }));
}

export function stats() {
  const store = load();
  const nodes = Object.values(store.nodes);
  const types = {};
  for (const n of nodes) types[n.type] = (types[n.type] || 0) + 1;
  const topLevel = nodes.filter(n => !n.parent).length;
  const rels = {};
  for (const e of store.edges) rels[e.rel] = (rels[e.rel] || 0) + 1;
  return {
    entities: nodes.length,
    edges: store.edges.length,
    topLevel,
    maxDepth: store.meta.maxDepth,
    categories: Object.keys(store.categories).length,
    types,
    relations: rels,
    lastConsolidated: store.meta.lastConsolidated
  };
}

export function orphans() {
  const store = load();
  return Object.values(store.nodes).filter(n => {
    if (n.parent) return false;
    const hasEdge = store.edges.some(e => e.from === n.id || e.to === n.id);
    const hasChild = Object.values(store.nodes).some(c => c.parent === n.id);
    return !hasEdge && !hasChild;
  });
}
