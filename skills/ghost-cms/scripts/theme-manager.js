#!/usr/bin/env node

/**
 * Ghost Theme Manager
 * Upload, activate, list, download, and delete Ghost themes
 */

import { readFileSync, createWriteStream } from 'fs';
import { basename, resolve, dirname, extname } from 'path';
import https from 'https';
import FormData from 'form-data';
import jwt from 'jsonwebtoken';

// Load credentials
const configDir = process.env.HOME + '/.config/ghost';
const apiKey = (process.env.GHOST_ADMIN_KEY || readFileSync(`${configDir}/api_key`, 'utf8')).trim();
const apiUrl = (process.env.GHOST_API_URL || readFileSync(`${configDir}/api_url`, 'utf8')).trim();

// Split key
const [keyId, keySecret] = apiKey.split(':');

// Generate JWT token
function generateToken() {
  const payload = {
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + 300,
    aud: '/admin/'
  };
  return jwt.sign(payload, Buffer.from(keySecret, 'hex'), {
    algorithm: 'HS256',
    keyid: keyId,
    header: { kid: keyId }
  });
}

// Make API request
function ghostApi(endpoint, method = 'GET', data = null) {
  const token = generateToken();
  const url = new URL(`${apiUrl}/ghost/api/admin${endpoint}`);
  
  const options = {
    method,
    headers: {
      'Authorization': `Ghost ${token}`,
      'Content-Type': 'application/json',
      'Accept-Version': 'v5.0'
    }
  };
  
  return new Promise((resolve, reject) => {
    const req = https.request(url, options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        if (res.statusCode === 204) {
          resolve({ statusCode: 204, message: 'Success (No Content)' });
          return;
        }
        try {
          resolve(JSON.parse(body));
        } catch (e) {
          reject(new Error(`Invalid JSON: ${body}`));
        }
      });
    });
    
    req.on('error', reject);
    
    if (data) {
      req.write(JSON.stringify(data));
    }
    
    req.end();
  });
}

// Upload theme (multipart/form-data)
function uploadTheme(zipPath, activate = false) {
  const token = generateToken();
  const url = new URL(`${apiUrl}/ghost/api/admin/themes/upload/`);
  
  const form = new FormData();
  form.append('file', readFileSync(zipPath), {
    filename: basename(zipPath),
    contentType: 'application/zip'
  });
  
  if (activate) {
    form.append('activate', 'true');
  }
  
  return new Promise((resolve, reject) => {
    const req = https.request(url, {
      method: 'POST',
      headers: {
        ...form.getHeaders(),
        'Authorization': `Ghost ${token}`,
        'Accept-Version': 'v5.0'
      }
    }, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(body));
        } catch (e) {
          reject(new Error(`Invalid JSON: ${body}`));
        }
      });
    });
    
    req.on('error', reject);
    form.pipe(req);
  });
}

// Validate theme name to prevent path traversal in API endpoints
function validateThemeName(themeName) {
  if (!themeName || typeof themeName !== 'string') {
    throw new Error('Theme name is required and must be a string');
  }
  
  // Prevent path traversal sequences
  if (themeName.includes('..') || themeName.includes('/') || themeName.includes('\\')) {
    throw new Error('Invalid theme name: path traversal not allowed');
  }
  
  // Prevent absolute paths
  if (themeName.startsWith('/')) {
    throw new Error('Invalid theme name: absolute paths not allowed');
  }
  
  // Only allow alphanumeric, hyphens, underscores, dots
  const validNameRegex = /^[\w\-\.]+$/;
  if (!validNameRegex.test(themeName)) {
    throw new Error('Invalid theme name: only alphanumeric, hyphens, underscores, and dots allowed');
  }
  
  // Validate length
  if (themeName.length === 0 || themeName.length > 100) {
    throw new Error('Invalid theme name: must be 1-100 characters');
  }
  
  return themeName;
}

