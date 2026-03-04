/**
 * Audit - Cryptographic Audit Trail
 *
 * Hash-chained operation logs with tamper detection
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { promisify } = require('util');

const appendFile = promisify(fs.appendFile);
const readFile = promisify(fs.readFile);
const mkdir = promisify(fs.mkdir);

class Audit {
  constructor(auditPath) {
    this.auditPath = auditPath || path.join(process.env.HOME, '.agentguard', 'audit');
    this.lastHash = null;
  }

  /**
   * Initialize audit directory
   */
  async init() {
    await mkdir(this.auditPath, { recursive: true });
  }

  /**
   * Compute hash of entry
   */
  hash(prevHash, data) {
    const content = prevHash + JSON.stringify(data);
    return crypto.createHash('sha256').update(content).digest('hex');
  }

  /**
   * Log an operation
   */
  async log(agentId, operation, details = {}) {
    await this.init();

    const date = new Date().toISOString().split('T')[0];
    const logFile = path.join(this.auditPath, `${agentId}-${date}.log`);

    // Load last hash from file if needed
    if (!this.lastHash && fs.existsSync(logFile)) {
      const lines = (await readFile(logFile, 'utf8')).trim().split('\n');
      if (lines.length > 0) {
        const lastLine = JSON.parse(lines[lines.length - 1]);
        this.lastHash = lastLine.hash;
      }
    }

    const prevHash = this.lastHash || '0'.repeat(64);

    const entry = {
      timestamp: new Date().toISOString(),
      agentId,
      operation,
      details,
      prevHash
    };

    entry.hash = this.hash(prevHash, entry);

    // Append to log
    await appendFile(logFile, JSON.stringify(entry) + '\n');

    // Update last hash
    this.lastHash = entry.hash;

    return entry;
  }

  /**
   * Get logs for agent
   */
  async getLogs(agentId, options = {}) {
    const { from, to, last, operation } = options;

    let logFiles = [];

    if (from || to) {
      // Date range query
      const files = fs.readdirSync(this.auditPath);
      logFiles = files
        .filter(f => f.startsWith(`${agentId}-`) && f.endsWith('.log'))
        .filter(f => {
          const date = f.replace(`${agentId}-`, '').replace('.log', '');
          if (from && date < from) return false;
          if (to && date > to) return false;
          return true;
        })
        .map(f => path.join(this.auditPath, f));
    } else {
      // Today's log
      const today = new Date().toISOString().split('T')[0];
      const logFile = path.join(this.auditPath, `${agentId}-${today}.log`);
      if (fs.existsSync(logFile)) {
        logFiles = [logFile];
      }
    }

    let entries = [];

    for (const file of logFiles) {
      if (!fs.existsSync(file)) continue;
      const lines = (await readFile(file, 'utf8')).trim().split('\n');
      for (const line of lines) {
        if (!line) continue;
        try {
          entries.push(JSON.parse(line));
        } catch (e) {
          // Skip malformed lines
        }
      }
    }

    // Filter by operation
    if (operation) {
      entries = entries.filter(e => e.operation === operation);
    }

    // Limit results
    if (last) {
      entries = entries.slice(-last);
    }

    return entries;
  }

  /**
   * Verify log integrity
   */
  async verify(agentId, date) {
    const logFile = path.join(this.auditPath, `${agentId}-${date}.log`);

    if (!fs.existsSync(logFile)) {
      return { valid: false, reason: 'Log file not found' };
    }

    const lines = (await readFile(logFile, 'utf8')).trim().split('\n');
    let prevHash = '0'.repeat(64);

    for (let i = 0; i < lines.length; i++) {
      const entry = JSON.parse(lines[i]);

      // Verify hash chain
      const expectedHash = this.hash(entry.prevHash, {
        timestamp: entry.timestamp,
        agentId: entry.agentId,
        operation: entry.operation,
        details: entry.details,
        prevHash: entry.prevHash
      });

      if (entry.hash !== expectedHash) {
        return {
          valid: false,
          reason: `Hash mismatch at line ${i + 1}`,
          line: i + 1
        };
      }

      if (entry.prevHash !== prevHash) {
        return {
          valid: false,
          reason: `Chain broken at line ${i + 1}`,
          line: i + 1
        };
      }

      prevHash = entry.hash;
    }

    return { valid: true, entries: lines.length };
  }

  /**
   * Export logs as JSON
   */
  async export(agentId, options = {}) {
    const logs = await this.getLogs(agentId, options);
    return {
      agentId,
      exportedAt: new Date().toISOString(),
      entries: logs,
      count: logs.length
    };
  }

  /**
   * Get statistics for agent
   */
  async stats(agentId, days = 7) {
    const stats = {
      totalOperations: 0,
      byOperation: {},
      byDay: {},
      approvals: 0,
      denials: 0
    };

    const today = new Date();
    for (let i = 0; i < days; i++) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];

      const logs = await this.getLogs(agentId, { from: dateStr, to: dateStr });

      stats.byDay[dateStr] = logs.length;
      stats.totalOperations += logs.length;

      for (const entry of logs) {
        stats.byOperation[entry.operation] = (stats.byOperation[entry.operation] || 0) + 1;
        if (entry.details.approved === true) stats.approvals++;
        if (entry.details.approved === false) stats.denials++;
      }
    }

    return stats;
  }
}

module.exports = Audit;
