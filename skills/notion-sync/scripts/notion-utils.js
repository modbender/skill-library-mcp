/**
 * Shared utilities for Notion API scripts
 * Common functions for HTTP requests, error handling, and data extraction
 */

const https = require('https');
const fs = require('fs');
const os = require('os');
const path = require('path');

const NOTION_VERSION = '2025-09-03';

// Cached token (resolved once per process)
let _cachedToken = undefined;

/**
 * Resolve the Notion API token from multiple sources (in priority order):
 *
 * 1. --token-file <path>    Read from a file (recommended for automation)
 * 2. --token-stdin           Read from stdin (recommended for pipes)
 * 3. ~/.notion-token         Auto-detected default token file
 * 4. NOTION_API_KEY env var  Environment variable fallback
 *
 * Credentials are never accepted as bare command-line arguments to avoid
 * exposure in process listings and shell history.
 */
function resolveToken() {
  if (_cachedToken !== undefined) return _cachedToken;

  const args = process.argv;

  for (let i = 2; i < args.length; i++) {
    // --token-file <path>
    if (args[i] === '--token-file' && args[i + 1]) {
      try {
        const tokenPath = expandHomePath(args[i + 1]);
        _cachedToken = fs.readFileSync(tokenPath, 'utf8').trim();
        return _cachedToken;
      } catch (err) {
        console.error(`Error reading token file "${args[i + 1]}": ${err.message}`);
        process.exit(1);
      }
    }
    // --token-stdin
    if (args[i] === '--token-stdin') {
      try {
        _cachedToken = fs.readFileSync(0, 'utf8').trim(); // fd 0 = stdin
        return _cachedToken;
      } catch (err) {
        console.error(`Error reading token from stdin: ${err.message}`);
        process.exit(1);
      }
    }
  }

  // Auto-check default token file
  const defaultTokenPath = path.join(os.homedir(), '.notion-token');
  if (fs.existsSync(defaultTokenPath)) {
    try {
      _cachedToken = fs.readFileSync(defaultTokenPath, 'utf8').trim();
      return _cachedToken;
    } catch (err) {
      console.error(`Error reading default token file "${defaultTokenPath}": ${err.message}`);
      process.exit(1);
    }
  }

  // Env var fallback
  if (process.env.NOTION_API_KEY) {
    _cachedToken = process.env.NOTION_API_KEY;
    return _cachedToken;
  }

  _cachedToken = null;
  return null;
}

/**
 * Expand a path that starts with ~ to the user's home directory
 */
function expandHomePath(inputPath) {
  if (!inputPath) return inputPath;
  if (inputPath === '~') return os.homedir();
  if (inputPath.startsWith('~/')) return path.join(os.homedir(), inputPath.slice(2));
  return inputPath;
}

/**
 * Normalize network-level request errors into user-friendly guidance
 */
function wrapNetworkError(err) {
  const networkCodes = new Set(['ENOTFOUND', 'ECONNREFUSED', 'ETIMEDOUT', 'ECONNRESET', 'EAI_AGAIN']);
  if (networkCodes.has(err.code)) {
    return new Error('Could not reach Notion API. Check your internet connection.');
  }
  return new Error(`Could not reach Notion API. ${err.message}`);
}

/**
 * Get the Notion API key (resolves from all supported sources)
 */
function getApiKey() {
  return resolveToken();
}

/**
 * Check if a Notion API token was provided, exit with helpful message if not
 */
