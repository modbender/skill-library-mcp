/**
 * ClawGuard Configuration Manager
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';

const CONFIG_DIR = join(homedir(), '.clawguard');
const CONFIG_PATH = join(CONFIG_DIR, 'config.json');

const DEFAULT_CONFIG = {
    level: 0,  // Security level: 0=silent (default), 1=cautious, 2=strict, 3=paranoid
    discord: {
        enabled: false,
        channelId: null,
        timeout: 60000  // 60 seconds default
    },
    audit: {
        enabled: true,
        path: join(CONFIG_DIR, 'audit.jsonl')
    },
    sync: {
        repoUrl: 'https://github.com/jugaad-lab/clawguard',
        branch: 'main',
        autoSync: true,
        syncIntervalHours: 24
    },
    detection: {
        thresholds: {
            block: 0.9,
            warn: 0.7,
            educate: 0.5
        }
    }
};

/**
 * Ensure config directory exists
 */
function ensureConfigDir() {
    if (!existsSync(CONFIG_DIR)) {
        mkdirSync(CONFIG_DIR, { recursive: true });
    }
}

/**
 * Load configuration
 */
export function loadConfig() {
    if (!existsSync(CONFIG_PATH)) {
        return DEFAULT_CONFIG;
    }
    
    try {
        const content = readFileSync(CONFIG_PATH, 'utf8');
        const config = JSON.parse(content);
        // Merge with defaults to handle new config keys
        return {
            ...DEFAULT_CONFIG,
            ...config,
            discord: { ...DEFAULT_CONFIG.discord, ...config.discord },
            audit: { ...DEFAULT_CONFIG.audit, ...config.audit },
            sync: { ...DEFAULT_CONFIG.sync, ...config.sync },
            detection: { ...DEFAULT_CONFIG.detection, ...config.detection }
        };
    } catch (error) {
        console.error(`Config load error: ${error.message}`);
        return DEFAULT_CONFIG;
    }
}

/**
 * Save configuration
 */
export function saveConfig(config) {
    ensureConfigDir();
    
    try {
        writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2), 'utf8');
    } catch (error) {
        console.error(`Config save error: ${error.message}`);
    }
}

/**
 * Update a specific config value
 */
export function updateConfig(key, value) {
    const config = loadConfig();
    const keys = key.split('.');
    
    let current = config;
    for (let i = 0; i < keys.length - 1; i++) {
        if (!current[keys[i]]) {
            current[keys[i]] = {};
        }
        current = current[keys[i]];
    }
    
    current[keys[keys.length - 1]] = value;
    saveConfig(config);
}

/**
 * Get a config value
 */
export function getConfig(key = null) {
    const config = loadConfig();
    
    if (!key) {
        return config;
    }
    
    const keys = key.split('.');
    let current = config;
    
    for (const k of keys) {
        if (current[k] === undefined) {
            return null;
        }
        current = current[k];
    }
    
    return current;
}

/**
 * Security level names and mappings
 */
export const SECURITY_LEVELS = {
    0: 'silent',
    1: 'cautious',
    2: 'strict',
    3: 'paranoid'
};

/**
 * Parse security level (number or name string) to number
 * @param {string|number} level - Level as number (0-3) or name (silent, cautious, strict, paranoid)
 * @returns {number|null} - Level number 0-3, or null if invalid
 */
export function parseSecurityLevel(level) {
    // If it's already a number
    if (typeof level === 'number') {
        return (level >= 0 && level <= 3) ? level : null;
    }
    
    // If it's a string
    if (typeof level === 'string') {
        // Try parsing as number
        const parsed = parseInt(level);
        if (!isNaN(parsed) && parsed >= 0 && parsed <= 3) {
            return parsed;
        }
        
        // Try parsing as name
        const normalized = level.toLowerCase();
        for (const [num, name] of Object.entries(SECURITY_LEVELS)) {
            if (name === normalized) {
                return parseInt(num);
            }
        }
    }
    
    return null;
}

/**
 * Get security level name
 * @param {number} level - Level number 0-3
 * @returns {string} - Level name
 */
export function getSecurityLevelName(level) {
    return SECURITY_LEVELS[level] || 'unknown';
}
