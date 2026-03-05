/**
 * NadMail Audit Logger
 * Records security-relevant operations (without sensitive data)
 */

const fs = require('fs');
const path = require('path');

const CONFIG_DIR = path.join(process.env.HOME, '.nadmail');
const AUDIT_FILE = path.join(CONFIG_DIR, 'audit.log');

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

function mask(value, showChars = 4) {
  if (!value) return null;
  if (value.length <= showChars * 2) return '***';
  return `${value.slice(0, showChars)}...${value.slice(-showChars)}`;
}

function maskEmail(email) {
  if (!email) return null;
  const [local, domain] = email.split('@');
  if (!domain) return mask(email);
  return `${mask(local, 2)}@${domain}`;
}

function logAudit(action, details = {}) {
  try {
    if (!fs.existsSync(CONFIG_DIR)) {
      fs.mkdirSync(CONFIG_DIR, { recursive: true, mode: 0o700 });
    }

    const sanitized = {};

    if (details.wallet) sanitized.wallet = mask(details.wallet, 6);
    if (details.to) sanitized.to = maskEmail(details.to);
    if (details.from) sanitized.from = maskEmail(details.from);
    if (details.email_id) sanitized.email_id = mask(details.email_id, 4);
    if (typeof details.success !== 'undefined') sanitized.success = details.success;
    if (details.error) {
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
    // Silently ignore audit errors
  }
}

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

async function main() {
  const entries = readAuditLog(50);

  if (entries.length === 0) {
    console.log('No audit records.');
    return;
  }

  console.log(`Audit log (last ${entries.length} entries)`);
  console.log('='.repeat(60));

  for (const entry of entries) {
    const time = new Date(entry.timestamp).toLocaleString();
    const status = entry.success === false ? 'FAIL' : 'OK';
    console.log(`[${status}] [${time}] ${entry.action}`);

    if (entry.wallet) console.log(`   Wallet: ${entry.wallet}`);
    if (entry.to) console.log(`   To: ${entry.to}`);
    if (entry.error) console.log(`   Error: ${entry.error}`);
  }
}

module.exports = {
  ACTIONS,
  logAudit,
  readAuditLog,
  mask,
  maskEmail,
};

if (require.main === module) {
  main().catch(console.error);
}
