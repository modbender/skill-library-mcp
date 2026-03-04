#!/usr/bin/env node
/**
 * Test suite for notion-sync utilities
 * Covers: normalizeId, parseRichText, parseMarkdownRichText, parseMarkdownToBlocks,
 *         blocksToMarkdown, formatPropertyValue, extractPropertyValue, extractTitle,
 *         richTextToMarkdown, richTextToPlain, createDetailedError
 *
 * Run: node scripts/test-normalize.js
 */

const fs = require('fs');
const os = require('os');
const path = require('path');
const {
  normalizeId,
  parseRichText,
  parseMarkdownRichText,
  parseMarkdownToBlocks,
  blocksToMarkdown,
  formatPropertyValue,
  extractPropertyValue,
  extractTitle,
  richTextToMarkdown,
  richTextToPlain,
  createDetailedError,
  stripTokenArg,
  hasJsonFlag,
  log,
  expandHomePath,
  resolveToken,
  _resetTokenCache,
  wrapNetworkError,
} = require('./notion-utils.js');
const { parseWatchArgs } = require('./watch-notion.js');
const { parseBatchUpdateArgs, DEFAULT_LIMIT } = require('./batch-update.js');

let passed = 0;
let failed = 0;

function assert(condition, description) {
  if (condition) {
    console.log(`  ✓ ${description}`);
    passed++;
  } else {
    console.log(`  ✗ ${description}`);
    failed++;
  }
}

function assertEqual(actual, expected, description) {
  const a = typeof actual === 'object' ? JSON.stringify(actual) : String(actual);
  const e = typeof expected === 'object' ? JSON.stringify(expected) : String(expected);
  if (a === e) {
    console.log(`  ✓ ${description}`);
    passed++;
  } else {
    console.log(`  ✗ ${description}`);
    console.log(`    Expected: ${e}`);
    console.log(`    Actual:   ${a}`);
    failed++;
  }
}

// --- normalizeId ---
console.log('\n📋 normalizeId');

assertEqual(
  normalizeId('abc12345-6789-0123-4567-890abcdef012'),
  'abc12345-6789-0123-4567-890abcdef012',
  'UUID with hyphens passes through'
);

assertEqual(
  normalizeId('abc12345678901234567890abcdef012'),
  'abc12345-6789-0123-4567-890abcdef012',
  'Compact 32-char format gets hyphens'
);

assertEqual(
  normalizeId('12a85c781e0b481a98d5e122e8e9c5f3'),
  '12a85c78-1e0b-481a-98d5-e122e8e9c5f3',
  'Real Notion UUID without hyphens'
);

assertEqual(
  normalizeId('tooshort'),
  'tooshort',
  'Invalid length returns as-is'
);

assertEqual(
  normalizeId('ABC12345678901234567890ABCDEF012'),
  'ABC12345-6789-0123-4567-890ABCDEF012',
  'Preserves case'
);

// --- parseRichText ---
console.log('\n📋 parseRichText (plain text → Notion rich_text)');

{
  const result = parseRichText('Hello world');
  assertEqual(result.length, 1, 'Short text: single chunk');
  assertEqual(result[0].text.content, 'Hello world', 'Short text: content preserved');
}

{
  const result = parseRichText('');
  assertEqual(result.length, 1, 'Empty text: returns one item');
  assertEqual(result[0].text.content, '', 'Empty text: empty content');
}

{
  const longText = 'x'.repeat(5000);
  const result = parseRichText(longText);
  assertEqual(result.length, 3, 'Long text (5000 chars): split into 3 chunks');
  assertEqual(result[0].text.content.length, 2000, 'First chunk: 2000 chars');
  assertEqual(result[1].text.content.length, 2000, 'Second chunk: 2000 chars');
  assertEqual(result[2].text.content.length, 1000, 'Third chunk: 1000 chars');
}

{
  const exact = 'x'.repeat(2000);
  const result = parseRichText(exact);
  assertEqual(result.length, 1, 'Exactly 2000 chars: single chunk');
}

// --- parseMarkdownRichText ---
console.log('\n📋 parseMarkdownRichText (markdown → Notion rich_text)');

