#!/usr/bin/env node

/**
 * OpenClaw X/Twitter Skill — CLI for posting tweets, threads, and media via X API v2.
 *
 * @author Abdelkrim BOUJRAF <abdelkrim@alt-f1.be>
 * @license MIT
 * @see https://www.alt-f1.be
 */

import { readFileSync, statSync, realpathSync } from 'node:fs';
import { basename, resolve } from 'node:path';
import { homedir, tmpdir } from 'node:os';
import { createHmac, randomBytes } from 'node:crypto';
import { config } from 'dotenv';
import { Command } from 'commander';

// ── Config ──────────────────────────────────────────────────────────────────

config();

let _cfg;
function getCfg() {
  if (!_cfg) {
    _cfg = {
      consumerKey:      env('X_CONSUMER_KEY'),
      consumerSecret:   env('X_CONSUMER_SECRET'),
      accessToken:      env('X_ACCESS_TOKEN'),
      accessTokenSecret: env('X_ACCESS_TOKEN_SECRET'),
    };
  }
  return _cfg;
}

function env(key) {
  const v = process.env[key];
  if (!v) {
    console.error(`ERROR: Missing required env var ${key}. See .env.example`);
    process.exit(1);
  }
  return v;
}

// ── Path validation (LFI protection) ────────────────────────────────────────

const BLOCKED_SEGMENTS = [
  '/.ssh/', '/.gnupg/', '/.env', '/.git/config', '/.netrc',
  '/etc/', '/proc/', '/sys/', '/dev/',
];

const ALLOWED_MEDIA_EXT = new Set(['jpg', 'jpeg', 'png', 'gif', 'webp', 'mp4']);

function validateFilePath(filePath, { mediaOnly = false } = {}) {
  const resolved = resolve(filePath);

  // Resolve symlinks to real location
  let real;
  try {
    real = realpathSync(resolved);
  } catch (e) {
    if (e.code === 'ENOENT') throw new Error(`File not found: ${filePath}`);
    throw e;
  }

  // Must be under home, cwd, or tmp
  const allowed = [homedir(), process.cwd(), tmpdir()];
  const isUnderAllowed = allowed.some(base => real.startsWith(base + '/') || real === base);
  if (!isUnderAllowed) {
    throw new Error(`Security: file path must be under home, working directory, or tmp — got: ${filePath}`);
  }

  // Block sensitive paths
  const lower = real.toLowerCase();
  for (const seg of BLOCKED_SEGMENTS) {
    if (lower.includes(seg)) {
      throw new Error(`Security: access to ${seg.replace(/\//g, '')} paths is blocked — got: ${filePath}`);
    }
  }

  // Extension check for media files
  if (mediaOnly) {
    const ext = basename(real).toLowerCase().split('.').pop();
    if (!ALLOWED_MEDIA_EXT.has(ext)) {
      throw new Error(`Security: invalid media extension '.${ext}' — allowed: ${[...ALLOWED_MEDIA_EXT].join(', ')}`);
    }
  }

  return real;
}

// ── OAuth 1.0a signing ──────────────────────────────────────────────────────

function oauthSign(method, url, params = {}) {
  const cfg = getCfg();
  const timestamp = Math.floor(Date.now() / 1000).toString();
  const nonce = randomBytes(16).toString('hex');

  const oauthParams = {
    oauth_consumer_key: cfg.consumerKey,
    oauth_nonce: nonce,
    oauth_signature_method: 'HMAC-SHA1',
    oauth_timestamp: timestamp,
    oauth_token: cfg.accessToken,
    oauth_version: '1.0',
  };

  // Combine oauth params + request params for signature base
  const allParams = { ...oauthParams, ...params };
  const paramString = Object.keys(allParams)
    .sort()
    .map(k => `${encodeRFC3986(k)}=${encodeRFC3986(allParams[k])}`)
    .join('&');

  const signatureBase = [
    method.toUpperCase(),
    encodeRFC3986(url),
    encodeRFC3986(paramString),
  ].join('&');

  const signingKey = `${encodeRFC3986(cfg.consumerSecret)}&${encodeRFC3986(cfg.accessTokenSecret)}`;
  const signature = createHmac('sha1', signingKey)
    .update(signatureBase)
    .digest('base64');

  oauthParams.oauth_signature = signature;

  const authHeader = 'OAuth ' + Object.keys(oauthParams)
    .sort()
    .map(k => `${encodeRFC3986(k)}="${encodeRFC3986(oauthParams[k])}"`)
    .join(', ');

  return authHeader;
}

