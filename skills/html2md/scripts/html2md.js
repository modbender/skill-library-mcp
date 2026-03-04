#!/usr/bin/env node

import { Readability } from '@mozilla/readability';
import { JSDOM } from 'jsdom';
import TurndownService from 'turndown';
import { readFileSync } from 'fs';

// ─── CLI Arg Parsing ─────────────────────────────────────────────────────────

const args = process.argv.slice(2);

function flag(name) {
  const i = args.indexOf(name);
  if (i !== -1) { args.splice(i, 1); return true; }
  return false;
}

function option(name) {
  const i = args.indexOf(name);
  if (i !== -1 && args[i + 1] !== undefined) {
    const val = args[i + 1];
    args.splice(i, 2);
    return val;
  }
  return null;
}

const _maxTokensRaw = option('--max-tokens');
const opts = {
  file:      option('--file'),
  stdin:     flag('--stdin'),
  maxTokens: _maxTokensRaw !== null ? parseInt(_maxTokensRaw) : null,
  noTables:  flag('--no-tables'),
  noLinks:   flag('--no-links'),
  noImages:  flag('--no-images'),
  json:      flag('--json'),
  help:      flag('--help') || flag('-h'),
};

const url = args.find(a => !a.startsWith('-')) || null;

if (opts.help) {
  console.log(`
html2md — Convert HTML pages to clean markdown

USAGE:
  html2md <url>                    Fetch URL and convert
  html2md --file <path>            Convert local HTML file
  cat page.html | html2md --stdin  Read HTML from stdin
  html2md --max-tokens 2000 <url>  Truncate to token budget
  html2md --no-tables <url>        Tables → bullet lists
  html2md --no-links <url>         Strip link URLs, keep text
  html2md --no-images <url>        Strip image references
  html2md --json <url>             Output JSON: {title, url, markdown, tokens}
  html2md --help                   Show this help
`.trim());
  process.exit(0);
}

// ─── Error Helper ────────────────────────────────────────────────────────────

function die(msg) {
  console.error(`html2md: ${msg}`);
  process.exit(1);
}

// ─── Token Counter (1 token ≈ 4 chars heuristic) ─────────────────────────────

function countTokens(text) {
  return Math.ceil(text.length / 4);
}

// ─── Fetch HTML ───────────────────────────────────────────────────────────────

async function fetchHtml(url) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 15000);

  let response;
  try {
    response = await fetch(url, {
      signal: controller.signal,
      redirect: 'follow',
      headers: {
        'User-Agent': 'html2md/1.0 (agent-friendly HTML converter; +https://github.com/openclaw/html2md)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
      },
    });
  } catch (err) {
    if (err.name === 'AbortError') die(`Timeout: request exceeded 15s for ${url}`);
    const cause = err.cause?.message || err.message;
    die(`Network error fetching ${url}: ${cause}`);
  } finally {
    clearTimeout(timer);
  }

  if (!response.ok) die(`HTTP ${response.status} ${response.statusText} — ${url}`);

  const ct = response.headers.get('content-type') || '';
  if (!ct.includes('html') && !ct.includes('xml') && !ct.includes('text')) {
    die(`Non-HTML content type: ${ct} — use a different tool for binary content`);
  }

  return { html: await response.text(), finalUrl: response.url };
}

// ─── Extract with Readability ─────────────────────────────────────────────────

function bodyFallback(dom) {
  // Remove noisy elements before using full body
  const doc = dom.window.document;
  const noise = ['script', 'style', 'noscript', 'nav', 'header', 'footer',
    'aside', 'form', 'iframe', 'svg', 'button', 'input', 'select',
    'textarea', '[role="banner"]', '[role="navigation"]', '[role="complementary"]',
    '[role="contentinfo"]', '.cookie-banner', '.ad', '.advertisement'];
  for (const sel of noise) {
    try {
      doc.querySelectorAll(sel).forEach(el => el.remove());
    } catch {}
  }
  const body = doc.body;
  return body ? body.innerHTML : '';
}

