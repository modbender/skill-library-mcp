#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const os = require('os');
const crypto = require('crypto');
const { JSDOM, VirtualConsole } = require('jsdom');
const { Readability } = require('@mozilla/readability');
const TurndownService = require('turndown');
const { Command } = require('commander');

const _fetch = global.fetch;
if (!_fetch) {
  console.error('This script requires Node 18+ for global fetch.');
  process.exit(1);
}

const DEFAULT_TIMEOUT_MS = Number(process.env.SMART_FETCH_TIMEOUT_MS || 15000);
const DEFAULT_RETRIES = Number(process.env.SMART_FETCH_RETRIES || 1);
const DISABLE_MARKDOWN_ENV = ['1', 'true', 'yes'].includes(String(process.env.SMART_FETCH_DISABLE_MARKDOWN || '').toLowerCase());
const MIN_BODY_CHARS = Number(process.env.SMART_FETCH_MIN_BODY_CHARS || 200);
const DEFAULT_MAX_CHARS = Number(process.env.SMART_FETCH_MAX_CHARS || 0);
const DEFAULT_MAX_BYTES = Number(process.env.SMART_FETCH_MAX_BYTES || 0);
const DEFAULT_CACHE_TTL = Number(process.env.SMART_FETCH_CACHE_TTL || 0);
const DEFAULT_CACHE_DIR = process.env.SMART_FETCH_CACHE_DIR || path.join(os.homedir(), '.cache', 'smart-fetch');

function parseCsvSet(v) {
  if (!v) return new Set();
  return new Set(String(v).split(',').map(s => s.trim().toLowerCase()).filter(Boolean));
}

const allowlist = parseCsvSet(process.env.SMART_FETCH_DOMAIN_ALLOWLIST);
const blocklist = parseCsvSet(process.env.SMART_FETCH_DOMAIN_BLOCKLIST);

function domainAllowed(hostname) {
  const host = String(hostname || '').toLowerCase();
  if (blocklist.has(host)) return false; // precedence: blocklist > allowlist > default
  if (allowlist.size > 0) return allowlist.has(host);
  return true;
}

function buildAcceptHeader(markdownEnabled) {
  return markdownEnabled
    ? 'text/markdown, text/html, application/xhtml+xml;q=0.9, */*;q=0.8'
    : 'text/html, application/xhtml+xml;q=0.9, */*;q=0.8';
}

function sha256(text) {
  return crypto.createHash('sha256').update(String(text || ''), 'utf8').digest('hex');
}

function stableCacheKey(parts) {
  return crypto.createHash('sha256').update(JSON.stringify(parts)).digest('hex');
}

function cacheFilePath(cacheDir, key) {
  return path.join(cacheDir, `${key}.json`);
}

function readCache(cacheDir, key) {
  try {
    const p = cacheFilePath(cacheDir, key);
    if (!fs.existsSync(p)) return null;
    return JSON.parse(fs.readFileSync(p, 'utf8'));
  } catch {
    return null;
  }
}

function writeCache(cacheDir, key, payload) {
  try {
    fs.mkdirSync(cacheDir, { recursive: true });
    const p = cacheFilePath(cacheDir, key);
    fs.writeFileSync(p, JSON.stringify(payload), 'utf8');
  } catch {
    // no-op
  }
}

async function fetchWithRetry(url, options, retries, debug) {
  let lastErr;
  for (let i = 0; i <= retries; i++) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), options.timeoutMs);
    try {
      const res = await _fetch(url, { headers: options.headers, signal: controller.signal, redirect: 'follow' });
      clearTimeout(timer);
      return res;
    } catch (err) {
      clearTimeout(timer);
      lastErr = err;
      if (debug) console.error(`Fetch attempt ${i + 1} failed: ${err.message}`);
      if (i < retries) {
        const backoffMs = 300 * (2 ** i); // exponential backoff
        await new Promise(r => setTimeout(r, backoffMs));
      }
    }
  }
  throw lastErr;
}

function htmlToMarkdown(html, url) {
  const virtualConsole = new VirtualConsole();
  const dom = new JSDOM(html, { url, virtualConsole });
  const article = new Readability(dom.window.document).parse();

  if (!article) {
    return {
      title: '',
      markdown: (dom.window.document.body?.textContent || '').trim(),
      warnings: ['readability_parse_failed']
    };
  }

  const turndownService = new TurndownService({ headingStyle: 'atx', codeBlockStyle: 'fenced' });
  turndownService.addRule('pre', {
    filter: ['pre'],
    replacement: content => `\n\n\`\`\`\n${content}\n\`\`\`\n\n`
  });

  const markdown = turndownService.turndown(article.content || '');
  return {
    title: article.title || '',
    markdown: article.title ? `# ${article.title}\n\n${markdown}` : markdown,
    warnings: []
  };
}

