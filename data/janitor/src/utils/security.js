/**
 * Security Utilities
 *
 * Input validation and sanitization functions to prevent:
 * - Path traversal attacks
 * - Command injection
 * - Shell injection
 * - URL injection
 */

const path = require('path');
const os = require('os');

class SecurityUtils {
  /**
   * Validate file path to prevent traversal
   * @param {string} filePath - Path to validate
   * @param {string} baseDir - Base directory (must be within this)
   * @returns {boolean} True if valid
   * @throws {Error} If invalid
   */
  static validatePath(filePath, baseDir) {
    // Check for null/undefined
    if (!filePath || !baseDir) {
      throw new Error('Path and baseDir are required');
    }

    // Resolve to absolute paths
    const absolutePath = path.resolve(filePath);
    const absoluteBase = path.resolve(baseDir);

    // Check for path traversal sequences
    if (filePath.includes('..')) {
      throw new Error(`Path traversal detected: ${filePath}`);
    }

    // Ensure path is within base directory
    if (!absolutePath.startsWith(absoluteBase)) {
      throw new Error(`Path outside base directory: ${filePath} not in ${baseDir}`);
    }

    // Check for suspicious patterns
    const suspiciousPatterns = [
      '/etc/',
      '/var/',
      '/usr/',
      '/bin/',
      '/sbin/',
      '/boot/',
      '/root/',
      'C:\\Windows',
      'C:\\Program Files'
    ];

    for (const pattern of suspiciousPatterns) {
      if (absolutePath.includes(pattern) && !absoluteBase.includes(pattern)) {
        throw new Error(`Suspicious system path detected: ${absolutePath}`);
      }
    }

    return true;
  }

