#!/usr/bin/env node

/**
 * Snippet Library Configuration
 * 
 * Manages snippet storage location configuration.
 * Default: ~/.local/share/ghost-snippets/ (outside repository)
 * 
 * Security: Keeps user content isolated from repository to prevent
 * accidental commits, even with .gitignore in place.
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import readline from 'readline';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

/**
 * Get default snippet library location (outside repository)
 * @returns {string} Default library path
 */
export function getDefaultLibraryPath() {
  const home = process.env.HOME || process.env.USERPROFILE;
  
  // Platform-specific defaults
  if (process.platform === 'darwin' || process.platform === 'linux') {
    // Unix-like: ~/.local/share/ghost-snippets/
    return path.join(home, '.local', 'share', 'ghost-snippets');
  } else if (process.platform === 'win32') {
    // Windows: %APPDATA%\ghost-snippets\
    return path.join(process.env.APPDATA || home, 'ghost-snippets');
  }
  
  // Fallback
  return path.join(home, '.ghost-snippets');
}

/**
 * Get configured snippet library location
 * Priority: ENV var > config file > default
 * @returns {string} Library path
 */
export function getLibraryPath() {
  // 1. Check environment variable
  if (process.env.GHOST_SNIPPETS_DIR) {
    return process.env.GHOST_SNIPPETS_DIR;
  }
  
  // 2. Check config file
  const configPath = getConfigPath();
  if (fs.existsSync(configPath)) {
    try {
      const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      if (config.libraryPath) {
        return config.libraryPath;
      }
    } catch (err) {
      console.error(`Warning: Could not read snippet config: ${err.message}`);
    }
  }
  
  // 3. Use default (outside repository)
  return getDefaultLibraryPath();
}

/**
 * Get config file path
 * @returns {string} Config file path
 */
export function getConfigPath() {
  const home = process.env.HOME || process.env.USERPROFILE;
  return path.join(home, '.config', 'ghost', 'snippets-config.json');
}

/**
 * Get examples directory (always in repository)
 * @returns {string} Examples path
 */
export function getExamplesPath() {
  return path.join(__dirname, 'examples');
}

/**
 * Initialize snippet library directory
 * Creates directory if it doesn't exist
 * @param {string} libraryPath - Library directory path
 */
export function initializeLibrary(libraryPath) {
  if (!fs.existsSync(libraryPath)) {
    fs.mkdirSync(libraryPath, { recursive: true, mode: 0o700 }); // Owner-only permissions
    console.log(`✅ Created snippet library: ${libraryPath}`);
  }
}

/**
 * Save library path configuration
 * @param {string} libraryPath - Library directory path
 */
export function saveConfig(libraryPath) {
  const configPath = getConfigPath();
  const configDir = path.dirname(configPath);
  
  if (!fs.existsSync(configDir)) {
    fs.mkdirSync(configDir, { recursive: true, mode: 0o700 });
  }
  
  const config = {
    libraryPath,
    createdAt: new Date().toISOString(),
    version: '0.1.0'
  };
  
  fs.writeFileSync(configPath, JSON.stringify(config, null, 2), { mode: 0o600 });
  console.log(`✅ Saved snippet config: ${configPath}`);
}

/**
 * Check if old library exists (in repository)
 * @returns {Object} Migration info
 */
export function checkOldLibrary() {
  const oldLibraryPath = path.join(__dirname, 'library');
  
  if (!fs.existsSync(oldLibraryPath)) {
    return { exists: false };
  }
  
  const files = fs.readdirSync(oldLibraryPath)
    .filter(f => f.endsWith('.json') && f !== '.gitkeep');
  
  return {
    exists: files.length > 0,
    path: oldLibraryPath,
    count: files.length,
    files
  };
}

/**
 * Migrate snippets from old location to new location
 * @param {string} newLibraryPath - New library path
 * @returns {number} Number of snippets migrated
 */
