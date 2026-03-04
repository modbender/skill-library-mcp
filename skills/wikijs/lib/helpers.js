import chalk from 'chalk';
import { existsSync, readFileSync, writeFileSync, mkdirSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';

// Global state
let verboseMode = false;
let debugMode = false;
let noColorMode = false;
let rateLimitMs = 0;

// ============ MODE SETTERS ============

export function setVerbose(enabled) {
  verboseMode = enabled;
}

export function setDebug(enabled) {
  debugMode = enabled;
  if (enabled) verboseMode = true;
}

export function setNoColor(enabled) {
  noColorMode = enabled;
  if (enabled) {
    chalk.level = 0;
  }
}

export function setRateLimit(ms) {
  rateLimitMs = ms;
}

// ============ LOGGING ============

export function debug(...args) {
  if (debugMode) {
    const prefix = noColorMode ? '[DEBUG]' : chalk.gray('[DEBUG]');
    console.error(prefix, ...args);
  }
}

export function verbose(...args) {
  if (verboseMode) {
    const prefix = noColorMode ? '[INFO]' : chalk.blue('[INFO]');
    console.error(prefix, ...args);
  }
}

// ============ RATE LIMITING ============

let lastRequestTime = 0;

export async function rateLimit() {
  if (rateLimitMs <= 0) return;

  const now = Date.now();
  const elapsed = now - lastRequestTime;

  if (elapsed < rateLimitMs) {
    const delay = rateLimitMs - elapsed;
    debug(`Rate limiting: waiting ${delay}ms`);
    await sleep(delay);
  }

  lastRequestTime = Date.now();
}

export function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ============ CACHING ============

const CACHE_DIR = join(homedir(), '.cache', 'wikijs-cli');
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes default

function getCachePath(key) {
  return join(CACHE_DIR, `${key}.json`);
}

export function getCached(key) {
  try {
    const cachePath = getCachePath(key);
    if (!existsSync(cachePath)) return null;

    const data = JSON.parse(readFileSync(cachePath, 'utf-8'));

    // Check TTL
    if (Date.now() - data.timestamp > (data.ttl || CACHE_TTL)) {
      debug(`Cache expired for ${key}`);
      return null;
    }

    debug(`Cache hit for ${key}`);
    return data.value;
  } catch (err) {
    debug(`Cache read error: ${err.message}`);
    return null;
  }
}

export function setCache(key, value, ttl = CACHE_TTL) {
  try {
    mkdirSync(CACHE_DIR, { recursive: true });
    const cachePath = getCachePath(key);
    const data = {
      timestamp: Date.now(),
      ttl,
      value
    };
    writeFileSync(cachePath, JSON.stringify(data));
    debug(`Cached ${key}`);
  } catch (err) {
    debug(`Cache write error: ${err.message}`);
  }
}

export async function clearCache() {
  try {
    const { rmSync } = await import('fs');
    rmSync(CACHE_DIR, { recursive: true, force: true });
    verbose('Cache cleared');
  } catch (err) {
    debug(`Cache clear error: ${err.message}`);
  }
}

// ============ PROGRESS ============

export function createProgress(total, label = 'Processing') {
  let current = 0;
  const startTime = Date.now();

  return {
    increment(amount = 1) {
      current += amount;
      this.render();
    },

    set(value) {
      current = value;
      this.render();
    },

    render() {
      if (!process.stderr.isTTY) return;

      const percent = Math.round((current / total) * 100);
      const barWidth = 30;
      const filled = Math.round((current / total) * barWidth);
      const empty = barWidth - filled;

      const bar = noColorMode
        ? `[${'='.repeat(filled)}${' '.repeat(empty)}]`
        : `[${chalk.green('█'.repeat(filled))}${chalk.gray('░'.repeat(empty))}]`;

      const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
      const status = `${bar} ${percent}% (${current}/${total}) ${elapsed}s`;

      process.stderr.write(`\r${label}: ${status}`);
    },

    done(message) {
      if (process.stderr.isTTY) {
        process.stderr.write('\r' + ' '.repeat(80) + '\r');
      }
      if (message) {
        console.log(message);
      }
    }
  };
}

// ============ TREE RENDERING ============

export function renderTree(items, options = {}) {
  const {
    getPath = item => item.path,
    getLabel = item => item.title || item.path,
    getId = item => item.id
  } = options;

  // Build tree structure
  const root = { children: {}, items: [] };

  for (const item of items) {
    const path = getPath(item);
    const parts = path.split('/').filter(Boolean);

    let current = root;
    for (let i = 0; i < parts.length; i++) {
      const part = parts[i];
      if (!current.children[part]) {
        current.children[part] = { children: {}, items: [] };
      }
      current = current.children[part];
    }
    current.items.push(item);
  }

  // Render tree
  const lines = [];

  function renderNode(node, prefix = '', isLast = true, name = '') {
    const children = Object.entries(node.children);
    const hasItems = node.items.length > 0;

    // Render directory name
    if (name) {
      const connector = isLast ? '└── ' : '├── ';
      const dirIcon = noColorMode ? '[D]' : chalk.blue('📁');
      lines.push(`${prefix}${connector}${dirIcon} ${name}/`);
    }

    const newPrefix = prefix + (name ? (isLast ? '    ' : '│   ') : '');

    // Render items (pages) in this directory
    const totalChildren = children.length + node.items.length;
    node.items.forEach((item, idx) => {
      const isLastItem = idx === node.items.length - 1 && children.length === 0;
      const connector = isLastItem ? '└── ' : '├── ';
      const pageIcon = noColorMode ? '[P]' : chalk.green('📄');
      const label = getLabel(item);
      const id = getId(item);
      const idStr = noColorMode ? `(${id})` : chalk.gray(`(${id})`);
      lines.push(`${newPrefix}${connector}${pageIcon} ${label} ${idStr}`);
    });

    // Render subdirectories
    children.forEach(([childName, childNode], idx) => {
      const isLastChild = idx === children.length - 1;
      renderNode(childNode, newPrefix, isLastChild, childName);
    });
  }

  renderNode(root);
  return lines.join('\n');
}

// ============ DIFF ============

export function diffStrings(str1, str2) {
  const lines1 = str1.split('\n');
  const lines2 = str2.split('\n');
  const result = [];

  const maxLen = Math.max(lines1.length, lines2.length);

  for (let i = 0; i < maxLen; i++) {
    const line1 = lines1[i];
    const line2 = lines2[i];

    if (line1 === undefined) {
      // Added line
      result.push({
        type: 'add',
        lineNum: i + 1,
        content: line2
      });
    } else if (line2 === undefined) {
      // Removed line
      result.push({
        type: 'remove',
        lineNum: i + 1,
        content: line1
      });
    } else if (line1 !== line2) {
      // Changed line
      result.push({
        type: 'remove',
        lineNum: i + 1,
        content: line1
      });
      result.push({
        type: 'add',
        lineNum: i + 1,
        content: line2
      });
    } else {
      // Unchanged - only show in context
      result.push({
        type: 'unchanged',
        lineNum: i + 1,
        content: line1
      });
    }
  }

  return result;
}

export function formatDiff(diff, contextLines = 3) {
  const lines = [];
  let lastPrintedLine = -contextLines - 1;

  for (let i = 0; i < diff.length; i++) {
    const item = diff[i];

    if (item.type === 'unchanged') {
      // Check if we're within context of a change
      const nearChange = diff.slice(Math.max(0, i - contextLines), i + contextLines + 1)
        .some(d => d.type !== 'unchanged');

      if (!nearChange) continue;
    }

    // Add separator if there's a gap
    if (item.lineNum > lastPrintedLine + 1 && lastPrintedLine > 0) {
      lines.push(noColorMode ? '...' : chalk.gray('...'));
    }

    const lineNum = String(item.lineNum).padStart(4);

    switch (item.type) {
      case 'add':
        lines.push(noColorMode
          ? `+ ${lineNum} | ${item.content}`
          : chalk.green(`+ ${lineNum} | ${item.content}`));
        break;
      case 'remove':
        lines.push(noColorMode
          ? `- ${lineNum} | ${item.content}`
          : chalk.red(`- ${lineNum} | ${item.content}`));
        break;
      default:
        lines.push(noColorMode
          ? `  ${lineNum} | ${item.content}`
          : chalk.gray(`  ${lineNum} | ${item.content}`));
    }

    lastPrintedLine = item.lineNum;
  }

  return lines.join('\n');
}

// ============ LINK EXTRACTION ============

export function extractLinks(markdown) {
  const links = [];

  // Markdown links: [text](url)
  const mdLinkRegex = /\[([^\]]*)\]\(([^)]+)\)/g;
  let match;
  while ((match = mdLinkRegex.exec(markdown)) !== null) {
    links.push({
      text: match[1],
      url: match[2],
      type: 'markdown'
    });
  }

  // Wiki-style links: [[page]] or [[page|text]]
  const wikiLinkRegex = /\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g;
  while ((match = wikiLinkRegex.exec(markdown)) !== null) {
    links.push({
      text: match[2] || match[1],
      url: match[1],
      type: 'wiki'
    });
  }

  return links;
}

