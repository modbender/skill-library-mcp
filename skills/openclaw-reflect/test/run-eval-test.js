#!/usr/bin/env node
/**
 * run-eval-test.js — Tests all evaluator backends against synthetic proposals.
 *
 * Flags:
 *   (none)      binary APPLY/HOLD via Dolphin 8B (Ollama) — legacy test
 *   --haiku     three-way via Claude Haiku (Anthropic API)
 *   --openai    three-way via gpt-4o-mini (OpenAI API)
 *   --ollama    three-way via first available Ollama model
 *   --rules     rule-based JS evaluator (no model, zero cost)
 *   --all       run all available backends and compare
 *
 * Run from: skills/openclaw-reflect/test/
 *   node run-eval-test.js --rules
 *   node run-eval-test.js --haiku
 *   node run-eval-test.js --all
 */
'use strict';

const fs    = require('fs');
const path  = require('path');
const http  = require('http');
const https = require('https');

const ASSETS_DIR   = path.join(__dirname, '..', 'assets');
const PROMPT_FILE  = path.join(ASSETS_DIR, 'evaluator-prompt.md');

const ANTHROPIC_KEY = process.env.ANTHROPIC_API_KEY;
const OPENAI_KEY    = process.env.OPENAI_API_KEY;
const OLLAMA_HOST   = process.env.OLLAMA_HOST || 'localhost';
const OLLAMA_PORT   = parseInt(process.env.OLLAMA_PORT || '11434', 10);

const ARGS = new Set(process.argv.slice(2));
const USE_ALL    = ARGS.has('--all');
const USE_HAIKU  = ARGS.has('--haiku')  || USE_ALL;
const USE_OPENAI = ARGS.has('--openai') || USE_ALL;
const USE_OLLAMA = ARGS.has('--ollama') || USE_ALL;
const USE_RULES  = ARGS.has('--rules')  || USE_ALL || (!USE_HAIKU && !USE_OPENAI && !USE_OLLAMA);

// ── Test cases ────────────────────────────────────────────────────────────────
// expected: what a correct evaluator should decide (APPROVE/REJECT/DEFER)
// Rules backend maps APPROVE→APPROVE, REJECT→REJECT, DEFER→DEFER
const TEST_CASES = [
  {
    name: 'specific, recurring path error (4 sessions)',
    expected: 'APPROVE',
    proposal: {
      id: 'test-001', tool: 'Bash',
      error_pattern: 'permission denied on /c/Users/sdysa/.openclaw/openclaw.json',
      recurrence: 7, session_count: 4, confidence: 0.78,
      blast_tier: 1, blast_target: 'MEMORY.md',
      sample_inputs: [
        'cat /c/Users/sdysa/.openclaw/openclaw.json',
        'python3 /c/Users/sdysa/.openclaw/workspace/moltbook.py wallet',
      ],
      hypothesis: {
        problem: 'Bash fails with permission denied on openclaw.json 7 times across 4 sessions.',
        proposed_change: 'Add to MEMORY.md: The openclaw.json config file requires elevated access. Use the OpenClaw CLI or moltbook.py instead of reading the file directly.',
        success_criteria: 'No more permission denied errors on openclaw.json in the next 5 sessions.',
      },
    },
  },
  {
    name: 'python3 shim error (3 sessions)',
    expected: 'APPROVE',
    proposal: {
      id: 'test-002', tool: 'Bash',
      error_pattern: 'python3: command not found',
      recurrence: 5, session_count: 3, confidence: 0.82,
      blast_tier: 1, blast_target: 'MEMORY.md',
      sample_inputs: [
        'python3 skills/openclaw-sentry/sentry.py scan',
        'python3 workspace/moltbook.py post',
      ],
      hypothesis: {
        problem: 'Bash fails with python3 not found 5 times across 3 sessions. Windows python3 is a Microsoft Store stub.',
        proposed_change: 'Add to MEMORY.md: On Windows, python3 is a Microsoft Store shim. Use the full path C:/Users/sdysa/AppData/Local/Programs/Python/Python312/python.exe or sys.executable.',
        success_criteria: 'No more python3 not found errors in the next 5 sessions.',
      },
    },
  },
  {
    name: 'vague generic advice',
    expected: 'REJECT',
    proposal: {
      id: 'test-003', tool: 'Bash',
      error_pattern: 'generic_error',
      recurrence: 3, session_count: 2, confidence: 0.45,
      blast_tier: 2, blast_target: 'CLAUDE.md',
      sample_inputs: ['various commands'],
      hypothesis: {
        problem: 'Bash tool has encountered errors 3 times across 2 sessions.',
        proposed_change: 'Add to CLAUDE.md: Be more careful when running bash commands. Double check commands before executing.',
        success_criteria: 'Fewer bash errors.',
      },
    },
  },
  {
    name: 'single session only (session_count=1)',
    expected: 'REJECT',
    proposal: {
      id: 'test-004', tool: 'Bash',
      error_pattern: 'connection refused',
      recurrence: 8, session_count: 1, confidence: 0.61,
      blast_tier: 1, blast_target: 'MEMORY.md',
      sample_inputs: [
        'curl http://localhost:18789/v1/models',
        'curl http://localhost:11434/api/tags',
      ],
      hypothesis: {
        problem: 'Connection refused errors occurred 8 times in 1 session.',
        proposed_change: 'Add to MEMORY.md: Always retry connections up to 3 times before failing.',
        success_criteria: 'Fewer connection errors.',
      },
    },
  },
  {
    name: 'ambiguous root cause, low sessions',
    expected: 'DEFER',
    proposal: {
      id: 'test-005', tool: 'WebFetch',
      error_pattern: 'SSL certificate has expired',
      recurrence: 3, session_count: 2, confidence: 0.41,
      blast_tier: 1, blast_target: 'MEMORY.md',
      sample_inputs: [
        'https://clawhub.io/u/AtlasPA',
        'https://clawhub.io/api/skills',
      ],
      hypothesis: {
        problem: 'WebFetch fails with SSL errors on clawhub.io 3 times across 2 sessions. Root cause unclear: could be site issue or environment.',
        proposed_change: 'Add to MEMORY.md: clawhub.io has SSL issues. Use clawhub.ai instead.',
        success_criteria: 'No more SSL errors on clawhub in next 5 sessions.',
      },
    },
  },
];

