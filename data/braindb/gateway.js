import express from 'express';
import { writeFileSync, readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { createCaptureRoute, warmPatternCache } from './auto-capture.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DATA_DIR = process.env.BRAINDB_DATA || join(__dirname, 'data');
const QUEUE_FILE = join(DATA_DIR, 'write-queue.json');
const EMBEDDINGS_FILE = join(DATA_DIR, 'embeddings.json');
const CONFIG_FILE = process.env.BRAINDB_CONFIG || join(__dirname, 'config.json');

// ─── Config Loading ──────────────────────────────────────
let CONFIG = {};
try {
  if (existsSync(CONFIG_FILE)) {
    CONFIG = JSON.parse(readFileSync(CONFIG_FILE, 'utf8'));
    console.log(`📋 Loaded config: architecture=${CONFIG.architecture || 'default'}`);
  }
} catch (e) { console.warn('Config load failed, using defaults:', e.message); }

const ARCHITECTURE = CONFIG.architecture || 'multi-vm';
const EMBEDDER_URL = CONFIG.embedder?.url || 'http://localhost:3334';

// ─── Shard Registry (config-driven) ─────────────────────
function buildShardRegistry(config) {
  const arch = config.architecture || 'multi-vm';
  const shardConfig = config.shards?.[arch];
  
  const SHARD_ROLES = {
    episodic: 'Events, conversations, outcomes',
    semantic: 'Concepts, relationships, ontology',
    procedural: 'Learned skills, workflows, patterns',
    association: 'Cross-shard links, motivation weights',
  };

  if (arch === 'single-node' && shardConfig?.neo4j) {
    // Single node: all shards point to same instance
    const url = new URL(shardConfig.neo4j.url);
    // Auth: env var > config file > default
    const neo4jUser = process.env.NEO4J_USER || 'neo4j';
    const neo4jPass = process.env.NEO4J_PASSWORD || '';
    const auth = shardConfig.neo4j.auth || (neo4jPass ? `${neo4jUser}:${neo4jPass}` : 'neo4j:neo4j');
    const shards = {};
    for (const [name, role] of Object.entries(SHARD_ROLES)) {
      shards[name] = { host: url.hostname, port: parseInt(url.port) || 7474, role, auth, singleNode: true };
    }
    return { shards, auth: 'Basic ' + Buffer.from(auth).toString('base64') };
  }
  
  if (shardConfig && typeof shardConfig === 'object' && !shardConfig.neo4j) {
    // Multi-shard (virtual or multi-vm): each shard has its own URL
    const shards = {};
    for (const [name, role] of Object.entries(SHARD_ROLES)) {
      const sc = shardConfig[name];
      if (sc?.url) {
        const url = new URL(sc.url);
        shards[name] = { 
          host: url.hostname, port: parseInt(url.port) || 7474, role,
          auth: sc.auth, vmid: sc.vmid, pveNode: sc.pveNode 
        };
      }
    }
    const firstAuth = Object.values(shardConfig).find(s => s?.auth)?.auth || 'neo4j:braindb2026';
    return { shards, auth: 'Basic ' + Buffer.from(firstAuth).toString('base64') };
  }

  // Default: single-node with localhost Neo4j
  const defaultAuth = 'neo4j:braindb';
  const defaultShards = {};
  for (const [name, role] of Object.entries(SHARD_ROLES)) {
    defaultShards[name] = { host: 'neo4j', port: 7474, role, singleNode: true };
  }
  return { shards: defaultShards, auth: 'Basic ' + Buffer.from(defaultAuth).toString('base64') };
}

const { shards: SHARDS, auth: NEO4J_AUTH } = buildShardRegistry(CONFIG);

// ─── Shard Health Tracking ───────────────────────────────
const shardHealth = {};
for (const name of Object.keys(SHARDS)) {
  shardHealth[name] = {
    status: 'unknown',    // online | offline | recovering
    lastSeen: null,
    lastError: null,
    failCount: 0,
    recoveryAt: null,
  };
}

// Write queue for offline shards
let writeQueue = [];
if (existsSync(QUEUE_FILE)) {
  try { writeQueue = JSON.parse(readFileSync(QUEUE_FILE, 'utf8')); } catch (e) {}
}

function saveQueue() {
  try { writeFileSync(QUEUE_FILE, JSON.stringify(writeQueue, null, 2)); } catch (e) {}
}

// ─── Core Motivations ────────────────────────────────────
let motivationWeights = {
  survive: 0.8, serve: 0.9, grow: 0.7, protect: 0.6, build: 0.85
};

// ─── Neo4j Query Helper (HA-aware) ──────────────────────
async function cypher(shard, statements, { timeout = 5000, allowOffline = false } = {}) {
  const { host, port } = SHARDS[shard];
  const health = shardHealth[shard];

  // If shard is known offline and we're not doing a health check, fail fast
  if (health.status === 'offline' && !allowOffline) {
    throw new Error(`Shard ${shard} is offline (last seen: ${health.lastSeen || 'never'})`);
  }

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);

  try {
    const res = await fetch(`http://${host}:${port}/db/neo4j/tx/commit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': NEO4J_AUTH },
      body: JSON.stringify({ statements: Array.isArray(statements) ? statements : [statements] }),
      signal: controller.signal,
    });
    clearTimeout(timer);

    const json = await res.json();
    if (json.errors?.length) throw new Error(JSON.stringify(json.errors));

    // Mark healthy
    health.status = 'online';
    health.lastSeen = new Date().toISOString();
    health.failCount = 0;
    health.lastError = null;

    return json.results;
  } catch (e) {
    clearTimeout(timer);
    health.failCount++;
    health.lastError = e.message;

    if (health.failCount >= 2) {
      health.status = 'offline';
      console.warn(`⚠️  Shard ${shard} marked OFFLINE after ${health.failCount} failures: ${e.message}`);
    }

    throw e;
  }
}

// ─── Health Check Loop ───────────────────────────────────
async function healthCheck() {
  for (const [name, shard] of Object.entries(SHARDS)) {
    try {
      await cypher(name, { statement: 'RETURN 1' }, { timeout: 3000, allowOffline: true });

      // If was offline and now recovered, drain queued writes
      if (shardHealth[name].status === 'online' && shardHealth[name].recoveryAt === null && writeQueue.length > 0) {
        shardHealth[name].recoveryAt = new Date().toISOString();
        console.log(`✅ Shard ${name} recovered! Draining ${writeQueue.filter(w => w.shard === name).length} queued writes...`);
        await drainQueue(name);
      }
    } catch (e) {
      // Already handled in cypher()
    }
  }
}

async function drainQueue(shard) {
  const pending = writeQueue.filter(w => w.shard === shard);
  const remaining = writeQueue.filter(w => w.shard !== shard);

  for (const item of pending) {
    try {
      await encode(item.payload, true); // true = skip re-queuing
      console.log(`  ✅ Drained: ${item.payload.event}`);
    } catch (e) {
      console.warn(`  ❌ Failed to drain: ${item.payload.event} — ${e.message}`);
      remaining.push(item); // re-queue
    }
  }

  writeQueue = remaining;
  saveQueue();
}

// Run health check every 30 seconds
setInterval(healthCheck, 30_000);
// Initial check
setTimeout(healthCheck, 2000);

// ─── Motivation Engine ───────────────────────────────────
function computeActivation(motivationDelta = {}) {
  let dot = 0, normSq = 0;
  for (const [key, w] of Object.entries(motivationWeights)) {
    const delta = motivationDelta[key] || 0;
    dot += delta * w;
    normSq += w * w;
  }
  const norm = Math.sqrt(normSq) || 1;
  const magnitude = Math.min(1.0, Math.abs(dot / norm));
  const signal = dot >= 0 ? 'reward' : 'threat';
  return { magnitude, signal };
}

// ─── Encode (Write Path — HA-aware) ─────────────────────
async function encode({ event, content, context = {}, shard = 'episodic', motivationDelta = {}, dedupThreshold = 0.90 }, skipQueue = false) {
  // ─── Input validation & normalization ───
  const VALID_SHARDS = new Set(['episodic', 'semantic', 'procedural', 'association']);
  if (!VALID_SHARDS.has(shard)) {
    const remap = { technical: 'semantic', functional: 'procedural', market: 'semantic',
      strategic: 'semantic', competitive: 'semantic', economic: 'semantic' };
    const oldShard = shard;
    shard = remap[shard] || 'semantic';
    console.warn(`⚠️ Invalid shard "${oldShard}" remapped to "${shard}"`);
  }
  if (!event) event = (content || 'unnamed memory').slice(0, 80);

  const { magnitude, signal } = computeActivation(motivationDelta);
  const strength = Math.max(0.1, magnitude);
  const id = `${shard.slice(0, 3)}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;

  // ─── Dedup check: reject if near-duplicate exists ───
  if (dedupThreshold > 0 && embeddingCache.length > 0) {
    try {
      const text = `${event}. ${content}`;
      const res = await fetch(`${EMBEDDER_URL}/embed`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ texts: [text] }),
      });
      const json = await res.json();
      if (json.ok && json.embeddings?.[0]) {
        const newEmb = json.embeddings[0];
        let maxSim = 0, dupId = null;
        for (const mem of embeddingCache) {
          if (!mem.embedding) continue;
          let dot = 0, nA = 0, nB = 0;
          for (let i = 0; i < newEmb.length; i++) {
            dot += newEmb[i] * mem.embedding[i];
            nA += newEmb[i] * newEmb[i];
            nB += mem.embedding[i] * mem.embedding[i];
          }
          const sim = dot / (Math.sqrt(nA) * Math.sqrt(nB) || 1);
          if (sim > maxSim) { maxSim = sim; dupId = mem.id; }
        }
        if (maxSim >= dedupThreshold) {
          console.log(`⚡ Dedup: rejected "${event.slice(0, 50)}" (sim=${maxSim.toFixed(3)} with ${dupId})`);
          return { id: null, strength, signal, shard, queued: false, deduplicated: true, duplicateOf: dupId, similarity: maxSim };
        }
      }
    } catch (e) { /* dedup check failure is non-fatal — proceed with encode */ }
  }

  try {
    // Write to target shard
    await cypher(shard, {
      statement: `
        CREATE (m:Memory:${shard.charAt(0).toUpperCase() + shard.slice(1)} {
          id: $id, trigger: $trigger, content: $content,
          context: $context, strength: $strength,
          encoding_strength: $strength, signal: $signal,
          formed: datetime($formed), last_activated: datetime(),
          activations: 1, type: $type
        }) RETURN m.id`,
      parameters: {
        id, trigger: event, content, context: JSON.stringify(context),
        strength, signal, type: shard,
        formed: context.when || new Date().toISOString(),
      }
    });

    // Form associations with recent memories on same shard
    try {
      await cypher(shard, {
        statement: `
          MATCH (m:Memory) WHERE m.id <> $id AND m.strength > 0.1
          AND m.last_activated > datetime() - duration('PT30M')
          WITH m ORDER BY m.strength DESC LIMIT 5
          MATCH (new:Memory {id: $id})
          CREATE (new)-[:ASSOCIATED_WITH {weight: $weight, co_activations: 1}]->(m)
          CREATE (m)-[:ASSOCIATED_WITH {weight: $weight, co_activations: 1}]->(new)`,
        parameters: { id, weight: (strength + 0.3) / 2 }
      });
    } catch (e) { /* association failure is non-fatal */ }

    // Cross-shard gossip
    try {
      await cypher('association', {
        statement: `
          MERGE (ref:ShardRef {id: $id, shard: $shard, type: $type})
          SET ref.trigger = $trigger, ref.strength = $strength,
              ref.signal = $signal, ref.last_seen = datetime()`,
        parameters: { id, shard, type: shard, trigger: event, strength, signal }
      });
    } catch (e) { /* gossip failure is non-fatal */ }

    // Auto-embed new memory
    addToEmbeddingCache(id, event, content, strength, shard, shard).catch(() => {});

    return { id, strength, signal, shard, queued: false };

  } catch (e) {
    // Shard is down — queue the write for later
    if (!skipQueue) {
      writeQueue.push({
        shard,
        queuedAt: new Date().toISOString(),
        payload: { event, content, context, shard, motivationDelta }
      });
      saveQueue();
      console.log(`📝 Queued write for offline shard ${shard}: ${event}`);
      return { id: null, strength, signal, shard, queued: true, queuedAt: new Date().toISOString() };
    }
    throw e;
  }
}