function checkApiKey() {
  if (!getApiKey()) {
    const message = 'No Notion API token found. Provide one via: --token-file <path>, --token-stdin (pipe), or NOTION_API_KEY env var.';
    if (hasJsonFlag()) {
      console.log(JSON.stringify({ error: message }, null, 2));
    } else {
      console.error('Error: No Notion API token provided');
      console.error('');
      console.error(message);
      console.error('');
      console.error('Usage (pick one):');
      console.error('  node scripts/<script>.js --token-file ~/.notion-token [args]');
      console.error('  echo "$NOTION_API_KEY" | node scripts/<script>.js --token-stdin [args]');
      console.error('  NOTION_API_KEY=ntn_... node scripts/<script>.js [args]');
      console.error('');
      console.error('Default: if ~/.notion-token exists, it is used automatically.');
      console.error('');
      console.error('Credentials are never passed as bare CLI arguments (security best practice).');
      console.error('Create an integration at https://www.notion.so/my-integrations');
    }
    process.exit(1);
  }
}

/**
 * Strip token-related flags from an args array so scripts don't parse them as their own args
 */
function hasJsonFlag() {
  return process.argv.includes('--json');
}

function log(msg) {
  if (!hasJsonFlag()) console.error(msg);
}

function stripTokenArg(args) {
  const result = [];
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--token-file' && i + 1 < args.length) {
      i++; // skip value
    } else if (args[i] === '--token-stdin') {
      // skip flag only (no value)
    } else if (args[i] === '--json') {
      // skip flag only (no value)
    } else {
      result.push(args[i]);
    }
  }
  return result;
}

/**
 * Make a Notion API request with proper error handling
 */
function notionRequest(path, method, data = null) {
  const apiKey = getApiKey();
  if (!apiKey) {
    return Promise.reject(new Error('No Notion API token found. Provide one via: --token-file <path>, --token-stdin (pipe), or NOTION_API_KEY env var.'));
  }

  return new Promise((resolve, reject) => {
    const requestData = data ? JSON.stringify(data) : null;

    const options = {
      hostname: 'api.notion.com',
      port: 443,
      path: path,
      method: method,
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Notion-Version': NOTION_VERSION,
        'Content-Type': 'application/json'
      }
    };

    if (requestData) {
      options.headers['Content-Length'] = Buffer.byteLength(requestData);
    }

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => body += chunk);
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          try {
            resolve(JSON.parse(body));
          } catch (e) {
            resolve(body);
          }
        } else {
          reject(createDetailedError(res.statusCode, body));
        }
      });
    });

    req.on('error', (err) => {
      reject(wrapNetworkError(err));
    });
    if (requestData) {
      req.write(requestData);
    }
    req.end();
  });
}

/**
 * Create detailed error message based on status code and response
 */
function createDetailedError(statusCode, body) {
  let error;
  try {
    error = JSON.parse(body);
  } catch (e) {
    return new Error(`API error (${statusCode}): ${body}`);
  }

  const errorCode = error.code;
  const errorMessage = error.message;

  switch (statusCode) {
    case 400:
      if (errorCode === 'validation_error') {
        return new Error(`Validation error: ${errorMessage}. Check your input data.`);
      }
      return new Error(`Bad request: ${errorMessage}`);

    case 401:
      return new Error('Authentication failed. Check that your token is valid and has access to this resource.');

    case 404:
      if (errorCode === 'object_not_found') {
        return new Error('Page/database not found. Verify the ID and that your integration has access.');
      }
      return new Error(`Not found: ${errorMessage}`);

    case 429:
      return new Error('Rate limit exceeded. Wait a moment and try again.');

    case 500:
    case 503:
      return new Error(`Notion server error (${statusCode}). Try again later.`);

    default:
      return new Error(`API error (${statusCode}): ${errorMessage || body}`);
  }
}

// --- ID Utilities ---

/**
 * Normalize a Notion page/block ID to UUID format with hyphens
 */
function normalizeId(id) {
  const clean = id.replace(/-/g, '');
  if (clean.length === 32) {
    return `${clean.slice(0, 8)}-${clean.slice(8, 12)}-${clean.slice(12, 16)}-${clean.slice(16, 20)}-${clean.slice(20)}`;
  }
  return id;
}

// --- Property Utilities ---

/**
 * Extract title from a page or database object
 */