{
  const result = parseMarkdownRichText('**bold text**');
  assertEqual(result.length, 1, 'Bold: single item');
  assertEqual(result[0].text.content, 'bold text', 'Bold: content extracted');
  assertEqual(result[0].annotations.bold, true, 'Bold: annotation set');
}

{
  const result = parseMarkdownRichText('*italic text*');
  assertEqual(result.length, 1, 'Italic: single item');
  assertEqual(result[0].text.content, 'italic text', 'Italic: content extracted');
  assertEqual(result[0].annotations.italic, true, 'Italic: annotation set');
}

{
  const result = parseMarkdownRichText('[Google](https://google.com)');
  assertEqual(result.length, 1, 'Link: single item');
  assertEqual(result[0].text.content, 'Google', 'Link: text extracted');
  assertEqual(result[0].text.link.url, 'https://google.com', 'Link: URL extracted');
}

{
  const result = parseMarkdownRichText('Hello **bold** world');
  assertEqual(result.length, 3, 'Mixed: 3 parts');
  assertEqual(result[0].text.content, 'Hello ', 'Mixed: prefix');
  assertEqual(result[1].annotations.bold, true, 'Mixed: bold middle');
  assertEqual(result[2].text.content, ' world', 'Mixed: suffix');
}

{
  const result = parseMarkdownRichText('plain text');
  assertEqual(result.length, 1, 'Plain: single item');
  assertEqual(result[0].text.content, 'plain text', 'Plain: content preserved');
  assert(!result[0].annotations, 'Plain: no annotations');
}

{
  const longText = 'x'.repeat(5000);
  const result = parseMarkdownRichText(longText);
  assertEqual(result.length, 3, 'Long plain markdown text: split into 3 chunks');
  assertEqual(result[0].text.content.length, 2000, 'Long plain: first chunk 2000 chars');
  assertEqual(result[1].text.content.length, 2000, 'Long plain: second chunk 2000 chars');
  assertEqual(result[2].text.content.length, 1000, 'Long plain: third chunk 1000 chars');
}

{
  const longBoldContent = 'b'.repeat(4500);
  const result = parseMarkdownRichText(`**${longBoldContent}**`);
  assertEqual(result.length, 3, 'Long bold markdown text: split into 3 chunks');
  assertEqual(result.every(item => item.annotations && item.annotations.bold), true, 'Long bold: bold annotation preserved across chunks');
  assertEqual(result.map(item => item.text.content).join(''), longBoldContent, 'Long bold: content preserved across chunks');
}

{
  const longLinkText = 'l'.repeat(4200);
  const result = parseMarkdownRichText(`[${longLinkText}](https://example.com)`);
  assertEqual(result.length, 3, 'Long link markdown text: split into 3 chunks');
  assertEqual(result.every(item => item.text.link && item.text.link.url === 'https://example.com'), true, 'Long link: URL preserved across chunks');
  assertEqual(result.map(item => item.text.content).join(''), longLinkText, 'Long link: content preserved across chunks');
}

// --- parseMarkdownToBlocks ---
console.log('\n📋 parseMarkdownToBlocks');

{
  const blocks = parseMarkdownToBlocks('# Heading 1');
  assertEqual(blocks.length, 1, 'H1: one block');
  assertEqual(blocks[0].type, 'heading_1', 'H1: correct type');
}

{
  const blocks = parseMarkdownToBlocks('## Heading 2');
  assertEqual(blocks.length, 1, 'H2: one block');
  assertEqual(blocks[0].type, 'heading_2', 'H2: correct type');
}

{
  const blocks = parseMarkdownToBlocks('### Heading 3');
  assertEqual(blocks.length, 1, 'H3: one block');
  assertEqual(blocks[0].type, 'heading_3', 'H3: correct type');
}

{
  const blocks = parseMarkdownToBlocks('---');
  assertEqual(blocks.length, 1, 'Divider: one block');
  assertEqual(blocks[0].type, 'divider', 'Divider: correct type');
}

{
  const blocks = parseMarkdownToBlocks('- Item 1\n- Item 2');
  assertEqual(blocks.length, 2, 'Bullet list: two blocks');
  assertEqual(blocks[0].type, 'bulleted_list_item', 'Bullet: correct type');
}

