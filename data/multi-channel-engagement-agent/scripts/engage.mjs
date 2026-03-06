#!/usr/bin/env node
/**
 * Multi-Channel Engagement Agent
 * 
 * Autonomous engagement bot for Twitter, Farcaster, and Moltbook.
 * Fetches trending, generates persona-driven replies, tracks state.
 * 
 * Usage:
 *   node engage.mjs --platform twitter
 *   node engage.mjs --platform farcaster
 *   node engage.mjs --platform moltbook
 *   node engage.mjs --all
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// ============================================
// CONFIGURATION
// ============================================

function loadConfig(configPath) {
  if (!fs.existsSync(configPath)) {
    throw new Error(`Config not found: ${configPath}\nCreate config.json with platform credentials.`);
  }
  return JSON.parse(fs.readFileSync(configPath, 'utf8'));
}

function loadState(stateFile) {
  try {
    return JSON.parse(fs.readFileSync(stateFile, 'utf8'));
  } catch {
    return {
      lastUpdated: new Date().toISOString(),
      repliedPosts: { twitter: [], farcaster: [], moltbook: [] },
      stats: { totalReplies: 0, byPlatform: { twitter: 0, farcaster: 0, moltbook: 0 } }
    };
  }
}

function saveState(stateFile, state) {
  state.lastUpdated = new Date().toISOString();
  fs.writeFileSync(stateFile, JSON.stringify(state, null, 2));
}

// ============================================
// PLATFORM: TWITTER (OAuth 1.0a)
// ============================================

async function fetchTrendingTwitter(config, limit = 5) {
  // Uses twitter-api-v2 library
  const { TwitterApi } = await import('twitter-api-v2');
  
  const client = new TwitterApi({
    appKey: config.oauth.consumerKey,
    appSecret: config.oauth.consumerSecret,
    accessToken: config.oauth.accessToken,
    accessSecret: config.oauth.accessTokenSecret
  });

  // Search for crypto/web3 content
  const results = await client.v2.search('crypto OR web3 OR base -is:retweet', {
    max_results: limit,
    'tweet.fields': ['author_id', 'created_at', 'public_metrics', 'conversation_id'],
    expansions: ['author_id'],
    'user.fields': ['username', 'name']
  });

  return results.data?.data?.map(tweet => ({
    id: tweet.id,
    text: tweet.text,
    authorId: tweet.author_id,
    authorUsername: results.includes?.users?.find(u => u.id === tweet.author_id)?.username || 'unknown',
    metrics: tweet.public_metrics,
    platform: 'twitter'
  })) || [];
}

async function postReplyTwitter(config, tweetId, replyText) {
  const { TwitterApi } = await import('twitter-api-v2');
  
  const client = new TwitterApi({
    appKey: config.oauth.consumerKey,
    appSecret: config.oauth.consumerSecret,
    accessToken: config.oauth.accessToken,
    accessSecret: config.oauth.accessTokenSecret
  });

  const result = await client.v2.reply(replyText, tweetId);
  return { success: true, replyId: result.data.id };
}

// ============================================
// PLATFORM: FARCASTER (Neynar API)
// ============================================

async function fetchTrendingFarcaster(config, limit = 5) {
  const response = await fetch(
    `https://api.neynar.com/v2/farcaster/feed/trending?limit=${limit}`,
    { headers: { 'x-api-key': config.neynarApiKey } }
  );
  
  if (!response.ok) {
    throw new Error(`Neynar API error: ${response.status}`);
  }

  const { casts } = await response.json();
  
  return casts.map(cast => ({
    id: cast.hash,
    text: cast.text,
    authorFid: cast.author.fid,
    authorUsername: cast.author.username,
    metrics: {
      likes: cast.reactions?.likes_count || 0,
      recasts: cast.reactions?.recasts_count || 0,
      replies: cast.replies?.count || 0
    },
    platform: 'farcaster'
  }));
}

async function postReplyFarcaster(config, parentCast, replyText) {
  // Uses farcaster-agent skill's post-cast.js
  const env = {
    PRIVATE_KEY: config.custodyPrivateKey,
    SIGNER_PRIVATE_KEY: config.signerPrivateKey,
    FID: config.fid.toString(),
    PARENT_FID: parentCast.authorFid.toString(),
    PARENT_HASH: parentCast.id
  };

  const envStr = Object.entries(env).map(([k, v]) => `$env:${k}="${v}"`).join('; ');
  const cmd = `${envStr}; node skills/farcaster-agent/src/post-cast.js "${replyText.replace(/"/g, '\\"')}"`;
  
  try {
    const output = execSync(cmd, { encoding: 'utf8', shell: 'powershell.exe' });
    const hashMatch = output.match(/Cast hash: (0x[a-f0-9]+)/i);
    return { success: true, replyHash: hashMatch?.[1] || 'unknown' };
  } catch (error) {
    throw new Error(`Farcaster post failed: ${error.message}`);
  }
}

// ============================================
// PLATFORM: MOLTBOOK
// ============================================

async function fetchTrendingMoltbook(config, limit = 5) {
  const response = await fetch(
    `https://www.moltbook.com/api/v1/posts?sort=hot&limit=${limit}`,
    { headers: { 'Authorization': `Bearer ${config.apiKey}` } }
  );

  if (!response.ok) {
    throw new Error(`Moltbook API error: ${response.status}`);
  }

  const { posts } = await response.json();
  
  return posts.map(post => ({
    id: post.id,
    text: post.content || post.title,
    authorUsername: post.author?.username || 'unknown',
    metrics: { upvotes: post.upvotes || 0, comments: post.comment_count || 0 },
    platform: 'moltbook'
  }));
}

function solveMathChallenge(challenge) {
  const match = challenge.match(/What is (.+)\?/i);
  if (match) {
    // Safe evaluation for simple math
    const expr = match[1].replace(/[^0-9+\-*/\s.()]/g, '');
    return Function(`"use strict"; return (${expr})`)();
  }
  throw new Error('Cannot parse captcha challenge');
}

