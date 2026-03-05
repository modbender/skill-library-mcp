#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

const STATE_DIR = path.join(process.env.HOME, '.openclaw/workspace/.agent-evolution');
const STATE_FILE = path.join(STATE_DIR, 'state.json');

// --- State helpers ---

function loadState() {
  if (!fs.existsSync(STATE_FILE)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
}

function saveState(state) {
  if (!fs.existsSync(STATE_DIR)) {
    fs.mkdirSync(STATE_DIR, { recursive: true });
  }
  fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2) + '\n');
}

function ensureState() {
  const state = loadState();
  if (!state) {
    out({ error: 'state.json not found. Run: node evolution.js init' });
    process.exit(1);
  }
  return state;
}

function out(obj) {
  console.log(JSON.stringify(obj, null, 2));
}

function now() {
  return new Date().toISOString();
}

// --- Weight calculation ---

function calcWeight(rule) {
  const base = 1.0;
  return Math.round((base + rule.execCount * 0.1 - rule.violationCount * 0.3) * 100) / 100;
}

// --- Commands ---

function cmdInit() {
  if (fs.existsSync(STATE_FILE)) {
    out({ status: 'already_exists', path: STATE_FILE });
    return;
  }
  const state = {
    rules: {},
    identity: {
      name: '',
      version: '1.0',
      coreTraits: [],
      activeGoals: [],
      currentPhase: '',
      relationshipMap: {},
      evolutionLog: []
    },
    patterns: {
      consecutive_code_writes: { count: 0, threshold: 3, alert: '统帅不亲自写代码', lastReset: null },
      repeated_operation: { history: [], threshold: 2, alert: '重复两次就封装', lastReset: null },
      debug_loop: { issue: null, attempts: 0, threshold: 3, alert: '换思路或报告', lastReset: null }
    }
  };
  saveState(state);
  out({ status: 'initialized', path: STATE_FILE });
}

function cmdCheck(ruleId) {
  if (!ruleId) { out({ error: 'usage: check <rule_id>' }); process.exit(1); }
  const state = ensureState();
  const rule = state.rules[ruleId];
  if (!rule) { out({ error: `rule not found: ${ruleId}` }); process.exit(1); }
  rule.execCount++;
  rule.lastExec = now();
  rule.weight = calcWeight(rule);
  saveState(state);
  out({ status: 'checked', ruleId, description: rule.description, execCount: rule.execCount, weight: rule.weight });
}

function cmdViolation(ruleId, context) {
  if (!ruleId) { out({ error: 'usage: violation <rule_id> <context>' }); process.exit(1); }
  const state = ensureState();
  const rule = state.rules[ruleId];
  if (!rule) { out({ error: `rule not found: ${ruleId}` }); process.exit(1); }
  rule.violationCount++;
  rule.lastViolation = now();
  rule.weight = calcWeight(rule);
  saveState(state);
  out({ status: 'violation_recorded', ruleId, context: context || '', violationCount: rule.violationCount, weight: rule.weight });
}

function cmdStats() {
  const state = ensureState();
  const rules = Object.entries(state.rules).map(([id, r]) => ({
    id, description: r.description, source: r.source,
    execCount: r.execCount, violationCount: r.violationCount,
    weight: r.weight, lastExec: r.lastExec, lastViolation: r.lastViolation
  }));
  rules.sort((a, b) => a.weight - b.weight);
  out({ totalRules: rules.length, rules });
}

function cmdAddRule(ruleId, description, source) {
  if (!ruleId || !description) { out({ error: 'usage: add-rule <rule_id> <description> <source>' }); process.exit(1); }
  const state = ensureState();
  if (state.rules[ruleId]) { out({ error: `rule already exists: ${ruleId}` }); process.exit(1); }
  state.rules[ruleId] = {
    description,
    source: source || 'manual',
    execCount: 0,
    violationCount: 0,
    lastExec: null,
    lastViolation: null,
    weight: 1.0
  };
  saveState(state);
  out({ status: 'rule_added', ruleId, description, source: source || 'manual' });
}

function cmdIdentity() {
  const state = ensureState();
  out(state.identity);
}

function cmdIdentityUpdate(field, value) {
  if (!field || value === undefined) { out({ error: 'usage: identity-update <field> <value>' }); process.exit(1); }
  const state = ensureState();
  // Handle array fields
  const arrayFields = ['coreTraits', 'activeGoals'];
  if (arrayFields.includes(field)) {
    try { value = JSON.parse(value); } catch (_) { value = [value]; }
  }
  // Handle object fields
  if (field === 'relationshipMap') {
    try { value = JSON.parse(value); } catch (_) { /* keep as string */ }
  }
  state.identity[field] = value;
  saveState(state);
  out({ status: 'identity_updated', field, value });
}

function cmdEvolve(change, trigger) {
  if (!change) { out({ error: 'usage: evolve <change> <trigger>' }); process.exit(1); }
  const state = ensureState();
  const entry = { date: now().slice(0, 10), change, trigger: trigger || 'unknown' };
  state.identity.evolutionLog.push(entry);
  saveState(state);
  out({ status: 'evolution_recorded', entry });
}