{
  const blocks = parseMarkdownToBlocks('```javascript\nconst x = 1;\n```');
  assertEqual(blocks.length, 1, 'Code block: one block');
  assertEqual(blocks[0].type, 'code', 'Code: correct type');
  assertEqual(blocks[0].code.language, 'javascript', 'Code: language preserved');
  assertEqual(blocks[0].code.rich_text[0].text.content, 'const x = 1;', 'Code: content preserved');
}

{
  const blocks = parseMarkdownToBlocks('```\nplain code\n```');
  assertEqual(blocks[0].code.language, 'plain text', 'Code no lang: defaults to plain text');
}

{
  const md = '# Title\n\nSome paragraph text.\n\n- Item 1\n- Item 2\n\n---\n\n## Section\n\n```js\ncode\n```';
  const blocks = parseMarkdownToBlocks(md);
  assertEqual(blocks.length, 7, 'Complex doc: 7 blocks (h1, para, 2 bullets, divider, h2, code)');
}

{
  const blocks = parseMarkdownToBlocks('');
  assertEqual(blocks.length, 0, 'Empty markdown: no blocks');
}

{
  const blocks = parseMarkdownToBlocks('Line 1\nLine 2\n\nLine 3');
  assertEqual(blocks.length, 2, 'Paragraph grouping: adjacent lines merge');
}

// --- blocksToMarkdown ---
console.log('\n📋 blocksToMarkdown');

{
  const blocks = [
    { type: 'heading_1', heading_1: { rich_text: [{ plain_text: 'Title' }] } },
    { type: 'paragraph', paragraph: { rich_text: [{ plain_text: 'Hello' }] } },
    { type: 'bulleted_list_item', bulleted_list_item: { rich_text: [{ plain_text: 'Item' }] } },
    { type: 'divider', divider: {} },
    { type: 'code', code: { language: 'js', rich_text: [{ plain_text: 'const x = 1' }] } },
  ];
  const md = blocksToMarkdown(blocks);
  assert(md.includes('# Title'), 'H1 rendered');
  assert(md.includes('Hello'), 'Paragraph rendered');
  assert(md.includes('- Item'), 'Bullet rendered');
  assert(md.includes('---'), 'Divider rendered');
  assert(md.includes('```js'), 'Code block rendered');
}

{
  const blocks = [
    { type: 'quote', quote: { rich_text: [{ plain_text: 'Wisdom' }] } },
    { type: 'callout', callout: { icon: { emoji: '💡' }, rich_text: [{ plain_text: 'Note' }] } },
  ];
  const md = blocksToMarkdown(blocks);
  assert(md.includes('> Wisdom'), 'Quote rendered');
  assert(md.includes('💡 Note'), 'Callout rendered');
}

{
  const blocks = [{ type: 'unsupported_type', unsupported_type: {} }];
  const md = blocksToMarkdown(blocks);
  assertEqual(md.trim(), '', 'Unknown block types: silently skipped');
}

// --- richTextToMarkdown ---
console.log('\n📋 richTextToMarkdown');

{
  const rt = [
    { plain_text: 'bold', annotations: { bold: true } },
    { plain_text: ' and ', annotations: {} },
    { plain_text: 'italic', annotations: { italic: true } },
  ];
  const md = richTextToMarkdown(rt);
  assertEqual(md, '**bold** and *italic*', 'Bold + italic annotations');
}

{
  const rt = [{ plain_text: 'code', annotations: { code: true } }];
  assertEqual(richTextToMarkdown(rt), '`code`', 'Code annotation');
}

{
  const rt = [{ plain_text: 'struck', annotations: { strikethrough: true } }];
  assertEqual(richTextToMarkdown(rt), '~~struck~~', 'Strikethrough annotation');
}

{
  const rt = [{ plain_text: 'Link', href: 'https://example.com', annotations: {} }];
  assertEqual(richTextToMarkdown(rt), '[Link](https://example.com)', 'Link via href');
}

{
  assertEqual(richTextToMarkdown([]), '', 'Empty array');
  assertEqual(richTextToMarkdown(null), '', 'Null input');
}

// --- richTextToPlain ---
console.log('\n📋 richTextToPlain');

{
  const rt = [{ plain_text: 'Hello ' }, { plain_text: 'world' }];
  assertEqual(richTextToPlain(rt), 'Hello world', 'Concatenates plain_text');
}

