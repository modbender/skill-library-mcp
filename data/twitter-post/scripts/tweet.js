#!/usr/bin/env node
/**
 * Twitter/X Official API v2 — Post tweets via OAuth 1.0a
 *
 * Usage:
 *   node tweet.js "Your tweet text here"
 *   node tweet.js --reply-to 123456789 "Reply text"
 *   node tweet.js --quote 123456789 "Quote tweet text"
 *   node tweet.js --thread "First tweet" "Second tweet" "Third tweet"
 *
 * Environment variables (required):
 *   TWITTER_CONSUMER_KEY        - OAuth 1.0a Consumer Key (API Key)
 *   TWITTER_CONSUMER_SECRET     - OAuth 1.0a Consumer Secret (API Key Secret)
 *   TWITTER_ACCESS_TOKEN        - OAuth 1.0a Access Token
 *   TWITTER_ACCESS_TOKEN_SECRET - OAuth 1.0a Access Token Secret
 *
 * Optional:
 *   HTTPS_PROXY                 - HTTP proxy (e.g. http://127.0.0.1:7897)
 *   TWITTER_DRY_RUN=1           - Print tweet without sending
 *
 * Output (JSON): { ok, id, url, remaining, limit }
 */
const crypto = require('crypto');
const https = require('https');
const http = require('http');
const tls = require('tls');
const { URL } = require('url');

// --- Config ---
const CK  = process.env.TWITTER_CONSUMER_KEY;
const CS  = process.env.TWITTER_CONSUMER_SECRET;
const AT  = process.env.TWITTER_ACCESS_TOKEN;
const ATS = process.env.TWITTER_ACCESS_TOKEN_SECRET;
const PROXY = process.env.HTTPS_PROXY || process.env.https_proxy || '';
const DRY = process.env.TWITTER_DRY_RUN === '1';

function die(msg) { console.error(JSON.stringify({ ok: false, error: msg })); process.exit(1); }
if (!CK || !CS || !AT || !ATS) die('Missing TWITTER_CONSUMER_KEY / TWITTER_CONSUMER_SECRET / TWITTER_ACCESS_TOKEN / TWITTER_ACCESS_TOKEN_SECRET');

