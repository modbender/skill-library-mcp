#!/usr/bin/env node
/**
 * Inspect a Notion database schema (properties and types)
 *
 * Usage: get-database-schema.js <database-id>
 */

const { checkApiKey, notionRequest, stripTokenArg, hasJsonFlag } = require('./notion-utils.js');

checkApiKey();

async function main() {
  const args = stripTokenArg(process.argv.slice(2));
  const dbId = args[0];

  if (!dbId || dbId === '--help') {
    console.log('Usage: get-database-schema.js <database-id> [--json]');
    process.exit(dbId === '--help' ? 0 : 1);
  }

  try {
    const db = await notionRequest(`/v1/databases/${dbId}`, 'GET');
    console.log(JSON.stringify(db, null, 2));
  } catch (error) {
    if (hasJsonFlag()) {
      console.log(JSON.stringify({ error: error.message }, null, 2));
    } else {
      console.error('Error:', error.message);
    }
    process.exit(1);
  }
}

main();