// Validate output path to prevent arbitrary file write
function validateOutputPath(outputPath) {
  if (!outputPath) {
    throw new Error('Output path is required');
  }
  
  // Resolve to absolute path
  const absolutePath = resolve(outputPath);
  
  // Get the directory part
  const outputDir = dirname(absolutePath);
  
  // Ensure output directory is within current working directory
  // This prevents writing to system directories like /etc, ~/.ssh, etc.
  const cwd = process.cwd();
  const resolvedOutputDir = resolve(outputDir);
  
  if (!resolvedOutputDir.startsWith(cwd)) {
    throw new Error(`Invalid output path: must be within current directory (${cwd})`);
  }
  
  // Prevent path traversal in filename
  const filename = basename(absolutePath);
  if (filename.includes('..') || filename.includes('/') || filename.includes('\\')) {
    throw new Error('Invalid filename: path traversal not allowed');
  }
  
  // Require .zip extension
  const ext = extname(filename).toLowerCase();
  if (ext !== '.zip') {
    throw new Error('Invalid filename: must have .zip extension');
  }
  
  // Additional safety: filename must not be empty after removing extension
  const nameWithoutExt = basename(filename, ext);
  if (!nameWithoutExt || nameWithoutExt.length === 0) {
    throw new Error('Invalid filename: name cannot be empty');
  }
  
  return absolutePath;
}

// Download theme
function downloadTheme(themeName, outputPath) {
  // CRITICAL: Validate inputs to prevent attacks
  const validatedThemeName = validateThemeName(themeName);
  const validatedPath = validateOutputPath(outputPath);
  
  const token = generateToken();
  const url = new URL(`${apiUrl}/ghost/api/admin/themes/${validatedThemeName}/download/`);
  
  return new Promise((resolve, reject) => {
    const req = https.request(url, {
      method: 'GET',
      headers: {
        'Authorization': `Ghost ${token}`,
        'Accept-Version': 'v5.0'
      }
    }, (res) => {
      if (res.statusCode !== 200) {
        let body = '';
        res.on('data', chunk => body += chunk);
        res.on('end', () => reject(new Error(`Download failed: ${body}`)));
        return;
      }
      
      const fileStream = createWriteStream(validatedPath);
      res.pipe(fileStream);
      
      fileStream.on('finish', () => {
        fileStream.close();
        resolve({ success: true, path: validatedPath });
      });
      
      fileStream.on('error', reject);
    });
    
    req.on('error', reject);
    req.end();
  });
}

