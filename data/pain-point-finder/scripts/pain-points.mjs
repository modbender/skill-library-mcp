#!/usr/bin/env node

/**
 * pain-points.mjs
 *
 * Pain point discovery on Reddit via PullPush API.
 * Subcommands: discover, scan, deep-dive
 *
 * All output is JSON to stdout:
 *   { ok: true,  data: { ... } }
 *   { ok: false, error: { message, details? } }
 *
 * Progress/debug messages go to stderr.
 */

import https from 'node:https';

// ─── constants ───────────────────────────────────────────────────────────────

const PULLPUSH_HOST = 'api.pullpush.io';
const SUBMISSION_PATH = '/reddit/search/submission/';
const COMMENT_PATH = '/reddit/search/comment/';

const MIN_DELAY_MS = 1000;
const JITTER_MS = 200;
const MAX_PER_MIN = 30;
const MAX_PER_RUN = 300;
const REQUEST_TIMEOUT_MS = 15000;

const MAX_RETRIES_429 = 5;
const MAX_RETRIES_5XX = 3;
const MAX_RETRIES_TIMEOUT = 1;
const BACKOFF_BASE_MS = 2000;

const PAGE_SIZE = 100; // PullPush hard cap

// ─── pain signal keywords ────────────────────────────────────────────────────

const PAIN_SIGNALS = {
  frustration: [
    'frustrated', 'frustrating', 'annoying', 'annoyed',
    'fed up', 'sick of', 'tired of', 'giving up', 'nightmare',
    'terrible', 'awful', 'broken', 'buggy', 'unusable',
    'horrible', 'worst', 'garbage', 'trash', 'joke',
    'hate', 'ruining', 'killing', 'destroying',
  ],
  desire: [
    'wish there was', 'looking for', 'alternative to',
    'switched from', 'better than', 'anything else',
    'does anyone know', 'recommendations for',
    'is there a', 'need something',
  ],
  cost: [
    'too expensive', 'price hike', 'overpriced', 'not worth',
    'hidden fees', 'ripoff', 'rip off', 'gouging',
    'cost went up', 'raised prices',
  ],
  agreement: [
    'same here', 'me too', 'can confirm', 'exactly this',
    'this is why', 'i had the same', 'happened to me',
    'i agree', 'so true', "couldn't agree more",
    'yep same', 'deal breaker for me too',
  ],
  solution: [
    'i switched to', 'i ended up using', 'the workaround is',
    'i built my own', 'i just use', 'try using',
    'we moved to', 'what worked for me', 'i found that',
    'we use', 'i use', 'we went with', 'i went with',
    'check out', 'look into', 'have you tried',
  ],
};

const SCAN_QUERIES = {
  frustration: [
    'frustrated', 'nightmare', 'terrible', 'unusable', 'hate',
  ],
  desire: [
    'alternative', 'looking for', 'switched from', 'wish',
  ],
  cost: [
    'expensive', 'overpriced', 'not worth',
  ],
};

const PAIN_FLAIRS = new Set([
  'rant', 'complaint', 'help', 'vent', 'venting', 'frustrated',
  'issue', 'problem', 'bug', 'support',
]);

// ─── rate limiter (token bucket) ─────────────────────────────────────────────

class RateLimiter {
  constructor() {
    this.timestamps = [];
    this.totalRequests = 0;
    this.lastRequestAt = 0;
  }

  async wait() {
    // hard cap per run
    if (this.totalRequests >= MAX_PER_RUN) {
      throw new Error(`Rate limit: max ${MAX_PER_RUN} requests per run exceeded`);
    }

    // per-minute cap
    const now = Date.now();
    this.timestamps = this.timestamps.filter(t => now - t < 60000);
    if (this.timestamps.length >= MAX_PER_MIN) {
      const oldest = this.timestamps[0];
      const waitMs = 60000 - (now - oldest) + 100;
      log(`[rate] per-minute cap hit, sleeping ${waitMs}ms`);
      await sleep(waitMs);
    }

    // min delay between requests
    const elapsed = Date.now() - this.lastRequestAt;
    const minWait = MIN_DELAY_MS + Math.floor(Math.random() * JITTER_MS);
    if (elapsed < minWait) {
      await sleep(minWait - elapsed);
    }

    this.timestamps.push(Date.now());
    this.lastRequestAt = Date.now();
    this.totalRequests++;
  }

