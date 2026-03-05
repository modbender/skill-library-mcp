/**
 * @fileoverview Cost estimation and tracking for subagent spawns
 * @module subagent-architecture/lib/cost-estimator
 * @license MIT
 * 
 * Implementation based on Agent Smith review (2026-02-22)
 * Provides: Pre-spawn estimation, accuracy tracking, continuous improvement
 */

const fs = require('fs');
const path = require('path');

/**
 * Base costs per model (per 1M tokens)
 * Updated: 2026-02-22 (Anthropic pricing)
 */
const MODEL_COSTS = {
  haiku: { input: 0.25, output: 1.25 },
  sonnet: { input: 3.00, output: 15.00 },
  opus: { input: 15.00, output: 75.00 }
};

/**
 * Complexity multipliers (estimated tokens used)
 */
const COMPLEXITY_TOKENS = {
  simple: 5000,   // Basic lookup, single operation
  medium: 15000,  // Research, code review
  high: 40000     // Implementation, deep analysis
};

/**
 * Pattern-specific adjustments (learned from historical data)
 * Updated via recalibrateEstimator()
 */
let PATTERN_ADJUSTMENTS = {};

/**
 * Estimate cost for a subagent spawn before execution
 * 
 * @param {Object} params - Estimation parameters
 * @param {string} params.task_complexity - "simple" | "medium" | "high"
 * @param {number} params.expected_duration_min - Expected runtime in minutes
 * @param {string} params.model - "haiku" | "sonnet" | "opus"
 * @param {boolean} [params.research_required=false] - Will task require web searches?
 * @param {string} [params.pattern] - Optional pattern name for historical adjustment
 * @returns {Object} Cost estimate with confidence intervals
 * 
 * @example
 * const estimate = estimateSubagentCost({
 *   task_complexity: "medium",
 *   expected_duration_min: 15,
 *   model: "sonnet",
 *   research_required: true,
 *   pattern: "researcher-specialist"
 * });
 * // Returns: { min: 0.42, expected: 0.60, max: 0.78, confidence: 0.7 }
 */
function estimateSubagentCost(params) {
  const {
    task_complexity = 'medium',
    expected_duration_min = 10,
    model = 'sonnet',
    research_required = false,
    pattern = null
  } = params;

  // Validate inputs
  if (!MODEL_COSTS[model]) {
    throw new Error(`Unknown model: ${model}. Must be haiku, sonnet, or opus`);
  }
  if (!COMPLEXITY_TOKENS[task_complexity]) {
    throw new Error(`Unknown complexity: ${task_complexity}. Must be simple, medium, or high`);
  }

  // Base token estimate
  const base_tokens = COMPLEXITY_TOKENS[task_complexity];

  // Research adds web searches (assume 5 searches, 2k tokens each)
  const research_tokens = research_required ? 10000 : 0;

  // Duration multiplier (longer tasks = more retries/refinement)
  const duration_multiplier = Math.sqrt(expected_duration_min / 10);

  const total_tokens = (base_tokens + research_tokens) * duration_multiplier;

  // Assume 60/40 input/output split
  const input_tokens = total_tokens * 0.6;
  const output_tokens = total_tokens * 0.4;

  // Calculate base cost
  let cost = (
    (input_tokens / 1000000) * MODEL_COSTS[model].input +
    (output_tokens / 1000000) * MODEL_COSTS[model].output
  );

  // Apply historical pattern adjustment if available
  let confidence = 0.7;  // Base confidence
  if (pattern) {
    const key = `${pattern}-${model}-${task_complexity}`;
    const adjustment = PATTERN_ADJUSTMENTS[key];
    
    if (adjustment && adjustment.sample_size > 5) {
      cost *= adjustment.multiplier;
      confidence = adjustment.confidence;
    }
  }

  // Confidence intervals (±30% typical variance, tighter with more data)
  const variance = 1 - (confidence * 0.3);  // Higher confidence = lower variance
  
  return {
    min: cost * (1 - variance),
    expected: cost,
    max: cost * (1 + variance),
    confidence: confidence
  };
}

/**
 * Log subagent cost after execution for accuracy tracking
 * 
 * @param {string} label - Subagent label (e.g., "researcher-market")
 * @param {Object} estimate - Original estimate from estimateSubagentCost()
 * @param {number} actual - Actual cost incurred
 * @param {Object} [metadata] - Optional metadata (duration, tokens, etc.)
 * 
 * @example
 * logSubagentCost(
 *   "researcher-market",
 *   { expected: 0.60, min: 0.42, max: 0.78 },
 *   0.55,
 *   { duration_min: 12, tokens_used: 38000 }
 * );
 */