assertEqual(richTextToPlain([]), '', 'Empty array');
assertEqual(richTextToPlain(null), '', 'Null input');

// --- formatPropertyValue ---
console.log('\n📋 formatPropertyValue');

assertEqual(
  formatPropertyValue('select', 'Done'),
  { select: { name: 'Done' } },
  'Select formatting'
);

assertEqual(
  formatPropertyValue('multi_select', 'AI,ML,Research'),
  { multi_select: [{ name: 'AI' }, { name: 'ML' }, { name: 'Research' }] },
  'Multi-select from comma string'
);

assertEqual(
  formatPropertyValue('multi_select', ['Tag1', 'Tag2']),
  { multi_select: [{ name: 'Tag1' }, { name: 'Tag2' }] },
  'Multi-select from array'
);

assertEqual(
  formatPropertyValue('checkbox', 'true'),
  { checkbox: true },
  'Checkbox string true'
);

assertEqual(
  formatPropertyValue('checkbox', 'false'),
  { checkbox: false },
  'Checkbox string false'
);

assertEqual(
  formatPropertyValue('checkbox', true),
  { checkbox: true },
  'Checkbox boolean true'
);

assertEqual(
  formatPropertyValue('number', '42.5'),
  { number: 42.5 },
  'Number from string'
);

assertEqual(
  formatPropertyValue('number', 99),
  { number: 99 },
  'Number from number'
);

assertEqual(
  formatPropertyValue('url', 'https://example.com'),
  { url: 'https://example.com' },
  'URL formatting'
);

assertEqual(
  formatPropertyValue('email', 'test@example.com'),
  { email: 'test@example.com' },
  'Email formatting'
);

assertEqual(
  formatPropertyValue('date', '2024-01-15'),
  { date: { start: '2024-01-15', end: null } },
  'Date single'
);

assertEqual(
  formatPropertyValue('date', '2024-01-15,2024-01-20'),
  { date: { start: '2024-01-15', end: '2024-01-20' } },
  'Date range'
);

assertEqual(
  formatPropertyValue('rich_text', 'Hello'),
  { rich_text: [{ type: 'text', text: { content: 'Hello' } }] },
  'Rich text formatting'
);

assertEqual(
  formatPropertyValue('title', 'My Title'),
  { title: [{ type: 'text', text: { content: 'My Title' } }] },
  'Title formatting'
);

{
  let threw = false;
  try { formatPropertyValue('invalid_type', 'val'); } catch (e) { threw = true; }
  assert(threw, 'Unsupported type throws error');
}

// --- extractPropertyValue ---
console.log('\n📋 extractPropertyValue');

assertEqual(
  extractPropertyValue({ type: 'title', title: [{ plain_text: 'Test' }] }),
  'Test',
  'Title extraction'
);

assertEqual(
  extractPropertyValue({ type: 'rich_text', rich_text: [{ plain_text: 'Hello ' }, { plain_text: 'world' }] }),
  'Hello world',
  'Rich text extraction (concatenated)'
);

assertEqual(
  extractPropertyValue({ type: 'select', select: { name: 'Done' } }),
  'Done',
  'Select extraction'
);

assertEqual(
  extractPropertyValue({ type: 'select', select: null }),
  null,
  'Select null extraction'
);

assertEqual(
  extractPropertyValue({ type: 'multi_select', multi_select: [{ name: 'A' }, { name: 'B' }] }),
  ['A', 'B'],
  'Multi-select extraction'
);

assertEqual(
  extractPropertyValue({ type: 'checkbox', checkbox: true }),
  true,
  'Checkbox extraction'
);

assertEqual(
  extractPropertyValue({ type: 'number', number: 42 }),
  42,
  'Number extraction'
);

assertEqual(
  extractPropertyValue({ type: 'url', url: 'https://example.com' }),
  'https://example.com',
  'URL extraction'
);

assertEqual(
  extractPropertyValue({ type: 'date', date: { start: '2024-01-15', end: null } }),
  { start: '2024-01-15', end: null },
  'Date extraction'
);

assertEqual(
  extractPropertyValue({ type: 'date', date: null }),
  null,
  'Date null extraction'
);

// --- extractTitle ---
console.log('\n📋 extractTitle');

