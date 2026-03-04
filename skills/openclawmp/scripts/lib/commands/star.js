// ============================================================================
// commands/star.js — Star / unstar an asset
// ============================================================================

'use strict';

const api = require('../api.js');
const auth = require('../auth.js');
const { ok, err, c } = require('../ui.js');

async function runStar(args) {
  if (args.length === 0) {
    err('Usage: openclawmp star <assetRef>');
    console.log('  Example: openclawmp star trigger/@xiaoyue/pdf-watcher');
    process.exit(1);
  }

  if (!auth.isAuthenticated()) {
    err('Authentication required. Run: openclawmp login');
    process.exit(1);
  }

  const asset = await api.resolveAssetRef(args[0]);
  const displayName = asset.displayName || asset.name || args[0];

  const { status, data } = await api.post(`/api/assets/${asset.id}/star`, {});

  if (status >= 200 && status < 300) {
    const totalStars = data.totalStars ?? data.stars ?? '?';
    ok(`★ 已收藏 ${c('bold', displayName)}（共 ${c('cyan', String(totalStars))} 人收藏）`);
  } else if (status === 409) {
    // Already starred
    ok(`★ 你已经收藏过 ${c('bold', displayName)} 了`);
  } else {
    err(`收藏失败 (${status}): ${data.error || data.message || JSON.stringify(data)}`);
    process.exit(1);
  }
}

async function runUnstar(args) {
  if (args.length === 0) {
    err('Usage: openclawmp unstar <assetRef>');
    console.log('  Example: openclawmp unstar trigger/@xiaoyue/pdf-watcher');
    process.exit(1);
  }

  if (!auth.isAuthenticated()) {
    err('Authentication required. Run: openclawmp login');
    process.exit(1);
  }

  const asset = await api.resolveAssetRef(args[0]);
  const displayName = asset.displayName || asset.name || args[0];

  const { status, data } = await api.del(`/api/assets/${asset.id}/star`);

  if (status >= 200 && status < 300) {
    ok(`☆ 已取消收藏 ${c('bold', displayName)}`);
  } else if (status === 404) {
    ok(`☆ 你还没有收藏 ${c('bold', displayName)}`);
  } else {
    err(`取消收藏失败 (${status}): ${data.error || data.message || JSON.stringify(data)}`);
    process.exit(1);
  }
}

module.exports = { runStar, runUnstar };