// ── Prompt ────────────────────────────────────────────────────────────────────
function loadPrompt() {
  try { return fs.readFileSync(PROMPT_FILE, 'utf8'); }
  catch { return 'You are a skeptical evaluator. APPROVE only clear, specific, recurring improvements. REJECT vague or single-session patterns. DEFER when uncertain.\n\nDECISION: APPROVE | REJECT | DEFER\nCONFIDENCE: 0.0-1.0\nREASONING: (2-3 sentences)'; }
}

// ── Message builder ───────────────────────────────────────────────────────────
function buildMessage(tc) {
  const p = tc.proposal;
  return `
## Current MEMORY.md (excerpt)
- Skills dir: c:\\Users\\sdysa\\.openclaw\\workspace\\skills\\
- Platform: Windows 10, bash shell
- OpenClaw gateway: localhost:18789

## Proposal to evaluate
ID: ${p.id}
Tool: ${p.tool}
Error pattern: ${p.error_pattern}
Recurrence: ${p.recurrence}x across ${p.session_count} sessions
Blast tier: ${p.blast_tier} (target: ${p.blast_target})
Confidence: ${p.confidence}

Problem: ${p.hypothesis.problem}
Proposed change: ${p.hypothesis.proposed_change}
Success criteria: ${p.hypothesis.success_criteria}

Sample inputs: ${p.sample_inputs.join(', ')}

---
DECISION: APPROVE | REJECT | DEFER
CONFIDENCE: 0.0-1.0
REASONING: (2-3 sentences)
MODIFICATION: (only if APPROVE)
`.trim();
}

// ── Backends ──────────────────────────────────────────────────────────────────
function callAnthropic(system, user) {
  return new Promise((resolve, reject) => {
    if (!ANTHROPIC_KEY) return reject(new Error('ANTHROPIC_API_KEY not set'));
    const body = JSON.stringify({
      model: 'claude-haiku-4-5-20251001', max_tokens: 400,
      system, messages: [{ role: 'user', content: user }],
    });
    const req = https.request({
      hostname: 'api.anthropic.com', path: '/v1/messages', method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body),
                 'x-api-key': ANTHROPIC_KEY, 'anthropic-version': '2023-06-01' },
    }, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          if (parsed.error) return reject(new Error(parsed.error.message));
          resolve(parsed?.content?.[0]?.text || '');
        } catch { reject(new Error('parse: ' + data.slice(0, 100))); }
      });
    });
    req.on('error', reject);
    req.setTimeout(30000, () => { req.destroy(); reject(new Error('timeout')); });
    req.write(body); req.end();
  });
}

function callOpenAI(system, user) {
  return new Promise((resolve, reject) => {
    if (!OPENAI_KEY) return reject(new Error('OPENAI_API_KEY not set'));
    const body = JSON.stringify({
      model: 'gpt-4o-mini', max_tokens: 400, temperature: 0.1,
      messages: [{ role: 'system', content: system }, { role: 'user', content: user }],
    });
    const req = https.request({
      hostname: 'api.openai.com', path: '/v1/chat/completions', method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body),
                 'Authorization': 'Bearer ' + OPENAI_KEY },
    }, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          if (parsed.error) return reject(new Error(parsed.error.message));
          resolve(parsed?.choices?.[0]?.message?.content || '');
        } catch { reject(new Error('parse: ' + data.slice(0, 100))); }
      });
    });
    req.on('error', reject);
    req.setTimeout(30000, () => { req.destroy(); reject(new Error('timeout')); });
    req.write(body); req.end();
  });
}

