import { execSync, spawnSync } from 'child_process';
import { SiteConfig, loadConfig } from '../config/loader.js';

export interface VaultCredentials {
  username?: string;
  password?: string;
  token?: string;
}

// Re-export discovery functions
export {
  extractDomain,
  extractSiteKey,
  search1PasswordItems,
  interactiveCredentialDiscovery
} from './discovery.js';

export abstract class VaultProvider {
  abstract name: string;
  abstract isAvailable(): boolean;
  abstract getCredentials(site: string, config: SiteConfig): Promise<VaultCredentials>;
}

// 1Password integration
class OnePasswordVault extends VaultProvider {
  name = '1password';

  isAvailable(): boolean {
    try {
      execSync('which op', { stdio: 'ignore' });
      return true;
    } catch {
      return false;
    }
  }

  async getCredentials(site: string, config: SiteConfig): Promise<VaultCredentials> {
    const creds: VaultCredentials = {};

    if (config.usernameField) {
      try {
        const vaultPath = `op://${config.vault}/${config.item}/${config.usernameField}`;
        const result = spawnSync('op', ['read', '-'], {
          input: vaultPath,
          encoding: 'utf-8'
        });
        if (result.status !== 0) {
          throw new Error(result.stderr || 'Failed to read from 1Password');
        }
        creds.username = result.stdout.trim();
      } catch (e: any) {
        throw new Error(`Failed to read username from 1Password: ${e.message || e}`);
      }
    }

    if (config.passwordField) {
      try {
        const vaultPath = `op://${config.vault}/${config.item}/${config.passwordField}`;
        const result = spawnSync('op', ['read', '-'], {
          input: vaultPath,
          encoding: 'utf-8'
        });
        if (result.status !== 0) {
          throw new Error(result.stderr || 'Failed to read from 1Password');
        }
        creds.password = result.stdout.trim();
      } catch (e: any) {
        throw new Error(`Failed to read password from 1Password: ${e.message || e}`);
      }
    }

    if (config.tokenField) {
      try {
        const vaultPath = `op://${config.vault}/${config.item}/${config.tokenField}`;
        const result = spawnSync('op', ['read', '-'], {
          input: vaultPath,
          encoding: 'utf-8'
        });
        if (result.status !== 0) {
          throw new Error(result.stderr || 'Failed to read from 1Password');
        }
        creds.token = result.stdout.trim();
      } catch (e: any) {
        throw new Error(`Failed to read token from 1Password: ${e.message || e}`);
      }
    }

    return creds;
  }
}

// Bitwarden integration
class BitwardenVault extends VaultProvider {
  name = 'bitwarden';