async function postReplyMoltbook(config, postId, replyText) {
  const headers = {
    'Authorization': `Bearer ${config.apiKey}`,
    'Content-Type': 'application/json'
  };

  // Step 1: Submit comment
  const response = await fetch('https://www.moltbook.com/api/v1/comments', {
    method: 'POST',
    headers,
    body: JSON.stringify({ post_id: postId, content: replyText })
  });

  const data = await response.json();
  
  if (data.verification) {
    // Step 2: Solve captcha
    const answer = solveMathChallenge(data.verification.challenge);
    
    // Step 3: Verify
    await fetch('https://www.moltbook.com/api/v1/verify', {
      method: 'POST',
      headers,
      body: JSON.stringify({
        verification_code: data.verification.code,
        answer: answer.toFixed(2)
      })
    });
  }

  return { success: true, commentId: data.id || 'pending' };
}

// ============================================
// REPLY GENERATION
// ============================================

function generateReply(post, persona) {
  // Analyze post content
  const text = post.text.toLowerCase();
  const topics = {
    technical: /deploy|contract|gas|rpc|api|code|build|ship|debug/i.test(text),
    defi: /defi|yield|liquidity|swap|pool|stake/i.test(text),
    community: /gm|wagmi|lfg|builder|fren|anon/i.test(text),
    question: /\?|how|what|why|when|where/i.test(text),
    announcement: /just|launch|ship|release|live|new/i.test(text)
  };

  // Build reply based on persona and topics
  let reply = '';
  const { toneBalance, signatureEmoji, phrases } = persona;
  
  if (topics.question && toneBalance.educational >= 50) {
    // Educational response to question
    reply = generateEducationalReply(post, persona);
  } else if (topics.announcement) {
    // Celebrate with substance
    reply = generateCelebrationReply(post, persona);
  } else if (topics.community) {
    // Community vibes
    reply = generateCommunityReply(post, persona);
  } else {
    // Default: add specific value
    reply = generateDefaultReply(post, persona);
  }

  // Add signature emoji
  if (!reply.includes(signatureEmoji)) {
    reply = reply.trim() + ' ' + signatureEmoji;
  }

  return reply;
}

function generateEducationalReply(post, persona) {
  const templates = [
    "Good question. Here's what I've found:\n\n[insight]\n\nWhat specific part are you stuck on?",
    "Few things to consider:\n\n1. [point1]\n2. [point2]\n\nHappy to dig deeper if needed.",
    "[Direct answer]\n\nThe key is [key insight]. What's your use case?"
  ];
  
  return templates[Math.floor(Math.random() * templates.length)]
    .replace('[insight]', 'Check the docs for specifics, but the pattern that works is...')
    .replace('[point1]', 'Start simple, iterate fast')
    .replace('[point2]', 'Test on testnet first')
    .replace('[Direct answer]', 'Short answer: yes, but with caveats')
    .replace('[key insight]', 'understanding the tradeoffs');
}

function generateCelebrationReply(post, persona) {
  const phrases = persona.phrases || ['ships > talks', 'based', 'lfg'];
  const phrase = phrases[Math.floor(Math.random() * phrases.length)];
  
  return `Shipping is the hardest part. Respect.\n\nWhat's the next milestone? ${phrase}`;
}

