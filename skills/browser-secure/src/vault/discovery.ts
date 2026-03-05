import { execSync } from 'child_process';
import * as readline from 'readline';
import { VaultCredentials } from './index.js';
import { SiteConfig, loadConfig, saveConfig } from '../config/loader.js';

interface BitwardenItem {
  id: string;
  name: string;
  login?: {
    username?: string;
    password?: string;
  };
  fields?: Array<{
    name: string;
    value: string;
    type: number;
  }>;
  notes?: string;
}

interface OnePasswordItem {
  id: string;
  title: string;
  vault: {
    id: string;
    name: string;
  };
  urls?: Array<{
    primary: boolean;
    href: string;
  }>;
  fields?: Array<{
    id: string;
    label: string;
    value?: string;
  }>;
}

/**
 * Extract domain from URL for matching
 */
export function extractDomain(url: string): string {
  try {
    const urlObj = new URL(url);
    // Remove www. and extract base domain
    return urlObj.hostname.replace(/^www\./, '').toLowerCase();
  } catch {
    // If URL parsing fails, try to extract domain manually
    const match = url.match(/(?:https?:\/\/)?(?:www\.)?([^\/]+)/);
    return match ? match[1].toLowerCase() : url.toLowerCase();
  }
}

/**
 * Extract base name for site key (e.g., "neilpatel" from "app.neilpatel.com")
 */
export function extractSiteKey(domain: string): string {
  const parts = domain.split('.');
  // Get the main domain (e.g., "neilpatel" from "app.neilpatel.com")
  if (parts.length >= 2) {
    return parts[parts.length - 2];
  }
  return domain;
}

/**
 * Check if Bitwarden CLI is available and logged in
 */