  get count() {
    return this.totalRequests;
  }
}

const rateLimiter = new RateLimiter();

// ─── helpers ─────────────────────────────────────────────────────────────────

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

function log(...args) {
  process.stderr.write(args.join(' ') + '\n');
}

function ok(data) {
  console.log(JSON.stringify({ ok: true, data }, null, 2));
}

function fail(message, details) {
  console.log(JSON.stringify({ ok: false, error: { message, details } }, null, 2));
  process.exit(1);
}

function unixNow() {
  return Math.floor(Date.now() / 1000);
}

function daysAgoUnix(days) {
  return unixNow() - days * 86400;
}

function utcToDate(utc) {
  return new Date(utc * 1000).toISOString().split('T')[0];
}

function excerpt(text, maxLen = 200) {
  if (!text) return '';
  const clean = text.replace(/\s+/g, ' ').trim();
  if (clean.length <= maxLen) return clean;
  return clean.slice(0, maxLen).trim() + '...';
}

// ─── HTTP client with retry ──────────────────────────────────────────────────

function httpGet(urlPath, params) {
  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== '') {
      qs.set(k, String(v));
    }
  }
  const fullPath = `${urlPath}?${qs.toString()}`;

  return new Promise((resolve, reject) => {
    const req = https.get({
      hostname: PULLPUSH_HOST,
      path: fullPath,
      headers: { 'User-Agent': 'openclaw-pain-points/1.0' },
      timeout: REQUEST_TIMEOUT_MS,
    }, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        if (res.statusCode === 200) {
          try {
            resolve(JSON.parse(body));
          } catch {
            reject(new Error(`Non-JSON response: ${body.slice(0, 200)}`));
          }
        } else {
          const err = new Error(`HTTP ${res.statusCode}`);
          err.statusCode = res.statusCode;
          reject(err);
        }
      });
    });
    req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });
    req.on('error', reject);
  });
}

async function fetchWithRetry(urlPath, params) {
  let lastErr;

  const maxRetries = MAX_RETRIES_429; // use highest as outer bound
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      await rateLimiter.wait();
      return await httpGet(urlPath, params);
    } catch (err) {
      lastErr = err;
      const code = err.statusCode || 0;
      const isTimeout = err.message === 'timeout';
      const is429 = code === 429;
      const is5xx = code >= 500 && code < 600;
      const is403 = code === 403;

      if (is403) {
        log(`[http] 403 blocked — stopping`);
        throw err;
      }

      let maxForType;
      if (is429) maxForType = MAX_RETRIES_429;
      else if (is5xx) maxForType = MAX_RETRIES_5XX;
      else if (isTimeout) maxForType = MAX_RETRIES_TIMEOUT;
      else maxForType = 1; // network errors

      if (attempt >= maxForType) break;

      const backoff = BACKOFF_BASE_MS * Math.pow(2, attempt);
      log(`[http] ${err.message} — retry ${attempt + 1} in ${backoff}ms`);
      await sleep(backoff);
    }
  }

  throw lastErr;
}

// ─── PullPush API helpers ────────────────────────────────────────────────────

async function searchSubmissions(params) {
  const result = await fetchWithRetry(SUBMISSION_PATH, {
    size: PAGE_SIZE,
    ...params,
  });
  return result?.data || [];
}

async function searchComments(params) {
  const result = await fetchWithRetry(COMMENT_PATH, {
    size: PAGE_SIZE,
    ...params,
  });
  return result?.data || [];
}

