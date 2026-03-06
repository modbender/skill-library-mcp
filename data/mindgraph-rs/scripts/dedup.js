#!/usr/bin/env node
/**
 * MindGraph Deduplication Script
 * 
 * Merges nodes with identical labels (case-insensitive).
 * Updated to use the 18 Cognitive Layer Tools API.
 */

'use strict';

const mg = require('/home/node/.openclaw/workspace/mindgraph-client.js');

async function withRetry(fn, label, maxRetries = 3, delayMs = 500) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (e) {
      if (e.message?.includes('database is locked') && attempt < maxRetries) {
        await new Promise(r => setTimeout(r, delayMs * attempt));
      } else throw e;
    }
  }
}

async function main() {
  console.log('Fetching all nodes...');
  const types = ['Entity','Source','Observation','Claim','Evidence','Pattern',
    'Hypothesis','Concept','Theory','Warrant','Analogy','Goal','Project',
    'Decision','Constraint','Milestone','Option','Flow','FlowStep','Affordance',
    'RiskAssessment','Preference','MemoryPolicy','Trace','Summary','Agent',
    'Task','Plan','PlanStep','Approval','Policy','Execution','Model','Method','Experiment','Snippet'];
  
  let allNodes = [];
  for (const t of types) {
    const r = await mg.getNodes({ nodeType: t, limit: 1000 });
    const nodes = r.items || r || [];
    allNodes.push(...nodes);
  }

  console.log(`Processing ${allNodes.length} nodes...`);

  // Group by label
  const groups = new Map();
  for (const node of allNodes) {
    let labelText = node.label.toLowerCase().trim();
    if (node.node_type === 'Source') {
      labelText = labelText.replace(/^source[:\s]+/, '');
    }
    const key = labelText;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(node);
  }

  let mergedCount = 0;

  for (const [key, nodes] of groups.entries()) {
    if (nodes.length <= 1) continue;

    console.log(`\nMerging group for key: "${key}" (${nodes.length} nodes)`);
    
    // Pick the canonical node
    const canonical = nodes.sort((a, b) => {
      const aScore = (Object.keys(a.props || {}).length) + (a.summary?.length || 0);
      const bScore = (Object.keys(b.props || {}).length) + (b.summary?.length || 0);
      return bScore - aScore;
    })[0];

    console.log(`  Canonical UID: ${canonical.uid} [${canonical.node_type}]`);

    for (const node of nodes) {
      if (node.uid === canonical.uid) continue;

      console.log(`  Merging duplicate: ${node.uid} [${node.node_type}]`);

      // Use mg.manageEntity for merging if it's an entity type, otherwise evolve tombstone
      try {
        await mg.manageEntity({
          action: 'merge',
          keepUid: canonical.uid,
          mergeUid: node.uid,
          agentId: 'dedup-script'
        });
        mergedCount++;
      } catch (e) {
        // If merge failed (e.g. not an entity or type mismatch), fall back to manual move + tombstone
        console.log(`    Manual merge for non-entity type: ${node.node_type}`);
        
        const edges = await mg.getEdges(node.uid);
        for (const edge of edges) {
          if (edge.tombstone_at) continue;
          try {
            if (edge.from_uid === node.uid) {
              await withRetry(() => mg.link(canonical.uid, edge.to_uid, edge.edge_type), `link out ${edge.edge_type}`);
            } else {
              await withRetry(() => mg.link(edge.from_uid, canonical.uid, edge.edge_type), `link in ${edge.edge_type}`);
            }
          } catch (err) {}
        }
        
        await withRetry(() => mg.evolve('tombstone', node.uid, { reason: 'merged with duplicate' }), `tombstone ${node.uid}`);
        mergedCount++;
      }
    }
  }

  console.log(`\nDone. Merged ${mergedCount} duplicate nodes.`);
}

main().catch(err => {
  console.error('FATAL:', err.message);
  process.exit(1);
});
