/**
 * ClawGuard Audit Trail
 * Append-only JSONL logging for all security decisions
 */

import { appendFileSync, readFileSync, existsSync, mkdirSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';

const AUDIT_DIR = join(homedir(), '.clawguard');
const AUDIT_PATH = join(AUDIT_DIR, 'audit.jsonl');

/**
 * Ensure audit directory exists
 */
function ensureAuditDir() {
    if (!existsSync(AUDIT_DIR)) {
        mkdirSync(AUDIT_DIR, { recursive: true });
    }
}

/**
 * Log a security check to the audit trail
 * @param {Object} entry - Audit entry
 * @param {string} entry.type - Check type (url, command, skill, message)
 * @param {string} entry.input - Input that was checked
 * @param {string} entry.verdict - safe, warning, blocked
 * @param {Object} entry.threat - Threat details (if any)
 * @param {number} entry.duration - Duration in milliseconds
 */
export function logAudit(entry) {
    ensureAuditDir();
    
    const auditEntry = {
        timestamp: new Date().toISOString(),
        type: entry.type,
        input: entry.input,
        verdict: entry.verdict,
        threat: entry.threat || null,
        duration_ms: entry.duration,
        metadata: entry.metadata || {}
    };
    
    try {
        appendFileSync(AUDIT_PATH, JSON.stringify(auditEntry) + '\n', 'utf8');
    } catch (error) {
        // Silent fail - don't break main functionality
        console.error(`Audit log error: ${error.message}`);
    }
}

/**
 * Read audit log entries
 * @param {Object} options - Filter options
 * @param {number} options.lines - Number of recent lines to return
 * @param {boolean} options.today - Only return today's entries
 * @returns {Array} Array of audit entries
 */
export function readAudit(options = {}) {
    if (!existsSync(AUDIT_PATH)) {
        return [];
    }
    
    const content = readFileSync(AUDIT_PATH, 'utf8');
    const lines = content.split('\n').filter(l => l.trim());
    
    let entries = lines.map(line => {
        try {
            return JSON.parse(line);
        } catch {
            return null;
        }
    }).filter(e => e !== null);
    
    // Filter by today if requested
    if (options.today) {
        const today = new Date().toISOString().split('T')[0];
        entries = entries.filter(e => e.timestamp.startsWith(today));
    }
    
    // Limit to recent N entries
    if (options.lines) {
        entries = entries.slice(-options.lines);
    }
    
    return entries;
}

/**
 * Get audit statistics
 */
export function getAuditStats() {
    if (!existsSync(AUDIT_PATH)) {
        return {
            total: 0,
            today: 0,
            blocked: 0,
            warnings: 0,
            safe: 0
        };
    }
    
    const entries = readAudit();
    const today = new Date().toISOString().split('T')[0];
    
    return {
        total: entries.length,
        today: entries.filter(e => e.timestamp.startsWith(today)).length,
        blocked: entries.filter(e => e.verdict === 'blocked').length,
        warnings: entries.filter(e => e.verdict === 'warning').length,
        safe: entries.filter(e => e.verdict === 'safe').length
    };
}