async function paginateSubmissions(params, maxPages = 1) {
  const all = [];
  let currentParams = { ...params };

  for (let page = 0; page < maxPages; page++) {
    let posts;
    try {
      posts = await searchSubmissions(currentParams);
    } catch (err) {
      log(`[paginate] page ${page + 1} failed: ${err.message} — returning partial`);
      break;
    }

    if (!posts.length) break;
    all.push(...posts);

    // set `before` to last post's created_utc for next page
    const last = posts[posts.length - 1];
    const lastUtc = last.created_utc;
    if (!lastUtc) break;
    currentParams = { ...currentParams, before: Math.floor(lastUtc) };
  }

  return all;
}

async function paginateComments(linkId, maxComments = 100) {
  const all = [];
  let before = null;
  const maxPages = Math.ceil(maxComments / PAGE_SIZE);

  for (let page = 0; page < maxPages; page++) {
    const params = { link_id: linkId, size: PAGE_SIZE };
    if (before) params.before = before;

    let comments;
    try {
      comments = await searchComments(params);
    } catch (err) {
      log(`[comments] page ${page + 1} failed: ${err.message} — returning partial`);
      break;
    }

    if (!comments.length) break;
    all.push(...comments);

    const last = comments[comments.length - 1];
    if (!last.created_utc) break;
    before = Math.floor(last.created_utc);
  }

  return all.slice(0, maxComments);
}

// ─── pain scoring ────────────────────────────────────────────────────────────

function matchSignals(text, category) {
  if (!text) return [];
  const lower = text.toLowerCase();
  return PAIN_SIGNALS[category].filter(kw => lower.includes(kw));
}

function computePainScore(post) {
  const title = (post.title || '').toLowerCase();
  const body = (post.selftext || '').toLowerCase();

  const titleSignals = [
    ...matchSignals(title, 'frustration'),
    ...matchSignals(title, 'desire'),
    ...matchSignals(title, 'cost'),
  ];
  const bodySignals = [
    ...matchSignals(body, 'frustration'),
    ...matchSignals(body, 'desire'),
    ...matchSignals(body, 'cost'),
  ];

  let score = 0;
  score += titleSignals.length * 2.0;
  score += bodySignals.length * 1.0;
  score += Math.log2((post.num_comments || 0) + 1) * 0.5;
  score += Math.log2((post.score || 0) + 1) * 0.3;

  if (post.upvote_ratio && post.upvote_ratio > 0.90) score += 1.0;

  const flair = (post.link_flair_text || '').toLowerCase();
  if (PAIN_FLAIRS.has(flair)) score += 1.0;

  return Math.round(score * 10) / 10;
}