function cmdLog(actionType, detail) {
  if (!actionType) { out({ error: 'usage: log <action_type> <detail>' }); process.exit(1); }
  const state = ensureState();
  const p = state.patterns;

  // consecutive_code_writes
  if (actionType === 'code_write') {
    p.consecutive_code_writes.count++;
  } else {
    p.consecutive_code_writes.count = 0;
  }

  // repeated_operation
  const hist = p.repeated_operation.history;
  hist.push({ type: actionType, detail: detail || '', time: now() });
  if (hist.length > 20) hist.splice(0, hist.length - 20);

  // debug_loop
  if (actionType === 'debug') {
    const issue = detail || 'unknown';
    if (p.debug_loop.issue === issue) {
      p.debug_loop.attempts++;
    } else {
      p.debug_loop.issue = issue;
      p.debug_loop.attempts = 1;
    }
  }

  saveState(state);
  out({ status: 'logged', actionType, detail: detail || '' });
}

function cmdDetect() {
  const state = ensureState();
  const p = state.patterns;
  const alerts = [];

  if (p.consecutive_code_writes.count >= p.consecutive_code_writes.threshold) {
    alerts.push({ pattern: 'consecutive_code_writes', count: p.consecutive_code_writes.count, alert: p.consecutive_code_writes.alert });
  }

  // Check repeated operations: same action_type >= threshold times in recent history
  const hist = p.repeated_operation.history;
  if (hist.length >= 2) {
    const typeCounts = {};
    for (const h of hist.slice(-10)) {
      typeCounts[h.type] = (typeCounts[h.type] || 0) + 1;
    }
    for (const [type, count] of Object.entries(typeCounts)) {
      if (count > p.repeated_operation.threshold) {
        alerts.push({ pattern: 'repeated_operation', type, count, alert: p.repeated_operation.alert });
      }
    }
  }

  if (p.debug_loop.attempts >= p.debug_loop.threshold) {
    alerts.push({ pattern: 'debug_loop', issue: p.debug_loop.issue, attempts: p.debug_loop.attempts, alert: p.debug_loop.alert });
  }

  out({ alerts, hasAlerts: alerts.length > 0 });
}

function cmdReset(patternId) {
  if (!patternId) { out({ error: 'usage: reset <pattern_id>' }); process.exit(1); }
  const state = ensureState();
  const p = state.patterns[patternId];
  if (!p) { out({ error: `pattern not found: ${patternId}` }); process.exit(1); }
  if ('count' in p) p.count = 0;
  if ('history' in p) p.history = [];
  if ('attempts' in p) { p.attempts = 0; p.issue = null; }
  p.lastReset = now();
  saveState(state);
  out({ status: 'reset', patternId });
}

function cmdReport() {
  const state = ensureState();

  // Rules summary
  const ruleEntries = Object.entries(state.rules);
  const lowWeight = ruleEntries.filter(([, r]) => r.weight < 0.5).map(([id, r]) => ({ id, weight: r.weight, violations: r.violationCount }));
  const neverExecuted = ruleEntries.filter(([, r]) => r.execCount === 0).map(([id]) => id);
  const topExecuted = ruleEntries.sort((a, b) => b[1].execCount - a[1].execCount).slice(0, 5).map(([id, r]) => ({ id, execCount: r.execCount, weight: r.weight }));

  // Pattern alerts
  const p = state.patterns;
  const alerts = [];
  if (p.consecutive_code_writes.count >= p.consecutive_code_writes.threshold) alerts.push(p.consecutive_code_writes.alert);
  if (p.debug_loop.attempts >= p.debug_loop.threshold) alerts.push(p.debug_loop.alert);

  out({
    totalRules: ruleEntries.length,
    lowWeightRules: lowWeight,
    neverExecuted,
    topExecuted,
    identity: { name: state.identity.name, version: state.identity.version, phase: state.identity.currentPhase },
    recentEvolution: state.identity.evolutionLog.slice(-3),
    patternAlerts: alerts
  });
}

// --- CLI dispatch ---

const [,, cmd, ...args] = process.argv;

const commands = {
  init: cmdInit,
  check: () => cmdCheck(args[0]),
  violation: () => cmdViolation(args[0], args.slice(1).join(' ')),
  stats: cmdStats,
  'add-rule': () => cmdAddRule(args[0], args[1], args[2]),
  identity: cmdIdentity,
  'identity-update': () => cmdIdentityUpdate(args[0], args.slice(1).join(' ')),
  evolve: () => cmdEvolve(args[0], args.slice(1).join(' ')),
  log: () => cmdLog(args[0], args.slice(1).join(' ')),
  detect: cmdDetect,
  reset: () => cmdReset(args[0]),
  report: cmdReport
};

if (!cmd || !commands[cmd]) {
  out({
    error: cmd ? `unknown command: ${cmd}` : 'no command specified',
    commands: Object.keys(commands)
  });
  process.exit(1);
}

commands[cmd]();
