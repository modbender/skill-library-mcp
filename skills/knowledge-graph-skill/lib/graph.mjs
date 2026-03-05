// graph.mjs — Core CRUD for knowledge graph nodes + edges

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STORE_PATH = join(__dirname, '..', 'data', 'kg-store.json');
const ACCESS_PATH = join(__dirname, '..', 'data', 'kg-access.json');

// ── Access Tracking ──
// Tracks how often entities are accessed (search, traverse, rels queries)
// Used by serialize.mjs to rank entities in summary by relevance

export function loadAccess() {
  if (!existsSync(ACCESS_PATH)) return {};
  try { return JSON.parse(readFileSync(ACCESS_PATH, 'utf8')); }
  catch { return {}; }
}

export function saveAccess(access) {
  writeFileSync(ACCESS_PATH, JSON.stringify(access) + '\n');
}

export function bumpAccess(entityIds) {
  const access = loadAccess();
  const now = Date.now();
  for (const id of entityIds) {
    if (!access[id]) access[id] = { count: 0, last: 0 };
    access[id].count++;
    access[id].last = now;
  }
  saveAccess(access);
}

// ── Valid Types & Relations ──
export const ENTITY_TYPES = [
  'human', 'ai', 'device', 'platform', 'project', 'decision', 'concept',
  'skill', 'network', 'credential', 'org', 'service',
  // life & world
  'place', 'event', 'media', 'product', 'account', 'routine', 'knowledge'
];

export const RELATION_TYPES = [
  'owns', 'uses', 'runs_on', 'runs', 'created', 'related_to', 'part_of',
  'instance_of', 'decided', 'depends_on', 'connected', 'manages',
  // life & social
  'likes', 'dislikes', 'located_in', 'knows', 'member_of', 'has'
];

const EMPTY_STORE = {
  version: 2,
  meta: { created: today(), lastConsolidated: null, entityCount: 0, edgeCount: 0, maxDepth: 0 },
  nodes: {},
  edges: [],
  categories: {}
};

function today() { return new Date().toISOString().slice(0, 10); }

export function load() {
  if (!existsSync(STORE_PATH)) return structuredClone(EMPTY_STORE);
  return JSON.parse(readFileSync(STORE_PATH, 'utf8'));
}

export function save(store) {
  // recalc meta
  const nodes = Object.values(store.nodes);
  store.meta.entityCount = nodes.length;
  store.meta.edgeCount = store.edges.length;
  store.meta.maxDepth = calcMaxDepth(store);
  writeFileSync(STORE_PATH, JSON.stringify(store, null, 2) + '\n');
}

function calcMaxDepth(store) {
  let max = 0;
  for (const n of Object.values(store.nodes)) {
    let d = 0, cur = n;
    while (cur.parent && store.nodes[cur.parent]) { d++; cur = store.nodes[cur.parent]; }
    if (d > max) max = d;
  }
  return max;
}

// ── Nodes ──

export function addNode(store, { id, alias, type, label, parent, category, tags, attrs, confidence }) {
  if (store.nodes[id]) throw new Error(`Node "${id}" already exists`);
  if (parent && !store.nodes[parent]) throw new Error(`Parent "${parent}" not found`);
  const resolvedType = type || 'concept';
  if (!ENTITY_TYPES.includes(resolvedType)) {
    console.warn(`⚠️  Unknown entity type "${resolvedType}" — known types: ${ENTITY_TYPES.join(', ')}`);
  }
  const node = {
    id, alias: alias || id.slice(0, 2).toUpperCase(),
    type: resolvedType, label: label || id,
    parent: parent || null,
    tags: tags || [], attrs: attrs || {},
    created: today(), updated: today()
  };
  // confidence: 0.0-1.0, default 0.8 (only store if explicitly set or non-default)
  const conf = parseFloat(confidence);
  if (!isNaN(conf)) node.confidence = Math.max(0, Math.min(1, conf));
  store.nodes[id] = node;
  if (category) {
    if (!store.categories[category]) store.categories[category] = [];
    if (!store.categories[category].includes(id)) store.categories[category].push(id);
  }
  return store.nodes[id];
}