  /**
   * Sanitize string for use in shell commands
   * @param {string} input - Input to sanitize
   * @returns {string} Sanitized string
   */
  static sanitizeShellArg(input) {
    if (typeof input !== 'string') {
      throw new Error('Input must be a string');
    }

    // Remove or escape dangerous characters
    return input
      .replace(/[\$`"\\]/g, '\\$&')  // Escape shell special chars
      .replace(/\n/g, '')             // Remove newlines
      .replace(/\r/g, '')             // Remove carriage returns
      .replace(/;/g, '')              // Remove command separators
      .replace(/\|/g, '')             // Remove pipes
      .replace(/&/g, '')              // Remove background operators
      .replace(/>/g, '')              // Remove redirects
      .replace(/</ g, '');            // Remove redirects
  }

  /**
   * Validate URL
   * @param {string} url - URL to validate
   * @param {string[]} allowedProtocols - Allowed protocols (default: ['https:'])
   * @returns {boolean} True if valid
   * @throws {Error} If invalid
   */
  static validateUrl(url, allowedProtocols = ['https:']) {
    if (!url) {
      throw new Error('URL is required');
    }

    let parsedUrl;
    try {
      parsedUrl = new URL(url);
    } catch (e) {
      throw new Error(`Invalid URL format: ${url}`);
    }

    // Check protocol
    if (!allowedProtocols.includes(parsedUrl.protocol)) {
      throw new Error(`Invalid protocol ${parsedUrl.protocol}. Allowed: ${allowedProtocols.join(', ')}`);
    }

    // Check for localhost/private IPs
    const privatePatterns = [
      '127.0.0.1',
      'localhost',
      '0.0.0.0',
      '10.',
      '172.16.',
      '192.168.'
    ];

    for (const pattern of privatePatterns) {
      if (parsedUrl.hostname.includes(pattern)) {
        throw new Error(`Private/local URL not allowed: ${parsedUrl.hostname}`);
      }
    }

    return true;
  }

  /**
   * Validate numeric value within range
   * @param {number} value - Value to validate
   * @param {number} min - Minimum value
   * @param {number} max - Maximum value
   * @param {string} name - Parameter name for error messages
   * @returns {boolean} True if valid
   * @throws {Error} If invalid
   */
  static validateNumber(value, min, max, name = 'value') {
    if (typeof value !== 'number' || isNaN(value)) {
      throw new Error(`${name} must be a valid number`);
    }

    if (value < min || value > max) {
      throw new Error(`${name} must be between ${min} and ${max} (got ${value})`);
    }

    return true;
  }

  /**
   * Validate email format (basic)
   * @param {string} email - Email to validate
   * @returns {boolean} True if valid
   * @throws {Error} If invalid
   */
  static validateEmail(email) {
    if (!email || typeof email !== 'string') {
      throw new Error('Email is required');
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      throw new Error(`Invalid email format: ${email}`);
    }

    return true;
  }

  /**
   * Sanitize filename for safe filesystem operations
   * @param {string} filename - Filename to sanitize
   * @returns {string} Safe filename
   */
  static sanitizeFilename(filename) {
    if (!filename || typeof filename !== 'string') {
      throw new Error('Filename is required');
    }

    return filename
      .replace(/[<>:"|?*]/g, '')      // Windows forbidden chars
      .replace(/\.\./g, '')            // Path traversal
      .replace(/^\./, '')              // Leading dot (hidden files)
      .replace(/\//g, '-')             // Path separators
      .replace(/\\/g, '-')             // Windows path separators
      .substring(0, 255);              // Max filename length
  }

  /**
   * Validate Git repository URL
   * @param {string} repoUrl - Git repo URL
   * @returns {boolean} True if valid
   * @throws {Error} If invalid
   */
  static validateGitRepo(repoUrl) {
    if (!repoUrl || typeof repoUrl !== 'string') {
      throw new Error('Repository URL is required');
    }

    // Support HTTPS and SSH
    const httpsPattern = /^https:\/\/[a-zA-Z0-9.-]+\/[a-zA-Z0-9._-]+\/[a-zA-Z0-9._-]+(\.git)?$/;
    const sshPattern = /^git@[a-zA-Z0-9.-]+:[a-zA-Z0-9._-]+\/[a-zA-Z0-9._-]+(\.git)?$/;

    if (!httpsPattern.test(repoUrl) && !sshPattern.test(repoUrl)) {
      throw new Error(`Invalid Git repository URL format: ${repoUrl}`);
    }

    return true;
  }

  /**
   * Check if deletion count is within safe limits
   * @param {number} count - Number of files to delete
   * @param {number} maxLimit - Maximum allowed (default: 1000)
   * @returns {boolean} True if safe
   * @throws {Error} If unsafe
   */
  static validateDeletionCount(count, maxLimit = 1000) {
    this.validateNumber(count, 0, maxLimit, 'deletion count');

    if (count > maxLimit) {
      throw new Error(
        `SAFETY: Refusing to delete ${count} files. ` +
        `Limit is ${maxLimit}. This may indicate misconfiguration.`
      );
    }

    return true;
  }

  /**
   * Validate directory exists and is accessible
   * @param {string} dirPath - Directory path
   * @param {string} baseDir - Base directory for validation
   * @returns {boolean} True if valid
   * @throws {Error} If invalid
   */
  static validateDirectory(dirPath, baseDir) {
    const fs = require('fs');

    // Validate path first
    this.validatePath(dirPath, baseDir);

    // Check exists
    if (!fs.existsSync(dirPath)) {
      throw new Error(`Directory does not exist: ${dirPath}`);
    }

    // Check is directory
    const stats = fs.statSync(dirPath);
    if (!stats.isDirectory()) {
      throw new Error(`Path is not a directory: ${dirPath}`);
    }

    return true;
  }

  /**
   * Create safe execution options for child_process
   * @param {number} timeout - Timeout in milliseconds
   * @returns {object} Execution options
   */
  static getSafeExecOptions(timeout = 60000) {
    return {
      timeout: timeout,
      maxBuffer: 50 * 1024 * 1024,  // 50MB max output
      shell: '/bin/bash',             // Explicit shell
      env: {
        ...process.env,
        PATH: process.env.PATH || '/usr/bin:/bin:/usr/local/bin'
      }
    };
  }

  /**
   * Log security event
   * @param {string} event - Event type
   * @param {string} message - Event message
   * @param {object} data - Additional data
   */
  static logSecurityEvent(event, message, data = {}) {
    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      event,
      message,
      ...data
    };

    console.warn('[SECURITY]', JSON.stringify(logEntry));
  }
}

module.exports = SecurityUtils;