// ─── Embedding Cache ─────────────────────────────────────
let embeddingCache = [];
function loadEmbeddings() {
  try {
    if (existsSync(EMBEDDINGS_FILE)) {
      embeddingCache = JSON.parse(readFileSync(EMBEDDINGS_FILE, 'utf8'));
      console.log(`📦 Loaded ${embeddingCache.length} embeddings from cache`);
    }
  } catch (e) { console.warn('Failed to load embeddings:', e.message); }
}
loadEmbeddings();

function cosineSim(a, b) {
  let dot = 0, normA = 0, normB = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }
  const denom = Math.sqrt(normA) * Math.sqrt(normB);
  return denom > 0 ? dot / denom : 0;
}

// LRU cache for query embeddings (avoids re-embedding same queries)
const queryEmbCache = new Map();
const QUERY_CACHE_MAX = 200;

async function getQueryEmbedding(query) {
  if (queryEmbCache.has(query)) return queryEmbCache.get(query);
  const res = await fetch(`${EMBEDDER_URL}/embed`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ texts: [query] }),
  });
  const json = await res.json();
  if (!json.ok || !json.embeddings?.[0]) return null;
  const emb = json.embeddings[0];
  queryEmbCache.set(query, emb);
  // Evict oldest if over limit
  if (queryEmbCache.size > QUERY_CACHE_MAX) {
    queryEmbCache.delete(queryEmbCache.keys().next().value);
  }
  return emb;
}

