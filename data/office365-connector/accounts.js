#!/usr/bin/env node
/**
 * Office 365 Multi-Account Management
 * Handles configuration and switching between multiple Microsoft 365 accounts
 */

const fs = require('fs');
const path = require('path');

const ACCOUNTS_CONFIG_PATH = path.join(process.env.HOME, '.openclaw', 'auth', 'office365-accounts.json');
const ACCOUNTS_DIR = path.join(process.env.HOME, '.openclaw', 'auth', 'office365');

// Ensure directories exist
function ensureDirectories() {
  const authDir = path.dirname(ACCOUNTS_CONFIG_PATH);
  if (!fs.existsSync(authDir)) {
    fs.mkdirSync(authDir, { recursive: true, mode: 0o700 });
  }
  if (!fs.existsSync(ACCOUNTS_DIR)) {
    fs.mkdirSync(ACCOUNTS_DIR, { recursive: true, mode: 0o700 });
  }
}

/**
 * Load accounts configuration
 */
function loadAccounts() {
  ensureDirectories();
  
  if (!fs.existsSync(ACCOUNTS_CONFIG_PATH)) {
    return {
      default: null,
      accounts: {}
    };
  }
  
  try {
    const data = fs.readFileSync(ACCOUNTS_CONFIG_PATH, 'utf8');
    return JSON.parse(data);
  } catch (e) {
    console.error('Failed to load accounts config:', e.message);
    return {
      default: null,
      accounts: {}
    };
  }
}

/**
 * Save accounts configuration
 */
function saveAccounts(config) {
  ensureDirectories();
  fs.writeFileSync(ACCOUNTS_CONFIG_PATH, JSON.stringify(config, null, 2), { mode: 0o600 });
}

/**
 * Get account token path
 */
function getAccountTokenPath(accountName) {
  return path.join(ACCOUNTS_DIR, `${accountName}.json`);
}

/**
 * Add or update account
 */
function addAccount(name, tenantId, clientId, clientSecret, options = {}) {
  const config = loadAccounts();
  
  config.accounts[name] = {
    tenantId,
    clientId,
    clientSecret,
    email: options.email || null,
    description: options.description || null,
    addedAt: config.accounts[name]?.addedAt || new Date().toISOString()
  };
  
  // Set as default if it's the first account
  if (!config.default) {
    config.default = name;
  }
  
  saveAccounts(config);
  return config.accounts[name];
}

/**
 * Remove account
 */
function removeAccount(name) {
  const config = loadAccounts();
  
  if (!config.accounts[name]) {
    throw new Error(`Account "${name}" not found`);
  }
  
  // Remove token file
  const tokenPath = getAccountTokenPath(name);
  if (fs.existsSync(tokenPath)) {
    fs.unlinkSync(tokenPath);
  }
  
  // Remove from config
  delete config.accounts[name];
  
  // Clear default if it was this account
  if (config.default === name) {
    config.default = Object.keys(config.accounts)[0] || null;
  }
  
  saveAccounts(config);
}

/**
 * Set default account
 */
function setDefault(name) {
  const config = loadAccounts();
  
  if (!config.accounts[name]) {
    throw new Error(`Account "${name}" not found`);
  }
  
  config.default = name;
  saveAccounts(config);
}

/**
 * Get account details
 */
function getAccount(name) {
  const config = loadAccounts();
  
  // If no name provided, use default
  if (!name) {
    name = config.default;
  }
  
  if (!name) {
    throw new Error('No account specified and no default account set');
  }
  
  const account = config.accounts[name];
  if (!account) {
    throw new Error(`Account "${name}" not found`);
  }
  
  return {
    name,
    ...account,
    tokenPath: getAccountTokenPath(name)
  };
}

/**
 * List all accounts
 */
function listAccounts() {
  const config = loadAccounts();
  return {
    default: config.default,
    accounts: Object.keys(config.accounts).map(name => ({
      name,
      isDefault: name === config.default,
      ...config.accounts[name]
    }))
  };
}

