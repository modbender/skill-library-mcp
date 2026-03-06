#!/usr/bin/env node
// Usage: NODE_PATH=/tmp/node_modules node post-article.js --title "Title" --body "Body" [--body-file /path] [--cover /path] [--port 18800] [--dry-run]
// Creates an X Article via CDP. Requires X Premium.
//
// Supports markdown: # → 标题, ##+ → 副标题, plain → 正文, ``` → code as body text
// Lists (- / 1.) are preserved as body text.

const { connect, cleanup, sleep, verifyAccount, dryRunScreenshot, SELECTORS, DEFAULT_PORT } = require('./lib/cdp-utils');
const fs = require('fs');

function parseArgs(argv) {
  const args = { title: '', body: '', cover: null, port: DEFAULT_PORT, account: '', dryRun: false };
  let i = 2;
  while (i < argv.length) {
    const a = argv[i];
    if (a === '--title' && argv[i + 1]) { args.title = argv[i + 1]; i += 2; }
    else if (a === '--body' && argv[i + 1]) { args.body = argv[i + 1]; i += 2; }
    else if (a === '--body-file' && argv[i + 1]) {
      if (!fs.existsSync(argv[i + 1])) {
        console.error(`File not found: ${argv[i + 1]}`);
        process.exit(1);
      }
      try {
        args.body = fs.readFileSync(argv[i + 1], 'utf-8');
      } catch (e) {
        console.error(`Cannot read file ${argv[i + 1]}: ${e.message}`);
        process.exit(1);
      }
      i += 2;
    }
    else if (a === '--cover' && argv[i + 1]) {
      if (!fs.existsSync(argv[i + 1])) {
        console.error(`Cover image not found: ${argv[i + 1]}`);
        process.exit(1);
      }
      args.cover = argv[i + 1];
      i += 2;
    }
    else if (a === '--port' && argv[i + 1]) {
      const p = parseInt(argv[i + 1], 10);
      if (isNaN(p) || p <= 0) { console.error(`Invalid port: ${argv[i + 1]}`); process.exit(1); }
      args.port = p;
      i += 2;
    }
    else if (a === '--account' && argv[i + 1]) { args.account = argv[i + 1]; i += 2; }
    else if (a === '--dry-run') { args.dryRun = true; i++; }
    else { i++; }
  }
  return args;
}

/**
 * Parse markdown body into structured blocks.
 * Returns array of { type: 'heading'|'subheading'|'body', text: string }
 */
