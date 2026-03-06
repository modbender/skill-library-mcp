#!/usr/bin/env node
/**
 * classify.js — Reads outcomes.jsonl, groups by error pattern + tool,
 * and writes patterns.json for patterns meeting the promotion threshold.
 *
 * Threshold: recurrence >= 3 across >= 2 distinct sessions.
 */
'use strict';

const fs = require('fs');
const path = require('path');

const REFLECT_DIR = path.join(process.cwd(), '.reflect');
const OUTCOMES_FILE = path.join(REFLECT_DIR, 'outcomes.jsonl');
const PATTERNS_FILE = path.join(REFLECT_DIR, 'patterns.json');

const RECURRENCE_MIN = 3;
const SESSION_MIN = 2;

function loadOutcomes() {
  if (!fs.existsSync(OUTCOMES_FILE)) return [];
  return fs.readFileSync(OUTCOMES_FILE, 'utf8')
    .trim().split('\n').filter(Boolean)
    .map(l => { try { return JSON.parse(l); } catch { return null; } })
    .filter(Boolean);
}

function buildKey(event) {
  if (event.outcome === 'success') return null;
  const pattern = event.error_pattern || 'generic_error';
  return `${event.tool}::${pattern.slice(0, 80)}`;
}

function classify(outcomes) {
  const groups = {};

  for (const ev of outcomes) {
    const key = buildKey(ev);
    if (!key) continue;

    if (!groups[key]) {
      groups[key] = {
        key,
        tool: ev.tool,
        error_pattern: ev.error_pattern || 'generic_error',
        occurrences: [],
        sessions: new Set(),
      };
    }
    groups[key].occurrences.push(ev);
    groups[key].sessions.add(ev.session);
  }

  // Filter to qualifying patterns
  const qualifying = Object.values(groups)
    .filter(g => g.occurrences.length >= RECURRENCE_MIN && g.sessions.size >= SESSION_MIN)
    .map(g => ({
      key: g.key,
      tool: g.tool,
      error_pattern: g.error_pattern,
      recurrence: g.occurrences.length,
      session_count: g.sessions.size,
      first_seen: g.occurrences[0].ts,
      last_seen: g.occurrences[g.occurrences.length - 1].ts,
      sample_inputs: g.occurrences.slice(-3).map(e => e.input_summary).filter(Boolean),
    }));

  return qualifying;
}

function main() {
  const outcomes = loadOutcomes();
  if (outcomes.length === 0) {
    process.stdout.write('no outcomes recorded yet');
    return;
  }

  const patterns = classify(outcomes);

  fs.writeFileSync(PATTERNS_FILE, JSON.stringify(patterns, null, 2), 'utf8');

  if (patterns.length === 0) {
    process.stdout.write(`analyzed ${outcomes.length} outcomes — no qualifying patterns`);
  } else {
    process.stdout.write(
      `found ${patterns.length} pattern(s) from ${outcomes.length} outcomes: ` +
      patterns.map(p => `${p.tool} (${p.recurrence}x)`).join(', ')
    );
  }
}

main();
