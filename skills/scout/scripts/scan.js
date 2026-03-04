#!/usr/bin/env node
/**
 * Scout Scan - Score multiple agents from a feed or submolt
 * Usage: node scan.js [--submolt=general] [--limit=10] [--sort=new] [--json]
 */

const { MoltbookClient } = require('./lib/moltbook');
const { TrustScorer } = require('./lib/scoring');

async function main() {
  const args = process.argv.slice(2);
  const jsonMode = args.includes('--json');
  const submolt = (args.find(a => a.startsWith('--submolt=')) || '').split('=')[1] || null;
  const limit = parseInt((args.find(a => a.startsWith('--limit=')) || '').split('=')[1]) || 10;
  const sort = (args.find(a => a.startsWith('--sort=')) || '').split('=')[1] || 'new';

  const apiKey = process.env.MOLTBOOK_API_KEY;
  if (!apiKey) {
    console.error('Error: MOLTBOOK_API_KEY environment variable required');
    process.exit(1);
  }

  const client = new MoltbookClient(apiKey);
  const scorer = new TrustScorer();

  try {
    // Get posts to find agents
    console.error(`Scanning ${submolt ? 'm/' + submolt : 'global feed'} (${sort}, limit ${limit})...`);
    const posts = submolt
      ? await client.getSubmoltPosts(submolt, sort, limit)
      : await client.getFeed(sort, limit);

    // Unique authors
    const authors = [...new Set(posts.map(p => p.author?.name).filter(Boolean))];
    console.error(`Found ${authors.length} unique agents. Scoring...`);

    const results = [];
    for (const name of authors) {
      try {
        const profile = await client.getProfile(name);
        const result = scorer.score(profile);
        results.push(result);
        console.error(`  ${name}: ${result.score}/100`);
        // Rate limit respect
        await new Promise(r => setTimeout(r, 500));
      } catch (err) {
        console.error(`  ${name}: FAILED (${err.message})`);
      }
    }

    // Sort by score descending
    results.sort((a, b) => b.score - a.score);

    if (jsonMode) {
      console.log(JSON.stringify(results, null, 2));
    } else {
      console.log(`\n=== SCOUT SCAN RESULTS ===`);
      console.log(`Source: ${submolt ? 'm/' + submolt : 'global'} | Sort: ${sort} | Agents: ${results.length}\n`);

      const bar = (s) => {
        const filled = Math.round(s / 10);
        return '\u2588'.repeat(filled) + '\u2591'.repeat(10 - filled);
      };

      results.forEach((r, i) => {
        const rec = r.recommendation;
        const flagStr = r.flags.length > 0 ? ` [${r.flags.join(', ')}]` : '';
        console.log(`${i + 1}. ${r.agentName.padEnd(20)} ${bar(r.score)} ${r.score}/100  ${rec.level}${flagStr}`);
      });

      console.log(`\nLegend: ${'\u2588'} = 10 points | HIGH = safe to transact | LOW = use caution`);
    }

  } catch (err) {
    console.error(`Error: ${err.message}`);
    process.exit(1);
  }
}

main();
