/**
 * Shared Hook Utilities - Deterministic, Pure Functions
 *
 * SECURITY MANIFEST:
 *   Environment variables: none
 *   External endpoints: none
 *   Local files read: hook config.json (token-context or token-model, via loadConfigCached)
 *   Local files written: none (config cache is in-memory)
 *
 * Design Contract:
 * - All functions are PURE unless named with `mutate_` prefix
 * - No exceptions for control flow - use Either/Maybe patterns
 * - All numeric limits are compile-time constants
 * - Logging only at entry, exit, error
 * - Immutability preferred; mutation is last resort
 *
 * Type Contract Notation:
 *   fn(input) -> Output | Error
 *   post: output satisfies predicate
 */

'use strict';

const { readFileSync, existsSync } = require('fs');
const { join, dirname } = require('path');

// =============================================================================
// COMPILE-TIME CONSTANTS (Theorems)
// =============================================================================

/** @constant {number} Maximum file name length */
const MAX_FILE_NAME_LENGTH = 255;

/** @constant {number} Config cache TTL in milliseconds */
const CONFIG_CACHE_TTL_MS = 60000;

/** @constant {number} Maximum log message length */
const MAX_LOG_MESSAGE_LENGTH = 500;

/** @constant {string[]} Allowed file extensions */
const ALLOWED_EXTENSIONS = ['.md', '.json', '.txt', '.yaml', '.yml'];

/** @constant {RegExp} Valid file name pattern */
const VALID_FILE_NAME_PATTERN = /^[a-zA-Z0-9._-]+$/;

// =============================================================================
// EITHER/MAYBE PATTERNS (No exceptions for control flow)
// =============================================================================

/**
 * @typedef {Object} Maybe
 * @property {boolean} isJust
 * @property {boolean} isNothing
 * @property {*} value
 */

/**
 * Creates a Maybe Just
 * @param {*} value
 * @returns {Maybe}
 * @post returns.just === true, returns.value === value
 */
const Just = (value) => ({
    isJust: true,
    isNothing: false,
    value
});

/**
 * Creates a Maybe Nothing
 * @returns {Maybe}
 * @post returns.isJust === false, returns.isNothing === true
 */
const Nothing = () => ({
    isJust: false,
    isNothing: true,
    value: null
});

/**
 * @typedef {Object} Either
 * @property {boolean} isLeft
 * @property {boolean} isRight
 * @property {*} leftValue
 * @property {*} rightValue
 */

/**
 * Creates a Left (Error)
 * @param {*} error
 * @returns {Either}
 * @post returns.isLeft === true
 */
const Left = (error) => ({
    isLeft: true,
    isRight: false,
    leftValue: error,
    rightValue: null
});

/**
 * Creates a Right (Success)
 * @param {*} value
 * @returns {Either}
 * @post returns.isRight === true
 */
const Right = (value) => ({
    isLeft: false,
    isRight: true,
    leftValue: null,
    rightValue: value
});

/**
 * Maps over Right value, passes Left through
 * @param {Function} fn - (a) -> b
 * @param {Either} either
 * @returns {Either}
 * @post if either.isRight, returns.rightValue === fn(either.rightValue)
 */
const mapRight = (fn, either) => 
    either.isRight ? Right(fn(either.rightValue)) : either;

/**
 * Maps over Left value, passes Right through  
 * @param {Function} fn - (a) -> b
 * @param {Either} either
 * @returns {Either}
 * @post if either.isLeft, returns.leftValue === fn(either.leftValue)
 */
const mapLeft = (fn, either) =>
    either.isLeft ? Left(fn(either.leftValue)) : either;

/**
 * Chains a function that returns Either
 * @param {Function} fn - (a) -> Either
 * @param {Either} either
 * @returns {Either}
 */
const flatMap = (fn, either) =>
    either.isRight ? fn(either.rightValue) : either;

/**
 * Gets value or default
 * @param {*} defaultValue
 * @param {Maybe} maybe
 * @returns {*}
 * @post returns maybe.isJust ? maybe.value : defaultValue
 */
const fromMaybe = (defaultValue, maybe) =>
    maybe.isJust ? maybe.value : defaultValue;

// =============================================================================
// PURE FUNCTIONS (No Side Effects)
// =============================================================================

/**
 * Validates file name is safe
 * @param {string} name
 * @returns {boolean}
 * @post returns === true iff name is safe
 */
const isValidFileName = (name) => 
    Boolean(name) &&
    typeof name === 'string' &&
    VALID_FILE_NAME_PATTERN.test(name) &&
    name.length > 0 &&
    name.length <= MAX_FILE_NAME_LENGTH;