function extractTitle(item) {
  if (item.object === 'page') {
    const titleProp = Object.values(item.properties || {}).find(p => p.type === 'title');
    if (titleProp && titleProp.title && titleProp.title.length > 0) {
      return titleProp.title.map(t => t.plain_text).join('');
    }
  } else if (item.object === 'database' || item.object === 'data_source') {
    if (item.title && item.title.length > 0) {
      return item.title.map(t => t.plain_text).join('');
    }
  }
  return '(Untitled)';
}

/**
 * Extract value from a property based on its type
 */
function extractPropertyValue(property) {
  switch (property.type) {
    case 'title':
      return property.title.map(t => t.plain_text).join('');
    case 'rich_text':
      return property.rich_text.map(t => t.plain_text).join('');
    case 'number':
      return property.number;
    case 'select':
      return property.select?.name || null;
    case 'multi_select':
      return property.multi_select.map(s => s.name);
    case 'date':
      return property.date ? { start: property.date.start, end: property.date.end } : null;
    case 'checkbox':
      return property.checkbox;
    case 'url':
      return property.url;
    case 'email':
      return property.email;
    case 'phone_number':
      return property.phone_number;
    case 'relation':
      return property.relation.map(r => r.id);
    case 'created_time':
      return property.created_time;
    case 'last_edited_time':
      return property.last_edited_time;
    default:
      return property[property.type];
  }
}

/**
 * Format property value for Notion API write operations
 */
function formatPropertyValue(propertyType, value) {
  switch (propertyType) {
    case 'select':
      return { select: { name: value } };

    case 'multi_select': {
      const tags = Array.isArray(value) ? value : value.split(',').map(t => t.trim());
      return { multi_select: tags.map(name => ({ name })) };
    }

    case 'checkbox': {
      const boolValue = typeof value === 'boolean' ? value :
        (String(value).toLowerCase() === 'true' || value === '1');
      return { checkbox: boolValue };
    }

    case 'number':
      return { number: typeof value === 'number' ? value : parseFloat(value) };

    case 'url':
      return { url: value };

    case 'email':
      return { email: value };

    case 'date': {
      if (typeof value === 'string') {
        const dates = value.split(',').map(d => d.trim());
        return { date: { start: dates[0], end: dates[1] || null } };
      }
      return { date: value };
    }

    case 'rich_text':
      return { rich_text: [{ type: 'text', text: { content: value } }] };

    case 'title':
      return { title: [{ type: 'text', text: { content: value } }] };

    default:
      throw new Error(`Unsupported property type: ${propertyType}. Supported: select, multi_select, checkbox, number, url, email, date, rich_text, title`);
  }
}

// --- Rich Text Utilities ---

/**
 * Parse plain text into Notion rich_text array, handling the 2000-char limit
 */
function parseRichText(text) {
  const maxLength = 2000;
  const richText = [];

  for (let i = 0; i < text.length; i += maxLength) {
    richText.push({
      type: 'text',
      text: { content: text.substring(i, i + maxLength) }
    });
  }

  return richText.length > 0 ? richText : [{ type: 'text', text: { content: '' } }];
}

/**
 * Parse markdown-formatted text into Notion rich_text with annotations
 */
function pushRichTextChunked(richText, item, maxLength = 2000) {
  const content = item?.text?.content || '';

  if (content.length === 0) {
    richText.push(item);
    return;
  }

  for (let i = 0; i < content.length; i += maxLength) {
    richText.push({
      ...item,
      text: {
        ...item.text,
        content: content.substring(i, i + maxLength)
      }
    });
  }
}

