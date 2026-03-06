#!/usr/bin/env node
/**
 * EvoMap Reviewer - Review and validate assets from other nodes
 * 
 * Fetches pending assets from EvoMap Hub, validates them, and submits decisions.
 */

const { getNodeId, buildDecision, getTransport } = require('/root/clawd/skills/evolver/src/gep/a2aProtocol');
const { computeAssetId } = require('/root/clawd/skills/evolver/src/gep/contentHash');

const HUB_URL = process.env.A2A_HUB_URL || 'https://evomap.ai';

/**
 * Main execution function
 */
async function main() {
  console.log('🔍 EvoMap Reviewer Starting...\n');
  
  try {
    // Step 1: Fetch pending assets for review
    const assets = await fetchPendingAssets();
    console.log(`📋 Found ${assets.length} assets to review`);
    
    if (assets.length === 0) {
      console.log('✅ No assets pending review');
      return { success: true, reviewed: 0, message: 'No pending assets' };
    }
    
    // Step 2: Review each asset
    const results = [];
    for (const asset of assets.slice(0, 5)) { // Review max 5 per run
      const result = await reviewAsset(asset);
      results.push(result);
      console.log(`  ${result.decision === 'accept' ? '✅' : result.decision === 'reject' ? '❌' : '⏸️'} ${result.assetId.slice(0, 30)}... - ${result.decision}`);
    }
    
    // Step 3: Summary
    const accepted = results.filter(r => r.decision === 'accept').length;
    const rejected = results.filter(r => r.decision === 'reject').length;
    const quarantined = results.filter(r => r.decision === 'quarantine').length;
    
    console.log('\n--- Review Summary ---');
    console.log(`✅ Accepted: ${accepted}`);
    console.log(`❌ Rejected: ${rejected}`);
    console.log(`⏸️ Quarantined: ${quarantined}`);
    
    return {
      success: true,
      reviewed: results.length,
      accepted,
      rejected,
      quarantined,
      results
    };
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    return { success: false, reason: 'error', error: error.message };
  }
}

/**
 * Fetch pending assets from EvoMap Hub
 */
async function fetchPendingAssets() {
  const nodeId = getNodeId();
  
  try {
    const msg = {
      protocol: 'gep-a2a',
      protocol_version: '1.0.0',
      message_type: 'fetch',
      message_id: `review_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
      sender_id: nodeId,
      timestamp: new Date().toISOString(),
      payload: {
        asset_type: null, // Fetch all types
        status: 'pending_review', // Request pending review assets
      },
    };

    const url = `${HUB_URL.replace(/\/+$/, '')}/a2a/fetch`;
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 8000);

    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(msg),
      signal: controller.signal,
    });
    clearTimeout(timer);

    if (!res.ok) return [];

    const data = await res.json();
    const payload = data.payload || data;
    
    // Return assets that need review (not from this node)
    const assets = Array.isArray(payload.results) ? payload.results : [];
    return assets.filter(a => a.source_node_id !== nodeId && a.status !== 'promoted');
  } catch (e) {
    console.error('Fetch error:', e.message);
    return [];
  }
}

/**
 * Review a single asset and submit decision
 */
async function reviewAsset(asset) {
  const assetId = asset.asset_id || asset.payload?.asset_id;
  const assetType = asset.asset_type || asset.payload?.type;
  
  if (!assetId) {
    return { assetId: 'unknown', decision: 'reject', reason: 'No asset ID' };
  }
  
  // Validate the asset
  const validation = validateAsset(asset);
  
  // Build decision
  let decision = 'quarantine';
  let reason = 'Needs manual review';
  
  if (validation.score >= 0.8) {
    decision = 'accept';
    reason = `Validated: ${validation.checks.join(', ')}`;
  } else if (validation.score <= 0.3) {
    decision = 'reject';
    reason = `Failed: ${validation.errors.join(', ')}`;
  }
  
  // Submit decision to Hub
  const submitted = await submitDecision(assetId, decision, reason);
  
  return {
    assetId,
    assetType,
    decision,
    reason,
    score: validation.score,
    submitted
  };
}

/**
 * Validate an asset
 */
function validateAsset(asset) {
  const checks = [];
  const errors = [];
  let score = 0.5; // Start neutral
  
  const payload = asset.payload || asset;
  
  // Check required fields
  if (payload.type && ['Gene', 'Capsule', 'EvolutionEvent'].includes(payload.type)) {
    checks.push('Valid type');
    score += 0.1;
  } else {
    errors.push('Invalid or missing type');
    score -= 0.2;
  }
  
  // Check for ID
  if (payload.id || payload.asset_id) {
    checks.push('Has ID');
    score += 0.1;
  } else {
    errors.push('Missing ID');
    score -= 0.1;
  }
  
  // Check for summary/content
  if (payload.summary || payload.content || (payload.trigger && payload.trigger.length > 0)) {
    checks.push('Has content');
    score += 0.1;
  } else {
    errors.push('Missing content/summary');
    score -= 0.1;
  }
  
  // Check schema version
  if (payload.schema_version) {
    checks.push('Has schema version');
    score += 0.1;
  }
  
  // Check for trigger (Capsule)
  if (payload.type === 'Capsule') {
    if (payload.trigger && Array.isArray(payload.trigger) && payload.trigger.length >= 1) {
      checks.push('Has triggers');
      score += 0.1;
    } else {
      errors.push('Missing or empty triggers');
      score -= 0.1;
    }
  }
  
  // Check for signals_match (Gene)
  if (payload.type === 'Gene') {
    if (payload.signals_match && Array.isArray(payload.signals_match) && payload.signals_match.length >= 1) {
      checks.push('Has signals');
      score += 0.1;
    } else {
      errors.push('Missing or empty signals_match');
      score -= 0.1;
    }
  }
  
  // Clamp score
  score = Math.max(0, Math.min(1, score));
  
  return { score, checks, errors };
}

/**
 * Submit a decision to EvoMap Hub
 */
async function submitDecision(assetId, decision, reason) {
  const nodeId = getNodeId();
  
  try {
    const decisionMsg = buildDecision({
      assetId,
      decision,
      reason: reason.slice(0, 200) // Limit length
    });
    
    const transport = getTransport('http');
    const result = await transport.send(decisionMsg, { hubUrl: HUB_URL });
    
    return result.ok;
  } catch (e) {
    console.error('Decision submission error:', e.message);
    return false;
  }
}

// Run if called directly
if (require.main === module) {
  main().then(result => {
    console.log('\n--- Result ---');
    console.log(JSON.stringify(result, null, 2));
    process.exit(result.success ? 0 : 1);
  }).catch(err => {
    console.error('Fatal error:', err);
    process.exit(1);
  });
}

module.exports = { main, fetchPendingAssets, reviewAsset, validateAsset };
