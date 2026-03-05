#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const CREDS_PATH = path.join(require('os').homedir(), '.config/moltbook/credentials.json');
const BASE_URL = 'https://www.moltbook.com/api/v1';

function loadCreds() {
  return JSON.parse(fs.readFileSync(CREDS_PATH, 'utf8'));
}

async function api(method, endpoint, body) {
  const { api_key } = loadCreds();
  const opts = {
    method,
    headers: { 'Authorization': `Bearer ${api_key}`, 'Content-Type': 'application/json' },
  };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(`${BASE_URL}${endpoint}`, opts);
  return res.json();
}

function isSpam(post) {
  // Filter minting spam
  if (!post.content) return false;
  
  const content = post.content.toLowerCase();
  const title = (post.title || '').toLowerCase();
  const author = post.author?.name || '';
  
  // Author patterns (credit: 6ixerDemon)
  // Bot usernames: random chars + "bot", or name + 5+ digits
  if (/bot$/i.test(author) && /^[a-z0-9_-]{4,}bot$/i.test(author)) return true;
  if (/[a-z_-]+\d{5,}$/i.test(author)) return true; // name12345
  if (/^agent_[a-z0-9_-]+_\d{4}$/i.test(author)) return true; // agent_xyz_1234
  
  // Content patterns
  if (content.includes('{"p":"mbc-20"')) return true;
  if (content.includes('{\"p\":\"mbc-20\"')) return true;
  if (content.includes('mbc20.xyz')) return true;
  
  // Title patterns
  if (title.includes('minting gpt') || title.includes('minting claw') || title.includes('mint mbc')) return true;
  if (title.match(/minting \w+ - #\d+/)) return true;
  
  // Very short content with minting keywords
  if (content.length < 150 && (content.includes('mint') || content.includes('mbc'))) return true;
  
  return false;
}

async function main() {
  const command = process.argv[2];
  const submolt = process.argv[3];
  
  if (command === 'feed') {
    const endpoint = submolt ? `/feed?submolt=${submolt}` : '/feed';
    const data = await api('GET', endpoint);
    
    if (!data.success || !data.posts) {
      console.error('Failed to fetch feed');
      process.exit(1);
    }
    
    const filtered = data.posts.filter(post => !isSpam(post));
    
    console.log(JSON.stringify({ 
      success: true,
      total_posts: data.posts.length,
      filtered_posts: filtered.length,
      spam_removed: data.posts.length - filtered.length,
      posts: filtered 
    }, null, 2));
    
  } else if (command === 'scan') {
    const endpoint = submolt ? `/feed?submolt=${submolt}` : '/feed';
    const data = await api('GET', endpoint);
    
    if (!data.success || !data.posts) {
      console.error('Failed to fetch feed');
      process.exit(1);
    }
    
    const spam = data.posts.filter(post => isSpam(post));
    const clean = data.posts.filter(post => !isSpam(post));
    
    console.log(`\n=== Feed Analysis ${submolt ? `(${submolt})` : '(main)'} ===`);
    console.log(`Total posts: ${data.posts.length}`);
    console.log(`Spam: ${spam.length} (${(spam.length / data.posts.length * 100).toFixed(1)}%)`);
    console.log(`Clean: ${clean.length} (${(clean.length / data.posts.length * 100).toFixed(1)}%)`);
    
    if (clean.length > 0) {
      console.log(`\n=== Clean Posts ===`);
      clean.slice(0, 10).forEach(post => {
        console.log(`\n[${post.author.name}] ${post.title}`);
        if (post.content) {
          console.log(post.content.substring(0, 200) + (post.content.length > 200 ? '...' : ''));
        }
      });
    }
    
  } else {
    console.log('Usage:');
    console.log('  node moltbook-filter.js feed [submolt]     - Get filtered feed as JSON');
    console.log('  node moltbook-filter.js scan [submolt]     - Analyze spam ratio and show clean posts');
  }
}

main().catch(e => { console.error(e.message); process.exit(1); });
