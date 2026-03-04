/**
 * Vault with 1Password Backend Support
 *
 * Can use either:
 * - Local encrypted storage (default)
 * - 1Password CLI as backend
 * - Hybrid: local cache + 1Password source
 */

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const { promisify } = require('util');
const OnePasswordProvider = require('./1password');

const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);
const mkdir = promisify(fs.mkdir);

const ALGORITHM = 'aes-256-gcm';
const KEY_LENGTH = 32;
const IV_LENGTH = 16;
const SALT_LENGTH = 32;
const AUTH_TAG_LENGTH = 16;
const PBKDF2_ITERATIONS = 100000;

class Vault {
  constructor(vaultPath, masterPassword, options = {}) {
    this.vaultPath = vaultPath || path.join(process.env.HOME, '.agentguard', 'vault');
    this.masterPassword = masterPassword;
    this.cache = new Map();

    // 1Password integration
    this.use1Password = options.use1Password || false;
    this.opProvider = null;

    if (this.use1Password) {
      this.opProvider = new OnePasswordProvider({
        account: options.opAccount,
        vault: options.opVault || 'Private'
      });
    }
  }

  /**
   * Initialize vault
   */
  async init() {
    await mkdir(this.vaultPath, { recursive: true });

    // If using 1Password, check availability
    if (this.use1Password && this.opProvider) {
      if (!this.opProvider.isAvailable()) {
        console.warn('1Password CLI not available, falling back to local vault');
        this.use1Password = false;
      }
    }

    // Get master password from 1Password if configured
    if (this.use1Password && !this.masterPassword) {
      try {
        this.masterPassword = await this.opProvider.getMasterPassword();
      } catch {
        // Generate and store if not exists
        this.masterPassword = crypto.randomBytes(32).toString('base64');
        await this.opProvider.storeMasterPassword(this.masterPassword);
      }
    }
  }

  /**
   * Derive encryption key from master password
   */
  deriveKey(password, salt) {
    return crypto.pbkdf2Sync(password, salt, PBKDF2_ITERATIONS, KEY_LENGTH, 'sha256');
  }

  /**
   * Encrypt data
   */
  encrypt(plaintext, key) {
    const iv = crypto.randomBytes(IV_LENGTH);
    const cipher = crypto.createCipheriv(ALGORITHM, key, iv);

    const encrypted = Buffer.concat([
      cipher.update(plaintext, 'utf8'),
      cipher.final()
    ]);

    const authTag = cipher.getAuthTag();

    return Buffer.concat([iv, authTag, encrypted]);
  }

  /**
   * Decrypt data
   */
  decrypt(ciphertext, key) {
    const iv = ciphertext.subarray(0, IV_LENGTH);
    const authTag = ciphertext.subarray(IV_LENGTH, IV_LENGTH + AUTH_TAG_LENGTH);
    const encrypted = ciphertext.subarray(IV_LENGTH + AUTH_TAG_LENGTH);

    const decipher = crypto.createDecipheriv(ALGORITHM, key, iv);
    decipher.setAuthTag(authTag);

    return Buffer.concat([
      decipher.update(encrypted),
      decipher.final()
    ]).toString('utf8');
  }

  /**
   * Store a credential
   */
  async store(agentId, key, value) {
    // If using 1Password, store there too
    if (this.use1Password && this.opProvider) {
      await this.opProvider.storeAgentCredential(agentId, key, value);
    }

    // Always store locally as backup/cache
    const agentPath = path.join(this.vaultPath, `${agentId}.vault`);

    let credentials = {};
    if (fs.existsSync(agentPath)) {
      credentials = await this.loadAll(agentId);
    }

    credentials[key] = {
      value,
      createdAt: credentials[key]?.createdAt || new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      source: this.use1Password ? '1password+local' : 'local'
    };

    // Generate salt if needed
    let saltPath = path.join(this.vaultPath, `${agentId}.salt`);
    let salt;
    if (fs.existsSync(saltPath)) {
      salt = await readFile(saltPath);
    } else {
      salt = crypto.randomBytes(SALT_LENGTH);
      await writeFile(saltPath, salt);
    }

    // Encrypt and save
    const keyDerived = this.deriveKey(this.masterPassword, salt);
    const encrypted = this.encrypt(JSON.stringify(credentials), keyDerived);

    await writeFile(agentPath, encrypted);
    this.cache.set(agentId, credentials);

    return {
      agentId,
      key,
      stored: true,
      source: this.use1Password ? '1password+local' : 'local'
    };
  }

