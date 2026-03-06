#!/usr/bin/env node
/**
 * Post-install hook for RescueClaw skill
 * Downloads the correct binary from GitHub Releases for the user's platform.
 * No curl | bash — pinned versioned URL, platform-detected.
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');
const https = require('https');

const VERSION = '0.2.0';
const REPO = 'harman314/rescueclaw';

const PLATFORM_MAP = {
  'linux-arm64':  'rescueclaw-linux-arm64',
  'linux-x64':    'rescueclaw-linux-amd64',
  'darwin-arm64': 'rescueclaw-macos-arm64',
  'darwin-x64':   'rescueclaw-macos-amd64',
};

console.log('🛟 RescueClaw Skill - Post-Install Setup\n');

// 1. Ensure data directory
const dataDir = path.join(os.homedir(), '.openclaw', 'rescueclaw');
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true, mode: 0o755 });
  console.log(`📁 Created data directory: ${dataDir}`);
} else {
  console.log(`✅ Data directory: ${dataDir}`);
}

// 2. Check if already installed
try {
  const ver = execSync('rescueclaw --version', { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] }).trim();
  console.log(`✅ RescueClaw daemon already installed: ${ver}`);
  process.exit(0);
} catch {
  // Not installed — proceed with download
}

// 3. Determine platform
const key = `${os.platform()}-${os.arch()}`;
const assetName = PLATFORM_MAP[key];

if (!assetName) {
  console.log(`⚠️  No pre-built binary for ${key}`);
  console.log(`   Build from source: https://github.com/${REPO}`);
  process.exit(0);
}

// 4. Download from GitHub Releases
const tarName = `${assetName}.tar.gz`;
const url = `https://github.com/${REPO}/releases/download/v${VERSION}/${tarName}`;
const installDir = path.join(os.homedir(), '.local', 'bin');
const installPath = path.join(installDir, 'rescueclaw');

console.log(`📦 Downloading ${assetName} v${VERSION}...`);
console.log(`   From: ${url}`);

fs.mkdirSync(installDir, { recursive: true });

const tmpFile = path.join(os.tmpdir(), tarName);

try {
  execSync(`curl -fsSL "${url}" -o "${tmpFile}"`, { stdio: 'inherit', timeout: 60000 });
  execSync(`tar xzf "${tmpFile}" -C "${installDir}"`, { stdio: 'inherit' });
  fs.chmodSync(installPath, 0o755);
  fs.unlinkSync(tmpFile);
  console.log(`✅ Installed to ${installPath}`);
  console.log(`   Ensure ~/.local/bin is in your PATH`);
} catch (err) {
  console.log(`⚠️  Download failed. Install manually:`);
  console.log(`   ${url}`);
  console.log(`   Extract and place 'rescueclaw' in your PATH`);
  try { fs.unlinkSync(tmpFile); } catch {}
}

console.log('\n🎯 Skill ready! Use rescueclaw-checkpoint.js for safe operations.');