export function migrateSnippets(newLibraryPath) {
  const oldInfo = checkOldLibrary();
  
  if (!oldInfo.exists) {
    return 0;
  }
  
  console.log(`\n📦 Found ${oldInfo.count} snippets in old location`);
  console.log(`   Migrating to: ${newLibraryPath}\n`);
  
  initializeLibrary(newLibraryPath);
  
  let migrated = 0;
  for (const file of oldInfo.files) {
    const oldPath = path.join(oldInfo.path, file);
    const newPath = path.join(newLibraryPath, file);
    
    try {
      // Copy file
      fs.copyFileSync(oldPath, newPath);
      fs.chmodSync(newPath, 0o600); // Owner-only permissions
      console.log(`   ✅ Migrated: ${file}`);
      migrated++;
    } catch (err) {
      console.error(`   ❌ Failed to migrate ${file}: ${err.message}`);
    }
  }
  
  console.log(`\n✅ Migrated ${migrated} snippets`);
  console.log(`   Old location: ${oldInfo.path}`);
  console.log(`   New location: ${newLibraryPath}\n`);
  
  return migrated;
}

/**
 * Interactive setup wizard
 * Prompts user to configure snippet library location
 * @returns {Promise<string>} Configured library path
 */
export async function setupWizard() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  
  const question = (query) => new Promise((resolve) => rl.question(query, resolve));
  
  console.log('\n╔════════════════════════════════════════════════════════╗');
  console.log('║       Ghost Snippet Library - First Time Setup        ║');
  console.log('╚════════════════════════════════════════════════════════╝\n');
  
  const defaultPath = getDefaultLibraryPath();
  const oldInfo = checkOldLibrary();
  
  if (oldInfo.exists) {
    console.log(`⚠️  Found ${oldInfo.count} snippets in old location (inside repository)`);
    console.log(`   ${oldInfo.path}\n`);
    console.log('🔒 For better security, snippets should be stored OUTSIDE the repository.');
    console.log('   This prevents accidental commits and keeps your content isolated.\n');
  } else {
    console.log('🔒 Snippets will be stored OUTSIDE the repository for security.');
    console.log('   This prevents accidental commits and keeps your content isolated.\n');
  }
  
  console.log(`📁 Recommended location:\n   ${defaultPath}\n`);
  
  const answer = await question('Use recommended location? (Y/n): ');
  
  let libraryPath;
  
  if (answer.toLowerCase() === 'n') {
    const customPath = await question('Enter custom path: ');
    libraryPath = customPath.trim() || defaultPath;
  } else {
    libraryPath = defaultPath;
  }
  
  rl.close();
  
  // Expand ~ to home directory
  if (libraryPath.startsWith('~')) {
    const home = process.env.HOME || process.env.USERPROFILE;
    libraryPath = path.join(home, libraryPath.slice(1));
  }
  
  // Initialize library
  initializeLibrary(libraryPath);
  
  // Migrate old snippets if they exist
  if (oldInfo.exists) {
    const migrated = migrateSnippets(libraryPath);
    
    if (migrated > 0) {
      console.log('💡 Old snippets have been copied (not moved).');
      console.log('   You can manually delete the old files when ready:\n');
      console.log(`   rm ${oldInfo.path}/*.json\n`);
    }
  }
  
  // Save configuration
  saveConfig(libraryPath);
  
  console.log('✅ Snippet library configured!\n');
  console.log(`📂 Location: ${libraryPath}`);
  console.log(`⚙️  Config:   ${getConfigPath()}\n`);
  console.log('💡 To change location later:');
  console.log(`   export GHOST_SNIPPETS_DIR="/path/to/snippets"\n`);
  
  return libraryPath;
}

/**
 * Ensure library is configured and initialized
 * Runs setup wizard if needed
 * @param {boolean} interactive - Allow interactive setup
 * @returns {Promise<string>} Library path
 */
export async function ensureConfigured(interactive = true) {
  let libraryPath = getLibraryPath();
  
  // If using default and it doesn't exist, run setup wizard
  if (libraryPath === getDefaultLibraryPath() && !fs.existsSync(getConfigPath())) {
    const oldInfo = checkOldLibrary();
    
    // If old library exists or we're interactive, run setup
    if (interactive && (oldInfo.exists || process.stdout.isTTY)) {
      libraryPath = await setupWizard();
    } else {
      // Non-interactive: use default and migrate silently
      initializeLibrary(libraryPath);
      if (oldInfo.exists) {
        migrateSnippets(libraryPath);
      }
      saveConfig(libraryPath);
    }
  } else {
    // Library configured, ensure it exists
    initializeLibrary(libraryPath);
  }
  
  return libraryPath;
}
