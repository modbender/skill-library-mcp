/**
 * ClawGuard (ClawGuard)
 * Main library exports
 */

export { ClawGuardDatabase, getDatabase, closeDatabase } from './database.js';
export { Detector, getDetector, RESULT, EXIT_CODE } from './detector.js';
export { scanMcpConfigs, getMcpConfigPaths, auditServer, parseMcpConfig } from './mcp-scanner.js';
export { logAudit, readAudit, getAuditStats } from './audit.js';
export { loadConfig, saveConfig, getConfig, updateConfig } from './config.js';
export { formatApprovalMessage } from './discord-approval.js';

// Convenience function for simple checks
import { getDetector } from './detector.js';

/**
 * Quick check function for integration
 * @param {string} input - The input to check
 * @param {string} type - Optional type: url, skill, command, message
 * @returns {Promise<Object>} Detection result
 */
export async function check(input, type = null) {
    const detector = getDetector();
    return detector.check(input, type);
}

/**
 * Check a URL
 * @param {string} url - URL to check
 * @returns {Promise<Object>} Detection result
 */
export async function checkUrl(url) {
    const detector = getDetector();
    return detector.checkUrl(url);
}

/**
 * Check a skill
 * @param {string} name - Skill name
 * @param {string} author - Optional author
 * @returns {Promise<Object>} Detection result
 */
export async function checkSkill(name, author = null) {
    const detector = getDetector();
    return detector.checkSkill(name, author);
}

/**
 * Check a command
 * @param {string} command - Shell command to check
 * @returns {Promise<Object>} Detection result
 */
export async function checkCommand(command) {
    const detector = getDetector();
    return detector.checkCommand(command);
}

/**
 * Check message content
 * @param {string} message - Message to check for threats
 * @returns {Promise<Object>} Detection result
 */
export async function checkMessage(message) {
    const detector = getDetector();
    return detector.checkMessage(message);
}

// Default export
export default {
    check,
    checkUrl,
    checkSkill,
    checkCommand,
    checkMessage
};
