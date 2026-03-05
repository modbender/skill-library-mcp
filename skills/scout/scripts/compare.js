#!/usr/bin/env node
/**
 * Scout Compare - Side-by-side agent comparison
 * Usage: node compare.js Agent1 Agent2 [Agent3...] [--json]
 */

const { MoltbookClient } = require('./lib/moltbook');
const { TrustScorer } = require('./lib/scoring');

async function main() {
  const args = process.argv.slice(2);
  const jsonMode = args.includes('--json');
  const agents = args.filter(a => !a.startsWith('--') && a.toLowerCase() !== 'vs');

  if (agents.length < 2) {
    console.error('Usage: node compare.js Agent1 Agent2 [Agent3...] [--json]');
    process.exit(1);
  }

  const apiKey = process.env.MOLTBOOK_API_KEY;
  if (!apiKey) {
    console.error('Error: MOLTBOOK_API_KEY required');
    process.exit(1);
  }

  const client = new MoltbookClient(apiKey);
  const scorer = new TrustScorer();

  const results = [];

  for (const name of agents) {
    try {
      console.error(`Scoring ${name}...`);
      const profile = await client.getProfile(name);
      const result = scorer.score(profile);
      results.push({ ...result, profile });
      await new Promise(r => setTimeout(r, 500));
    } catch (err) {
      console.error(`  Failed: ${err.message}`);
    }
  }

  if (jsonMode) {
    console.log(JSON.stringify(results.map(r => ({
      agent: r.agentName,
      score: r.score,
      dimensions: r.dimensions,
      recommendation: r.recommendation,
      flags: r.flags
    })), null, 2));
    return;
  }

  // Visual comparison table
  const bar = (s) => {
    const filled = Math.round(s / 10);
    return '\u2588'.repeat(filled) + '\u2591'.repeat(10 - filled);
  };

  const maxNameLen = Math.max(...results.map(r => r.agentName.length), 10);
  const pad = (s, n) => s.padEnd(n);

  console.log(`\n=== SCOUT COMPARISON ===\n`);

  // Header
  const header = pad('', 20) + results.map(r => pad(r.agentName, maxNameLen + 2)).join('');
  console.log(header);
  console.log('-'.repeat(header.length));

  // Trust Score
  console.log(pad('TRUST SCORE', 20) + results.map(r =>
    pad(`${r.score}/100`, maxNameLen + 2)).join(''));
  console.log('');

  // Dimensions
  const dimNames = [
    ['volumeValue', 'Volume & Value'],
    ['originality', 'Originality'],
    ['engagement', 'Engagement'],
    ['credibility', 'Credibility'],
    ['capability', 'Capability'],
    ['spam', 'Spam Risk']
  ];

  for (const [key, label] of dimNames) {
    console.log(pad(label, 20) + results.map(r =>
      pad(`${r.dimensions[key].score}/100`, maxNameLen + 2)).join(''));
  }

  console.log('');

  // Key stats
  console.log(pad('Karma', 20) + results.map(r =>
    pad(`${r.profile.agent.karma}`, maxNameLen + 2)).join(''));
  console.log(pad('Followers', 20) + results.map(r =>
    pad(`${r.profile.agent.follower_count}`, maxNameLen + 2)).join(''));
  console.log(pad('Posts/day', 20) + results.map(r =>
    pad(`${r.dimensions.volumeValue.details.postsPerDay}`, maxNameLen + 2)).join(''));
  console.log(pad('Avg upvotes', 20) + results.map(r =>
    pad(`${r.dimensions.volumeValue.details.avgUpvotes}`, maxNameLen + 2)).join(''));
  console.log(pad('Claimed', 20) + results.map(r =>
    pad(`${r.profile.agent.is_claimed ? 'Yes' : 'No'}`, maxNameLen + 2)).join(''));
  console.log(pad('Trust Level', 20) + results.map(r =>
    pad(`${r.recommendation.level}`, maxNameLen + 2)).join(''));

  console.log('');

  // Flags
  console.log(pad('Flags', 20) + results.map(r =>
    pad(r.flags.length > 0 ? r.flags.join(', ') : '(none)', maxNameLen + 2)).join(''));

  // Verdict
  console.log('');
  const sorted = [...results].sort((a, b) => b.score - a.score);
  if (sorted[0].score - sorted[sorted.length - 1].score < 5) {
    console.log(`Verdict: Agents are comparable in trust level.`);
  } else {
    console.log(`Verdict: ${sorted[0].agentName} (${sorted[0].score}) is the most trusted.`);
    if (sorted.length > 2) {
      console.log(`Ranking: ${sorted.map((r, i) => `${i + 1}. ${r.agentName} (${r.score})`).join(' > ')}`);
    }
  }
}

main();
