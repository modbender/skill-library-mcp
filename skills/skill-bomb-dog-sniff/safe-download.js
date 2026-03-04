#!/usr/bin/env node
// safe-download.js - Download, scan, and safely install skills
// Part of bomb-dog-sniff security toolkit
// Version: 1.2.0 - Hardened Edition

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { spawn } = require('child_process');
const { scanSkill } = require('./scan');

// Security constants
const MAX_DOWNLOAD_SIZE = 50 * 1024 * 1024; // 50MB max download
const DOWNLOAD_TIMEOUT = 120000; // 2 minutes
const SAFE_INSTALL_DIR = process.env.OPENCLAW_SKILLS_DIR || 
  path.join(process.env.HOME || '/tmp', '.openclaw', 'workspace', 'skills');

// Generate secure quarantine path (not predictable)
function getQuarantinePath() {
  const random = crypto.randomBytes(8).toString('hex');
  const timestamp = Date.now();
  return path.join(require('os').tmpdir(), `bds-q-${timestamp}-${random}`);
}

// Validate and sanitize path components
function sanitizePath(input) {
  if (!input || typeof input !== 'string') {
    throw new Error('Invalid path input');
  }
  
  // Remove null bytes
  let sanitized = input.replace(/\0/g, '');
  
  // Prevent path traversal
  if (sanitized.includes('..')) {
    throw new Error('Path traversal detected');
  }
  
  // Remove shell metacharacters
  sanitized = sanitized.replace(/[;&|`$(){}[\]\\]/g, '');
  
  return sanitized;
}

// Validate URL format
function validateUrl(url) {
  try {
    const parsed = new URL(url);
    // Only allow HTTPS
    if (parsed.protocol !== 'https:') {
      throw new Error('Only HTTPS URLs are allowed');
    }
    return parsed;
  } catch (err) {
    throw new Error(`Invalid URL: ${err.message}`);
  }
}

// Download file with size limit and timeout using native HTTPS
async function downloadFile(url, destPath) {
  return new Promise((resolve, reject) => {
    const https = require('https');
    const file = fs.createWriteStream(destPath, { flags: 'wx' });
    let downloadedSize = 0;
    let timeout;
    
    const cleanup = () => {
      clearTimeout(timeout);
      try {
        fs.unlinkSync(destPath);
      } catch (e) {
        // Ignore cleanup errors
      }
    };
    
    // Set download timeout
    timeout = setTimeout(() => {
      cleanup();
      reject(new Error('Download timeout'));
    }, DOWNLOAD_TIMEOUT);
    
    const request = https.get(url, {
      headers: {
        'User-Agent': 'bomb-dog-sniff/1.2.0',
      },
      timeout: DOWNLOAD_TIMEOUT,
    }, (response) => {
      if (response.statusCode >= 300 && response.statusCode < 400 && response.headers.location) {
        // Handle redirect
        clearTimeout(timeout);
        file.close();
        fs.unlinkSync(destPath);
        downloadFile(response.headers.location, destPath).then(resolve).catch(reject);
        return;
      }
      
      if (response.statusCode !== 200) {
        clearTimeout(timeout);
        cleanup();
        reject(new Error(`HTTP ${response.statusCode}`));
        return;
      }
      
      response.on('data', (chunk) => {
        downloadedSize += chunk.length;
        if (downloadedSize > MAX_DOWNLOAD_SIZE) {
          clearTimeout(timeout);
          cleanup();
          reject(new Error(`Download exceeds maximum size (${MAX_DOWNLOAD_SIZE} bytes)`));
        }
      });
      
      response.pipe(file);
      
      file.on('finish', () => {
        clearTimeout(timeout);
        file.close(() => resolve(downloadedSize));
      });
    });
    
    request.on('error', (err) => {
      clearTimeout(timeout);
      cleanup();
      reject(err);
    });
    
    file.on('error', (err) => {
      clearTimeout(timeout);
      cleanup();
      reject(err);
    });
  });
}

// Extract zip file securely
async function extractZip(zipPath, destDir) {
  return new Promise((resolve, reject) => {
    // Use unzip with security options
    const child = spawn('unzip', ['-q', '-o', zipPath, '-d', destDir], {
      timeout: 60000,
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    
    let stderr = '';
    child.stderr.on('data', (data) => {
      stderr += data.toString();
    });
    
    child.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Unzip failed: ${stderr || `exit code ${code}`}`));
      } else {
        resolve();
      }
    });
    
    child.on('error', (err) => {
      reject(new Error(`Failed to run unzip: ${err.message}`));
    });
  });
}