export function isBitwardenAvailable(): boolean {
  try {
    execSync('which bw', { stdio: 'ignore' });
    // Check if vault is unlocked
    execSync('bw status', { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}

/**
 * Check if 1Password CLI is available
 */
export function is1PasswordAvailable(): boolean {
  try {
    execSync('which op', { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}

/**
 * Search Bitwarden for items matching a domain
 */
export function searchBitwardenItems(domain: string): BitwardenItem[] {
  try {
    const siteKey = extractSiteKey(domain);
    
    // Search all items
    const allItems: BitwardenItem[] = JSON.parse(
      execSync('bw list items', { encoding: 'utf-8', timeout: 10000 })
    );
    
    // Filter items that match the domain
    const results = allItems.filter(item => {
      const name = item.name.toLowerCase();
      const notes = (item.notes || '').toLowerCase();
      
      return name.includes(siteKey) || 
             name.includes(domain.replace('.', '')) ||
             domain.includes(name.replace(/\s+/g, '').toLowerCase()) ||
             notes.includes(domain);
    });
    
    return results.slice(0, 10); // Limit to 10 results
  } catch (e) {
    console.error('Failed to search Bitwarden:', e);
    return [];
  }
}

/**
 * Search 1Password for items matching a domain
 */
export function search1PasswordItems(domain: string): OnePasswordItem[] {
  try {
    // Search by domain in URLs and titles
    const siteKey = extractSiteKey(domain);
    
    // Try searching by URL first
    let results: OnePasswordItem[] = [];
    
    try {
      const urlResults = JSON.parse(
        execSync(`op item list --categories login --format json`, { encoding: 'utf-8', timeout: 10000 })
      ) as OnePasswordItem[];
      
      // Filter items that match the domain
      results = urlResults.filter(item => {
        const title = item.title.toLowerCase();
        const vaultName = item.vault.name.toLowerCase();
        
        // Check if domain is in title or vault name
        return title.includes(siteKey) || 
               title.includes(domain.replace('.', '')) ||
               domain.includes(title.replace(/\s+/g, '').toLowerCase());
      });
    } catch (e) {
      // If URL search fails, fall back to general search
    }
    
    // If no results, try a broader search
    if (results.length === 0) {
      try {
        const allItems = JSON.parse(
          execSync(`op item list --categories login --format json`, { encoding: 'utf-8', timeout: 10000 })
        ) as OnePasswordItem[];
        
        // Fuzzy match on title
        results = allItems.filter(item => {
          const title = item.title.toLowerCase();
          return title.includes(siteKey.substring(0, 4)); // Match first 4 chars
        });
      } catch (e) {
        // Ignore errors
      }
    }
    
    return results.slice(0, 10); // Limit to 10 results
  } catch (e) {
    console.error('Failed to search 1Password:', e);
    return [];
  }
}

/**
 * Get detailed fields for a 1Password item
 */
export function get1PasswordItemFields(itemId: string): Array<{label: string, value?: string}> {
  try {
    const item = JSON.parse(
      execSync(`op item get ${itemId} --format json`, { encoding: 'utf-8', timeout: 10000 })
    ) as OnePasswordItem;
    
    return item.fields || [];
  } catch (e) {
    return [];
  }
}

/**
 * Prompt user for input
 */
function promptUser(question: string): Promise<string> {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

/**
 * Interactive credential selection - supports Bitwarden (default) and 1Password
 */
export async function interactiveCredentialDiscovery(
  url: string,
  domain: string
): Promise<{ credentials: VaultCredentials; siteConfig: SiteConfig; siteKey: string } | null> {
  console.log(`\n🔍 Auto-discovering credentials for ${domain}...`);
  
  // Determine which vault to use (Bitwarden preferred, fallback to 1Password)
  const hasBitwarden = isBitwardenAvailable();
  const has1Password = is1PasswordAvailable();
  
  if (!hasBitwarden && !has1Password) {
    console.log(`\n⚠️  No password manager CLI found.`);
    console.log(`\n💡 To enable auto-vault, install one of the following:`);
    console.log(`   • Bitwarden (free): brew install bitwarden-cli`);
    console.log(`   • 1Password (paid): brew install 1password-cli`);
    
    const createNew = await promptUser('\nWould you like to manually enter credentials? (y/n): ');
    if (createNew.toLowerCase() === 'y') {
      return await manualCredentialEntry(domain);
    }
    return null;
  }
  
  // Try Bitwarden first (default)
  if (hasBitwarden) {
    const bwResult = await interactiveBitwardenDiscovery(domain);
    if (bwResult) return bwResult;
  }
  
  // Fall back to 1Password if Bitwarden has no matches
  if (has1Password) {
    console.log(`\n🔄 Trying 1Password...`);
    const opResult = await interactive1PasswordDiscovery(domain);
    if (opResult) return opResult;
  }
  
  // No matches found in any vault
  console.log(`\n❌ No matching credentials found for ${domain}`);
  
  const createNew = await promptUser('\nWould you like to manually enter credentials? (y/n): ');
  if (createNew.toLowerCase() === 'y') {
    return await manualCredentialEntry(domain);
  }
  
  return null;
}

/**
 * Interactive credential discovery from Bitwarden
 */
async function interactiveBitwardenDiscovery(
  domain: string
): Promise<{ credentials: VaultCredentials; siteConfig: SiteConfig; siteKey: string } | null> {
  const items = searchBitwardenItems(domain);
  
  if (items.length === 0) {
    return null; // Let caller try 1Password or manual entry
  }
  
  console.log(`\n📋 Found ${items.length} matching credential(s) in Bitwarden:\n`);
  
  items.forEach((item, index) => {
    console.log(`  ${index + 1}) ${item.name}`);
    if (item.login?.username) {
      console.log(`     Username: ${item.login.username}`);
    }
  });
  
  console.log(`  n) None of these - try another vault`);
  console.log(`  m) Manually enter credentials`);
  
  const choice = await promptUser('\nSelect credential to use (1-' + items.length + ', n, or m): ');
  
  if (choice.toLowerCase() === 'n') {
    return null;
  }
  
  if (choice.toLowerCase() === 'm') {
    return await manualCredentialEntry(domain);
  }
  
  const selectedIndex = parseInt(choice) - 1;
  if (isNaN(selectedIndex) || selectedIndex < 0 || selectedIndex >= items.length) {
    console.log('Invalid selection. Skipping authentication.');
    return null;
  }
  
  const selectedItem = items[selectedIndex];
  
  // Extract credentials directly from Bitwarden item
  const credentials: VaultCredentials = {};
  
  if (selectedItem.login?.username) {
    credentials.username = selectedItem.login.username;
  }
  if (selectedItem.login?.password) {
    credentials.password = selectedItem.login.password;
  }
  
  // Check for token/API key in custom fields
  const tokenField = selectedItem.fields?.find(f => 
    f.name.toLowerCase().includes('token') || 
    f.name.toLowerCase().includes('api') ||
    f.name.toLowerCase().includes('key')
  );
  if (tokenField) {
    credentials.token = tokenField.value;
  }
  
  // Build site config
  const siteKey = extractSiteKey(domain);
  const siteConfig: SiteConfig = {
    vault: 'bitwarden',
    item: selectedItem.name,
    usernameField: credentials.username ? 'username' : undefined,
    passwordField: credentials.password ? 'password' : undefined,
    tokenField: tokenField ? tokenField.name : undefined
  };
  
  // Ask if user wants to save this configuration
  const saveConfigChoice = await promptUser('\nSave this credential mapping for future use? (y/n): ');
  
  if (saveConfigChoice.toLowerCase() === 'y') {
    const config = loadConfig();
    config.vault.provider = 'bitwarden';
    config.vault.sites[siteKey] = siteConfig;
    saveConfig(config);
    console.log(`✅ Saved credential mapping for "${siteKey}" to ~/.browser-secure/config.yaml`);
    console.log(`   Default vault provider set to: Bitwarden`);
  }
  
  return { credentials, siteConfig, siteKey };
}

/**
 * Interactive credential discovery from 1Password
 */
async function interactive1PasswordDiscovery(
  domain: string
): Promise<{ credentials: VaultCredentials; siteConfig: SiteConfig; siteKey: string } | null> {
  const items = search1PasswordItems(domain);
  
  if (items.length === 0) {
    return null;
  }
  
  console.log(`\n📋 Found ${items.length} matching credential(s) in 1Password:\n`);
  
  items.forEach((item, index) => {
    console.log(`  ${index + 1}) ${item.title} (Vault: ${item.vault.name})`);
    if (item.urls && item.urls.length > 0) {
      console.log(`     URL: ${item.urls[0].href}`);
    }
  });
  
  console.log(`  n) None of these - skip authentication`);
  console.log(`  m) Manually enter credentials`);
  
  const choice = await promptUser('\nSelect credential to use (1-' + items.length + ', n, or m): ');
  
  if (choice.toLowerCase() === 'n') {
    return null;
  }
  
  if (choice.toLowerCase() === 'm') {
    return await manualCredentialEntry(domain);
  }
  
  const selectedIndex = parseInt(choice) - 1;
  if (isNaN(selectedIndex) || selectedIndex < 0 || selectedIndex >= items.length) {
    console.log('Invalid selection. Skipping authentication.');
    return null;
  }
  
  const selectedItem = items[selectedIndex];
  
  // Get field details
  const fields = get1PasswordItemFields(selectedItem.id);
  
  // Auto-detect field names
  const usernameField = fields.find(f => 
    f.label.toLowerCase().includes('username') || 
    f.label.toLowerCase().includes('email') ||
    f.label.toLowerCase().includes('user')
  )?.label;
  
  const passwordField = fields.find(f => 
    f.label.toLowerCase().includes('password')
  )?.label;
  
  const tokenField = fields.find(f => 
    f.label.toLowerCase().includes('token') || 
    f.label.toLowerCase().includes('api') ||
    f.label.toLowerCase().includes('key')
  )?.label;
  
  // Build site config
  const siteKey = extractSiteKey(domain);
  const siteConfig: SiteConfig = {
    vault: selectedItem.vault.name,
    item: selectedItem.title,
    usernameField,
    passwordField,
    tokenField
  };
  
  // Fetch credentials
  const credentials: VaultCredentials = {};
  
  if (usernameField) {
    try {
      const vaultPath = `op://${selectedItem.vault.name}/${selectedItem.title}/${usernameField}`;
      credentials.username = execSync(`op read "${vaultPath}"`, { encoding: 'utf-8' }).trim();
    } catch (e) {
      console.warn(`Warning: Could not read username field: ${e}`);
    }
  }
  
  if (passwordField) {
    try {
      const vaultPath = `op://${selectedItem.vault.name}/${selectedItem.title}/${passwordField}`;
      credentials.password = execSync(`op read "${vaultPath}"`, { encoding: 'utf-8' }).trim();
    } catch (e) {
      console.warn(`Warning: Could not read password field: ${e}`);
    }
  }
  
  if (tokenField) {
    try {
      const vaultPath = `op://${selectedItem.vault.name}/${selectedItem.title}/${tokenField}`;
      credentials.token = execSync(`op read "${vaultPath}"`, { encoding: 'utf-8' }).trim();
    } catch (e) {
      console.warn(`Warning: Could not read token field: ${e}`);
    }
  }
  
  // Ask if user wants to save this configuration
  const saveConfigChoice = await promptUser('\nSave this credential mapping for future use? (y/n): ');
  
  if (saveConfigChoice.toLowerCase() === 'y') {
    const config = loadConfig();
    config.vault.sites[siteKey] = siteConfig;
    saveConfig(config);
    console.log(`✅ Saved credential mapping for "${siteKey}" to ~/.browser-secure/config.yaml`);
  }
  
  return { credentials, siteConfig, siteKey };
}

/**
 * Manually enter credentials
 */
async function manualCredentialEntry(domain: string): Promise<{ credentials: VaultCredentials; siteConfig: SiteConfig; siteKey: string } | null> {
  console.log('\n📝 Manual credential entry\n');
  
  const username = await promptUser('Username/Email (press Enter to skip): ');
  const password = await promptUser('Password (press Enter to skip): ');
  
  if (!username && !password) {
    console.log('No credentials entered. Skipping authentication.');
    return null;
  }
  
  const siteKey = extractSiteKey(domain);
  
  const credentials: VaultCredentials = {};
  if (username) credentials.username = username;
  if (password) credentials.password = password;
  
  const siteConfig: SiteConfig = {
    vault: 'manual',
    item: `${siteKey}-manual`,
    usernameField: username ? 'username' : undefined,
    passwordField: password ? 'password' : undefined
  };
  
  // Ask to save
  const saveChoice = await promptUser('\nSave these credentials to config? (y/n): ');
  if (saveChoice.toLowerCase() === 'y') {
    const config = loadConfig();
    config.vault.sites[siteKey] = siteConfig;
    saveConfig(config);
    console.log(`✅ Saved credential config for "${siteKey}"`);
    console.log('⚠️  Note: Manual credentials are not stored securely. Consider adding to a password manager.');
  }
  
  return { credentials, siteConfig, siteKey };
}
