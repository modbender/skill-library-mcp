/**
 * BaseMail Audit Logger
 * Records security-relevant operations (without sensitive data)
 */

const fs = require('fs');
const path = require('path');

const CONFIG_DIR = path.join(process.env.HOME, '.basemail');
const AUDIT_FILE = path.join(CONFIG_DIR, 'audit.log');

/**
 * Valid audit actions
 */
const ACTIONS = {
  WALLET_CREATED: 'wallet_created',
  REGISTER: 'register',
  SEND_EMAIL: 'send_email',
  INBOX_LIST: 'inbox_list',
  INBOX_READ: 'inbox_read',
  TOKEN_REFRESH: 'token_refresh',
  DECRYPT_ATTEMPT: 'decrypt_attempt',
  ENCRYPT_KEY: 'encrypt_key',
};

/**
 * Mask sensitive data for logging
 * @param {string} value - The value to mask
 * @param {number} showChars - Characters to show at start/end
 * @returns {string} Masked value
 */
function mask(value, showChars = 4) {
  if (!value) return null;
  if (value.length <= showChars * 2) return '***';
  return `${value.slice(0, showChars)}...${value.slice(-showChars)}`;
}

/**
 * Mask email for logging
 * @param {string} email - The email to mask
 * @returns {string} Masked email
 */
function maskEmail(email) {
  if (!email) return null;
  const [local, domain] = email.split('@');
  if (!domain) return mask(email);
  return `${mask(local, 2)}@${domain}`;
}

/**
 * Log an audit entry
 * @param {string} action - The action being logged
 * @param {object} details - Additional details (will be sanitized)
 */
function logAudit(action, details = {}) {
  try {
    // Ensure config directory exists
    if (!fs.existsSync(CONFIG_DIR)) {
      fs.mkdirSync(CONFIG_DIR, { recursive: true, mode: 0o700 });
    }
    
    // Sanitize details - never log sensitive data
    const sanitized = {};
    
    if (details.wallet) {
      sanitized.wallet = mask(details.wallet, 6);
    }
    if (details.to) {
      sanitized.to = maskEmail(details.to);
    }
    if (details.from) {
      sanitized.from = maskEmail(details.from);
    }
    if (details.email_id) {
      sanitized.email_id = mask(details.email_id, 4);
    }
    if (typeof details.success !== 'undefined') {
      sanitized.success = details.success;
    }
    if (details.error) {
      // Only log error type, not full message (may contain sensitive info)
      sanitized.error = typeof details.error === 'string' 
        ? details.error.slice(0, 50) 
        : 'error';
    }
    
    const entry = {
      timestamp: new Date().toISOString(),
      action,
      ...sanitized,
    };
    
    fs.appendFileSync(AUDIT_FILE, JSON.stringify(entry) + '\n', { mode: 0o600 });
  } catch (e) {
    // Silently ignore audit errors - don't break main functionality
  }
}

/**
 * Read audit log entries
 * @param {number} limit - Maximum entries to return (default: 100)
 * @returns {Array} Array of audit entries
 */
function readAuditLog(limit = 100) {
  try {
    if (!fs.existsSync(AUDIT_FILE)) {
      return [];
    }
    
    const content = fs.readFileSync(AUDIT_FILE, 'utf8');
    const lines = content.trim().split('\n').filter(Boolean);
    
    return lines
      .slice(-limit)
      .map(line => {
        try {
          return JSON.parse(line);
        } catch {
          return null;
        }
      })
      .filter(Boolean);
  } catch (e) {
    return [];
  }
}

/**
 * CLI: View audit log
 */
async function main() {
  const entries = readAuditLog(50);
  
  if (entries.length === 0) {
    console.log('📋 沒有審計記錄');
    return;
  }
  
  console.log(`📋 審計記錄 (最近 ${entries.length} 筆)`);
  console.log('═'.repeat(60));
  
  for (const entry of entries) {
    const time = new Date(entry.timestamp).toLocaleString();
    const status = entry.success === false ? '❌' : '✅';
    console.log(`${status} [${time}] ${entry.action}`);
    
    if (entry.wallet) console.log(`   錢包: ${entry.wallet}`);
    if (entry.to) console.log(`   收件人: ${entry.to}`);
    if (entry.error) console.log(`   錯誤: ${entry.error}`);
  }
}

// Export for use as module
module.exports = {
  ACTIONS,
  logAudit,
  readAuditLog,
  mask,
  maskEmail,
};

// Run CLI if executed directly
if (require.main === module) {
  main().catch(console.error);
}
