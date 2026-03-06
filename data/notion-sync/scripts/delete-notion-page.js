#!/usr/bin/env node
/**
 * Archive (soft-delete) a Notion page
 *
 * Usage: delete-notion-page.js <page-id>
 */

const { checkApiKey, notionRequest, stripTokenArg, hasJsonFlag, log } = require('./notion-utils.js');

checkApiKey();

async function main() {
  const args = stripTokenArg(process.argv.slice(2));
  const pageId = args[0];

  if (!pageId || pageId === '--help') {
    console.log('Usage: delete-notion-page.js <page-id> [--json]');
    console.log('');
    console.log('Note: This archives the page (sets archived: true), not permanent deletion.');
    process.exit(pageId === '--help' ? 0 : 1);
  }

  try {
    log(`Archiving page: ${pageId}`);
    const result = await notionRequest(`/v1/pages/${pageId}`, 'PATCH', { archived: true });

    const output = {
      id: result.id,
      archived: result.archived,
      url: result.url,
    };

    if (hasJsonFlag()) {
      console.log(JSON.stringify(output, null, 2));
    } else {
      console.log('✓ Page archived successfully');
      console.log(`  Page ID: ${result.id}`);
      console.log(`  Archived: ${result.archived}`);
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
