/**
 * Encryption Utilities for Wallet Storage
 *
 * Uses AES-256-GCM for encrypting private keys
 * Industry standard for secure key storage
 */

import * as crypto from 'crypto';

const ALGORITHM = 'aes-256-gcm';
const IV_LENGTH = 16; // 128 bits
const AUTH_TAG_LENGTH = 16; // 128 bits
const KEY_LENGTH = 32; // 256 bits

/**
 * Derive a 256-bit encryption key from the secret
 * Uses PBKDF2 with SHA-256
 */
function deriveKey(secret: string, salt: Buffer): Buffer {
  return crypto.pbkdf2Sync(
    secret,
    salt,
    100000, // iterations (industry standard)
    KEY_LENGTH,
    'sha256'
  );
}

/**
 * Encrypt private key using AES-256-GCM
 *
 * @param privateKey - Private key to encrypt (hex string with or without 0x prefix)
 * @param secret - Encryption secret from WALLET_ENCRYPTION_SECRET env var
 * @returns Encrypted string in format: salt:iv:authTag:encryptedData (all hex)
 */
export function encryptPrivateKey(privateKey: string, secret: string): string {
  if (!secret || secret.length < 32) {
    throw new Error('WALLET_ENCRYPTION_SECRET must be at least 32 characters');
  }

  // Remove 0x prefix if present
  const cleanPrivateKey = privateKey.startsWith('0x') ? privateKey.slice(2) : privateKey;

  // Generate random salt and IV for each encryption
  const salt = crypto.randomBytes(32);
  const iv = crypto.randomBytes(IV_LENGTH);

  // Derive encryption key from secret
  const key = deriveKey(secret, salt);

  // Create cipher
  const cipher = crypto.createCipheriv(ALGORITHM, key, iv);

  // Encrypt private key
  let encrypted = cipher.update(cleanPrivateKey, 'utf8', 'hex');
  encrypted += cipher.final('hex');

  // Get authentication tag
  const authTag = cipher.getAuthTag();

  // Return format: salt:iv:authTag:encryptedData
  return [
    salt.toString('hex'),
    iv.toString('hex'),
    authTag.toString('hex'),
    encrypted
  ].join(':');
}

/**
 * Decrypt private key using AES-256-GCM
 *
 * @param encryptedData - Encrypted string in format: salt:iv:authTag:encryptedData
 * @param secret - Encryption secret from WALLET_ENCRYPTION_SECRET env var
 * @returns Decrypted private key with 0x prefix
 */
export function decryptPrivateKey(encryptedData: string, secret: string): `0x${string}` {
  if (!secret || secret.length < 32) {
    throw new Error('WALLET_ENCRYPTION_SECRET must be at least 32 characters');
  }

  // Parse encrypted data
  const parts = encryptedData.split(':');
  if (parts.length !== 4) {
    throw new Error('Invalid encrypted data format');
  }

  const [saltHex, ivHex, authTagHex, encrypted] = parts;

  // Convert from hex
  const salt = Buffer.from(saltHex, 'hex');
  const iv = Buffer.from(ivHex, 'hex');
  const authTag = Buffer.from(authTagHex, 'hex');

  // Derive encryption key
  const key = deriveKey(secret, salt);

  // Create decipher
  const decipher = crypto.createDecipheriv(ALGORITHM, key, iv);
  decipher.setAuthTag(authTag);

  // Decrypt
  let decrypted = decipher.update(encrypted, 'hex', 'utf8');
  decrypted += decipher.final('utf8');

  // Return with 0x prefix
  return `0x${decrypted}` as `0x${string}`;
}

/**
 * Validate encryption secret strength
 */
export function validateEncryptionSecret(secret: string): { valid: boolean; reason?: string } {
  if (!secret) {
    return { valid: false, reason: 'Encryption secret is required' };
  }

  if (secret.length < 32) {
    return { valid: false, reason: 'Encryption secret must be at least 32 characters' };
  }

  // Check for common weak patterns
  if (secret === 'your_random_secret_here' || secret === 'dev-secret-change-in-production') {
    return { valid: false, reason: 'Please use a strong, random encryption secret' };
  }

  return { valid: true };
}

/**
 * Generate a strong encryption secret (for CLI tools)
 */
export function generateEncryptionSecret(): string {
  return crypto.randomBytes(32).toString('hex');
}