/**
 * Classifies message complexity - PURE
 * @param {string} message
 * @returns {{level: string, confidence: number, reasoning: string}}
 * @post returns.level in ['simple', 'standard', 'complex']
 * @post 0 <= returns.confidence <= 1
 */
const classifyComplexity = (message) => {
    // Defensive: handle invalid input
    if (!message || typeof message !== 'string') {
        return { level: 'standard', confidence: 0, reasoning: 'Invalid input' };
    }

    const trimmed = message.trim();
    const lower = trimmed.toLowerCase();

    if (trimmed.length === 0) {
        return { level: 'standard', confidence: 0, reasoning: 'Empty message' };
    }

    // Simple patterns (greetings, acknowledgments)
    const simplePatterns = [
        /^(hi|hey|hello|yo|sup|howdy)$/i,
        /^(thanks|thank you|thx|ty)$/i,
        /^(ok|okay|sure|got it|understood|roger|affirmative)$/i,
        /^(yes|yeah|yep|yup|no|nope|nah)$/i,
        /^(good|great|nice|cool|awesome|amazing|wonderful|perfect)$/i,
        /^\?+$/,
    ];

    for (const pattern of simplePatterns) {
        if (pattern.test(trimmed)) {
            return { level: 'simple', confidence: 0.95, reasoning: `Matched: ${pattern.source}` };
        }
    }

    // Complex patterns (design, architecture)
    const complexPatterns = [
        /^(design|architect)\s+\w+/i,
        /\barchitect(?:ure|ing)?\b/i,
        /\bcomprehensive\b/i,
        /\banalyze\s+deeply\b/i,
        /\bplan\s+\w+\s+system\b/i,
        /\bcreate\s+\w+\s+from\s+scratch\b/i,
    ];

    for (const pattern of complexPatterns) {
        if (pattern.test(lower)) {
            return { level: 'complex', confidence: 0.90, reasoning: `Complex: ${pattern.source}` };
        }
    }

    // Default: standard
    return { level: 'standard', confidence: 0.60, reasoning: 'Default classification' };
};

/**
 * Gets allowed files for complexity level - PURE
 * @param {string} level
 * @param {Object} customConfig
 * @returns {string[]}
 * @post returns.length > 0
 */
const getAllowedFiles = (level, customConfig) => {
    const defaults = {
        simple: ['SOUL.md', 'IDENTITY.md'],
        standard: ['SOUL.md', 'IDENTITY.md', 'USER.md'],
        complex: ['SOUL.md', 'IDENTITY.md', 'USER.md', 'TOOLS.md', 'AGENTS.md', 'MEMORY.md', 'HEARTBEAT.md']
    };

    const config = customConfig || {};
    const files = config.files || {};

    return files[level] || defaults[level] || defaults.standard;
};

/**
 * Classifies for model tier - PURE
 * @param {string} message
 * @returns {{tier: string, confidence: number, reasoning: string}}
 * @post returns.tier in ['quick', 'standard', 'deep']
 */
const classifyForModel = (message) => {
    if (!message || typeof message !== 'string') {
        return { tier: 'standard', confidence: 0, reasoning: 'Invalid input' };
    }

    const trimmed = message.trim();
    const lower = trimmed.toLowerCase();

    if (trimmed.length === 0) {
        return { tier: 'standard', confidence: 0, reasoning: 'Empty' };
    }

    // Quick patterns
    const quickPatterns = [
        /^(hi|hey|hello|yo|sup|howdy)$/i,
        /^(thanks|thank you|thx|ty)$/i,
        /^(ok|okay|sure|got it|understood)$/i,
        /^(yes|no|yeah|nope)$/i,
        /^heartbeat$/i,
        /^check\s+(email|calendar|weather|status)/i,
    ];

    for (const pattern of quickPatterns) {
        if (pattern.test(trimmed) || pattern.test(lower)) {
            return { tier: 'quick', confidence: 0.90, reasoning: `Quick: ${pattern.source}` };
        }
    }

    // Deep patterns
    const deepPatterns = [
        /^(design|architect)\s+\w+/i,
        /\barchitect(?:ure|ing)?\b/i,
        /\bcomprehensive\b/i,
        /\banalyze\s+deeply\b/i,
    ];

    for (const pattern of deepPatterns) {
        if (pattern.test(lower)) {
            return { tier: 'deep', confidence: 0.90, reasoning: `Deep: ${pattern.source}` };
        }
    }

    return { tier: 'standard', confidence: 0.60, reasoning: 'Default' };
};

/**
 * Extracts user message from context - PURE
 * @param {Object} context
 * @returns {Maybe<string>}
 * @post returns.isJust === true iff message found
 */