function parseMarkdownBlocks(md) {
  const lines = md.split('\n');
  const blocks = [];
  let currentBlock = null;
  let inCodeBlock = false;
  let codeLines = [];
  let skipFirstH1 = true;

  function flush() {
    if (currentBlock) { blocks.push(currentBlock); currentBlock = null; }
  }

  for (const line of lines) {
    // Code block toggle
    if (line.trim().startsWith('```')) {
      if (inCodeBlock) {
        if (codeLines.length > 0) {
          flush();
          blocks.push({ type: 'body', text: codeLines.join('\n') });
        }
        codeLines = [];
        inCodeBlock = false;
      } else {
        flush();
        inCodeBlock = true;
      }
      continue;
    }

    if (inCodeBlock) {
      codeLines.push(line);
      continue;
    }

    // First H1 = skip (already in title)
    if (line.startsWith('# ') && skipFirstH1) {
      skipFirstH1 = false;
      continue;
    }
    skipFirstH1 = false;

    // ## and deeper → subheading
    if (line.match(/^#{2,}\s+/)) {
      flush();
      blocks.push({ type: 'subheading', text: line.replace(/^#+\s+/, '') });
      continue;
    }

    // # → heading
    if (line.startsWith('# ')) {
      flush();
      blocks.push({ type: 'heading', text: line.replace(/^#\s+/, '') });
      continue;
    }

    // Horizontal rule → skip
    if (line.match(/^[-*_]{3,}\s*$/)) continue;

    // Blockquote: strip >
    const stripped = line.startsWith('> ') ? line.slice(2) : line;

    // Empty line = paragraph break
    if (stripped.trim() === '') {
      flush();
      continue;
    }

    // Strip bold markers (editor handles formatting separately)
    const cleaned = stripped.replace(/\*\*([^*]+)\*\*/g, '$1');

    // Accumulate body
    if (currentBlock && currentBlock.type === 'body') {
      currentBlock.text += '\n' + cleaned;
    } else {
      flush();
      currentBlock = { type: 'body', text: cleaned };
    }
  }

  // Flush remaining code block
  if (inCodeBlock && codeLines.length > 0) {
    flush();
    blocks.push({ type: 'body', text: codeLines.join('\n') });
  }
  flush();

  return blocks.filter(b => b.text.trim());
}

/**
 * Select format from the editor dropdown menu.
 */
// Locale-aware format labels: [zh, en]
const FORMAT_LABELS = {
  heading:    ['标题', 'Title'],
  subheading: ['副标题', 'Subtitle'],
  body:       ['正文', 'Body'],
};
const ALL_FORMAT_LABELS = Object.values(FORMAT_LABELS).flat();

/**
 * Read the current format from the editor's format button.
 * @returns {string|null} format label or null
 */
async function getCurrentFormat(page) {
  const buttons = await page.$$('button');
  for (const btn of buttons) {
    const text = await btn.evaluate(el => el.textContent?.trim());
    if (text && ALL_FORMAT_LABELS.some(l => l === text)) {
      return text;
    }
  }
  return null;
}

/**
 * Select format from the editor dropdown menu.
 * Reads current format first to avoid unnecessary switches.
 */
async function selectFormat(page, format) {
  const current = await getCurrentFormat(page);
  if (current === format) return; // Already correct

  const buttons = await page.$$('button');
  let formatBtn = null;
  for (const btn of buttons) {
    const text = await btn.evaluate(el => el.textContent?.trim());
    if (text && ALL_FORMAT_LABELS.some(l => l === text)) {
      formatBtn = btn;
      break;
    }
  }
  if (!formatBtn) return;

  await formatBtn.click();
  await sleep(500);

  const menuItems = await page.$$(SELECTORS.menuItem);
  // Find the target format's label group for matching either locale
  const labelGroup = Object.values(FORMAT_LABELS).find(g => g.includes(format)) || [format];
  for (const item of menuItems) {
    const text = await item.evaluate(el => el.textContent?.trim());
    if (text && labelGroup.some(l => l === text)) {
      await item.click();
      await sleep(300);
      return;
    }
  }
  await page.keyboard.press('Escape');
  await sleep(200);
}

(async () => {
  const args = parseArgs(process.argv);
  if (!args.title || !args.body) {
    console.error('Usage: node post-article.js --title "Title" --body "Body" [--body-file /path] [--cover /path] [--port 18800] [--dry-run]');
    process.exit(1);
  }

  const { browser, newPage } = await connect(args.port);
  const page = await newPage();

  try {
    await verifyAccount(page, args.account || null);

    // Step 1: Article list
    console.log('[1] Opening article list...');
    await page.goto('https://x.com/compose/articles', { waitUntil: 'networkidle2', timeout: 30000 });
    await sleep(3000);

    // Step 2: Create new article
    console.log('[2] Creating new article...');
    const createBtn = await page.$(SELECTORS.articleCreateBtn);
    if (!createBtn) throw new Error('Create button not found. Are you on the articles page?');
    await createBtn.click();

    // Wait for editor to load (selector-based, no fixed sleep)
    const composer = await page.waitForSelector(SELECTORS.articleComposer, { timeout: 15000 })
      .catch(() => null);
    if (!composer) throw new Error('Article editor did not load');

    // Also wait for title field
    const titleField = await page.waitForSelector(SELECTORS.articleTitle, { timeout: 5000 })
      .catch(() => null);

    // Step 3: Fill title
    console.log('[3] Filling title...');
    if (!titleField) throw new Error('Title field not found');
    await titleField.click();
    await sleep(300);
    await page.keyboard.type(args.title, { delay: 20 });
    await sleep(500);

    // Step 4: Fill body
    console.log('[4] Filling body...');
    const blocks = parseMarkdownBlocks(args.body);
    console.log(`    ${blocks.length} blocks parsed`);

    const bodyField = await page.$(SELECTORS.articleComposer);
    if (!bodyField) throw new Error('Body composer not found');
    await bodyField.click();
    await sleep(500);

    // Detect locale from first format button text
    const detectedFormat = await getCurrentFormat(page);
    const isEn = detectedFormat && FORMAT_LABELS.body[1] === detectedFormat || FORMAT_LABELS.heading[1] === detectedFormat;
    const li = isEn ? 1 : 0; // locale index
    const formatMap = { heading: FORMAT_LABELS.heading[li], subheading: FORMAT_LABELS.subheading[li], body: FORMAT_LABELS.body[li] };

    for (let i = 0; i < blocks.length; i++) {
      const block = blocks[i];
      const targetFormat = formatMap[block.type];

      // selectFormat reads actual editor state, no tracking needed
      await selectFormat(page, targetFormat);

      // Use CDP Input.insertText for speed
      const client = await page.target().createCDPSession();
      const lines = block.text.split('\n');
      for (let j = 0; j < lines.length; j++) {
        if (j > 0) {
          await page.keyboard.down('Shift');
          await page.keyboard.press('Enter');
          await page.keyboard.up('Shift');
        }
        await client.send('Input.insertText', { text: lines[j] });
      }
      await client.detach();
      await sleep(50);

      // Enter for new block
      if (i < blocks.length - 1) {
        await page.keyboard.press('Enter');
        await sleep(100);
      }

      if ((i + 1) % 20 === 0) console.log(`    Progress: ${i + 1}/${blocks.length}`);
    }

    await sleep(1000);
    console.log('[4] Body filled.');

    // Step 5: Cover image
    if (args.cover) {
      console.log('[5] Uploading cover...');
      const mediaBtn = await page.$('[aria-label="添加媒体内容"], [aria-label="Add media"]');
      if (mediaBtn) {
        await mediaBtn.click();
        await sleep(1000);
        const fileInput = await page.$('input[type="file"]');
        if (fileInput) {
          await fileInput.uploadFile(args.cover);
          await sleep(3000);
        }
      }
    }

    if (args.dryRun) {
      await dryRunScreenshot(page, 'post-article');
      console.log('[DRY RUN] Article filled but not published.');
      browser.disconnect();
      return;
    }

    // Step 6: Publish
    console.log('[6] Publishing...');
    const allButtons = await page.$$('button');
    let publishBtn = null;
    for (const btn of allButtons) {
      const text = await btn.evaluate(el => el.textContent?.trim());
      if (text === '发布' || text === 'Publish') { publishBtn = btn; break; }
    }
    if (!publishBtn) throw new Error('Publish button not found');
    await publishBtn.click();
    await sleep(5000);

    console.log('OK: Article published');
  } catch (e) {
    console.error('FAIL: ' + e.message);
    process.exit(1);
  } finally {
    if (!args.dryRun) await cleanup(page, browser);
  }
})();
