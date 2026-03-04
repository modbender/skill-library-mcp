#!/usr/bin/env node
/**
 * Update Notion page properties (for database pages)
 *
 * Usage: update-page-properties.js <page-id> <property-name> <value> [--type <type>]
 */

const {
  checkApiKey,
  notionRequest,
  formatPropertyValue,
  stripTokenArg,
  hasJsonFlag,
  log,
} = require('./notion-utils.js');

checkApiKey();

async function updatePageProperties(pageId, propertyName, value, propertyType = 'select') {
  const properties = {};
  properties[propertyName] = formatPropertyValue(propertyType, value);

  log(`Updating page: ${pageId}`);
  log(`Property: ${propertyName} (${propertyType})`);
  log(`Value: ${value}`);

  const result = await notionRequest(`/v1/pages/${pageId}`, 'PATCH', { properties });

  return {
    id: result.id,
    url: result.url,
    updated: result.last_edited_time
  };
}

async function main() {
  const args = stripTokenArg(process.argv.slice(2));

  if (args.length < 3 || args[0] === '--help') {
    console.log('Usage: update-page-properties.js <page-id> <property-name> <value> [--type <type>] [--json]');
    console.log('');
    console.log('Supported types: select, multi_select, checkbox, number, url, email, date, rich_text');
    console.log('');
    console.log('Examples:');
    console.log('  update-page-properties.js <id> Status Complete --type select');
    console.log('  update-page-properties.js <id> Tags "AI,Leadership" --type multi_select');
    console.log('  update-page-properties.js <id> Published true --type checkbox');
    console.log('  update-page-properties.js <id> "Publish Date" 2024-02-01 --type date --json');
    process.exit(0);
  }

  const pageId = args[0];
  const propertyName = args[1];
  const value = args[2];
  let propertyType = 'select';

  for (let i = 3; i < args.length; i++) {
    if (args[i] === '--type' && args[i + 1]) { propertyType = args[++i]; }
  }

  try {
    const result = await updatePageProperties(pageId, propertyName, value, propertyType);
    console.log(JSON.stringify(result, null, 2));
    log('\n✓ Page updated successfully');
    log(`  URL: ${result.url}`);
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