  isAvailable(): boolean {
    try {
      execSync('which bw', { stdio: 'ignore' });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Ensure Bitwarden is authenticated and vault is unlocked
   * Tries API key auth first, then falls back to password/session
   */
  private ensureAuthenticated(): void {
    // Check if already unlocked
    try {
      const status = JSON.parse(execSync('bw status', { encoding: 'utf-8' }));
      if (status.status === 'unlocked') {
        return; // Already good to go
      }
    } catch {
      // Not authenticated, try to login
    }

    // Try API key auth (preferred for automation) - this does login only
    const clientId = process.env.BW_CLIENTID;
    const clientSecret = process.env.BW_CLIENTSECRET;
    let loggedIn = false;

    if (clientId && clientSecret) {
      try {
        execSync('bw login --apikey', {
          env: { ...process.env, BW_CLIENTID: clientId, BW_CLIENTSECRET: clientSecret },
          stdio: 'ignore'
        });
        loggedIn = true;
      } catch (e) {
        console.warn('⚠️  Bitwarden API key login failed, trying password/session...');
      }
    }

    // Try password-based unlock (needed after API key login or for direct unlock)
    const password = process.env.BW_PASSWORD;
    if (password) {
      try {
        execSync('bw unlock --raw', {
          env: { ...process.env, BW_PASSWORD: password },
          stdio: 'ignore'
        });
        return;
      } catch (e) {
        console.warn('⚠️  Bitwarden password unlock failed.');
      }
    }

    // Check for existing BW_SESSION
    if (process.env.BW_SESSION) {
      try {
        execSync('bw status', { stdio: 'ignore' });
        return;
      } catch {
        // Session invalid
      }
    }

    throw new Error(
      'Bitwarden vault is locked. Please set one of:\n' +
      '  • BW_PASSWORD (master password for unlock)\n' +
      '  • BW_SESSION (session token from: export BW_SESSION=$(bw unlock --raw))\n' +
      '\nNote: BW_CLIENTID + BW_CLIENTSECRET only handle login, not vault unlock.\n' +
      'For full automation, set BW_PASSWORD or BW_SESSION in your .env file.'
    );
  }

  async getCredentials(site: string, config: SiteConfig): Promise<VaultCredentials> {
    this.ensureAuthenticated();

    const creds: VaultCredentials = {};

    try {
      // Get item by name
      const items = JSON.parse(execSync(`bw list items --search "${config.item}"`, { encoding: 'utf-8' }));
      if (items.length === 0) {
        throw new Error(`Item "${config.item}" not found in Bitwarden`);
      }
      const item = items[0];

      if (config.usernameField) {
        creds.username = item.login?.username;
      }
      if (config.passwordField) {
        creds.password = item.login?.password;
      }
      if (config.tokenField) {
        // Check custom fields
        const tokenField = item.fields?.find((f: any) => f.name === config.tokenField);
        creds.token = tokenField?.value;
      }
    } catch (e) {
      throw new Error(`Failed to read from Bitwarden: ${e}`);
    }

    return creds;
  }
}

// macOS Keychain integration
class KeychainVault extends VaultProvider {
  name = 'keychain';

  isAvailable(): boolean {
    try {
      execSync('which security', { stdio: 'ignore' });
      return process.platform === 'darwin';
    } catch {
      return false;
    }
  }

  async getCredentials(site: string, config: SiteConfig): Promise<VaultCredentials> {
    const creds: VaultCredentials = {};

    if (config.passwordField) {
      try {
        creds.password = execSync(
          `security find-generic-password -s "${config.item}" -w`,
          { encoding: 'utf-8' }
        ).trim();
      } catch (e) {
        throw new Error(`Failed to read from keychain: ${e}`);
      }
    }

    return creds;
  }
}

// Environment variable fallback
class EnvironmentVault extends VaultProvider {
  name = 'env';

  isAvailable(): boolean {
    return true;
  }

  async getCredentials(site: string, config: SiteConfig): Promise<VaultCredentials> {
    const creds: VaultCredentials = {};
    const prefix = `BROWSER_SECURE_${site.toUpperCase()}`;

    creds.username = process.env[`${prefix}_USERNAME`];
    creds.password = process.env[`${prefix}_PASSWORD`];
    creds.token = process.env[`${prefix}_TOKEN`];

    return creds;
  }
}

// Vault manager
const vaults: VaultProvider[] = [
  new OnePasswordVault(),
  new BitwardenVault(),
  new KeychainVault(),
  new EnvironmentVault()
];

export function getVaultProvider(name: string): VaultProvider {
  const vault = vaults.find(v => v.name === name);
  if (!vault) {
    throw new Error(`Unknown vault provider: ${name}`);
  }
  if (!vault.isAvailable()) {
    throw new Error(`Vault provider "${name}" is not available. Please install the CLI tool.`);
  }
  return vault;
}

export async function getSiteCredentials(site: string): Promise<VaultCredentials> {
  const config = loadConfig();
  const siteConfig = config.vault.sites[site];
  
  if (!siteConfig) {
    throw new Error(`Site "${site}" not configured. Add it to ~/.browser-secure/config.yaml`);
  }

  const vault = getVaultProvider(config.vault.provider);
  return vault.getCredentials(site, siteConfig);
}

export function listAvailableVaults(): string[] {
  return vaults.filter(v => v.isAvailable()).map(v => v.name);
}