// Query expansion: map colloquial phrases to domain terms
// ─── Action Intent Detection ─────────────────────────────
function detectActionIntent(query) {
  const lq = query.toLowerCase();
  const actionPatterns = [
    /\b(send|post|check|scan|run|build|create|deploy|fetch|search|schedule|set up|configure|install|update|restart|stop|start|delete|remove|monitor|automate|notify|alert)\b/,
    /\b(i need to|i want to|can you|please|let's|let me|go ahead and)\b/,
    /\b(what tool|which tool|what's the command|what script)\b/,
  ];
  return actionPatterns.some(p => p.test(lq));
}

function expandQueryLocal(query) {
  // Generic expansions — override/extend via config.json "queryExpansions"
  const defaults = {
    'make money': 'revenue income earnings profit client',
    'how much': 'amount total cost price revenue',
    'who am i': 'identity role name title background',
    'what am i': 'identity role name assistant agent',
    'who is': 'identity background role name profile',
    'my name': 'name identity who am called',
    'what happened': 'event milestone decision',
    'build next': 'product roadmap app idea project',
    'my tools': 'tools scripts commands CLI platform',
    'what tools': 'tools scripts commands CLI platform',
    'my computer': 'hardware computer machine server',
    'work on': 'product roadmap opportunity project next',
    'should we': 'product roadmap opportunity project next priority',
    'kids': 'children family school son daughter',
    'children': 'kids family school son daughter',
    'family': 'wife kids children spouse partner',
    'wife': 'spouse partner family',
    'personality': 'behavior communication style tone vibe soul',
    'how do i': 'workflow process steps guide instructions',
  };
  const custom = CONFIG.queryExpansions || {};
  const expansions = { ...defaults, ...custom };
  let expanded = query;
  const lq = query.toLowerCase();
  for (const [phrase, terms] of Object.entries(expansions)) {
    if (lq.includes(phrase)) expanded += ' ' + terms;
  }
  return expanded;
}

async function semanticRecall(query, maxResults = 10) {
  if (embeddingCache.length === 0) return [];

  try {
    // Expand vague queries with domain terms
    const expandedQuery = expandQueryLocal(query);
    const queryEmb = await getQueryEmbedding(expandedQuery);
    if (!queryEmb) {
      console.warn('Semantic recall: failed to embed query');
      return [];
    }

    // Compute similarity locally (fast: ~978 cosine sims in <5ms)
    const scored = [];
    for (const mem of embeddingCache) {
      if (!mem.embedding) continue;
      const sim = cosineSim(queryEmb, mem.embedding);
      if (sim > 0.25) {
        scored.push({
          id: mem.id,
          trigger: mem.trigger || '',
          content: mem.content || '',
          strength: mem.strength || 0,
          type: mem.type || '',
          source_shard: mem.shard || '',
          similarity: sim,
          activation_source: 'semantic',
        });
      }
    }

    // Term-coverage boost: memories containing more expansion terms rank higher
    const expansionTerms = expandedQuery.toLowerCase().split(/\s+/).filter(w => w.length > 2);
    if (expansionTerms.length > 3) {
      for (const mem of scored) {
        const memText = `${mem.trigger} ${mem.content}`.toLowerCase();
        const coverage = expansionTerms.filter(t => memText.includes(t)).length / expansionTerms.length;
        mem.similarity += coverage * 0.08;
      }
    }

    scored.sort((a, b) => b.similarity - a.similarity);
    return scored.slice(0, maxResults);
  } catch (e) {
    console.warn('Semantic recall failed, falling back to text:', e.message);
    return [];
  }
}

async function addToEmbeddingCache(id, trigger, content, strength, type, shard) {
  try {
    const text = `${trigger}. ${content}`;
    const res = await fetch(`${EMBEDDER_URL}/embed`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    const json = await res.json();
    if (json.ok && json.embeddings?.[0]) {
      embeddingCache.push({ id, trigger, content, strength, type, shard, embedding: json.embeddings[0] });
      writeFileSync(EMBEDDINGS_FILE, JSON.stringify(embeddingCache));
    }
  } catch (e) { /* non-fatal */ }
}

// ─── Recall (Read Path — HA-aware, semantic + graph) ────
async function recall({ query, context = {}, maxResults = 10, spreadDepth = 1, shards = null, executionAware = 'auto' }) {
  const targetShards = (shards || Object.keys(SHARDS).filter(s => s !== 'association'))
    .filter(s => shardHealth[s].status !== 'offline');

  const isActionQuery = executionAware === 'on' || 
    (executionAware === 'auto' && detectActionIntent(query));

  if (targetShards.length === 0) {
    return []; // All shards offline — return empty rather than error
  }

  // ═══ PHASE 1: Semantic search via embeddings (primary) ═══
  const semanticResults = await semanticRecall(query, maxResults);
  
  // Skip text search if semantic results are strong (top result > 0.6 and we have enough)
  if (semanticResults.length >= maxResults && semanticResults[0]?.similarity > 0.6) {
    // Fire-and-forget Hebbian on semantic results
    const byShard = {};
    for (const r of semanticResults) {
      if (r.source_shard) (byShard[r.source_shard] ??= []).push(r.id);
    }
    for (const [shard, ids] of Object.entries(byShard)) {
      cypher(shard, {
        statement: `UNWIND $ids AS id MATCH (m:Memory {id: id})
          SET m.strength = CASE WHEN m.strength * 1.05 > 1.0 THEN 1.0 ELSE m.strength * 1.05 END,
              m.last_activated = datetime(), m.activations = m.activations + 1`,
        parameters: { ids }
      }, { timeout: 3000 }).catch(() => {});
    }
    return semanticResults.slice(0, maxResults);
  }

  // ═══ PHASE 2: Graph text search (supplement — only when semantic is weak) ═══
  const words = query.split(/\s+/).filter(w => w.length > 2);
  const conditions = words.map((_, i) => `(m.trigger CONTAINS $w${i} OR m.content CONTAINS $w${i})`).join(' OR ');
  const params = Object.fromEntries(words.map((w, i) => [`w${i}`, w]));
  params.limit = maxResults;

  const allResults = [...semanticResults]; // Start with semantic results
  const seenIds = new Set(semanticResults.map(r => r.id));

  const queries = targetShards.map(async (shard) => {
    try {
      const results = await cypher(shard, {
        statement: `
          MATCH (m:Memory)
          WHERE m.strength > 0.05
          AND (${conditions || 'false'})
          WITH m,
            m.strength * (1.0 / (1.0 + duration.between(m.last_activated, datetime()).seconds / 3600.0)) AS relevance
          ORDER BY relevance DESC LIMIT $limit
          OPTIONAL MATCH (m)-[a:ASSOCIATED_WITH]->(spread:Memory)
          WHERE spread.strength > 0.1
          RETURN m.id, m.trigger, m.content, m.strength, m.signal, m.type,
                 relevance,
                 collect({id: spread.id, trigger: spread.trigger, weight: a.weight})[0..3] AS associations`,
        parameters: params,
      }, { timeout: 5000 });

      for (const row of results[0]?.data || []) {
        if (seenIds.has(row.row[0])) continue; // dedupe
        seenIds.add(row.row[0]);
        allResults.push({
          id: row.row[0], trigger: row.row[1], content: row.row[2],
          strength: row.row[3], signal: row.row[4], type: row.row[5],
          relevance: row.row[6], associations: row.row[7],
          source_shard: shard, activation_source: 'direct',
        });
      }
    } catch (e) {
      console.warn(`Recall from ${shard} failed: ${e.message}`);
    }
  });

  await Promise.all(queries);

  // Reactivate retrieved nodes (Hebbian reinforcement) — fire-and-forget, don't block recall
  // Batch by shard for efficiency
  const byShard = {};
  for (const r of allResults) {
    if (r.source_shard) byShard[r.source_shard] = byShard[r.source_shard] || [];
    if (r.source_shard) byShard[r.source_shard].push(r.id);
  }
  for (const [shard, ids] of Object.entries(byShard)) {
    cypher(shard, {
      statement: `UNWIND $ids AS id MATCH (m:Memory {id: id})
        SET m.strength = CASE WHEN m.strength * 1.05 > 1.0 THEN 1.0 ELSE m.strength * 1.05 END,
            m.last_activated = datetime(), m.activations = m.activations + 1`,
      parameters: { ids }
    }, { timeout: 3000 }).catch(() => {}); // non-blocking
  }

  // Sort: semantic similarity is primary signal, text match is supplementary
  // When action intent detected, procedural/execution memories get a boost
  allResults.sort((a, b) => {
    const simA = a.similarity || 0;
    const simB = b.similarity || 0;

    let execBoostA = 0, execBoostB = 0;
    if (isActionQuery) {
      if (a.source_shard === 'procedural') execBoostA += 0.1;
      if (b.source_shard === 'procedural') execBoostB += 0.1;
      const ctxA = typeof a.context === 'object' ? a.context : {};
      const ctxB = typeof b.context === 'object' ? b.context : {};
      if (ctxA.source === 'execution-awareness') execBoostA += 0.15;
      if (ctxB.source === 'execution-awareness') execBoostB += 0.15;
      if (ctxA.category === 'tool-catalog') execBoostA += 0.05;
      if (ctxB.category === 'tool-catalog') execBoostB += 0.05;
    }

    const effSimA = simA + execBoostA;
    const effSimB = simB + execBoostB;

    const tierA = effSimA > 0.4 ? 1 : 0;
    const tierB = effSimB > 0.4 ? 1 : 0;
    if (tierA !== tierB) return tierB - tierA;
    if (tierA === 1) {
      const scoreA = effSimA + (a.strength || 0) * 0.1;
      const scoreB = effSimB + (b.strength || 0) * 0.1;
      return scoreB - scoreA;
    }
    return (b.relevance || 0) - (a.relevance || 0);
  });

  if (isActionQuery) {
    for (const r of allResults) {
      if (r.source_shard === 'procedural' || 
          (typeof r.context === 'object' && r.context?.source === 'execution-awareness')) {
        r.executionRelevant = true;
      }
    }
  }

  return allResults.slice(0, maxResults);
}

// ─── Decay Sweep ─────────────────────────────────────────
async function runDecay() {
  const results = {};
  for (const shard of Object.keys(SHARDS).filter(s => s !== 'association')) {
    if (shardHealth[shard].status === 'offline') {
      results[shard] = { skipped: true, reason: 'offline' };
      continue;
    }
    try {
      const res = await cypher(shard, [
        {
          statement: `
            MATCH (m:Memory) WHERE m.strength > 0.01
            WITH m, m.strength * exp(-0.001 * duration.between(m.last_activated, datetime()).seconds / 3600.0 / CASE WHEN m.encoding_strength > 0 THEN m.encoding_strength ELSE 0.5 END) AS newStrength
            WHERE abs(newStrength - m.strength) > 0.001
            SET m.strength = CASE WHEN newStrength < 0.01 THEN 0 ELSE newStrength END
            RETURN count(m) AS decayed`
        },
        { statement: `MATCH (m:Memory) WHERE m.strength < 0.01 RETURN count(m) AS dead` }
      ]);
      results[shard] = {
        decayed: res[0]?.data?.[0]?.row?.[0] || 0,
        dead: res[1]?.data?.[0]?.row?.[0] || 0,
      };
    } catch (e) {
      results[shard] = { error: e.message };
    }
  }
  return results;
}

// ─── Stats (HA-aware) ────────────────────────────────────
async function getStats() {
  const stats = { shards: {}, total: { nodes: 0, relationships: 0 }, ha: {}, writeQueue: writeQueue.length };
  for (const [name, shard] of Object.entries(SHARDS)) {
    const health = shardHealth[name];
    if (health.status === 'offline') {
      stats.shards[name] = {
        host: shard.host, vmid: shard.vmid, pveNode: shard.pveNode,
        role: shard.role, status: 'offline',
        lastSeen: health.lastSeen, lastError: health.lastError,
      };
      continue;
    }
    try {
      const res = await cypher(name, [
        { statement: 'MATCH (m:Memory) WHERE m.strength > 0 RETURN count(m) AS memories' },
        { statement: 'MATCH ()-[r]->() RETURN count(r) AS relationships' },
        { statement: 'MATCH (m:Memory) WHERE m.strength > 0 RETURN avg(m.strength) AS avgStrength' },
      ], { timeout: 3000 });
      stats.shards[name] = {
        host: shard.host, vmid: shard.vmid, pveNode: shard.pveNode,
        role: shard.role, memories: res[0]?.data?.[0]?.row?.[0] || 0,
        relationships: res[1]?.data?.[0]?.row?.[0] || 0,
        avgStrength: res[2]?.data?.[0]?.row?.[0] || 0,
        status: 'online',
      };
      stats.total.nodes += stats.shards[name].memories;
      stats.total.relationships += stats.shards[name].relationships;
    } catch (e) {
      stats.shards[name] = { host: shard.host, status: 'error', error: e.message };
    }
  }
  stats.ha = {
    onlineShards: Object.values(stats.shards).filter(s => s.status === 'online').length,
    totalShards: Object.keys(SHARDS).length,
    writeQueueDepth: writeQueue.length,
    note: 'Proxmox HA manages VM restart/migration. Gateway handles shard unavailability with write queuing and automatic drain on recovery.',
  };
  stats.motivations = motivationWeights;
  return stats;
}

// ─── Express Server ──────────────────────────────────────
const app = express();
app.use(express.json({ limit: '1mb' }));

// ─── Optional API Key Authentication ─────────────────────
const API_KEY = process.env.BRAINDB_API_KEY;
if (API_KEY) {
  app.use((req, res, next) => {
    // Health check is always public (for Docker healthcheck + monitoring)
    if (req.path === '/health') return next();
    const auth = req.headers.authorization;
    if (auth === `Bearer ${API_KEY}`) return next();
    res.status(401).json({ ok: false, error: 'Unauthorized' });
  });
  console.log('🔐 API key authentication enabled');
}

app.get('/health', async (req, res) => {
  const stats = await getStats();
  const online = stats.ha.onlineShards;
  const total = stats.ha.totalShards;
  res.json({
    status: online === total ? 'healthy' : online > 0 ? 'degraded' : 'offline',
    version: '0.3.0-ha',
    uptime: process.uptime(),
    shards: `${online}/${total} online`,
    totalMemories: stats.total.nodes,
    totalRelationships: stats.total.relationships,
    writeQueue: stats.ha.writeQueueDepth,
    degradedShards: Object.entries(stats.shards)
      .filter(([_, s]) => s.status !== 'online')
      .map(([name, s]) => ({ name, status: s.status, lastSeen: s.lastSeen })),
  });
});

app.post('/memory/encode', async (req, res) => {
  try {
    const result = await encode(req.body);
    res.json({ ok: true, ...result });
  } catch (e) {
    res.status(400).json({ ok: false, error: e.message });
  }
});

app.post('/memory/recall', async (req, res) => {
  try {
    const { query, executionAware, ...rest } = req.body;
    const isAction = executionAware === 'on' || 
      (executionAware !== 'off' && detectActionIntent(query || ''));
    const results = await recall({ query, executionAware, ...rest });
    const online = Object.values(shardHealth).filter(s => s.status === 'online').length;
    const execResults = results.filter(r => r.executionRelevant).length;
    res.json({
      ok: true, count: results.length, results,
      shardsQueried: online,
      degraded: online < Object.keys(SHARDS).length,
      ...(isAction && { actionIntent: true, executionResults: execResults }),
    });
  } catch (e) {
    res.status(400).json({ ok: false, error: e.message });
  }
});

// ─── Execution Focus Recall ──────────────────────────────
// Returns tool/capability awareness memories relevant to the user's intent.
// Filters to execution-awareness memories and boosts procedural shard.
app.post('/memory/execution-focus', async (req, res) => {
  const start = Date.now();
  try {
    const { query, intent, limit = 5 } = req.body;
    if (!query && !intent) {
      return res.status(400).json({ ok: false, error: 'query or intent required' });
    }

    // Build an execution-oriented query
    const searchQuery = intent || query;
    const executionTerms = [
      searchQuery,
      `how to ${searchQuery}`,
      `tool for ${searchQuery}`,
      `${searchQuery} workflow pattern`,
    ].join('. ');

    // Recall with procedural bias
    const results = await recall({
      query: executionTerms,
      maxResults: limit * 3, // Over-fetch then filter
      shards: ['procedural'], // Only procedural shard
    });

    // Boost execution-awareness memories
    const scored = results.map(r => {
      let boost = 0;
      const ctx = r.context || {};
      if (ctx.source === 'execution-awareness') boost += 0.2;
      if (ctx.category === 'execution-pattern') boost += 0.15;
      if (ctx.category === 'tool-catalog') boost += 0.1;
      if (ctx.category === 'failure-memory') boost += 0.05;
      return { ...r, executionScore: (r.similarity || 0) + boost };
    });

    scored.sort((a, b) => b.executionScore - a.executionScore);
    const final = scored.slice(0, limit);

    res.json({
      ok: true,
      count: final.length,
      results: final,
      latency: Date.now() - start,
      mode: 'execution-focus',
    });
  } catch (e) {
    res.status(400).json({ ok: false, error: e.message, latency: Date.now() - start });
  }
});

// ─── Auto-Capture: Learn from tool executions ────────────
app.post('/memory/capture-execution', createCaptureRoute(encode, recall));

app.post('/memory/decay', async (req, res) => {
  try { res.json({ ok: true, ...(await runDecay()) }); }
  catch (e) { res.status(500).json({ ok: false, error: e.message }); }
});

app.get('/config', (req, res) => {
  res.json({
    ok: true,
    architecture: ARCHITECTURE,
    shards: Object.fromEntries(
      Object.entries(SHARDS).map(([k, v]) => [k, { host: v.host, port: v.port, role: v.role, singleNode: v.singleNode || false }])
    ),
    embedder: EMBEDDER_URL,
    recall: CONFIG.recall || { semanticThreshold: 0.4, fastPathThreshold: 0.6, dedupThreshold: 0.90 },
  });
});

app.get('/memory/stats', async (req, res) => {
  try { res.json({ ok: true, ...(await getStats()) }); }
  catch (e) { res.status(500).json({ ok: false, error: e.message }); }
});

app.get('/memory/motivations', (req, res) => {
  res.json({ ok: true, motivations: motivationWeights });
});

app.post('/memory/motivations', (req, res) => {
  for (const [name, weight] of Object.entries(req.body)) {
    if (motivationWeights[name] !== undefined) {
      motivationWeights[name] = Math.max(0.2, Math.min(1.0, weight));
    }
  }
  res.json({ ok: true, motivations: motivationWeights });
});

app.get('/memory/node/:id', async (req, res) => {
  for (const shard of Object.keys(SHARDS).filter(s => s !== 'association')) {
    if (shardHealth[shard].status === 'offline') continue;
    try {
      const results = await cypher(shard, {
        statement: `
          MATCH (m:Memory {id: $id})
          OPTIONAL MATCH (m)-[r]->(other)
          RETURN m, collect({type: type(r), target: other.id, weight: r.weight}) AS relationships`,
        parameters: { id: req.params.id }
      });
      if (results[0]?.data?.length) {
        return res.json({ ok: true, shard, node: results[0].data[0].row[0], relationships: results[0].data[0].row[1] });
      }
    } catch (e) { continue; }
  }
  res.status(404).json({ ok: false, error: 'not found' });
});

// Queue inspection
app.get('/memory/queue', (req, res) => {
  res.json({ ok: true, depth: writeQueue.length, items: writeQueue });
});

// Force drain
app.post('/memory/queue/drain', async (req, res) => {
  const shard = req.body?.shard;
  if (shard) {
    await drainQueue(shard);
  } else {
    for (const s of Object.keys(SHARDS)) {
      if (shardHealth[s].status === 'online') await drainQueue(s);
    }
  }
  res.json({ ok: true, remaining: writeQueue.length });
});

// Shard health overview
app.get('/memory/ha', (req, res) => {
  res.json({
    ok: true,
    shards: Object.entries(shardHealth).map(([name, h]) => ({
      name,
      ...SHARDS[name],
      ...h,
    })),
    writeQueue: writeQueue.length,
    proxmoxHA: 'All VMs (113-118) have HA enabled: max_restart=2, max_relocate=2. Proxmox handles VM-level recovery. Gateway handles service-level resilience.',
  });
});

// ─── Gemini-Enhanced Recall — 1 Router Per Shard ─────────
// 3 parallel Gemini Flash calls, each a specialist:
//   Episodic router: "What events/conversations relate?"
//   Semantic router: "What facts/concepts relate?"
//   Procedural router: "What skills/lessons relate?"
// Each judges only its shard's candidates. Runs in parallel = same latency as 1 call.
const GEMINI_KEY_FILE = process.env.GEMINI_KEY_FILE || join(process.env.HOME || '/root', '.config/clawdbot/gemini-key.txt');
let GEMINI_KEY = process.env.GEMINI_KEY || '';
if (!GEMINI_KEY) { try { GEMINI_KEY = readFileSync(GEMINI_KEY_FILE, 'utf8').trim(); } catch {} }

const SHARD_ROUTER_PROMPTS = {
  episodic: `You are the EPISODIC memory router — you specialize in events, conversations, and things that happened. Given the query, select memories that describe relevant events, interactions, decisions, or milestones. Include anything where "what happened" matters.`,
  semantic: `You are the SEMANTIC memory router — you specialize in facts, concepts, identity, and knowledge. Given the query, select memories that contain relevant facts, preferences, relationships, or conceptual knowledge. Think about what the person KNOWS, not just what happened.`,
  procedural: `You are the PROCEDURAL memory router — you specialize in skills, workflows, lessons learned, and how-to knowledge. Given the query, select memories about processes, rules, best practices, or things learned from experience. Think about what someone SHOULD DO.`,
};

async function geminiRoute(query, candidates, shardType, maxPick = 5) {
  if (candidates.length === 0) return [];
  
  const candidateList = candidates.map((c, i) =>
    `[${i}] ${c.trigger || ''}: ${(c.content || '').slice(0, 150)}`
  ).join('\n');

  const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${GEMINI_KEY}`;
  const res = await fetch(geminiUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      contents: [{ parts: [{ text: `${SHARD_ROUTER_PROMPTS[shardType]}

QUERY: "${query}"

CANDIDATES:
${candidateList}

Return JSON: {"selected": [0, 2, 4], "confidence": 0.85}
Rules:
- Select genuinely relevant memories (direct AND conceptual matches)
- Be inclusive — if it MIGHT help answer the query, include it
- Max ${maxPick} selected, ordered by relevance` }] }],
      generationConfig: { temperature: 0, maxOutputTokens: 150, responseMimeType: 'application/json' },
    }),
  });
  
  const json = await res.json();
  const text = json.candidates?.[0]?.content?.parts?.[0]?.text || '{}';
  const parsed = JSON.parse(text);
  
  return (parsed.selected || [])
    .filter(i => i >= 0 && i < candidates.length)
    .map(i => ({ ...candidates[i], gemini_selected: true, router: shardType, confidence: parsed.confidence }));
}

// ─── Phase 0: Query Expansion (with LRU cache) ──────────
const EXPANSION_CACHE_FILE = join(__dirname, '..', 'data', 'expansion-cache.json');
const EXPANSION_CACHE_MAX = 500;
let expansionCache = new Map(); // normalized query → { queries, hits, lastHit }

function loadExpansionCache() {
  try {
    if (existsSync(EXPANSION_CACHE_FILE)) {
      const entries = JSON.parse(readFileSync(EXPANSION_CACHE_FILE, 'utf8'));
      expansionCache = new Map(entries);
      console.log(`📦 Loaded ${expansionCache.size} expansion cache entries`);
    }
  } catch (e) {}
}
loadExpansionCache();

function saveExpansionCache() {
  try {
    // LRU eviction — keep most recently hit entries
    const entries = [...expansionCache.entries()]
      .sort((a, b) => (b[1].lastHit || 0) - (a[1].lastHit || 0))
      .slice(0, EXPANSION_CACHE_MAX);
    writeFileSync(EXPANSION_CACHE_FILE, JSON.stringify(entries));
  } catch (e) {}
}

function normalizeQuery(q) {
  return q.toLowerCase()
    .replace(/[^\w\s]/g, '')
    .replace(/\s+/g, ' ')
    .replace(/(\w)s\b/g, '$1') // strip trailing s (possessives + plurals)
    .trim();
}

// Fuzzy cache lookup — exact match first, then check if any cached key is a substring or vice versa
function cacheGet(query) {
  const norm = normalizeQuery(query);
  
  // Exact match
  if (expansionCache.has(norm)) {
    const entry = expansionCache.get(norm);
    entry.hits = (entry.hits || 0) + 1;
    entry.lastHit = Date.now();
    return entry.queries;
  }
  
  // Fuzzy: check if query words are a superset/subset of a cached key
  const qWords = new Set(norm.split(' ').filter(w => w.length > 2));
  for (const [key, entry] of expansionCache) {
    const kWords = new Set(key.split(' ').filter(w => w.length > 2));
    // If 80%+ of query words appear in cached key (or vice versa), it's a hit
    const overlap = [...qWords].filter(w => kWords.has(w)).length;
    const similarity = overlap / Math.max(qWords.size, kWords.size);
    if (similarity >= 0.6) {
      entry.hits = (entry.hits || 0) + 1;
      entry.lastHit = Date.now();
      return entry.queries;
    }
  }
  
  return null;
}

async function expandQuery(query) {
  if (!GEMINI_KEY) return [query];
  
  // Check cache first
  const cached = cacheGet(query);
  if (cached) return cached;
  
  const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${GEMINI_KEY}`;
  try {
    const res = await fetch(geminiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: [{ text: `Given this query about a person's life/work, generate 2-3 alternative search queries that would find relevant memories. Think about synonyms, related concepts, and indirect connections.

QUERY: "${query}"

Return JSON: {"queries": ["original query", "alternative 1", "alternative 2"]}
Rules:
- First query should be the original (possibly cleaned up)
- Alternatives should capture different angles (e.g., if asking about "UI preference", also search "component library", "DaisyUI", "shadcn")
- Keep queries short and specific
- Think about what TERMS the memories might actually contain` }] }],
        generationConfig: { temperature: 0, maxOutputTokens: 150, responseMimeType: 'application/json' },
      }),
    });
    const json = await res.json();
    const text = json.candidates?.[0]?.content?.parts?.[0]?.text || '{}';
    const parsed = JSON.parse(text);
    const queries = parsed.queries || [query];
    
    // Cache it
    const norm = normalizeQuery(query);
    expansionCache.set(norm, { queries, hits: 0, lastHit: Date.now(), created: Date.now() });
    saveExpansionCache();
    
    return queries;
  } catch (e) {
    console.warn('Query expansion failed, using original:', e.message);
    return [query];
  }
}