assertEqual(
  extractTitle({ object: 'page', properties: { Name: { type: 'title', title: [{ plain_text: 'My Page' }] } } }),
  'My Page',
  'Page title extraction'
);

assertEqual(
  extractTitle({ object: 'database', title: [{ plain_text: 'My DB' }] }),
  'My DB',
  'Database title extraction'
);

assertEqual(
  extractTitle({ object: 'page', properties: {} }),
  '(Untitled)',
  'Missing title returns (Untitled)'
);

assertEqual(
  extractTitle({ object: 'page', properties: { Name: { type: 'title', title: [{ plain_text: 'Part 1' }, { plain_text: ' Part 2' }] } } }),
  'Part 1 Part 2',
  'Multi-part title concatenated'
);

// --- createDetailedError ---
console.log('\n📋 createDetailedError');

{
  const err = createDetailedError(401, '{}');
  assert(err.message.includes('Authentication') || err.message.includes('--token'), '401: authentication error');
}

{
  const err = createDetailedError(404, JSON.stringify({ code: 'object_not_found', message: 'Not found' }));
  assert(err.message.includes('not found'), '404 object_not_found');
}

{
  const err = createDetailedError(429, '{}');
  assert(err.message.includes('Rate limit'), '429: rate limit');
}

{
  const err = createDetailedError(400, JSON.stringify({ code: 'validation_error', message: 'Bad input' }));
  assert(err.message.includes('Validation'), '400 validation error');
}

{
  const err = createDetailedError(500, '{}');
  assert(err.message.includes('server error'), '500: server error');
}

{
  const err = createDetailedError(418, 'not json');
  assert(err.message.includes('418'), 'Non-JSON body handled');
}

// --- hasJsonFlag ---
console.log('\n📋 hasJsonFlag');

{
  const originalArgv = process.argv.slice();
  process.argv = ['node', 'script.js', '--json'];
  assertEqual(hasJsonFlag(), true, 'Returns true when --json is present');
  process.argv = ['node', 'script.js', '--limit', '5'];
  assertEqual(hasJsonFlag(), false, 'Returns false when --json is absent');
  process.argv = originalArgv;
}

{
  const originalArgv = process.argv.slice();
  const originalConsoleError = console.error;
  const captured = [];
  console.error = (...args) => captured.push(args.join(' '));

  process.argv = ['node', 'script.js'];
  log('visible log');

  process.argv = ['node', 'script.js', '--json'];
  log('hidden log');

  console.error = originalConsoleError;
  process.argv = originalArgv;

  assertEqual(captured.includes('visible log'), true, 'log() writes to stderr without --json');
  assertEqual(captured.includes('hidden log'), false, 'log() is suppressed with --json');
}

// --- stripTokenArg ---
console.log('\n📋 stripTokenArg');

assertEqual(
  stripTokenArg(['--token-file', '/path/to/token', 'query']),
  ['query'],
  'Strips --token-file and its value'
);

assertEqual(
  stripTokenArg(['query', '--limit', '5']),
  ['query', '--limit', '5'],
  'No token flags: passes through unchanged'
);

assertEqual(
  stripTokenArg([]),
  [],
  'Empty array'
);

assertEqual(
  stripTokenArg(['--filter', 'page', '--token-file', '~/.notion-token', '--limit', '5']),
  ['--filter', 'page', '--limit', '5'],
  'Strips --token-file from middle of args'
);

assertEqual(
  stripTokenArg(['--token-stdin', 'query', '--limit', '5']),
  ['query', '--limit', '5'],
  'Strips --token-stdin flag (no value)'
);

assertEqual(
  stripTokenArg(['--token-stdin', '--token-file', '/tmp/t', 'search']),
  ['search'],
  'Strips multiple token flags at once'
);

assertEqual(
  stripTokenArg(['query', '--json', '--limit', '5']),
  ['query', '--limit', '5'],
  'Strips --json flag'
);


// --- token resolution and path expansion ---
console.log('\n📋 token resolution and path expansion');

{
  const originalHomedir = os.homedir;
  os.homedir = () => '/tmp/notion-home';
  assertEqual(
    expandHomePath('~/.notion-token'),
    '/tmp/notion-home/.notion-token',
    '~ expansion in token file path'
  );
  os.homedir = originalHomedir;
}