function logSubagentCost(label, estimate, actual, metadata = {}) {
  const record = {
    timestamp: Date.now(),
    date: new Date().toISOString(),
    label: label,
    pattern: extractPattern(label),
    model: estimate.model || metadata.model || 'unknown',
    complexity: estimate.complexity || metadata.complexity || 'unknown',
    estimated: estimate.expected,
    actual: actual,
    error: (actual - estimate.expected) / estimate.expected,  // % error
    duration_min: metadata.duration_min || estimate.expected_duration_min || null,
    research: metadata.research_required || estimate.research_required || false,
    ...metadata
  };

  // Append to JSONL log
  const workspaceRoot = process.env.OPENCLAW_WORKSPACE || process.cwd();
  const logPath = path.join(workspaceRoot, 'memory', 'subagent-costs.jsonl');
  
  try {
    // Ensure directory exists
    const logDir = path.dirname(logPath);
    if (!fs.existsSync(logDir)) {
      fs.mkdirSync(logDir, { recursive: true });
    }

    fs.appendFileSync(logPath, JSON.stringify(record) + '\n', 'utf8');
  } catch (error) {
    console.error(`Failed to log subagent cost: ${error.message}`);
  }

  return record;
}

/**
 * Extract pattern name from subagent label
 * 
 * @param {string} label - Subagent label (e.g., "researcher-market-analysis")
 * @returns {string} Pattern name (e.g., "researcher")
 * @private
 */
function extractPattern(label) {
  // Common patterns: researcher-, coder-, architect-, reviewer-, proxy-
  const patterns = [
    'researcher', 'coder', 'architect', 'reviewer', 
    'proxy', 'security', 'analyst', 'auditor'
  ];
  
  for (const pattern of patterns) {
    if (label.toLowerCase().startsWith(pattern)) {
      return pattern;
    }
  }
  
  return 'unknown';
}

/**
 * Recalibrate estimation formula based on historical data
 * Should be run monthly to improve accuracy
 * 
 * @param {Object} [options] - Calibration options
 * @param {number} [options.window_days=30] - Days of history to analyze
 * @param {number} [options.min_samples=5] - Minimum samples required per group
 * @returns {Object} Calibration summary
 * 
 * @example
 * const summary = recalibrateEstimator({ window_days: 30 });
 * console.log(`Updated ${summary.groups_updated} pattern groups`);
 */
function recalibrateEstimator(options = {}) {
  const {
    window_days = 30,
    min_samples = 5
  } = options;

  const logPath = path.join(process.env.OPENCLAW_WORKSPACE || process.cwd(), 'memory', 'subagent-costs.jsonl');
  
  if (!fs.existsSync(logPath)) {
    console.warn('No cost log found. Cannot recalibrate.');
    return { groups_updated: 0, message: 'No historical data' };
  }

  // Read and parse JSONL
  const logContent = fs.readFileSync(logPath, 'utf8');
  const records = logContent
    .split('\n')
    .filter(line => line.trim())
    .map(line => {
      try {
        return JSON.parse(line);
      } catch {
        return null;
      }
    })
    .filter(r => r !== null);

  // Filter to recent records
  const cutoff = Date.now() - (window_days * 24 * 60 * 60 * 1000);
  const recent = records.filter(r => r.timestamp > cutoff);

  if (recent.length === 0) {
    return { groups_updated: 0, message: 'No recent data' };
  }

  // Group by pattern + model + complexity
  const groups = {};
  recent.forEach(r => {
    const key = `${r.pattern}-${r.model}-${r.complexity}`;
    if (!groups[key]) groups[key] = [];
    groups[key].push(r);
  });

  // Calculate adjustments for each group
  let updated_count = 0;
  const adjustments = {};

  for (const [key, records] of Object.entries(groups)) {
    if (records.length < min_samples) continue;

    // Calculate mean error and standard deviation
    const errors = records.map(r => r.error);
    const mean_error = errors.reduce((sum, e) => sum + e, 0) / errors.length;
    const variance = errors.reduce((sum, e) => sum + Math.pow(e - mean_error, 2), 0) / errors.length;
    const std_dev = Math.sqrt(variance);

    adjustments[key] = {
      multiplier: 1 + mean_error,  // Adjust base estimate
      confidence: Math.max(0.5, Math.min(0.95, 1 - std_dev)),  // Higher std_dev = lower confidence
      sample_size: records.length,
      mean_error: mean_error,
      std_dev: std_dev
    };

    updated_count++;
  }

  // Update global adjustments
  PATTERN_ADJUSTMENTS = { ...PATTERN_ADJUSTMENTS, ...adjustments };

  return {
    groups_updated: updated_count,
    adjustments: adjustments,
    total_records: recent.length,
    window_days: window_days
  };
}