function encodeRFC3986(str) {
  return encodeURIComponent(String(str))
    .replace(/!/g, '%21')
    .replace(/\*/g, '%2A')
    .replace(/'/g, '%27')
    .replace(/\(/g, '%28')
    .replace(/\)/g, '%29');
}

// ── API helpers ─────────────────────────────────────────────────────────────

const API_BASE = 'https://api.x.com/2';
const UPLOAD_BASE = 'https://upload.twitter.com/1.1';

async function apiRequest(method, url, body = null, useOAuth1 = true) {
  const headers = { 'Content-Type': 'application/json' };

  if (useOAuth1) {
    headers['Authorization'] = oauthSign(method, url);
  } else {
    headers['Authorization'] = `Bearer ${getCfg().bearerToken}`;
  }

  const opts = { method, headers };
  if (body) opts.body = JSON.stringify(body);

  const resp = await fetch(url, opts);
  const text = await resp.text();

  let data;
  try { data = JSON.parse(text); } catch { data = text; }

  if (!resp.ok) {
    const errMsg = data?.detail || data?.errors?.[0]?.message || data?.title || text;
    throw new Error(`X API ${resp.status}: ${errMsg}`);
  }

  return data;
}

async function uploadMedia(filePath) {
  const safePath = validateFilePath(filePath, { mediaOnly: true });
  const cfg = getCfg();
  const fileBuffer = readFileSync(safePath);
  const stat = statSync(safePath);
  const filename = basename(filePath);

  if (stat.size > 5 * 1024 * 1024) {
    throw new Error(`File too large (${(stat.size / 1048576).toFixed(1)} MB > 5 MB limit for images)`);
  }

  // Determine MIME type
  const ext = filename.toLowerCase().split('.').pop();
  const mimeMap = {
    jpg: 'image/jpeg', jpeg: 'image/jpeg', png: 'image/png',
    gif: 'image/gif', webp: 'image/webp', mp4: 'video/mp4',
  };
  const mimeType = mimeMap[ext] || 'application/octet-stream';

  // Use v1.1 media upload (multipart form)
  const url = `${UPLOAD_BASE}/media/upload.json`;

  const boundary = '----OpenClawBoundary' + randomBytes(8).toString('hex');
  const bodyParts = [];

  // media_data field (base64)
  bodyParts.push(`--${boundary}\r\n`);
  bodyParts.push(`Content-Disposition: form-data; name="media_data"\r\n\r\n`);
  bodyParts.push(fileBuffer.toString('base64'));
  bodyParts.push('\r\n');

  // media_category
  const category = mimeType.startsWith('video') ? 'tweet_video' : 'tweet_image';
  bodyParts.push(`--${boundary}\r\n`);
  bodyParts.push(`Content-Disposition: form-data; name="media_category"\r\n\r\n`);
  bodyParts.push(category);
  bodyParts.push('\r\n');

  bodyParts.push(`--${boundary}--\r\n`);

  const fullBody = bodyParts.join('');

  const authHeader = oauthSign('POST', url);

  const resp = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': authHeader,
      'Content-Type': `multipart/form-data; boundary=${boundary}`,
    },
    body: fullBody,
  });

  const text = await resp.text();
  let data;
  try { data = JSON.parse(text); } catch { data = text; }

  if (!resp.ok) {
    throw new Error(`Media upload failed (${resp.status}): ${JSON.stringify(data)}`);
  }

  return data.media_id_string;
}

// ── Commands ────────────────────────────────────────────────────────────────