  /**
   * Get a credential
   */
  async get(agentId, key) {
    // Try 1Password first if enabled
    if (this.use1Password && this.opProvider) {
      try {
        const value = await this.opProvider.getAgentCredential(agentId, key);
        return value;
      } catch {
        // Fall back to local
      }
    }

    // Load from local vault
    const credentials = await this.loadAll(agentId);
    if (!credentials[key]) {
      throw new Error(`Credential not found: ${agentId}/${key}`);
    }
    return credentials[key].value;
  }

  /**
   * Load all credentials for an agent
   */
  async loadAll(agentId) {
    if (this.cache.has(agentId)) {
      return this.cache.get(agentId);
    }

    const agentPath = path.join(this.vaultPath, `${agentId}.vault`);
    const saltPath = path.join(this.vaultPath, `${agentId}.salt`);

    if (!fs.existsSync(agentPath)) {
      return {};
    }

    const encrypted = await readFile(agentPath);
    const salt = await readFile(saltPath);

    const key = this.deriveKey(this.masterPassword, salt);
    const decrypted = this.decrypt(encrypted, key);
    const credentials = JSON.parse(decrypted);

    this.cache.set(agentId, credentials);
    return credentials;
  }

  /**
   * Delete a credential
   */
  async delete(agentId, key) {
    // Delete from 1Password if enabled
    if (this.use1Password && this.opProvider) {
      try {
        await this.opProvider.delete(`AgentGuard: ${agentId} - ${key}`);
      } catch {
        // Ignore if not in 1Password
      }
    }

    // Delete from local
    const credentials = await this.loadAll(agentId);
    if (!credentials[key]) {
      return false;
    }

    delete credentials[key];

    const saltPath = path.join(this.vaultPath, `${agentId}.salt`);
    const agentPath = path.join(this.vaultPath, `${agentId}.vault`);
    const salt = await readFile(saltPath);
    const keyDerived = this.deriveKey(this.masterPassword, salt);
    const encrypted = this.encrypt(JSON.stringify(credentials), keyDerived);

    await writeFile(agentPath, encrypted);
    this.cache.set(agentId, credentials);

    return true;
  }

  /**
   * List all keys for an agent
   */
  async listKeys(agentId) {
    const credentials = await this.loadAll(agentId);
    return Object.keys(credentials).map(k => ({
      key: k,
      createdAt: credentials[k].createdAt,
      updatedAt: credentials[k].updatedAt,
      source: credentials[k].source || 'local'
    }));
  }

  /**
   * Get 1Password reference for use in op inject
   */
  getOpReference(agentId, key) {
    if (!this.opProvider) {
      throw new Error('1Password not configured');
    }
    return this.opProvider.getReference(agentId, key);
  }

  /**
   * Sync all credentials from 1Password to local
   */
  async syncFrom1Password(agentId) {
    if (!this.use1Password || !this.opProvider) {
      throw new Error('1Password not configured');
    }

    // List items matching agent pattern
    const items = await this.opProvider.listItems();
    const agentItems = items.filter(i =>
      i.title.startsWith(`AgentGuard: ${agentId} -`)
    );

    for (const item of items) {
      const match = item.title.match(/AgentGuard: (.+?) - (.+)/);
      if (match) {
        const [, itemAgentId, key] = match;
        if (itemAgentId === agentId) {
          const value = await this.opProvider.getAgentCredential(agentId, key);
          // Store locally without triggering 1Password write
          const credentials = await this.loadAll(agentId);
          credentials[key] = {
            value,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            source: '1password'
          };

          const saltPath = path.join(this.vaultPath, `${agentId}.salt`);
          const agentPath = path.join(this.vaultPath, `${agentId}.vault`);
          let salt;
          if (fs.existsSync(saltPath)) {
            salt = await readFile(saltPath);
          } else {
            salt = crypto.randomBytes(SALT_LENGTH);
            await writeFile(saltPath, salt);
          }

          const keyDerived = this.deriveKey(this.masterPassword, salt);
          const encrypted = this.encrypt(JSON.stringify(credentials), keyDerived);
          await writeFile(agentPath, encrypted);
          this.cache.set(agentId, credentials);
        }
      }
    }

    return { synced: agentItems.length };
  }
}

module.exports = Vault;
