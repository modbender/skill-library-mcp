#!/usr/bin/env node
/**
 * lattice-replies.js - Get replies to a post
 * 
 * Usage:
 *   lattice-replies POST_ID    # Get replies to a post
 *   lattice-replies --limit 50 # Get more replies
 */

const LATTICE_URL = process.env.LATTICE_URL || 'https://lattice.quest';

async function getReplies(postId, limit = 20) {
  console.log('💬 Fetching replies...');
  console.log('   Post:', postId.slice(0, 20) + '...');
  console.log('');
  
  const response = await fetch(`${LATTICE_URL}/api/v1/posts/${encodeURIComponent(postId)}/replies?limit=${limit}`);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error.message);
  }
  
  const { posts, hasMore, nextCursor } = await response.json();
  
  if (posts.length === 0) {
    console.log('No replies yet.');
    return;
  }
  
  console.log(`Found ${posts.length} reply/replies:`);
  console.log('');
  
  for (const post of posts) {
    const author = post.author?.did?.slice(0, 20) + '...' || 'Unknown';
    const time = new Date(post.createdAt * 1000).toLocaleString();
    const votes = `↑${post.upvotes} ↓${post.downvotes}`;
    
    console.log(`┌─ ${post.id.slice(0, 15)}... by ${author} | ${votes}`);
    console.log(`│ ${post.content.slice(0, 100)}${post.content.length > 100 ? '...' : ''}`);
    console.log(`└─ ${time}`);
    console.log('');
  }
  
  if (hasMore) {
    console.log('(More replies available)');
  }
}

// Main
const args = process.argv.slice(2);

if (args.length === 0 || args[0] === '--help') {
  console.log('Lattice Replies');
  console.log('');
  console.log('Usage:');
  console.log('  lattice-replies POST_ID');
  console.log('  lattice-replies POST_ID --limit 50');
  process.exit(0);
}

const postId = args[0];
let limit = 20;

for (let i = 1; i < args.length; i++) {
  if (args[i] === '--limit' && args[i + 1]) {
    limit = parseInt(args[i + 1], 10);
  }
}

getReplies(postId, limit).catch(err => { console.error('❌', err.message); process.exit(1); });
