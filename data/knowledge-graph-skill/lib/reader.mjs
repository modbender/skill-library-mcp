// reader.mjs — Read-only KG access for other agents
// Import this from any agent script to query the KG without modifying it.
//
// Usage:
//   import { createReader } from '<skill-dir>/lib/reader.mjs';
//   const kg = createReader(); // uses default store path
//   const kg = createReader('/custom/path/kg-store.json'); // custom path
//
// API:
//   kg.search(query, opts?)         — multi-layer search, returns nodes[]
//   kg.getNode(id)                  — get single node by id
//   kg.traverse(id, opts?)          — BFS from node, returns nodes[]
//   kg.stats()                      — graph statistics object

import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DEFAULT_STORE = join(__dirname, '..', 'data', 'kg-store.json');

const EMPTY_STORE = {
  version: 2,
  meta: { entityCount: 0, edgeCount: 0, maxDepth: 0 },
  nodes: {}, edges: [], categories: {}
};

function loadStore(storePath) {
  const path = storePath || DEFAULT_STORE;
  if (!existsSync(path)) return structuredClone(EMPTY_STORE);
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch {
    return structuredClone(EMPTY_STORE);
  }
}

function normalize(s) {
  return (s || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
}

function scoreNode(node, q) {
  const nq = normalize(q);
  let score = 0;
  if (normalize(node.id) === nq) score += 100;
  if (normalize(node.alias) === nq) score += 90;
  if (normalize(node.label) === nq) score += 80;
  if (normalize(node.id).includes(nq)) score += 50;
  if (normalize(node.label).includes(nq)) score += 40;
  for (const t of node.tags || []) {
    if (normalize(t) === nq) { score += 60; break; }
    if (normalize(t).includes(nq)) { score += 30; break; }
  }
  for (const v of Object.values(node.attrs || {})) {
    if (normalize(String(v)).includes(nq)) { score += 20; break; }
  }
  return score;
}

/**
 * Create a read-only KG reader.
 * @param {string} [storePath] - Optional path to kg-store.json
 * @param {object} [opts]
 * @param {boolean} [opts.cache=true] - Cache store in memory (reload once)
 */
export function createReader(storePath, opts = {}) {
  const useCache = opts.cache !== false;
  let _store = null;

  function store() {
    if (!useCache || !_store) _store = loadStore(storePath);
    return _store;
  }

  /**
   * Reload the store from disk (useful if the KG was modified externally)
   */
  function reload() {
    _store = loadStore(storePath);
    return _store.meta;
  }

  /**
   * Multi-layer search across id, alias, label, tags, and attrs.
   * @param {string} query
   * @param {object} [opts]
   * @param {number} [opts.limit=20]
   * @param {string} [opts.type] - Filter by type
   * @param {number} [opts.minScore=1] - Minimum score threshold
   * @returns {Array} - Matching nodes sorted by score, each with _score property
   */
  function search(query, opts = {}) {
    const s = store();
    const limit = opts.limit || 20;
    const typeFilter = opts.type || null;
    const minScore = opts.minScore || 1;
    const results = [];
    for (const node of Object.values(s.nodes)) {
      if (typeFilter && node.type !== typeFilter) continue;
      const score = scoreNode(node, query);
      if (score >= minScore) results.push({ ...node, _score: score });
    }
    results.sort((a, b) => b._score - a._score);
    return results.slice(0, limit);
  }

  /**
   * Get a single node by ID.
   * @param {string} id
   * @returns {object|null}
   */
  function getNode(id) {
    return store().nodes[id] || null;
  }

  /**
   * BFS traversal from a starting node.
   * @param {string} startId
   * @param {object} [opts]
   * @param {number} [opts.depth=3] - Max traversal depth
   * @param {boolean} [opts.includeParent=true] - Follow parent-child links
   * @param {boolean} [opts.includeEdges=true] - Follow explicit edges
   * @returns {Array} - Reachable nodes with _depth property
   */
  function traverse(startId, opts = {}) {
    const s = store();
    const maxDepth = opts.depth || 3;
    const includeParent = opts.includeParent !== false;
    const includeEdges = opts.includeEdges !== false;
    const visited = new Set();
    const result = [];

    function walk(id, depth) {
      if (depth > maxDepth || visited.has(id)) return;
      visited.add(id);
      const node = s.nodes[id];
      if (!node) return;
      result.push({ ...node, _depth: depth });
      // Children (hierarchy)
      if (includeParent) {
        for (const n of Object.values(s.nodes)) {
          if (n.parent === id) walk(n.id, depth + 1);
        }
        // Also follow to parent
        if (node.parent) walk(node.parent, depth + 1);
      }
      // Edges
      if (includeEdges) {
        for (const e of s.edges) {
          if (e.from === id) walk(e.to, depth + 1);
          if (e.to === id) walk(e.from, depth + 1);
        }
      }
    }

    walk(startId, 0);
    return result;
  }

  /**
   * Graph statistics.
   * @returns {object}
   */
  function stats() {
    const s = store();
    const nodes = Object.values(s.nodes);
    const types = {};
    for (const n of nodes) types[n.type] = (types[n.type] || 0) + 1;
    const rels = {};
    for (const e of s.edges) rels[e.rel] = (rels[e.rel] || 0) + 1;
    const topLevel = nodes.filter(n => !n.parent).length;
    const uncertain = nodes.filter(n => n.confidence !== undefined && n.confidence < 0.5).length;
    const avgConf = nodes.filter(n => n.confidence !== undefined).length
      ? nodes.filter(n => n.confidence !== undefined).reduce((s, n) => s + n.confidence, 0) /
        nodes.filter(n => n.confidence !== undefined).length
      : null;
    return {
      entities: nodes.length,
      edges: s.edges.length,
      topLevel,
      maxDepth: s.meta.maxDepth,
      categories: Object.keys(s.categories).length,
      categoryNames: Object.keys(s.categories),
      types,
      relations: rels,
      uncertain,
      avgConfidence: avgConf !== null ? Math.round(avgConf * 100) / 100 : 'n/a',
      lastConsolidated: s.meta.lastConsolidated || null,
      storePath: storePath || DEFAULT_STORE
    };
  }

  /**
   * Get all nodes of a given type.
   * @param {string} type
   * @returns {Array}
   */
  function findByType(type) {
    return Object.values(store().nodes).filter(n => n.type === type);
  }

  /**
   * Get all nodes in a given category.
   * @param {string} category
   * @returns {Array}
   */
  function findByCategory(category) {
    const s = store();
    const ids = s.categories[category] || [];
    return ids.map(id => s.nodes[id]).filter(Boolean);
  }

  /**
   * Get edges for a node.
   * @param {string} nodeId
   * @returns {Array}
   */
  function getEdges(nodeId) {
    return store().edges.filter(e => e.from === nodeId || e.to === nodeId);
  }

  /**
   * Get direct children of a node.
   * @param {string} nodeId
   * @returns {Array}
   */
  function getChildren(nodeId) {
    return Object.values(store().nodes).filter(n => n.parent === nodeId);
  }

  /**
   * List all categories.
   * @returns {string[]}
   */
  function listCategories() {
    return Object.keys(store().categories);
  }

  return {
    search,
    getNode,
    traverse,
    stats,
    findByType,
    findByCategory,
    getEdges,
    getChildren,
    listCategories,
    reload
  };
}

// ── Convenience: default reader (singleton, cached) ──
let _defaultReader = null;
export function getDefaultReader() {
  if (!_defaultReader) _defaultReader = createReader();
  return _defaultReader;
}

// Named exports matching task spec
export const search = (q, opts) => getDefaultReader().search(q, opts);
export const getNode = (id) => getDefaultReader().getNode(id);
export const traverse = (id, opts) => getDefaultReader().traverse(id, opts);
export const stats = () => getDefaultReader().stats();