/**
 * Estimate with historical adjustment (convenience wrapper)
 * 
 * @param {Object} params - Same as estimateSubagentCost
 * @returns {Object} Adjusted cost estimate
 * 
 * @example
 * const estimate = estimateWithHistory({
 *   task_complexity: "high",
 *   expected_duration_min: 20,
 *   model: "sonnet",
 *   pattern: "researcher-specialist"
 * });
 */
function estimateWithHistory(params) {
  return estimateSubagentCost(params);
}

/**
 * Get cost tier for a given estimate
 * 
 * @param {number} cost - Estimated or actual cost
 * @returns {string} Tier: "micro" | "small" | "medium" | "large"
 */
function getCostTier(cost) {
  if (cost < 0.10) return 'micro';
  if (cost < 0.50) return 'small';
  if (cost < 2.00) return 'medium';
  return 'large';
}

/**
 * Get historical success rate for a pattern
 * 
 * @param {string} pattern - Pattern name
 * @param {Object} [options] - Query options
 * @returns {Object} Success metrics
 */
function getPatternHistory(pattern, options = {}) {
  const { window_days = 90 } = options;
  const logPath = path.join(process.env.OPENCLAW_WORKSPACE || process.cwd(), 'memory', 'subagent-costs.jsonl');
  
  if (!fs.existsSync(logPath)) {
    return { success_rate: null, total_spawns: 0, message: 'No historical data' };
  }

  const logContent = fs.readFileSync(logPath, 'utf8');
  const records = logContent
    .split('\n')
    .filter(line => line.trim())
    .map(line => {
      try {
        return JSON.parse(line);
      } catch {
        return null;
      }
    })
    .filter(r => r !== null);

  const cutoff = Date.now() - (window_days * 24 * 60 * 60 * 1000);
  const patternRecords = records.filter(r => 
    r.pattern === pattern && r.timestamp > cutoff
  );

  if (patternRecords.length === 0) {
    return { success_rate: null, total_spawns: 0, message: 'No data for pattern' };
  }

  // Calculate metrics
  const errors = patternRecords.map(r => r.error);
  const mean_error = errors.reduce((sum, e) => sum + e, 0) / errors.length;
  const costs = patternRecords.map(r => r.actual);
  const avg_cost = costs.reduce((sum, c) => sum + c, 0) / costs.length;

  return {
    total_spawns: patternRecords.length,
    avg_cost: avg_cost,
    cost_accuracy: mean_error,
    window_days: window_days
  };
}

// ─── Session cost accumulator ─────────────────────────────────────────────────
// WHY: Per-session cost totals let the main agent enforce a $0.50 guard rail
// without querying the JSONL log every time. In-memory only — not persisted.
// For persistent session tracking, use lib/subagent-run-logger.js instead.

const SESSION_COSTS = new Map(); // sessionId → { total: number, spawns: Array }

/**
 * Record an estimated cost for a subagent spawn in the session accumulator.
 *
 * @param {string} sessionId - Session identifier
 * @param {number} estimatedCost - Pre-spawn cost estimate in USD
 * @param {string} label - Subagent label (for audit trail)
 */
function trackSessionSpawn(sessionId, estimatedCost, label) {
  if (!SESSION_COSTS.has(sessionId)) {
    SESSION_COSTS.set(sessionId, { total: 0, spawns: [] });
  }
  const bucket = SESSION_COSTS.get(sessionId);
  bucket.total += estimatedCost || 0;
  bucket.spawns.push({
    label: label || 'unknown',
    cost: estimatedCost || 0,
    timestamp: Date.now()
  });
}

/**
 * Get the accumulated estimated cost for a session.
 *
 * @param {string} sessionId
 * @returns {number} Total estimated cost in USD (0 if session not tracked)
 */
function getSessionTotal(sessionId) {
  const bucket = SESSION_COSTS.get(sessionId);
  return bucket ? bucket.total : 0;
}

/**
 * Check whether a session has exceeded (or would exceed) the cost threshold.
 *
 * @param {string} sessionId
 * @param {number} [threshold=0.50] - Cost threshold in USD
 * @returns {{ exceeded: boolean, total: number, count: int }}
 */
function checkSessionThreshold(sessionId, threshold = 0.50) {
  const bucket = SESSION_COSTS.get(sessionId);
  const total = bucket ? bucket.total : 0;
  const count = bucket ? bucket.spawns.length : 0;
  return {
    exceeded: total >= threshold,
    total: Math.round(total * 10000) / 10000,
    count
  };
}

module.exports = {
  estimateSubagentCost,
  logSubagentCost,
  recalibrateEstimator,
  estimateWithHistory,
  getCostTier,
  getPatternHistory,
  trackSessionSpawn,
  getSessionTotal,
  checkSessionThreshold,
  MODEL_COSTS,
  COMPLEXITY_TOKENS
};