function parseMarkdownRichText(text) {
  const richText = [];
  const parts = text.split(/(\*\*.*?\*\*|\*.*?\*|\[.*?\]\(.*?\))/);

  for (const part of parts) {
    if (!part) continue;

    if (part.startsWith('**') && part.endsWith('**')) {
      pushRichTextChunked(richText, {
        type: 'text',
        text: { content: part.slice(2, -2) },
        annotations: { bold: true }
      });
    } else if (part.startsWith('*') && part.endsWith('*') && !part.startsWith('**')) {
      pushRichTextChunked(richText, {
        type: 'text',
        text: { content: part.slice(1, -1) },
        annotations: { italic: true }
      });
    } else {
      const linkMatch = part.match(/\[(.*?)\]\((.*?)\)/);
      if (linkMatch) {
        pushRichTextChunked(richText, {
          type: 'text',
          text: { content: linkMatch[1], link: { url: linkMatch[2] } }
        });
      } else {
        pushRichTextChunked(richText, {
          type: 'text',
          text: { content: part }
        });
      }
    }
  }

  return richText.length > 0 ? richText : [{ type: 'text', text: { content: text } }];
}

// --- Markdown Parsing ---

/**
 * Parse markdown string into Notion block array
 * @param {string} markdown - Markdown content
 * @param {object} options - { richText: 'plain' | 'markdown' }
 */
