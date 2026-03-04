// Security and Authentication Module
const crypto = require('crypto');
const rateLimit = require('express-rate-limit');

class VisualizationSecurity {
  constructor() {
    this.apiKeys = new Map(); // In production, use a proper database
    this.rateLimiter = this.createRateLimiter();
  }

  // Create API key for user
  createAPIKey(userId, permissions = ['read', 'generate']) {
    const apiKey = 'viz_' + crypto.randomBytes(32).toString('hex');
    const apiKeyHash = crypto.createHash('sha256').update(apiKey).digest('hex');
    
    this.apiKeys.set(apiKeyHash, {
      userId: userId,
      permissions: permissions,
      createdAt: new Date(),
      lastUsed: null
    });
    
    return { apiKey, apiKeyId: apiKeyHash };
  }

  // Validate API key
  validateAPIKey(apiKey) {
    const apiKeyHash = crypto.createHash('sha256').update(apiKey).digest('hex');
    const keyData = this.apiKeys.get(apiKeyHash);
    
    if (!keyData) {
      return { valid: false, error: 'Invalid API key' };
    }
    
    // Update last used timestamp
    keyData.lastUsed = new Date();
    this.apiKeys.set(apiKeyHash, keyData);
    
    return { valid: true, userId: keyData.userId, permissions: keyData.permissions };
  }

  // Revoke API key
  revokeAPIKey(apiKey) {
    const apiKeyHash = crypto.createHash('sha256').update(apiKey).digest('hex');
    return this.apiKeys.delete(apiKeyHash);
  }

  // List API keys for user
  listAPIKeys(userId) {
    const userKeys = [];
    for (const [keyId, keyData] of this.apiKeys.entries()) {
      if (keyData.userId === userId) {
        userKeys.push({
          keyId: keyId,
          createdAt: keyData.createdAt,
          lastUsed: keyData.lastUsed,
          permissions: keyData.permissions
        });
      }
    }
    return userKeys;
  }

  // Create rate limiter
  createRateLimiter(options = {}) {
    const defaultOptions = {
      windowMs: 15 * 60 * 1000, // 15 minutes
      max: 100, // limit each IP to 100 requests per windowMs
      message: 'Too many requests from this IP, please try again later.',
      standardHeaders: true,
      legacyHeaders: false,
      ...options
    };
    
    return rateLimit(defaultOptions);
  }

  // Apply rate limiting to request
  applyRateLimit(req, res, next) {
    return this.rateLimiter(req, res, next);
  }

  // Encrypt sensitive configuration
  encryptConfig(config, encryptionKey) {
    const algorithm = 'aes-256-cbc';
    const key = crypto.scryptSync(encryptionKey, 'salt', 32);
    const iv = crypto.randomBytes(16);
    
    const cipher = crypto.createCipher(algorithm, key);
    let encrypted = cipher.update(JSON.stringify(config), 'utf8', 'hex');
    encrypted += cipher.final('hex');
    
    return { encrypted, iv: iv.toString('hex') };
  }

  // Decrypt sensitive configuration
  decryptConfig(encryptedData, iv, encryptionKey) {
    const algorithm = 'aes-256-cbc';
    const key = crypto.scryptSync(encryptionKey, 'salt', 32);
    const ivBuffer = Buffer.from(iv, 'hex');
    
    const decipher = crypto.createDecipher(algorithm, key);
    let decrypted = decipher.update(encryptedData, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    
    return JSON.parse(decrypted);
  }

  // Validate user permissions
  hasPermission(userId, permission, resource) {
    // In real implementation, this would check against user roles and permissions
    // For now, assume all users have basic permissions
    const basicPermissions = ['read', 'generate'];
    return basicPermissions.includes(permission);
  }

  // Log security events
  logSecurityEvent(eventType, details) {
    console.log(`[SECURITY] ${new Date().toISOString()} - ${eventType}:`, details);
    // In production, this would write to a secure audit log
  }
}

module.exports = VisualizationSecurity;