const extractUserMessage = (context) => {
    if (!context || !context.sessionEntry) {
        return Nothing();
    }

    const { messages, lastMessage } = context.sessionEntry;

    if (messages && Array.isArray(messages)) {
        for (let i = messages.length - 1; i >= 0; i--) {
            const msg = messages[i];
            if (msg && msg.role === 'user' && msg.content) {
                return Just(msg.content);
            }
        }
    }

    return lastMessage ? Just(lastMessage) : Nothing();
};

/**
 * Gets model for tier - PURE
 * @param {string} tier
 * @param {Object} customModels
 * @returns {string}
 */
const getModelForTier = (tier, customModels) => {
    const defaults = {
        quick: 'openrouter/stepfun/step-3.5-flash:free',
        standard: 'anthropic/claude-haiku-4',
        deep: 'openrouter/minimax/minimax-m2.5'
    };

    const models = customModels || {};
    return models[tier] || defaults[tier] || defaults.standard;
};

/**
 * Gets cost for tier - PURE
 * @param {string} tier
 * @returns {string}
 */
const getTierCost = (tier) => {
    const costs = {
        quick: '$0.00/MT',
        standard: '$0.25/MT',
        deep: '$0.60+/MT'
    };
    return costs[tier] || costs.standard;
};

/**
 * Gets status emoji for budget percent - PURE
 * @param {number} percent
 * @returns {string}
 * @post returns in ['✅', '🟡', '🔴', '🚨']
 */
const getStatusEmoji = (percent) => {
    if (percent >= 1.0) return '🚨';
    if (percent >= 0.95) return '🔴';
    if (percent >= 0.80) return '🟡';
    return '✅';
};

/**
 * Determines if in quiet hours - PURE
 * @param {number} hour - 0-23
 * @param {Object} quietHoursConfig
 * @returns {boolean}
 */
const isQuietHours = (hour, quietHoursConfig) => {
    const start = quietHoursConfig?.start ?? 23;
    const end = quietHoursConfig?.end ?? 8;

    if (start > end) {
        // Spans midnight (e.g., 23:00 - 08:00)
        return hour >= start || hour < end;
    }
    return hour >= start && hour < end;
};

/**
 * Truncates message for logging - PURE
 * @param {string} message
 * @returns {string}
 */
const truncateForLog = (message) => {
    if (!message) return '';
    return message.length > MAX_LOG_MESSAGE_LENGTH 
        ? message.substring(0, MAX_LOG_MESSAGE_LENGTH) + '...'
        : message;
};

// =============================================================================
// IMPURE FUNCTIONS (Explicitly Named)
// =============================================================================

/** @type {Object|null} Cached config */
let _configCache = null;

/** @type {number} Cache timestamp */
let _configCacheTime = 0;

/**
 * Loads config with caching - IMPURE (side effect: file I/O)
 * @param {Function} logFn - Logging function
 * @returns {Object}
 */
const loadConfigCached = (logFn) => {
    const now = Date.now();
    
    // Return cached if valid
    if (_configCache && (now - _configCacheTime) < CONFIG_CACHE_TTL_MS) {
        return _configCache;
    }

    // Load from file
    const configPath = join(dirname(__dirname), 'token-context', 'config.json');
    const fallbackPath = join(dirname(__dirname), 'token-model', 'config.json');
    
    const path = existsSync(configPath) ? configPath : fallbackPath;
    
    if (existsSync(path)) {
        try {
            const content = readFileSync(path, 'utf-8');
            _configCache = JSON.parse(content);
            _configCacheTime = now;
            logFn?.('[shared] Config loaded and cached');
            return _configCache;
        } catch (e) {
            logFn?.(`[shared] Config load error: ${e.message}`);
        }
    }

    // Default config
    _configCache = { enabled: true, logLevel: 'info' };
    _configCacheTime = now;
    return _configCache;
};

/**
 * Resets config cache - IMPURE (mutation)
 */
const resetConfigCache = () => {
    _configCache = null;
    _configCacheTime = 0;
};

// =============================================================================
// EXPORTS
// =============================================================================

module.exports = {
    // Constants
    MAX_FILE_NAME_LENGTH,
    CONFIG_CACHE_TTL_MS,
    MAX_LOG_MESSAGE_LENGTH,
    ALLOWED_EXTENSIONS,
    VALID_FILE_NAME_PATTERN,

    // Maybe/Either
    Just,
    Nothing,
    Left,
    Right,
    mapRight,
    mapLeft,
    flatMap,
    fromMaybe,

    // Pure functions
    isValidFileName,
    classifyComplexity,
    getAllowedFiles,
    classifyForModel,
    extractUserMessage,
    getModelForTier,
    getTierCost,
    getStatusEmoji,
    isQuietHours,
    truncateForLog,

    // Impure (explicitly named)
    loadConfigCached,
    resetConfigCache,
};