function analyzeComments(comments) {
  let agreementCount = 0;
  const agreements = [];
  const solutions = [];
  const mentionedTools = new Set();
  const topQuotes = [];

  const sorted = [...comments].sort((a, b) => (b.score || 0) - (a.score || 0));

  for (const c of sorted) {
    const body = (c.body || '').trim();
    if (!body || body === '[deleted]' || body === '[removed]') continue;

    const agreeMatches = matchSignals(body, 'agreement');
    if (agreeMatches.length > 0) {
      agreementCount++;
      agreements.push({ body: excerpt(body, 150), score: c.score || 0, signals: agreeMatches });
    }

    const solutionMatches = matchSignals(body, 'solution');
    if (solutionMatches.length > 0) {
      solutions.push({ body: excerpt(body, 200), score: c.score || 0, signals: solutionMatches });

      // extract tool names: look for capitalized words after solution keywords
      const TOOL_NOISE = new Set([
        'I', 'It', 'The', 'This', 'That', 'My', 'We', 'They', 'But', 'And',
        'Or', 'So', 'If', 'Is', 'Was', 'Are', 'Not', 'For', 'You', 'Your',
        'Just', 'Also', 'Been', 'Have', 'Has', 'Had', 'Very', 'Really',
        'MIL', 'DIY', 'OP', 'PSA', 'TBH', 'IMO', 'FWIW', 'TIL',
      ]);
      const lower = body.toLowerCase();
      for (const kw of solutionMatches) {
        const idx = lower.indexOf(kw);
        if (idx >= 0) {
          const after = body.slice(idx + kw.length, idx + kw.length + 50);
          const toolMatch = after.match(/\s+([A-Z][a-zA-Z0-9]+(?:\s[A-Z][a-zA-Z0-9]+)?)/);
          if (toolMatch) {
            const name = toolMatch[1].trim();
            if (!TOOL_NOISE.has(name) && name.length > 1) {
              mentionedTools.add(name);
            }
          }
        }
      }
    }

    // top quotes: high-score comments with pain signals
    const painMatches = [
      ...matchSignals(body, 'frustration'),
      ...matchSignals(body, 'desire'),
      ...matchSignals(body, 'cost'),
    ];
    if (painMatches.length > 0 && (c.score || 0) >= 2) {
      topQuotes.push({ body: excerpt(body, 200), score: c.score || 0, signals: painMatches });
    }
  }

  const validComments = comments.filter(c => {
    const b = (c.body || '').trim();
    return b && b !== '[deleted]' && b !== '[removed]';
  });

  const agreementRatio = validComments.length > 0
    ? Math.round((agreementCount / validComments.length) * 100) / 100
    : 0;

  let validationStrength;
  if (agreementRatio > 0.20 && agreementCount >= 10) validationStrength = 'strong';
  else if (agreementRatio > 0.10 && agreementCount >= 5) validationStrength = 'moderate';
  else if (agreementRatio > 0.05 || agreementCount >= 3) validationStrength = 'weak';
  else validationStrength = 'anecdotal';

  return {
    totalComments: validComments.length,
    agreementCount,
    agreementRatio,
    validationStrength,
    topQuotes: topQuotes.slice(0, 5),
    agreements: agreements.slice(0, 5),
    solutionAttempts: solutions.slice(0, 10),
    mentionedTools: [...mentionedTools].slice(0, 15),
  };
}

// ─── subcommand: discover ────────────────────────────────────────────────────

async function cmdDiscover(args) {
  const domain = args.domain;
  if (!domain) fail('--domain is required');

  const limit = args.limit || 10;

  log(`[discover] domain="${domain}", limit=${limit}`);

  // step 1: seed queries
  const seedQueries = [
    `"${domain}"`,
    `"${domain} tool"`,
    `"${domain} software"`,
    `"${domain} app"`,
    `"${domain} alternative"`,
  ];

  const subredditCounts = {};

  for (const q of seedQueries) {
    log(`[discover] seed query: ${q}`);
    let posts;
    try {
      posts = await searchSubmissions({
        q,
        size: PAGE_SIZE,
        score: '>3',
        sort: 'desc',
        sort_type: 'num_comments',
      });
    } catch (err) {
      log(`[discover] seed query failed: ${err.message} — skipping`);
      continue;
    }

    for (const p of posts) {
      const sub = p.subreddit;
      if (!sub) continue;
      if (!subredditCounts[sub]) subredditCounts[sub] = { seedHits: 0, painHits: 0 };
      subredditCounts[sub].seedHits++;
    }
  }

  // step 2: rank by seed frequency, take top candidates
  const candidates = Object.entries(subredditCounts)
    .sort((a, b) => b[1].seedHits - a[1].seedHits)
    .slice(0, limit + 2);

  log(`[discover] ${candidates.length} candidate subreddits found`);

  // step 3: validate with pain queries — count how many return results
  // Use size=1 per query to minimize API load; we only care about existence + score
  const painValidationQueries = [
    'frustrated', 'alternative', 'expensive',
  ];

  for (const [sub, counts] of candidates) {
    for (const pq of painValidationQueries) {
      let posts;
      try {
        posts = await searchSubmissions({
          q: pq,
          subreddit: sub,
          size: 1,
        });
      } catch (err) {
        log(`[discover] validation failed for r/${sub}: ${err.message}`);
        continue;
      }
      // 1 point if any result exists, bonus for high-score results
      if (posts.length > 0) {
        counts.painHits += 1;
        if ((posts[0].score || 0) > 10) counts.painHits += 1;
      }
    }
  }

  // step 4: final ranking
  const ranked = candidates
    .map(([name, counts]) => ({
      name,
      seedHits: counts.seedHits,
      painHits: counts.painHits,
      score: counts.seedHits * 2 + counts.painHits,
    }))
    .sort((a, b) => b.score - a.score)
    .slice(0, limit);

  ok({
    domain,
    subreddits: ranked,
    api_calls: rateLimiter.count,
  });
}

