#!/usr/bin/env node
/**
 * evaluate.js — Evaluation separation layer for openclaw-reflect.
 *
 * Routes each proposal through an adversarial evaluator using whatever
 * inference backend is available in the environment. The same model that
 * generated the proposal can evaluate it — what matters is a fresh invocation
 * with an adversarial mandate and no memory of the original session.
 *
 * Backend cascade (first available wins):
 *   1. Anthropic API  (ANTHROPIC_API_KEY)  → claude-haiku-4-5-20251001
 *   2. OpenAI API     (OPENAI_API_KEY)     → gpt-4o-mini
 *   3. Ollama         (OLLAMA_HOST)        → first available model
 *   4. Rule-based     (always available)   → deterministic JS checklist
 *
 * Override: set REFLECT_EVALUATOR=anthropic|openai|ollama|rules to force a backend.
 */
'use strict';

const fs    = require('fs');
const path  = require('path');
const http  = require('http');
const https = require('https');

const REFLECT_DIR          = path.join(process.cwd(), '.reflect');
const PROPOSALS_FILE       = path.join(REFLECT_DIR, 'proposals.json');
const EVALUATOR_PROMPT_FILE = path.join(__dirname, '..', 'assets', 'evaluator-prompt.md');

// ── Config ────────────────────────────────────────────────────────────────────
const FORCED_BACKEND = process.env.REFLECT_EVALUATOR; // optional override

const ANTHROPIC_KEY  = process.env.ANTHROPIC_API_KEY;
const OPENAI_KEY     = process.env.OPENAI_API_KEY;
const OLLAMA_HOST    = process.env.OLLAMA_HOST || 'localhost';
const OLLAMA_PORT    = parseInt(process.env.OLLAMA_PORT || '11434', 10);

const GEN_PARAMS = { temperature: 0.1, max_tokens: 400 };

// ── Loaders ───────────────────────────────────────────────────────────────────
function loadProposals() {
  if (!fs.existsSync(PROPOSALS_FILE)) return [];
  try { return JSON.parse(fs.readFileSync(PROPOSALS_FILE, 'utf8')); }
  catch { return []; }
}

function loadEvaluatorPrompt() {
  try { return fs.readFileSync(EVALUATOR_PROMPT_FILE, 'utf8'); }
  catch { return FALLBACK_PROMPT; }
}

function loadCurrentMemory() {
  try { return fs.readFileSync(path.join(process.cwd(), 'MEMORY.md'), 'utf8').slice(0, 2000); }
  catch { return '(MEMORY.md not found)'; }
}

// ── Message builder ───────────────────────────────────────────────────────────
function buildUserMessage(proposal, memory) {
  return `
## Current MEMORY.md (excerpt)
${memory}

## Proposal to evaluate
ID: ${proposal.id}
Tool: ${proposal.tool}
Error pattern: ${proposal.error_pattern}
Recurrence: ${proposal.recurrence}x across ${proposal.session_count} distinct sessions
Blast tier: ${proposal.blast_tier} (writes to: ${proposal.blast_target})
Preliminary confidence: ${proposal.confidence}

Problem: ${proposal.hypothesis.problem}
Proposed change: ${proposal.hypothesis.proposed_change}
Success criteria: ${proposal.hypothesis.success_criteria}

Sample inputs that triggered the error:
${(proposal.sample_inputs || []).slice(0, 3).map((s, i) => `${i + 1}. ${s}`).join('\n') || '(none recorded)'}

---
DECISION: APPROVE | REJECT | DEFER
CONFIDENCE: 0.0-1.0
REASONING: (2-3 sentences)
MODIFICATION: (only if APPROVE — exact text to add to ${proposal.blast_target})
`.trim();
}

// ── Backend: Anthropic ────────────────────────────────────────────────────────
function callAnthropic(systemPrompt, userMessage) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({
      model: 'claude-haiku-4-5-20251001',
      max_tokens: GEN_PARAMS.max_tokens,
      system: systemPrompt,
      messages: [{ role: 'user', content: userMessage }],
    });

    const req = https.request({
      hostname: 'api.anthropic.com',
      path: '/v1/messages',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body),
        'x-api-key': ANTHROPIC_KEY,
        'anthropic-version': '2023-06-01',
      },
    }, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          if (parsed.error) return reject(new Error('Anthropic: ' + parsed.error.message));
          resolve({ text: parsed?.content?.[0]?.text || '', backend: 'anthropic/claude-haiku-4-5-20251001' });
        } catch { reject(new Error('Anthropic parse error: ' + data.slice(0, 200))); }
      });
    });

    req.on('error', e => reject(new Error('Anthropic unreachable: ' + e.message)));
    req.setTimeout(30000, () => { req.destroy(); reject(new Error('Anthropic timeout')); });
    req.write(body); req.end();
  });
}

