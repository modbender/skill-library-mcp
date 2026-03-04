/**
 * Audit Logging System
 * Immutable append-only log for compliance & debugging
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

class AuditLogger {
  constructor(logDir = './audit-logs') {
    this.logDir = logDir;
    this.ensureLogDir();
    this.currentFile = this.getCurrentLogFile();
  }

  ensureLogDir() {
    if (!fs.existsSync(this.logDir)) {
      fs.mkdirSync(this.logDir, { recursive: true });
    }
  }

  getCurrentLogFile() {
    const date = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
    return path.join(this.logDir, `audit-${date}.jsonl`);
  }

  /**
   * Create audit entry with hash chain for integrity
   */
  createEntry(event, data) {
    const timestamp = new Date().toISOString();
    
    // Get previous hash for chain integrity
    const previousHash = this.getLastHash();
    
    const entry = {
      timestamp,
      event,
      data,
      previousHash,
      sequence: this.getNextSequence()
    };

    // Calculate entry hash
    entry.hash = this.hashEntry(entry);

    return entry;
  }

  hashEntry(entry) {
    const data = JSON.stringify({
      timestamp: entry.timestamp,
      event: entry.event,
      data: entry.data,
      previousHash: entry.previousHash,
      sequence: entry.sequence
    });
    
    return crypto.createHash('sha256').update(data).digest('hex');
  }

  getLastHash() {
    const currentFile = this.getCurrentLogFile();
    if (!fs.existsSync(currentFile)) {
      return '0000000000000000000000000000000000000000000000000000000000000000';
    }

    const lines = fs.readFileSync(currentFile, 'utf8').trim().split('\n');
    if (lines.length === 0 || lines[0] === '') {
      return '0000000000000000000000000000000000000000000000000000000000000000';
    }

    const lastLine = lines[lines.length - 1];
    const lastEntry = JSON.parse(lastLine);
    return lastEntry.hash;
  }

  getNextSequence() {
    const currentFile = this.getCurrentLogFile();
    if (!fs.existsSync(currentFile)) {
      return 1;
    }

    const lines = fs.readFileSync(currentFile, 'utf8').trim().split('\n');
    if (lines.length === 0 || lines[0] === '') {
      return 1;
    }

    const lastLine = lines[lines.length - 1];
    const lastEntry = JSON.parse(lastLine);
    return (lastEntry.sequence || 0) + 1;
  }

  /**
   * Append entry to log (atomic, append-only)
   */
  log(event, data) {
    const entry = this.createEntry(event, data);
    const line = JSON.stringify(entry) + '\n';
    
    // Atomic append
    fs.appendFileSync(this.currentFile, line);
    
    return entry;
  }

  /**
   * Convenience methods for common events
   */
  logAuth(agentId, success, reason = null) {
    return this.log('auth', { agentId, success, reason });
  }

  logBalanceCheck(agentId, address, balance) {
    return this.log('balance_check', { agentId, address, balance });
  }

  logPaymentRequest(agentId, recipient, amount, approved) {
    return this.log('payment_request', { agentId, recipient, amount, approved });
  }

  logPaymentExecuted(agentId, recipient, amount, txHash, gasCost) {
    return this.log('payment_executed', { 
      agentId, 
      recipient, 
      amount, 
      txHash, 
      gasCost,
      explorerUrl: `https://polygonscan.com/tx/${txHash}`
    });
  }

  logPaymentFailed(agentId, recipient, amount, error) {
    return this.log('payment_failed', { agentId, recipient, amount, error });
  }

  logRateLimitHit(agentId, reason) {
    return this.log('rate_limit', { agentId, reason });
  }

  /**
   * Query logs (read-only)
   */
  query(filter = {}) {
    const files = fs.readdirSync(this.logDir)
      .filter(f => f.startsWith('audit-') && f.endsWith('.jsonl'))
      .sort()
      .reverse(); // Most recent first

    const results = [];
    const limit = filter.limit || 100;

    for (const file of files) {
      const filePath = path.join(this.logDir, file);
      const lines = fs.readFileSync(filePath, 'utf8').trim().split('\n');
      
      for (const line of lines.reverse()) {
        if (line === '') continue;
        
        const entry = JSON.parse(line);
        
        // Apply filters
        if (filter.event && entry.event !== filter.event) continue;
        if (filter.agentId && entry.data.agentId !== filter.agentId) continue;
        if (filter.since && entry.timestamp < filter.since) continue;
        
        results.push(entry);
        
        if (results.length >= limit) {
          return results;
        }
      }
    }

    return results;
  }

  /**
   * Verify log integrity (hash chain validation)
   */
  verify() {
    const files = fs.readdirSync(this.logDir)
      .filter(f => f.startsWith('audit-') && f.endsWith('.jsonl'))
      .sort();

    let previousHash = '0000000000000000000000000000000000000000000000000000000000000000';
    let totalEntries = 0;
    let expectedSequence = 1;

    for (const file of files) {
      const filePath = path.join(this.logDir, file);
      const lines = fs.readFileSync(filePath, 'utf8').trim().split('\n');
      
      for (const line of lines) {
        if (line === '') continue;
        
        const entry = JSON.parse(line);
        totalEntries++;

        // Verify hash chain
        if (entry.previousHash !== previousHash) {
          return {
            valid: false,
            error: `Hash chain broken at sequence ${entry.sequence}`,
            expected: previousHash,
            actual: entry.previousHash
          };
        }

        // Verify hash
        const calculatedHash = this.hashEntry(entry);
        if (entry.hash !== calculatedHash) {
          return {
            valid: false,
            error: `Hash mismatch at sequence ${entry.sequence}`,
            expected: calculatedHash,
            actual: entry.hash
          };
        }

        // Verify sequence (within file)
        if (entry.sequence !== expectedSequence) {
          return {
            valid: false,
            error: `Sequence gap at ${entry.sequence}, expected ${expectedSequence}`
          };
        }

        previousHash = entry.hash;
        expectedSequence++;
      }
    }

    return {
      valid: true,
      totalEntries,
      lastHash: previousHash
    };
  }

  /**
   * Get summary stats
   */
  getStats() {
    const entries = this.query({ limit: 10000 });
    const now = Date.now();
    const last24h = new Date(now - 24 * 60 * 60 * 1000).toISOString();

    return {
      totalEntries: entries.length,
      last24h: entries.filter(e => e.timestamp > last24h).length,
      byEvent: entries.reduce((acc, e) => {
        acc[e.event] = (acc[e.event] || 0) + 1;
        return acc;
      }, {}),
      integrity: this.verify()
    };
  }
}

module.exports = { AuditLogger };