// ─── Phase 4: Cross-Shard Synthesis ──────────────────────
async function synthesize(query, routerResults, maxResults = 10) {
  if (!GEMINI_KEY) return routerResults;
  
  // Flatten all router-selected memories
  const allSelected = routerResults.flat();
  if (allSelected.length <= maxResults) return allSelected; // nothing to filter
  
  const candidateList = allSelected.map((c, i) =>
    `[${i}] (${c.router || c.type}) ${c.trigger || ''}: ${(c.content || '').slice(0, 200)}`
  ).join('\n');

  const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${GEMINI_KEY}`;
  try {
    const res = await fetch(geminiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: [{ text: `You are the SYNTHESIS router — you see memories from ALL shards (episodic events, semantic facts, procedural skills) and must select the MOST relevant combination to answer the query. Look for cross-shard connections that individual routers might miss.

QUERY: "${query}"

ALL SELECTED MEMORIES (from 3 specialist routers):
${candidateList}

Return JSON: {"selected": [0, 2, 4, 7], "reasoning": "brief explanation of cross-shard connections found"}
Rules:
- Rank by combined relevance to the query
- Prioritize memories that CONNECT across types (e.g., an event that relates to a fact that explains a skill)
- Keep up to ${maxResults} memories
- Be INCLUSIVE — when in doubt, keep it` }] }],
        generationConfig: { temperature: 0, maxOutputTokens: 200, responseMimeType: 'application/json' },
      }),
    });
    const json = await res.json();
    const text = json.candidates?.[0]?.content?.parts?.[0]?.text || '{}';
    const parsed = JSON.parse(text);
    
    const selected = (parsed.selected || [])
      .filter(i => i >= 0 && i < allSelected.length)
      .map(i => ({ ...allSelected[i], synthesis_selected: true, synthesis_reasoning: parsed.reasoning }));
    
    return selected.length > 0 ? selected : allSelected.slice(0, maxResults);
  } catch (e) {
    console.warn('Synthesis failed, using router results:', e.message);
    return allSelected.slice(0, maxResults);
  }
}

// ─── Smart Recall Core (used by both live + speculative) ─
async function smartRecallCore({ query, context = {}, maxResults = 10 }) {
  const start = Date.now();
  const phases = {};
  
  // ═══ PHASE 0+1 PARALLEL: Expansion + Embeddings fire simultaneously ═══
  const cacheHit = cacheGet(query) !== null;
  const allCandidates = new Map();
  
  // Fire BOTH at the same time
  const [expandedQueries, baseResults] = await Promise.all([
    expandQuery(query),                    // Gemini call OR cache hit
    semanticRecall(query, 20),             // Embeddings on original query (always instant)
  ]);
  
  // Collect base results immediately
  for (const r of baseResults) {
    allCandidates.set(r.id, r);
  }
  
  phases.expansion = { ms: Date.now() - start, queries: expandedQueries, cached: cacheHit };
  
  // Now run expanded queries (skip the original since we already searched it)
  const extraQueries = expandedQueries.filter(q => normalizeQuery(q) !== normalizeQuery(query));
  if (extraQueries.length > 0) {
    const extraResults = await Promise.all(extraQueries.map(q => semanticRecall(q, 15)));
    for (const results of extraResults) {
      for (const r of results) {
        if (!allCandidates.has(r.id) || r.similarity > allCandidates.get(r.id).similarity) {
          allCandidates.set(r.id, r);
        }
      }
    }
  }
  
  const allSemantic = [...allCandidates.values()]
    .sort((a, b) => (b.similarity || 0) - (a.similarity || 0))
    .slice(0, 30);
  
  const p1End = Date.now();
  phases.embedding = { ms: p1End - start, candidates: allSemantic.length, queries_run: expandedQueries.length, parallel: true };
  
  if (!GEMINI_KEY || allSemantic.length === 0) {
    return { results: allSemantic.slice(0, maxResults), method: 'embed-only', phases, total_ms: Date.now() - start };
  }
  
  // Split candidates by shard/type
  const byType = { episodic: [], semantic: [], procedural: [] };
  for (const mem of allSemantic) {
    const t = mem.type || mem.shard || 'semantic';
    if (byType[t]) byType[t].push(mem);
    else byType.semantic.push(mem);
  }
  
  // ═══ PHASE 2: Fire 3 shard routers IN PARALLEL (3 Gemini calls) ═══
  const p2Start = Date.now();
  const routerResults = await Promise.all([
    geminiRoute(query, byType.episodic, 'episodic', 7).catch(() => []),
    geminiRoute(query, byType.semantic, 'semantic', 7).catch(() => []),
    geminiRoute(query, byType.procedural, 'procedural', 7).catch(() => []),
  ]);
  
  phases.routers = {
    ms: Date.now() - p2Start,
    episodic: { candidates: byType.episodic.length, selected: routerResults[0].length },
    semantic: { candidates: byType.semantic.length, selected: routerResults[1].length },
    procedural: { candidates: byType.procedural.length, selected: routerResults[2].length },
  };
  
  // ═══ PHASE 3: Cross-Shard Synthesis (1 Gemini call) ═══
  const p3Start = Date.now();
  const totalSelected = routerResults.flat().length;
  let finalResults;
  
  if (totalSelected > maxResults) {
    // Only synthesize if we have more than we need
    finalResults = await synthesize(query, routerResults, maxResults);
    phases.synthesis = { ms: Date.now() - p3Start, input: totalSelected, output: finalResults.length, active: true };
  } else {
    // Merge and dedupe directly
    const merged = routerResults.flat();
    const seen = new Set();
    finalResults = merged.filter(r => { if (seen.has(r.id)) return false; seen.add(r.id); return true; });
    phases.synthesis = { ms: 0, input: totalSelected, output: finalResults.length, active: false, reason: 'under maxResults' };
  }
  
  // If routers returned nothing, fall back to top embedding results
  if (finalResults.length === 0) {
    finalResults = allSemantic.slice(0, maxResults);
    phases.fallback = true;
  }
  
  // Hebbian reinforcement (async, non-blocking)
  for (const r of finalResults) {
    const shard = r.source_shard || r.shard || r.type;
    if (!shard || !SHARDS[shard]) continue;
    cypher(shard, {
      statement: `MATCH (m:Memory {id: $id}) SET m.strength = CASE WHEN m.strength * 1.05 > 1.0 THEN 1.0 ELSE m.strength * 1.05 END, m.last_activated = datetime(), m.activations = m.activations + 1`,
      parameters: { id: r.id }
    }, { timeout: 3000 }).catch(() => {});
  }
  
  const gemini_calls = (cacheHit ? 0 : 1) + 3 + (phases.synthesis.active ? 1 : 0);
  
  // Track for predictive warming (async, non-blocking)
  trackQuery(query);
  
  return {
    results: finalResults,
    method: 'smart-recall-v2',
    gemini_calls,
    phases,
    total_ms: Date.now() - start,
    candidates_screened: allSemantic.length,
  };
}

// ─── Smart Recall Entry Point (checks speculative cache) ─
async function smartRecall({ query, context = {}, maxResults = 10 }) {
  const start = Date.now();
  
  // Check speculative recall cache first (semantic matching)
  const cached = await recallCacheGet(query);
  if (cached) {
    // Track for further predictions even on cache hit
    trackQuery(query);
    return {
      results: cached.results,
      method: 'speculative-cache-hit',
      total_ms: Date.now() - start,
      cache_hits: cached.hits,
      cache_age_ms: Date.now() - cached.timestamp,
      gemini_calls: 0,
      phases: { speculative: { hit: true, age_ms: Date.now() - cached.timestamp } },
    };
  }
  
  // Cache miss — run full pipeline
  const result = await smartRecallCore({ query, context, maxResults });
  
  // Cache the result for future speculative hits
  recallCacheSet(query, result.results, 'live');
  
  return result;
}

app.post('/memory/smart-recall', async (req, res) => {
  try {
    const result = await smartRecall(req.body);
    res.json({ ok: true, count: result.results.length, ...result });
  } catch (e) {
    res.status(400).json({ ok: false, error: e.message });
  }
});

// ─── Expansion Cache Endpoints ───────────────────────────
app.get('/memory/cache', (req, res) => {
  const entries = [...expansionCache.entries()].map(([key, val]) => ({
    query: key, ...val
  })).sort((a, b) => (b.hits || 0) - (a.hits || 0));
  res.json({ ok: true, size: expansionCache.size, max: EXPANSION_CACHE_MAX, entries });
});

app.post('/memory/cache/warm', async (req, res) => {
  // Pre-warm cache with a list of queries
  const queries = req.body?.queries || [];
  let warmed = 0;
  for (const q of queries) {
    const norm = normalizeQuery(q);
    if (!expansionCache.has(norm)) {
      await expandQuery(q);
      warmed++;
    }
  }
  res.json({ ok: true, warmed, total: expansionCache.size });
});

app.delete('/memory/cache', (req, res) => {
  expansionCache.clear();
  saveExpansionCache();
  res.json({ ok: true, cleared: true });
});

// ─── Predictive Cache Warmer (Conversation-Aware) ────────
// Watches recent queries, predicts what you'll ask next, pre-warms expansions
const recentQueries = []; // sliding window of last N queries
const RECENT_WINDOW = 10;
const PREDICT_INTERVAL = null; // set by startPredictor()
let predictorRunning = false;

async function predictAndWarm(recentContext) {
  if (!GEMINI_KEY || recentContext.length === 0) return [];
  
  const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${GEMINI_KEY}`;
  try {
    const res = await fetch(geminiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: [{ text: `You observe queries into a PERSONAL memory system — it stores facts about a specific person's life, preferences, decisions, relationships, and work. NOT general knowledge.

Based on recent queries, predict 8-12 follow-up questions someone would ask about this PERSON'S specific data. Focus on:
- Their PREFERENCES and opinions (what they like/hate/chose)
- Their RELATIONSHIPS (family, coworkers, clients)  
- Their DECISIONS and rules (how they do things, what they decided)
- Their BUSINESS specifics (revenue, clients, products, stack choices)
- Their PERSONAL details (schedule, location, career milestones)

RECENT QUERIES (newest first):
${recentContext.map((q, i) => `${i+1}. ${q}`).join('\n')}

Return JSON: {"predictions": ["question 1", "question 2", ...]}
Rules:
- Every question should ask about THIS PERSON's specific data, not general knowledge
- Use their name/business name if known from queries
- Predict both direct follow-ups AND related personal topics
- Think: "What else would someone want to know about THIS person?"
- Cast a wide net — 8-12 predictions, mix of specific and exploratory` }] }],
        generationConfig: { temperature: 0.3, maxOutputTokens: 400, responseMimeType: 'application/json' },
      }),
    });
    const json = await res.json();
    const text = json.candidates?.[0]?.content?.parts?.[0]?.text || '{}';
    const parsed = JSON.parse(text);
    return parsed.predictions || [];
  } catch (e) {
    console.warn('Prediction failed:', e.message);
    return [];
  }
}