function getFirstOllamaModel() {
  return new Promise((resolve, reject) => {
    http.get(`http://${OLLAMA_HOST}:${OLLAMA_PORT}/api/tags`, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try {
          const models = JSON.parse(data)?.models || [];
          if (!models.length) return reject(new Error('No Ollama models installed'));
          resolve(models[0].name);
        } catch { reject(new Error('Ollama tags parse error')); }
      });
    }).on('error', e => reject(new Error('Ollama unreachable: ' + e.message)));
  });
}

function callOllamaModel(model, system, user) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({
      model, stream: false,
      messages: [{ role: 'system', content: system }, { role: 'user', content: user }],
      options: { temperature: 0.1, num_predict: 400 },
    });
    const req = http.request({
      hostname: OLLAMA_HOST, port: OLLAMA_PORT,
      path: '/v1/chat/completions', method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) },
    }, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try { resolve(JSON.parse(data)?.choices?.[0]?.message?.content || ''); }
        catch { reject(new Error('parse: ' + data.slice(0, 100))); }
      });
    });
    req.on('error', reject);
    req.setTimeout(90000, () => { req.destroy(); reject(new Error('timeout')); });
    req.write(body); req.end();
  });
}

function evaluateByRules(tc) {
  const p = tc.proposal;
  const reasons = [];
  let decision = 'APPROVE';

  if (p.session_count < 2) { decision = 'REJECT'; reasons.push('single session (session_count < 2)'); }
  if (p.recurrence < 3)    { decision = 'REJECT'; reasons.push('insufficient recurrence (< 3)'); }

  const change = (p.hypothesis?.proposed_change || '').toLowerCase();
  const VAGUE = ['be more careful', 'double check', 'pay attention', 'be careful', 'always verify'];
  if (VAGUE.some(v => change.includes(v))) { decision = 'REJECT'; reasons.push('vague advice'); }

  const SYMPTOM = ['retry', 'wait and retry', 'try again', 'increase timeout'];
  if (SYMPTOM.some(s => change.includes(s)) && !change.includes('because')) {
    decision = 'REJECT'; reasons.push('treats symptom not cause');
  }

  if (decision === 'APPROVE') {
    if (p.session_count < 3 && p.recurrence < 5) { decision = 'DEFER'; reasons.push('borderline evidence'); }
    if (p.confidence < 0.50) { decision = 'DEFER'; reasons.push('low confidence (< 0.50)'); }
  }

  return `DECISION: ${decision}\nCONFIDENCE: ${decision === 'APPROVE' ? '0.80' : decision === 'REJECT' ? '0.85' : '0.60'}\nREASONING: Rule-based. ${reasons.length ? reasons.join('; ') + '.' : 'All quantitative criteria met.'}`;
}

// ── Parser ────────────────────────────────────────────────────────────────────
function parse(text) {
  const decision   = (text.match(/DECISION:\s*(APPROVE|REJECT|DEFER)/i) || [])[1]?.toUpperCase() || 'DEFER';
  const confidence = parseFloat((text.match(/CONFIDENCE:\s*([\d.]+)/i) || [])[1] || '0.5');
  const reasoning  = (text.match(/REASONING:\s*(.+?)(?=\nMODIFICATION:|$)/si) || [])[1]?.trim() || text.slice(0, 200);
  return { decision, confidence: Math.min(1, Math.max(0, isNaN(confidence) ? 0.5 : confidence)), reasoning };
}

// ── Runner ────────────────────────────────────────────────────────────────────
async function runBackend(label, callFn, systemPrompt) {
  console.log(`\n${'─'.repeat(60)}`);
  console.log(`Backend: ${label}`);
  console.log('─'.repeat(60));

  let passed = 0;
  const results = [];

  for (const tc of TEST_CASES) {
    process.stdout.write(`\n  [${tc.name}]\n    Calling...`);
    const start = Date.now();
    try {
      const raw     = await callFn(systemPrompt, buildMessage(tc));
      const result  = parse(raw);
      const elapsed = ((Date.now() - start) / 1000).toFixed(1);
      const pass    = result.decision === tc.expected;
      if (pass) passed++;
      console.log(` ${elapsed}s`);
      console.log(`    ${pass ? '✓' : '✗'} ${result.decision} (expected: ${tc.expected})  conf: ${result.confidence.toFixed(2)}`);
      console.log(`    ${result.reasoning.slice(0, 140)}`);
      results.push({ name: tc.name, expected: tc.expected, got: result.decision, pass });
    } catch (e) {
      console.log(` ERROR: ${e.message}`);
      results.push({ name: tc.name, expected: tc.expected, got: 'ERROR', pass: false });
    }
  }

  const accuracy = (passed / TEST_CASES.length * 100).toFixed(0);
  console.log(`\n  Score: ${passed}/${TEST_CASES.length} (${accuracy}%)`);
  return { label, passed, total: TEST_CASES.length, accuracy: parseInt(accuracy) };
}

