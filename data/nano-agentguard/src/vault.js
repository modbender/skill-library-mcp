/**
 * Vault - Encrypted Credential Storage
 *
 * AES-256-GCM encryption with PBKDF2 key derivation
 */

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const { promisify } = require('util');

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
  constructor(vaultPath, masterPassword) {
    this.vaultPath = vaultPath || path.join(process.env.HOME, '.agentguard', 'vault');
    this.masterPassword = masterPassword;
    this.cache = new Map();
  }

  /**
   * Initialize vault directory
   */
  async init() {
    await mkdir(this.vaultPath, { recursive: true });
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
   * Store a credential for an agent
   */
  async store(agentId, key, value) {
    const agentPath = path.join(this.vaultPath, `${agentId}.vault`);

    // Load existing credentials or create new
    let credentials = {};
    if (fs.existsSync(agentPath)) {
      credentials = await this.loadAll(agentId);
    }

    credentials[key] = {
      value,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    // Generate salt for this agent if new
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

    // Update cache
    this.cache.set(agentId, credentials);

    return { agentId, key, stored: true };
  }

  /**
   * Get a credential for an agent
   */
  async get(agentId, key) {
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
    // Check cache first
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

    // Cache for future use
    this.cache.set(agentId, credentials);

    return credentials;
  }

  /**
   * Delete a credential
   */
  async delete(agentId, key) {
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
   * List all keys for an agent (not values)
   */
  async listKeys(agentId) {
    const credentials = await this.loadAll(agentId);
    return Object.keys(credentials).map(k => ({
      key: k,
      createdAt: credentials[k].createdAt,
      updatedAt: credentials[k].updatedAt
    }));
  }
}

module.exports = Vault;