function parseMarkdownToBlocks(markdown, options = {}) {
  const useMarkdownRichText = options.richText === 'markdown';
  const toRichText = useMarkdownRichText ? parseMarkdownRichText : parseRichText;

  const lines = markdown.split('\n');
  const blocks = [];
  let currentParagraph = [];
  let inCodeBlock = false;
  let codeLanguage = '';
  let codeContent = [];

  const flushParagraph = () => {
    if (currentParagraph.length > 0) {
      const text = currentParagraph.join('\n').trim();
      if (text) {
        blocks.push({
          type: 'paragraph',
          paragraph: { rich_text: toRichText(text) }
        });
      }
      currentParagraph = [];
    }
  };

  for (const line of lines) {
    // Code blocks
    if (line.startsWith('```')) {
      if (!inCodeBlock) {
        flushParagraph();
        inCodeBlock = true;
        codeLanguage = line.slice(3).trim() || 'plain text';
        codeContent = [];
      } else {
        blocks.push({
          type: 'code',
          code: {
            language: codeLanguage,
            rich_text: [{ type: 'text', text: { content: codeContent.join('\n') } }]
          }
        });
        inCodeBlock = false;
        codeLanguage = '';
        codeContent = [];
      }
      continue;
    }

    if (inCodeBlock) {
      codeContent.push(line);
      continue;
    }

    // Headings (check ### before ## before #)
    const headingMatch = line.match(/^(#{1,3})\s+(.*)/);
    if (headingMatch) {
      flushParagraph();
      const level = headingMatch[1].length;
      const text = headingMatch[2].trim();
      const type = `heading_${level}`;
      blocks.push({ type, [type]: { rich_text: toRichText(text) } });
      continue;
    }

    // Horizontal rules
    if (/^---+$/.test(line)) {
      flushParagraph();
      blocks.push({ type: 'divider', divider: {} });
      continue;
    }

    // Bullet lists
    if (/^[-*]\s+/.test(line)) {
      flushParagraph();
      const text = line.replace(/^[-*]\s+/, '').trim();
      blocks.push({
        type: 'bulleted_list_item',
        bulleted_list_item: { rich_text: toRichText(text) }
      });
      continue;
    }

    // Empty lines
    if (line.trim() === '') {
      flushParagraph();
      continue;
    }

    currentParagraph.push(line);
  }

  flushParagraph();
  return blocks;
}

// --- Block to Markdown ---

/**
 * Extract plain text from rich_text array
 */
function richTextToPlain(richText) {
  if (!richText || richText.length === 0) return '';
  return richText.map(rt => rt.plain_text || '').join('');
}

/**
 * Extract markdown-formatted text from rich_text array
 */
function richTextToMarkdown(richText) {
  if (!richText || richText.length === 0) return '';

  return richText.map(rt => {
    let text = rt.plain_text || '';
    const ann = rt.annotations || {};

    if (ann.code) text = `\`${text}\``;
    if (ann.bold) text = `**${text}**`;
    if (ann.italic) text = `*${text}*`;
    if (ann.strikethrough) text = `~~${text}~~`;

    if (rt.href) {
      text = `[${text}](${rt.href})`;
    } else if (rt.text && rt.text.link) {
      text = `[${text}](${rt.text.link.url})`;
    }

    return text;
  }).join('');
}

/**
 * Convert Notion blocks to markdown string
 */
function blocksToMarkdown(blocks) {
  const lines = [];

  for (const block of blocks) {
    const type = block.type;
    const content = block[type];

    switch (type) {
      case 'heading_1':
        lines.push(`# ${richTextToMarkdown(content.rich_text)}`, '');
        break;
      case 'heading_2':
        lines.push(`## ${richTextToMarkdown(content.rich_text)}`, '');
        break;
      case 'heading_3':
        lines.push(`### ${richTextToMarkdown(content.rich_text)}`, '');
        break;
      case 'paragraph': {
        const text = richTextToMarkdown(content.rich_text);
        if (text.trim()) lines.push(text, '');
        break;
      }
      case 'bulleted_list_item':
        lines.push(`- ${richTextToMarkdown(content.rich_text)}`);
        break;
      case 'numbered_list_item':
        lines.push(`1. ${richTextToMarkdown(content.rich_text)}`);
        break;
      case 'code': {
        const code = richTextToPlain(content.rich_text);
        const lang = content.language || 'plain text';
        lines.push(`\`\`\`${lang}`, code, '```', '');
        break;
      }
      case 'divider':
        lines.push('---', '');
        break;
      case 'quote':
        lines.push(`> ${richTextToMarkdown(content.rich_text)}`, '');
        break;
      case 'callout': {
        const emoji = content.icon?.emoji || '📌';
        lines.push(`${emoji} ${richTextToMarkdown(content.rich_text)}`, '');
        break;
      }
      default:
        break;
    }
  }

  return lines.join('\n');
}

// --- Notion Page Helpers ---

/**
 * Fetch all blocks from a page/block, handling pagination
 */
async function getAllBlocks(blockId) {
  const normalizedId = normalizeId(blockId);
  let allBlocks = [];
  let cursor = null;

  do {
    const encodedId = encodeURIComponent(normalizedId);
    const path = `/v1/blocks/${encodedId}/children${cursor ? `?start_cursor=${encodeURIComponent(cursor)}` : ''}`;
    const response = await notionRequest(path, 'GET');
    allBlocks = allBlocks.concat(response.results);
    cursor = response.has_more ? response.next_cursor : null;
  } while (cursor);

  return allBlocks;
}

/**
 * Append blocks to a page in batches with rate limiting
 */
async function appendBlocksBatched(pageId, blocks, batchSize = 100, delayMs = 350) {
  for (let i = 0; i < blocks.length; i += batchSize) {
    const batch = blocks.slice(i, i + batchSize);
    await notionRequest(`/v1/blocks/${pageId}/children`, 'PATCH', { children: batch });

    if (i + batchSize < blocks.length) {
      await new Promise(resolve => setTimeout(resolve, delayMs));
    }
  }
}

module.exports = {
  // Config
  NOTION_VERSION,
  getApiKey,
  resolveToken,
  checkApiKey,
  stripTokenArg,
  hasJsonFlag,
  log,
  expandHomePath,
  wrapNetworkError,

  // HTTP
  notionRequest,
  createDetailedError,

  // IDs
  normalizeId,

  // Properties
  extractTitle,
  extractPropertyValue,
  formatPropertyValue,

  // Rich text
  parseRichText,
  parseMarkdownRichText,
  richTextToPlain,
  richTextToMarkdown,

  // Markdown conversion
  parseMarkdownToBlocks,
  blocksToMarkdown,

  // Page helpers
  getAllBlocks,
  appendBlocksBatched,

  // Testing
  _resetTokenCache: () => { _cachedToken = undefined; },
};