async function warmPredictions() {
  if (recentQueries.length < 2) return; // need context
  
  const predictions = await predictAndWarm(recentQueries);
  let warmed = 0;
  
  for (const q of predictions) {
    const norm = normalizeQuery(q);
    if (!expansionCache.has(norm)) {
      await expandQuery(q); // this caches automatically
      warmed++;
    }
  }
  
  if (warmed > 0) {
    console.log(`🔮 Predictive warmer: ${warmed} new expansions cached from ${predictions.length} predictions`);
  }
}

// ─── Speculative Recall Cache ────────────────────────────
// Full recall results cached — not just expansions, but the actual memories
const RECALL_CACHE_MAX = 100;
const RECALL_CACHE_TTL = 300_000; // 5 min — memories don't change fast
const recallCache = new Map(); // normalized query → { results, timestamp, hits }

async function recallCacheGet(query) {
  const norm = normalizeQuery(query);
  
  // Exact match
  if (recallCache.has(norm)) {
    const entry = recallCache.get(norm);
    if (Date.now() - entry.timestamp < RECALL_CACHE_TTL) {
      entry.hits++;
      return entry;
    }
    recallCache.delete(norm); // expired
  }
  
  // Semantic match via embedder — embed query, compare to cached query embeddings
  if (recallCache.size > 0) {
    try {
      const cachedEntries = [...recallCache.entries()]
        .filter(([_, e]) => Date.now() - e.timestamp < RECALL_CACHE_TTL);
      
      if (cachedEntries.length > 0) {
        // Embed the incoming query
        const qRes = await fetch(`${EMBEDDER_URL}/embed`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: query }),
        });
        const qJson = await qRes.json();
        if (qJson.ok && qJson.embeddings?.[0]) {
          const qEmb = qJson.embeddings[0];
          
          // Embed cached keys that don't have embeddings yet
          let bestSim = 0, bestKey = null;
          for (const [key, entry] of cachedEntries) {
            if (!entry.embedding) {
              const kRes = await fetch(`${EMBEDDER_URL}/embed`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: key }),
              });
              const kJson = await kRes.json();
              if (kJson.ok && kJson.embeddings?.[0]) entry.embedding = kJson.embeddings[0];
            }
            if (entry.embedding) {
              // Cosine similarity
              let dot = 0, nA = 0, nB = 0;
              for (let i = 0; i < qEmb.length; i++) {
                dot += qEmb[i] * entry.embedding[i];
                nA += qEmb[i] * qEmb[i];
                nB += entry.embedding[i] * entry.embedding[i];
              }
              const sim = dot / (Math.sqrt(nA) * Math.sqrt(nB));
              if (sim > bestSim) { bestSim = sim; bestKey = key; }
            }
          }
          
          if (bestSim > 0.75 && bestKey) {
            const entry = recallCache.get(bestKey);
            if (entry) {
              entry.hits++;
              console.log(`🎯 Semantic cache hit: "${query.slice(0,40)}" → "${bestKey.slice(0,40)}" (sim: ${bestSim.toFixed(3)})`);
              return entry;
            }
          }
        }
      }
    } catch (e) {
      // Fall back to word overlap if embedder fails
    }
  }
  
  // Fallback: word overlap
  const qWords = new Set(norm.split(' ').filter(w => w.length > 2));
  for (const [key, entry] of recallCache) {
    if (Date.now() - entry.timestamp >= RECALL_CACHE_TTL) continue;
    const kWords = new Set(key.split(' ').filter(w => w.length > 2));
    const overlap = [...qWords].filter(w => kWords.has(w)).length;
    const similarity = overlap / Math.max(qWords.size, kWords.size);
    if (similarity >= 0.6) {
      entry.hits++;
      return entry;
    }
  }
  return null;
}

