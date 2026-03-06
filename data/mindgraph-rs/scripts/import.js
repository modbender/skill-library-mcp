#!/usr/bin/env node
/**
 * MindGraph Import Script
 * 
 * Updated to use the 18 Cognitive Layer Tools API for all writes.
 * 
 * Usage:
 *   node skills/mindgraph/import.js <extracted.json>
 */

'use strict';

const fs = require('fs');
const path = require('path');
const https = require('https');

const mg = require('/home/node/.openclaw/workspace/mindgraph-client.js');

// ─── Deduplication & Cache ────────────────────────────────────────────────────

const nodeCache = new Map(); // label → uid

async function findExisting(label) {
  if (nodeCache.has(label)) return nodeCache.get(label);
  
  const q = label.replace(/[-:\/\\()']/g, ' ').replace(/\s+/g, ' ').trim();
  if (!q) return null;

  // Pass 1: FTS exact label match
  try {
    const results = await mg.search(q, { limit: 5 });
    const match = (results || []).find(n => 
      n.label && n.label.toLowerCase() === label.toLowerCase()
    );
    if (match) {
      nodeCache.set(label, match.uid);
      return match.uid;
    }
  } catch (e) {}

  // Pass 2: Semantic similarity (catches near-duplicates with different wording)
  // Only if OPENAI_API_KEY is available; threshold 0.92 — high bar to avoid false merges
  if (process.env.OPENAI_API_KEY) {
    try {
      const results = await mg.retrieve('semantic', { query: label, limit: 3 });
      const items = Array.isArray(results) ? results : (results.items || []);
      const match = items.find(n =>
        !n.tombstone_at &&
        (n.score || 0) >= 0.92 &&
        n.label.toLowerCase() !== label.toLowerCase() // wasn't caught by FTS
      );
      if (match) {
        console.log(`  SEMANTIC-DEDUP: "${label}" → "${match.label}" (${Math.round(match.score * 100)}%)`);
        nodeCache.set(label, match.uid);
        return match.uid;
      }
    } catch (e) {}
  }

  return null;
}

// ─── Node Writer (Cognitive Mapping) ──────────────────────────────────────────

async function writeNode(node, opts) {
  const { dryRun, noDedup } = opts;

  if (!node.label || !node.type) {
    console.error(`  SKIP: missing label or type`, JSON.stringify(node).slice(0, 100));
    return null;
  }

  if (!noDedup) {
    const existingUid = await findExisting(node.label);
    if (existingUid) {
      console.log(`  DEDUP: ${node.label} → ${existingUid}`);
      nodeCache.set(node.label, existingUid);
      return existingUid;
    }
  }

  if (dryRun) {
    const fakeUid = `dry-${Math.random().toString(36).slice(2, 10)}`;
    console.log(`  DRY-RUN CREATE [${node.type}]: ${node.label}`);
    nodeCache.set(node.label, fakeUid);
    return fakeUid;
  }

  const type = node.type.toLowerCase();
  const label = node.label;
  const content = node.props?.content || node.summary || '';
  const props = node.props || {};

  try {
    let result;
    
    switch (type) {
      // 1. Reality
      case 'claim':
      case 'observation':
      case 'snippet':
      case 'source':
        result = await mg.ingest(label, content, type, { confidence: node.confidence });
        break;

      // 2. Entity
      case 'entity':
      case 'person':
      case 'organization':
      case 'service':
      case 'product':
      case 'location':
        result = await mg.manageEntity({ action: 'create', label, entityType: node.type });
        break;

      // 3. Epistemic Layer
      case 'argument':
        result = await mg.addArgument({ ...props, label });
        break;
      case 'inquiry':
      case 'question':
      case 'hypothesis':
      case 'anomaly':
        result = await mg.addInquiry(label, content, type, props);
        break;
      case 'structure':
      case 'concept':
      case 'pattern':
      case 'theory':
        result = await mg.addStructure(label, content, type, props);
        break;

      // 4. Intent Layer
      case 'commitment':
      case 'goal':
      case 'project':
      case 'milestone':
      case 'constraint':
        result = await mg.addCommitment(label, content, type, props);
        break;
      case 'decision':
      case 'option':
        result = await mg.deliberate({ action: 'open_decision', label, description: content, ...props });
        break;

      // 5. Action Layer
      case 'flow':
      case 'flowstep':
      case 'affordance':
      case 'control':
        result = await mg.procedure({ action: 'create_flow', label, description: content, ...props });
        break;
      case 'risk':
      case 'filter':
        result = await mg.risk({ action: 'assess', label, description: content, ...props });
        break;

      // 6. Memory Layer
      case 'session':
      case 'trace':
        result = await mg.sessionOp({ action: 'open', label, focus: content, ...props });
        break;
      case 'summary':
        result = await mg.distill(label, content, props);
        break;
      case 'memorypolicy':
      case 'preference':
        result = await mg.memoryConfig({ action: 'set_preference', label, value: content, ...props });
        break;

      // 7. Agent Layer
      case 'plan':
      case 'task':
        result = await mg.plan({ action: 'create_task', label, description: content, ...props });
        break;
      case 'governance':
      case 'policy':
        result = await mg.governance({ action: 'create_policy', label, policyContent: content, ...props });
        break;
      case 'execution':
        result = await mg.execution({ action: 'start', label, ...props });
        break;

      default:
        // Fallback to ingest if type is unrecognized
        result = await mg.ingest(label, content, type, props);
    }

    const uid = result?.uid;
    if (uid) {
      nodeCache.set(label, uid);
      console.log(`  CREATED [${node.type}]: ${label} → ${uid}`);
    }
    return uid;
  } catch (e) {
    console.error(`  ERROR creating "${label}": ${e.message}`);
    return null;
  }
}

// ─── Main Logic (Refactored) ──────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.log('Usage: node import.js <extracted.json> [--dry-run] [--no-dedup]');
    process.exit(0);
  }

  const opts = {
    dryRun: args.includes('--dry-run'),
    noDedup: args.includes('--no-dedup'),
  };

  const inputArg = args.find(a => !a.startsWith('--'));
  const raw = inputArg === '-' ? fs.readFileSync('/dev/stdin', 'utf8') : fs.readFileSync(inputArg, 'utf8');
  const data = JSON.parse(raw);
  const { meta, nodes, edges } = data;

  console.log(`\n=== MindGraph Cognitive Import ===`);
  console.log(`Source: ${meta?.source_path || 'unknown'}`);
  console.log(`Nodes: ${nodes?.length || 0}, Edges: ${edges?.length || 0}\n`);

  // Pre-load graph for dedup
  const allLive = await mg.getNodes({ limit: 1000 });
  for (const n of (allLive.items || [])) {
    nodeCache.set(n.label, n.uid);
    nodeCache.set(n.label.toLowerCase(), n.uid);
  }

  // Phase 1: Nodes
  let created = 0, deduped = 0, failed = 0;
  for (const node of (nodes || [])) {
    const sizeBefore = nodeCache.size;
    const uid = await writeNode(node, opts);
    if (uid) {
      if (nodeCache.size > sizeBefore) created++;
      else deduped++;
    } else failed++;
  }

  // Phase 2: Edges
  console.log('\n--- Phase 2: Writing edges ---');
  for (const edge of (edges || [])) {
    const fromUid = nodeCache.get(edge.from) || nodeCache.get(edge.from.toLowerCase());
    const toUid = nodeCache.get(edge.to) || nodeCache.get(edge.to.toLowerCase());

    if (fromUid && toUid) {
      try {
        if (!opts.dryRun) await mg.link(fromUid, toUid, edge.type.toUpperCase());
        console.log(`  EDGE [${edge.type}]: ${edge.from.slice(0, 20)} → ${edge.to.slice(0, 20)}`);
      } catch (e) {
        console.error(`  ERROR edge: ${e.message}`);
      }
    }
  }

  // Phase 3: Auto-wiring to source
  const sourceLabel = meta?.source_path ? `Source: ${path.basename(meta.source_path)}` : null;
  const sourceUid = sourceLabel ? nodeCache.get(sourceLabel) : null;
  if (sourceUid && !opts.dryRun) {
    console.log('\n--- Phase 3: Auto-wiring to source ---');
    for (const node of (nodes || [])) {
      const nodeUid = nodeCache.get(node.label);
      if (nodeUid && nodeUid !== sourceUid) {
        await mg.link(nodeUid, sourceUid, 'DERIVED_FROM').catch(() => {});
      }
    }
  }

  console.log(`\n=== DONE ===`);
}

main().catch(e => {
  console.error('FATAL:', e.message);
  process.exit(1);
});
