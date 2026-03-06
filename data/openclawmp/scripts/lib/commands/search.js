// ============================================================================
// commands/search.js — Search the marketplace
// ============================================================================

'use strict';

const api = require('../api.js');
const { fish, err, c, typeIcon } = require('../ui.js');

async function run(args) {
  const query = args.join(' ');
  if (!query) {
    err('Usage: openclawmp search <query>');
    process.exit(1);
  }

  fish(`Searching the market for "${query}"...`);
  console.log('');

  const result = await api.searchAssets(query);
  const assets = result?.items || [];
  const total = result?.total || 0;

  if (assets.length === 0) {
    console.log('  No results found.');
    return;
  }

  console.log(`  Found ${total} result(s):`);
  console.log('');

  for (const a of assets) {
    const icon = typeIcon(a.type);
    const installs = a.installs || 0;
    const author = a.author || 'unknown';
    const authorId = a.authorId || 'unknown';

    console.log(`  ${icon} ${c('bold', a.displayName)}`);
    console.log(`     ${a.type}/@${authorId}/${a.name}  •  v${a.version}  •  by ${c('cyan', author)}  •  Installs: ${installs}`);

    const desc = (a.description || '').slice(0, 80);
    if (desc) {
      console.log(`     ${c('dim', desc)}`);
    }
    console.log('');
  }
}

module.exports = { run };