function recallCacheSet(query, results, method) {
  const norm = normalizeQuery(query);
  recallCache.set(norm, { results, method, timestamp: Date.now(), hits: 0 });
  // LRU eviction
  if (recallCache.size > RECALL_CACHE_MAX) {
    const oldest = [...recallCache.entries()].sort((a, b) => a[1].timestamp - b[1].timestamp)[0];
    recallCache.delete(oldest[0]);
  }
}

// Track queries and trigger speculative recall after every 3rd new query
let queriesSinceLastPredict = 0;
function trackQuery(query) {
  recentQueries.unshift(query);
  if (recentQueries.length > RECENT_WINDOW) recentQueries.pop();
  
  queriesSinceLastPredict++;
  if (queriesSinceLastPredict >= 2 || recentQueries.length <= 2) {
    queriesSinceLastPredict = 0;
    // Fire FULL speculative recall pipeline async
    speculativeRecall().catch(e => console.warn('Speculative recall error:', e.message));
  }
}

async function speculativeRecall() {
  if (recentQueries.length < 1) return;
  
  const predictions = await predictAndWarm(recentQueries);
  let warmed = 0, skipped = 0;
  
  // Phase 1: Warm ALL expansion caches first (cheap, parallel)
  await Promise.all(predictions.map(q => expandQuery(q).catch(() => {})));
  
  // Phase 2: Run full recalls in parallel (up to 4 at a time to not hammer Gemini)
  const BATCH = 4;
  for (let i = 0; i < predictions.length; i += BATCH) {
    const batch = predictions.slice(i, i + BATCH);
    await Promise.all(batch.map(async (q) => {
      if (recallCacheGet(q)) { skipped++; return; }
      try {
        const result = await smartRecallCore({ query: q, maxResults: 10 });
        recallCacheSet(q, result.results, 'speculative');
        warmed++;
      } catch (e) { /* non-fatal */ }
    }));
  }
  
  if (warmed > 0) {
    console.log(`🔮 Speculative recall: ${warmed} full recalls pre-computed, ${skipped} already cached (${recallCache.size} total)`);
  }
}