// ─── subcommand: scan ────────────────────────────────────────────────────────

async function cmdScan(args) {
  const subreddits = args.subreddits;
  if (!subreddits || !subreddits.length) fail('--subreddits is required (comma-separated)');

  const days = args.days || 365;
  const minScore = args.minScore || 1;
  const minComments = args.minComments || 3;
  const limit = args.limit || 30;
  const pages = args.pages || 2;
  const domain = args.domain || '';

  const after = daysAgoUnix(days);
  const before = unixNow();

  log(`[scan] subreddits=${subreddits.join(',')}, days=${days}, minScore=${minScore}, minComments=${minComments}`);

  // build query set — unquoted single keywords work best on PullPush
  const queries = [];
  for (const cat of Object.keys(SCAN_QUERIES)) {
    for (const q of SCAN_QUERIES[cat]) {
      queries.push({ q, category: cat });
    }
  }
  // domain-specific queries
  if (domain) {
    queries.push({ q: `${domain} frustrated`, category: 'domain' });
    queries.push({ q: `${domain} terrible`, category: 'domain' });
    queries.push({ q: `${domain} alternative`, category: 'domain' });
  }

  const postsById = new Map();
  let queriesRun = 0;

  for (const sub of subreddits) {
    for (const { q, category } of queries) {
      log(`[scan] r/${sub} q=${q} (${category})`);
      queriesRun++;

      let posts;
      try {
        posts = await paginateSubmissions({
          q,
          subreddit: sub,
          score: `>${minScore}`,
          sort: 'desc',
          sort_type: 'num_comments',
          after,
          before,
        }, pages);
      } catch (err) {
        if (err.statusCode === 403) {
          log(`[scan] 403 blocked — aborting`);
          break;
        }
        log(`[scan] query failed: ${err.message} — skipping`);
        continue;
      }

      for (const p of posts) {
        if (!postsById.has(p.id)) {
          postsById.set(p.id, p);
        }
      }
    }
  }

  log(`[scan] ${postsById.size} unique posts after dedup`);

  // filter and score
  // When --domain is set, boost posts that mention the domain in title/body
  // and penalize those that don't, so generic "alternative" matches sink down
  const domainLower = domain.toLowerCase();
  const domainWords = domainLower.split(/\s+/).filter(w => w.length > 2);

  const scored = [];
  for (const post of postsById.values()) {
    if ((post.num_comments || 0) < minComments) continue;

    let painScore = computePainScore(post);
    // domain relevance boost/penalty
    if (domain) {
      const text = ((post.title || '') + ' ' + (post.selftext || '')).toLowerCase();
      const hasDomain = domainWords.some(w => text.includes(w));
      if (hasDomain) {
        painScore += 3.0;
      } else {
        painScore -= 2.0;
      }
    }

    const titleSignals = [
      ...matchSignals(post.title, 'frustration'),
      ...matchSignals(post.title, 'desire'),
      ...matchSignals(post.title, 'cost'),
    ];

    painScore = Math.round(painScore * 10) / 10;

    scored.push({
      id: post.id,
      title: post.title || '',
      subreddit: post.subreddit || '',
      url: `https://www.reddit.com${post.permalink || ''}`,
      score: post.score || 0,
      num_comments: post.num_comments || 0,
      upvote_ratio: post.upvote_ratio || 0,
      created_utc: post.created_utc || 0,
      date: post.created_utc ? utcToDate(post.created_utc) : null,
      selftext_excerpt: excerpt(post.selftext, 200),
      painScore,
      painSignals: [...new Set(titleSignals)],
      flair: post.link_flair_text || null,
    });
  }

  scored.sort((a, b) => b.painScore - a.painScore);
  const topPosts = scored.slice(0, limit);

  ok({
    posts: topPosts,
    stats: {
      subreddits: subreddits.length,
      queries_run: queriesRun,
      api_calls: rateLimiter.count,
      raw_posts: postsById.size,
      after_filter: topPosts.length,
    },
  });
}

