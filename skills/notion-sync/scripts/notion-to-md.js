#!/usr/bin/env node
/**
 * Notion page to Markdown converter
 * Fetches a Notion page and converts blocks to markdown
 *
 * Usage: notion-to-md.js <page-id> [output-file]
 */

const {
  checkApiKey,
  notionRequest,
  normalizeId,
  getAllBlocks,
  blocksToMarkdown,
  stripTokenArg,
  hasJsonFlag,
  log,
} = require('./notion-utils.js');

/**
 * Fetch page metadata
 */
async function getPage(pageId) {
  const id = normalizeId(pageId);
  return notionRequest(`/v1/pages/${encodeURIComponent(id)}`, 'GET');
}

async function main() {
  const args = stripTokenArg(process.argv.slice(2));

  if (args.length < 1 || args[0] === '--help') {
    console.log('Usage: notion-to-md.js <page-id> [output-file] [--json]');
    console.log('');
    console.log('Example:');
    console.log('  notion-to-md.js "abc123..." newsletter.md --json');
    process.exit(args[0] === '--help' ? 0 : 1);
  }

  const pageId = normalizeId(args[0]);
  const outputFile = args[1] || null;

  try {
    const page = await getPage(pageId);
    const title = page.properties?.title?.title?.[0]?.plain_text || 'Untitled';

    const blocks = await getAllBlocks(pageId);
    const markdown = blocksToMarkdown(blocks);

    if (outputFile) {
      const fs = require('fs');
      fs.writeFileSync(outputFile, `# ${title}\n\n${markdown}`, 'utf8');
      if (!hasJsonFlag()) {
        log(`✓ Saved to ${outputFile}`);
      }
    } else if (!hasJsonFlag()) {
      console.log(markdown);
    }

    const result = {
      markdown,
      pageId,
      title,
      lastEditedTime: page.last_edited_time,
      blockCount: blocks.length,
    };

    if (hasJsonFlag()) {
      console.log(JSON.stringify({ markdown, pageId }, null, 2));
    }

    return result;
  } catch (error) {
    if (hasJsonFlag()) {
      console.log(JSON.stringify({ error: error.message }, null, 2));
    } else {
      log(`Error: ${error.message}`);
    }
    process.exit(1);
  }
}

if (require.main === module) {
  checkApiKey();
  main();
} else {
  // Re-export utilities for backwards compatibility (v1.0.x)
  // Prefer importing from notion-utils.js directly for new code
  module.exports = { getPage, main, getAllBlocks, blocksToMarkdown, normalizeId };
}
