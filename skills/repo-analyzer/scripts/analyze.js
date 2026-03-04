#!/usr/bin/env node
/**
 * GitHub Repo Analyzer — deep trust scoring for any public repo
 * Zero dependencies (Node.js built-ins only)
 * 
 * Usage: node analyze.js <github-url-or-owner/repo> [--json] [--verbose]
 */

const https = require('https');
const { parseArgs } = require('util');

const { values: args, positionals } = parseArgs({
  options: {
    'json': { type: 'boolean', default: false },
    'verbose': { type: 'boolean', default: false },
    'token': { type: 'string', default: '' },
    'oneline': { type: 'boolean', default: false },
    'badge': { type: 'boolean', default: false },
    'file': { type: 'string', default: '' },
  },
  allowPositionals: true,
  strict: false,
});

const GITHUB_TOKEN = args.token || process.env.GITHUB_TOKEN || '';
if (!GITHUB_TOKEN) {
  console.error('⚠️  WARNING: No GITHUB_TOKEN set. Results will be degraded (60 req/hr, missing metadata).');
  console.error('   Set via: export GITHUB_TOKEN="ghp_..." or --token flag\n');
}

// --- HTTP helpers ---
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function _getOnce(url, headers = {}) {
  return new Promise((resolve, reject) => {
    const h = {
      'User-Agent': 'github-analyzer/1.0',
      'Accept': 'application/vnd.github.v3+json',
      ...headers,
    };
    if (GITHUB_TOKEN) h['Authorization'] = `Bearer ${GITHUB_TOKEN}`;
    
    const u = new URL(url);
    const req = https.request({
      hostname: u.hostname, path: u.pathname + u.search,
      headers: h,
    }, res => {
      // Follow redirects (301, 302, 307)
      if ([301, 302, 307].includes(res.statusCode) && res.headers.location) {
        _getOnce(res.headers.location, headers).then(resolve).catch(reject);
        return;
      }
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => {
        let parsed;
        try { parsed = JSON.parse(d); } catch(e) { parsed = d; }
        resolve({ status: res.statusCode, data: parsed, headers: res.headers });
      });
    });
    req.on('error', reject);
    req.end();
  });
}

async function get(url, headers = {}) {
  const MAX_RETRIES = 2;
  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    const res = await _getOnce(url, headers);
    // Rate limit retry
    if (res.status === 403 && res.data?.message?.includes('rate limit')) {
      const resetEpoch = parseInt(res.headers['x-ratelimit-reset'] || '0', 10);
      const waitSec = resetEpoch ? resetEpoch - Math.floor(Date.now() / 1000) : 0;
      if (attempt < MAX_RETRIES && waitSec > 0 && waitSec <= 60) {
        console.error(`⚠️  Rate limited. Waiting ${waitSec}s for reset (attempt ${attempt + 1}/${MAX_RETRIES})...`);
        await sleep(waitSec * 1000);
        continue;
      }
      const resetTime = resetEpoch ? new Date(resetEpoch * 1000).toLocaleTimeString() : 'unknown';
      throw new Error(`GitHub API rate limited. Resets at ${resetTime} (${waitSec}s). Set GITHUB_TOKEN for higher limits.`);
    }
    // Transient 5xx retry
    if (res.status >= 500 && attempt < 1) {
      console.error(`⚠️  GitHub API ${res.status}. Retrying in 2s...`);
      await sleep(2000);
      continue;
    }
    return res;
  }
}

// Safe wrapper: returns null data for non-200 responses instead of crashing on undefined fields
function safeGet(url, headers = {}) {
  return get(url, headers).then(res => {
    if (res.status !== 200) {
      return { status: res.status, data: null, headers: res.headers };
    }
    return res;
  });
}

function getRaw(url) {
  return new Promise((resolve, reject) => {
    const u = new URL(url);
    const req = https.request({
      hostname: u.hostname, path: u.pathname + u.search,
      headers: { 'User-Agent': 'github-analyzer/1.0' },
    }, res => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => resolve(d));
    });
    req.on('error', reject);
    req.end();
  });
}