function truncateByCodePoints(text, maxCodePoints) {
  if (maxCodePoints <= 0) return text;
  const cps = Array.from(text || '');
  if (cps.length <= maxCodePoints) return text;
  return cps.slice(0, maxCodePoints).join('');
}

function closeFenceIfNeeded(text) {
  const matches = String(text || '').match(/```/g);
  const count = matches ? matches.length : 0;
  if (count % 2 === 1) return `${text}\n\n\`\`\``;
  return text;
}

function applyLimits(body, maxChars, maxBytes, warnings) {
  let out = body || '';

  // max-chars is Unicode codepoint count (not UTF-16 code units)
  if (maxChars > 0) {
    const beforeCount = Array.from(out).length;
    out = truncateByCodePoints(out, maxChars);
    const afterCount = Array.from(out).length;
    if (afterCount < beforeCount) warnings.push('truncated_by_max_chars');
  }

  if (maxBytes > 0) {
    const b = Buffer.byteLength(out, 'utf8');
    if (b > maxBytes) {
      let lo = 0, hi = out.length;
      while (lo < hi) {
        const mid = Math.floor((lo + hi + 1) / 2);
        if (Buffer.byteLength(out.slice(0, mid), 'utf8') <= maxBytes) lo = mid; else hi = mid - 1;
      }
      out = out.slice(0, lo);
      warnings.push('truncated_by_max_bytes');
    }
  }

  if (warnings.includes('truncated_by_max_chars') || warnings.includes('truncated_by_max_bytes')) {
    out = closeFenceIfNeeded(out);
  }

  return out;
}

function detectSafetyFlags(text) {
  const s = String(text || '').toLowerCase();
  const rules = [
    { key: 'contains_shell_exec_lure', re: /(curl\s+[^\n]*\|\s*(bash|sh))|(wget\s+[^\n]*\|\s*(bash|sh))/i },
    { key: 'contains_run_command_lure', re: /(run this command|execute in terminal|复制到终端执行)/i },
    { key: 'contains_download_and_execute_lure', re: /(download and run|下载安装并运行|粘贴并执行)/i },
    { key: 'contains_api_key_request', re: /(paste.*api key|share your api key|提供你的api key|输入你的token)/i }
  ];
  return rules.filter(r => r.re.test(s)).map(r => r.key);
}

function routeAdvice(pathName, warnings) {
  // enum-based actions for stable downstream routing
  if (warnings.includes('readability_parse_failed') && pathName === 'html_fallback') {
    return { severity: 'error', recommendedNextAction: 'retry_with_alternate_extractor' };
  }
  if (warnings.includes('body_too_short')) {
    return { severity: 'warn', recommendedNextAction: 'retry_with_higher_limits' };
  }
  if (warnings.includes('truncated_by_max_chars') || warnings.includes('truncated_by_max_bytes')) {
    return { severity: 'warn', recommendedNextAction: 'retry_with_higher_limits' };
  }
  if (pathName === 'other') {
    return { severity: 'warn', recommendedNextAction: 'skip_summarization_use_metadata_only' };
  }
  return { severity: 'info', recommendedNextAction: 'none' };
}

function emit(result, asJson) {
  if (asJson) console.log(JSON.stringify(result, null, 2));
  else console.log(result.body || '');
}

const program = new Command();
program
  .name('smart-fetch')
  .description('Fetch URL content with markdown-first negotiation and HTML fallback extraction')
  .argument('<url>', 'URL to fetch')
  .option('-d, --debug', 'Show debug info')
  .option('-r, --raw', 'Return raw content if markdown fetch fails', false)
  .option('--json', 'Output structured metadata + body as JSON', false)
  .option('--timeout <ms>', 'Request timeout in ms', String(DEFAULT_TIMEOUT_MS))
  .option('--retries <n>', 'Retry count on network failure', String(DEFAULT_RETRIES))
  .option('--no-markdown', 'Disable markdown negotiation and force HTML-first mode')
  .option('--max-chars <n>', 'Hard output Unicode codepoint limit (0=disabled)', String(DEFAULT_MAX_CHARS))
  .option('--max-bytes <n>', 'Hard output byte limit (0=disabled)', String(DEFAULT_MAX_BYTES))
  .option('--cache-ttl <sec>', 'Cache TTL seconds (<=0 disables cache)', String(DEFAULT_CACHE_TTL))
  .option('--cache-dir <path>', 'Cache directory', DEFAULT_CACHE_DIR)
  .action(async (url, options) => {
    const startedAt = Date.now();
    const warnings = [];

    try {
      const u = new URL(url);
      if (!domainAllowed(u.hostname)) throw new Error(`Domain blocked by policy: ${u.hostname}`);

      const markdownEnabled = !DISABLE_MARKDOWN_ENV && options.markdown !== false; // env disable has highest priority
      const timeoutMs = Number(options.timeout || DEFAULT_TIMEOUT_MS);
      const retries = Math.max(0, Number(options.retries || DEFAULT_RETRIES));
      const maxChars = Math.max(0, Number(options.maxChars || DEFAULT_MAX_CHARS));
      const maxBytes = Math.max(0, Number(options.maxBytes || DEFAULT_MAX_BYTES));
      const cacheTtl = Math.max(0, Number(options.cacheTtl || DEFAULT_CACHE_TTL));
      const cacheDir = options.cacheDir || DEFAULT_CACHE_DIR;

      const policyKey = {
        url,
        markdownEnabled,
        raw: !!options.raw,
        maxChars,
        maxBytes
      };
      const ck = stableCacheKey(policyKey);

      if (options.debug) {
        console.error(`Fetching: ${url}`);
        console.error(`markdownEnabled=${markdownEnabled}, timeoutMs=${timeoutMs}, retries=${retries}, maxChars=${maxChars}, maxBytes=${maxBytes}, cacheTtl=${cacheTtl}`);
      }

      const cached = cacheTtl > 0 ? readCache(cacheDir, ck) : null;
      if (cached && Date.now() - (cached.fetchedAt || 0) < cacheTtl * 1000) {
        const out = {
          ...cached,
          path: 'cache_hit',
          cacheHit: true,
          revalidated: false,
          latencyMs: Date.now() - startedAt
        };
        out.contentSafetyFlags = detectSafetyFlags(out.body);
        Object.assign(out, routeAdvice(out.path, out.warnings || []));
        emit(out, options.json);
        return;
      }

      const reqHeaders = {
        'User-Agent': 'SmartFetch/1.2.1 (OpenClaw)',
        Accept: buildAcceptHeader(markdownEnabled)
      };
      if (cached?.etag) reqHeaders['If-None-Match'] = cached.etag;
      if (cached?.lastModified) reqHeaders['If-Modified-Since'] = cached.lastModified;

      const response = await fetchWithRetry(url, { timeoutMs, headers: reqHeaders }, retries, options.debug);

      if (response.status === 304 && cached) {
        const out = {
          ...cached,
          path: 'cache_revalidated_304',
          cacheHit: true,
          revalidated: true,
          latencyMs: Date.now() - startedAt,
          fetchedAt: Date.now()
        };
        out.contentSafetyFlags = detectSafetyFlags(out.body);
        Object.assign(out, routeAdvice(out.path, out.warnings || []));
        writeCache(cacheDir, ck, out);
        emit(out, options.json);
        return;
      }

      const status = response.status;
      const finalUrl = response.url || url;
      const contentType = (response.headers.get('content-type') || '').toLowerCase();
      const markdownTokens = response.headers.get('x-markdown-tokens');
      const etag = response.headers.get('etag');
      const lastModified = response.headers.get('last-modified');
      const text = await response.text();

      if (!response.ok) throw new Error(`HTTP ${status}`);

      let pathName = 'other';
      let body = text;

      if (contentType.includes('text/markdown')) {
        pathName = 'markdown_direct';
      } else if (contentType.includes('text/html')) {
        if (options.raw) {
          pathName = 'html_raw';
        } else {
          pathName = 'html_fallback';
          const converted = htmlToMarkdown(text, finalUrl);
          body = converted.markdown;
          warnings.push(...converted.warnings);
          if (!converted.title) warnings.push('missing_title');
          if ((body || '').trim().length < MIN_BODY_CHARS) warnings.push('body_too_short');
        }
      } else {
        warnings.push('non_html_or_markdown_content_type');
      }

      // limits always apply to final body
      body = applyLimits(body, maxChars, maxBytes, warnings);
      const contentHash = sha256(body);
      const contentSafetyFlags = detectSafetyFlags(body);

      const result = {
        url,
        finalUrl,
        status,
        contentType,
        path: pathName,
        cacheHit: false,
        revalidated: false,
        markdownTokens: markdownTokens ? Number(markdownTokens) : null,
        bytes: Buffer.byteLength(body || '', 'utf8'),
        latencyMs: Date.now() - startedAt,
        etag,
        lastModified,
        contentHash,
        warnings,
        contentSafetyFlags,
        ...routeAdvice(pathName, warnings),
        body,
        fetchedAt: Date.now()
      };

      if (cacheTtl > 0) writeCache(cacheDir, ck, result);
      emit(result, options.json);
    } catch (error) {
      const result = {
        url,
        finalUrl: null,
        status: null,
        contentType: null,
        path: 'error',
        cacheHit: false,
        revalidated: false,
        markdownTokens: null,
        bytes: 0,
        latencyMs: Date.now() - startedAt,
        warnings: ['fetch_error'],
        contentSafetyFlags: [],
        severity: 'error',
        recommendedNextAction: 'manual_review_needed',
        error: error.message,
        body: ''
      };
      if (options.json) console.log(JSON.stringify(result, null, 2));
      else console.error(`Error: ${error.message}`);
      process.exit(1);
    }
  });

program.parse();
