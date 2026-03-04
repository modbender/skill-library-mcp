#!/usr/bin/env node
/**
 * Scout Graph Analysis - Build interaction graph and run SybilRank
 * 
 * Usage:
 *   node graph-analysis.js --submolt=usdc [--seeds=Lloyd,Fledge] [--json]
 *   node graph-analysis.js --agent=AgentName [--depth=2]
 */

const { MoltbookClient } = require('./lib/moltbook');
const { InteractionGraph } = require('./lib/graph');

async function main() {
  const args = process.argv.slice(2);
  const jsonMode = args.includes('--json');
  const submolt = (args.find(a => a.startsWith('--submolt=')) || '').split('=')[1];
  const agentName = (args.find(a => a.startsWith('--agent=')) || '').split('=')[1];
  const seedsArg = (args.find(a => a.startsWith('--seeds=')) || '').split('=')[1];
  const seeds = seedsArg ? seedsArg.split(',') : [];
  const limit = parseInt((args.find(a => a.startsWith('--limit=')) || '').split('=')[1]) || 30;

  const apiKey = process.env.MOLTBOOK_API_KEY;
  if (!apiKey) {
    console.error('Error: MOLTBOOK_API_KEY required');
    process.exit(1);
  }

  const client = new MoltbookClient(apiKey);
  const graph = new InteractionGraph();

  if (submolt) {
    console.error(`Building interaction graph from m/${submolt}...`);

    // Fetch posts from submolt
    const posts = await client.getSubmoltPosts(submolt, 'hot', limit);
    console.error(`Got ${posts.length} posts. Fetching comments...`);

    // For each post, fetch comments to build the graph
    for (const post of posts) {
      const authorName = post.author?.name;
      if (!authorName) continue;

      try {
        const comments = await client._request(`/posts/${post.id}/comments`);
        if (comments.success && comments.comments) {
          for (const comment of comments.comments) {
            const commenterName = comment.author?.name;
            if (commenterName && commenterName !== authorName) {
              graph.addInteraction(commenterName, authorName);
            }
          }
        }
        // Rate limit
        await new Promise(r => setTimeout(r, 300));
      } catch (err) {
        console.error(`  Error fetching comments for ${post.id}: ${err.message}`);
      }
    }
  } else if (agentName) {
    console.error(`Building ego graph for ${agentName}...`);

    // Get agent's posts and their comments
    const profile = await client.getProfile(agentName);

    // From posts: who comments on this agent
    for (const post of profile.posts) {
      try {
        const comments = await client._request(`/posts/${post.id}/comments`);
        if (comments.success && comments.comments) {
          for (const comment of comments.comments) {
            const commenterName = comment.author?.name;
            if (commenterName && commenterName !== agentName) {
              graph.addInteraction(commenterName, agentName);
            }
          }
        }
        await new Promise(r => setTimeout(r, 300));
      } catch (err) {
        // skip
      }
    }

    // From comments: who this agent comments on
    for (const comment of profile.comments) {
      const postAuthor = comment.post?.author?.name || comment.post_author;
      if (postAuthor && postAuthor !== agentName) {
        graph.addInteraction(agentName, postAuthor);
      }
    }
  } else {
    console.error('Usage: node graph-analysis.js --submolt=usdc [--seeds=A,B] [--json]');
    console.error('       node graph-analysis.js --agent=AgentName');
    process.exit(1);
  }

  // Run analysis
  const stats = graph.stats();
  console.error(`Graph: ${stats.nodes} nodes, ${stats.edges} edges, density: ${Math.round(stats.density * 1000) / 1000}`);

  // SybilRank
  const sybilScores = graph.sybilRank(seeds);

  // Reciprocal detection
  const reciprocals = graph.findReciprocals(2);

  if (jsonMode) {
    console.log(JSON.stringify({
      stats,
      sybilRank: sybilScores,
      reciprocals,
    }, null, 2));
    return;
  }

  // Display results
  console.log(`\n=== SCOUT GRAPH ANALYSIS ===`);
  console.log(`Nodes: ${stats.nodes} | Edges: ${stats.edges} | Density: ${Math.round(stats.density * 1000) / 1000} | Avg degree: ${stats.avgDegree}`);
  if (seeds.length > 0) {
    console.log(`Seeds: ${seeds.join(', ')}`);
  }

  // SybilRank scores sorted
  console.log(`\nSybilRank Trust Propagation:`);
  const sorted = Object.entries(sybilScores).sort((a, b) => b[1] - a[1]);

  const maxNameLen = Math.max(...sorted.map(([n]) => n.length), 10);
  const pad = (s, n) => s.padEnd(n);
  const bar = (s) => {
    const filled = Math.round(s / 10);
    return '\u2588'.repeat(filled) + '\u2591'.repeat(10 - filled);
  };

  for (const [name, score] of sorted) {
    const div = graph.diversity(name);
    console.log(`  ${pad(name, maxNameLen)} ${bar(score)} ${score}/100  (in:${div.uniqueIncoming} out:${div.uniqueOutgoing})`);
  }

  // Reciprocals
  if (reciprocals.length > 0) {
    console.log(`\nReciprocal Comment Rings (potential coordination):`);
    for (const r of reciprocals.slice(0, 10)) {
      const sym = Math.round(r.symmetry * 100);
      console.log(`  ${r.agents[0]} <-> ${r.agents[1]}  (${r.weightAB}/${r.weightBA} interactions, ${sym}% symmetric)`);
    }
  } else {
    console.log(`\nNo reciprocal comment rings detected.`);
  }

  // Individual agent stats (if specified)
  if (agentName) {
    const div = graph.diversity(agentName);
    console.log(`\n${agentName} Interaction Profile:`);
    console.log(`  Outgoing: ${div.totalOutgoing} interactions with ${div.uniqueOutgoing} unique agents`);
    console.log(`  Incoming: ${div.totalIncoming} interactions from ${div.uniqueIncoming} unique agents`);
    console.log(`  Concentration (Gini): ${Math.round(div.outgoingConcentration * 100)}%`);
    console.log(`  Diversity Score: ${div.diversityScore}/100`);
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