// ─── subcommand: deep-dive ───────────────────────────────────────────────────

async function cmdDeepDive(args) {
  const postIds = [];

  if (args.post) {
    // single post id or URL
    const id = extractPostId(args.post);
    if (!id) fail(`Cannot parse post ID from: ${args.post}`);
    postIds.push(id);
  } else if (args.fromScan) {
    // read scan results from file
    let scanData;
    try {
      const fs = await import('node:fs');
      const raw = fs.readFileSync(args.fromScan, 'utf8');
      scanData = JSON.parse(raw);
    } catch (err) {
      fail(`Cannot read scan file: ${err.message}`);
    }

    const posts = scanData?.data?.posts || scanData?.posts || [];
    const top = args.top || 10;
    for (const p of posts.slice(0, top)) {
      if (p.id) postIds.push(p.id);
    }
  } else if (args.fromStdin) {
    // read from stdin
    let input = '';
    const { stdin } = await import('node:process');
    for await (const chunk of stdin) {
      input += chunk;
    }
    try {
      const scanData = JSON.parse(input);
      const posts = scanData?.data?.posts || scanData?.posts || [];
      const top = args.top || 10;
      for (const p of posts.slice(0, top)) {
        if (p.id) postIds.push(p.id);
      }
    } catch (err) {
      fail(`Cannot parse stdin JSON: ${err.message}`);
    }
  } else {
    fail('--post <id|url> or --from-scan <file> or --stdin is required');
  }

  const maxComments = args.maxComments || 200;

  log(`[deep-dive] ${postIds.length} post(s), maxComments=${maxComments}`);

  const results = [];

  for (const postId of postIds) {
    log(`[deep-dive] fetching comments for ${postId}`);

    // fetch post metadata
    let postMeta = null;
    try {
      const posts = await searchSubmissions({ ids: postId, size: 1 });
      if (posts.length > 0) postMeta = posts[0];
    } catch (err) {
      log(`[deep-dive] post metadata fetch failed: ${err.message}`);
    }

    // fetch comments
    let comments;
    try {
      comments = await paginateComments(postId, maxComments);
    } catch (err) {
      log(`[deep-dive] comment fetch failed for ${postId}: ${err.message}`);
      results.push({
        postId,
        error: err.message,
      });
      continue;
    }

    const analysis = analyzeComments(comments);

    results.push({
      post: postMeta ? {
        id: postMeta.id,
        title: postMeta.title || '',
        subreddit: postMeta.subreddit || '',
        url: `https://www.reddit.com${postMeta.permalink || ''}`,
        score: postMeta.score || 0,
        num_comments: postMeta.num_comments || 0,
        painScore: computePainScore(postMeta),
        selftext_excerpt: excerpt(postMeta.selftext, 300),
      } : { id: postId },
      analysis,
    });
  }

  ok({
    results,
    api_calls: rateLimiter.count,
  });
}