function extractContent(html, pageUrl) {
  const dom = new JSDOM(html, { url: pageUrl || 'http://localhost/' });
  const title = dom.window.document.title || '';

  const reader = new Readability(dom.window.document.cloneNode(true), {
    charThreshold: 0,
    keepClasses: false,
  });

  const article = reader.parse();

  // Quality check: if Readability returns too little content, fall back to body
  const MIN_WORDS = 30;
  const wordCount = (str) => str ? str.trim().split(/\s+/).length : 0;

  if (!article || wordCount(article.content) < MIN_WORDS) {
    return {
      title,
      content: bodyFallback(dom),
    };
  }

  return {
    title: article.title || title,
    content: article.content || '',
  };
}

// ─── Turndown Setup ────────────────────────────────────────────────────────────

function buildTurndown(opts) {
  const td = new TurndownService({
    headingStyle: 'atx',
    hr: '---',
    bulletListMarker: '-',
    codeBlockStyle: 'fenced',
    emDelimiter: '_',
    strongDelimiter: '**',
    linkStyle: 'inlined',
  });

  // Remove script/style/nav/footer/aside/form by default
  td.remove(['script', 'style', 'nav', 'footer', 'aside', 'form', 'noscript', 'iframe', 'svg', 'button', 'input', 'select', 'textarea']);

  // Handle images
  td.addRule('images', {
    filter: 'img',
    replacement: (content, node) => {
      if (opts.noImages) return '';
      const alt = node.getAttribute('alt') || '';
      if (!alt.trim()) return '';
      return `[image: ${alt.trim()}]`;
    },
  });

  // Handle links
  if (opts.noLinks) {
    td.addRule('links', {
      filter: 'a',
      replacement: (content) => content || '',
    });
  }

  // Handle tables → bullet lists if --no-tables
  if (opts.noTables) {
    td.addRule('tableRows', {
      filter: ['table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td'],
      replacement: (content, node) => {
        const tag = node.nodeName.toLowerCase();
        if (tag === 'td' || tag === 'th') {
          return content.trim() ? `- ${content.trim()}\n` : '';
        }
        if (tag === 'tr') return content;
        if (tag === 'table') return `\n${content}\n`;
        return content;
      },
    });
  }

  return td;
}

// ─── Post-Processing ──────────────────────────────────────────────────────────

const SOCIAL_CTA_PATTERNS = [
  /share (on|to|via) (twitter|facebook|linkedin|instagram|reddit|whatsapp)/gi,
  /tweet this/gi,
  /share this (post|article|story|page)/gi,
  /follow (us|me) on (twitter|facebook|instagram|linkedin)/gi,
  /subscribe to (our|my|the) newsletter/gi,
  /sign up for (our|my|the) newsletter/gi,
  /get (updates|articles|posts) (in your inbox|by email|via email)/gi,
  /join [\d,k+]+ (readers|subscribers)/gi,
  /sponsored by|advertisement|ad choices/gi,
];