export function isInternalLink(url) {
  // Internal links don't start with http/https/mailto/etc
  return !url.match(/^(https?:|mailto:|tel:|ftp:|#)/i);
}

// ============ MARKDOWN LINTING ============

export function lintMarkdown(content) {
  const issues = [];
  const lines = content.split('\n');

  lines.forEach((line, idx) => {
    const lineNum = idx + 1;

    // Check for trailing whitespace
    if (line.match(/\s+$/)) {
      issues.push({
        line: lineNum,
        type: 'warning',
        rule: 'no-trailing-spaces',
        message: 'Trailing whitespace'
      });
    }

    // Check for multiple consecutive blank lines
    if (idx > 0 && line === '' && lines[idx - 1] === '') {
      issues.push({
        line: lineNum,
        type: 'warning',
        rule: 'no-multiple-blanks',
        message: 'Multiple consecutive blank lines'
      });
    }

    // Check for headings without space after #
    if (line.match(/^#+[^#\s]/)) {
      issues.push({
        line: lineNum,
        type: 'error',
        rule: 'heading-space',
        message: 'Missing space after heading markers'
      });
    }

    // Check for very long lines (>120 chars, excluding links)
    if (line.length > 120 && !line.includes('http')) {
      issues.push({
        line: lineNum,
        type: 'warning',
        rule: 'line-length',
        message: `Line too long (${line.length} > 120 characters)`
      });
    }

    // Check for tabs (prefer spaces)
    if (line.includes('\t')) {
      issues.push({
        line: lineNum,
        type: 'warning',
        rule: 'no-tabs',
        message: 'Tab character found (prefer spaces)'
      });
    }

    // Check for broken link syntax
    if (line.match(/\[[^\]]*\]\([^)]*$/)) {
      issues.push({
        line: lineNum,
        type: 'error',
        rule: 'valid-link',
        message: 'Unclosed link syntax'
      });
    }
  });

  // Check document structure
  const headings = lines.filter(l => l.match(/^#{1,6}\s/));
  if (headings.length > 0 && !headings[0].match(/^#\s/)) {
    issues.push({
      line: 1,
      type: 'warning',
      rule: 'first-heading-h1',
      message: 'First heading should be H1'
    });
  }

  // Check for empty document
  const nonEmptyLines = lines.filter(l => l.trim().length > 0);
  if (nonEmptyLines.length === 0) {
    issues.push({
      line: 1,
      type: 'error',
      rule: 'no-empty',
      message: 'Document is empty'
    });
  }

  return {
    valid: issues.filter(i => i.type === 'error').length === 0,
    errors: issues.filter(i => i.type === 'error'),
    warnings: issues.filter(i => i.type === 'warning'),
    all: issues
  };
}

export function formatLintResults(results) {
  const lines = [];

  if (results.errors.length > 0) {
    lines.push(noColorMode ? 'Errors:' : chalk.red('Errors:'));
    results.errors.forEach(e => {
      lines.push(`  Line ${e.line}: ${e.message} (${e.rule})`);
    });
  }

  if (results.warnings.length > 0) {
    lines.push(noColorMode ? 'Warnings:' : chalk.yellow('Warnings:'));
    results.warnings.forEach(w => {
      lines.push(`  Line ${w.line}: ${w.message} (${w.rule})`);
    });
  }

  if (results.valid && results.warnings.length === 0) {
    lines.push(noColorMode ? 'No issues found' : chalk.green('No issues found'));
  }

  return lines.join('\n');
}

// ============ OFFLINE MODE ============

let offlineMode = false;
const OFFLINE_CACHE_FILE = join(CACHE_DIR, 'offline-data.json');

export function setOfflineMode(enabled) {
  offlineMode = enabled;
  if (enabled) {
    verbose('Offline mode enabled');
  }
}

export function isOfflineMode() {
  return offlineMode;
}

export function getOfflineData() {
  try {
    if (!existsSync(OFFLINE_CACHE_FILE)) return null;
    const data = JSON.parse(readFileSync(OFFLINE_CACHE_FILE, 'utf-8'));
    return data;
  } catch (err) {
    debug(`Failed to read offline data: ${err.message}`);
    return null;
  }
}

export function saveOfflineData(data) {
  try {
    mkdirSync(CACHE_DIR, { recursive: true });
    const offlineData = {
      timestamp: Date.now(),
      pages: data.pages || [],
      tags: data.tags || []
    };
    writeFileSync(OFFLINE_CACHE_FILE, JSON.stringify(offlineData, null, 2));
    debug('Offline data saved');
  } catch (err) {
    debug(`Failed to save offline data: ${err.message}`);
  }
}

export default {
  setVerbose,
  setDebug,
  setNoColor,
  setRateLimit,
  debug,
  verbose,
  rateLimit,
  sleep,
  getCached,
  setCache,
  clearCache,
  createProgress,
  renderTree,
  diffStrings,
  formatDiff,
  extractLinks,
  isInternalLink,
  lintMarkdown,
  formatLintResults,
  setOfflineMode,
  isOfflineMode,
  getOfflineData,
  saveOfflineData
};
