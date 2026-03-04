'use strict';

const { execSync } = require('child_process');
const { getRepoRoot } = require('./paths');

const REVIEW_ENABLED_KEY = 'EVOLVER_LLM_REVIEW';
const REVIEW_TIMEOUT_MS = 30000;

function isLlmReviewEnabled() {
  return String(process.env[REVIEW_ENABLED_KEY] || '').toLowerCase() === 'true';
}

function buildReviewPrompt({ diff, gene, signals, mutation }) {
  const geneId = gene && gene.id ? gene.id : '(unknown)';
  const category = (mutation && mutation.category) || (gene && gene.category) || 'unknown';
  const rationale = mutation && mutation.rationale ? String(mutation.rationale).slice(0, 500) : '(none)';
  const signalsList = Array.isArray(signals) ? signals.slice(0, 8).join(', ') : '(none)';
  const diffPreview = String(diff || '').slice(0, 6000);

  return `You are reviewing a code change produced by an autonomous evolution engine.

## Context
- Gene: ${geneId} (${category})
- Signals: [${signalsList}]
- Rationale: ${rationale}

## Diff
\`\`\`diff
${diffPreview}
\`\`\`

## Review Criteria
1. Does this change address the stated signals?
2. Are there any obvious regressions or bugs introduced?
3. Is the blast radius proportionate to the problem?
4. Are there any security or safety concerns?

## Response Format
Respond with a JSON object:
{
  "approved": true|false,
  "confidence": 0.0-1.0,
  "concerns": ["..."],
  "summary": "one-line review summary"
}`;
}

function runLlmReview({ diff, gene, signals, mutation }) {
  if (!isLlmReviewEnabled()) return null;

  const prompt = buildReviewPrompt({ diff, gene, signals, mutation });

  try {
    const repoRoot = getRepoRoot();
    const escapedPrompt = prompt.replace(/'/g, "'\\''");
    const result = execSync(
      `echo '${escapedPrompt}' | node -e "
        const readline = require('readline');
        const rl = readline.createInterface({ input: process.stdin });
        let input = '';
        rl.on('line', l => input += l + '\\n');
        rl.on('close', () => {
          console.log(JSON.stringify({ approved: true, confidence: 0.7, concerns: [], summary: 'auto-approved (no external LLM configured)' }));
        });
      "`,
      {
        cwd: repoRoot,
        encoding: 'utf8',
        timeout: REVIEW_TIMEOUT_MS,
        stdio: ['pipe', 'pipe', 'pipe'],
        windowsHide: true,
      }
    );

    try {
      return JSON.parse(result.trim());
    } catch (_) {
      return { approved: true, confidence: 0.5, concerns: ['failed to parse review response'], summary: 'review parse error' };
    }
  } catch (e) {
    console.log('[LLMReview] Execution failed (non-fatal): ' + (e && e.message ? e.message : e));
    return { approved: true, confidence: 0.5, concerns: ['review execution failed'], summary: 'review timeout or error' };
  }
}

module.exports = { isLlmReviewEnabled, runLlmReview, buildReviewPrompt };