/**
 * Import from legacy single-account setup
 */
function importLegacy() {
  const legacyTokenPath = path.join(process.env.HOME, '.openclaw', 'auth', 'microsoft-graph.json');
  
  if (!fs.existsSync(legacyTokenPath)) {
    return null;
  }
  
  const config = loadAccounts();
  
  // Check if already imported
  if (Object.keys(config.accounts).length > 0) {
    return null;
  }
  
  // Get credentials from environment
  const tenantId = process.env.AZURE_TENANT_ID;
  const clientId = process.env.AZURE_CLIENT_ID;
  const clientSecret = process.env.AZURE_CLIENT_SECRET;
  
  if (!tenantId || !clientId || !clientSecret) {
    console.log('⚠️  Legacy token file found but no credentials in environment');
    return null;
  }
  
  // Add as "primary" account
  addAccount('primary', tenantId, clientId, clientSecret, {
    description: 'Imported from legacy setup'
  });
  
  // Move token file
  const newTokenPath = getAccountTokenPath('primary');
  fs.copyFileSync(legacyTokenPath, newTokenPath);
  fs.unlinkSync(legacyTokenPath);
  
  console.log('✅ Imported legacy account as "primary"');
  return 'primary';
}

// CLI usage
if (require.main === module) {
  const command = process.argv[2];
  const args = process.argv.slice(3);
  
  try {
    if (command === 'list') {
      const result = listAccounts();
      console.log('📧 Office 365 Accounts:\n');
      
      if (result.accounts.length === 0) {
        console.log('No accounts configured.');
        console.log('\nAdd an account with:');
        console.log('  node accounts.js add <name> <tenant-id> <client-id> <client-secret>');
      } else {
        result.accounts.forEach(acc => {
          const defaultMarker = acc.isDefault ? ' [DEFAULT]' : '';
          console.log(`${acc.name}${defaultMarker}`);
          if (acc.email) console.log(`  Email: ${acc.email}`);
          if (acc.description) console.log(`  Description: ${acc.description}`);
          console.log(`  Added: ${new Date(acc.addedAt).toLocaleDateString()}`);
          console.log('');
        });
      }
      
    } else if (command === 'add') {
      if (args.length < 4) {
        console.log('Usage: node accounts.js add <name> <tenant-id> <client-id> <client-secret> [email] [description]');
        process.exit(1);
      }
      
      const [name, tenantId, clientId, clientSecret, email, description] = args;
      addAccount(name, tenantId, clientId, clientSecret, { email, description });
      console.log(`✅ Added account "${name}"`);
      
    } else if (command === 'remove') {
      if (args.length < 1) {
        console.log('Usage: node accounts.js remove <name>');
        process.exit(1);
      }
      
      removeAccount(args[0]);
      console.log(`✅ Removed account "${args[0]}"`);
      
    } else if (command === 'default') {
      if (args.length < 1) {
        console.log('Usage: node accounts.js default <name>');
        process.exit(1);
      }
      
      setDefault(args[0]);
      console.log(`✅ Set "${args[0]}" as default account`);
      
    } else if (command === 'import-legacy') {
      const result = importLegacy();
      if (!result) {
        console.log('No legacy setup found or already imported');
      }
      
    } else {
      console.log('Office 365 Multi-Account Management\n');
      console.log('Commands:');
      console.log('  list                      - List all accounts');
      console.log('  add <name> ...            - Add new account');
      console.log('  remove <name>             - Remove account');
      console.log('  default <name>            - Set default account');
      console.log('  import-legacy             - Import from single-account setup');
      process.exit(1);
    }
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

module.exports = {
  loadAccounts,
  saveAccounts,
  addAccount,
  removeAccount,
  setDefault,
  getAccount,
  listAccounts,
  getAccountTokenPath,
  importLegacy
};