// ── Backend: OpenAI ───────────────────────────────────────────────────────────
function callOpenAI(systemPrompt, userMessage) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({
      model: 'gpt-4o-mini',
      max_tokens: GEN_PARAMS.max_tokens,
      temperature: GEN_PARAMS.temperature,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userMessage },
      ],
    });

    const req = https.request({
      hostname: 'api.openai.com',
      path: '/v1/chat/completions',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body),
        'Authorization': 'Bearer ' + OPENAI_KEY,
      },
    }, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          if (parsed.error) return reject(new Error('OpenAI: ' + parsed.error.message));
          resolve({ text: parsed?.choices?.[0]?.message?.content || '', backend: 'openai/gpt-4o-mini' });
        } catch { reject(new Error('OpenAI parse error: ' + data.slice(0, 200))); }
      });
    });

    req.on('error', e => reject(new Error('OpenAI unreachable: ' + e.message)));
    req.setTimeout(30000, () => { req.destroy(); reject(new Error('OpenAI timeout')); });
    req.write(body); req.end();
  });
}

// ── Backend: Ollama ───────────────────────────────────────────────────────────
async function getOllamaModel() {
  // Prefer REFLECT_EVAL_MODEL env var, otherwise use first available model
  if (process.env.REFLECT_EVAL_MODEL) return process.env.REFLECT_EVAL_MODEL;
  return new Promise((resolve, reject) => {
    http.get(`http://${OLLAMA_HOST}:${OLLAMA_PORT}/api/tags`, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try {
          const models = JSON.parse(data)?.models || [];
          if (models.length === 0) return reject(new Error('No Ollama models installed'));
          resolve(models[0].name);
        } catch { reject(new Error('Ollama tags parse error')); }
      });
    }).on('error', e => reject(new Error('Ollama unreachable: ' + e.message)));
  });
}

function callOllamaModel(model, systemPrompt, userMessage) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({
      model,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userMessage },
      ],
      stream: false,
      options: { temperature: GEN_PARAMS.temperature, num_predict: GEN_PARAMS.max_tokens },
    });

    const req = http.request({
      hostname: OLLAMA_HOST, port: OLLAMA_PORT,
      path: '/v1/chat/completions', method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) },
    }, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try { resolve({ text: JSON.parse(data)?.choices?.[0]?.message?.content || '', backend: 'ollama/' + model }); }
        catch { reject(new Error('Ollama parse error: ' + data.slice(0, 200))); }
      });
    });

    req.on('error', e => reject(new Error('Ollama error: ' + e.message)));
    req.setTimeout(90000, () => { req.destroy(); reject(new Error('Ollama timeout')); });
    req.write(body); req.end();
  });
}

async function callOllama(systemPrompt, userMessage) {
  const model = await getOllamaModel();
  return callOllamaModel(model, systemPrompt, userMessage);
}

// ── Backend: Rule-based (zero dependencies) ───────────────────────────────────
function evaluateByRules(proposal) {
  const reasons = [];
  let decision = 'APPROVE';

  // Hard blocks — any one of these = REJECT
  if (proposal.session_count < 2) {
    decision = 'REJECT';
    reasons.push('single session only (session_count < 2)');
  }
  if (proposal.recurrence < 3) {
    decision = 'REJECT';
    reasons.push('insufficient recurrence (< 3)');
  }

  const change = (proposal.hypothesis?.proposed_change || '').toLowerCase();
  const VAGUE_PATTERNS = ['be more careful', 'double check', 'pay attention', 'be careful', 'always verify'];
  if (VAGUE_PATTERNS.some(p => change.includes(p))) {
    decision = 'REJECT';
    reasons.push('proposed change is vague advice, not a specific rule');
  }

  const SYMPTOM_PATTERNS = ['retry', 'wait and retry', 'try again', 'increase timeout'];
  if (SYMPTOM_PATTERNS.some(p => change.includes(p)) && !change.includes('because')) {
    decision = 'REJECT';
    reasons.push('proposed change treats symptom, not root cause');
  }

  // Soft concerns — push toward DEFER
  if (decision === 'APPROVE') {
    if (proposal.session_count < 3 && proposal.recurrence < 5) {
      decision = 'DEFER';
      reasons.push('borderline evidence (< 3 sessions and < 5 recurrences)');
    }
    if (proposal.confidence < 0.50) {
      decision = 'DEFER';
      reasons.push('low preliminary confidence (< 0.50)');
    }
  }

  const confidence = decision === 'APPROVE' ? Math.min(proposal.confidence + 0.1, 0.90)
                   : decision === 'REJECT'  ? 0.85
                   : 0.60;

  return {
    text: [
      `DECISION: ${decision}`,
      `CONFIDENCE: ${confidence.toFixed(2)}`,
      `REASONING: Rule-based evaluation. ${reasons.length ? reasons.join('; ') + '.' : 'All quantitative criteria met.'}`,
    ].join('\n'),
    backend: 'rules',
  };
}

