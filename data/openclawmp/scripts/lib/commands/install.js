// ============================================================================
// commands/install.js — Install an asset from the marketplace
// ============================================================================

'use strict';

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const api = require('../api.js');
const config = require('../config.js');
const { fish, info, ok, warn, err, c, detail } = require('../ui.js');

/**
 * Parse an install spec: type/@author/slug or type/slug
 * @returns {{ type: string, slug: string, authorFilter: string }}
 */
function parseSpec(spec) {
  if (!spec || !spec.includes('/')) {
    throw new Error('Format must be <type>/@<author>/<slug>, e.g. trigger/@xiaoyue/fs-event-trigger');
  }

  const firstSlash = spec.indexOf('/');
  const type = spec.slice(0, firstSlash);
  const rest = spec.slice(firstSlash + 1);

  let slug, authorFilter = '';

  if (rest.startsWith('@')) {
    // Scoped: @author/slug
    const slashIdx = rest.indexOf('/');
    if (slashIdx === -1) {
      throw new Error('Format must be <type>/@<author>/<slug>');
    }
    authorFilter = rest.slice(1, slashIdx); // strip @
    slug = rest.slice(slashIdx + 1);
  } else {
    // Legacy: type/slug
    slug = rest;
  }

  return { type, slug, authorFilter };
}

/**
 * Extract a tar.gz or zip buffer to a directory
 */
function extractPackage(buffer, targetDir) {
  const tmpFile = path.join(require('os').tmpdir(), `openclawmp-pkg-${process.pid}-${Date.now()}`);
  fs.writeFileSync(tmpFile, buffer);

  try {
    // Try tar first
    try {
      execSync(`tar xzf "${tmpFile}" -C "${targetDir}" --strip-components=1 2>/dev/null`, { stdio: 'pipe' });
      return true;
    } catch {
      // Try without --strip-components
      try {
        execSync(`tar xzf "${tmpFile}" -C "${targetDir}" 2>/dev/null`, { stdio: 'pipe' });
        return true;
      } catch {
        // Try unzip
        try {
          execSync(`unzip -o -q "${tmpFile}" -d "${targetDir}" 2>/dev/null`, { stdio: 'pipe' });
          // If single subdirectory, move contents up
          const entries = fs.readdirSync(targetDir);
          const dirs = entries.filter(e => fs.statSync(path.join(targetDir, e)).isDirectory());
          if (dirs.length === 1 && entries.length === 1) {
            const subdir = path.join(targetDir, dirs[0]);
            for (const f of fs.readdirSync(subdir)) {
              fs.renameSync(path.join(subdir, f), path.join(targetDir, f));
            }
            fs.rmdirSync(subdir);
          }
          return true;
        } catch {
          return false;
        }
      }
    }
  } finally {
    try { fs.unlinkSync(tmpFile); } catch {}
  }
}

/**
 * Count files recursively in a directory
 */
function countFiles(dir) {
  let count = 0;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.isFile()) count++;
    else if (entry.isDirectory()) count += countFiles(path.join(dir, entry.name));
  }
  return count;
}

/**
 * Write manifest.json for the installed asset
 */
