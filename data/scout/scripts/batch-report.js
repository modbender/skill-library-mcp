#!/usr/bin/env node
/**
 * Scout Batch Report - Generate reports for multiple agents and save to file
 * Usage: node batch-report.js Agent1 Agent2 ... [--output=reports.md] [--json]
 *    or: node batch-report.js --submolt=usdc --limit=20 [--output=reports.md]
 */

const { MoltbookClient } = require('./lib/moltbook');
const { TrustScorer } = require('./lib/scoring');
const fs = require('fs');

async function main() {
  const args = process.argv.slice(2);
  const jsonMode = args.includes('--json');
  const outputFile = (args.find(a => a.startsWith('--output=')) || '').split('=')[1];
  const submolt = (args.find(a => a.startsWith('--submolt=')) || '').split('=')[1];
  const limit = parseInt((args.find(a => a.startsWith('--limit=')) || '').split('=')[1]) || 20;
  const agents = args.filter(a => !a.startsWith('--'));

  const apiKey = process.env.MOLTBOOK_API_KEY;
  if (!apiKey) {
    console.error('Error: MOLTBOOK_API_KEY required');
    process.exit(1);
  }

  const client = new MoltbookClient(apiKey);
  const scorer = new TrustScorer();

  let agentNames = agents;

  // If submolt mode, discover agents
  if (submolt) {
    console.error(`Discovering agents from m/${submolt}...`);
    const posts = await client.getSubmoltPosts(submolt, 'hot', limit);
    agentNames = [...new Set(posts.map(p => p.author?.name).filter(Boolean))];
    console.error(`Found ${agentNames.length} agents.`);
  }

  if (agentNames.length === 0) {
    console.error('No agents specified. Provide names or use --submolt=X');
    process.exit(1);
  }

  const results = [];
  let markdown = `# Scout Batch Trust Reports\n\nGenerated: ${new Date().toISOString()}\nAgents: ${agentNames.length}\n\n---\n\n`;

  // Summary table
  markdown += `## Summary\n\n`;
  markdown += `| Rank | Agent | Score | Level | Flags |\n`;
  markdown += `|------|-------|-------|-------|-------|\n`;

  for (const name of agentNames) {
    try {
      console.error(`Scoring ${name}...`);
      const profile = await client.getProfile(name);
      const result = scorer.score(profile);
      results.push({ ...result, profile });
      await new Promise(r => setTimeout(r, 500));
    } catch (err) {
      console.error(`  ${name}: FAILED (${err.message})`);
    }
  }

  // Sort by score
  results.sort((a, b) => b.score - a.score);

  // Summary table
  results.forEach((r, i) => {
    const flags = r.flags.length > 0 ? r.flags.join(', ') : '-';
    markdown += `| ${i + 1} | ${r.agentName} | ${r.score}/100 | ${r.recommendation.level} | ${flags} |\n`;
  });

  markdown += `\n---\n\n## Detailed Reports\n\n`;

  // Individual reports
  for (const r of results) {
    const a = r.profile.agent;
    const vv = r.dimensions.volumeValue.details;
    const orig = r.dimensions.originality.details;
    const cap = r.dimensions.capability.details;
    const rec = r.recommendation;

    markdown += `### ${r.agentName} - ${r.score}/100 (${rec.level})\n\n`;
    markdown += `| Dimension | Score |\n`;
    markdown += `|-----------|-------|\n`;
    markdown += `| Volume & Value | ${r.dimensions.volumeValue.score}/100 |\n`;
    markdown += `| Originality | ${r.dimensions.originality.score}/100 |\n`;
    markdown += `| Engagement | ${r.dimensions.engagement.score}/100 |\n`;
    markdown += `| Credibility | ${r.dimensions.credibility.score}/100 |\n`;
    markdown += `| Capability | ${r.dimensions.capability.score}/100 |\n`;
    markdown += `| Spam Risk | ${r.dimensions.spam.score}/100 |\n\n`;

    markdown += `**Profile:** Karma ${a.karma} | ${a.follower_count} followers | ${vv.postsPerDay} posts/day | ${vv.avgUpvotes} avg upvotes\n`;
    if (a.owner) {
      markdown += `**Owner:** @${a.owner.x_handle} (${a.owner.x_follower_count} X followers)\n`;
    }
    markdown += `**Bio:** ${(a.description || '(none)').slice(0, 150)}\n`;

    if (r.flags.length > 0) {
      markdown += `**Flags:** ${r.flags.join(', ')}\n`;
    }

    markdown += `**Transaction:** ${rec.text} | Max: ${rec.maxTransaction} USDC\n`;
    markdown += `\n---\n\n`;
  }

  if (outputFile) {
    fs.writeFileSync(outputFile, markdown);
    console.error(`Report saved to ${outputFile}`);
  }

  if (jsonMode) {
    console.log(JSON.stringify(results.map(r => ({
      agent: r.agentName,
      score: r.score,
      level: r.recommendation.level,
      dimensions: Object.fromEntries(
        Object.entries(r.dimensions).map(([k, v]) => [k, v.score])
      ),
      flags: r.flags,
      karma: r.profile.agent.karma,
      owner: r.profile.agent.owner?.x_handle || null
    })), null, 2));
  } else if (!outputFile) {
    console.log(markdown);
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
