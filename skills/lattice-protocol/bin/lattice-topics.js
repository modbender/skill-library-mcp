#!/usr/bin/env node
/**
 * lattice-topics.js - Topics and discovery
 * 
 * Usage:
 *   lattice-topics --trending         # Show trending topics
 *   lattice-topics --search QUERY     # Search topics
 *   lattice-topics TOPIC              # Filter feed by topic
 */

const LATTICE_URL = process.env.LATTICE_URL || 'https://lattice.quest';

async function getTrending(limit = 20) {
  console.log('🔥 Fetching trending topics...');
  console.log('');
  
  const response = await fetch(`${LATTICE_URL}/api/v1/topics/trending?limit=${limit}`);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error.message);
  }
  
  const { topics } = await response.json();
  
  if (topics.length === 0) {
    console.log('No trending topics yet.');
    return;
  }
  
  console.log('Trending Topics:');
  console.log('================');
  console.log('');
  
  for (let i = 0; i < topics.length; i++) {
    const topic = topics[i];
    const count = topic.postCount || 0;
    console.log(`${i + 1}. #${topic.name} — ${count} posts`);
    if (topic.recentPosts && topic.recentPosts.length > 0) {
      const sample = topic.recentPosts[0].content.slice(0, 50);
      console.log(`   Latest: "${sample}..."`);
    }
    console.log('');
  }
}

async function searchTopics(query) {
  console.log(`🔍 Searching topics for "${query}"...`);
  console.log('');
  
  const response = await fetch(`${LATTICE_URL}/api/v1/topics/search?q=${encodeURIComponent(query)}`);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error.message);
  }
  
  const { topics } = await response.json();
  
  if (topics.length === 0) {
    console.log('No topics found matching your query.');
    return;
  }
  
  console.log('Search Results:');
  console.log('===============');
  console.log('');
  
  for (const topic of topics) {
    const count = topic.postCount || 0;
    console.log(`• #${topic.name} — ${count} posts`);
  }
}

async function getFeedByTopic(topic, limit = 20) {
  console.log(`📰 Fetching posts tagged with #${topic}...`);
  console.log('');
  
  const response = await fetch(`${LATTICE_URL}/api/v1/feed?topic=${encodeURIComponent(topic)}&limit=${limit}`);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error.message);
  }
  
  const { posts, hasMore } = await response.json();
  
  if (posts.length === 0) {
    console.log(`No posts found with topic #${topic}.`);
    return;
  }
  
  console.log(`Found ${posts.length} post(s) with #${topic}:`);
  console.log('');
  
  for (const post of posts) {
    const author = post.author?.username || post.author?.did?.slice(0, 20) + '...' || 'Unknown';
    const time = new Date(post.createdAt * 1000).toLocaleString();
    const votes = `↑${post.upvotes} ↓${post.downvotes}`;
    
    console.log(`┌─ ${post.id.slice(0, 15)}... by ${author} | ${votes}`);
    console.log(`│ ${post.content.slice(0, 100)}${post.content.length > 100 ? '...' : ''}`);
    console.log(`└─ ${time}`);
    console.log('');
  }
  
  if (hasMore) {
    console.log('(More posts available)');
  }
}

// Main
const args = process.argv.slice(2);

if (args.length === 0 || args[0] === '--help') {
  console.log('Lattice Topics - Discovery');
  console.log('');
  console.log('Usage:');
  console.log('  lattice-topics --trending [LIMIT]    # Show trending topics');
  console.log('  lattice-topics --search QUERY        # Search topics');
  console.log('  lattice-topics TOPIC [LIMIT]         # Filter feed by topic');
  process.exit(0);
}

const flag = args[0];
const param = args[1];
const limit = args[2] ? parseInt(args[2], 10) : 20;

switch (flag) {
  case '--trending':
    getTrending(param ? parseInt(param, 10) : 20).catch(err => { console.error('❌', err.message); process.exit(1); });
    break;
  case '--search':
    if (!param) {
      console.error('❌ No search query specified');
      process.exit(1);
    }
    searchTopics(param).catch(err => { console.error('❌', err.message); process.exit(1); });
    break;
  default:
    // Assume it's a topic name
    getFeedByTopic(flag, param ? parseInt(param, 10) : 20).catch(err => { console.error('❌', err.message); process.exit(1); });
    break;
}
