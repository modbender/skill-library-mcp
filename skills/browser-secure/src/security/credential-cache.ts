import crypto from 'crypto';
import fs from 'fs';
import path from 'path';
import os from 'os';
import { VaultCredentials } from '../vault/index.js';
import { getSessionConfig, expandPath } from '../config/loader.js';

interface CachedCredential {
  site: string;
  credentials: VaultCredentials;
  encrypted: boolean;
  expiresAt: number;
}

const CACHE_DIR = path.join(os.homedir(), '.browser-secure', 'cache');
const CACHE_FILE = path.join(CACHE_DIR, 'credentials.cache');
const AES_ALGORITHM = 'aes-256-gcm';

// Get or derive encryption key from environment
function getEncryptionKey(): Buffer {
  const envKey = process.env.BROWSER_SECURE_CACHE_KEY;
  if (envKey) {
    // Use provided key, hashed to 32 bytes
    return crypto.createHash('sha256').update(envKey).digest();
  }
  // Require environment variable for credential caching
  throw new Error('BROWSER_SECURE_CACHE_KEY must be set for credential caching');
}

let encryptionKey: Buffer | null = null;

function getKey(): Buffer {
  if (!encryptionKey) {
    encryptionKey = getEncryptionKey();
  }
  return encryptionKey;
}

function ensureCacheDir(): void {
  if (!fs.existsSync(CACHE_DIR)) {
    fs.mkdirSync(CACHE_DIR, { recursive: true, mode: 0o700 });
  }
}

function encryptData(data: string): { encrypted: Buffer; authTag: Buffer; iv: Buffer } {
  const key = getKey();
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv(AES_ALGORITHM, key, iv);

  const encrypted = Buffer.concat([cipher.update(data, 'utf-8'), cipher.final()]);
  const authTag = cipher.getAuthTag();

  return { encrypted, authTag, iv };
}

function decryptData(encrypted: Buffer, authTag: Buffer, iv: Buffer): string {
  const key = getKey();
  const decipher = crypto.createDecipheriv(AES_ALGORITHM, key, iv);
  decipher.setAuthTag(authTag);

  return Buffer.concat([decipher.update(encrypted), decipher.final()]).toString('utf-8');
}

interface SerializedCache {
  version: number;
  entries: Array<{
    site: string;
    credentials: string;  // base64 encrypted
    authTag: string;      // base64
    iv: string;           // base64
    expiresAt: number;
  }>;
}

export async function cacheCredentials(site: string, credentials: VaultCredentials): Promise<void> {
  ensureCacheDir();

  const config = getSessionConfig();
  const cacheDurationMs = config.credentialCacheMinutes * 60 * 1000;

  const entry: CachedCredential = {
    site,
    credentials,
    encrypted: true,
    expiresAt: Date.now() + cacheDurationMs
  };

  // Load existing cache
  const cache = loadCacheFile();

  // Remove existing entry for this site
  const existingIndex = cache.entries.findIndex(e => e.site === site);
  if (existingIndex >= 0) {
    cache.entries.splice(existingIndex, 1);
  }

  // Encrypt credentials
  const credsJson = JSON.stringify(credentials);
  const { encrypted, authTag, iv } = encryptData(credsJson);

  // Add new entry
  cache.entries.push({
    site,
    credentials: encrypted.toString('base64'),
    authTag: authTag.toString('base64'),
    iv: iv.toString('base64'),
    expiresAt: entry.expiresAt
  });

  // Clean up expired entries
  cleanupExpiredEntries(cache);

  // Write cache
  saveCacheFile(cache);

  // Set restrictive permissions
  try {
    fs.chmodSync(CACHE_FILE, 0o600);
  } catch {
    // Ignore permission errors
  }
}

export async function getCachedCredentials(site: string): Promise<VaultCredentials | null> {
  if (!fs.existsSync(CACHE_FILE)) {
    return null;
  }

  const cache = loadCacheFile();
  const entry = cache.entries.find(e => e.site === site);

  if (!entry) {
    return null;
  }

  // Check expiration
  if (Date.now() > entry.expiresAt) {
    // Remove expired entry
    const index = cache.entries.indexOf(entry);
    cache.entries.splice(index, 1);
    saveCacheFile(cache);
    return null;
  }

  try {
    // Decrypt credentials
    const encrypted = Buffer.from(entry.credentials, 'base64');
    const authTag = Buffer.from(entry.authTag, 'base64');
    const iv = Buffer.from(entry.iv, 'base64');

    const decrypted = decryptData(encrypted, authTag, iv);
    return JSON.parse(decrypted) as VaultCredentials;
  } catch (e) {
    // Decryption failed (likely wrong key or corrupted data)
    const index = cache.entries.indexOf(entry);
    cache.entries.splice(index, 1);
    saveCacheFile(cache);
    return null;
  }
}

export function clearCredentialCache(): void {
  if (fs.existsSync(CACHE_FILE)) {
    fs.unlinkSync(CACHE_FILE);
  }
  // Also clear any in-memory key
  encryptionKey = null;
}

export function isCacheValid(site: string): boolean {
  if (!fs.existsSync(CACHE_FILE)) {
    return false;
  }

  const cache = loadCacheFile();
  const entry = cache.entries.find(e => e.site === site);

  if (!entry) {
    return false;
  }

  return Date.now() <= entry.expiresAt;
}

function loadCacheFile(): SerializedCache {
  if (!fs.existsSync(CACHE_FILE)) {
    return { version: 1, entries: [] };
  }

  try {
    const content = fs.readFileSync(CACHE_FILE, 'utf-8');
    const parsed = JSON.parse(content);
    if (parsed.version === 1 && Array.isArray(parsed.entries)) {
      return parsed as SerializedCache;
    }
    return { version: 1, entries: [] };
  } catch {
    return { version: 1, entries: [] };
  }
}

function saveCacheFile(cache: SerializedCache): void {
  ensureCacheDir();
  fs.writeFileSync(CACHE_FILE, JSON.stringify(cache, null, 2), 'utf-8');
}

function cleanupExpiredEntries(cache: SerializedCache): void {
  const now = Date.now();
  cache.entries = cache.entries.filter(e => e.expiresAt > now);
}

// Initialize encryption key from environment if available
if (process.env.BROWSER_SECURE_CACHE_KEY) {
  encryptionKey = getEncryptionKey();
}
