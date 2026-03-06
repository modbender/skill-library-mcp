/**
 * Configuration Manager
 *
 * Manages Janitor configuration via CLI
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

class ConfigManager {
  constructor() {
    this.configPath = path.join(os.homedir(), '.openclaw', 'janitor-config.json');
    this.config = this._loadConfig();
  }

  /**
   * Get configuration value
   * @param {string} key - Configuration key (dot notation supported)
   * @returns {*} Configuration value
   */
  get(key) {
    return this._getNestedValue(this.config, key);
  }

  /**
   * Set configuration value
   * @param {string} key - Configuration key (dot notation supported)
   * @param {*} value - Value to set
   * @returns {boolean} Success
   */
  set(key, value) {
    try {
      this._setNestedValue(this.config, key, value);
      this._saveConfig();
      return true;
    } catch (error) {
      console.error('Failed to set config:', error.message);
      return false;
    }
  }

  /**
   * Delete configuration key
   * @param {string} key - Configuration key
   * @returns {boolean} Success
   */
  delete(key) {
    try {
      this._deleteNestedValue(this.config, key);
      this._saveConfig();
      return true;
    } catch (error) {
      console.error('Failed to delete config:', error.message);
      return false;
    }
  }

  /**
   * List all configuration
   * @param {string} prefix - Optional prefix filter
   * @returns {Object} Configuration
   */
  list(prefix = null) {
    if (prefix) {
      const value = this._getNestedValue(this.config, prefix);
      return value || {};
    }

    return this.config;
  }

  /**
   * Reset configuration to defaults
   */
  reset() {
    this.config = this._getDefaultConfig();
    this._saveConfig();
  }

  /**
   * Export configuration to file
   * @param {string} filePath - Export file path
   */
  exportConfig(filePath) {
    fs.writeFileSync(filePath, JSON.stringify(this.config, null, 2), 'utf-8');
  }

  /**
   * Import configuration from file
   * @param {string} filePath - Import file path
   */
  importConfig(filePath) {
    const imported = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
    this.config = { ...this.config, ...imported };
    this._saveConfig();
  }

  /**
   * Load configuration from file
   * @private
   */
  _loadConfig() {
    if (!fs.existsSync(this.configPath)) {
      return this._getDefaultConfig();
    }

    try {
      return JSON.parse(fs.readFileSync(this.configPath, 'utf-8'));
    } catch (error) {
      console.warn('Failed to load config, using defaults:', error.message);
      return this._getDefaultConfig();
    }
  }

  /**
   * Save configuration to file
   * @private
   */
  _saveConfig() {
    const dir = path.dirname(this.configPath);

    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    fs.writeFileSync(this.configPath, JSON.stringify(this.config, null, 2), 'utf-8');
  }

  /**
   * Get default configuration
   * @private
   */
  _getDefaultConfig() {
    return {
      enabled: true,
      unusedFileAgeDays: 7,
      sessionManagement: {
        enabled: true,
        monitoring: {
          intervalMinutes: 5,
          alertThreshold: 80,
          emergencyThreshold: 95
        },
        pruning: {
          maxSessionAge: 7,
          maxContextTokens: 160000,
          keepRecentHours: 24,
          keepMinimumSessions: 5
        },
        archiving: {
          enabled: true,
          retentionDays: 30,
          compression: true,
          backupToGithub: false
        },
        preservation: {
          pinned: true,
          highEngagement: true,
          minMessagesForImportant: 10
        },
        notifications: {
          enabled: false,
          channels: ['log'],
          onCleanup: true,
          onEmergency: true
        }
      }
    };
  }

  /**
   * Get nested value using dot notation
   * @private
   */
  _getNestedValue(obj, key) {
    const keys = key.split('.');
    let value = obj;

    for (const k of keys) {
      if (value === undefined || value === null) {
        return undefined;
      }
      value = value[k];
    }

    return value;
  }

  /**
   * Set nested value using dot notation
   * @private
   */
  _setNestedValue(obj, key, value) {
    const keys = key.split('.');
    const lastKey = keys.pop();
    let current = obj;

    for (const k of keys) {
      if (!current[k] || typeof current[k] !== 'object') {
        current[k] = {};
      }
      current = current[k];
    }

    // Try to parse value
    let parsedValue = value;
    if (value === 'true') parsedValue = true;
    else if (value === 'false') parsedValue = false;
    else if (value === 'null') parsedValue = null;
    else if (!isNaN(value) && value !== '') parsedValue = Number(value);

    current[lastKey] = parsedValue;
  }

  /**
   * Delete nested value using dot notation
   * @private
   */
  _deleteNestedValue(obj, key) {
    const keys = key.split('.');
    const lastKey = keys.pop();
    let current = obj;

    for (const k of keys) {
      if (!current[k]) {
        return;
      }
      current = current[k];
    }

    delete current[lastKey];
  }

  /**
   * Display configuration in nice format
   */
  display(prefix = null) {
    const config = this.list(prefix);

    console.log('\nJanitor Configuration:');
    console.log('='.repeat(60));

    this._displayObject(config, prefix || 'janitor');

    console.log('='.repeat(60));
    console.log(`\nConfig file: ${this.configPath}\n`);
  }

  /**
   * Display object recursively
   * @private
   */
  _displayObject(obj, prefix, indent = 0) {
    const spaces = '  '.repeat(indent);

    for (const [key, value] of Object.entries(obj)) {
      const fullKey = prefix ? `${prefix}.${key}` : key;

      if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
        console.log(`${spaces}${key}:`);
        this._displayObject(value, fullKey, indent + 1);
      } else {
        const valueStr = JSON.stringify(value);
        console.log(`${spaces}${key}: ${valueStr}`);
      }
    }
  }

  /**
   * Validate configuration
   */
  validate() {
    const errors = [];

    // Validate numeric ranges
    const alertThreshold = this.get('sessionManagement.monitoring.alertThreshold');
    if (alertThreshold < 0 || alertThreshold > 100) {
      errors.push('alertThreshold must be between 0 and 100');
    }

    const emergencyThreshold = this.get('sessionManagement.monitoring.emergencyThreshold');
    if (emergencyThreshold < 0 || emergencyThreshold > 100) {
      errors.push('emergencyThreshold must be between 0 and 100');
    }

    if (emergencyThreshold <= alertThreshold) {
      errors.push('emergencyThreshold must be greater than alertThreshold');
    }

    // Validate positive numbers
    const intervalMinutes = this.get('sessionManagement.monitoring.intervalMinutes');
    if (intervalMinutes <= 0) {
      errors.push('intervalMinutes must be positive');
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }
}

module.exports = ConfigManager;