// Copy directory recursively with validation
async function copyDir(src, dest) {
  const entries = fs.readdirSync(src, { withFileTypes: true });
  
  if (!fs.existsSync(dest)) {
    fs.mkdirSync(dest, { recursive: true });
  }
  
  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    
    // Validate entry name
    if (entry.name.includes('..') || entry.name.includes('\0')) {
      console.error(`Warning: Skipping invalid entry: ${entry.name}`);
      continue;
    }
    
    if (entry.isDirectory()) {
      await copyDir(srcPath, destPath);
    } else if (entry.isFile()) {
      // Copy file
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

// Clean quarantine directory
function cleanQuarantine(quarantinePath) {
  if (quarantinePath && fs.existsSync(quarantinePath)) {
    try {
      fs.rmSync(quarantinePath, { recursive: true, force: true });
    } catch (err) {
      console.error(`Warning: Failed to clean quarantine: ${err.message}`);
    }
  }
}

// Download skill from various sources
async function downloadSkill(source, quarantinePath) {
  console.error(`📥 Downloading skill from: ${source}`);
  
  // Check if it's a GitHub URL
  if (source.includes('github.com')) {
    return downloadFromGitHub(source, quarantinePath);
  }
  
  // Check if it's a clawhub skill name
  if (!source.includes('/') && !source.includes('http') && !source.includes('\\')) {
    return downloadFromClawhub(source, quarantinePath);
  }
  
  // Check if it's a local path
  if (fs.existsSync(source)) {
    return copyLocalSkill(source, quarantinePath);
  }
  
  throw new Error(`Unknown source type: ${source}. Supported: GitHub URL, clawhub skill name, local path`);
}

// Download from GitHub
async function downloadFromGitHub(githubUrl, quarantinePath) {
  // Validate and parse URL
  const parsedUrl = validateUrl(githubUrl);
  
  // Handle different GitHub URL formats
  if (githubUrl.includes('/blob/')) {
    throw new Error('Single file URLs not supported. Use repository root URL.');
  }
  
  // Extract owner/repo from URL
  const match = githubUrl.match(/github\.com\/([^\/]+)\/([^\/]+?)(?:\.git|\/|$)/);
  if (!match) {
    throw new Error('Invalid GitHub URL format');
  }
  
  const [, owner, repo] = match;
  
  // Validate owner and repo names
  if (!/^[a-zA-Z0-9_.-]+$/.test(owner) || !/^[a-zA-Z0-9_.-]+$/.test(repo)) {
    throw new Error('Invalid GitHub owner or repository name');
  }
  
  // Try main branch first, then master
  const branches = ['main', 'master'];
  let lastError = null;
  
  for (const branch of branches) {
    try {
      const downloadUrl = `https://github.com/${owner}/${repo}/archive/refs/heads/${branch}.zip`;
      const zipPath = path.join(quarantinePath, 'download.zip');
      
      console.error(`   Trying ${branch} branch...`);
      await downloadFile(downloadUrl, zipPath);
      
      // Extract
      await extractZip(zipPath, quarantinePath);
      
      // Remove zip file
      fs.unlinkSync(zipPath);
      
      // Find extracted directory
      const entries = fs.readdirSync(quarantinePath);
      const extracted = entries.find(d => d.startsWith(`${repo}-`) && !d.endsWith('.zip'));
      
      if (!extracted) {
        throw new Error('Failed to find extracted directory');
      }
      
      return path.join(quarantinePath, extracted);
    } catch (err) {
      lastError = err;
      if (err.message.includes('HTTP 404')) {
        // Try next branch
        continue;
      }
      throw err;
    }
  }
  
  throw new Error(`Failed to download from GitHub: ${lastError?.message || 'Repository not found'}`);
}

// Download from clawhub (placeholder - would integrate with actual clawhub)
async function downloadFromClawhub(skillName, quarantinePath) {
  // Validate skill name
  if (!/^[a-zA-Z0-9_-]+$/.test(skillName)) {
    throw new Error('Invalid skill name. Use alphanumeric characters, hyphens, and underscores only.');
  }
  
  console.error(`🔍 Fetching ${skillName} from clawhub...`);
  
  // Sanitize skill name
  const sanitizedName = sanitizePath(skillName);
  
  try {
    // Use clawhub CLI if available (with safe argument passing)
    const skillPath = path.join(quarantinePath, sanitizedName);
    
    await new Promise((resolve, reject) => {
      const child = spawn('npx', ['clawhub@latest', 'download', sanitizedName, skillPath], {
        timeout: 120000,
        stdio: ['ignore', 'pipe', 'pipe'],
        env: { ...process.env, NODE_NO_WARNINGS: '1' },
      });
      
      let stderr = '';
      child.stderr.on('data', (data) => {
        stderr += data.toString();
      });
      
      child.on('close', (code) => {
        if (code !== 0) {
          reject(new Error(`clawhub download failed: ${stderr || `exit code ${code}`}`));
        } else {
          resolve();
        }
      });
      
      child.on('error', (err) => {
        reject(new Error(`Failed to run clawhub: ${err.message}`));
      });
    });
    
    return skillPath;
  } catch (err) {
    // Fallback: try to find in known locations
    const bundledPath = path.join(
      process.env.HOME || '/tmp', 
      '.npm-global/lib/node_modules/openclaw/skills',
      sanitizedName
    );
    
    if (fs.existsSync(bundledPath)) {
      const targetPath = path.join(quarantinePath, sanitizedName);
      await copyDir(bundledPath, targetPath);
      return targetPath;
    }
    
    throw new Error(`Failed to download ${sanitizedName} from clawhub: ${err.message}`);
  }
}

// Copy local skill
async function copyLocalSkill(localPath, quarantinePath) {
  const resolvedPath = path.resolve(localPath);
  
  // Validate it's a directory
  const stats = fs.statSync(resolvedPath);
  if (!stats.isDirectory()) {
    throw new Error('Local path must be a directory');
  }
  
  const skillName = path.basename(resolvedPath);
  const targetPath = path.join(quarantinePath, skillName);
  
  // Validate skill name
  if (!/^[a-zA-Z0-9_.-]+$/.test(skillName)) {
    throw new Error('Invalid skill directory name');
  }
  
  await copyDir(resolvedPath, targetPath);
  return targetPath;
}

// Install skill to final destination
async function installSkill(skillPath, skillName, options = {}) {
  const { backup = true, dryRun = false } = options;
  const targetPath = path.join(SAFE_INSTALL_DIR, skillName);
  
  if (dryRun) {
    console.error(`   (Dry run - would install to: ${targetPath})`);
    return targetPath;
  }
  
  // Ensure target directory exists
  if (!fs.existsSync(SAFE_INSTALL_DIR)) {
    fs.mkdirSync(SAFE_INSTALL_DIR, { recursive: true });
  }
  
  // Check if already exists
  if (fs.existsSync(targetPath)) {
    if (backup) {
      // Create backup with unique name
      const timestamp = Date.now();
      const random = crypto.randomBytes(4).toString('hex');
      const backupPath = path.join(SAFE_INSTALL_DIR, `${skillName}.backup-${timestamp}-${random}`);
      
      console.error(`⚠️  Skill ${skillName} already exists. Creating backup...`);
      fs.renameSync(targetPath, backupPath);
      
      // Keep only last 5 backups
      try {
        const backups = fs.readdirSync(SAFE_INSTALL_DIR)
          .filter(f => f.startsWith(`${skillName}.backup-`))
          .map(f => ({
            name: f,
            path: path.join(SAFE_INSTALL_DIR, f),
            mtime: fs.statSync(path.join(SAFE_INSTALL_DIR, f)).mtime,
          }))
          .sort((a, b) => b.mtime - a.mtime);
        
        for (const old of backups.slice(5)) {
          fs.rmSync(old.path, { recursive: true, force: true });
        }
      } catch (e) {
        // Ignore backup cleanup errors
      }
    } else {
      // Remove existing without backup
      fs.rmSync(targetPath, { recursive: true, force: true });
    }
  }
  
  // Move from quarantine to skills directory (atomic on same filesystem)
  fs.renameSync(skillPath, targetPath);
  
  // Verify installation
  if (!fs.existsSync(targetPath)) {
    throw new Error('Installation verification failed');
  }
  
  console.error(`✅ Installed to: ${targetPath}`);
  return targetPath;
}

// Main safe download function
async function safeDownload(source, options = {}) {
  const { 
    autoInstall = false, 
    riskThreshold = 39, 
    dryRun = false,
    verbose = false,
  } = options;
  
  let quarantinePath = null;
  
  console.error('🛡️  Bomb-Dog-Sniff Safe Download');
  console.error('====================================\n');
  
  try {
    // Step 1: Create secure quarantine directory
    quarantinePath = getQuarantinePath();
    fs.mkdirSync(quarantinePath, { recursive: true, mode: 0o700 }); // Restrictive permissions
    
    // Step 2: Download to quarantine
    const downloadedPath = await downloadSkill(source, quarantinePath);
    const skillName = path.basename(downloadedPath);
    
    console.error(`📦 Downloaded to quarantine: ${downloadedPath}\n`);
    
    // Step 3: Scan
    console.error('🔍 Scanning for malicious patterns...\n');
    const scanResult = scanSkill(downloadedPath, { verbose });
    
    // Display scan results
    console.error(`Risk Score: ${scanResult.riskScore}/100`);
    console.error(`Risk Level: ${scanResult.riskLevel}`);
    console.error(`Files Scanned: ${scanResult.stats.scannedFiles}`);
    console.error(`Findings: ${scanResult.stats.totalFindings}\n`);
    
    if (scanResult.findings.length > 0 && verbose) {
      console.error('--- Findings ---');
      scanResult.findings.slice(0, 10).forEach(f => {
        console.error(`[${f.severity}] ${f.category}: ${f.file}:${f.line}`);
        console.error(`    ${f.description}`);
      });
      if (scanResult.findings.length > 10) {
        console.error(`    ... and ${scanResult.findings.length - 10} more`);
      }
      console.error('');
    }
    
    // Step 4: Decision
    if (scanResult.riskScore > riskThreshold) {
      console.error(`❌ BLOCKED: Risk score ${scanResult.riskScore} exceeds threshold (${riskThreshold})`);
      console.error(`Recommendation: ${scanResult.recommendation}\n`);
      
      // Clean up quarantine
      cleanQuarantine(quarantinePath);
      
      return {
        success: false,
        installed: false,
        reason: 'RISK_THRESHOLD_EXCEEDED',
        scanResult,
        scanId: scanResult.scanId,
      };
    }
    
    console.error(`✅ PASSED: Risk score ${scanResult.riskScore} is within safe threshold\n`);
    
    // Step 5: Install if requested
    if (autoInstall) {
      console.error('📥 Installing skill...');
      const installedPath = await installSkill(downloadedPath, skillName, { dryRun });
      
      // Clean up quarantine (only if not dry-run, since install moves the directory)
      if (!dryRun) {
        cleanQuarantine(quarantinePath);
      }
      
      return {
        success: true,
        installed: true,
        installedPath,
        scanResult,
        scanId: scanResult.scanId,
      };
    }
    
    // Return scan result for manual review
    return {
      success: true,
      installed: false,
      quarantinePath: downloadedPath,
      message: 'Skill is safe. Review quarantined copy and install manually.',
      scanResult,
      scanId: scanResult.scanId,
    };
    
  } catch (err) {
    // Clean up on error
    cleanQuarantine(quarantinePath);
    throw err;
  }
}

// CLI entry point
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    console.log(`
Usage: node safe-download.js [options] <source>

Source:
  - GitHub URL: https://github.com/user/skill-repo
  - Clawhub name: skill-name
  - Local path: ./path/to/skill

Options:
  -i, --install       Auto-install if scan passes
  -t, --threshold N   Set risk threshold (default: 39)
  -d, --dry-run       Scan only, don't install
  -v, --verbose       Show all findings
  -j, --json          Output JSON only
  -h, --help          Show this help

Examples:
  node safe-download.js -i https://github.com/user/my-skill
  node safe-download.js -i -t 20 cool-skill
  node safe-download.js -d ./unverified-skill
  node safe-download.js -i -j cool-skill > result.json
`);
    process.exitCode = 0;
    return;
  }
  
  // Parse arguments
  const options = {
    autoInstall: false,
    riskThreshold: 39,
    dryRun: false,
    verbose: false,
    json: false,
  };
  
  let source = null;
  
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    
    if (arg === '--install' || arg === '-i') {
      options.autoInstall = true;
    } else if (arg === '--dry-run' || arg === '-d') {
      options.dryRun = true;
    } else if (arg === '--verbose' || arg === '-v') {
      options.verbose = true;
    } else if (arg === '--json' || arg === '-j') {
      options.json = true;
    } else if ((arg === '--threshold' || arg === '-t') && args[i + 1]) {
      options.riskThreshold = parseInt(args[i + 1], 10);
      if (isNaN(options.riskThreshold)) {
        console.error('Error: Invalid threshold value');
        process.exitCode = 1;
        return;
      }
      i++;
    } else if (!arg.startsWith('-') && !source) {
      source = arg;
    }
  }
  
  if (!source) {
    console.error('Error: No source specified. Use --help for usage.');
    process.exitCode = 1;
    return;
  }
  
  try {
    const result = await safeDownload(source, options);
    
    if (options.json) {
      console.log(JSON.stringify(result, null, 2));
    } else if (!result.installed && result.success) {
      console.error(`\n📋 ${result.message}`);
      console.error(`   Location: ${result.quarantinePath}`);
    }
    
    // Set exit code
    if (!result.success) {
      process.exitCode = 2;
    } else if (options.autoInstall && !result.installed) {
      process.exitCode = 1;
    } else {
      process.exitCode = 0;
    }
  } catch (err) {
    console.error(`\n❌ Error: ${err.message}`);
    process.exitCode = 1;
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = { 
  safeDownload, 
  downloadSkill,
  downloadFromGitHub,
  downloadFromClawhub,
  copyLocalSkill,
  installSkill,
  validateUrl,
  sanitizePath,
};