// ── Backend cascade ───────────────────────────────────────────────────────────
async function runEvaluator(systemPrompt, userMessage, proposal) {
  const order = FORCED_BACKEND
    ? [FORCED_BACKEND]
    : ['anthropic', 'openai', 'ollama', 'rules'];

  for (const backend of order) {
    try {
      if (backend === 'anthropic' && ANTHROPIC_KEY) {
        return await callAnthropic(systemPrompt, userMessage);
      }
      if (backend === 'openai' && OPENAI_KEY) {
        return await callOpenAI(systemPrompt, userMessage);
      }
      if (backend === 'ollama') {
        return await callOllama(systemPrompt, userMessage);
      }
      if (backend === 'rules') {
        return evaluateByRules(proposal);
      }
    } catch (e) {
      process.stderr.write(` [${backend} failed: ${e.message.slice(0, 60)}]`);
      // continue to next backend
    }
  }

  // Should never reach here — rules always works
  return evaluateByRules(proposal);
}

// ── Response parser ───────────────────────────────────────────────────────────
function parseResponse(text, backend) {
  const decision     = (text.match(/DECISION:\s*(APPROVE|REJECT|DEFER)/i) || [])[1]?.toUpperCase() || 'DEFER';
  const confidence   = parseFloat((text.match(/CONFIDENCE:\s*([\d.]+)/i) || [])[1] || '0.5');
  const reasoning    = (text.match(/REASONING:\s*(.+?)(?=\nMODIFICATION:|$)/si) || [])[1]?.trim() || text.slice(0, 300);
  const modification = (text.match(/MODIFICATION:\s*(.+?)$/si) || [])[1]?.trim() || null;

  return {
    decision,
    confidence: isNaN(confidence) ? 0.5 : Math.min(1, Math.max(0, confidence)),
    reasoning: reasoning || '(no reasoning)',
    modification,
    evaluator: backend,
  };
}

// ── Main ──────────────────────────────────────────────────────────────────────
async function main() {
  const proposals = loadProposals();
  const pending   = proposals.filter(p => p.status === 'pending_evaluation');

  if (pending.length === 0) {
    process.stdout.write('no proposals pending evaluation');
    return;
  }

  const systemPrompt  = loadEvaluatorPrompt();
  const currentMemory = loadCurrentMemory();
  const results       = [];

  for (const proposal of pending) {
    process.stderr.write(`  evaluating ${proposal.id}...`);
    const start = Date.now();

    try {
      const userMessage          = buildUserMessage(proposal, currentMemory);
      const { text, backend }    = await runEvaluator(systemPrompt, userMessage, proposal);
      const evaluation           = parseResponse(text, backend);
      const elapsed              = ((Date.now() - start) / 1000).toFixed(1);

      proposal.evaluation    = evaluation;
      proposal.evaluated_at  = new Date().toISOString();
      proposal.status        = evaluation.decision === 'APPROVE' ? 'approved'
                             : evaluation.decision === 'REJECT'  ? 'rejected'
                             : 'deferred';

      process.stderr.write(` ${proposal.status} via ${backend} (${evaluation.confidence.toFixed(2)}, ${elapsed}s)\n`);
      results.push(`${proposal.id}: ${proposal.status} [${evaluation.confidence.toFixed(2)}] via ${backend}`);
    } catch (e) {
      // Last-resort fallback — rules can't throw, but just in case
      const fallback = evaluateByRules(proposal);
      const evaluation = parseResponse(fallback.text, 'rules');
      proposal.evaluation   = evaluation;
      proposal.evaluated_at = new Date().toISOString();
      proposal.status       = 'deferred';
      results.push(`${proposal.id}: deferred (fallback rules, error: ${e.message.slice(0, 50)})`);
    }
  }

  fs.writeFileSync(PROPOSALS_FILE, JSON.stringify(proposals, null, 2), 'utf8');
  process.stdout.write(results.join(', ') || 'done');
}

main().catch(e => {
  process.stdout.write('evaluate error: ' + e.message);
  process.exit(0);
});

// ── Fallback evaluator prompt (if assets/evaluator-prompt.md missing) ─────────
const FALLBACK_PROMPT = `You are a skeptical evaluator for an AI agent's self-improvement system.
Find reasons to REJECT or DEFER. Approve only when confident.

Approve only if ALL are true:
1. Specific and falsifiable — not vague advice
2. Non-contradictory with current MEMORY.md
3. Recurring across at least 2 distinct sessions
4. Addresses root cause, not symptom
5. Has measurable success criteria

Reject if: generic, contradictory, single-session, or treats a symptom.
Defer if: fewer than 5 recurrences, ambiguous root cause, or needs operator judgment.

DECISION: APPROVE | REJECT | DEFER
CONFIDENCE: 0.0-1.0
REASONING: (2-3 sentences)
MODIFICATION: (only if APPROVE — exact text to add)`;
