#!/usr/bin/env node
/**
 * Markdown to Notion page converter
 * Parses markdown and creates a Notion page with formatted blocks
 *
 * Usage: md-to-notion.js <markdown-file> <parent-page-id> <page-title>
 */

const fs = require('fs');
const {
  checkApiKey,
  notionRequest,
  parseMarkdownToBlocks,
  appendBlocksBatched,
  stripTokenArg,
  hasJsonFlag,
  log,
} = require('./notion-utils.js');

checkApiKey();

async function main() {
  const args = stripTokenArg(process.argv.slice(2));

  if (args.length < 3 || args[0] === '--help') {
    console.log('Usage: md-to-notion.js <markdown-file> <parent-page-id> <page-title> [--json]');
    console.log('');
    console.log('Example:');
    console.log('  md-to-notion.js draft.md "abc123..." "Newsletter Draft" --json');
    process.exit(args[0] === '--help' ? 0 : 1);
  }

  const [mdFile, parentId, pageTitle] = args;

  if (!fs.existsSync(mdFile)) {
    const message = `File not found: ${mdFile}`;
    if (hasJsonFlag()) console.log(JSON.stringify({ error: message }, null, 2));
    else log(`Error: ${message}`);
    process.exit(1);
  }

  try {
    const markdown = fs.readFileSync(mdFile, 'utf8');
    const blocks = parseMarkdownToBlocks(markdown, { richText: 'markdown' });

    log(`Parsed ${blocks.length} blocks from markdown`);

    const page = await notionRequest('/v1/pages', 'POST', {
      parent: { page_id: parentId },
      properties: {
        title: { title: [{ text: { content: pageTitle } }] }
      },
      children: blocks.slice(0, 100)
    });
    log(`✓ Created page: ${page.url}`);

    if (blocks.length > 100) {
      await appendBlocksBatched(page.id, blocks.slice(100));
      log(`✓ Appended ${blocks.length - 100} remaining blocks`);
    }

    const result = {
      url: page.url,
      pageId: page.id,
      title: pageTitle,
      blockCount: blocks.length,
    };

    if (hasJsonFlag()) {
      console.log(JSON.stringify(result, null, 2));
    } else {
      console.log('\n✅ Successfully created Notion page!');
      console.log(`📄 URL: ${page.url}`);
      console.log(`🆔 Page ID: ${page.id}`);
    }
  } catch (error) {
    if (hasJsonFlag()) {
      console.log(JSON.stringify({ error: error.message }, null, 2));
    } else {
      log(`Error: ${error.message}`);
    }
    process.exit(1);
  }
}

main();
