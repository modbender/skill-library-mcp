#!/usr/bin/env node
/**
 * Scout Trust Report v2
 * Usage: node trust-report.js <agentName> [--json]
 */

const { MoltbookClient } = require('./lib/moltbook');
const { TrustScorer } = require('./lib/scoring');

async function main() {
  const args = process.argv.slice(2);
  const jsonMode = args.includes('--json');
  const agentName = args.find(a => !a.startsWith('--'));

  if (!agentName) {
    console.error('Usage: node trust-report.js <agentName> [--json]');
    process.exit(1);
  }

  const apiKey = process.env.MOLTBOOK_API_KEY;
  if (!apiKey) {
    console.error('Error: MOLTBOOK_API_KEY environment variable required');
    process.exit(1);
  }

  const client = new MoltbookClient(apiKey);
  const scorer = new TrustScorer();

  try {
    console.error(`Fetching profile for ${agentName}...`);
    const profile = await client.getProfile(agentName);

    console.error(`Scoring ${agentName}...`);
    const result = scorer.score(profile);

    if (jsonMode) {
      console.log(JSON.stringify(result, null, 2));
    } else {
      // Print visual report
      console.log(result.summary);

      // Statistical context
      console.log(`Statistical Context:`);
      console.log(`  Sample size: ${result.sampleSize} data points`);
      console.log(`  Confidence: ${result.confidence}% (Wilson lower bound)`);
      console.log(`  Freshness: ${result.decay}% (trust decay applied)`);

      const a = profile.agent;
      console.log(`\nProfile:`);
      console.log(`  Karma: ${a.karma} | Followers: ${a.follower_count} | Following: ${a.following_count}`);
      console.log(`  Claimed: ${a.is_claimed ? 'Yes' : 'No'} | Age: ${result.dimensions.credibility.details.accountAgeDays} days`);
      if (a.owner) {
        console.log(`  Owner: @${a.owner.x_handle} (${a.owner.x_follower_count} followers)`);
      }
      console.log(`  Bio: ${(a.description || '(none)').slice(0, 120)}`);

      console.log(`\nActivity:`);
      const vv = result.dimensions.volumeValue.details;
      console.log(`  Posts analyzed: ${vv.totalPosts} (${vv.postsPerDay}/day avg)`);
      console.log(`  Avg upvotes/post: ${vv.avgUpvotes} (Bayesian: ${vv.bayesianUpvotes})`);
      console.log(`  Avg comments/post: ${vv.avgComments}`);

      // Burstiness
      const spam = result.dimensions.spam.details;
      if (spam.postBurstiness !== null) {
        console.log(`  Posting burstiness: ${spam.postBurstiness} (B<-0.5=robotic, B>0=natural)`);
      }

      const orig = result.dimensions.originality.details;
      console.log(`\nOriginality Analysis:`);
      console.log(`  Comment NCD similarity: ${orig.avgNCD} (lower=more similar, <0.15=copied)`);
      console.log(`  Top 3 opener coverage: ${orig.top3TwoWordCoverage}%`);
      console.log(`  Structural concentration: ${orig.topStructuralCoverage}%`);
      console.log(`  Post keyword overlap: ${orig.avgPostSimilarity}%`);
      if (orig.topPatterns.length > 0) {
        console.log(`  Top patterns:`);
        orig.topPatterns.forEach(p => {
          console.log(`    "${p.pattern}..." - ${p.count}x (${p.pct}%)`);
        });
      }

      const eng = result.dimensions.engagement.details;
      console.log(`\nEngagement:`);
      console.log(`  Avg comment length: ${eng.avgCommentLength} chars`);
      console.log(`  Unique posts commented: ${eng.uniquePostsCommented}`);
      console.log(`  Response relevance: ${eng.relevanceScore}/100`);

      const cap = result.dimensions.capability.details;
      console.log(`\nCapability Evidence:`);
      console.log(`  Code blocks: ${cap.codeBlocks} | URLs: ${cap.urls} | Tx hashes: ${cap.txHashes}`);
      console.log(`  Technical density: ${cap.technicalDensity}%`);
      console.log(`  Claims in bio: ${cap.hasClaims ? 'Yes' : 'No'}`);

      const rec = result.recommendation;
      console.log(`\nTransaction Recommendation:`);
      console.log(`  Trust level: ${rec.level}`);
      console.log(`  ${rec.text}`);
      console.log(`  Max single transaction: ${rec.maxTransaction} USDC`);
      console.log(`  Escrow: ${rec.escrowPct}% escrowed | Terms: ${rec.escrowTerms}`);
    }

    process.exit(0);
  } catch (err) {
    console.error(`Error: ${err.message}`);
    process.exit(1);
  }
}

main();