async function main() {
  const systemPrompt = loadPrompt();
  const scores = [];

  if (USE_RULES) {
    const s = await runBackend('Rule-based (no model)', (_, user) => Promise.resolve(evaluateByRules(TEST_CASES.find(tc => buildMessage(tc) === user) || TEST_CASES[0])), systemPrompt);
    // Rules backend passes proposal directly — rewire to use tc directly
    scores.push(await runRules());
  }

  if (USE_HAIKU) {
    scores.push(await runBackend('Claude Haiku (Anthropic)', (sys, usr) => callAnthropic(sys, usr), systemPrompt));
  }

  if (USE_OPENAI) {
    scores.push(await runBackend('GPT-4o-mini (OpenAI)', (sys, usr) => callOpenAI(sys, usr), systemPrompt));
  }

  if (USE_OLLAMA) {
    try {
      const model = await getFirstOllamaModel();
      scores.push(await runBackend(`Ollama/${model}`, (sys, usr) => callOllamaModel(model, sys, usr), systemPrompt));
    } catch (e) {
      console.log(`\nOllama unavailable: ${e.message}`);
    }
  }

  if (scores.length > 1) {
    console.log(`\n${'═'.repeat(60)}`);
    console.log('Summary');
    console.log('═'.repeat(60));
    for (const s of scores) {
      console.log(`  ${s.label.padEnd(35)} ${s.passed}/${s.total}  (${s.accuracy}%)`);
    }
    const winner = scores.reduce((a, b) => a.accuracy >= b.accuracy ? a : b);
    console.log(`\n  Best: ${winner.label} at ${winner.accuracy}%`);
  }

  console.log('');
}

// Rules backend runs differently — directly against proposal objects
async function runRules() {
  console.log(`\n${'─'.repeat(60)}`);
  console.log('Backend: Rule-based (no model)');
  console.log('─'.repeat(60));

  let passed = 0;
  const results = [];

  for (const tc of TEST_CASES) {
    const raw    = evaluateByRules(tc);
    const result = parse(raw);
    const pass   = result.decision === tc.expected;
    if (pass) passed++;
    console.log(`\n  [${tc.name}]`);
    console.log(`    ${pass ? '✓' : '✗'} ${result.decision} (expected: ${tc.expected})  conf: ${result.confidence.toFixed(2)}`);
    console.log(`    ${result.reasoning.slice(0, 140)}`);
    results.push({ name: tc.name, expected: tc.expected, got: result.decision, pass });
  }

  const accuracy = (passed / TEST_CASES.length * 100).toFixed(0);
  console.log(`\n  Score: ${passed}/${TEST_CASES.length} (${accuracy}%)`);
  return { label: 'Rule-based (no model)', passed, total: TEST_CASES.length, accuracy: parseInt(accuracy) };
}

// Simplified main that avoids the rewiring complexity
async function run() {
  const systemPrompt = loadPrompt();
  const scores = [];

  if (USE_RULES)  scores.push(await runRules());
  if (USE_HAIKU)  scores.push(await runBackend('Claude Haiku (Anthropic)', callAnthropic, systemPrompt));
  if (USE_OPENAI) scores.push(await runBackend('GPT-4o-mini (OpenAI)', callOpenAI, systemPrompt));
  if (USE_OLLAMA) {
    try {
      const model = await getFirstOllamaModel();
      scores.push(await runBackend(`Ollama/${model}`, (s, u) => callOllamaModel(model, s, u), systemPrompt));
    } catch (e) { console.log(`\nOllama unavailable: ${e.message}`); }
  }

  if (scores.length > 1) {
    console.log(`\n${'═'.repeat(60)}`);
    console.log('Summary');
    console.log('═'.repeat(60));
    for (const s of scores) console.log(`  ${s.label.padEnd(38)} ${s.passed}/${s.total}  (${s.accuracy}%)`);
    const winner = scores.reduce((a, b) => a.accuracy >= b.accuracy ? a : b);
    console.log(`\n  Best: ${winner.label} at ${winner.accuracy}%`);
  }

  console.log('');
  process.exit(scores.every(s => s.passed === s.total) ? 0 : 1);
}

run().catch(e => { console.error('Fatal:', e.message); process.exit(1); });
