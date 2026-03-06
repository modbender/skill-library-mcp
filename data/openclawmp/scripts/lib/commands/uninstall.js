// ============================================================================
// commands/uninstall.js — Uninstall an asset
// ============================================================================

'use strict';

const fs = require('fs');
const path = require('path');
const config = require('../config.js');
const { fish, ok, err, c } = require('../ui.js');

async function run(args) {
  if (args.length === 0) {
    err('Usage: openclawmp uninstall <type>/<slug>');
    process.exit(1);
  }

  const spec = args[0];
  const parts = spec.split('/');
  const type = parts[0];
  // Handle type/@author/slug or type/slug — take the last segment as slug
  const slug = parts[parts.length - 1];

  let targetDir;
  try {
    targetDir = path.join(config.installDirForType(type), slug);
  } catch (e) {
    err(e.message);
    process.exit(1);
  }

  if (!fs.existsSync(targetDir)) {
    err(`${type}/${slug} is not installed`);
    process.exit(1);
  }

  fish(`Uninstalling ${type}/${slug}...`);
  fs.rmSync(targetDir, { recursive: true, force: true });

  // Remove from lockfile — try multiple key formats
  const lock = config.readLockfile();
  const keysToRemove = Object.keys(lock.installed || {}).filter(k => {
    // Match type/slug or type/@author/slug
    return k === `${type}/${slug}` || k.startsWith(`${type}/`) && k.endsWith(`/${slug}`);
  });
  for (const key of keysToRemove) {
    config.removeLockfile(key);
  }

  ok(`Uninstalled ${type}/${slug}`);
  console.log(`   ${c('dim', `Removed: ${targetDir}`)}`);
}

module.exports = { run };