// --- OAuth 1.0a ---
function penc(s) {
  return encodeURIComponent(s).replace(/[!'()*]/g, c => '%' + c.charCodeAt(0).toString(16).toUpperCase());
}

function oauthSign(method, url, params) {
  const paramStr = Object.keys(params).sort().map(k => `${penc(k)}=${penc(params[k])}`).join('&');
  const baseStr = `${method}&${penc(url)}&${penc(paramStr)}`;
  const sigKey = `${penc(CS)}&${penc(ATS)}`;
  return crypto.createHmac('sha1', sigKey).update(baseStr).digest('base64');
}

function authHeader(method, url) {
  const p = {
    oauth_consumer_key: CK,
    oauth_nonce: crypto.randomBytes(32).toString('hex'),
    oauth_signature_method: 'HMAC-SHA1',
    oauth_timestamp: Math.floor(Date.now() / 1000).toString(),
    oauth_token: AT,
    oauth_version: '1.0'
  };
  p.oauth_signature = oauthSign(method, url, p);
  return 'OAuth ' + Object.keys(p).map(k => `${penc(k)}="${penc(p[k])}"`).join(', ');
}

// --- HTTP with optional proxy ---
function request(method, urlStr, body) {
  return new Promise((resolve, reject) => {
    const u = new URL(urlStr);
    const bodyStr = body ? JSON.stringify(body) : '';
    const headers = { 'Authorization': authHeader(method, urlStr) };
    if (body) {
      headers['Content-Type'] = 'application/json';
      headers['Content-Length'] = Buffer.byteLength(bodyStr);
    }
    const opts = { hostname: u.hostname, path: u.pathname + u.search, method, headers };

    function doRequest(socket) {
      if (socket) { opts.socket = socket; opts.createConnection = () => socket; }
      const req = https.request(opts, resp => {
        let d = ''; resp.on('data', c => d += c);
        resp.on('end', () => {
          try { resolve({ status: resp.statusCode, data: JSON.parse(d), headers: resp.headers }); }
          catch { resolve({ status: resp.statusCode, data: d, headers: resp.headers }); }
        });
      });
      req.on('error', reject);
      if (bodyStr) req.write(bodyStr);
      req.end();
    }

    if (PROXY) {
      const pu = new URL(PROXY);
      const proxyReq = http.request({
        hostname: pu.hostname, port: pu.port,
        method: 'CONNECT', path: `${u.hostname}:443`
      });
      proxyReq.on('connect', (res, socket) => {
        if (res.statusCode !== 200) return reject(new Error(`Proxy CONNECT failed: ${res.statusCode}`));
        const tlsSocket = tls.connect({ socket, servername: u.hostname }, () => doRequest(tlsSocket));
        tlsSocket.on('error', reject);
      });
      proxyReq.on('error', reject);
      proxyReq.end();
    } else {
      doRequest(null);
    }
  });
}

// --- Tweet weight (Twitter's weighted char count) ---
function tweetWeight(text) {
  let w = 0;
  for (const ch of text) {
    w += (ch.codePointAt(0) > 0x1FFF) ? 2 : 1;
  }
  // URLs count as 23 chars
  const urlRegex = /https?:\/\/\S+/g;
  const urls = text.match(urlRegex) || [];
  for (const url of urls) {
    let urlWeight = 0;
    for (const ch of url) urlWeight += (ch.codePointAt(0) > 0x1FFF) ? 2 : 1;
    w = w - urlWeight + 23;
  }
  return w;
}

// --- Post a single tweet ---
async function postTweet(text, opts = {}) {
  const weight = tweetWeight(text);
  if (weight > 280) die(`Tweet too long: ${weight}/280 weighted chars`);

  if (DRY) {
    console.error(`[DRY RUN] ${weight}/280: ${text}`);
    return { ok: true, id: 'dry-run', url: '#', remaining: '-', limit: '-' };
  }

  const body = { text };
  if (opts.replyTo) body.reply = { in_reply_to_tweet_id: opts.replyTo };
  if (opts.quoteTweetId) body.quote_tweet_id = opts.quoteTweetId;

  const r = await request('POST', 'https://api.twitter.com/2/tweets', body);
  if (r.status === 201) {
    const id = r.data.data.id;
    return {
      ok: true,
      id,
      url: `https://x.com/i/status/${id}`,
      remaining: r.headers['x-rate-limit-remaining'],
      limit: r.headers['x-rate-limit-limit']
    };
  }
  die(`API error ${r.status}: ${JSON.stringify(r.data)}`);
}

// --- CLI ---
async function main() {
  const args = process.argv.slice(2);
  let replyTo = null, quoteTweetId = null, thread = false;
  const texts = [];

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--reply-to' && args[i + 1]) { replyTo = args[++i]; continue; }
    if (args[i] === '--quote' && args[i + 1]) { quoteTweetId = args[++i]; continue; }
    if (args[i] === '--thread') { thread = true; continue; }
    if (args[i] === '--help' || args[i] === '-h') {
      console.log(`Usage: node tweet.js [options] "text" ["text2" ...]
Options:
  --reply-to <id>   Reply to a tweet
  --quote <id>      Quote tweet
  --thread           Post multiple args as a thread
  --help             Show this help

Env vars: TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
Optional: HTTPS_PROXY, TWITTER_DRY_RUN=1`);
      process.exit(0);
    }
    texts.push(args[i]);
  }

  if (texts.length === 0) die('No tweet text provided. Use --help for usage.');

  if (thread && texts.length > 1) {
    // Post thread
    const results = [];
    let prevId = replyTo;
    for (const t of texts) {
      const r = await postTweet(t, { replyTo: prevId, quoteTweetId: results.length === 0 ? quoteTweetId : undefined });
      results.push(r);
      prevId = r.id;
    }
    console.log(JSON.stringify({ ok: true, thread: results }));
  } else {
    const r = await postTweet(texts.join(' '), { replyTo, quoteTweetId });
    console.log(JSON.stringify(r));
  }
}

main().catch(e => die(e.message));