app.get('/memory/cache/recalls', (req, res) => {
  const entries = [...recallCache.entries()].map(([key, val]) => ({
    query: key, hits: val.hits, method: val.method,
    age_ms: Date.now() - val.timestamp,
    memories: val.results?.length || 0,
  })).sort((a, b) => b.hits - a.hits);
  res.json({ ok: true, size: recallCache.size, max: RECALL_CACHE_MAX, ttl_ms: RECALL_CACHE_TTL, entries });
});

app.get('/memory/cache/predictions', async (req, res) => {
  const predictions = await predictAndWarm(recentQueries);
  res.json({ ok: true, recentQueries, predictions });
});

app.post('/memory/cache/predict', async (req, res) => {
  // Force a prediction cycle now
  const before = expansionCache.size;
  await warmPredictions();
  res.json({ ok: true, newEntries: expansionCache.size - before, cacheSize: expansionCache.size });
});

// ═══ AUTO-ENCODE: Conversation turn → distilled memories ═══════════════════
app.post('/memory/auto-encode', async (req, res) => {
  const start = Date.now();
  const { userMessage, agentResponse, sessionKey, topic } = req.body;
  
  if (!userMessage && !agentResponse) {
    return res.status(400).json({ ok: false, error: 'Need userMessage or agentResponse' });
  }
  
  if (!GEMINI_KEY) {
    return res.status(500).json({ ok: false, error: 'No Gemini API key configured' });
  }

  try {
    // Step 1: Run Encoding Router — distill conversation into memories
    const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${GEMINI_KEY}`;
    
    // Get recent memories for dedup context
    const recentMemories = [];
    for (const shard of ['semantic', 'procedural', 'episodic']) {
      try {
        const result = await cypher(shard, {
          statement: `MATCH (m:Memory) WHERE m.last_activated > datetime() - duration('PT2H')
            RETURN m.id AS id, m.trigger AS trigger, m.content AS content, m.type AS type
            ORDER BY m.last_activated DESC LIMIT 10`,
          parameters: {}
        });
        if (result?.results?.[0]?.data) {
          recentMemories.push(...result.results[0].data.map(r => ({
            id: r.row[0], trigger: r.row[1], content: r.row[2], type: r.row[3]
          })));
        }
      } catch {}
    }

    const recentList = recentMemories.slice(0, 15).map(m =>
      `- [${m.type}] ${m.trigger}: ${(m.content || '').slice(0, 100)}`
    ).join('\n');

    const routerPrompt = `You are a memory encoding router for an AI agent's persistent memory system.

Given a conversation turn, decide what lasting memories should be stored. Focus on PERSONAL, USER-SPECIFIC data that an LLM wouldn't know from training:
- Decisions made, preferences stated
- Business facts (revenue, clients, pricing, stack choices)
- Personal details (family, schedule, rules, pet peeves)
- Project milestones and status changes
- Lessons learned, mistakes made
- Rules and constraints ("never do X", "always use Y")
- Relationships between people, projects, tools

User said: "${(userMessage || '').slice(0, 1000)}"
Agent said: "${(agentResponse || '').slice(0, 1500)}"
${topic ? `Topic: ${topic}` : ''}

Recent memories already stored (DO NOT duplicate these):
${recentList || '(none)'}

Output JSON:
{
  "worth_remembering": true,
  "memories": [
    {
      "shard": "semantic",
      "trigger": "concise trigger phrase for retrieval",
      "content": "distilled fact (not raw conversation text)",
      "motivation_delta": {"survive": 0, "serve": 0.5, "grow": 0.3, "protect": 0, "build": 0.4}
    }
  ],
  "skip_reason": null
}

Rules:
- Only store things worth remembering long-term
- Skip greetings, routine status checks, "yes/no" responses, tool outputs
- Distill into clean memory text — facts, not quotes
- shard choices: "semantic" (facts/prefs/identity), "procedural" (rules/workflows/lessons), "episodic" (events/milestones/decisions)
- motivation_delta values 0-1: survive (self-preservation), serve (helping user), grow (learning), protect (security), build (creating)
- Output 0-5 memories per turn (usually 0-1)
- If not worth remembering, set worth_remembering=false and explain in skip_reason`;

    const routerRes = await fetch(geminiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: [{ text: routerPrompt }] }],
        generationConfig: { temperature: 0, maxOutputTokens: 600, responseMimeType: 'application/json' },
      }),
    });
    
    const routerJson = await routerRes.json();
    const routerText = routerJson.candidates?.[0]?.content?.parts?.[0]?.text || '{}';
    let parsed;
    try {
      parsed = JSON.parse(routerText);
    } catch {
      const match = routerText.match(/\{[\s\S]*\}/);
      parsed = match ? JSON.parse(match[0]) : { worth_remembering: false, memories: [], skip_reason: 'Parse failed' };
    }

    if (!parsed.worth_remembering || !parsed.memories?.length) {
      return res.json({
        ok: true, encoded: 0, skipped: true,
        skip_reason: parsed.skip_reason || 'Nothing worth remembering',
        latency: Date.now() - start,
      });
    }

    // Step 2: Dedup each proposed memory against existing embeddings
    const encoded = [];
    const duplicates = [];
    
    for (const mem of parsed.memories) {
      // Check semantic similarity against existing memories
      const dedupText = `${mem.trigger} ${mem.content}`;
      let isDuplicate = false;
      
      try {
        const simRes = await fetch(`${EMBEDDER_URL}/batch_similarity`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: dedupText, candidates: recentMemories.map(m => `${m.trigger} ${m.content}`).slice(0, 30) }),
        });
        const simData = await simRes.json();
        if (simData.similarities) {
          const maxSim = Math.max(...simData.similarities);
          if (maxSim > 0.85) {
            isDuplicate = true;
            duplicates.push({ trigger: mem.trigger, similarity: maxSim });
          }
        }
      } catch {} // Embedder down = skip dedup, encode anyway

      if (!isDuplicate) {
        try {
          const result = await encode({
            event: mem.trigger,
            content: mem.content,
            context: { source: 'auto-encode', sessionKey, topic, when: new Date().toISOString() },
            shard: mem.shard || 'semantic',
            motivationDelta: mem.motivation_delta || {},
          });
          encoded.push({ id: result.id, shard: result.shard, trigger: mem.trigger });
        } catch (e) {
          console.warn(`Auto-encode failed for "${mem.trigger}":`, e.message);
        }
      }
    }

    res.json({
      ok: true,
      encoded: encoded.length,
      duplicates: duplicates.length,
      memories: encoded,
      duplicateDetails: duplicates,
      latency: Date.now() - start,
    });

  } catch (e) {
    console.error('Auto-encode error:', e);
    res.status(500).json({ ok: false, error: e.message, latency: Date.now() - start });
  }
});

// ─── Session Context — Compaction-Proof Conversational Memory ─────────
const SESSION_CONTEXT_PREFIX = 'session-ctx::';

app.post('/memory/session-context', async (req, res) => {
  const start = Date.now();
  const { sessionKey, topic, activeTask, lastUserMessage, lastAgentAction, pendingQuestions, decisions, summary } = req.body;
  if (!sessionKey) return res.status(400).json({ ok: false, error: 'sessionKey required' });

  const contextId = `${SESSION_CONTEXT_PREFIX}${sessionKey}`;
  const content = [
    summary && `Summary: ${summary}`,
    topic && `Topic: ${topic}`,
    activeTask && `Active task: ${activeTask}`,
    lastUserMessage && `Last user said: ${lastUserMessage}`,
    lastAgentAction && `Agent was doing: ${lastAgentAction}`,
    pendingQuestions && `Pending: ${pendingQuestions}`,
    decisions && `Decisions: ${decisions}`,
  ].filter(Boolean).join('\n');
  if (!content) return res.status(400).json({ ok: false, error: 'No context fields provided' });

  try {
    // Delete previous session context (overwrite)
    for (const shardName of ['episodic']) {
      try {
        await cypher(shardName, {
          statement: `MATCH (m:Memory) WHERE m.trigger STARTS WITH $prefix DETACH DELETE m`,
          parameters: { prefix: contextId },
        });
      } catch {}
    }
    // Remove from embedding cache
    for (let i = embeddingCache.length - 1; i >= 0; i--) {
      if (embeddingCache[i].trigger && embeddingCache[i].trigger.startsWith(contextId)) {
        embeddingCache.splice(i, 1);
      }
    }
    const result = await encode({
      event: contextId,
      content,
      context: { source: 'session-context', sessionKey, when: new Date().toISOString() },
      shard: 'episodic',
      motivationDelta: { survive: 0.8, serve: 0.5 },
      dedupThreshold: 0,
    });
    res.json({ ok: true, id: result.id, latency: Date.now() - start });
  } catch (e) {
    res.status(500).json({ ok: false, error: e.message });
  }
});

app.get('/memory/session-context', async (req, res) => {
  const start = Date.now();
  const { sessionKey } = req.query;
  const prefix = sessionKey ? `${SESSION_CONTEXT_PREFIX}${sessionKey}` : SESSION_CONTEXT_PREFIX;
  try {
    const r = await cypher('episodic', {
      statement: `MATCH (m:Memory) WHERE m.trigger STARTS WITH $prefix
        RETURN m.id AS id, m.content AS content, m.trigger AS trigger, m.created AS created
        ORDER BY m.created DESC LIMIT ${sessionKey ? 1 : 5}`,
      parameters: { prefix },
    });
    const data = r?.[0]?.data;
    if (sessionKey) {
      const row = data?.[0];
      res.json({ ok: true, context: row ? { id: row.row[0], content: row.row[1], trigger: row.row[2], created: row.row[3] } : null, latency: Date.now() - start });
    } else {
      res.json({ ok: true, contexts: (data || []).map(d => ({ id: d.row[0], content: d.row[1], created: d.row[2] })), latency: Date.now() - start });
    }
  } catch (e) {
    res.status(500).json({ ok: false, error: e.message });
  }
});

const PORT = process.env.PORT || 3333;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🧠 BrainDB Gateway v0.5.0 listening on port ${PORT}`);
  console.log(`   Architecture: ${ARCHITECTURE}`);
  console.log(`   Shards: ${Object.keys(SHARDS).join(', ')}`);
  console.log(`   Auth: ${API_KEY ? 'API key required' : 'open (localhost only)'}`);
  console.log(`   Write queue: ${writeQueue.length} pending`);
  warmPatternCache(recall).catch(() => {});
});
