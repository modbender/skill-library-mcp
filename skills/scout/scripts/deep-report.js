#!/usr/bin/env node
/**
 * Scout Deep Report - Enhanced trust report with on-chain + graph analysis
 * Usage: node deep-report.js <agentName> [--wallet=0x...] [--chain=base-sepolia] [--json]
 */

const { MoltbookClient } = require('./lib/moltbook');
const { TrustScorer } = require('./lib/scoring');
const { OnchainAnalyzer } = require('./lib/onchain');
const { InteractionGraph } = require('./lib/graph');

async function main() {
  const args = process.argv.slice(2);
  const jsonMode = args.includes('--json');
  const agentName = args.find(a => !a.startsWith('--'));
  const wallet = (args.find(a => a.startsWith('--wallet=')) || '').split('=')[1];
  const chain = (args.find(a => a.startsWith('--chain=')) || '').split('=')[1] || 'base-sepolia';

  if (!agentName) {
    console.error('Usage: node deep-report.js <agentName> [--wallet=0x...] [--chain=base-sepolia] [--json]');
    process.exit(1);
  }

  const apiKey = process.env.MOLTBOOK_API_KEY;
  if (!apiKey) {
    console.error('Error: MOLTBOOK_API_KEY required');
    process.exit(1);
  }

  const client = new MoltbookClient(apiKey);
  const scorer = new TrustScorer();
  const onchain = new OnchainAnalyzer();

  console.error(`=== Deep Analysis: ${agentName} ===`);

  // 1. Standard trust scoring
  console.error('[1/3] Running Moltbook trust analysis...');
  const profile = await client.getProfile(agentName);
  const trustResult = scorer.score(profile);

  // 2. On-chain analysis (if wallet provided)
  let onchainResult = null;
  if (wallet) {
    console.error(`[2/3] Analyzing on-chain activity (${chain})...`);
    onchainResult = await onchain.analyze(wallet, chain);
  } else {
    console.error('[2/3] No wallet provided, skipping on-chain analysis.');
  }

  // 3. Ego graph analysis
  console.error('[3/3] Building interaction graph...');
  const graph = new InteractionGraph();

  // Build ego graph from profile data
  for (const post of profile.posts) {
    try {
      const comments = await client._request(`/posts/${post.id}/comments`);
      if (comments.success && comments.comments) {
        for (const comment of comments.comments) {
          const commenter = comment.author?.name;
          if (commenter && commenter !== agentName) {
            graph.addInteraction(commenter, agentName);
          }
        }
      }
      await new Promise(r => setTimeout(r, 300));
    } catch (err) { /* skip */ }
  }

  for (const comment of profile.comments) {
    const postAuthor = comment.post?.author?.name || comment.post_author;
    if (postAuthor && postAuthor !== agentName) {
      graph.addInteraction(agentName, postAuthor);
    }
  }

  const graphStats = graph.stats();
  const diversity = graph.diversity(agentName);

  // Composite deep score
  let deepScore = trustResult.score;
  const bonuses = [];

  // On-chain bonus (up to +15)
  if (onchainResult && onchainResult.hasActivity) {
    const onchainBonus = Math.min(15, Math.round(onchainResult.score * 0.15));
    deepScore += onchainBonus;
    bonuses.push({ source: 'On-chain activity', bonus: onchainBonus });
  }

  // Graph diversity bonus (up to +10)
  if (diversity.diversityScore > 50) {
    const graphBonus = Math.min(10, Math.round((diversity.diversityScore - 50) * 0.2));
    deepScore += graphBonus;
    bonuses.push({ source: 'Interaction diversity', bonus: graphBonus });
  }

  deepScore = Math.min(100, deepScore);

  if (jsonMode) {
    console.log(JSON.stringify({
      agent: agentName,
      deepScore,
      moltbookScore: trustResult.score,
      bonuses,
      trust: trustResult,
      onchain: onchainResult,
      graph: { stats: graphStats, diversity },
    }, null, 2));
    return;
  }

  // Display
  console.log(trustResult.summary);

  console.log(`\nStatistical Context:`);
  console.log(`  Sample size: ${trustResult.sampleSize} | Confidence: ${trustResult.confidence}% | Freshness: ${trustResult.decay}%`);

  if (onchainResult) {
    console.log(`\nOn-Chain Analysis (${chain}):`);
    if (onchainResult.hasActivity) {
      const d = onchainResult.details;
      console.log(`  Wallet: ${wallet}`);
      console.log(`  Transactions: ${d.txCount} | Unique counterparties: ${d.uniqueCounterparties}`);
      console.log(`  USDC: ${d.usdcTxCount} transfers | ${d.usdcVolume} USDC total volume`);
      console.log(`    Sent: ${d.usdcSent} | Received: ${d.usdcReceived} | Counterparties: ${d.usdcCounterparties}`);
      console.log(`  Contract interactions: ${d.contractInteractions}`);
      console.log(`  Last activity: ${d.lastActivityDays} days ago`);
      console.log(`  On-chain score: ${onchainResult.score}/100`);
    } else {
      console.log(`  No on-chain activity found for ${wallet}`);
    }
  }

  console.log(`\nInteraction Graph:`);
  console.log(`  Graph: ${graphStats.nodes} nodes, ${graphStats.edges} edges`);
  console.log(`  Outgoing: ${diversity.totalOutgoing} interactions with ${diversity.uniqueOutgoing} unique agents`);
  console.log(`  Incoming: ${diversity.totalIncoming} interactions from ${diversity.uniqueIncoming} unique agents`);
  console.log(`  Concentration (Gini): ${Math.round(diversity.outgoingConcentration * 100)}%`);
  console.log(`  Diversity score: ${diversity.diversityScore}/100`);

  console.log(`\n=== DEEP TRUST SCORE: ${deepScore}/100 ===`);
  console.log(`  Base (Moltbook): ${trustResult.score}/100`);
  for (const b of bonuses) {
    console.log(`  + ${b.source}: +${b.bonus}`);
  }

  const rec = scorer._recommend ? new TrustScorer()._recommend || trustResult.recommendation : trustResult.recommendation;
  console.log(`\nTransaction Recommendation:`);
  console.log(`  ${trustResult.recommendation.text}`);
  console.log(`  Max: ${trustResult.recommendation.maxTransaction} USDC | Escrow: ${trustResult.recommendation.escrowPct}%`);
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
