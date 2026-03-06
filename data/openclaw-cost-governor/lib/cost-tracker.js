#!/usr/bin/env node
// Cost Governor v1.1.0 — OpenClaw Community — MIT License

const fs = require('fs');
const path = require('path');

// Auto-detect workspace
const WORKSPACE = process.env.OPENCLAW_WORKSPACE || path.join(process.env.HOME || '~', '.openclaw', 'workspace');
const COST_TRACKING_FILE = path.join(WORKSPACE, 'notes', 'cost-tracking.md');

// Model cost rates (per 1K tokens)
const MODEL_COSTS = {
  opus: { input: 0.075, output: 0.375 },
  sonnet: { input: 0.003, output: 0.015 },
  haiku: { input: 0.0008, output: 0.004 },
  grok: { input: 0.003, output: 0.015 },
  'gpt-4': { input: 0.03, output: 0.06 }
};

// Task type multipliers
const TASK_MULTIPLIERS = {
  creative: 7.5,
  research: 3,
  technical: 2,
  simple: 1.5
};

// Approval threshold
const APPROVAL_THRESHOLD = 0.50;

/**
 * Estimate cost for a task
 * @param {string} taskType - creative|research|technical|simple
 * @param {number} estimatedOutputTokens - Expected output tokens
 * @param {string} model - opus|sonnet|haiku|grok|gpt-4
 * @returns {number} Estimated cost in USD
 */
function estimateCost(taskType, estimatedOutputTokens, model = 'sonnet') {
  const normalizedModel = model.toLowerCase();
  const costs = MODEL_COSTS[normalizedModel] || MODEL_COSTS.sonnet;
  const multiplier = TASK_MULTIPLIERS[taskType] || TASK_MULTIPLIERS.technical;
  
  // Formula: (estimated_output_tokens / 1000) * output_rate * task_multiplier
  const baseCost = (estimatedOutputTokens / 1000) * costs.output;
  const adjustedCost = baseCost * multiplier;
  
  return adjustedCost;
}

/**
 * Check if approval is required
 * @param {number} estimatedCost - Estimated cost in USD
 * @returns {boolean} True if approval required
 */
function checkApprovalRequired(estimatedCost) {
  return estimatedCost > APPROVAL_THRESHOLD;
}

/**
 * Initialize cost tracking file if it doesn't exist
 */
function initializeCostTracking() {
  if (!fs.existsSync(COST_TRACKING_FILE)) {
    const header = `# Cost Tracking

## Format
Each entry follows this structure:
\`\`\`
### [YYYY-MM-DD HH:MM] [Label]
- **Model:** [model name]
- **Task Type:** [creative|research|technical|simple]
- **Estimated:** $X.XX
- **Actual:** $X.XX (pending)
- **Approved:** [yes|no|auto]
- **Notes:** [optional context]
\`\`\`

---

`;
    fs.mkdirSync(path.dirname(COST_TRACKING_FILE), { recursive: true });
    fs.writeFileSync(COST_TRACKING_FILE, header);
  }
}

/**
 * Log a subagent spawn with cost estimate
 * @param {string} label - Subagent label
 * @param {string} model - Model name
 * @param {number} estimatedCost - Estimated cost in USD
 * @param {boolean} approved - Whether approved (true|false|'auto')
 * @param {object} options - Optional metadata
 */
function logSpawn(label, model, estimatedCost, approved, options = {}) {
  initializeCostTracking();
  
  const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 16);
  const approvedStr = approved === 'auto' ? 'auto' : (approved ? 'yes' : 'no');
  
  const entry = `### [${timestamp}] ${label}
- **Model:** ${model}
- **Task Type:** ${options.taskType || 'unknown'}
- **Estimated:** $${estimatedCost.toFixed(2)}
- **Actual:** $0.00 (pending)
- **Approved:** ${approvedStr}
${options.notes ? `- **Notes:** ${options.notes}\n` : ''}
---

`;
  
  fs.appendFileSync(COST_TRACKING_FILE, entry);
}

/**
 * Update an entry with actual cost
 * @param {string} label - Subagent label to find
 * @param {number} actualCost - Actual cost in USD
 */
function logActual(label, actualCost) {
  if (!fs.existsSync(COST_TRACKING_FILE)) {
    throw new Error('Cost tracking file not found. No spawn to update.');
  }
  
  let content = fs.readFileSync(COST_TRACKING_FILE, 'utf8');
  
  // Find the most recent entry for this label
  const labelPattern = new RegExp(`(### \\[\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}\\] ${label.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}[\\s\\S]*?)- \\*\\*Actual:\\*\\* \\$[0-9.]+( \\(pending\\))?`, 'g');
  
  const matches = [...content.matchAll(labelPattern)];
  if (matches.length === 0) {
    throw new Error(`No pending entry found for label: ${label}`);
  }
  
  // Update the last match
  const lastMatch = matches[matches.length - 1];
  const replacement = lastMatch[1] + `- **Actual:** $${actualCost.toFixed(2)}`;
  content = content.substring(0, lastMatch.index) + replacement + content.substring(lastMatch.index + lastMatch[0].length);
  
  fs.writeFileSync(COST_TRACKING_FILE, content);
}

module.exports = {
  estimateCost,
  checkApprovalRequired,
  logSpawn,
  logActual,
  APPROVAL_THRESHOLD
};