function generateCommunityReply(post, persona) {
  const greetings = ['gm', 'ser', 'anon'];
  const greeting = greetings[Math.floor(Math.random() * greetings.length)];
  
  return `${greeting}! The builder energy is real.\n\nWhat are you working on?`;
}

function generateDefaultReply(post, persona) {
  return `Interesting angle. What led you to this take?\n\nCurious to hear more context.`;
}

// ============================================
// MAIN ENGAGEMENT FLOW
// ============================================

async function engage(platform, config, state, persona) {
  console.log(`\n🎯 Engaging on ${platform}...`);
  
  const platformConfig = config.platforms[platform];
  if (!platformConfig?.enabled) {
    console.log(`⏭️  ${platform} is disabled, skipping.`);
    return null;
  }

  // Fetch trending
  console.log(`📥 Fetching trending...`);
  let trending;
  switch (platform) {
    case 'twitter':
      trending = await fetchTrendingTwitter(platformConfig, config.settings.trendingLimit);
      break;
    case 'farcaster':
      trending = await fetchTrendingFarcaster(platformConfig, config.settings.trendingLimit);
      break;
    case 'moltbook':
      trending = await fetchTrendingMoltbook(platformConfig, config.settings.trendingLimit);
      break;
  }
  
  console.log(`📊 Found ${trending.length} trending posts`);

  // Filter already replied
  const replied = state.repliedPosts[platform] || [];
  const unreplied = trending.filter(post => !replied.includes(post.id));
  
  console.log(`🔍 ${unreplied.length} unreplied posts`);
  
  if (unreplied.length === 0) {
    console.log(`✅ All trending already replied, skipping.`);
    return null;
  }

  // Pick random unreplied
  const target = unreplied[Math.floor(Math.random() * unreplied.length)];
  console.log(`🎲 Selected: @${target.authorUsername}`);
  console.log(`📝 "${target.text.substring(0, 80)}..."`);

  // Generate reply
  const replyText = generateReply(target, persona);
  console.log(`💬 Reply: "${replyText.substring(0, 80)}..."`);

  // Post reply
  console.log(`📤 Posting reply...`);
  let result;
  switch (platform) {
    case 'twitter':
      result = await postReplyTwitter(platformConfig, target.id, replyText);
      break;
    case 'farcaster':
      result = await postReplyFarcaster(platformConfig, target, replyText);
      break;
    case 'moltbook':
      result = await postReplyMoltbook(platformConfig, target.id, replyText);
      break;
  }

  // Update state
  state.repliedPosts[platform].push(target.id);
  state.stats.totalReplies++;
  state.stats.byPlatform[platform]++;

  console.log(`✅ Reply posted successfully!`);
  
  return {
    platform,
    target: { id: target.id, author: target.authorUsername, text: target.text },
    reply: replyText,
    result
  };
}

// ============================================
// CLI
// ============================================

async function main() {
  const args = process.argv.slice(2);
  const platformArg = args.find(a => a.startsWith('--platform='))?.split('=')[1];
  const allPlatforms = args.includes('--all');
  const configPath = args.find(a => a.startsWith('--config='))?.split('=')[1] || 'config.json';
  
  if (!platformArg && !allPlatforms) {
    console.log('Usage:');
    console.log('  node engage.mjs --platform=twitter');
    console.log('  node engage.mjs --platform=farcaster');
    console.log('  node engage.mjs --platform=moltbook');
    console.log('  node engage.mjs --all');
    console.log('  node engage.mjs --all --config=my-config.json');
    process.exit(1);
  }

  // Load config
  const config = loadConfig(configPath);
  const stateFile = config.settings?.stateFile || 'engagement-state.json';
  const state = loadState(stateFile);
  const persona = config.persona;

  console.log('🤖 Multi-Channel Engagement Agent');
  console.log(`📁 Config: ${configPath}`);
  console.log(`💾 State: ${stateFile}`);
  console.log(`🎭 Persona: ${persona.name}`);

  const platforms = allPlatforms 
    ? ['twitter', 'farcaster', 'moltbook'].filter(p => config.platforms[p]?.enabled)
    : [platformArg];

  const results = [];
  
  for (const platform of platforms) {
    try {
      const result = await engage(platform, config, state, persona);
      if (result) results.push(result);
    } catch (error) {
      console.error(`❌ Error on ${platform}: ${error.message}`);
    }
  }

  // Save state
  saveState(stateFile, state);
  console.log(`\n💾 State saved (${state.stats.totalReplies} total replies)`);

  // Summary
  if (results.length > 0) {
    console.log('\n📊 Summary:');
    results.forEach(r => {
      console.log(`  ${r.platform}: Replied to @${r.target.author}`);
    });
  }
}

main().catch(console.error);