function extractPostId(input) {
  // URL: https://www.reddit.com/r/sub/comments/ABC123/title/
  const urlMatch = input.match(/\/comments\/([a-z0-9]+)/i);
  if (urlMatch) return urlMatch[1];
  // bare ID
  if (/^[a-z0-9]+$/i.test(input)) return input;
  return null;
}

// ─── CLI arg parser ──────────────────────────────────────────────────────────

function parseArgs(argv) {
  const result = { _: [] };
  let i = 0;
  while (i < argv.length) {
    const arg = argv[i];
    if (arg.startsWith('--')) {
      const key = arg.slice(2);
      // check if next arg is a value or another flag
      if (i + 1 < argv.length && !argv[i + 1].startsWith('--')) {
        result[key] = argv[i + 1];
        i += 2;
      } else {
        result[key] = true;
        i++;
      }
    } else {
      result._.push(arg);
      i++;
    }
  }
  return result;
}

function toCamelCase(str) {
  return str.replace(/-([a-z])/g, (_, c) => c.toUpperCase());
}

// ─── main ────────────────────────────────────────────────────────────────────

async function main() {
  const argv = process.argv.slice(2);

  if (argv.length === 0 || argv.includes('--help')) {
    log(`
pain-points — Reddit pain point discovery via PullPush API

Usage:
  pain-points.mjs <command> [options]

Commands:
  discover   Find relevant subreddits for a domain
  scan       Broad pain-point search across subreddits
  deep-dive  Deep comment analysis for specific posts

discover options:
  --domain <str>        Domain to search (required)
  --limit <n>           Max subreddits to return (default: 10)

scan options:
  --subreddits <list>   Comma-separated subreddits (required)
  --domain <str>        Domain for extra queries
  --days <n>            Search last N days (default: 365)
  --minScore <n>        Min post score (default: 1)
  --minComments <n>     Min comments (default: 3)
  --limit <n>           Max posts to return (default: 30)
  --pages <n>           Pages per query (default: 2)

deep-dive options:
  --post <id|url>       Single post to analyze
  --from-scan <file>    JSON file from scan output
  --stdin               Read scan JSON from stdin
  --top <n>             Analyze top N posts (default: 10)
  --maxComments <n>     Max comments per post (default: 200)

Examples:
  node pain-points.mjs discover --domain "project management" --limit 5
  node pain-points.mjs scan --subreddits projectmanagement,SaaS --days 30
  node pain-points.mjs deep-dive --post 1inyk7o
  node pain-points.mjs scan ... | node pain-points.mjs deep-dive --stdin --top 5
`);
    process.exit(0);
  }

  const command = argv[0];
  const raw = parseArgs(argv.slice(1));

  // normalize args
  const args = {};
  for (const [k, v] of Object.entries(raw)) {
    if (k === '_') {
      args._ = v;
    } else {
      args[toCamelCase(k)] = v;
    }
  }

  // parse common types
  if (args.limit) args.limit = parseInt(args.limit, 10);
  if (args.days) args.days = parseInt(args.days, 10);
  if (args.minScore) args.minScore = parseInt(args.minScore, 10);
  if (args.minComments) args.minComments = parseInt(args.minComments, 10);
  if (args.pages) args.pages = parseInt(args.pages, 10);
  if (args.top) args.top = parseInt(args.top, 10);
  if (args.maxComments) args.maxComments = parseInt(args.maxComments, 10);
  if (typeof args.subreddits === 'string') {
    args.subreddits = args.subreddits.split(',').map(s => s.trim()).filter(Boolean);
  }

  switch (command) {
    case 'discover':
      await cmdDiscover(args);
      break;
    case 'scan':
      await cmdScan(args);
      break;
    case 'deep-dive':
      await cmdDeepDive(args);
      break;
    default:
      fail(`Unknown command: ${command}. Use --help for usage.`);
  }
}

main().catch(err => {
  fail(err.message);
});
