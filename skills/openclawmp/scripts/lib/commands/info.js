// ============================================================================
// commands/info.js — View asset details from the registry
// ============================================================================

'use strict';

const api = require('../api.js');
const config = require('../config.js');
const { info, err, c } = require('../ui.js');

async function run(args) {
  if (args.length === 0) {
    err('Usage: openclawmp info <type>/<slug>');
    process.exit(1);
  }

  const spec = args[0];
  const parts = spec.split('/');
  const type = parts[0];
  const slug = parts[parts.length - 1];

  info(`Looking up ${type}/${slug}...`);

  const asset = await api.findAsset(type, slug);
  if (!asset) {
    err(`Not found: ${type}/${slug}`);
    process.exit(1);
  }

  // V1 AssetCompact: author is a string, authorId is separate
  const authorName = asset.author || 'unknown';
  const authorId = asset.authorId || '';
  const tags = (asset.tags || []).join(', ');

  console.log('');
  console.log(`  🐟 ${c('bold', asset.displayName || asset.name)}`);
  console.log(`  ${'─'.repeat(40)}`);
  console.log(`  Type:      ${asset.type}`);
  console.log(`  Package:   ${asset.name}`);
  console.log(`  Version:   ${asset.version}`);
  console.log(`  Author:    ${c('cyan', authorName)} ${c('dim', `(${authorId})`)}`);
  console.log(`  Installs:  ${asset.installs || 0}`);
  if (tags) {
    console.log(`  Tags:      ${tags}`);
  }
  if (asset.description) {
    console.log('');
    console.log(`  ${asset.description}`);
  }
  console.log('');
  console.log(`  Install:   openclawmp install ${asset.type}/@${authorId}/${asset.name}`);
  console.log(`  Registry:  ${config.getApiBase()}/asset/${asset.id}`);
  console.log('');
}

module.exports = { run };
