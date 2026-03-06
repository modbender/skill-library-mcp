#!/usr/bin/env node
/**
 * evaluate-enforcement-need.js
 *
 * Evaluates whether a rule needs Lobster enforcement per CR-012 criteria.
 *
 * Input (via env):
 *   RULE_NAME        - Short slug for the rule
 *   RULE_DESCRIPTION - Plain-language rule description
 *
 * Output (stdout JSON):
 *   {
 *     needsEnforcement: boolean,
 *     reason: string,
 *     criteria: string[],   // which criteria matched
 *     score: number         // 0-4
 *   }
 */

const ruleName = process.env.RULE_NAME || '';
const ruleDescription = process.env.RULE_DESCRIPTION || '';

const text = `${ruleName} ${ruleDescription}`.toLowerCase();

// CR-012 Criterion 1: High-stakes keywords
const HIGH_STAKES_KEYWORDS = [
  'external', 'send', 'message', 'email', 'money', 'payment', 'billing',
  'delete', 'remove', 'destroy', 'publish', 'deploy', 'release', 'production',
  'tweet', 'post', 'broadcast', 'notify', 'alert', 'sms', 'webhook',
  'purchase', 'charge', 'invoice', 'transfer', 'bank', 'credit', 'debit',
  'public', 'customer', 'user data', 'pii', 'gdpr'
];

// CR-012 Criterion 2: Pattern-of-violations keywords
const VIOLATION_PATTERN_KEYWORDS = [
  'again', 'repeatedly', 'keep', 'still', 'despite', 'ignore', 'ignoring',
  'previously', 'last time', 'already told', 'already said', 'broke', 'broken',
  'violated', 'violation', 'failure', 'failed', 'pattern'
];

// CR-012 Criterion 3: Multi-step sequence keywords
const MULTI_STEP_KEYWORDS = [
  'then', 'after', 'before', 'first', 'second', 'third', 'next', 'finally',
  'sequence', 'workflow', 'step', 'always first', 'must then', 'only then',
  'prior to', 'followed by', 'preceding', 'subsequent'
];

// CR-012 Criterion 4: External/public action keywords (broader)
const EXTERNAL_ACTION_KEYWORDS = [
  'send to', 'reply to', 'forward', 'share', 'submit', 'push', 'commit',
  'merge', 'pr', 'pull request', 'api call', 'webhook', 'http', 'post request',
  'external service', 'third party', '3rd party', 'integration'
];

function matchKeywords(text, keywords) {
  return keywords.filter(kw => text.includes(kw));
}

const highStakesMatches = matchKeywords(text, HIGH_STAKES_KEYWORDS);
const violationMatches = matchKeywords(text, VIOLATION_PATTERN_KEYWORDS);
const multiStepMatches = matchKeywords(text, MULTI_STEP_KEYWORDS);
const externalMatches = matchKeywords(text, EXTERNAL_ACTION_KEYWORDS);

const criteria = [];
const matchedDetails = {};

if (highStakesMatches.length > 0) {
  criteria.push('high-stakes');
  matchedDetails['high-stakes'] = highStakesMatches.slice(0, 5);
}
if (violationMatches.length > 0) {
  criteria.push('pattern-of-violations');
  matchedDetails['pattern-of-violations'] = violationMatches.slice(0, 5);
}
if (multiStepMatches.length >= 2) {
  // Require at least 2 multi-step keywords to avoid false positives
  criteria.push('multi-step-sequence');
  matchedDetails['multi-step-sequence'] = multiStepMatches.slice(0, 5);
}
if (externalMatches.length > 0 && !criteria.includes('high-stakes')) {
  // Only add external-action if not already captured by high-stakes
  criteria.push('external-action');
  matchedDetails['external-action'] = externalMatches.slice(0, 5);
}

const score = criteria.length;
const needsEnforcement = score > 0;

let reason = '';
if (!needsEnforcement) {
  reason = 'No high-stakes, violation pattern, or multi-step sequence detected. TOOLS.md entry sufficient.';
} else {
  const parts = [];
  if (criteria.includes('high-stakes')) {
    parts.push(`high-stakes action detected (${matchedDetails['high-stakes'].join(', ')})`);
  }
  if (criteria.includes('pattern-of-violations')) {
    parts.push(`pattern-of-violations language detected (${matchedDetails['pattern-of-violations'].join(', ')})`);
  }
  if (criteria.includes('multi-step-sequence')) {
    parts.push(`multi-step sequence detected (${matchedDetails['multi-step-sequence'].join(', ')})`);
  }
  if (criteria.includes('external-action')) {
    parts.push(`external action detected (${matchedDetails['external-action'].join(', ')})`);
  }
  reason = `Lobster enforcement recommended: ${parts.join('; ')}.`;
}

const result = {
  needsEnforcement,
  reason,
  criteria,
  score,
  matchedDetails
};

process.stdout.write(JSON.stringify(result, null, 2) + '\n');
process.exit(0);
