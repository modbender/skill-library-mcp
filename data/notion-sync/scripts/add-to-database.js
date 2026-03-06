#!/usr/bin/env node
/**
 * Add a markdown file as a page in a Notion database
 *
 * Usage: add-to-database.js <database-id> <page-title> <markdown-file-path>
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
    console.log('Usage: add-to-database.js <database-id> <page-title> <markdown-file-path> [--json]');
    console.log('');
    console.log('Example:');
    console.log('  add-to-database.js <db-id> "Research Report" research.md --json');
    process.exit(args[0] === '--help' ? 0 : 1);
  }

  const [dbId, title, mdPath] = args;

  if (!fs.existsSync(mdPath)) {
    const message = `File not found: ${mdPath}`;
    if (hasJsonFlag()) console.log(JSON.stringify({ error: message }, null, 2));
    else log(`Error: ${message}`);
    process.exit(1);
  }

  try {
    log('Adding page to database...');
    log(`  Database: ${dbId}`);
    log(`  Title: ${title}`);
    log(`  Source: ${mdPath}`);

    const page = await notionRequest('/v1/pages', 'POST', {
      parent: { type: 'database_id', database_id: dbId },
      properties: {
        'Name': { title: [{ text: { content: title } }] }
      }
    });

    const markdown = fs.readFileSync(mdPath, 'utf8');
    const blocks = parseMarkdownToBlocks(markdown);
    log(`Parsed ${blocks.length} blocks from markdown`);

    await appendBlocksBatched(page.id, blocks);

    const result = {
      id: page.id,
      url: `https://notion.so/${page.id.replace(/-/g, '')}`,
      title,
      blockCount: blocks.length,
    };

    if (hasJsonFlag()) {
      console.log(JSON.stringify(result, null, 2));
    } else {
      console.log(`✓ Page created: ${page.id}`);
      console.log(`  URL: ${result.url}`);
      console.log('\n✅ Successfully added to database!');
      console.log(`📄 URL: ${result.url}`);
      console.log('\n💡 Add additional properties (Type, Tags, Status) manually in Notion');
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