export function updateNode(store, id, patch) {
  if (!store.nodes[id]) throw new Error(`Node "${id}" not found`);
  const n = store.nodes[id];
  for (const [k, v] of Object.entries(patch)) {
    if (k === 'id') continue; // immutable
    if (k === 'attrs') Object.assign(n.attrs, v);
    else if (k === 'tags') n.tags = [...new Set([...n.tags, ...v])];
    else n[k] = v;
  }
  n.updated = today();
  return n;
}

export function removeNode(store, id, cascade = true) {
  if (!store.nodes[id]) throw new Error(`Node "${id}" not found`);
  if (cascade) {
    // remove children recursively
    const children = Object.values(store.nodes).filter(n => n.parent === id);
    for (const c of children) removeNode(store, c.id, true);
  }
  // remove edges referencing this node
  store.edges = store.edges.filter(e => e.from !== id && e.to !== id);
  // remove from categories
  for (const cat of Object.values(store.categories)) {
    const idx = cat.indexOf(id);
    if (idx !== -1) cat.splice(idx, 1);
  }
  delete store.nodes[id];
}

export function getNode(store, id) { return store.nodes[id] || null; }

export function getChildren(store, id) {
  return Object.values(store.nodes).filter(n => n.parent === id);
}

export function getDescendants(store, id) {
  const result = [];
  const stack = [id];
  while (stack.length) {
    const cur = stack.pop();
    const children = Object.values(store.nodes).filter(n => n.parent === cur);
    for (const c of children) { result.push(c); stack.push(c.id); }
  }
  return result;
}

// ── Edges ──

export function addEdge(store, { from, to, rel, attrs }) {
  if (!store.nodes[from]) throw new Error(`Node "${from}" not found`);
  if (!store.nodes[to]) throw new Error(`Node "${to}" not found`);
  if (!RELATION_TYPES.includes(rel)) {
    console.warn(`⚠️  Unknown relation type "${rel}" — known types: ${RELATION_TYPES.join(', ')}`);
  }
  // dedupe
  const exists = store.edges.find(e => e.from === from && e.to === to && e.rel === rel);
  if (exists) return exists;
  const edge = { from, to, rel, attrs: attrs || {}, created: today() };
  store.edges.push(edge);
  return edge;
}

export function removeEdge(store, { from, to, rel }) {
  const before = store.edges.length;
  store.edges = store.edges.filter(e => !(e.from === from && e.to === to && (!rel || e.rel === rel)));
  return before - store.edges.length;
}

export function getEdges(store, nodeId) {
  return store.edges.filter(e => e.from === nodeId || e.to === nodeId);
}

// ── Merge ──

export function mergeNodes(store, targetId, sourceId, mode = 'absorb') {
  const target = store.nodes[targetId];
  const source = store.nodes[sourceId];
  if (!target || !source) throw new Error('Node not found');

  if (mode === 'nest') {
    // source becomes child of target
    source.parent = targetId;
    source.updated = today();
    return { mode: 'nest', target: targetId, source: sourceId };
  }

  // absorb: merge attrs+tags, re-point edges, delete source
  Object.assign(target.attrs, source.attrs);
  target.tags = [...new Set([...target.tags, ...source.tags])];
  target.updated = today();

  // re-point edges
  for (const e of store.edges) {
    if (e.from === sourceId) e.from = targetId;
    if (e.to === sourceId) e.to = targetId;
  }
  // re-parent children
  for (const n of Object.values(store.nodes)) {
    if (n.parent === sourceId) n.parent = targetId;
  }
  // dedupe edges after re-point
  const seen = new Set();
  store.edges = store.edges.filter(e => {
    const key = `${e.from}>${e.rel}>${e.to}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
  removeNode(store, sourceId, false);
  return { mode: 'absorb', target: targetId, absorbed: sourceId };
}
