/**
 * BaseMail Crypto Utilities
 * AES-256-GCM encryption for private keys
 */

const crypto = require('crypto');

/**
 * Encrypt a private key with a password
 * @param {string} privateKey - The private key to encrypt
 * @param {string} password - The encryption password
 * @returns {object} Encrypted data object
 */
function encryptPrivateKey(privateKey, password) {
  const salt = crypto.randomBytes(16);
  const key = crypto.scryptSync(password, salt, 32);
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
  
  let encrypted = cipher.update(privateKey, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  const authTag = cipher.getAuthTag();
  
  return {
    encrypted,
    salt: salt.toString('hex'),
    iv: iv.toString('hex'),
    authTag: authTag.toString('hex'),
    algorithm: 'aes-256-gcm',
    version: 1,
  };
}

/**
 * Decrypt an encrypted private key
 * @param {object} encryptedData - The encrypted data object
 * @param {string} password - The decryption password
 * @returns {string} The decrypted private key
 * @throws {Error} If decryption fails
 */
function decryptPrivateKey(encryptedData, password) {
  const key = crypto.scryptSync(
    password, 
    Buffer.from(encryptedData.salt, 'hex'), 
    32
  );
  
  const decipher = crypto.createDecipheriv(
    encryptedData.algorithm || 'aes-256-gcm',
    key,
    Buffer.from(encryptedData.iv, 'hex')
  );
  
  decipher.setAuthTag(Buffer.from(encryptedData.authTag, 'hex'));
  
  let decrypted = decipher.update(encryptedData.encrypted, 'hex', 'utf8');
  decrypted += decipher.final('utf8');
  
  return decrypted;
}

/**
 * Validate password strength
 * @param {string} password - The password to validate
 * @returns {object} { valid: boolean, errors: string[] }
 */
function validatePassword(password) {
  const errors = [];
  
  if (!password || password.length < 8) {
    errors.push('Password must be at least 8 characters');
  }
  
  if (password && password.length > 128) {
    errors.push('Password must not exceed 128 characters');
  }
  
  if (password && (!/[a-zA-Z]/.test(password) || !/[0-9]/.test(password))) {
    errors.push('Password must contain at least one letter and one number');
  }
  
  return {
    valid: errors.length === 0,
    errors,
  };
}

module.exports = {
  encryptPrivateKey,
  decryptPrivateKey,
  validatePassword,
};