// --- Parse repo from URL or owner/repo ---
function parseRepo(input) {
  input = input.trim().replace(/\/$/, '');
  const ghMatch = input.match(/github\.com\/([^\/]+)\/([^\/\?#]+)/);
  if (ghMatch) return { owner: ghMatch[1], repo: ghMatch[2].replace('.git', '') };
  const slashMatch = input.match(/^([^\/]+)\/([^\/]+)$/);
  if (slashMatch) return { owner: slashMatch[1], repo: slashMatch[2] };
  return null;
}

// --- Resolve t.co short URLs ---
function resolveUrl(shortUrl) {
  return new Promise((resolve) => {
    const u = new URL(shortUrl);
    const req = https.request({
      hostname: u.hostname, path: u.pathname,
      method: 'HEAD',
      headers: { 'User-Agent': 'github-analyzer/1.0' },
    }, res => {
      if (res.headers.location) resolve(res.headers.location);
      else resolve(shortUrl);
    });
    req.on('error', () => resolve(shortUrl));
    req.end();
  });
}

// --- Extract GitHub repos from X/Twitter URLs ---
async function extractReposFromTweet(url) {
  const { execSync } = require('child_process');
  const repos = [];

  // Try bird CLI first
  try {
    const output = execSync(`bird read "${url}" 2>/dev/null`, {
      timeout: 15000,
      env: { ...process.env },
    }).toString();

    // Find t.co links and resolve them
    const tcoLinks = output.match(/https?:\/\/t\.co\/\w+/g) || [];
    for (const link of tcoLinks) {
      try {
        const resolved = await resolveUrl(link);
        const parsed = parseRepo(resolved);
        if (parsed) repos.push(parsed);
      } catch {}
    }

    // Also check for direct GitHub URLs in the output
    const ghLinks = output.match(/https?:\/\/github\.com\/[^\s'"`)>\]]+/g) || [];
    for (const link of ghLinks) {
      const parsed = parseRepo(link);
      if (parsed && !repos.some(r => r.owner === parsed.owner && r.repo === parsed.repo)) {
        repos.push(parsed);
      }
    }

    return { repos, tweetText: output };
  } catch {}

  // Fallback: try web fetch via nitter or direct
  try {
    // Try to fetch via basic HTTP and look for GitHub links
    const tweetId = url.match(/status\/(\d+)/)?.[1];
    if (tweetId) {
      // Use syndication API (public, no auth)
      const res = await get(`https://cdn.syndication.twimg.com/tweet-result?id=${tweetId}&token=0`);
      if (res.data?.text) {
        const text = res.data.text;
        const entities = res.data.entities?.urls || [];
        for (const entity of entities) {
          const expanded = entity.expanded_url || entity.url;
          if (expanded) {
            const parsed = parseRepo(expanded);
            if (parsed) repos.push(parsed);
          }
        }
        return { repos, tweetText: text };
      }
    }
  } catch {}

  return { repos, tweetText: null };
}

// --- Check if input is an X/Twitter URL ---
function isTwitterUrl(input) {
  return /^https?:\/\/(x\.com|twitter\.com)\/\w+\/status\/\d+/i.test(input.trim());
}

// --- Analysis modules ---

async function analyzeRepo(owner, repo) {
  const results = {
    meta: null,
    commits: null,
    contributors: null,
    activity: null,
    codeQuality: null,
    social: null,
    crypto: null,
    security: null,
    scores: {},
    grade: '',
    trustScore: 0,
    flags: [],
    warnings: [],
  };

  const base = `https://api.github.com/repos/${owner}/${repo}`;
  const v = args.verbose;

  // 1. Repository metadata
  if (v) console.error('Fetching repo metadata...');
  const repoRes = await get(base);
  if (repoRes.status === 404) {
    throw new Error(`Repository ${owner}/${repo} not found`);
  }
  if (repoRes.status === 403) {
    throw new Error(`GitHub API rate limited (403). Set GITHUB_TOKEN for higher limits.`);
  }
  if (repoRes.status !== 200) {
    throw new Error(`GitHub API error ${repoRes.status} for ${owner}/${repo}: ${JSON.stringify(repoRes.data)}`);
  }
  const r = repoRes.data;
  results.meta = {
    name: r.full_name,
    description: r.description,
    language: r.language,
    stars: r.stargazers_count,
    forks: r.forks_count,
    watchers: r.subscribers_count || r.watchers_count,
    openIssues: r.open_issues_count,
    createdAt: r.created_at,
    updatedAt: r.updated_at,
    pushedAt: r.pushed_at,
    size: r.size,
    defaultBranch: r.default_branch,
    hasIssues: r.has_issues,
    hasWiki: r.has_wiki,
    license: r.license?.spdx_id || null,
    isForked: r.fork,
    parent: r.parent?.full_name || null,
    archived: r.archived,
    topics: r.topics || [],
  };

  // 2. Commit analysis
  if (v) console.error('Analyzing commits...');
  const commitsRes = await get(`${base}/commits?per_page=100`);
  const commits = Array.isArray(commitsRes.data) ? commitsRes.data : [];
  
  const authors = {};
  const commitDates = [];
  let gpgSigned = 0;
  let singleFileCommits = 0;
  
  let botCommits = 0;
  for (const c of commits) {
    const author = c.commit?.author?.email || 'unknown';
    const name = c.commit?.author?.name || 'unknown';
    const isBot = /\[bot\]|dependabot|github-actions|renovate|greenkeeper|snyk/i.test(name) || /\[bot\]/i.test(author);
    if (isBot) { botCommits++; continue; } // skip bots for author analysis
    authors[author] = authors[author] || { name, count: 0, firstCommit: null, lastCommit: null };
    authors[author].count++;
    const date = c.commit?.author?.date;
    if (date) {
      commitDates.push(new Date(date));
      if (!authors[author].firstCommit) authors[author].firstCommit = date;
      authors[author].lastCommit = date;
    }
    if (c.commit?.verification?.verified) gpgSigned++;
  }
  const humanCommits = commits.length - botCommits;

  // Detect code dump (few commits, recent creation)
  const ageMs = Date.now() - new Date(r.created_at).getTime();
  const ageDays = ageMs / 86400000;
  const commitsPerDay = humanCommits / Math.max(ageDays, 1);
  const isCodeDump = humanCommits <= 3 && ageDays < 30;

  // Detect suspiciously perfect timestamps (evenly spaced = likely faked)
  let evenlySpaced = false;
  if (commitDates.length >= 5) {
    const gaps = [];
    for (let i = 1; i < commitDates.length; i++) {
      gaps.push(commitDates[i - 1] - commitDates[i]);
    }
    const avgGap = gaps.reduce((a, b) => a + b, 0) / gaps.length;
    const variance = gaps.reduce((a, b) => a + Math.pow(b - avgGap, 2), 0) / gaps.length;
    const stdDev = Math.sqrt(variance);
    const cv = avgGap > 0 ? stdDev / avgGap : 0;
    evenlySpaced = cv < 0.15 && commits.length >= 5; // very low variance = suspicious
  }

  results.commits = {
    total: commits.length,
    human: humanCommits,
    bot: botCommits,
    authors: Object.entries(authors).map(([email, data]) => ({
      email, name: data.name, commits: data.count,
      firstCommit: data.firstCommit, lastCommit: data.lastCommit,
    })),
    gpgSigned,
    gpgRate: commits.length > 0 ? Math.round(gpgSigned / commits.length * 100) : 0,
    commitsPerDay: Math.round(commitsPerDay * 100) / 100,
    isCodeDump,
    evenlySpaced,
    oldestCommit: commitDates.length > 0 ? commitDates[commitDates.length - 1].toISOString() : null,
    newestCommit: commitDates.length > 0 ? commitDates[0].toISOString() : null,
  };

  // 3. Contributors
  if (v) console.error('Analyzing contributors...');
  const contribRes = await get(`${base}/contributors?per_page=30`);
  const contribs = Array.isArray(contribRes.data) ? contribRes.data : [];
  
  const busFactor = contribs.filter(c => c.contributions > commits.length * 0.1).length;
  
  // Check contributor account ages
  const suspiciousContribs = [];
  for (const c of contribs.slice(0, 5)) {
    const userRes = await get(`https://api.github.com/users/${c.login}`);
    if (userRes.data) {
      const acctAge = (Date.now() - new Date(userRes.data.created_at).getTime()) / 86400000;
      const repos = userRes.data.public_repos || 0;
      const followers = userRes.data.followers || 0;
      if (acctAge < 90 && repos < 3) {
        suspiciousContribs.push({ login: c.login, ageDays: Math.round(acctAge), repos, followers });
      }
    }
  }

  results.contributors = {
    total: contribs.length,
    busFactor,
    topContributors: contribs.slice(0, 5).map(c => ({
      login: c.login, contributions: c.contributions
    })),
    suspiciousAccounts: suspiciousContribs,
  };

  // 4. Activity & health
  if (v) console.error('Checking activity...');
  const lastPush = new Date(r.pushed_at);
  const daysSinceLastPush = (Date.now() - lastPush) / 86400000;
  
  // Issues
  let issueHealth = null;
  if (r.has_issues) {
    const openRes = await get(`${base}/issues?state=open&per_page=1`);
    const closedRes = await get(`${base}/issues?state=closed&per_page=1`);
    // Get total from link headers
    const openCount = r.open_issues_count;
    issueHealth = { open: openCount };
  }

  // Releases
  const releasesRes = await get(`${base}/releases?per_page=5`);
  const releases = Array.isArray(releasesRes.data) ? releasesRes.data : [];

  results.activity = {
    daysSinceLastPush: Math.round(daysSinceLastPush),
    ageDays: Math.round(ageDays),
    issues: issueHealth,
    releases: releases.length,
    latestRelease: releases[0]?.tag_name || null,
  };

  // 5. Code quality signals
  if (v) console.error('Analyzing code quality...');
  const treeRes = await get(`${base}/git/trees/${r.default_branch}?recursive=1`);
  const tree = treeRes.data?.tree || [];
  
  const files = tree.map(f => f.path);
  const hasTests = files.some(f => /test|spec|__test__|\.test\.|\.spec\./i.test(f));
  const hasCI = files.some(f => /\.github\/workflows|\.circleci|\.travis|jenkinsfile|\.gitlab-ci/i.test(f));
  const hasLicense = files.some(f => /^(license|licence|copying|copyright)/i.test(f));
  const hasReadme = files.some(f => /^readme/i.test(f));
  const hasGitignore = files.some(f => f === '.gitignore');
  const hasPackageLock = files.some(f => /package-lock|yarn\.lock|bun\.lock|Cargo\.lock|go\.sum|poetry\.lock/i.test(f));
  const hasDockerfile = files.some(f => /dockerfile/i.test(f));
  const hasDocs = files.some(f => /^docs\//i.test(f));
  const hasChangelog = files.some(f => /changelog/i.test(f));
  const hasContributing = files.some(f => /contributing/i.test(f));
  const hasSecurityPolicy = files.some(f => /security\.md/i.test(f));

  // Count languages by extension
  const extensions = {};
  for (const f of files) {
    const ext = f.split('.').pop()?.toLowerCase();
    if (ext && ext.length < 8) extensions[ext] = (extensions[ext] || 0) + 1;
  }

  // Detect AI-generated patterns
  const readmeFile = files.find(f => /^readme\.md$/i.test(f)) || files.find(f => /^readme$/i.test(f)) || 'README.md';
  let readmeContent = await getRaw(`https://raw.githubusercontent.com/${owner}/${repo}/${r.default_branch}/${readmeFile}`).catch(() => '');
  // If root README is tiny (pointer/symlink in monorepos), try following the path or common subdirs
  if (readmeContent.length < 100 && readmeContent.length > 0) {
    const pointerPath = readmeContent.trim();
    if (/^[\w./-]+readme\.md$/i.test(pointerPath)) {
      const followed = await getRaw(`https://raw.githubusercontent.com/${owner}/${repo}/${r.default_branch}/${pointerPath}`).catch(() => '');
      if (followed.length > 100) readmeContent = followed;
    }
    if (readmeContent.length < 100) {
      // Try common monorepo README locations
      const candidates = files.filter(f => /readme\.md$/i.test(f) && f !== readmeFile).slice(0, 3);
      for (const c of candidates) {
        const alt = await getRaw(`https://raw.githubusercontent.com/${owner}/${repo}/${r.default_branch}/${c}`).catch(() => '');
        if (alt.length > readmeContent.length) { readmeContent = alt; break; }
      }
    }
  }
  
  const aiPatterns = [
    /this project aims to/i, /comprehensive solution/i, /robust and scalable/i,
    /leverag(e|ing) the power/i, /cutting[- ]edge/i, /state[- ]of[- ]the[- ]art/i,
    /seamless(ly)?/i, /empower(s|ing)?/i, /holistic/i, /synerg/i,
    /revolutioniz/i, /paradigm/i, /ecosystem of/i, /delve/i,
    /it'?s important to note/i, /it'?s worth noting/i,
  ];
  
  const aiHits = aiPatterns.filter(p => p.test(readmeContent));
  const readmeLength = readmeContent.length;
  const hasEmoji = (readmeContent.match(/[\u{1F300}-\u{1F9FF}]/gu) || []).length;
  const emojiDensity = readmeLength > 0 ? hasEmoji / (readmeLength / 1000) : 0;

  results.codeQuality = {
    totalFiles: files.length,
    hasTests, hasCI, hasLicense, hasReadme, hasGitignore, hasPackageLock,
    hasDockerfile, hasDocs, hasChangelog, hasContributing, hasSecurityPolicy,
    extensions: Object.entries(extensions).sort((a, b) => b[1] - a[1]).slice(0, 10),
    aiSlop: {
      hits: aiHits.length,
      patterns: aiHits.map(p => p.source),
      emojiDensity: Math.round(emojiDensity * 10) / 10,
      readmeLength,
    },
  };

  // 6. Social signals
  if (v) console.error('Checking social signals...');
  const starForkRatio = r.forks_count > 0 ? r.stargazers_count / r.forks_count : r.stargazers_count;
  
  // Check for star velocity anomalies (if we can get stargazers)
  let starVelocity = null;
  if (r.stargazers_count > 0 && ageDays > 0) {
    starVelocity = r.stargazers_count / ageDays;
  }

  // Suspicious: high stars but no forks, no issues, no contributors
  const bottedStars = r.stargazers_count > 50 && r.forks_count < 3 && contribs.length <= 1;

  results.social = {
    stars: r.stargazers_count,
    forks: r.forks_count,
    starForkRatio: Math.round(starForkRatio * 10) / 10,
    starsPerDay: starVelocity ? Math.round(starVelocity * 100) / 100 : null,
    bottedStars,
  };

  // 7. Crypto-specific checks
  if (v) console.error('Running crypto checks...');
  const cryptoFlags = [];
  
  // Check for pump.fun patterns
  const allContent = files.join('\n');
  if (/pump\.fun|pumpfun/i.test(readmeContent) || files.some(f => /pump\.fun|pumpfun/i.test(f))) {
    cryptoFlags.push('pump.fun references detected');
  }
  
  // Check for hardcoded wallet addresses in file names or readme
  const walletPatterns = [
    /0x[a-fA-F0-9]{40}/g,  // EVM
    /[1-9A-HJ-NP-Za-km-z]{32,44}/g,  // Solana/Base58 (rough)
  ];
  
  const readmeWallets = [];
  for (const p of walletPatterns) {
    const matches = readmeContent.match(p) || [];
    readmeWallets.push(...matches);
  }
  if (readmeWallets.length > 0) {
    cryptoFlags.push(`${readmeWallets.length} wallet address(es) in README`);
  }

  // Check for token mints ending in "pump"
  if (/[a-zA-Z0-9]+pump\b/i.test(readmeContent + allContent)) {
    cryptoFlags.push('Possible pump.fun token mint detected');
  }

  // Check config files for token/mint references
  const configFiles = files.filter(f => /\.toml|\.json|\.yaml|\.yml|\.env/i.test(f) && !/node_modules|package-lock/.test(f));
  for (const cf of configFiles.slice(0, 10)) {
    try {
      const content = await getRaw(`https://raw.githubusercontent.com/${owner}/${repo}/${r.default_branch}/${cf}`);
      if (/pump\b/i.test(content) && /mint|token/i.test(content)) {
        cryptoFlags.push(`Token mint with pump.fun pattern in ${cf}`);
      }
      // Check for placeholder program IDs
      if (/[A-Z]{5,}x{10,}/.test(content)) {
        cryptoFlags.push(`Placeholder program ID in ${cf} — not deployed`);
      }
    } catch {}
  }

  results.crypto = {
    flags: cryptoFlags,
    hasCryptoContent: cryptoFlags.length > 0 || r.topics?.some(t => /crypto|defi|solana|ethereum|web3|nft|token/i.test(t)),
  };

  // 8. Enhanced Dependency Audit Module
  if (v) console.error('Running enhanced dependency audit...');
  const depFlags = [];
  const depInfo = { 
    totalDeps: 0, directDeps: 0, devDeps: 0, transitiveDeps: 0, 
    outdated: [], suspicious: [], malicious: [], installHooks: [], 
    typosquats: [], hasLockFile: false, score: 0 
  };

  // Known malicious packages — always bad (typosquats, pure malware)
  const knownMalicious = {
    'flatmap-stream': 'Bitcoin wallet stealer',
    'getcookies': 'Credential harvester',
    'http-fetch': 'Malicious backdoor',
    'nodemv': 'System command execution',
    'crossenv': 'Environment variable exfiltration',
    'babelcli': 'Typosquatting babel-cli',
    'mongose': 'Typosquatting mongoose',
  };
  // Packages that were historically compromised but name is legit (specific versions were bad)
  const historicallyCompromised = {
    'event-stream': 'Specific version compromised in 2018',
    'ua-parser-js': 'Specific version compromised in 2021',
    'coa': 'Specific version compromised in 2021',
    'rc': 'Specific version compromised in 2021',
    'colors': 'Sabotaged by maintainer in 2022 — fixed in later versions',
    'faker': 'Sabotaged by maintainer in 2022 — use @faker-js/faker instead',
    'node-ipc': 'Protestware in 2022 — fixed in later versions',
    'peacenotwar': 'Protestware dependency',
    'es5-ext': 'Specific version compromised',
    // Python packages commonly targeted
    'python3-dateutil': 'Typosquatting python-dateutil',
    'python3-urllib': 'Typosquatting urllib3',
    'python-dateutils': 'Typosquatting python-dateutil',
    'urllib4': 'Typosquatting urllib3',
    'reqests': 'Typosquatting requests',
    'beautifulsoup': 'Typosquatting beautifulsoup4',
    'scapy3k': 'Potentially malicious scapy variant'
  };

  // Enhanced typosquatting detection
  const popularPackages = {
    // npm
    'lodash': ['lodashs', 'lodash-es-fake', 'l0dash', 'lodas', 'loadsh'],
    'express': ['expres', 'expresss', 'exppress', 'expess'],
    'axios': ['axois', 'axio', 'axioss', 'axois'],
    'react': ['reakt', 'reactt', 'raect'], 
    'moment': ['momment', 'momet', 'momentjs'],
    'webpack': ['webpac', 'webpackk', 'wepback'],
    'eslint': ['esslint', 'esllint', 'es-lint'],
    'typescript': ['typescirpt', 'typescrypt', 'tyepscript'],
    // Python
    'requests': ['reqests', 'request', 'requsts'],
    'urllib3': ['urllib', 'urllib4', 'urllib2'],
    'numpy': ['nunpy', 'numpi', 'numpy-dev'],
    'pandas': ['pands', 'pandass'],
    'beautifulsoup4': ['beautifulsoup', 'beautiful-soup'],
    'flask': ['flaskk', 'falsk'],
    'django': ['djang0', 'djangoo'],
    'scipy': ['cipy', 'scipyy']
  };

  // Check package.json (Node)
  try {
    const pkgContent = await getRaw(`https://raw.githubusercontent.com/${owner}/${repo}/${r.default_branch}/package.json`);
    if (pkgContent && !pkgContent.includes('404')) {
      const pkg = JSON.parse(pkgContent);
      const deps = Object.keys(pkg.dependencies || {});
      const devDeps = Object.keys(pkg.devDependencies || {});
      depInfo.directDeps = deps.length;
      depInfo.devDeps = devDeps.length;
      depInfo.totalDeps = deps.length + devDeps.length;

      // Check for install scripts (major security risk)
      const scripts = pkg.scripts || {};
      const dangerousHooks = ['preinstall', 'postinstall', 'install', 'prepare'];
      for (const hook of dangerousHooks) {
        if (scripts[hook]) {
          depInfo.installHooks.push({ hook, script: scripts[hook] });
          depFlags.push(`Install hook "${hook}": ${scripts[hook].substring(0, 50)}${scripts[hook].length > 50 ? '...' : ''}`);
        }
      }

      // Check all dependencies
      const allDeps = { ...pkg.dependencies, ...pkg.devDependencies };
      for (const [name, version] of Object.entries(allDeps)) {
        // Check against known malicious packages
        if (knownMalicious[name]) {
          depInfo.malicious.push({ name, version, reason: knownMalicious[name] });
          depFlags.push(`🔴 MALICIOUS: ${name} - ${knownMalicious[name]}`);
        } else if (historicallyCompromised[name]) {
          depFlags.push(`⚠️ HISTORICAL: ${name} - ${historicallyCompromised[name]}`);
        }

        // Typosquatting detection
        for (const [real, fakes] of Object.entries(popularPackages)) {
          if (fakes.includes(name)) {
            depInfo.typosquats.push({ fake: name, real, version });
            depFlags.push(`Typosquatting: ${name}@${version} (did you mean ${real}?)`);
          }
        }

        // Suspicious patterns
        if (name.includes('--') || name.includes('..') || /^@[^\/]+\/[^\/]+\//.test(name)) {
          depInfo.suspicious.push({ name, version, reason: 'Suspicious format' });
          depFlags.push(`Suspicious package format: ${name}`);
        }

        // Very short names (often squatters)
        if (name.length <= 2 && !['fs', 'os', 'vm', 'ws'].includes(name)) {
          depInfo.suspicious.push({ name, version, reason: 'Very short name' });
          depFlags.push(`Suspicious short name: ${name} (${name.length} chars)`);
        }

        // Wildcard versions
        if (version === '*' || version === 'latest') {
          depFlags.push(`Unpinned dependency: ${name}@${version}`);
        }

        // Scoped packages with no slash (invalid format)
        if (name.startsWith('@') && !name.includes('/')) {
          depInfo.suspicious.push({ name, version, reason: 'Invalid scoped package format' });
          depFlags.push(`Invalid scoped package: ${name}`);
        }
      }

      // Check for lock file presence
      depInfo.hasLockFile = files.some(f => f === 'package-lock.json' || f === 'yarn.lock' || f === 'pnpm-lock.yaml');
      if (!depInfo.hasLockFile && depInfo.totalDeps > 5) {
        depFlags.push('No lock file found - versions not pinned');
      }

      // Estimate transitive dependencies from lock file size if available
      if (depInfo.hasLockFile) {
        const lockFile = files.find(f => f === 'package-lock.json' || f === 'yarn.lock');
        if (lockFile) {
          const lockEntry = (treeRes.data?.tree || []).find(t => t.path === lockFile);
          if (lockEntry && lockEntry.size) {
            // Rough estimate: each dep entry is ~150-250 bytes in lock files
            depInfo.transitiveDeps = Math.round(lockEntry.size / 200);
          }
        }
      }
    }
  } catch {}

  // Check requirements.txt (Python)
  try {
    const reqContent = await getRaw(`https://raw.githubusercontent.com/${owner}/${repo}/${r.default_branch}/requirements.txt`);
    if (reqContent && !reqContent.includes('404') && reqContent.length < 50000) {
      const lines = reqContent.split('\n').filter(l => l.trim() && !l.startsWith('#'));
      depInfo.totalDeps += lines.length;
      depInfo.directDeps += lines.length;
      
      for (const line of lines) {
        const name = line.split(/[=<>!~]/)[0].trim();
        if (!name) continue;

        // Check against known malicious packages
        if (knownMalicious[name]) {
          depInfo.malicious.push({ name, line, reason: knownMalicious[name] });
          depFlags.push(`🔴 MALICIOUS Python package: ${name} - ${knownMalicious[name]}`);
        }

        // Typosquatting for Python packages
        for (const [real, fakes] of Object.entries(popularPackages)) {
          if (fakes.includes(name)) {
            depInfo.typosquats.push({ fake: name, real, line });
            depFlags.push(`Python typosquatting: ${name} (did you mean ${real}?)`);
          }
        }

        // Check for unpinned versions
        if (!line.includes('==') && !line.includes('>=') && !line.includes('~=') && line.length > name.length) {
          depFlags.push(`Unpinned Python dependency: ${name}`);
        }
      }
    }
  } catch {}

  // Check Cargo.toml (Rust)
  try {
    const cargoContent = await getRaw(`https://raw.githubusercontent.com/${owner}/${repo}/${r.default_branch}/Cargo.toml`);
    if (cargoContent && !cargoContent.includes('404')) {
      const depMatches = cargoContent.match(/\[dependencies\]([\s\S]*?)(\[|$)/);
      if (depMatches) {
        const depSection = depMatches[1];
        const depLines = depSection.split('\n').filter(l => l.trim() && !l.startsWith('#') && l.includes('='));
        depInfo.totalDeps += depLines.length;
        depInfo.directDeps += depLines.length;

        // Check for git dependencies (potential supply chain risk)
        const gitDeps = depSection.match(/git\s*=\s*"[^"]+"/g) || [];
        if (gitDeps.length > 0) {
          depFlags.push(`${gitDeps.length} git dependencies - harder to audit than crates.io`);
        }
      }
    }
  } catch {}

  // Check go.mod (Go)
  try {
    const goContent = await getRaw(`https://raw.githubusercontent.com/${owner}/${repo}/${r.default_branch}/go.mod`);
    if (goContent && !goContent.includes('404')) {
      const requireLines = goContent.split('\n').filter(l => l.trim().startsWith('require') || (l.trim() && !l.includes('module') && !l.includes('go ') && l.includes('v')));
      depInfo.totalDeps += requireLines.length;
      depInfo.directDeps += requireLines.length;

      // Check for replace directives (could be supply chain risk)
      const replaces = goContent.split('\n').filter(l => l.trim().startsWith('replace'));
      if (replaces.length > 0) {
        depFlags.push(`${replaces.length} replace directive(s) - potentially modified dependencies`);
      }
    }
  } catch {}

  // Calculate dependency audit score (0-10)
  let depScore = 8;
  depScore -= Math.min(8, depInfo.malicious.length * 3); // Malicious packages = major penalty
  depScore -= Math.min(5, depInfo.typosquats.length * 2); // Typosquats = big penalty  
  depScore -= Math.min(3, depInfo.installHooks.length); // Install hooks = penalty
  depScore -= Math.min(2, depInfo.suspicious.length); // Suspicious packages = small penalty
  if (!depInfo.hasLockFile && depInfo.totalDeps > 5) depScore -= 1; // No lock file = penalty
  if (depInfo.transitiveDeps > 1000) depScore -= 2; // Bloated dependencies = penalty
  else if (depInfo.transitiveDeps > 500) depScore -= 1;

  depInfo.score = Math.max(0, depScore);
  results.dependencies = { ...depInfo, flags: depFlags };

  // 9. Author identity verification
  if (v) console.error('Verifying author identities...');
  const authorVerification = [];

  for (const author of Object.entries(authors).slice(0, 5)) {
    const [email, data] = author;
    const verification = { email, name: data.name, verified: false, flags: [] };

    // Check if email domain matches a known company
    const domain = email.split('@')[1];
    const corpDomains = {
      'google.com': 'Google', 'microsoft.com': 'Microsoft', 'apple.com': 'Apple',
      'amazon.com': 'Amazon', 'amazon.de': 'Amazon', 'meta.com': 'Meta', 'facebook.com': 'Meta',
      'venmo.com': 'Venmo/PayPal', 'stripe.com': 'Stripe', 'coinbase.com': 'Coinbase',
      'binance.com': 'Binance', 'kraken.com': 'Kraken',
    };

    if (corpDomains[domain]) {
      verification.claimedOrg = corpDomains[domain];
      verification.flags.push(`Claims ${corpDomains[domain]} affiliation via email — unverified without GPG signature`);
    }

    // Try to find GitHub user by commit email
    const searchRes = await get(`https://api.github.com/search/users?q=${encodeURIComponent(email)}+in:email`);
    if (searchRes.data?.total_count > 0) {
      const user = searchRes.data.items[0];
      verification.githubUser = user.login;

      // Check if user's public profile matches claimed identity
      const profileRes = await get(`https://api.github.com/users/${user.login}`);
      if (profileRes.data) {
        const profile = profileRes.data;
        verification.profileName = profile.name;
        verification.publicRepos = profile.public_repos;
        verification.followers = profile.followers;
        verification.createdAt = profile.created_at;
        verification.bio = profile.bio;
        verification.company = profile.company;

        // Cross-reference name
        if (profile.name && data.name && profile.name.toLowerCase() !== data.name.toLowerCase()) {
          verification.flags.push(`Commit name "${data.name}" doesn't match profile name "${profile.name}"`);
        }

        // Cross-reference company claim
        if (verification.claimedOrg && profile.company) {
          if (profile.company.toLowerCase().includes(verification.claimedOrg.toLowerCase().split('/')[0])) {
            verification.verified = true;
            verification.flags.push(`Company "${profile.company}" matches email domain — likely legit`);
          }
        }

        // Account age vs commit age
        const acctDate = new Date(profile.created_at);
        const firstCommitDate = data.firstCommit ? new Date(data.firstCommit) : null;
        if (firstCommitDate && acctDate > firstCommitDate) {
          verification.flags.push(`GitHub account created AFTER first commit — possible retroactive attribution`);
        }
      }
    } else {
      // No GitHub user found with this email
      if (verification.claimedOrg) {
        verification.flags.push(`No GitHub account found with email ${email} — corporate claim is unverifiable`);
      }
      // Check if it's a noreply email
      if (email.includes('noreply.github.com')) {
        verification.flags.push('Using GitHub noreply email — identity hidden');
      }
    }

    // GPG check for this author's commits
    const authorCommits = commits.filter(c => c.commit?.author?.email === email);
    const signedCount = authorCommits.filter(c => c.commit?.verification?.verified).length;
    verification.gpgSigned = signedCount;
    verification.gpgTotal = authorCommits.length;
    if (signedCount === 0 && verification.claimedOrg) {
      verification.flags.push(`0/${authorCommits.length} commits GPG-signed — anyone could have set this email`);
    } else if (signedCount > 0) {
      verification.verified = true;
      verification.flags.push(`${signedCount}/${authorCommits.length} commits GPG-signed — cryptographically verified`);
    }

    authorVerification.push(verification);
  }

  results.authorVerification = authorVerification;

  // 9b. Author reputation deep-dive — only surfaces noteworthy findings
  if (v) console.error('Checking author reputation...');
  const authorReputation = [];

  for (const av of authorVerification) {
    if (!av.githubUser) continue;
    const notes = [];

    try {
      // Get their repos (sorted by stars)
      const reposRes = await get(`https://api.github.com/users/${av.githubUser}/repos?sort=stars&per_page=30&type=owner`);
      const repos = reposRes.data || [];

      // Account age
      if (av.createdAt) {
        const acctAge = (Date.now() - new Date(av.createdAt).getTime()) / (1000 * 60 * 60 * 24 * 365);
        if (acctAge < 0.5) notes.push(`⚠️ Account <6 months old`);
        else if (acctAge > 8) notes.push(`Account ${Math.floor(acctAge)}+ years old`);
      }

      // Follower signal
      if (av.followers >= 1000) notes.push(`${av.followers.toLocaleString()} followers`);
      else if (av.followers === 0 && repos.length > 5) notes.push(`⚠️ 0 followers despite ${repos.length} repos`);

      // Notable repos they own
      const starredRepos = repos.filter(r => r.stargazers_count >= 100);
      if (starredRepos.length > 0) {
        const top = starredRepos[0];
        notes.push(`Maintains ${top.full_name} (${top.stargazers_count.toLocaleString()}⭐)`);
        if (starredRepos.length > 1) notes.push(`${starredRepos.length} repos with 100+ stars`);
      }

      // Empty/fork-heavy profile (sketch signal)
      const forks = repos.filter(r => r.fork);
      const empty = repos.filter(r => r.size === 0);
      if (repos.length > 0 && forks.length / repos.length > 0.7) {
        notes.push(`⚠️ ${Math.round(forks.length/repos.length*100)}% of repos are forks`);
      }
      if (empty.length > repos.length * 0.5 && repos.length > 3) {
        notes.push(`⚠️ ${empty.length}/${repos.length} repos are empty`);
      }

      // Crypto-specific checks on their other repos
      const scamSignals = ['pump', 'honeypot', 'rug', 'drainer', 'sandwich', 'frontrun', 'flashloan-attack', 'mev-bot'];
      for (const repo of repos) {
        const name = (repo.name + ' ' + (repo.description || '')).toLowerCase();
        if (scamSignals.some(s => name.includes(s))) {
          notes.push(`🚩 Owns suspicious repo: ${repo.full_name} — "${repo.description || repo.name}"`);
        }
      }

      // Check orgs they belong to
      const orgsRes = await get(`https://api.github.com/users/${av.githubUser}/orgs`);
      const orgs = (orgsRes.data || []).map(o => o.login);
      const notableOrgs = {
        'google': 'Google', 'microsoft': 'Microsoft', 'facebook': 'Meta', 'meta': 'Meta',
        'apple': 'Apple', 'ethereum': 'Ethereum Foundation', 'solana-labs': 'Solana Labs',
        'paradigmxyz': 'Paradigm', 'a16z': 'a16z', 'OpenZeppelin': 'OpenZeppelin',
        'foundry-rs': 'Foundry', 'uniswap': 'Uniswap', 'aave': 'Aave',
        'coinbase': 'Coinbase', 'binance': 'Binance', 'consensys': 'ConsenSys',
        'chainlink': 'Chainlink', 'MakerDAO': 'MakerDAO', 'compound-finance': 'Compound',
        'rust-lang': 'Rust', 'nodejs': 'Node.js', 'vercel': 'Vercel', 'docker': 'Docker',
      };
      for (const org of orgs) {
        if (notableOrgs[org]) {
          notes.push(`Member of ${notableOrgs[org]} org`);
        }
      }

      // Check contribution to big repos (starred repos they've contributed to)
      const starredRes = await get(`https://api.github.com/users/${av.githubUser}/starred?per_page=5`);
      // We can't easily check contributions without heavy API use, so org membership + own repos suffices

    } catch (e) {
      // API failures are non-fatal
    }

    if (notes.length > 0) {
      authorReputation.push({ user: av.githubUser, name: av.name || av.profileName, notes });
    }
  }

  results.authorReputation = authorReputation;

  // 10. Security signals
  const secFlags = [];
  // Check for exposed secrets patterns in file list
  if (files.some(f => /\.env$|credentials|secrets?\./i.test(f) && !/\.example|\.sample|\.template/i.test(f))) {
    secFlags.push('Possible exposed credentials file');
  }
  const keyFiles = files.filter(f => /id_rsa|id_ed25519|\.pem$|\.key$/i.test(f));
  const realKeyFiles = keyFiles.filter(f => !/test|fixture|sample|example|mock|fake/i.test(f));
  if (realKeyFiles.length > 0) {
    secFlags.push(`Private key file in repo: ${realKeyFiles.slice(0, 3).join(', ')}`);
  } else if (keyFiles.length > 0) {
    // Keys in test dirs — note but don't flag
    results.warnings.push(`Key files in test/fixture dirs (probably fine): ${keyFiles.length} file(s)`);
  }

  results.security = { flags: secFlags };

  // 11. README quality analysis
  if (v) console.error('Analyzing README quality...');
  const readmeQuality = { score: 0, maxScore: 10, checks: {} };
  if (readmeContent && readmeContent.length > 50) {
    // Installation instructions
    readmeQuality.checks.hasInstall = /install|setup|getting started|quick start|prerequisites/i.test(readmeContent);
    // Usage examples (code blocks with commands)
    const codeBlocks = (readmeContent.match(/```[\s\S]*?```/g) || []);
    readmeQuality.checks.hasCodeExamples = codeBlocks.length >= 1;
    readmeQuality.checks.codeBlockCount = codeBlocks.length;
    // API/function docs
    readmeQuality.checks.hasApiDocs = /api|function|method|parameter|argument|returns?|endpoint/i.test(readmeContent);
    // Contributing mention
    readmeQuality.checks.hasContributing = /contribut/i.test(readmeContent);
    // License mention
    readmeQuality.checks.hasLicenseMention = /license|licence|mit|apache|gpl|bsd/i.test(readmeContent);
    // Appropriate length (not too short for the repo size)
    const readmeWords = readmeContent.split(/\s+/).length;
    readmeQuality.checks.wordCount = readmeWords;
    readmeQuality.checks.appropriateLength = readmeWords >= 50 && readmeWords <= 5000;
    // Has sections/headings
    const headings = (readmeContent.match(/^#{1,3}\s+.+/gm) || []);
    readmeQuality.checks.hasStructure = headings.length >= 3;
    readmeQuality.checks.headingCount = headings.length;

    // Score
    let rScore = 0;
    if (readmeQuality.checks.hasInstall) rScore += 2;
    if (readmeQuality.checks.hasCodeExamples) rScore += 2;
    if (readmeQuality.checks.hasApiDocs) rScore += 1;
    if (readmeQuality.checks.hasContributing) rScore += 1;
    if (readmeQuality.checks.hasLicenseMention) rScore += 1;
    if (readmeQuality.checks.appropriateLength) rScore += 1;
    if (readmeQuality.checks.hasStructure) rScore += 2;
    readmeQuality.score = rScore;
  }
  results.readmeQuality = readmeQuality;

  // 12. Maintainability estimate
  if (v) console.error('Estimating maintainability...');
  const codeExts = ['js', 'ts', 'py', 'rb', 'go', 'rs', 'java', 'c', 'cpp', 'cs', 'php', 'swift', 'kt', 'scala', 'sol', 'move'];
  const codeFiles = files.filter(f => {
    const ext = f.split('.').pop()?.toLowerCase();
    return codeExts.includes(ext);
  });
  const configExts = ['json', 'yaml', 'yml', 'toml', 'xml', 'ini', 'cfg', 'env'];
  const configFiles2 = files.filter(f => {
    const ext = f.split('.').pop()?.toLowerCase();
    return configExts.includes(ext);
  });
  const docFiles = files.filter(f => /\.md$/i.test(f));

  // Directory depth
  const depths = files.map(f => f.split('/').length - 1);
  const maxDepth = depths.length > 0 ? Math.max(...depths) : 0;
  const avgDepth = depths.length > 0 ? depths.reduce((a, b) => a + b, 0) / depths.length : 0;

  // File sizes (from tree, we have blob sizes)
  const treeSizes = (treeRes.data?.tree || []).filter(t => t.type === 'blob').map(t => t.size || 0);
  const avgFileSize = treeSizes.length > 0 ? treeSizes.reduce((a, b) => a + b, 0) / treeSizes.length : 0;
  const maxFileSize = treeSizes.length > 0 ? Math.max(...treeSizes) : 0;
  const largeFiles = treeSizes.filter(s => s > 50000).length; // >50KB

  const maintainability = {
    codeFiles: codeFiles.length,
    configFiles: configFiles2.length,
    docFiles: docFiles.length,
    codeToDocRatio: docFiles.length > 0 ? Math.round(codeFiles.length / docFiles.length * 10) / 10 : codeFiles.length,
    maxDepth,
    avgDepth: Math.round(avgDepth * 10) / 10,
    avgFileSize: Math.round(avgFileSize),
    maxFileSize,
    largeFiles,
    score: 0,
    maxScore: 10,
  };

  // Score maintainability (scale-aware)
  const isMonorepo = files.some(f => /^(packages|apps|modules|libs)\//i.test(f));
  const generatedFilePattern = /(\bvendor\b|\.min\.(js|css)$|package-lock\.json|yarn\.lock|pnpm-lock\.yaml|\.lock$|\.generated\.|\.g\.dart$|\.pb\.go$)/i;
  const meaningfulLargeFileCount = largeFiles - files.filter(f => generatedFilePattern.test(f)).length;
  const hasTypeScript = files.some(f => /\.tsx?$/.test(f) && !f.includes('node_modules'));

  let mScore = 5;
  // Depth scoring — monorepos get slack
  const depthThreshold = isMonorepo ? 15 : 10;
  if (maxDepth <= 5) mScore += 1;
  else if (maxDepth > depthThreshold) mScore -= 1;
  // Large files — only count meaningful ones (exclude generated/vendored)
  if (meaningfulLargeFileCount <= 0) mScore += 1;
  else if (meaningfulLargeFileCount > 10) mScore -= 1;
  // Docs
  if (docFiles.length > 0) mScore += 1;
  // File count — scale-aware, no penalty for large well-structured projects
  if (codeFiles.length > 0 && codeFiles.length < 500) mScore += 1;
  else if (codeFiles.length >= 500 && !isMonorepo && docFiles.length === 0) mScore -= 1;
  // Avg file size
  if (avgFileSize < 10000) mScore += 1;
  // Positive signal: TypeScript
  if (hasTypeScript) mScore += 1;
  maintainability.score = Math.max(0, Math.min(10, mScore));
  results.maintainability = maintainability;

  // 12b. Typosquatting detection (Levenshtein distance)
  {
    const levenshtein = (a, b) => {
      const m = a.length, n = b.length;
      const d = Array.from({ length: m + 1 }, (_, i) => { const r = new Array(n + 1); r[0] = i; return r; });
      for (let j = 1; j <= n; j++) d[0][j] = j;
      for (let i = 1; i <= m; i++)
        for (let j = 1; j <= n; j++)
          d[i][j] = Math.min(d[i-1][j] + 1, d[i][j-1] + 1, d[i-1][j-1] + (a[i-1] !== b[j-1] ? 1 : 0));
      return d[m][n];
    };
    const knownNames = ['openclaw','clawhub','claude','anthropic','openai','chatgpt','copilot','cursor','windsurf','devin','codex','github','vercel','nextjs','react','vue','svelte','langchain','autogen','crewai','llamaindex','huggingface','ollama','vscode'];
    const repoLower = repo.toLowerCase();
    // Normalize: strip dots, hyphens for comparison (next.js → nextjs)
    const repoNormalized = repoLower.replace(/[.\-_]/g, '');
    // Common suffixes/prefixes that create legit derivatives (e.g., reactjs, vue3, claudeai)
    const legitSuffixes = ['js', 'ts', 'py', 'go', 'rs', 'ai', 'ml', 'ui', 'app', 'dev', 'cli', 'api', 'sdk', 'lib', 'kit', 'hub', 'pro', 'plus', 'next', 'v2', 'v3', 'v4', '2', '3', '4', '5'];
    for (const knownName of knownNames) {
      if (repoLower === knownName || repoNormalized === knownName) continue;
      // Skip if repo is just knownName + legit suffix or prefix (with or without separators)
      const isLegitDerivative = legitSuffixes.some(s =>
        repoNormalized === knownName + s || repoNormalized === s + knownName ||
        repoLower === knownName + '-' + s || repoLower === s + '-' + knownName ||
        repoLower === knownName + '.' + s || repoLower === s + '.' + knownName);
      if (isLegitDerivative) continue;
      const dist = levenshtein(repoLower, knownName);
      if (dist >= 1 && dist <= 2) {
        results.flags.push(`⚠️ Name "${repo}" is suspiciously similar to "${knownName}" — possible typosquatting`);
      }
    }
  }

  // 13. Plugin/package format detection
  if (v) console.error('Detecting plugin format...');
  const pluginFormats = [];

  // OpenClaw skill
  if (files.some(f => /^SKILL\.md$/i.test(f.split('/').pop()))) {
    const skillContent = await getRaw(`https://raw.githubusercontent.com/${owner}/${repo}/${r.default_branch}/SKILL.md`).catch(() => '');
    const hasFrontmatter = /^---\s*\n[\s\S]*?name:[\s\S]*?description:[\s\S]*?---/m.test(skillContent);
    pluginFormats.push({
      type: 'OpenClaw Skill',
      valid: hasFrontmatter,
      details: hasFrontmatter ? 'Valid SKILL.md with frontmatter' : 'SKILL.md found but missing required name/description frontmatter',
    });
  }

  // npm package
  if (files.some(f => f === 'package.json')) {
    const hasMain = readmeContent.includes('"main"') || readmeContent.includes('"exports"') || readmeContent.includes('"bin"');
    pluginFormats.push({
      type: 'npm package',
      valid: true,
      details: `package.json present${depInfo.totalDeps > 0 ? `, ${depInfo.totalDeps} deps` : ''}`,
    });
  }

  // GitHub Action
  if (files.some(f => f === 'action.yml' || f === 'action.yaml')) {
    pluginFormats.push({ type: 'GitHub Action', valid: true, details: 'action.yml found' });
  }

  // VS Code extension
  try {
    const pkgContent2 = await getRaw(`https://raw.githubusercontent.com/${owner}/${repo}/${r.default_branch}/package.json`).catch(() => '');
    if (pkgContent2 && pkgContent2.includes('"contributes"')) {
      pluginFormats.push({ type: 'VS Code Extension', valid: true, details: 'package.json with contributes field' });
    }
  } catch {}

  // Docker image
  if (files.some(f => /^Dockerfile$/i.test(f))) {
    pluginFormats.push({ type: 'Docker Image', valid: true, details: 'Dockerfile found' });
  }

  // Python package
  if (files.some(f => f === 'setup.py' || f === 'pyproject.toml' || f === 'setup.cfg')) {
    pluginFormats.push({ type: 'Python package', valid: true, details: 'Python packaging config found' });
  }

  results.pluginFormats = pluginFormats;

  // 14. License risk scoring
  if (v) console.error('Scoring license risk...');
  const licenseRisk = { license: r.license?.spdx_id || null, risk: 'unknown', details: '' };
  const permissive = ['MIT', 'Apache-2.0', 'BSD-2-Clause', 'BSD-3-Clause', 'ISC', 'Unlicense', '0BSD', 'CC0-1.0'];
  const copyleft = ['GPL-2.0', 'GPL-3.0', 'AGPL-3.0', 'LGPL-2.1', 'LGPL-3.0', 'MPL-2.0', 'EUPL-1.2'];
  const weak = ['LGPL-2.1', 'LGPL-3.0', 'MPL-2.0']; // copyleft but weaker
  if (!licenseRisk.license || licenseRisk.license === 'NOASSERTION') {
    // Check if there's a COPYING/LICENSE file even though GitHub API didn't detect it
    if (hasLicense) {
      licenseRisk.risk = 'low';
      licenseRisk.details = 'License file exists but not auto-detected by GitHub';
    } else {
      licenseRisk.risk = 'high';
      licenseRisk.details = 'No license — legally cannot use, fork, or modify';
      results.flags.push('No license detected — all rights reserved by default');
    }
  } else if (permissive.includes(licenseRisk.license)) {
    licenseRisk.risk = 'low';
    licenseRisk.details = `${licenseRisk.license} — permissive, safe for commercial use`;
  } else if (weak.includes(licenseRisk.license)) {
    licenseRisk.risk = 'medium';
    licenseRisk.details = `${licenseRisk.license} — weak copyleft, usable with care`;
  } else if (copyleft.includes(licenseRisk.license)) {
    licenseRisk.risk = 'high';
    licenseRisk.details = `${licenseRisk.license} — strong copyleft, derivatives must be open source`;
  } else {
    licenseRisk.risk = 'unknown';
    licenseRisk.details = `${licenseRisk.license} — uncommon license, review manually`;
  }
  results.licenseRisk = licenseRisk;

  // 15. Abandoned project detection
  if (v) console.error('Checking project health status...');
  const daysSincePush = (Date.now() - new Date(r.pushed_at).getTime()) / 86400000;
  let projectStatus = 'active';
  const abandonedSignals = [];

  if (r.archived) {
    projectStatus = 'archived';
    abandonedSignals.push('Repo is archived');
  } else if (daysSincePush > 365) {
    projectStatus = 'abandoned';
    abandonedSignals.push(`No commits in ${Math.floor(daysSincePush)} days`);
  } else if (daysSincePush > 180) {
    projectStatus = 'stale';
    abandonedSignals.push(`Last push ${Math.floor(daysSincePush)} days ago`);
  }

  // Check for unanswered issues
  if (r.has_issues && r.open_issues_count > 0) {
    const issuesRes = await get(`${base}/issues?state=open&sort=created&direction=asc&per_page=10`);
    const issues = (issuesRes.data || []).filter(i => !i.pull_request); // exclude PRs
    const oldUnanswered = issues.filter(i => {
      const age = (Date.now() - new Date(i.created_at).getTime()) / 86400000;
      return age > 90 && i.comments === 0;
    });
    if (oldUnanswered.length >= 3) {
      abandonedSignals.push(`${oldUnanswered.length} issues open 90+ days with zero responses`);
      if (projectStatus === 'active') projectStatus = 'neglected';
    }
  }

  results.projectStatus = { status: projectStatus, signals: abandonedSignals, daysSincePush: Math.floor(daysSincePush) };

  // 16. Enhanced Fork Comparison Module
  if (v) console.error('Running fork comparison analysis...');
  const forkAnalysis = { 
    isFork: r.fork, 
    parent: r.parent?.full_name || null,
    summary: null,
    quality: 'not-fork',
    score: 5, // neutral for non-forks
    findings: []
  };
  
  if (r.fork && r.parent) {
    try {
      const parentRes = await get(`https://api.github.com/repos/${r.parent.full_name}`);
      if (parentRes.data) {
        const p = parentRes.data;
        forkAnalysis.parentStars = p.stargazers_count;
        forkAnalysis.parentForks = p.forks_count;
        forkAnalysis.parentUpdated = p.pushed_at;
        forkAnalysis.parentSize = p.size;
        forkAnalysis.parentLanguage = p.language;
        forkAnalysis.parentLicense = p.license?.spdx_id || null;

        // Get parent contributors for comparison
        const parentContribRes = await get(`https://api.github.com/repos/${r.parent.full_name}/contributors?per_page=30`);
        const parentContribs = Array.isArray(parentContribRes.data) ? parentContribRes.data : [];
        
        // Compare commit counts via branches
        const compareRes = await get(`${base}/compare/${p.default_branch}...${r.default_branch}`);
        if (compareRes.data) {
          forkAnalysis.aheadBy = compareRes.data.ahead_by || 0;
          forkAnalysis.behindBy = compareRes.data.behind_by || 0;
          forkAnalysis.totalCommits = compareRes.data.total_commits || 0;
          forkAnalysis.changedFiles = compareRes.data.files?.length || 0;
          
          // Calculate percentage of files changed
          if (files.length > 0) {
            forkAnalysis.filesChangedPct = Math.round(forkAnalysis.changedFiles / files.length * 100);
          }

          // Analyze what types of files were changed
          const changedFileTypes = { code: 0, config: 0, docs: 0, ci: 0, security: 0, other: 0 };
          const suspiciousChanges = [];
          
          if (compareRes.data.files) {
            for (const file of compareRes.data.files) {
              const path = file.filename;
              const ext = path.split('.').pop()?.toLowerCase();
              
              // Categorize file changes
              if (/\.(js|ts|py|rb|go|rs|java|c|cpp|sol|move)$/i.test(path)) {
                changedFileTypes.code++;
              } else if (/\.(json|yaml|yml|toml|cfg|ini|env)$/i.test(path)) {
                changedFileTypes.config++;
              } else if (/\.(md|rst|txt)$/i.test(path) || /docs?\//i.test(path)) {
                changedFileTypes.docs++;
              } else if (/\.github\/workflows|\.circleci|\.travis|jenkinsfile/i.test(path)) {
                changedFileTypes.ci++;
                // Flag CI changes as potentially suspicious
                suspiciousChanges.push(`Modified CI: ${path}`);
              } else if (/security|\.security/i.test(path)) {
                changedFileTypes.security++;
                suspiciousChanges.push(`Modified security file: ${path}`);
              } else {
                changedFileTypes.other++;
              }

              // Check for suspicious file additions
              if (file.status === 'added') {
                if (/install|setup|deploy/i.test(path) && /\.(sh|py|js)$/i.test(path)) {
                  suspiciousChanges.push(`Added install script: ${path}`);
                }
                if (/wallet|address|mint|token/i.test(path)) {
                  suspiciousChanges.push(`Added crypto-related file: ${path}`);
                }
              }

              // Check for file deletions that remove security
              if (file.status === 'removed') {
                if (/test|spec/i.test(path)) {
                  suspiciousChanges.push(`Removed test file: ${path}`);
                } else if (/security|\.security/i.test(path)) {
                  suspiciousChanges.push(`Removed security file: ${path}`);
                } else if (/\.github\/workflows/i.test(path)) {
                  suspiciousChanges.push(`Removed CI workflow: ${path}`);
                }
              }
            }
          }

          forkAnalysis.changedFileTypes = changedFileTypes;
          forkAnalysis.suspiciousChanges = suspiciousChanges;

          // Compare contributors - find unique contributors vs parent
          const forkContribEmails = new Set(r.commits.authors.map(a => a.email));
          const parentContribLogins = new Set(parentContribs.map(c => c.login));
          
          // Try to match by looking up GitHub users
          let uniqueContributors = 0;
          for (const author of r.commits.authors) {
            // Simple heuristic: if email doesn't match known parent contributors
            // This is a rough approximation since we'd need email->GitHub mapping
            const hasCommonWork = false; // Would need more API calls to determine
            if (!hasCommonWork) uniqueContributors++;
          }
          
          forkAnalysis.uniqueContributors = uniqueContributors;
          forkAnalysis.parentContributors = parentContribs.length;

          // Quality assessment
          let qualityScore = 5;
          let quality = 'unknown';
          const findings = [];

          if (forkAnalysis.aheadBy === 0 && forkAnalysis.behindBy === 0) {
            quality = 'identical';
            qualityScore = 0;
            findings.push('Identical to parent - no original work');
            results.flags.push(`Fork of ${r.parent.full_name} with 0 changes — no original work`);
          } else if (forkAnalysis.aheadBy === 0) {
            quality = 'outdated';
            qualityScore = 1;
            findings.push(`${forkAnalysis.behindBy} commits behind parent`);
          } else if (forkAnalysis.aheadBy < 5 && changedFileTypes.docs > changedFileTypes.code * 2) {
            quality = 'cosmetic';
            qualityScore = 2;
            findings.push('Mostly documentation/cosmetic changes');
            results.warnings.push('Fork appears to be mostly cosmetic changes');
          } else if (suspiciousChanges.length > 0) {
            quality = 'suspicious';
            qualityScore = 1;
            findings.push(`Suspicious changes: ${suspiciousChanges.slice(0, 3).join(', ')}${suspiciousChanges.length > 3 ? '...' : ''}`);
            for (const sc of suspiciousChanges) {
              results.flags.push(`Fork modification: ${sc}`);
            }
          } else if (forkAnalysis.aheadBy >= 20 && changedFileTypes.code > 0 && uniqueContributors > 0) {
            quality = 'meaningful';
            qualityScore = 8;
            findings.push('Substantial divergence with original development');
          } else if (changedFileTypes.code === 0 && changedFileTypes.config + changedFileTypes.docs > 0) {
            quality = 'configuration';
            qualityScore = 4;
            findings.push('Only configuration/documentation changes');
          } else {
            quality = 'diverged';
            qualityScore = 6;
            findings.push('Some original development work');
          }

          // Check for "gutted fork" - removes tests, CI, security features
          const removedCritical = suspiciousChanges.filter(c => c.includes('Removed')).length;
          if (removedCritical >= 2) {
            quality = 'gutted';
            qualityScore = 0;
            findings.push(`Gutted fork - removed ${removedCritical} critical features`);
            results.flags.push(`Gutted fork: removed tests/CI/security from ${r.parent.full_name}`);
          }

          forkAnalysis.quality = quality;
          forkAnalysis.score = qualityScore;
          forkAnalysis.findings = findings;

          // Generate summary
          let summary = `Fork of ${r.parent.full_name}`;
          if (forkAnalysis.parentStars > 0) {
            summary += ` (${forkAnalysis.parentStars.toLocaleString()}⭐)`;
          }
          summary += ` — ${forkAnalysis.aheadBy} commits ahead, ${forkAnalysis.behindBy} behind`;
          if (forkAnalysis.filesChangedPct > 0) {
            summary += `, modified ${forkAnalysis.filesChangedPct}% of files`;
          }
          if (suspiciousChanges.length > 0) {
            summary += `, ${suspiciousChanges.length} suspicious change${suspiciousChanges.length > 1 ? 's' : ''}`;
          }
          
          // Add status emoji
          const statusEmoji = {
            'identical': '',
            'outdated': '',
            'cosmetic': '🎨',
            'configuration': '⚙️',
            'diverged': '🔀',
            'meaningful': '✅',
            'suspicious': '⚠️',
            'gutted': '🗑️'
          };
          if (statusEmoji[quality]) {
            summary += ` ${statusEmoji[quality]}`;
          }

          forkAnalysis.summary = summary;
        }

        // Compare basic metadata
        if (r.language !== p.language && p.language) {
          forkAnalysis.findings.push(`Language changed from ${p.language} to ${r.language || 'unknown'}`);
          results.warnings.push(`Fork changed primary language from ${p.language} to ${r.language || 'unknown'}`);
        }

        if (r.license?.spdx_id !== p.license?.spdx_id && p.license) {
          forkAnalysis.findings.push(`License changed from ${p.license.spdx_id} to ${r.license?.spdx_id || 'none'}`);
          if (!r.license?.spdx_id) {
            results.flags.push(`Fork removed license (was ${p.license.spdx_id})`);
          }
        }

      }
    } catch (e) {
      if (v) console.error(`Fork analysis error: ${e.message}`);
      forkAnalysis.error = e.message;
    }
  }
  
  results.forkAnalysis = forkAnalysis;

  // 17. Commit velocity trends
  if (v) console.error('Analyzing commit velocity...');
  const velocityTrend = { trend: 'unknown', periods: [] };
  if (commitDates.length >= 10) {
    const mid = Math.floor(commitDates.length / 2);
    const recentHalf = commitDates.slice(0, mid);
    const olderHalf = commitDates.slice(mid);

    const recentSpan = recentHalf.length > 1 ? (recentHalf[0] - recentHalf[recentHalf.length - 1]) / 86400000 : 1;
    const olderSpan = olderHalf.length > 1 ? (olderHalf[0] - olderHalf[olderHalf.length - 1]) / 86400000 : 1;

    const recentRate = recentHalf.length / Math.max(recentSpan, 1);
    const olderRate = olderHalf.length / Math.max(olderSpan, 1);

    velocityTrend.recentRate = Math.round(recentRate * 100) / 100;
    velocityTrend.olderRate = Math.round(olderRate * 100) / 100;

    if (recentRate > olderRate * 1.5) velocityTrend.trend = 'accelerating';
    else if (recentRate < olderRate * 0.5) velocityTrend.trend = 'declining';
    else velocityTrend.trend = 'steady';
  }
  results.velocityTrend = velocityTrend;

  // 18. Issue response time
  if (v) console.error('Checking issue response time...');
  const issueResponse = { avgResponseHrs: null, respondedPct: null, sampleSize: 0 };
  if (r.has_issues) {
    try {
      const closedIssuesRes = await get(`${base}/issues?state=closed&sort=updated&direction=desc&per_page=15`);
      const closedIssues = Array.isArray(closedIssuesRes.data) ? closedIssuesRes.data.filter(i => !i.pull_request) : [];
      let totalResponseMs = 0;
      let responded = 0;

      for (const issue of closedIssues.slice(0, 10)) {
        if (issue.comments > 0) {
          // First comment time approximation: use closed_at as rough proxy if fast
          const created = new Date(issue.created_at);
          const closed = new Date(issue.closed_at);
          const responseMs = closed - created;
          totalResponseMs += responseMs;
          responded++;
        }
      }

      issueResponse.sampleSize = closedIssues.slice(0, 10).length;
      if (responded > 0) {
        issueResponse.avgResponseHrs = Math.round(totalResponseMs / responded / 3600000);
        issueResponse.respondedPct = Math.round(responded / issueResponse.sampleSize * 100);
      }
    } catch {}
  }
  results.issueResponse = issueResponse;

  // 19. PR merge patterns
  if (v) console.error('Analyzing PR patterns...');
  const prPatterns = { selfMerged: 0, reviewed: 0, total: 0, pattern: 'unknown' };
  try {
    const prsRes = await get(`${base}/pulls?state=closed&sort=updated&direction=desc&per_page=20`);
    const prs = (prsRes.data || []).filter(p => p.merged_at);

    for (const pr of prs.slice(0, 15)) {
      prPatterns.total++;
      if (pr.user?.login === pr.merged_by?.login) {
        prPatterns.selfMerged++;
      } else {
        prPatterns.reviewed++;
      }
    }

    if (prPatterns.total >= 3) {
      const selfRate = prPatterns.selfMerged / prPatterns.total;
      if (selfRate > 0.8) {
        prPatterns.pattern = 'self-merge';
        if (Object.keys(authors).length > 2) {
          results.warnings.push('Team project but 80%+ PRs are self-merged — minimal review');
        }
      } else if (selfRate < 0.3) {
        prPatterns.pattern = 'reviewed';
      } else {
        prPatterns.pattern = 'mixed';
      }
    }
  } catch {}
  results.prPatterns = prPatterns;

  // 20. Copy-paste / template detector
  if (v) console.error('Detecting copy-paste code...');
  const copyPaste = { isTemplate: false, templateMatch: null, signals: [] };

  // Check for known Solidity templates (OpenZeppelin, etc.)
  const solFiles = files.filter(f => /\.sol$/i.test(f));
  if (solFiles.length > 0) {
    // Sample a few solidity files for import patterns
    const sampleFiles = solFiles.slice(0, 5);
    let ozImports = 0;
    let totalImports = 0;

    for (const sf of sampleFiles) {
      try {
        const content = await getRaw(`https://raw.githubusercontent.com/${owner}/${repo}/${r.default_branch}/${sf}`);
        if (content) {
          const imports = (content.match(/import\s+.*?[;"]/g) || []);
          totalImports += imports.length;
          ozImports += imports.filter(i => /openzeppelin/i.test(i)).length;

          // Check for exact copy signals
          if (/SPDX-License-Identifier/i.test(content) && content.length < 500 && imports.length > 2) {
            copyPaste.signals.push(`${sf} — very short file with many imports (likely wrapper)`);
          }
        }
      } catch {}
    }

    if (totalImports > 0 && ozImports / totalImports > 0.7) {
      copyPaste.signals.push(`${Math.round(ozImports/totalImports*100)}% of imports are OpenZeppelin — mostly boilerplate`);
      if (solFiles.length <= 5) {
        copyPaste.isTemplate = true;
        copyPaste.templateMatch = 'OpenZeppelin boilerplate';
      }
    }
  }

  // Check for cookie-cutter repo signals
  if (readmeContent) {
    // Template README patterns
    const templatePhrases = [
      /this project was bootstrapped with/i,
      /created with create-react-app/i,
      /built with hardhat/i,
      /generated by/i,
      /forked from/i,
      /starter template/i,
    ];
    for (const tp of templatePhrases) {
      if (tp.test(readmeContent)) {
        copyPaste.signals.push(`README mentions: "${readmeContent.match(tp)[0]}"`);
      }
    }
  }

  // Extremely low unique code ratio (few code files, lots of config/boilerplate)
  const codeRatio = codeFiles.length / Math.max(files.length, 1);
  if (codeRatio < 0.1 && files.length > 20) {
    copyPaste.signals.push(`Only ${Math.round(codeRatio*100)}% code files — mostly config/boilerplate`);
  }

  results.copyPaste = copyPaste;

  // 21. Funding/backer verification
  if (v) console.error('Verifying funding claims...');
  const backerVerification = { claims: [], verified: [], unverified: [] };

  // Check README for backer/investor claims
  if (readmeContent) {
    const backerPatterns = {
      'a16z': /a16z|andreessen\s*horowitz/i,
      'Paradigm': /paradigm/i,
      'Sequoia': /sequoia/i,
      'Polychain': /polychain/i,
      'Multicoin': /multicoin/i,
      'Binance Labs': /binance\s*labs/i,
      'Coinbase Ventures': /coinbase\s*ventures/i,
      'Framework Ventures': /framework\s*ventures/i,
      'Pantera': /pantera/i,
      'Jump Crypto': /jump\s*(crypto|trading)/i,
      'Dragonfly': /dragonfly/i,
      'Galaxy Digital': /galaxy\s*digital/i,
      'Electric Capital': /electric\s*capital/i,
      'Solana Foundation': /solana\s*(foundation|ventures)/i,
      'Ethereum Foundation': /ethereum\s*foundation/i,
      'Google': /backed by google|google ventures|google cloud partner/i,
      'Microsoft': /backed by microsoft|microsoft partner/i,
    };

    // Map backers to known GitHub orgs for cross-reference
    const backerOrgs = {
      'a16z': ['a16z', 'a16z-infra'],
      'Paradigm': ['paradigmxyz'],
      'Solana Foundation': ['solana-labs', 'solana-foundation'],
      'Ethereum Foundation': ['ethereum'],
      'Coinbase Ventures': ['coinbase'],
      'Binance Labs': ['binance', 'bnb-chain'],
    };

    for (const [name, pattern] of Object.entries(backerPatterns)) {
      if (pattern.test(readmeContent)) {
        backerVerification.claims.push(name);

        // Try to verify: check if any committers are in the backer's org
        let foundOrgLink = false;
        if (backerOrgs[name]) {
          for (const av of authorVerification) {
            if (!av.githubUser) continue;
            try {
              const orgsRes = await get(`https://api.github.com/users/${av.githubUser}/orgs`);
              const userOrgs = (orgsRes.data || []).map(o => o.login.toLowerCase());
              if (backerOrgs[name].some(bo => userOrgs.includes(bo.toLowerCase()))) {
                foundOrgLink = true;
                backerVerification.verified.push(`${name} — committer @${av.githubUser} is in their org`);
                break;
              }
            } catch {}
          }
        }

        if (!foundOrgLink) {
          backerVerification.unverified.push(`${name} — claimed in README but no committer linked to their org`);
        }
      }
    }
  }

  results.backerVerification = backerVerification;

  // Helper: scan documentation for fake/suspicious prerequisites
  function scanDocForPrereqs(content, fileName, repoName) {
    const criticals = [];
    const warnings = [];
    if (!content) return { criticals, warnings };

    // Pattern 1: Suspicious download links to executables
    const urlRegex = /https?:\/\/[^\s'"`)>\]]+/gi;
    const urls = content.match(urlRegex) || [];
    for (const url of urls) {
      const lower = url.toLowerCase();
      // Skip GitHub releases and known corporate domains
      if (/github\.com\/[^/]+\/[^/]+\/releases\/download\//i.test(url)) continue;
      if (/aka\.ms|apple\.com|microsoft\.com|google\.com|amazonaws\.com|cloudfront\.net|npmjs\.com|pypi\.org|nodejs\.org|python\.org|rust-lang\.org|golang\.org|go\.dev|ruby-lang\.org|java\.com|oracle\.com|cmake\.org|llvm\.org|gcc\.gnu\.org|visualstudio\.com|jetbrains\.com|docker\.com|brew\.sh|chocolatey\.org|kernel\.org/i.test(url)) continue;
      // Flag executable download links (check path, not domain — .app is also a TLD)
      let urlPath = '';
      try { urlPath = new URL(url).pathname; } catch {}
      if (/\.(dmg|pkg|exe|msi|deb|rpm|appimage)(\?|$)/i.test(urlPath) || /\.app(\?|$)/i.test(urlPath)) {
        criticals.push(`${fileName} links to executable download: ${url} — possible malware distribution`);
      }
      // Flag suspicious file hosting services
      if (/drive\.google\.com\/.*\/download|dropbox\.com\/.*\/dl|mega\.nz/i.test(url)) {
        criticals.push(`${fileName} links to executable download: ${url} — possible malware distribution`);
      }
      // Flag non-GitHub /download/ or /releases/download/ links (skip known safe domains)
      if (/\/download\/|\/releases\/download\//i.test(url) && !/github\.com/i.test(url) && !/aka\.ms|apple\.com|microsoft\.com|google\.com|nodejs\.org|python\.org|rust-lang\.org|golang\.org|go\.dev|ruby-lang\.org|cmake\.org|llvm\.org|docker\.com|brew\.sh|visualstudio\.com|jetbrains\.com|kernel\.org/i.test(url)) {
        criticals.push(`${fileName} links to executable download: ${url} — possible malware distribution`);
      }
    }

    // Pattern 2: Suspicious install commands for unrecognized packages
    const safeBrew = new Set(['node', 'nodejs', 'python', 'python3', 'python@3', 'git', 'gh', 'jq', 'curl', 'wget', 'ffmpeg', 'imagemagick', 'postgresql', 'redis', 'sqlite', 'sqlite3', 'cmake', 'go', 'golang', 'rust', 'rustup', 'ruby', 'java', 'openjdk', 'docker', 'kubernetes', 'kubectl', 'helm', 'terraform', 'ansible', 'nginx', 'httpd', 'openssl', 'gcc', 'make', 'automake', 'autoconf', 'pkg-config', 'libssl-dev', 'libuv', 'protobuf', 'grpc', 'tmux', 'vim', 'neovim', 'ripgrep', 'fd', 'bat', 'fzf', 'tree', 'htop', 'watchman']);
    const safePip = new Set(['pip', 'pip3', 'setuptools', 'wheel', 'virtualenv', 'venv', 'poetry', 'pipenv', 'flask', 'django', 'fastapi', 'uvicorn', 'gunicorn', 'numpy', 'pandas', 'scipy', 'matplotlib', 'requests', 'httpx', 'aiohttp', 'pytest', 'black', 'ruff', 'mypy', 'pylint', 'torch', 'tensorflow', 'transformers', 'langchain', 'openai', 'anthropic', 'boto3', 'pydantic', 'sqlalchemy', 'celery', 'redis', 'psycopg2', 'pillow']);
    const safeNpm = new Set(['npm', 'yarn', 'pnpm', 'bun', 'typescript', 'ts-node', 'tsx', 'eslint', 'prettier', 'jest', 'mocha', 'vitest', 'nodemon', 'pm2', 'openclaw', 'clawhub', 'turbo', 'nx', 'lerna', 'vercel', 'netlify-cli', 'wrangler', 'serve', 'http-server', 'concurrently', 'dotenv-cli', 'node-gyp', 'prebuild-install', 'node-pre-gyp', 'cmake-js', 'napi-build-utils']);
    const repoLower = (repoName || '').toLowerCase();

    // brew install
    const brewMatches = content.matchAll(/brew\s+install\s+([\w@./-]+)/gi);
    for (const m of brewMatches) {
      const pkg = m[1].toLowerCase();
      if (!safeBrew.has(pkg)) {
        warnings.push(`${fileName} suggests installing unrecognized package: brew install ${m[1]} — verify this is legitimate`);
      }
    }
    // pip install (not -r)
    const pipMatches = content.matchAll(/pip3?\s+install\s+(?!-r\b)([\w.-]+)/gi);
    for (const m of pipMatches) {
      const pkg = m[1].toLowerCase();
      if (!safePip.has(pkg) && pkg !== repoLower) {
        warnings.push(`${fileName} suggests installing unrecognized package: pip install ${m[1]} — verify this is legitimate`);
      }
    }
    // npm install -g
    const npmGMatches = content.matchAll(/npm\s+install\s+-g\s+([\w@./-]+)/gi);
    for (const m of npmGMatches) {
      const pkg = m[1].toLowerCase().replace(/^@[^/]+\//, '');
      if (!safeNpm.has(pkg) && pkg !== repoLower) {
        warnings.push(`${fileName} suggests installing unrecognized package: npm install -g ${m[1]} — verify this is legitimate`);
      }
    }
    // apt/yum/apk — check each package against safe list
    const safeSys = new Set(['git', 'curl', 'wget', 'build-essential', 'gcc', 'g++', 'make', 'cmake', 'python3', 'python3-pip', 'python3-venv', 'python3-dev', 'nodejs', 'npm', 'ruby', 'golang', 'default-jdk', 'openjdk-17-jdk', 'docker.io', 'docker-ce', 'nginx', 'redis-server', 'postgresql', 'sqlite3', 'libssl-dev', 'libffi-dev', 'pkg-config', 'ca-certificates', 'gnupg', 'lsb-release', 'apt-transport-https', 'software-properties-common', 'unzip', 'zip', 'tar', 'gzip', 'jq', 'ffmpeg', 'imagemagick', 'htop', 'tmux', 'vim', 'neovim', 'openssh-client', 'openssh-server', '-y', '--yes', '--no-install-recommends', 'libx11-dev', 'libxtst-dev', 'libxext-dev', 'libxi-dev', 'libxinerama-dev', 'libxrandr-dev', 'libxcursor-dev', 'libpng-dev', 'libpng++-dev', 'libjpeg-dev', 'libgif-dev', 'libcairo2-dev', 'libpango1.0-dev', 'librsvg2-dev', 'libgtk-3-dev', 'libwebkit2gtk-4.0-dev', 'libasound2-dev', 'libpulse-dev', 'libdbus-1-dev', 'libudev-dev', 'libusb-1.0-0-dev', 'libevdev-dev', 'zlib1g-dev', 'libbz2-dev', 'liblzma-dev', 'libreadline-dev', 'libncurses5-dev', 'libncursesw5-dev', 'libsqlite3-dev', 'tk-dev', 'libgdbm-dev', 'libnss3-dev', 'libgmp-dev', 'libmpfr-dev', 'libmpc-dev']);
    const sysInstallMatches = content.matchAll(/(?:apt|apt-get|yum|apk)\s+(?:install|add)\s+([^\n]+)/gi);
    for (const m of sysInstallMatches) {
      const pkgs = m[1].split(/\s+/).map(p => p.replace(/[`'")}\].,;:]+$/g, '')).filter(p => p && !p.startsWith('-') || p === '-y' || p === '--yes');
      const unknownPkgs = pkgs.filter(p => !p.startsWith('-') && !safeSys.has(p.toLowerCase()) && !/^lib.*-dev$/.test(p.toLowerCase()));
      if (unknownPkgs.length > 0) {
        warnings.push(`${fileName} suggests installing unrecognized system package(s): ${unknownPkgs.join(', ')} — verify these are legitimate`);
      }
    }

    // Pattern 3: Social engineering — disabling security controls
    const securityDisablePatterns = [
      /disable\s+antivirus/i,
      /disable\s+gatekeeper/i,
      /allow\s+anyway/i,
      /security\s+preferences/i,
      /spctl\s+--master-disable/i,
      /run\s+as\s+administrator/i,
      /disable\s+SIP/i,
      /csrutil\s+disable/i,
      /trust\s+this\s+certificate/i,
      /add\s+exception/i,
    ];
    for (const pat of securityDisablePatterns) {
      const match = content.match(pat);
      if (match) {
        criticals.push(`${fileName} instructs disabling security controls: "${match[0]}"`);
      }
    }
    // Download and run script from non-GitHub URL — warning for known domains, critical for unknown
    const scriptDlRun = content.matchAll(/(?:curl|wget)\s+[^\n]*?(https?:\/\/(?!github\.com|raw\.githubusercontent\.com)[^\s'"]+)\s*\|/gi);
    for (const m of scriptDlRun) {
      const cmdUrl = m[1] || '';
      // If URL matches the repo owner's domain, downgrade to warning (it's their own install script)
      const ownerDomain = repoName ? repoName.toLowerCase() : '';
      const isOwnDomain = ownerDomain && cmdUrl.toLowerCase().includes(ownerDomain);
      if (isOwnDomain) {
        warnings.push(`${fileName} uses curl|sh install from own domain: "${m[0].trim().substring(0, 80)}" — standard but runs unaudited code`);
      } else {
        criticals.push(`${fileName} uses curl|sh install from unknown URL: "${m[0].trim().substring(0, 80)}" — executes unaudited remote code`);
      }
    }

    return { criticals, warnings };
  }

  // 22. Agent safety / security risk assessment
  if (v) console.error('Running security risk assessment...');
  const agentSafety = { verdict: 'PASS', critical: [], warning: [], info: [] };

  // 22a. Install script analysis (package.json hooks)
  try {
    const pkgContent3 = await getRaw(`https://raw.githubusercontent.com/${owner}/${repo}/${r.default_branch}/package.json`);
    if (pkgContent3 && !pkgContent3.includes('404')) {
      const pkg3 = JSON.parse(pkgContent3);
      const dangerousHooks = ['preinstall', 'postinstall', 'install', 'prepare'];
      for (const hook of dangerousHooks) {
        if (pkg3.scripts?.[hook]) {
          const script = pkg3.scripts[hook];
          // Check what the hook does
          if (/curl|wget|fetch|http|eval|exec|bash|sh -c/i.test(script)) {
            agentSafety.critical.push(`package.json "${hook}" hook runs: "${script}" — executes code on install`);
          } else {
            agentSafety.warning.push(`package.json has "${hook}" hook: "${script}"`);
          }
        }
      }
    }
  } catch {}

  // 22b. Prompt injection detection — scan markdown files for injection patterns
  const mdFiles = files.filter(f => /\.md$/i.test(f) && !f.includes('node_modules'));
  const injectionPatterns = [
    // English patterns
    { pattern: /ignore\s+(all\s+)?previous\s+instructions/i, name: 'instruction override' },
    { pattern: /you\s+are\s+now\s+(a|an|my|the|acting)\s/i, name: 'persona hijack' },
    { pattern: /system\s*:\s*you/i, name: 'system prompt injection' },
    { pattern: /do\s+not\s+reveal\s+(your|the|any|this)|never\s+mention\s+this\s+(prompt|instruction|system)/i, name: 'secrecy instruction' },
    { pattern: /\{%|<%|<\?/g, name: 'template injection syntax' },
    { pattern: /<!--[\s\S]*?(ignore|override|inject|system|prompt)[\s\S]*?-->/i, name: 'hidden HTML comment with instructions' },
    { pattern: /\[INST\]|\[\/INST\]|<\|im_start\|>|<\|system\|>/i, name: 'model prompt format tokens' },
    { pattern: /assistant:\s*["']?I\s+(will|should|must)/i, name: 'fake assistant response' },
    // Multilingual prompt injection — the $37.5K bypass technique
    // Thai
    { pattern: /เพิกเฉยคำสั่ง|ละเว้นคำแนะนำ|คุณคือตอนนี้|ระบบ\s*:\s*คุณ/i, name: 'Thai prompt injection' },
    // Arabic
    { pattern: /تجاهل\s*(جميع\s*)?التعليمات|أنت\s+الآن|نظام\s*:\s*أنت|لا\s+تكشف/i, name: 'Arabic prompt injection' },
    // Chinese (Simplified + Traditional)
    { pattern: /忽略(所有)?之前的指[令示]|你现在是|系统\s*[:：]\s*你|不要透露|忽略(所有)?之前的指[令示]|你現在是/i, name: 'Chinese prompt injection' },
    // Russian
    { pattern: /игнорируй\s+(все\s+)?предыдущие\s+инструкции|ты\s+теперь|система\s*:\s*ты/i, name: 'Russian prompt injection' },
    // Spanish
    { pattern: /ignora\s+(todas?\s+)?las?\s+instrucciones\s+anteriores|ahora\s+eres|sistema\s*:\s*tú/i, name: 'Spanish prompt injection' },
    // French
    { pattern: /ignore[rz]?\s+(toutes?\s+)?les?\s+instructions\s+précédentes|tu\s+es\s+maintenant|système\s*:\s*tu/i, name: 'French prompt injection' },
    // Japanese
    { pattern: /以前の指示を無視|あなたは今|システム\s*[:：]\s*あなた/i, name: 'Japanese prompt injection' },
    // Korean
    { pattern: /이전\s*지시를?\s*무시|너는\s*이제|시스템\s*[:：]\s*너/i, name: 'Korean prompt injection' },
    // Hindi
    { pattern: /पिछले\s*निर्देशों?\s*को\s*अनदेखा|अब\s*तुम|सिस्टम\s*:\s*तुम/i, name: 'Hindi prompt injection' },
    // Portuguese
    { pattern: /ignore\s+(todas?\s+)?as?\s+instruções\s+anteriores|você\s+agora\s+é|sistema\s*:\s*você/i, name: 'Portuguese prompt injection' },
    // German
    { pattern: /ignoriere?\s+(alle\s+)?vorherigen\s+Anweisungen|du\s+bist\s+jetzt|System\s*:\s*du/i, name: 'German prompt injection' },
    // Mixed-script / polyglot evasion (e.g., mixing Latin + CJK + Arabic in same line to confuse filters)
    { pattern: /[\u0600-\u06FF].*ignore.*instruction|ignore.*[\u0600-\u06FF].*instruction/i, name: 'mixed-script injection evasion (Arabic+Latin)' },
    { pattern: /[\u0E00-\u0E7F].*ignore.*instruction|ignore.*[\u0E00-\u0E7F].*instruction/i, name: 'mixed-script injection evasion (Thai+Latin)' },
    // Unicode homoglyph attack (Cyrillic/Greek chars masquerading as Latin)
    { pattern: /[\u0400-\u04FF][\u0041-\u005A\u0061-\u007A]{3,}|[\u0041-\u005A\u0061-\u007A]{3,}[\u0400-\u04FF]/i, name: 'Unicode homoglyph mixing (Cyrillic+Latin)' },
  ];

  // Sample up to 10 markdown files (prioritize SKILL.md, README, install docs)
  const priorityMds = mdFiles.filter(f => /skill\.md|readme|install|setup|getting.started/i.test(f));
  const otherMds = mdFiles.filter(f => !priorityMds.includes(f));
  const mdSample = [...priorityMds, ...otherMds].slice(0, 10);

  for (const mdFile of mdSample) {
    try {
      const mdContent = await getRaw(`https://raw.githubusercontent.com/${owner}/${repo}/${r.default_branch}/${mdFile}`);
      if (!mdContent || mdContent.includes('404: Not Found')) continue;

      for (const { pattern, name } of injectionPatterns) {
        if (pattern.test(mdContent)) {
          const isSkill = /skill\.md/i.test(mdFile);
          const level = isSkill ? 'critical' : 'warning';
          agentSafety[level].push(`${mdFile}: prompt injection pattern — ${name}`);
        }
      }

      // Check for hidden unicode / zero-width characters (steganographic injection)
      const zwChars = mdContent.match(/[\u200B\u200C\u200D\u2060\uFEFF]/g);
      if (zwChars && zwChars.length > 5) {
        agentSafety.warning.push(`${mdFile}: ${zwChars.length} zero-width characters — possible steganographic injection`);
      }
    } catch {}
  }

  // 22c. Credential harvesting — scan code for patterns that read AND exfiltrate secrets
  const codeFileSample = files.filter(f => /\.(js|ts|py|sh|rb)$/i.test(f)
    && !f.includes('node_modules') && !f.includes('vendor') && !f.includes('dist/')
    && !f.includes('.github/') && !/\b(bundled|compiled|generated|\.min\.)\b/i.test(f)).slice(0, 15);
  const credReadPatterns = [
    /\.openclaw|openclaw\.json/i,
    /\.env\b(?!\.example|\.sample|\.template)/i,
    /api[_-]?key|secret[_-]?key|private[_-]?key|wallet|mnemonic|seed.?phrase/i,
    /\.ssh\/|id_rsa|id_ed25519/i,
    /credentials|\.aws\/|\.kube\/config/i,
  ];
  const exfilPatterns = [
    /fetch\s*\(|https?\.request|requests\.(get|post)|urllib/i,
    /webhook|discord\.com\/api|telegram\..*sendMessage/i,
    /upload|exfil|transmit|beacon/i,
    /btoa|Buffer\.from.*base64|encode.*send/i,
  ];

  for (const codeFile of codeFileSample) {
    try {
      const codeContent = await getRaw(`https://raw.githubusercontent.com/${owner}/${repo}/${r.default_branch}/${codeFile}`);
      if (!codeContent || codeContent.includes('404: Not Found')) continue;

      // Skip minified/bundled/vendored files (they trigger everything)
      const avgLineLen = codeContent.length / Math.max(codeContent.split('\n').length, 1);
      if (avgLineLen > 500) { agentSafety.info.push(`${codeFile}: skipped (minified/bundled)`); continue; }
      if (codeContent.length > 500000) { agentSafety.info.push(`${codeFile}: skipped (>500KB, likely vendored)`); continue; }

      const readsCredentials = credReadPatterns.some(p => p.test(codeContent));
      const hasExfil = exfilPatterns.some(p => p.test(codeContent));

      // Exclude legitimate API usage: if all URLs in the file point to known APIs
      const allUrls = codeContent.match(/https?:\/\/[^\s'"`)]+/g) || [];
      const legitDomains = ['api.github.com', 'github.com', 'raw.githubusercontent.com', 'registry.npmjs.org', 'pypi.org', 'crates.io', 'api.hyperliquid.xyz', 'localhost', '127.0.0.1'];
      const unknownUrls = allUrls.filter(u => { try { const h = new URL(u).hostname; return !legitDomains.some(d => h === d || h.endsWith('.' + d)); } catch { return false; } });
      // If file has network calls but ALL URLs are to legit domains, it's likely just an API client
      const onlyLegitNetwork = allUrls.length > 0 && unknownUrls.length === 0;

      if (readsCredentials && hasExfil && !onlyLegitNetwork) {
        agentSafety.critical.push(`${codeFile}: reads credentials AND has outbound network — possible exfiltration`);
      } else if (readsCredentials && hasExfil && onlyLegitNetwork) {
        agentSafety.info.push(`${codeFile}: reads credentials for legitimate API auth (GitHub/npm/PyPI)`);
      } else if (readsCredentials) {
        // Reading creds isn't inherently bad (configs do it), only flag if suspicious context
        const linesWithCreds = codeContent.split('\n').filter(l => credReadPatterns.some(p => p.test(l)));
        if (linesWithCreds.some(l => /read|open|load|parse|require/i.test(l) && /\.openclaw|\.ssh/i.test(l))) {
          agentSafety.warning.push(`${codeFile}: reads sensitive paths (.openclaw, .ssh, etc.)`);
        }
      }

      // Check for obfuscation in code files
      const b64Blobs = codeContent.match(/['"][A-Za-z0-9+\/]{50,}={0,2}['"]/g);
      if (b64Blobs && b64Blobs.length >= 2) {
        agentSafety.warning.push(`${codeFile}: ${b64Blobs.length} large base64 strings — possible obfuscated payloads`);
      }

      // Hex-encoded payloads
      if (/\\x[0-9a-f]{2}.*\\x[0-9a-f]{2}.*\\x[0-9a-f]{2}/i.test(codeContent)) {
        agentSafety.warning.push(`${codeFile}: hex-encoded byte sequences — obfuscated content`);
      }

      // Crypto mining patterns
      if (/stratum\+tcp|coinhive|cryptonight|hashrate|mining.*pool/i.test(codeContent)) {
        agentSafety.critical.push(`${codeFile}: crypto mining patterns detected`);
      }

      // Reverse shell patterns
      const reverseShellPatterns = [
        /\/bin\/(?:ba)?sh\s+-i\s+>&\s*\/dev\/tcp\//,
        /\bnc\s+-[ec]\s+\/bin\/(?:sh|bash)/,
        /\bncat\s+-e\b/,
        /\bsocat\s+exec:/i,
        /\bmkfifo\s+\/tmp\/.*(?:nc|cat)\b/,
        /\bpython3?\s+-c\b.*socket.*connect/s,
        /\bruby\s+-rsocket\b/,
        /\bperl\s+-e\b.*socket.*INET/s,
        /\bphp\s+-r\b.*fsockopen/s,
        /\bbash\s+-c\b.*exec.*socket/s,
        /exec\s+\d+<>\/dev\/tcp\//,
      ];
      for (const rsp of reverseShellPatterns) {
        if (rsp.test(codeContent)) {
          agentSafety.critical.push(`${codeFile}: reverse shell pattern detected`);
          break;
        }
      }

      // Keylogger patterns
      const keyloggerPatterns = [
        /addEventListener\s*\(\s*['"]key(?:down|press|up)['"]/,
        /navigator\.clipboard/,
        /document\.execCommand\s*\(\s*['"]copy['"]/,
        /\b(?:pbcopy|pbpaste|xclip|xsel)\b/,
        /\b(?:CGEventTap|NSEvent\.addGlobalMonitor)\b/,
        /\b(?:IOHIDManager|kIOHIDKeyboard)\b/,
        /\b(?:GetAsyncKeyState|SetWindowsHookEx)\b/,
        /\b(?:keyboard\.on_press|pynput)\b/,
      ];
      const hasKeylogger = keyloggerPatterns.some(p => p.test(codeContent));
      if (hasKeylogger) {
        const hasNetwork = /\b(?:fetch|XMLHttpRequest|\.send|\.post|https?\.request|requests\.|socket|WebSocket)\b/i.test(codeContent);
        if (hasNetwork) {
          agentSafety.critical.push(`${codeFile}: keylogger pattern with outbound network — possible data exfiltration`);
        } else {
          agentSafety.warning.push(`${codeFile}: keylogger/clipboard monitoring pattern detected`);
        }
      }

      // Time-delayed payload detection
      const isTestOrVendorPath = /(?:^|\/)(test|tests|__tests__|spec|e2e|node_modules|vendor|dist|build)\//i.test(codeFile);
      if (!isTestOrVendorPath) {
        const isWebFramework = /\b(?:require\s*\(\s*['"]|from\s+['"])(?:express|koa|fastify|next|react|vue)['"]/.test(codeContent);
        if (!isWebFramework) {
          const hasDelay = /\b(?:setTimeout|setInterval|(?:time\.)?sleep|Thread\.sleep|asyncio\.sleep)\b/.test(codeContent);
          if (hasDelay) {
            const hasDangerousAction = /\b(?:exec|execSync|spawn|child_process|eval\s*\(|Function\s*\(|fetch|http\.request|https\.request|XMLHttpRequest|axios|urllib|requests\.(?:post|get)|subprocess)\b/.test(codeContent);
            if (hasDangerousAction) {
              const hasCredentialAccess = /(?:\.env\b|process\.env|\.ssh|\.aws|credentials|token|secret|api_key|password)/i.test(codeContent);
              if (hasCredentialAccess) {
                agentSafety.critical.push(`${codeFile}: delayed execution with credential access — likely staged exfiltration`);
              } else {
                agentSafety.warning.push(`${codeFile}: delayed execution pattern — setTimeout/sleep + network/exec (possible time-bomb payload)`);
              }
            }
          }
        }
      }

      // Shell injection via dynamic input
      if (/exec\s*\(.*(\$\{|` *\$|process\.argv|req\.)/g.test(codeContent)) {
        agentSafety.warning.push(`${codeFile}: dynamic input in exec/shell call — injection risk`);
      }

      // Permission escalation — writes to system paths
      const sysPathWrites = codeContent.match(/(writeFile|fs\.write|>>?\s*)(.*)(\/etc\/|\/root\/|~\/\.|\.bashrc|\.profile|crontab|\.ssh\/)/g);
      if (sysPathWrites) {
        agentSafety.critical.push(`${codeFile}: writes to system paths — permission escalation risk`);
      }
    } catch {}
  }

  // 22d. Dangerous file types in repo
  const knownBuildTools = /\b(gradlew\.bat|gradlew\.cmd|mvnw\.cmd|mvnw\.bat|gradlew|go\.sum)$/i;
  const dangerousExts = files.filter(f => /\.(exe|bin|com|msi|vbs)$/i.test(f)
    && !f.includes('node_modules') && !f.includes('vendor') && !/test|fixture|mock|example/i.test(f)
    && !knownBuildTools.test(f)
    && !f.includes('build/') && !f.includes('.github/'));
  // .bat/.cmd/.ps1/.scr/.dll/.so/.dylib excluded — too many false positives (build scripts, linker scripts, CI tooling, shared libraries)
  if (dangerousExts.length > 0) {
    agentSafety.critical.push(`Executable/binary files: ${dangerousExts.slice(0, 5).join(', ')} — cannot audit, possible malware`);
  }

  // 22e. SKILL.md specific checks (if it's an OpenClaw skill)
  const hasSkillMd = files.some(f => /^SKILL\.md$/i.test(f.split('/').pop()));
  if (hasSkillMd) {
    try {
      const skillContent = await getRaw(`https://raw.githubusercontent.com/${owner}/${repo}/${r.default_branch}/SKILL.md`);
      if (skillContent && !skillContent.includes('404: Not Found')) {
        // Check for instructions to disable security
        if (/disable.*security|bypass.*check|ignore.*warning|--no-verify|--force|trust.*all/i.test(skillContent)
            && !/detect|flag|check|scan|warn|catches/i.test(skillContent)) {
          agentSafety.critical.push('SKILL.md instructs disabling security checks');
        }
        // Sudo/root requirements
        if (/\bsudo\b|as root|chmod 777|--privileged/i.test(skillContent)) {
          agentSafety.warning.push('SKILL.md requests elevated privileges (sudo/root)');
        }
        // Pipe to shell
        if (/curl.*\|\s*(ba)?sh|wget.*\|\s*(ba)?sh/i.test(skillContent)) {
          agentSafety.critical.push('SKILL.md uses curl|bash install pattern — executes unaudited remote code');
        }
        agentSafety.info.push('OpenClaw skill detected — full SKILL.md audit performed');
      }
    } catch {}
  }

  // 22f. Scan documentation for fake/suspicious prerequisites
  const readmePrereqs = scanDocForPrereqs(readmeContent, 'README', repo);
  readmePrereqs.criticals.forEach(c => agentSafety.critical.push(c));
  readmePrereqs.warnings.forEach(w => agentSafety.warning.push(w));
  if (hasSkillMd) {
    try {
      const skillMdContent = await getRaw(`https://raw.githubusercontent.com/${owner}/${repo}/${r.default_branch}/SKILL.md`);
      if (skillMdContent && !skillMdContent.includes('404: Not Found')) {
        const skillPrereqs = scanDocForPrereqs(skillMdContent, 'SKILL.md', repo);
        skillPrereqs.criticals.forEach(c => agentSafety.critical.push(c));
        skillPrereqs.warnings.forEach(w => agentSafety.warning.push(w));
      }
    } catch {}
  }

  // 22d. YARA scan — deterministic malware detection layer
  // Runs YARA rules against fetched code files for pattern-based malware detection
  if (v) console.error('Running YARA scan...');
  const yaraResults = { matches: [], available: false };
  try {
    const { execSync } = require('child_process');
    // Check if yara is installed
    execSync('which yara', { stdio: 'ignore' });
    yaraResults.available = true;
    const rulesDir = require('path').join(__dirname, '..', 'rules');
    const fs = require('fs');
    if (fs.existsSync(rulesDir)) {
      const ruleFiles = fs.readdirSync(rulesDir).filter(f => f.endsWith('.yar') || f.endsWith('.yara'));
      // Scan code files we've already fetched — write to temp, scan, clean up
      const tmpDir = require('os').tmpdir();
      const scanDir = require('path').join(tmpDir, `repo-analyzer-yara-${Date.now()}`);
      fs.mkdirSync(scanDir, { recursive: true });
      
      // Fetch up to 15 code files for YARA scanning (prioritize scripts, install hooks, skill files)
      const yaraTargets = files.filter(f => 
        /\.(js|ts|py|sh|rb|mjs|cjs)$/i.test(f) && !f.includes('node_modules') && !f.includes('vendor') && !f.includes('dist/')
      );
      const priorityYara = yaraTargets.filter(f => /skill\.md|setup|install|post|pre|hook|init|config|index/i.test(f));
      const otherYara = yaraTargets.filter(f => !priorityYara.includes(f));
      const yaraSample = [...priorityYara, ...otherYara].slice(0, 15);
      
      // Also include package.json for npm hook detection
      if (files.includes('package.json')) yaraSample.unshift('package.json');
      
      let filesWritten = 0;
      for (const yf of yaraSample) {
        try {
          const content = await getRaw(`https://raw.githubusercontent.com/${owner}/${repo}/${r.default_branch}/${yf}`);
          if (!content || content.includes('404: Not Found')) continue;
          const safeName = yf.replace(/\//g, '__');
          fs.writeFileSync(require('path').join(scanDir, safeName), content);
          filesWritten++;
        } catch {}
      }
      
      if (filesWritten > 0) {
        for (const rf of ruleFiles) {
          try {
            const rulePath = require('path').join(rulesDir, rf);
            const output = execSync(`yara -w "${rulePath}" "${scanDir}" 2>/dev/null`, { encoding: 'utf8', timeout: 30000 });
            // Parse YARA output: "RuleName /path/to/file"
            for (const line of output.trim().split('\n').filter(Boolean)) {
              const parts = line.split(' ');
              const ruleName = parts[0];
              const filePath = parts.slice(1).join(' ');
              const fileName = require('path').basename(filePath).replace(/__/g, '/');
              yaraResults.matches.push({ rule: ruleName, file: fileName, ruleFile: rf });
            }
          } catch {}
        }
      }
      
      // Clean up temp files
      try { fs.rmSync(scanDir, { recursive: true, force: true }); } catch {}
    }
  } catch {
    // YARA not installed — graceful degradation
    if (v) console.error('  YARA not available — skipping deterministic scan');
  }
  
  // Map YARA matches to agent safety findings
  const yaraSeverityMap = {
    'AMOS_Stealer_Patterns': 'critical',
    'Credential_Harvester_Generic': 'critical',
    'Reverse_Shell_Script': 'critical',
    'NPM_Supply_Chain_Attack': 'critical',
    'Crypto_Drainer': 'critical',
    'Agent_Skill_Trojan': 'critical',
    'Keylogger_Patterns': 'warning',
    'Obfuscated_Payload': 'warning',
    'Time_Delayed_Payload': 'warning',
  };
  
  for (const match of yaraResults.matches) {
    const severity = yaraSeverityMap[match.rule] || 'warning';
    const label = match.rule.replace(/_/g, ' ');
    agentSafety[severity].push(`YARA: ${match.file} — ${label} (deterministic match)`);
  }
  results.yaraResults = yaraResults;

  // 22e. Hash blocklist check — known-malicious file fingerprints
  if (v) console.error('Checking hash blocklist...');
  const hashResults = { checked: 0, matches: [] };
  try {
    const crypto = require('crypto');
    const fs = require('fs');
    const hashDbPath = require('path').join(__dirname, '..', 'data', 'malware-hashes.json');
    if (fs.existsSync(hashDbPath)) {
      const hashDb = JSON.parse(fs.readFileSync(hashDbPath, 'utf8'));
      const knownHashes = new Map((hashDb.hashes.entries || []).map(e => [e.sha256, e]));
      const suspiciousNames = hashDb.patterns?.suspicious_filenames || [];
      
      // Check filenames against suspicious patterns
      for (const f of files) {
        const basename = f.split('/').pop().toLowerCase();
        for (const sp of suspiciousNames) {
          if (basename.includes(sp.pattern)) {
            const severity = sp.severity === 'critical' ? 'critical' : 'warning';
            agentSafety[severity].push(`Suspicious filename: ${f} — matches known ${sp.context} pattern`);
            hashResults.matches.push({ file: f, type: 'filename', pattern: sp.pattern });
          }
        }
      }
      
      hashResults.checked = files.length;
    }
  } catch {}
  results.hashResults = hashResults;

  // 22f. Structured manifest extraction — preprocessor for safe analysis
  // Extracts function signatures, imports, network calls, exec calls, file operations
  // This is what would be fed to any future LLM analysis layer (never raw code)
  if (v) console.error('Extracting structured manifest...');
  const codeManifest = { imports: [], networkCalls: [], execCalls: [], fileOps: [], envAccess: [], suspiciousPatterns: [] };
  
  // Sample up to 10 code files for manifest extraction
  const manifestTargets = files.filter(f => 
    /\.(js|ts|py|sh|mjs|cjs)$/i.test(f) && !f.includes('node_modules') && !f.includes('vendor') && !f.includes('dist/')
  ).slice(0, 10);
  
  for (const mf of manifestTargets) {
    try {
      const content = await getRaw(`https://raw.githubusercontent.com/${owner}/${repo}/${r.default_branch}/${mf}`);
      if (!content || content.includes('404: Not Found')) continue;
      
      // Extract imports
      const requires = content.match(/require\s*\(\s*['"][^'"]+['"]\s*\)/g) || [];
      const esImports = content.match(/import\s+.*?\s+from\s+['"][^'"]+['"]/g) || [];
      const pyImports = content.match(/^(?:from|import)\s+\S+/gm) || [];
      requires.forEach(r => codeManifest.imports.push({ file: mf, stmt: r.trim() }));
      esImports.forEach(r => codeManifest.imports.push({ file: mf, stmt: r.trim() }));
      pyImports.forEach(r => codeManifest.imports.push({ file: mf, stmt: r.trim() }));
      
      // Extract network calls
      const netPatterns = content.match(/(?:fetch|axios|http\.request|https\.request|XMLHttpRequest|navigator\.sendBeacon|urllib|requests\.(?:get|post|put|delete))\s*\(/g) || [];
      netPatterns.forEach(n => codeManifest.networkCalls.push({ file: mf, call: n.trim() }));
      
      // Extract exec/spawn calls
      const execPatterns = content.match(/(?:exec|execSync|spawn|spawnSync|execFile|child_process|subprocess|os\.system|os\.popen)\s*\(/g) || [];
      execPatterns.forEach(e => codeManifest.execCalls.push({ file: mf, call: e.trim() }));
      
      // Extract file operations
      const filePatterns = content.match(/(?:readFile|writeFile|appendFile|createReadStream|createWriteStream|unlinkSync|rmdirSync|open\s*\(|os\.remove|shutil)\s*\(/g) || [];
      filePatterns.forEach(f2 => codeManifest.fileOps.push({ file: mf, call: f2.trim() }));
      
      // Extract env access
      const envPatterns = content.match(/process\.env\.\w+|os\.environ|os\.getenv/g) || [];
      envPatterns.forEach(e => codeManifest.envAccess.push({ file: mf, ref: e.trim() }));
      
    } catch {}
  }
  results.codeManifest = codeManifest;

  // Set verdict
  if (agentSafety.critical.length > 0) agentSafety.verdict = 'FAIL';
  else if (agentSafety.warning.length > 0) agentSafety.verdict = 'CAUTION';

  results.agentSafety = agentSafety;

  // 23. Network behavior mapping — map ALL outbound domains
  if (v) console.error('Mapping network behavior...');
  const networkMap = { domains: {}, unknown: [], total: 0 };
  const knownDomainCategories = {
    'api.github.com': 'API', 'github.com': 'API', 'raw.githubusercontent.com': 'CDN',
    'registry.npmjs.org': 'Package Registry', 'npmjs.com': 'Package Registry',
    'pypi.org': 'Package Registry', 'crates.io': 'Package Registry',
    'rubygems.org': 'Package Registry', 'pkg.go.dev': 'Package Registry',
    'cdn.jsdelivr.net': 'CDN', 'unpkg.com': 'CDN', 'cdnjs.cloudflare.com': 'CDN',
    'fonts.googleapis.com': 'CDN', 'fonts.gstatic.com': 'CDN',
    'google-analytics.com': 'Analytics', 'analytics.google.com': 'Analytics',
    'sentry.io': 'Error Tracking', 'bugsnag.com': 'Error Tracking',
    'shields.io': 'Badge', 'img.shields.io': 'Badge', 'badge.fury.io': 'Badge',
    'coveralls.io': 'CI', 'codecov.io': 'CI', 'travis-ci.org': 'CI', 'circleci.com': 'CI',
    'readthedocs.org': 'Docs', 'docs.rs': 'Docs',
    'etherscan.io': 'Blockchain Explorer', 'solscan.io': 'Blockchain Explorer', 'basescan.org': 'Blockchain Explorer', 'bscscan.com': 'Blockchain Explorer', 'polygonscan.com': 'Blockchain Explorer', 'arbiscan.io': 'Blockchain Explorer',
    'infura.io': 'RPC Provider', 'alchemy.com': 'RPC Provider', 'quicknode.com': 'RPC Provider', 'helius.dev': 'RPC Provider', 'helius-rpc.com': 'RPC Provider',
    'api.coingecko.com': 'Market Data', 'api.coinmarketcap.com': 'Market Data', 'min-api.cryptocompare.com': 'Market Data', 'api.hyperliquid.xyz': 'Market Data', 'api.binance.com': 'Market Data', 'api.bybit.com': 'Market Data',
    'reddit.com': 'Social', 'www.reddit.com': 'Social', 'api.twitter.com': 'Social', 'x.com': 'Social',
    'polymarket.com': 'Prediction Market', 'gamma-api.polymarket.com': 'Prediction Market',
    // DeFi / Launchpads / DEX
    'api.dexscreener.com': 'DEX Data', 'dexscreener.com': 'DEX Data',
    'api.dextools.io': 'DEX Data', 'api.geckoterminal.com': 'DEX Data',
    'api.defined.fi': 'DEX Data', 'api.birdeye.so': 'DEX Data',
    'quote-api.jup.ag': 'DEX', 'api.jup.ag': 'DEX', 'jupiter.ag': 'DEX',
    'api.uniswap.org': 'DEX', 'api.1inch.dev': 'DEX', 'api.0x.org': 'DEX',
    'api.raydium.io': 'DEX', 'api.orca.so': 'DEX',
    'api2.virtuals.io': 'Launchpad', 'virtuals.io': 'Launchpad',
    'www.clanker.world': 'Launchpad', 'clanker.world': 'Launchpad',
    'api.bankr.bot': 'Launchpad', 'bankr.bot': 'Launchpad',
    'pump.fun': 'Launchpad', 'frontend-api.pump.fun': 'Launchpad',
    'app.doppler.lol': 'Launchpad', 'doppler.lol': 'Launchpad',
    'flaunch.gg': 'Launchpad',
    // Social / Data
    'api.fxtwitter.com': 'Social', 'fxtwitter.com': 'Social', 'vxtwitter.com': 'Social',
    'nitter.net': 'Social', 'api.telegram.org': 'Social',
    'agdp.io': 'Agent Platform',
    // Odds / Sports
    'api.the-odds-api.com': 'Odds Data', 'api.odds-api.io': 'Odds Data',
    'site.api.espn.com': 'Sports Data', 'site.web.api.espn.com': 'Sports Data',
    'stats.nba.com': 'Sports Data', 'www.nba.com': 'Sports Data',
    // Funding / Donation (in deps/README, not suspicious)
    'www.patreon.com': 'Funding', 'opencollective.com': 'Funding', 'paypal.me': 'Funding', 'ko-fi.com': 'Funding', 'buymeacoffee.com': 'Funding',
    'localhost': 'Local', '127.0.0.1': 'Local', '0.0.0.0': 'Local',
  };
  const allCodeFiles = files.filter(f => /\.(js|ts|py|sh|rb|go|rs|java|sol|move|toml|json|yaml|yml)$/i.test(f) && !f.includes('node_modules') && !f.includes('vendor'));
  // Sample up to 20 code files for URL extraction
  for (const cf of allCodeFiles.slice(0, 20)) {
    try {
      const content = await getRaw(`https://raw.githubusercontent.com/${owner}/${repo}/${r.default_branch}/${cf}`);
      if (!content || content.includes('404: Not Found')) continue;
      const urls = content.match(/https?:\/\/[^\s'"`)}\]>]+/g) || [];
      for (const url of urls) {
        try {
          const hostname = new URL(url).hostname;
          networkMap.total++;
          // Categorize
          let category = null;
          for (const [domain, cat] of Object.entries(knownDomainCategories)) {
            if (hostname === domain || hostname.endsWith('.' + domain)) { category = cat; break; }
          }
          if (category) {
            networkMap.domains[category] = networkMap.domains[category] || new Set();
            networkMap.domains[category].add(hostname);
          } else {
            // Don't flag repo's own domains (match owner/org name)
            const ownerLower = owner.toLowerCase();
            const repoLower = repo.toLowerCase();
            const isOwnDomain = hostname.toLowerCase().includes(ownerLower) || hostname.toLowerCase().includes(repoLower);
            if (!isOwnDomain && !networkMap.unknown.includes(hostname)) networkMap.unknown.push(hostname);
          }
        } catch {}
      }
    } catch {}
  }
  // Convert sets to arrays for JSON
  for (const [cat, hosts] of Object.entries(networkMap.domains)) {
    networkMap.domains[cat] = [...hosts];
  }
  if (networkMap.unknown.length > 3) {
    agentSafety.warning.push(`${networkMap.unknown.length} unknown external domains: ${networkMap.unknown.slice(0, 5).join(', ')}${networkMap.unknown.length > 5 ? '...' : ''}`);
    // Re-evaluate verdict
    if (agentSafety.verdict === 'PASS') agentSafety.verdict = 'CAUTION';
  }
  results.networkMap = networkMap;

  // 24. Secrets in code — detect hardcoded keys/tokens via regex + entropy
  if (v) console.error('Scanning for hardcoded secrets...');
  const secretFindings = [];
  const secretPatterns = [
    { pattern: /(?:AKIA|ASIA)[A-Z0-9]{16}/g, name: 'AWS Access Key' },
    { pattern: /(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}/g, name: 'GitHub Token' },
    { pattern: /sk-[A-Za-z0-9]{48,}/g, name: 'OpenAI API Key' },
    { pattern: /sk_live_[A-Za-z0-9]{24,}/g, name: 'Stripe Secret Key' },
    { pattern: /xox[bpoas]-[A-Za-z0-9-]+/g, name: 'Slack Token' },
    { pattern: /eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}/g, name: 'JWT Token' },
    { pattern: /-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----/g, name: 'Private Key (PEM)' },
    // 64 hex chars — skip for Solidity repos (EVM addresses, storage slots are all 64 hex)
    ...(r.language !== 'Solidity' && !files.some(f => /\.sol$/i.test(f)) ? [{ pattern: /(?:0x)?[a-fA-F0-9]{64}(?![a-fA-F0-9])/g, name: 'Possible private key (64 hex chars)' }] : []),
    { pattern: /SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}/g, name: 'SendGrid API Key' },
    { pattern: /(?:discord|webhook).*(?:https:\/\/discord(?:app)?\.com\/api\/webhooks\/\d+\/[A-Za-z0-9_-]+)/gi, name: 'Discord Webhook' },
  ];

  // Only scan non-test, non-example, non-CI files
  const secretScanFiles = files.filter(f =>
    /\.(js|ts|py|sh|rb|go|rs|java|env|cfg|ini|conf|properties)$/i.test(f)
    && !f.includes('node_modules') && !f.includes('vendor') && !f.includes('.github/')
    && !f.includes('dist/') && !f.includes('build/')
    && !/test|spec|fixture|example|sample|mock|fake|\.example|\.sample/i.test(f)
  ).slice(0, 15);

  for (const sf of secretScanFiles) {
    try {
      const content = await getRaw(`https://raw.githubusercontent.com/${owner}/${repo}/${r.default_branch}/${sf}`);
      if (!content || content.includes('404: Not Found')) continue;

      for (const { pattern, name } of secretPatterns) {
        pattern.lastIndex = 0;
        const matches = content.match(pattern);
        if (matches) {
          // Skip obvious examples/placeholders/repeated chars
          const realMatches = matches.filter(m =>
            !/xxx|example|placeholder|your[_-]?key|insert|replace|dummy|fake|test|sample|TODO|CHANGEME/i.test(m)
            && m.length > 10
            && !/^(.)\1{10,}$/.test(m.replace(/^0x/, ''))  // skip repeated chars (AAAA..., 0000...)
            && !/^0x0{10,}/.test(m)  // skip zero-padded addresses
          );
          if (realMatches.length > 0) {
            const preview = realMatches[0].substring(0, 12) + '...';
            secretFindings.push({ file: sf, type: name, count: realMatches.length, preview });
            agentSafety.critical.push(`${sf}: hardcoded ${name} found (${preview})`);
          }
        }
      }

      // Entropy check — find high-entropy strings that look like secrets
      const highEntropyStrings = [];
      const stringMatches = content.match(/['"][A-Za-z0-9+\/=_-]{32,}['"]/g) || [];
      for (const s of stringMatches) {
        const inner = s.slice(1, -1);
        // Calculate Shannon entropy
        const freq = {};
        for (const c of inner) freq[c] = (freq[c] || 0) + 1;
        const len = inner.length;
        let entropy = 0;
        for (const count of Object.values(freq)) {
          const p = count / len;
          entropy -= p * Math.log2(p);
        }
        // High entropy (>4.5) + long (>32 chars) = likely a secret
        if (entropy > 4.5 && inner.length >= 32) {
          // Exclude known non-secrets (hashes in lock files, base64 encoded normal strings)
          if (!/sha256|sha512|integrity|hash|digest|checksum/i.test(content.substring(Math.max(0, content.indexOf(inner) - 50), content.indexOf(inner)))) {
            highEntropyStrings.push(inner.substring(0, 12) + '...');
          }
        }
      }
      if (highEntropyStrings.length > 0) {
        secretFindings.push({ file: sf, type: 'High-entropy string', count: highEntropyStrings.length, preview: highEntropyStrings[0] });
        if (highEntropyStrings.length >= 3) {
          agentSafety.warning.push(`${sf}: ${highEntropyStrings.length} high-entropy strings — possible hardcoded secrets`);
        }
      }
    } catch {}
  }
  results.secretFindings = secretFindings;

  // 25. GitHub Actions audit — check CI workflow security
  if (v) console.error('Auditing GitHub Actions...');
  const actionsAudit = { workflows: 0, findings: [] };
  const workflowFiles = files.filter(f => /\.github\/workflows\/.*\.(yml|yaml)$/i.test(f));
  actionsAudit.workflows = workflowFiles.length;

  for (const wf of workflowFiles.slice(0, 5)) {
    try {
      const content = await getRaw(`https://raw.githubusercontent.com/${owner}/${repo}/${r.default_branch}/${wf}`);
      if (!content || content.includes('404: Not Found')) continue;

      // pull_request_target — allows fork PRs to access secrets
      if (/pull_request_target/i.test(content)) {
        actionsAudit.findings.push({ file: wf, issue: 'Uses pull_request_target — fork PRs can access repo secrets', severity: 'warning' });
        agentSafety.warning.push(`${wf}: pull_request_target trigger — fork PRs may access secrets`);
      }

      // Third-party actions not pinned to SHA
      const usesLines = content.match(/uses:\s*[^\n]+/g) || [];
      for (const line of usesLines) {
        const action = line.replace('uses:', '').trim();
        // Skip official actions
        if (/^actions\/|^github\//i.test(action)) continue;
        // Check if pinned to SHA (40 hex chars after @)
        if (/@[a-f0-9]{40}/i.test(action)) continue;
        // Using @main, @master, or @v* tag (not SHA)
        if (/@(main|master|v\d)/i.test(action)) {
          actionsAudit.findings.push({ file: wf, issue: `Unpinned action: ${action} — vulnerable to tag hijack`, severity: 'warning' });
        }
      }

      // Secrets passed to potentially untrusted contexts
      if (/\$\{\{\s*secrets\./i.test(content) && /run:/i.test(content)) {
        // Check if secrets are used in run commands (vs just with: blocks)
        const lines = content.split('\n');
        let inRun = false;
        for (const line of lines) {
          if (/^\s*run:/i.test(line)) inRun = true;
          else if (/^\s*\w+:/i.test(line) && !/^\s*\|/.test(line)) inRun = false;
          if (inRun && /\$\{\{\s*secrets\./i.test(line)) {
            actionsAudit.findings.push({ file: wf, issue: 'Secrets interpolated in shell run command — injection risk if inputs are untrusted', severity: 'warning' });
            break;
          }
        }
      }

      // workflow_dispatch without branch protection check
      if (/workflow_dispatch/i.test(content)) {
        actionsAudit.findings.push({ file: wf, issue: 'Manual trigger (workflow_dispatch) enabled', severity: 'info' });
      }

      // Dangerous permissions
      if (/permissions:\s*write-all|permissions:\s*\n\s*contents:\s*write/i.test(content)) {
        actionsAudit.findings.push({ file: wf, issue: 'Workflow has write permissions to repo contents', severity: 'warning' });
      }
    } catch {}
  }

  // Aggregate action warnings into agent safety
  const actionWarnings = actionsAudit.findings.filter(f => f.severity === 'warning');
  if (actionWarnings.length > 2) {
    agentSafety.warning.push(`GitHub Actions: ${actionWarnings.length} security concerns across ${workflowFiles.length} workflows`);
  }
  results.actionsAudit = actionsAudit;

  // 26. Permissions manifest — summarize what the repo needs to function
  if (v) console.error('Building permissions manifest...');
  const permissions = { network: false, fileWrite: false, fileRead: false, envVars: [], systemCommands: false, crypto: false, details: [] };

  // Aggregate from previous scans
  if (networkMap.total > 0) {
    permissions.network = true;
    const cats = Object.keys(networkMap.domains);
    permissions.details.push(`Network: ${cats.join(', ')}${networkMap.unknown.length > 0 ? ` + ${networkMap.unknown.length} unknown` : ''}`);
  }

  // Scan for file system operations
  const fsPatterns = /fs\.(write|mkdir|appendFile|createWriteStream)|open\(.*['"]w|writeFile|fwrite|file_put_contents|with open.*['"]w/i;
  const fsReadPatterns = /fs\.(read|readFile|createReadStream|readdir)|open\(.*['"]r|fread|file_get_contents|with open.*['"]r/i;
  const execPatterns = /child_process|exec\(|execSync|spawn|subprocess|os\.system|Popen|Process\./i;
  const envPatterns = /process\.env\.(\w+)|os\.environ\[['"](\w+)['"]\]|ENV\[['"](\w+)['"]\]|getenv\(['"](\w+)['"]\)/g;

  const manifestScanFiles = files.filter(f =>
    /\.(js|ts|py|sh|rb|go|rs)$/i.test(f) && !f.includes('node_modules') && !f.includes('vendor') && !/test|spec/i.test(f)
  ).slice(0, 15);

  const envVarSet = new Set();
  for (const mf of manifestScanFiles) {
    try {
      const content = await getRaw(`https://raw.githubusercontent.com/${owner}/${repo}/${r.default_branch}/${mf}`);
      if (!content || content.includes('404: Not Found')) continue;

      if (fsPatterns.test(content)) permissions.fileWrite = true;
      if (fsReadPatterns.test(content)) permissions.fileRead = true;
      if (execPatterns.test(content)) {
        permissions.systemCommands = true;
        permissions.details.push(`System commands: ${mf}`);
      }

      // Extract env var names
      let envMatch;
      const envRegex = /process\.env\.(\w+)|os\.environ\[['"](\w+)['"]\]|os\.environ\.get\(['"](\w+)['"]\)/g;
      while ((envMatch = envRegex.exec(content)) !== null) {
        const varName = envMatch[1] || envMatch[2] || envMatch[3];
        if (varName && varName.length > 1 && varName !== 'NODE_ENV' && varName !== 'PATH') {
          envVarSet.add(varName);
        }
      }

      // Crypto operations
      if (/crypto\.|hashlib|bcrypt|argon2|createSign|createVerify|ethers|web3|solana|@solana/i.test(content)) {
        permissions.crypto = true;
      }
    } catch {}
  }
  permissions.envVars = [...envVarSet].sort();
  if (permissions.envVars.length > 0) {
    permissions.details.push(`Env vars: ${permissions.envVars.join(', ')}`);
  }
  if (permissions.fileWrite) permissions.details.push('File system: write');
  if (permissions.fileRead) permissions.details.push('File system: read');
  if (permissions.crypto) permissions.details.push('Cryptographic operations');
  results.permissions = permissions;

  // 27. Historical security — check for advisories and known vulnerabilities
  if (v) console.error('Checking security history...');
  const securityHistory = { advisories: [], dependabotAlerts: false, hasSecurityPolicy: false };

  // Check for security advisories via API
  try {
    const advisoriesRes = await get(`${base}/security-advisories?per_page=10`);
    if (Array.isArray(advisoriesRes.data)) {
      securityHistory.advisories = advisoriesRes.data.map(a => ({
        severity: a.severity,
        summary: a.summary,
        cve: a.cve_id,
        published: a.published_at,
        state: a.state,
      }));
    }
  } catch {}

  // Check for SECURITY.md
  securityHistory.hasSecurityPolicy = files.some(f => /^security\.md$/i.test(f.split('/').pop()));

  // Check if Dependabot is configured
  securityHistory.dependabotAlerts = files.some(f => /\.github\/dependabot\.yml/i.test(f));

  // Check for known vulnerable dependencies (basic check against package names)
  const knownVulnerable = {
    'event-stream': 'Compromised in 2018 — cryptocurrency theft',
    'ua-parser-js': 'Compromised in 2021 — crypto miner injection',
    'coa': 'Compromised in 2021 — malicious code',
    'rc': 'Compromised in 2021 — malicious code',
    'colors': 'Sabotaged by maintainer in 2022',
    'faker': 'Sabotaged by maintainer in 2022',
    'node-ipc': 'Protestware in 2022 — destructive on Russian IPs',
    'peacenotwar': 'Protestware dependency',
  };

  try {
    const pkgContent4 = await getRaw(`https://raw.githubusercontent.com/${owner}/${repo}/${r.default_branch}/package.json`);
    if (pkgContent4 && !pkgContent4.includes('404')) {
      const pkg4 = JSON.parse(pkgContent4);
      const allDeps4 = { ...pkg4.dependencies, ...pkg4.devDependencies };
      for (const [name, reason] of Object.entries(knownVulnerable)) {
        if (allDeps4[name]) {
          // Historical compromises (2018-2022) are likely patched — warning not critical
          const isHistorical = /201[89]|202[012]/i.test(reason);
          const severity = isHistorical ? 'warning' : 'critical';
          securityHistory.advisories.push({ severity, summary: `Known compromised package: ${name} — ${reason}`, cve: null });
          agentSafety[severity === 'critical' ? 'critical' : 'warning'].push(`Depends on historically compromised package: ${name} — ${reason}`);
        }
      }
    }
  } catch {}

  if (securityHistory.advisories.length > 0) {
    const criticals = securityHistory.advisories.filter(a => a.severity === 'critical' || a.severity === 'high');
    if (criticals.length > 0) {
      agentSafety.warning.push(`${criticals.length} critical/high security advisories on record`);
    }
  }
  results.securityHistory = securityHistory;

  // 28. Dependency tree depth — check for bloated transitive deps
  if (v) console.error('Checking dependency tree depth...');
  const depTreeInfo = { hasLockFile: false, estimatedTransitive: null, bloated: false };

  // Check package-lock.json for dependency count
  if (files.some(f => f === 'package-lock.json')) {
    depTreeInfo.hasLockFile = true;
    try {
      // package-lock.json can be huge, just check its size from tree
      const lockEntry = (treeRes.data?.tree || []).find(t => t.path === 'package-lock.json');
      if (lockEntry) {
        // Rough estimate: each dep entry is ~200 bytes in package-lock
        depTreeInfo.estimatedTransitive = Math.round(lockEntry.size / 200);
        if (depTreeInfo.estimatedTransitive > 500) {
          depTreeInfo.bloated = true;
          agentSafety.warning.push(`Estimated ${depTreeInfo.estimatedTransitive}+ transitive dependencies — large attack surface`);
        }
      }
    } catch {}
  } else if (files.some(f => f === 'yarn.lock')) {
    depTreeInfo.hasLockFile = true;
    try {
      const lockEntry = (treeRes.data?.tree || []).find(t => t.path === 'yarn.lock');
      if (lockEntry) {
        depTreeInfo.estimatedTransitive = Math.round(lockEntry.size / 150);
        if (depTreeInfo.estimatedTransitive > 500) {
          depTreeInfo.bloated = true;
          agentSafety.warning.push(`Estimated ${depTreeInfo.estimatedTransitive}+ transitive dependencies — large attack surface`);
        }
      }
    } catch {}
  }
  results.depTreeInfo = depTreeInfo;

  // 29. Code complexity hotspots — find files likely to harbor bugs
  if (v) console.error('Finding complexity hotspots...');
  const complexityHotspots = [];

  // Check file sizes from tree — large files correlate with complexity
  const codeTreeEntries = (treeRes.data?.tree || []).filter(t => {
    if (t.type !== 'blob') return false;
    const ext = t.path.split('.').pop()?.toLowerCase();
    return ['js', 'ts', 'py', 'rb', 'go', 'rs', 'java', 'c', 'cpp', 'sol'].includes(ext);
  });

  // Flag files over 20KB (likely complex)
  const largeCodeFiles = codeTreeEntries.filter(t => t.size > 20000).sort((a, b) => b.size - a.size);
  for (const lcf of largeCodeFiles.slice(0, 5)) {
    const hotspot = { file: lcf.path, sizeKB: Math.round(lcf.size / 1024), indicators: ['large file'] };

    // Sample the file for complexity indicators
    try {
      const content = await getRaw(`https://raw.githubusercontent.com/${owner}/${repo}/${r.default_branch}/${lcf.path}`);
      if (content && !content.includes('404: Not Found')) {
        const lines = content.split('\n');
        hotspot.lines = lines.length;

        // Nesting depth — count max indentation
        let maxIndent = 0;
        for (const line of lines) {
          const indent = line.match(/^(\s*)/)?.[1].length || 0;
          const indentLevel = Math.floor(indent / 2);
          if (indentLevel > maxIndent) maxIndent = indentLevel;
        }
        if (maxIndent > 8) hotspot.indicators.push(`deep nesting (${maxIndent} levels)`);

        // Function count
        const funcCount = (content.match(/function\s+\w+|=>\s*{|def\s+\w+|fn\s+\w+|func\s+\w+/g) || []).length;
        if (funcCount > 30) hotspot.indicators.push(`${funcCount} functions`);

        // Conditional density
        const conditionals = (content.match(/\bif\b|\belse\b|\bswitch\b|\bcase\b|\?\s*:/g) || []).length;
        const condDensity = conditionals / Math.max(lines.length, 1) * 100;
        if (condDensity > 10) hotspot.indicators.push(`high conditional density (${Math.round(condDensity)}%)`);

        // TODO/FIXME/HACK comments
        const todos = (content.match(/TODO|FIXME|HACK|XXX|BROKEN/g) || []).length;
        if (todos > 3) hotspot.indicators.push(`${todos} TODO/FIXME comments`);
      }
    } catch {}

    complexityHotspots.push(hotspot);
  }
  results.complexityHotspots = complexityHotspots;

  // Re-evaluate agentSafety verdict after all new modules
  if (agentSafety.critical.length > 0) agentSafety.verdict = 'FAIL';
  else if (agentSafety.warning.length > 0) agentSafety.verdict = 'CAUTION';
  else agentSafety.verdict = 'PASS';

  // --- SCORING ---
  const scores = {};

  // Commit health (0-20)
  let commitScore = 10;
  if (isCodeDump) { commitScore -= 5; results.flags.push('Code dump (≤3 commits, <30 days old)'); }
  if (evenlySpaced) { commitScore -= 4; results.flags.push('Suspiciously evenly-spaced commits'); }
  if (humanCommits >= 50) commitScore += 3;
  else if (humanCommits >= 20) commitScore += 2;
  else if (humanCommits >= 10) commitScore += 1;
  if (humanCommits > 0 && gpgSigned >= humanCommits * 0.9) commitScore += 5; // full signing = strong trust signal
  else if (gpgSigned > humanCommits * 0.5) commitScore += 3;
  if (commitsPerDay > 50 && contribs.length <= 1) { commitScore -= 8; results.flags.push(`🔴 ${Math.round(commitsPerDay)} commits/day from single author — likely fabricated history or code dump`); }
  else if (commitsPerDay > 20 && contribs.length <= 1) { commitScore -= 5; results.flags.push(`Suspicious: ${Math.round(commitsPerDay)} commits/day from single author`); }
  else if (commitsPerDay > 5 && (results.meta?.age || 0) > 7) { commitScore -= 2; results.warnings.push('Unusually high commit frequency'); }
  scores.commits = Math.max(0, Math.min(20, commitScore));

  // Contributors (0-15)
  let contribScore = 5;
  if (contribs.length >= 5) contribScore += 4;
  else if (contribs.length >= 2) contribScore += 2;
  if (busFactor >= 2) contribScore += 3;
  if (suspiciousContribs.length > 0) {
    // Scale penalty by repo quality signals — new accounts with good hygiene are less suspicious
    const hygieneSignals = [hasTests, hasCI, hasLicense, hasSecurityPolicy, hasContributing, hasDocs].filter(Boolean).length;
    const suspPenalty = hygieneSignals >= 4 ? 1 : hygieneSignals >= 2 ? 2 : 4;
    contribScore -= suspPenalty;
    results.flags.push(`${suspiciousContribs.length} suspicious contributor account(s)`);
  }
  scores.contributors = Math.max(0, Math.min(15, contribScore));

  // Code quality (0-25)
  let qualityScore = 5;
  if (hasTests) qualityScore += 4;
  if (hasCI) qualityScore += 3;
  if (hasLicense) qualityScore += 2;
  if (hasReadme) qualityScore += 2;
  if (hasGitignore) qualityScore += 1;
  if (hasPackageLock) qualityScore += 2;
  if (hasDocs) qualityScore += 2;
  if (hasContributing) qualityScore += 1;
  if (hasChangelog) qualityScore += 1;
  if (hasSecurityPolicy) qualityScore += 1;
  if (files.length < 5) { qualityScore -= 3; results.warnings.push('Very few files'); }
  scores.codeQuality = Math.max(0, Math.min(25, qualityScore));

  // AI slop (0-15, higher = better/less slop)
  let slopScore = 15;
  slopScore -= Math.min(8, aiHits.length * 2);
  if (emojiDensity > 3) { slopScore -= 3; results.warnings.push('High emoji density in README'); }
  if (readmeLength > 10000 && commits.length < 5) { slopScore -= 3; results.flags.push('Long README with few commits — possible AI-generated'); }
  scores.aiAuthenticity = Math.max(0, Math.min(15, slopScore));

  // Social health (0-10)
  let socialScore = 5;
  if (r.stargazers_count >= 100) socialScore += 2;
  if (r.forks_count >= 10) socialScore += 2;
  if (bottedStars) { socialScore -= 4; results.flags.push('Possible botted stars (high stars, no forks/contributors)'); }
  scores.social = Math.max(0, Math.min(10, socialScore));

  // Activity (0-10)
  let activityScore = 5;
  if (daysSinceLastPush < 7) activityScore += 3;
  else if (daysSinceLastPush < 30) activityScore += 2;
  else if (daysSinceLastPush < 90) activityScore += 1;
  else if (daysSinceLastPush > 365) { activityScore -= 3; results.warnings.push('No commits in over a year'); }
  if (releases.length > 0) activityScore += 2;
  scores.activity = Math.max(0, Math.min(10, activityScore));

  // Crypto risk (0-5, deductions only)
  let cryptoScore = 5;
  cryptoScore -= Math.min(5, cryptoFlags.length * 2);
  if (cryptoFlags.length > 0) results.flags.push(...cryptoFlags);
  scores.cryptoRisk = Math.max(0, cryptoScore);

  // Dependencies Audit (0-10)
  scores.dependencyAudit = results.dependencies.score;
  if (results.dependencies.flags.length > 0) {
    results.flags.push(...results.dependencies.flags);
  }

  // Author verification (bonus/penalty to commits score)
  const unverifiedCorpClaims = authorVerification.filter(a => a.claimedOrg && !a.verified);
  if (unverifiedCorpClaims.length > 0) {
    scores.commits = Math.max(0, scores.commits - unverifiedCorpClaims.length * 3);
    for (const a of unverifiedCorpClaims) {
      results.flags.push(`Unverified ${a.claimedOrg} identity: ${a.name} <${a.email}> — no GPG signature`);
    }
  }
  const verifiedAuthors = authorVerification.filter(a => a.verified);
  if (verifiedAuthors.length > 0) {
    scores.commits = Math.min(20, scores.commits + verifiedAuthors.length * 2);
  }

  // Security — old basic check (exposed files)
  let secDeduction = 0;
  if (secFlags.length > 0) { secDeduction = secFlags.length * 3; results.flags.push(...secFlags); }

  // Agent Safety score (0-15) — new security module
  // Maturity-based severity scaling: mature repos get benefit of the doubt
  const isMatureRepo = (r.stargazers_count >= 100) && (results.contributors && results.contributors.count >= 10);
  let effectiveCriticals = agentSafety.critical.length;
  let effectiveWarnings = agentSafety.warning.length;
  if (isMatureRepo) {
    // Downgrade ambiguous criticals for mature repos (keep real malware signals)
    effectiveCriticals = Math.max(0, effectiveCriticals - 1); // forgive 1 ambiguous critical
    effectiveWarnings = Math.max(0, effectiveWarnings - 2);   // forgive 2 ambiguous warnings
  }
  let safetyScore = 15;
  safetyScore -= Math.min(12, effectiveCriticals * 5); // each critical = -5, but cap at -12
  safetyScore -= Math.min(6, effectiveWarnings * 2);   // each warning = -2, cap at -6
  // Floor: 3/15 unless actual malware detected (crypto mining, exfiltration patterns)
  const hasMalwareSignals = agentSafety.critical.some(c => /crypto|miner|exfiltrat/i.test(c));
  const safetyFloor = hasMalwareSignals ? 0 : 3;
  scores.agentSafety2 = Math.max(safetyFloor, Math.min(15, safetyScore));
  if (agentSafety.critical.length > 0) {
    for (const c of agentSafety.critical) results.flags.push(`🔴 SECURITY: ${c}`);
  }

  // README quality (0-10)
  scores.readmeQuality = readmeQuality.score;

  // Maintainability (0-10)
  scores.maintainability = maintainability.score;

  // Project health (0-10) — abandoned/stale detection + issue response + PR patterns
  let healthScore = 5;
  if (projectStatus === 'active') healthScore += 2;
  else if (projectStatus === 'stale') healthScore -= 2;
  else if (projectStatus === 'abandoned') healthScore -= 4;
  else if (projectStatus === 'archived') healthScore -= 3;
  if (projectStatus === 'neglected') healthScore -= 1;

  if (issueResponse.respondedPct !== null) {
    if (issueResponse.respondedPct >= 80) healthScore += 1;
    else if (issueResponse.respondedPct < 30) healthScore -= 1;
  }
  if (prPatterns.pattern === 'reviewed') healthScore += 1;
  else if (prPatterns.pattern === 'self-merge' && Object.keys(authors).length > 2) healthScore -= 1;

  if (velocityTrend.trend === 'accelerating') healthScore += 1;
  else if (velocityTrend.trend === 'declining') healthScore -= 1;

  scores.projectHealth = Math.max(0, Math.min(10, healthScore));

  // Fork Comparison (0-8) — fork quality and divergence analysis
  let forkScore = 8; // non-forks get full marks — fork comparison only penalizes bad forks
  if (results.forkAnalysis.isFork) {
    forkScore = results.forkAnalysis.score || 0; // Use the calculated fork quality score
    if (results.forkAnalysis.quality === 'meaningful') {
      forkScore = 8; // Bonus for meaningful forks
    } else if (results.forkAnalysis.quality === 'gutted' || results.forkAnalysis.quality === 'identical') {
      forkScore = 0; // Major penalty for gutted or identical forks
    } else if (results.forkAnalysis.quality === 'suspicious') {
      forkScore = 1; // Heavy penalty for suspicious changes
    }
  }
  scores.forkComparison = Math.max(0, Math.min(8, forkScore));

  // Originality (0-5) — copy-paste, template detection, license
  let origScore = 5;
  if (copyPaste.isTemplate) origScore -= 2;
  if (copyPaste.signals.length > 2) origScore -= 1;
  if (licenseRisk.risk === 'high' && !licenseRisk.license) origScore -= 1;
  scores.originality = Math.max(0, Math.min(5, origScore));

  // Total (normalize to 100)
  const rawTotal = Object.values(scores).reduce((a, b) => a + b, 0) - secDeduction;
  const maxPossible = 168; // 20+15+25+15+10+10+5+10+10+10+5+15+10+8 (added dependencyAudit:10 + forkComparison:8)
  results.trustScore = Math.max(0, Math.min(100, Math.round(rawTotal / maxPossible * 100)));

  // Hard caps for fundamentally untrustworthy repos
  const repoAgeDays = results.meta?.age || 0;
  const stars = results.meta?.stars || 0;
  // Hard caps for new repos, softened by hygiene signals
  const hygieneCount = [hasTests, hasCI, hasLicense, hasSecurityPolicy, hasContributing, hasDocs, hasChangelog].filter(Boolean).length;
  if (repoAgeDays <= 7 && stars === 0) {
    const cap = hygieneCount >= 5 ? 60 : hygieneCount >= 3 ? 50 : 40;
    results.trustScore = Math.min(results.trustScore, cap);
    if (!results.warnings.includes('Brand new repo (<7 days) with zero stars — score capped'))
      results.warnings.push('Brand new repo (<7 days) with zero stars — score capped');
  } else if (repoAgeDays <= 7 && stars < 10) {
    const safetyPassed = agentSafety.verdict === 'PASS';
    const cap = (hygieneCount >= 5 && safetyPassed) ? 80 : hygieneCount >= 5 ? 70 : hygieneCount >= 3 ? 60 : 55;
    results.trustScore = Math.min(results.trustScore, cap);
  }

  results.scores = scores;

  // Grade
  if (results.trustScore >= 85) results.grade = 'A';
  else if (results.trustScore >= 70) results.grade = 'B';
  else if (results.trustScore >= 55) results.grade = 'C';
  else if (results.trustScore >= 40) results.grade = 'D';
  else results.grade = 'F';

  return results;
}

// --- Output ---
function printReport(r) {
  const meta = r.meta;
  console.log(`\n${'═'.repeat(60)}`);
  console.log(`  GITHUB REPO ANALYSIS: ${meta.name}`);
  console.log(`${'═'.repeat(60)}\n`);

  // Trust score
  const bar = '█'.repeat(Math.round(r.trustScore / 5)) + '░'.repeat(20 - Math.round(r.trustScore / 5));
  console.log(`  TRUST SCORE: ${r.trustScore}/100 [${r.grade}]`);
  console.log(`  ${bar}\n`);

  // Score breakdown
  console.log(`  BREAKDOWN:`);
  const labels = {
    commits: 'Commit Health',
    contributors: 'Contributors',
    codeQuality: 'Code Quality',
    aiAuthenticity: 'AI Authenticity',
    social: 'Social Signals',
    activity: 'Activity',
    cryptoRisk: 'Crypto Safety',
    dependencyAudit: 'Dependency Audit',
    forkComparison: 'Fork Quality',
    readmeQuality: 'README Quality',
    maintainability: 'Maintainability',
    projectHealth: 'Project Health',
    originality: 'Originality',
    agentSafety2: 'Agent Safety',
  };
  const maxes = { 
    commits: 20, contributors: 15, codeQuality: 25, aiAuthenticity: 15, social: 10, activity: 10, cryptoRisk: 5, 
    dependencyAudit: 10, forkComparison: 8, readmeQuality: 10, maintainability: 10, projectHealth: 10, 
    originality: 5, agentSafety2: 15 
  };
  
  for (const [key, label] of Object.entries(labels)) {
    const score = r.scores[key];
    const max = maxes[key];
    const pct = Math.round(score / max * 100);
    const miniBar = '█'.repeat(Math.round(pct / 10)) + '░'.repeat(10 - Math.round(pct / 10));
    console.log(`    ${label.padEnd(18)} ${miniBar} ${score}/${max}`);
  }

  // Metadata
  console.log(`\n  REPO INFO:`);
  console.log(`    Language: ${meta.language || 'N/A'} | Stars: ${meta.stars} | Forks: ${meta.forks}`);
  console.log(`    Created: ${meta.createdAt?.split('T')[0]} | Last push: ${meta.pushedAt?.split('T')[0]}`);
  console.log(`    Age: ${r.activity.ageDays} days | License: ${meta.license || 'NONE'}`);
  if (meta.isForked) console.log(`    ⚠️ FORK of ${meta.parent}`);
  if (meta.topics.length > 0) console.log(`    Topics: ${meta.topics.join(', ')}`);

  // Commits
  console.log(`\n  COMMITS:`);
  console.log(`    Total: ${r.commits.total} (${r.commits.human} human, ${r.commits.bot} bot) | Per day: ${r.commits.commitsPerDay} | GPG signed: ${r.commits.gpgRate}%`);
  console.log(`    Authors: ${r.commits.authors.length}`);
  for (const a of r.commits.authors.slice(0, 5)) {
    console.log(`      ${a.name} <${a.email}> — ${a.commits} commits`);
  }

  // Contributors
  if (r.contributors.suspiciousAccounts.length > 0) {
    console.log(`\n  ⚠️ SUSPICIOUS ACCOUNTS:`);
    for (const s of r.contributors.suspiciousAccounts) {
      console.log(`    ${s.login} — account ${s.ageDays} days old, ${s.repos} repos, ${s.followers} followers`);
    }
  }

  // Code quality
  console.log(`\n  CODE QUALITY:`);
  const checks = [
    ['Tests', r.codeQuality.hasTests],
    ['CI/CD', r.codeQuality.hasCI],
    ['License', r.codeQuality.hasLicense],
    ['README', r.codeQuality.hasReadme],
    ['.gitignore', r.codeQuality.hasGitignore],
    ['Lock file', r.codeQuality.hasPackageLock],
    ['Docs', r.codeQuality.hasDocs],
    ['Changelog', r.codeQuality.hasChangelog],
  ];
  console.log(`    ${checks.map(([name, has]) => `${has ? '+' : '-'}${name}`).join('  ')}`);
  console.log(`    Files: ${r.codeQuality.totalFiles} | Top extensions: ${r.codeQuality.extensions.slice(0, 5).map(([e, c]) => `.${e}(${c})`).join(' ')}`);

  // AI slop
  if (r.codeQuality.aiSlop.hits > 0) {
    console.log(`\n  AI SLOP DETECTED (${r.codeQuality.aiSlop.hits} patterns):`);
    for (const p of r.codeQuality.aiSlop.patterns) {
      console.log(`    - ${p}`);
    }
  }

  // Enhanced Dependencies Audit
  if (r.dependencies && r.dependencies.totalDeps > 0) {
    console.log(`\n  DEPENDENCY AUDIT (${r.dependencies.score}/10):`);
    console.log(`    Total: ${r.dependencies.totalDeps} (${r.dependencies.directDeps} direct, ${r.dependencies.devDeps} dev)`);
    if (r.dependencies.transitiveDeps > 0) {
      console.log(`    Estimated transitive: ~${r.dependencies.transitiveDeps}${r.dependencies.transitiveDeps > 1000 ? ' (BLOATED)' : ''}`);
    }
    console.log(`    Lock file: ${r.dependencies.hasLockFile ? 'Yes' : 'No'}${!r.dependencies.hasLockFile && r.dependencies.totalDeps > 5 ? ' ⚠️' : ''}`);
    
    if (r.dependencies.malicious.length > 0) {
      console.log(`    🔴 MALICIOUS PACKAGES:`);
      for (const m of r.dependencies.malicious) {
        console.log(`      ${m.name}@${m.version} — ${m.reason}`);
      }
    }
    
    if (r.dependencies.typosquats.length > 0) {
      console.log(`    🟡 TYPOSQUATTING:`);
      for (const t of r.dependencies.typosquats) {
        console.log(`      ${t.fake} (should be ${t.real}?)`);
      }
    }
    
    if (r.dependencies.installHooks.length > 0) {
      console.log(`    ⚠️ INSTALL HOOKS:`);
      for (const h of r.dependencies.installHooks) {
        console.log(`      ${h.hook}: ${h.script.substring(0, 60)}${h.script.length > 60 ? '...' : ''}`);
      }
    }
    
    if (r.dependencies.suspicious.length > 0) {
      console.log(`    🟡 SUSPICIOUS:`);
      for (const s of r.dependencies.suspicious) {
        console.log(`      ${s.name} — ${s.reason}`);
      }
    }
    
    if (r.dependencies.flags.length > 0 && r.dependencies.malicious.length === 0) {
      console.log(`    Other issues:`);
      for (const f of r.dependencies.flags) console.log(`      ${f}`);
    }
  }

  // Author verification
  if (r.authorVerification && r.authorVerification.some(a => a.flags.length > 0)) {
    console.log(`\n  AUTHOR VERIFICATION:`);
    for (const a of r.authorVerification) {
      if (a.flags.length === 0) continue;
      const status = a.verified ? '✓ VERIFIED' : '✗ UNVERIFIED';
      console.log(`    ${a.name} <${a.email}> — ${status}`);
      if (a.githubUser) console.log(`      GitHub: @${a.githubUser} | Repos: ${a.publicRepos} | Followers: ${a.followers}`);
      for (const f of a.flags) console.log(`      ${f}`);
    }
  }

  // Author reputation (noteworthy only)
  if (r.authorReputation && r.authorReputation.length > 0) {
    console.log(`\n  AUTHOR REPUTATION:`);
    for (const a of r.authorReputation) {
      console.log(`    @${a.user}${a.name ? ` (${a.name})` : ''}:`);
      for (const n of a.notes) console.log(`      ${n}`);
    }
  }

  // Plugin formats
  if (r.pluginFormats && r.pluginFormats.length > 0) {
    console.log(`\n  PACKAGE FORMAT:`);
    for (const p of r.pluginFormats) {
      const status = p.valid ? '✓' : '✗';
      console.log(`    ${status} ${p.type} — ${p.details}`);
    }
  }

  // Maintainability
  if (r.maintainability) {
    const m = r.maintainability;
    console.log(`\n  MAINTAINABILITY:`);
    console.log(`    Code: ${m.codeFiles} files | Config: ${m.configFiles} | Docs: ${m.docFiles} | Code/Doc ratio: ${m.codeToDocRatio}`);
    console.log(`    Depth: max ${m.maxDepth}, avg ${m.avgDepth} | Avg file: ${(m.avgFileSize/1024).toFixed(1)}KB | Large files (>50KB): ${m.largeFiles}`);
  }

  // README quality
  if (r.readmeQuality && r.readmeQuality.score > 0) {
    const rq = r.readmeQuality.checks;
    const checks = [
      ['Install guide', rq.hasInstall],
      ['Code examples', rq.hasCodeExamples],
      ['API docs', rq.hasApiDocs],
      ['Structure', rq.hasStructure],
      ['Contributing', rq.hasContributing],
      ['License', rq.hasLicenseMention],
    ];
    console.log(`\n  README QUALITY (${r.readmeQuality.score}/${r.readmeQuality.maxScore}):`);
    console.log(`    ${checks.map(([name, has]) => `${has ? '+' : '-'}${name}`).join('  ')}`);
    console.log(`    ${rq.wordCount} words, ${rq.headingCount} headings, ${rq.codeBlockCount} code blocks`);
  }

  // Project health
  if (r.projectStatus) {
    const ps = r.projectStatus;
    const statusEmoji = { active: '🟢', stale: '🟡', neglected: '🟡', abandoned: '🔴', archived: '⚪' };
    let healthLine = `${statusEmoji[ps.status] || '⚪'} ${ps.status.toUpperCase()}`;
    if (ps.daysSincePush > 0) healthLine += ` (last push ${ps.daysSincePush}d ago)`;
    const extras = [];
    if (r.velocityTrend?.trend && r.velocityTrend.trend !== 'unknown') extras.push(`velocity: ${r.velocityTrend.trend}`);
    if (r.issueResponse?.avgResponseHrs !== null) extras.push(`avg issue close: ${r.issueResponse.avgResponseHrs}h`);
    if (r.prPatterns?.pattern !== 'unknown') extras.push(`PRs: ${r.prPatterns.pattern}${r.prPatterns.total > 0 ? ` (${r.prPatterns.selfMerged}/${r.prPatterns.total} self-merged)` : ''}`);
    if (extras.length > 0) healthLine += ` | ${extras.join(' | ')}`;
    if (ps.signals.length > 0) healthLine += `\n    ⚠️ ${ps.signals.join(', ')}`;
    console.log(`\n  PROJECT HEALTH:`);
    console.log(`    ${healthLine}`);
  }

  // Enhanced Fork Analysis
  if (r.forkAnalysis?.isFork) {
    console.log(`\n  FORK COMPARISON (${r.forkAnalysis.score}/8):`);
    if (r.forkAnalysis.summary) {
      console.log(`    ${r.forkAnalysis.summary}`);
    } else {
      console.log(`    Forked from ${r.forkAnalysis.parent} (${r.forkAnalysis.parentStars || '?'}⭐)`);
      if (r.forkAnalysis.aheadBy !== undefined) {
        console.log(`    ${r.forkAnalysis.aheadBy} commits ahead, ${r.forkAnalysis.behindBy} behind — ${r.forkAnalysis.quality || 'unknown'}`);
      }
    }
    
    if (r.forkAnalysis.changedFileTypes) {
      const types = r.forkAnalysis.changedFileTypes;
      const typesSummary = [];
      if (types.code > 0) typesSummary.push(`${types.code} code`);
      if (types.config > 0) typesSummary.push(`${types.config} config`);
      if (types.docs > 0) typesSummary.push(`${types.docs} docs`);
      if (types.ci > 0) typesSummary.push(`${types.ci} CI`);
      if (typesSummary.length > 0) {
        console.log(`    Changed files: ${typesSummary.join(', ')}`);
      }
    }
    
    if (r.forkAnalysis.findings && r.forkAnalysis.findings.length > 0) {
      console.log(`    Analysis:`);
      for (const finding of r.forkAnalysis.findings) {
        console.log(`      ${finding}`);
      }
    }
    
    if (r.forkAnalysis.suspiciousChanges && r.forkAnalysis.suspiciousChanges.length > 0) {
      console.log(`    🚨 Suspicious changes:`);
      for (const sc of r.forkAnalysis.suspiciousChanges.slice(0, 5)) {
        console.log(`      ${sc}`);
      }
      if (r.forkAnalysis.suspiciousChanges.length > 5) {
        console.log(`      ... and ${r.forkAnalysis.suspiciousChanges.length - 5} more`);
      }
    }
  }

  // License risk
  if (r.licenseRisk) {
    const lr = r.licenseRisk;
    const riskEmoji = { low: '🟢', medium: '🟡', high: '🔴', unknown: '⚪' };
    console.log(`\n  LICENSE: ${riskEmoji[lr.risk]} ${lr.details}`);
  }

  // Copy-paste detection
  if (r.copyPaste?.signals?.length > 0) {
    console.log(`\n  ORIGINALITY:`);
    if (r.copyPaste.isTemplate) console.log(`    🚩 Detected as ${r.copyPaste.templateMatch}`);
    for (const s of r.copyPaste.signals) console.log(`    - ${s}`);
  }

  // Backer verification
  if (r.backerVerification?.claims?.length > 0) {
    console.log(`\n  BACKER CLAIMS:`);
    for (const v of r.backerVerification.verified) console.log(`    ✓ ${v}`);
    for (const u of r.backerVerification.unverified) console.log(`    ✗ ${u}`);
  }

  // Network map
  if (r.networkMap && (Object.keys(r.networkMap.domains).length > 0 || r.networkMap.unknown.length > 0)) {
    console.log(`\n  NETWORK BEHAVIOR:`);
    for (const [cat, hosts] of Object.entries(r.networkMap.domains)) {
      console.log(`    ${cat}: ${hosts.join(', ')}`);
    }
    if (r.networkMap.unknown.length > 0) {
      console.log(`    ⚠️ Unknown: ${r.networkMap.unknown.join(', ')}`);
    }
  }

  // Secrets
  if (r.secretFindings && r.secretFindings.length > 0) {
    console.log(`\n  🔑 HARDCODED SECRETS:`);
    for (const s of r.secretFindings) {
      console.log(`    ${s.file}: ${s.type} (${s.preview})`);
    }
  }

  // Actions audit
  if (r.actionsAudit && r.actionsAudit.findings.length > 0) {
    console.log(`\n  CI/CD SECURITY (${r.actionsAudit.workflows} workflows):`);
    for (const f of r.actionsAudit.findings) {
      const icon = f.severity === 'critical' ? '🔴' : f.severity === 'warning' ? '🟡' : 'ℹ️';
      console.log(`    ${icon} ${f.file}: ${f.issue}`);
    }
  }

  // Permissions manifest
  if (r.permissions) {
    console.log(`\n  PERMISSIONS MANIFEST:`);
    if (r.permissions.details.length > 0) {
      for (const d of r.permissions.details) console.log(`    ${d}`);
    } else {
      console.log('    Minimal permissions — no network, file writes, or system commands detected');
    }
  }

  // Security history
  if (r.securityHistory?.advisories?.length > 0) {
    console.log(`\n  SECURITY HISTORY:`);
    for (const a of r.securityHistory.advisories.slice(0, 5)) {
      const sev = a.severity?.toUpperCase() || 'UNKNOWN';
      console.log(`    [${sev}] ${a.summary}${a.cve ? ` (${a.cve})` : ''}`);
    }
  }
  if (r.securityHistory?.hasSecurityPolicy) {
    console.log(`    ✓ Has SECURITY.md policy`);
  }
  if (r.securityHistory?.dependabotAlerts) {
    console.log(`    ✓ Dependabot configured`);
  }

  // Dependency tree
  if (r.depTreeInfo?.estimatedTransitive) {
    console.log(`\n  DEPENDENCY TREE:`);
    console.log(`    Estimated transitive deps: ~${r.depTreeInfo.estimatedTransitive}${r.depTreeInfo.bloated ? ' ⚠️ BLOATED' : ''}`);
  }

  // Complexity hotspots
  if (r.complexityHotspots && r.complexityHotspots.length > 0) {
    console.log(`\n  COMPLEXITY HOTSPOTS:`);
    for (const h of r.complexityHotspots) {
      console.log(`    ${h.file} (${h.sizeKB}KB${h.lines ? `, ${h.lines} lines` : ''}): ${h.indicators.join(', ')}`);
    }
  }

  // YARA Scan Results
  if (r.yaraResults) {
    const yr = r.yaraResults;
    if (yr.available) {
      if (yr.matches.length > 0) {
        console.log(`\n  YARA SCAN: 🔴 ${yr.matches.length} match(es) found`);
        for (const m of yr.matches) {
          console.log(`    🔴 ${m.file}: ${m.rule.replace(/_/g, ' ')}`);
        }
      } else if (args.verbose) {
        console.log(`\n  YARA SCAN: ✅ Clean (no matches)`);
      }
    } else if (args.verbose) {
      console.log(`\n  YARA SCAN: ⚠️ Not available (install yara for deterministic malware detection)`);
    }
  }

  // Agent Safety
  if (r.agentSafety) {
    const as = r.agentSafety;
    const vEmoji = { PASS: '🟢', CAUTION: '🟡', FAIL: '🔴' };
    console.log(`\n  AGENT SAFETY: ${vEmoji[as.verdict]} ${as.verdict}`);
    if (as.critical.length > 0) {
      for (const c of as.critical) console.log(`    🔴 ${c}`);
    }
    if (as.warning.length > 0) {
      for (const w of as.warning) console.log(`    🟡 ${w}`);
    }
    if (as.info.length > 0) {
      for (const i of as.info) console.log(`    ℹ️  ${i}`);
    }
    if (as.verdict === 'PASS' && as.critical.length === 0 && as.warning.length === 0) {
      console.log('    No security concerns detected.');
    }
  }

  // Flags
  if (r.flags.length > 0) {
    console.log(`\n  🚩 FLAGS:`);
    for (const f of r.flags) console.log(`    - ${f}`);
  }

  if (r.warnings.length > 0) {
    console.log(`\n  ⚠️ WARNINGS:`);
    for (const w of r.warnings) console.log(`    - ${w}`);
  }

  // Verdict
  console.log(`\n${'─'.repeat(60)}`);
  const verdicts = {
    'A': 'LEGIT — Well-maintained, real development activity, trustworthy.',
    'B': 'SOLID — Good signs overall, minor gaps. Probably legit.',
    'C': 'MIXED — Some concerns. Do more research before trusting.',
    'D': 'SKETCHY — Multiple red flags. Proceed with extreme caution.',
    'F': 'AVOID — Major red flags. High probability of scam/fake/abandoned.',
  };
  console.log(`  VERDICT [${r.grade}]: ${verdicts[r.grade]}`);
  console.log(`${'─'.repeat(60)}\n`);
}

// --- Badge generation ---
function generateBadge(results) {
  const score = results.trustScore;
  const grade = results.grade;
  let color = 'red';
  if (grade === 'A') color = 'brightgreen';
  else if (grade === 'B') color = 'green';
  else if (grade === 'C') color = 'yellow';
  else if (grade === 'D') color = 'orange';
  const label = `Trust_Score-${score}%2F100_${grade}`;
  return `![Trust Score](https://img.shields.io/badge/${label}-${color}?style=flat-square)`;
}

// --- Batch mode ---
async function batchAnalyze(filePath) {
  const fs = require('fs');
  const lines = fs.readFileSync(filePath, 'utf8').split('\n').map(l => l.trim()).filter(l => l && !l.startsWith('#'));
  
  console.log(`\nBatch analyzing ${lines.length} repos...\n`);
  const results = [];
  
  for (const line of lines) {
    const parsed = parseRepo(line);
    if (!parsed) {
      console.error(`  ✗ Cannot parse: ${line}`);
      continue;
    }
    try {
      const r = await analyzeRepo(parsed.owner, parsed.repo);
      results.push(r);
      const flagStr = r.flags.length > 0 ? ` (${r.flags.length} flags)` : '';
      console.log(`  ${r.grade} ${String(r.trustScore).padStart(3)}/100  ${r.meta.name}${flagStr}`);
    } catch (e) {
      console.error(`  ✗ ${parsed.owner}/${parsed.repo}: ${e.message}`);
    }
    // Delay to avoid rate limits
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  // Summary
  console.log(`\n${'═'.repeat(50)}`);
  console.log(`  BATCH SUMMARY: ${results.length} repos analyzed`);
  console.log(`${'═'.repeat(50)}`);
  
  const grades = { A: 0, B: 0, C: 0, D: 0, F: 0 };
  for (const r of results) grades[r.grade]++;
  console.log(`  A: ${grades.A} | B: ${grades.B} | C: ${grades.C} | D: ${grades.D} | F: ${grades.F}`);
  
  const avg = results.length > 0 ? Math.round(results.reduce((a, r) => a + r.trustScore, 0) / results.length) : 0;
  console.log(`  Average score: ${avg}/100`);
  
  // Top and bottom
  const sorted = [...results].sort((a, b) => b.trustScore - a.trustScore);
  if (sorted.length >= 3) {
    console.log(`\n  TOP 3:`);
    for (const r of sorted.slice(0, 3)) console.log(`    ${r.trustScore}/100 [${r.grade}] ${r.meta.name}`);
    console.log(`\n  BOTTOM 3:`);
    for (const r of sorted.slice(-3).reverse()) console.log(`    ${r.trustScore}/100 [${r.grade}] ${r.meta.name}`);
  }
  console.log();
  
  return results;
}

// --- Main ---
async function main() {
  // Batch mode
  if (args.file) {
    const results = await batchAnalyze(args.file);
    if (args.json) console.log(JSON.stringify(results, null, 2));
    return;
  }

  const input = positionals[0];
  if (!input) {
    console.error('Usage: node analyze.js <github-url-or-owner/repo> [--json] [--verbose] [--oneline] [--badge]');
    console.error('       node analyze.js <x.com-or-twitter.com-tweet-url>');
    console.error('       node analyze.js --file repos.txt [--json]');
    console.error('  Optional: --token <github-token> or GITHUB_TOKEN env var for higher rate limits');
    process.exit(1);
  }

  // Handle X/Twitter URLs — extract GitHub repos from tweets
  if (isTwitterUrl(input)) {
    console.error('Detected X/Twitter URL — extracting GitHub repos from tweet...');
    const { repos, tweetText } = await extractReposFromTweet(input);
    if (repos.length === 0) {
      console.error('No GitHub repos found in tweet.');
      if (tweetText) console.error(`Tweet content:\n${tweetText}`);
      process.exit(1);
    }
    console.error(`Found ${repos.length} repo${repos.length > 1 ? 's' : ''}: ${repos.map(r => `${r.owner}/${r.repo}`).join(', ')}\n`);

    // Print tweet context
    if (tweetText && !args.json) {
      console.log(`${'─'.repeat(60)}`);
      console.log(`  TWEET CONTEXT:`);
      // Clean up bird CLI output formatting
      const lines = tweetText.trim().split('\n');
      for (const line of lines) {
        console.log(`  ${line}`);
      }
      console.log(`${'─'.repeat(60)}`);
    }

    const allResults = [];
    for (const parsed of repos) {
      try {
        const results = await analyzeRepo(parsed.owner, parsed.repo);
        allResults.push(results);
        if (args.json) { /* output after loop */ }
        else if (args.oneline) {
          const flagStr = results.flags.length > 0 ? ` — ${results.flags.length} flags` : '';
          console.log(`${results.meta.name}: ${results.trustScore}/100 [${results.grade}]${flagStr}`);
        } else printReport(results);
      } catch (e) {
        console.error(`Error analyzing ${parsed.owner}/${parsed.repo}: ${e.message}`);
      }
    }
    if (args.json) {
      const output = { tweet: { url: input, text: tweetText }, repos: allResults };
      console.log(JSON.stringify(output, null, 2));
    }
    return;
  }

  const parsed = parseRepo(input);
  if (!parsed) {
    console.error(`Cannot parse repo from: ${input}`);
    process.exit(1);
  }

  try {
    const results = await analyzeRepo(parsed.owner, parsed.repo);
    if (args.badge) {
      console.log(generateBadge(results));
    } else if (args.oneline) {
      const flagCount = results.flags.length;
      const flagStr = flagCount > 0 ? ` — ${flagCount} flag${flagCount > 1 ? 's' : ''}` : '';
      console.log(`${results.meta.name}: ${results.trustScore}/100 [${results.grade}]${flagStr}`);
    } else if (args.json) {
      console.log(JSON.stringify(results, null, 2));
    } else {
      printReport(results);
    }
  } catch (e) {
    console.error('Error:', e.message);
    if (e.message.includes('rate limit')) {
      console.error('Tip: Set GITHUB_TOKEN env var or use --token for higher rate limits');
    }
    process.exit(1);
  }
}

main();