{
  const originalArgv = process.argv.slice();
  const originalEnv = process.env.NOTION_API_KEY;
  const originalHomedir = os.homedir;

  const tempHome = fs.mkdtempSync(path.join(os.tmpdir(), 'notion-home-'));
  const defaultTokenFile = path.join(tempHome, '.notion-token');
  fs.writeFileSync(defaultTokenFile, 'token_from_default_file\n', 'utf8');

  delete process.env.NOTION_API_KEY;
  process.argv = ['node', 'script.js'];
  os.homedir = () => tempHome;
  _resetTokenCache();

  assertEqual(resolveToken(), 'token_from_default_file', 'Auto-detects ~/.notion-token before env var');

  _resetTokenCache();
  process.argv = originalArgv;
  os.homedir = originalHomedir;
  if (originalEnv === undefined) {
    delete process.env.NOTION_API_KEY;
  } else {
    process.env.NOTION_API_KEY = originalEnv;
  }
}

// --- error message formatting ---
console.log('\n📋 friendly error messages');

{
  const err401 = createDetailedError(401, '{}');
  assert(err401.message.includes('Authentication failed'), '401 has friendly auth message');

  const err404 = createDetailedError(404, JSON.stringify({ code: 'object_not_found', message: 'Not found' }));
  assert(err404.message.includes('Verify the ID'), '404 has actionable not-found guidance');

  const networkErr = wrapNetworkError({ code: 'ENOTFOUND', message: 'lookup failed' });
  assertEqual(
    networkErr.message,
    'Could not reach Notion API. Check your internet connection.',
    'Network error maps to friendly connectivity guidance'
  );
}

// --- watch-notion --state-file parsing ---
console.log('\n📋 watch-notion --state-file parsing');

{
  const originalHomedir = os.homedir;
  os.homedir = () => '/tmp/notion-home';

  const parsed = parseWatchArgs(['--state-file', '~/.watch-state.json', 'page-id', 'local.md']);
  assertEqual(parsed.pageId, 'page-id', 'Parses page-id with --state-file');
  assertEqual(parsed.localPath, 'local.md', 'Parses local path with --state-file');
  assertEqual(parsed.stateFile, '/tmp/notion-home/.watch-state.json', 'Expands ~ in --state-file path');

  os.homedir = originalHomedir;
}

// --- batch-update argument parsing ---
console.log('\n📋 batch-update argument parsing');

{
  const parsed = parseBatchUpdateArgs([
    'db-123',
    'Status',
    'Review',
    '--filter',
    '{"property":"Status","select":{"equals":"Draft"}}',
    '--type',
    'select',
    '--limit',
    '25',
  ]);

  assertEqual(parsed.stdinMode, false, 'Query mode detected by default');
  assertEqual(parsed.databaseId, 'db-123', 'Query mode parses database ID');
  assertEqual(parsed.propertyName, 'Status', 'Query mode parses property name');
  assertEqual(parsed.value, 'Review', 'Query mode parses value');
  assertEqual(parsed.propertyType, 'select', 'Query mode parses --type');
  assertEqual(parsed.limit, 25, 'Query mode parses --limit');
  assertEqual(parsed.filter.property, 'Status', 'Query mode parses --filter JSON');
}

{
  const parsed = parseBatchUpdateArgs(['--stdin', 'Status', 'Review', '--type', 'select']);
  assertEqual(parsed.stdinMode, true, '--stdin mode detection');
  assertEqual(parsed.propertyName, 'Status', 'stdin mode parses property name');
  assertEqual(parsed.value, 'Review', 'stdin mode parses value');
}

{
  const parsed = parseBatchUpdateArgs(['db-123', 'Status', 'Review', '--dry-run']);
  assertEqual(parsed.dryRun, true, '--dry-run flag detection');
}

{
  const parsed = parseBatchUpdateArgs(['db-123', 'Status', 'Review']);
  assertEqual(parsed.limit, DEFAULT_LIMIT, '--limit default value');
}

// --- Summary ---
console.log(`\n${'='.repeat(50)}`);
console.log(`Results: ${passed} passed, ${failed} failed, ${passed + failed} total`);
process.exit(failed > 0 ? 1 : 0);
