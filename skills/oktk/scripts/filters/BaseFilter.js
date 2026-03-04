/**
 * BaseFilter - Abstract base class for all oktk filters
 */

class BaseFilter {
  constructor(context = {}) {
    this.context = {
      compressionLevel: 'summary', // minimal, summary, detailed, raw
      ...context
    };
  }

  /**
   * Apply filter to output - must be implemented by subclasses
   * @param {string} output - Raw command output
   * @param {object} context - Additional context (exitCode, command, etc.)
   * @returns {string} Filtered output
   */
  async apply(output, context = {}) {
    throw new Error('apply() must be implemented by subclass');
  }

  /**
   * Compress output based on compression level
   */
  compress(output, level = this.context.compressionLevel) {
    switch (level) {
      case 'minimal':
        return this.oneLiner(output);
      case 'summary':
        return this.compact(output);
      case 'detailed':
        return this.filtered(output);
      case 'raw':
        return output;
      default:
        return this.compact(output);
    }
  }

  /**
   * One-liner summary (minimal level)
   */
  oneLiner(output) {
    return output.split('\n')[0] || '';
  }

  /**
   * Compact summary (default level)
   */
  compact(output) {
    return this.filtered(output);
  }

  /**
   * Filtered output (detailed level)
   */
  filtered(output) {
    // Default: just remove excessive whitespace
    return output
      .replace(/\n{3,}/g, '\n\n')
      .trim();
  }

  /**
   * Remove ANSI color codes
   */
  removeAnsiCodes(text) {
    return text.replace(/\x1b\[[0-9;]*m/g, '');
  }

  /**
   * Detect if output is binary
   */
  isBinary(output) {
    // Check for non-UTF8 sequences
    return /[\x00-\x08\x0E-\x1F\x7F-\xFF]{10,}/.test(output);
  }

  /**
   * Detect if output contains errors
   */
  hasErrors(output) {
    const errorPatterns = [
      /error/i,
      /failed/i,
      /exception/i,
      /fatal/i,
      /cannot/i,
      /unable/i
    ];
    return errorPatterns.some(pattern => pattern.test(output));
  }

  /**
   * Truncate large output
   */
  truncate(output, maxSize = 50000) {
    if (output.length <= maxSize) {
      return output;
    }

    const keepStart = Math.floor(maxSize / 2);
    const keepEnd = Math.floor(maxSize / 2);

    return [
      output.substring(0, keepStart),
      `\n\n[... ${output.length - maxSize} characters hidden ...]\n\n`,
      output.substring(output.length - keepEnd)
    ].join('');
  }

  /**
   * Redact sensitive patterns
   */
  redactSecrets(output) {
    return output
      .replace(/api[_-]?key[=:]\s*[^\s]+/gi, 'api_key=***')
      .replace(/secret[=:]\s*[^\s]+/gi, 'secret=***')
      .replace(/token[=:]\s*[^\s]+/gi, 'token=***')
      .replace(/password[=:]\s*[^\s]+/gi, 'password=***')
      .replace(/bearer\s+[^\s]+/gi, 'bearer ***');
  }

  /**
   * Count lines in output
   */
  countLines(output) {
    return output.split('\n').filter(line => line.trim()).length;
  }

  /**
   * Format bytes to human readable
   */
  formatBytes(bytes) {
    const sizes = ['B', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 B';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  }

  /**
   * Format duration to human readable
   */
  formatDuration(ms) {
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${Math.floor(ms / 60000)}m ${Math.floor((ms % 60000) / 1000)}s`;
  }

  /**
   * Extract key-value pairs from output
   */
  extractKeyValue(output, separator = '=') {
    const lines = output.split('\n');
    const result = {};

    for (const line of lines) {
      if (line.includes(separator)) {
        const [key, value] = line.split(separator).map(s => s.trim());
        if (key) result[key] = value;
      }
    }

    return result;
  }

  /**
   * Group lines by pattern
   */
  groupByPattern(output, pattern) {
    const lines = output.split('\n');
    const groups = {};

    for (const line of lines) {
      const match = line.match(pattern);
      if (match && match[1]) {
        const key = match[1];
        if (!groups[key]) groups[key] = [];
        groups[key].push(line);
      }
    }

    return groups;
  }

  /**
   * Validate output is safe to filter
   * Returns true if output can be safely filtered
   */
  canFilter(output) {
    // Don't filter binary output
    if (this.isBinary(output)) {
      return false;
    }

    // Don't filter if output is very small
    if (output.length < 100) {
      return false;
    }

    return true;
  }
}

module.exports = BaseFilter;