// Commands
const commands = {
  async list() {
    const result = await ghostApi('/themes/');
    if (result.themes) {
      console.log('📦 Installed Themes:\n');
      result.themes.forEach(theme => {
        const active = theme.active ? '✅ ACTIVE' : '  ';
        const version = theme.package?.version || 'unknown';
        console.log(`${active} ${theme.name} (v${version})`);
        if (theme.warnings?.length > 0) {
          theme.warnings.forEach(w => console.log(`   ⚠️  ${w}`));
        }
      });
      
      // Show active theme at bottom
      const activeTheme = result.themes.find(t => t.active);
      if (activeTheme) {
        console.log(`\n✨ Current active theme: ${activeTheme.name}`);
      }
    }
    return result;
  },
  
  async upload(zipPath, options = {}) {
    console.log(`📤 Uploading theme: ${basename(zipPath)}...`);
    const result = await uploadTheme(zipPath, options.activate);
    
    if (result.themes) {
      const theme = result.themes[0];
      console.log(`✅ Theme uploaded: ${theme.name} (v${theme.package?.version})`);
      
      if (theme.warnings?.length > 0) {
        console.log('\n⚠️  Warnings:');
        theme.warnings.forEach(w => console.log(`   - ${w}`));
      }
      
      if (options.activate) {
        console.log(`✨ Theme activated: ${theme.name}`);
      } else {
        console.log(`\n💡 Activate with: node theme-manager.js activate ${theme.name}`);
      }
    } else if (result.errors) {
      console.error('❌ Upload failed:');
      result.errors.forEach(e => {
        console.error(`   ${e.message}`);
        if (e.context) console.error(`   ${e.context}`);
      });
    }
    
    return result;
  },
  
  async activate(themeName) {
    // CRITICAL: Validate theme name to prevent path traversal in API endpoint
    const validatedThemeName = validateThemeName(themeName);
    console.log(`✨ Activating theme: ${validatedThemeName}...`);
    const result = await ghostApi(`/themes/${validatedThemeName}/activate/`, 'PUT');
    
    if (result.themes) {
      const theme = result.themes[0];
      console.log(`✅ Theme activated: ${theme.name} (v${theme.package?.version})`);
      console.log('\n🌐 Your site appearance has been updated!');
    } else if (result.errors) {
      console.error('❌ Activation failed:');
      result.errors.forEach(e => console.error(`   ${e.message}`));
    }
    
    return result;
  },
  
  async delete(themeName) {
    // CRITICAL: Validate theme name to prevent path traversal in API endpoint
    const validatedThemeName = validateThemeName(themeName);
    console.log(`🗑️  Deleting theme: ${validatedThemeName}...`);
    
    // Check if active first
    const list = await ghostApi('/themes/');
    const theme = list.themes?.find(t => t.name === validatedThemeName);
    
    if (!theme) {
      console.error(`❌ Theme not found: ${validatedThemeName}`);
      return;
    }
    
    if (theme.active) {
      console.error(`❌ Cannot delete active theme: ${validatedThemeName}`);
      console.error('   Activate a different theme first:');
      list.themes.filter(t => !t.active).forEach(t => {
        console.error(`   node theme-manager.js activate ${t.name}`);
      });
      return;
    }
    
    const result = await ghostApi(`/themes/${validatedThemeName}/`, 'DELETE');
    
    if (result.statusCode === 204) {
      console.log(`✅ Theme deleted: ${validatedThemeName}`);
    } else if (result.errors) {
      console.error('❌ Deletion failed:');
      result.errors.forEach(e => console.error(`   ${e.message}`));
    }
    
    return result;
  },
  
  async download(themeName, outputPath) {
    console.log(`📥 Downloading theme: ${themeName}...`);
    const result = await downloadTheme(themeName, outputPath);
    
    if (result.success) {
      console.log(`✅ Theme downloaded: ${result.path}`);
    }
    
    return result;
  },
  
  async active() {
    const result = await ghostApi('/themes/');
    const activeTheme = result.themes?.find(t => t.active);
    
    if (activeTheme) {
      console.log(`✨ Active theme: ${activeTheme.name} (v${activeTheme.package?.version})`);
      return activeTheme;
    } else {
      console.log('❓ No active theme found');
      return null;
    }
  }
};

// CLI
const [,, command, ...args] = process.argv;

if (!command || command === 'help') {
  console.log(`
Ghost Theme Manager

Usage:
  node theme-manager.js <command> [arguments]

Commands:
  list                              List all installed themes
  upload <zip-path> [--activate]    Upload theme ZIP (optionally activate)
  activate <theme-name>             Activate installed theme
  delete <theme-name>               Delete theme (cannot delete active theme)
  download <theme-name> <output>    Download theme as ZIP
  active                            Show currently active theme
  help                              Show this help

Examples:
  node theme-manager.js list
  node theme-manager.js upload ./my-theme.zip
  node theme-manager.js upload ./my-theme.zip --activate
  node theme-manager.js activate casper
  node theme-manager.js download my-theme backup.zip
  node theme-manager.js delete old-theme
  node theme-manager.js active

Notes:
  - Themes must be valid Ghost theme ZIP files
  - Active theme cannot be deleted (switch first)
  - Theme changes take effect immediately
  - See references/themes.md for theme structure and best practices
`);
  process.exit(0);
}

// Execute command
if (!commands[command]) {
  console.error(`❌ Unknown command: ${command}`);
  console.error('Run: node theme-manager.js help');
  process.exit(1);
}

const hasActivateFlag = args.includes('--activate');
const cleanArgs = args.filter(a => a !== '--activate');

commands[command](...cleanArgs, hasActivateFlag ? { activate: true } : {})
  .then(() => process.exit(0))
  .catch(err => {
    console.error('❌ Error:', err.message);
    process.exit(1);
  });
