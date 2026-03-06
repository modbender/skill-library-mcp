#!/usr/bin/env node
/**
 * Batch update Notion database page properties
 *
 * Modes:
 * 1) Query + Update:
 *    batch-update.js <database-id> <property-name> <value> --filter '<json>' [--type select] [--dry-run] [--limit 100]
 *
 * 2) Stdin page IDs:
 *    echo "page-id-1\npage-id-2" | batch-update.js --stdin <property-name> <value> [--type select] [--dry-run]
 */

const {
  checkApiKey,
  notionRequest,
  formatPropertyValue,
  extractPropertyValue,
  stripTokenArg,
  hasJsonFlag,
  log,
} = require('./notion-utils.js');

const DEFAULT_LIMIT = 100;
const UPDATE_DELAY_MS = 300;

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function parseBatchUpdateArgs(args) {
  const options = {
    stdinMode: false,
    dryRun: false,
    propertyType: 'select',
    limit: DEFAULT_LIMIT,
    filter: null,
  };

  const positional = [];

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    if (arg === '--stdin') {
      options.stdinMode = true;
      continue;
    }

    if (arg === '--dry-run') {
      options.dryRun = true;
      continue;
    }

    if (arg === '--type' && args[i + 1]) {
      options.propertyType = args[++i];
      continue;
    }

    if (arg === '--limit' && args[i + 1]) {
      options.limit = parseInt(args[++i], 10);
      continue;
    }

    if (arg === '--filter' && args[i + 1]) {
      try {
        options.filter = JSON.parse(args[++i]);
      } catch (err) {
        throw new Error(`Invalid JSON for --filter: ${err.message}`);
      }
      continue;
    }

    positional.push(arg);
  }

  if (!Number.isInteger(options.limit) || options.limit <= 0) {
    throw new Error('--limit must be a positive integer');
  }

  if (options.stdinMode) {
    return {
      ...options,
      propertyName: positional[0],
      value: positional[1],
    };
  }

  return {
    ...options,
    databaseId: positional[0],
    propertyName: positional[1],
    value: positional[2],
  };
}

async function queryMatchingPages(databaseId, filter, limit) {
  log(`Fetching database info: ${databaseId}`);
  const dbInfo = await notionRequest(`/v1/databases/${databaseId}`, 'GET');

  const dataSourceId = dbInfo.data_sources && dbInfo.data_sources.length > 0
    ? dbInfo.data_sources[0].id
    : databaseId;

  log(`Querying data source: ${dataSourceId}`);

  let results = [];
  let cursor = null;

  do {
    const remaining = limit - results.length;
    const payload = {
      page_size: Math.min(100, remaining),
    };

    if (filter) payload.filter = filter;
    if (cursor) payload.start_cursor = cursor;

    const response = await notionRequest(`/v1/data_sources/${dataSourceId}/query`, 'POST', payload);
    results = results.concat(response.results || []);

    if (results.length >= limit) break;
    cursor = response.has_more ? response.next_cursor : null;
  } while (cursor);

  return results.slice(0, limit);
}

function readStdinIds() {
  const input = require('fs').readFileSync(0, 'utf8');
  return input
    .split(/\r?\n/)
    .map(line => line.trim())
    .filter(Boolean);
}

async function updatePage(pageId, propertyName, value, propertyType) {
  const properties = {
    [propertyName]: formatPropertyValue(propertyType, value),
  };

  const result = await notionRequest(`/v1/pages/${pageId}`, 'PATCH', { properties });
  return {
    id: result.id,
    url: result.url,
    updated: result.last_edited_time,
  };
}

async function runBatchUpdate(parsed) {
  let pages = [];

  if (parsed.stdinMode) {
    const pageIds = readStdinIds().slice(0, parsed.limit);
    pages = await Promise.all(pageIds.map(async (id) => {
      const page = await notionRequest(`/v1/pages/${id}`, 'GET');
      return page;
    }));
  } else {
    pages = await queryMatchingPages(parsed.databaseId, parsed.filter, parsed.limit);
  }

  const total = pages.length;
  const results = [];

  for (let i = 0; i < total; i++) {
    const page = pages[i];
    const currentValue = page.properties && page.properties[parsed.propertyName]
      ? extractPropertyValue(page.properties[parsed.propertyName])
      : null;

    if (parsed.dryRun) {
      log(`Would update page ${i + 1}/${total}: ${page.id} (current: ${JSON.stringify(currentValue)})`);
      results.push({ id: page.id, url: page.url, updated: false });
      continue;
    }

    log(`Updating page ${i + 1}/${total}...`);
    const updated = await updatePage(page.id, parsed.propertyName, parsed.value, parsed.propertyType);
    results.push(updated);

    if (i < total - 1) {
      await sleep(UPDATE_DELAY_MS);
    }
  }

  if (parsed.dryRun) {
    log(`✓ Dry run: would update ${total} pages`);
  } else {
    log(`✓ Updated ${total} pages`);
  }

  return results;
}

function printHelp() {
  console.log('Usage:');
  console.log('  batch-update.js <database-id> <property-name> <value> --filter <json> [--type <type>] [--dry-run] [--limit 100] [--json]');
  console.log('  batch-update.js --stdin <property-name> <value> [--type <type>] [--dry-run] [--limit 100] [--json]');
  console.log('');
  console.log('Supported types: select, multi_select, checkbox, number, url, email, date, rich_text');
}

async function main() {
  const args = stripTokenArg(process.argv.slice(2));

  if (args.length === 0 || args.includes('--help')) {
    printHelp();
    process.exit(0);
  }

  let parsed;
  try {
    parsed = parseBatchUpdateArgs(args);
  } catch (error) {
    if (hasJsonFlag()) {
      console.log(JSON.stringify({ error: error.message }, null, 2));
    } else {
      log(`Error: ${error.message}`);
    }
    process.exit(1);
  }

  if (parsed.stdinMode) {
    if (!parsed.propertyName || parsed.value === undefined) {
      printHelp();
      process.exit(1);
    }
  } else if (!parsed.databaseId || !parsed.propertyName || parsed.value === undefined) {
    printHelp();
    process.exit(1);
  }

  try {
    const results = await runBatchUpdate(parsed);
    console.log(JSON.stringify(results, null, 2));
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
  module.exports = {
    parseBatchUpdateArgs,
    runBatchUpdate,
    queryMatchingPages,
    DEFAULT_LIMIT,
  };
}