function writeManifest(asset, targetDir, hasPackage) {
  const manifest = {
    schema: 1,
    type: asset.type,
    name: asset.name,
    displayName: asset.displayName || '',
    version: asset.version,
    author: asset.author || '',
    authorId: asset.authorId || '',
    description: asset.description || '',
    tags: asset.tags || [],
    category: asset.category || '',
    installedFrom: 'openclawmp',
    registryId: asset.id,
    hasPackage,
  };
  fs.writeFileSync(path.join(targetDir, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n');
}

/**
 * Post-install hints per asset type
 */
function showPostInstallHints(type, slug, targetDir) {
  switch (type) {
    case 'skill':
      console.log(`   ${c('green', 'Ready!')} Will be loaded in the next agent session.`);
      break;
    case 'plugin':
      console.log(`   ${c('yellow', 'Requires restart:')} openclaw gateway restart`);
      break;
    case 'channel':
      console.log(`   ${c('yellow', 'Requires config:')} Set credentials in openclaw.json, then restart`);
      break;
    case 'trigger':
      console.log(`   ${c('yellow', 'Manual setup:')} Read README.md for cron/heartbeat configuration`);
      console.log(`   ${c('dim', `cat ${targetDir}/README.md`)}`);
      break;
    case 'experience':
      console.log(`   ${c('yellow', 'Reference:')} Read README.md for setup instructions`);
      console.log(`   ${c('dim', `cat ${targetDir}/README.md`)}`);
      break;
  }
}

async function run(args, flags) {
  if (args.length === 0) {
    err('Usage: openclawmp install <type>/@<author>/<slug>');
    console.log('  Example: openclawmp install trigger/@xiaoyue/fs-event-trigger');
    process.exit(1);
  }

  const { type, slug, authorFilter } = parseSpec(args[0]);
  const displaySpec = `${type}/${authorFilter ? `@${authorFilter}/` : ''}${slug}`;

  fish('OpenClaw Marketplace Install');
  console.log('');
  info(`Looking up ${c('bold', displaySpec)} in the market...`);

  // Query the registry
  const asset = await api.findAsset(type, slug, authorFilter);
  if (!asset) {
    err(`Asset ${c('bold', displaySpec)} not found in the market.`);
    console.log('');
    console.log(`  Try: openclawmp search ${slug}`);
    process.exit(1);
  }

  const displayName = asset.displayName || asset.name;
  const version = asset.version;
  const authorName = asset.author || 'unknown';
  const authorId = asset.authorId || '';

  console.log(`  ${c('bold', displayName)} ${c('dim', `v${version}`)}`);
  console.log(`  by ${c('cyan', authorName)} ${c('dim', `(${authorId})`)}`);
  console.log('');

  // Determine install directory
  const targetDir = path.join(config.installDirForType(type), slug);

  // Check if already installed
  if (fs.existsSync(targetDir)) {
    if (flags.force || flags.y) {
      fs.rmSync(targetDir, { recursive: true, force: true });
    } else {
      warn(`Already installed at ${targetDir}`);
      // In non-interactive mode, skip confirmation
      const readline = require('readline');
      const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
      const answer = await new Promise(resolve => {
        rl.question('  Overwrite? [y/N] ', resolve);
      });
      rl.close();
      if (!/^[yY]/.test(answer)) {
        console.log('  Aborted.');
        return;
      }
      fs.rmSync(targetDir, { recursive: true, force: true });
    }
  }

  info(`Installing to ${c('dim', targetDir)}...`);
  fs.mkdirSync(targetDir, { recursive: true });

  // Try downloading the actual package
  let hasPackage = false;
  const pkgBuffer = await api.download(`/api/assets/${asset.id}/download`);

  if (pkgBuffer && pkgBuffer.length > 0) {
    info('📦 Downloading package from registry...');
    hasPackage = extractPackage(pkgBuffer, targetDir);
    if (hasPackage) {
      const fileCount = countFiles(targetDir);
      console.log(`  📦 Extracted ${c('bold', String(fileCount))} files from package`);
    }
  }

  // No package → error (no fallback generation)
  if (!hasPackage) {
    try { fs.rmSync(targetDir, { recursive: true, force: true }); } catch {}
    err('该资产没有可安装的 package。');
    console.log(`  请在水产市场查看详情：${config.getApiBase()}/asset/${asset.id}`);
    process.exit(1);
  }

  // Always write manifest.json
  writeManifest(asset, targetDir, hasPackage);
  console.log('  Created: manifest.json');

  // Update lockfile
  const lockKey = `${type}/${authorId ? `@${authorId}/` : ''}${slug}`;
  config.updateLockfile(lockKey, version, targetDir);

  console.log('');
  ok(`Installed ${c('bold', displayName)} v${version}`);
  detail('Location', targetDir);
  detail('Registry', `${config.getApiBase()}/asset/${asset.id}`);
  detail('Command', `openclawmp install ${type}/@${authorId}/${slug}`);
  console.log('');

  showPostInstallHints(type, slug, targetDir);
  console.log('');
}

module.exports = { run };