async function cmdTweet(text, options) {
  const body = { text };

  // Handle media
  if (options.media) {
    const mediaId = await uploadMedia(options.media);
    body.media = { media_ids: [mediaId] };
    console.log(`📎 Media uploaded (ID: ${mediaId})`);
  }

  // Handle reply
  if (options.reply) {
    body.reply = { in_reply_to_tweet_id: options.reply };
  }

  const result = await apiRequest('POST', `${API_BASE}/tweets`, body);
  const tweetId = result.data?.id;
  console.log(`✅ Tweet posted!`);
  console.log(`   ID: ${tweetId}`);
  console.log(`   URL: https://x.com/i/status/${tweetId}`);
  return tweetId;
}

async function cmdThread(options) {
  let tweets;

  if (options.file) {
    const safePath = validateFilePath(options.file);
    const content = readFileSync(safePath, 'utf-8');
    tweets = content.split(/\n---\n/).map(t => t.trim()).filter(Boolean);
  } else if (options.tweets) {
    tweets = options.tweets;
  } else {
    console.error('ERROR: Provide --file or tweets as arguments');
    process.exit(1);
  }

  if (tweets.length === 0) {
    console.error('ERROR: No tweets to post');
    process.exit(1);
  }

  if (tweets.length > 25) {
    console.error(`ERROR: Thread too long (${tweets.length} tweets, max 25)`);
    process.exit(1);
  }

  console.log(`🧵 Posting thread (${tweets.length} tweets)...\n`);

  let previousId = null;
  const postedIds = [];

  for (let i = 0; i < tweets.length; i++) {
    const body = { text: tweets[i] };
    if (previousId) {
      body.reply = { in_reply_to_tweet_id: previousId };
    }

    const result = await apiRequest('POST', `${API_BASE}/tweets`, body);
    previousId = result.data?.id;
    postedIds.push(previousId);
    console.log(`  ${i + 1}/${tweets.length} ✅ https://x.com/i/status/${previousId}`);
  }

  console.log(`\n🧵 Thread posted! First tweet: https://x.com/i/status/${postedIds[0]}`);
}

async function cmdVerify() {
  const url = `${API_BASE}/users/me`;
  const headers = {
    'Authorization': oauthSign('GET', url),
  };
  const resp = await fetch(url, { headers });
  const text = await resp.text();
  let result;
  try { result = JSON.parse(text); } catch { throw new Error(text); }
  if (!resp.ok) throw new Error(`X API ${resp.status}: ${result?.detail || result?.title || text}`);
  const user = result.data;
  console.log('✅ Connection verified!\n');
  console.log(`  Name:     ${user.name}`);
  console.log(`  Handle:   @${user.username}`);
  console.log(`  ID:       ${user.id}`);
}

// ── CLI ─────────────────────────────────────────────────────────────────────

const program = new Command();

program
  .name('xpost')
  .description('OpenClaw X/Twitter Skill — post tweets, threads, and media')
  .version('0.1.0');

program
  .command('tweet')
  .description('Post a tweet')
  .argument('<text>', 'Tweet text (max 280 chars)')
  .option('-m, --media <file>', 'Attach image (jpg/png/gif/webp, max 5MB)')
  .option('-r, --reply <tweet_id>', 'Reply to a tweet')
  .action(wrap(cmdTweet));

program
  .command('thread')
  .description('Post a thread (multiple tweets)')
  .argument('[tweets...]', 'Tweet texts (each becomes a tweet in the thread)')
  .option('-f, --file <file>', 'File with tweets separated by ---')
  .action(wrap(async (tweets, options) => {
    options.tweets = tweets.length > 0 ? tweets : null;
    await cmdThread(options);
  }));

program
  .command('verify')
  .description('Verify API connection and show account info')
  .action(wrap(cmdVerify));

function wrap(fn) {
  return async (...args) => {
    try {
      await fn(...args);
    } catch (err) {
      console.error(`ERROR: ${err.message}`);
      process.exit(1);
    }
  };
}

program.parse();