// Only match actual breadcrumb separators (not URL slashes)
const BREADCRUMB_PATTERN = /^(\S[^[(\n]*?\s*[›»]\s*){2,}\S[^[(\n]*$/gm;

function postProcess(md, opts) {
  // Strip HTML comments
  md = md.replace(/<!--[\s\S]*?-->/g, '');

  // Remove empty markdown links [](url) → ''
  md = md.replace(/\[]\([^)]*\)/g, '');

  // Remove zero-width chars, soft hyphens, non-breaking spaces → space
  md = md.replace(/[\u00AD\u200B\u200C\u200D\u200E\u200F\uFEFF]/g, '');
  md = md.replace(/\u00A0/g, ' ');

  // Remove social CTAs (line-by-line)
  const lines = md.split('\n');
  const filtered = lines.filter(line => {
    const trimmed = line.trim();
    if (!trimmed) return true; // keep blank lines for now
    return !SOCIAL_CTA_PATTERNS.some(p => { p.lastIndex = 0; return p.test(trimmed); });
  });
  md = filtered.join('\n');

  // Remove breadcrumb lines (e.g. "Home › Blog › Article")
  md = md.replace(BREADCRUMB_PATTERN, '');

  // Remove empty headings (## or ### with nothing after)
  md = md.replace(/^#{1,6}\s*$/gm, '');

  // Remove lines that are just punctuation/noise after stripping
  md = md.replace(/^[\s*_\-=]{0,3}$/gm, '');

  // Collapse 3+ consecutive blank lines → 2
  md = md.replace(/\n{3,}/g, '\n\n');

  // Strip trailing whitespace on each line
  md = md.split('\n').map(l => l.trimEnd()).join('\n');

  // Trim overall
  md = md.trim();

  return md;
}

// ─── Token Budget Truncation ──────────────────────────────────────────────────

function truncateToTokens(md, maxTokens) {
  const total = countTokens(md);
  if (total <= maxTokens) return md;

  const lines = md.split('\n');

  // Collect heading lines first
  const headingLines = lines.filter(l => /^#{1,6}\s/.test(l));

  const headingBlock = headingLines.join('\n');
  let budget = maxTokens - countTokens(headingBlock) - 20; // reserve for truncation note

  if (budget <= 0) {
    const note = `\n\n[truncated — ${total - countTokens(headingBlock)} more tokens]`;
    return headingBlock + note;
  }

  // Walk lines in document order, skip heading lines (already included), fill budget
  const body = [];
  for (const line of lines) {
    if (/^#{1,6}\s/.test(line)) continue; // headings already at top
    const cost = countTokens(line + '\n');
    if (budget - cost < 0) break;
    body.push(line);
    budget -= cost;
  }

  const remaining = total - maxTokens;
  const truncNote = `\n\n[truncated — ${remaining > 0 ? remaining : 1} more tokens]`;

  let result = headingBlock;
  if (body.length) result += '\n\n' + body.join('\n');
  result += truncNote;

  return result.trim();
}

// ─── Main ─────────────────────────────────────────────────────────────────────

async function main() {
  let html = '';
  let pageUrl = '';
  let title = '';

  if (opts.stdin) {
    // Read from stdin
    const chunks = [];
    for await (const chunk of process.stdin) chunks.push(chunk);
    html = Buffer.concat(chunks).toString('utf8');
    pageUrl = url || 'http://localhost/';
  } else if (opts.file) {
    try {
      html = readFileSync(opts.file, 'utf8');
      pageUrl = `file://${opts.file}`;
    } catch (err) {
      die(`Cannot read file: ${opts.file} — ${err.message}`);
    }
  } else if (url) {
    const result = await fetchHtml(url);
    html = result.html;
    pageUrl = result.finalUrl;
  } else {
    die('No input specified. Usage: html2md <url> | --file <path> | --stdin\nRun html2md --help for more info.');
  }

  // Extract
  const extracted = extractContent(html, pageUrl);
  title = extracted.title;

  // Convert
  const td = buildTurndown(opts);
  let markdown = td.turndown(extracted.content);

  // Post-process
  markdown = postProcess(markdown, opts);

  // Prepend title if not already first heading
  if (title && !markdown.startsWith('# ')) {
    markdown = `# ${title}\n\n${markdown}`;
  }

  // Token budget
  if (opts.maxTokens) {
    markdown = truncateToTokens(markdown, opts.maxTokens);
  }

  const tokens = countTokens(markdown);

  // Output
  if (opts.json) {
    const out = {
      title,
      url: pageUrl,
      markdown,
      tokens,
    };
    process.stdout.write(JSON.stringify(out, null, 2) + '\n');
  } else {
    process.stdout.write(markdown + '\n');
  }
}

main().catch(err => {
  die(`Unexpected error: ${err.message}`);
});
