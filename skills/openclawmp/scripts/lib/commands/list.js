// ============================================================================
// commands/list.js — List installed assets
// ============================================================================

'use strict';

const config = require('../config.js');
const { fish, c } = require('../ui.js');

async function run() {
  fish('Installed from OpenClaw Marketplace');
  console.log('');

  const lock = config.readLockfile();
  const installed = lock.installed || {};
  const keys = Object.keys(installed).sort();

  if (keys.length === 0) {
    console.log('  Nothing installed yet.');
    console.log('  Try: openclawmp search web-search');
    return;
  }

  for (const key of keys) {
    const entry = installed[key];
    const ver = entry.version || '?';
    const loc = entry.location || '?';
    const ts = (entry.installedAt || '?').slice(0, 10);

    console.log(`  📦 ${c('bold', key)}  v${ver}  ${c('dim', `(${ts})`)}`);
    console.log(`     ${c('dim', loc)}`);
    console.log('');
  }
}

module.exports = { run };
