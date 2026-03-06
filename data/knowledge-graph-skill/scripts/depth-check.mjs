#!/usr/bin/env node
/**
 * depth-check.mjs — KG Depth Heuristic Scorer
 *
 * Analyzes text content and recommends how many KG layers to extract.
 * For complex content (score ≥ 4), outputs a BASH SCRIPT TEMPLATE
 * with built-in validation checkpoints that enforce multi-pass extraction.
 *
 * Usage:
 *   node scripts/depth-check.mjs "article text or summary"
 *   echo "article text" | node scripts/depth-check.mjs
 *   node scripts/depth-check.mjs --file /path/to/article.txt
 *   node scripts/depth-check.mjs --json   # machine-readable output
 */

import { readFileSync } from 'fs';
import { createInterface } from 'readline';
import { loadConfig } from '../lib/config.mjs';

// ─── Detection Helpers ─────────────────────────────────────────────────────

function countNamedEntities(text) {
  const properNounPattern = /\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b/g;
  const matches = new Set(text.match(properNounPattern) || []);
  const stopWords = new Set(['The','In','On','At','By','For','With','From','To','A','An','And','Or','But','Is','Are','Was','Were','Has','Have','Had','This','That','These','Those','It','Its','As','If','Of','We','They','He','She','You','I','My','Our','Their','His','Her','Your']);
  for (const w of matches) stopWords.has(w) && matches.delete(w);
  return matches.size;
}

function detectTimeline(text) {
  const patterns = [
    /\b(20\d{2}|19\d{2})\b/g,
    /\bQ[1-4]\s+\d{4}\b/gi,
    /\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b/gi,
    /\b(before|after|then|next|subsequently|earlier|later|finally|first|second|third)\b/gi,
  ];
  let count = 0;
  for (const p of patterns) count += (text.match(p) || []).length;
  return count >= 3;
}

function detectCausalChains(text) {
  const causalWords = /\b(because|therefore|thus|hence|as a result|leads? to|causes?|triggers?|results? in|due to|consequently|which means|driven by|fueled by|cascades?|compounds?|amplifies?)\b/gi;
  return (text.match(causalWords) || []).length >= 3;
}

function detectDomains(text) {
  const domains = {
    technology: /\b(AI|ML|software|algorithm|model|neural|compute|API|cloud|SaaS|tech|code|agent|automation)\b/gi,
    finance: /\b(GDP|revenue|market|capital|debt|credit|investment|stock|bond|fund|equity|profit|loss|interest|fiscal|monetary|economy|financial|bank|insurance|annuity|default)\b/gi,
    social: /\b(society|social|cultural|community|protest|inequality|employment|labor|worker|people|public|demographic|population|household)\b/gi,
    policy: /\b(policy|regulation|law|government|federal|congress|act|bill|proposal|legislation|mandate|compliance|regulatory|authority|agency)\b/gi,
    science: /\b(research|study|data|analysis|experiment|paper|findings|evidence|hypothesis|theory|scientific|academic)\b/gi,
    geopolitics: /\b(country|nation|global|international|trade|tariff|sanctions|diplomatic|geopolitic|border|import|export|currency|rupee|dollar|yuan)\b/gi,
    health: /\b(health|medical|clinical|patient|hospital|drug|pharmaceutical|disease|therapy|treatment|mental)\b/gi,
  };
  let count = 0;
  for (const [, pattern] of Object.entries(domains)) {
    if ((text.match(pattern) || []).length >= 2) count++;
  }
  return count;
}

function detectPolicies(text) {
  return /\b(Act|Bill|Proposal|Plan|Program|Initiative|Framework|Strategy|Policy|Regulation|Reform)\b/g.test(text);
}

function detectStats(text) {
  const patterns = [/\d+\.?\d*\s*%/g, /\$\d[\d,.]*\s*(billion|million|trillion|B|M|T)?/gi, /\b\d{4,}[\d,.]*\b/g];
  let count = 0;
  for (const p of patterns) count += (text.match(p) || []).length;
  return count >= 4;
}

// ─── Scoring ───────────────────────────────────────────────────────────────

function score(text) {
  const namedEntities = countNamedEntities(text);
  const checks = {
    'named_entities':   { pass: namedEntities >= 5,  label: `≥5 named entities (found ~${namedEntities})` },
    'timeline':         { pass: detectTimeline(text),       label: 'Timeline or event sequence' },
    'causal_chains':    { pass: detectCausalChains(text),   label: 'Causal chains (A → B → C)' },
    'multi_domain':     { pass: detectDomains(text) >= 3,   label: `≥3 distinct domains (found ${detectDomains(text)})` },
    'policies':         { pass: detectPolicies(text),        label: 'Policy / proposals / institutional responses' },
    'statistics':       { pass: detectStats(text),           label: 'Quantitative data / statistics' },
    'multiple_actors':  { pass: namedEntities >= 8, label: `Multiple actors (found ~${namedEntities} named entities)` },
  };

  const total = Object.values(checks).filter(c => c.pass).length;

  let depth, template;
  if (total <= 1)      { depth = 1; template = 'Simple — 1 node with attrs.'; }
  else if (total <= 3) { depth = 2; template = 'Moderate — root + key concepts.'; }
  else if (total <= 5) { depth = 3; template = 'Rich — root → domains → mechanisms + cross-relations.'; }
  else                 { depth = 4; template = 'Complex — full extraction required.'; }

  return { score: total, depth, template, checks, namedEntities };
}

function qualityTargets(result, text) {
  if (result.score <= 3) return null;
  const cfg = loadConfig();
  const dc = cfg.depthCheck;
  const vc = cfg.validation;
  const nc = result.namedEntities;
  const datePatterns = [/\bQ[1-4]\s+\d{4}\b/gi, /\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b/gi, /\b(?:early|mid|late|end of)\s+\d{4}\b/gi];
  let dateCount = 0;
  for (const p of datePatterns) dateCount += (text.match(p) || []).length;
  const statPatterns = [/\d+\.?\d*\s*%/g, /\$\d[\d,.]*\s*(?:billion|million|trillion|B|M|T)?/gi];
  let statCount = 0;
  for (const p of statPatterns) statCount += (text.match(p) || []).length;
  const cappedNc = Math.min(nc, dc.entityCapForEstimate);
  const minEntities = Math.max(vc.minEntities, Math.round(cappedNc * dc.minEntitiesMultiplier));

  return {
    minEntities,
    maxEntities: minEntities + dc.extraEntities,
    minDepth: result.depth,
    minEvents: Math.max(3, Math.min(dateCount, 12)),
    minConcepts: Math.max(3, Math.round(result.score * 1.5)),
    minOrgsWithAttrs: Math.max(3, Math.round(cappedNc * 0.3)),
    minRelations: Math.max(10, Math.round(cappedNc * 0.5)),
    detectedDates: dateCount,
    detectedStats: statCount,
  };
}

// ─── Output ────────────────────────────────────────────────────────────────

function printResult(text, jsonMode) {
  const result = score(text);
  const qt = qualityTargets(result, text);

  if (jsonMode) {
    console.log(JSON.stringify({ ...result, qualityTargets: qt }, null, 2));
    return;
  }

  const bar = '█'.repeat(result.score) + '░'.repeat(7 - result.score);
  const depthLabel = ['', '🟢 Simple', '🟡 Moderate', '🟠 Rich', '🔴 Complex'][result.depth] || '🔴 Complex';

  console.log('');
  console.log(`  Score: [${bar}] ${result.score}/7 — ${depthLabel} — ${result.depth} layers`);
  console.log(`  Note: ${result.template}`);
  console.log('');

  // Signals
  for (const [, { pass, label }] of Object.entries(result.checks)) {
    console.log(`  ${pass ? '✓' : '✗'} ${label}`);
  }

  if (!qt) {
    // Simple content — just show basic instructions
    console.log('');
    console.log('  → Use add.mjs to create root node + a few concept children.');
    console.log('  → Run summarize.mjs after.');
    return;
  }

  // Complex content (score ≥ 4): show targets + BASH TEMPLATE
  console.log('');
  console.log('  ── Targets ──');
  console.log(`  Entities: ${qt.minEntities}–${qt.maxEntities} | Relations: ≥${qt.minRelations} | Depth: ≥${qt.minDepth}`);
  console.log(`  Events: ≥${qt.minEvents} | Orgs with attrs: ≥${qt.minOrgsWithAttrs} | Stats: ~${qt.detectedStats}`);
  console.log('');
  console.log('  ⛔ DO NOT finish with fewer than ' + qt.minEntities + ' entities.');
  console.log('');

  // THE KEY CHANGE: output a bash script template with built-in validation
  console.log('  ═══════════════════════════════════════════════════════');
  console.log('  HOW TO EXTRACT: Write a bash script with this structure:');
  console.log('  ═══════════════════════════════════════════════════════');
  console.log('');
  console.log('  Save the article text to /tmp/article.txt first, then write a script like:');
  console.log('');
  console.log('  ```bash');
  console.log('  #!/bin/bash');
  console.log('  set -e');
  console.log('  cd "$(dirname "$0")/.."  # or cd to workspace root');
  console.log('');
  console.log('  S=skills/knowledge-graph/scripts  # shorthand');
  console.log('');
  console.log('  # ── PHASE 1: Root + Domains ──');
  console.log('  node $S/add.mjs entity --id "ROOT_ID" --type "knowledge" --label "TITLE" --attrs \'{"url":"...","date":"..."}\'');
  console.log('  node $S/add.mjs entity --id "domain_X" --type "concept" --label "Domain X" --parent "ROOT_ID"');
  console.log('  # ... more domains ...');
  console.log('');
  console.log('  # ── PHASE 2: Mechanisms/sub-concepts UNDER domains ──');
  console.log('  node $S/add.mjs entity --id "mech_X" --type "concept" --label "Mechanism" --parent "domain_X" --attrs \'{"description":"..."}\'');
  console.log('  # ... more mechanisms/sub-themes ...');
  console.log('');
  console.log('  # ── PHASE 3: Orgs, People, Events UNDER mechanisms (depth ≥3!) ──');
  console.log('  # ⚠️ Orgs/events go under MECHANISMS, not directly under domains!');
  console.log('  #    root → domain → mechanism → org/event (this gives depth 3+)');
  console.log('  # ⚠️ Every org MUST have --attrs with role/stats. No empty shells!');
  console.log('  # ⚠️ Every event MUST have --attrs with date. No dateless events!');
  console.log('  node $S/add.mjs entity --id "org_X" --type "org" --label "OrgName" --parent "mech_X" --attrs \'{"role":"...","stats":"..."}\'');
  console.log('  node $S/add.mjs entity --id "event_X" --type "event" --label "Event" --parent "mech_X" --attrs \'{"date":"Q1 2027","details":"..."}\'');
  console.log('  node $S/add.mjs entity --id "human_X" --type "human" --label "Person" --attrs \'{"role":"..."}\'');
  console.log('  # ... ALL orgs, events, people from the article ...');
  console.log('');
  console.log('  # ── PHASE 4: Relations (≥1 per 2 entities) ──');
  console.log('  node $S/add.mjs rel --from "org_X" --to "org_Y" --rel "owns"');
  console.log('  node $S/add.mjs rel --from "event_X" --to "org_X" --rel "related_to"');
  console.log('  # ... ALL cross-links between entities ...');
  console.log('');
  console.log('  # ── PHASE 5: Validate (MANDATORY — do NOT skip) ──');
  console.log('  node $S/summarize.mjs');
  console.log('  echo ""');
  console.log('  echo "=== VALIDATION ==="');
  console.log('  node $S/validate-kg.mjs --file /tmp/article.txt --root "ROOT_ID" --fix');
  console.log('  ```');
  console.log('');
  console.log('  The validate-kg.mjs script will output ✅ PASS or ❌ FAIL.');
  console.log('  If FAIL: read the missing items, write ANOTHER script to add them, then validate again.');
  console.log('  Keep going until you get ✅ PASS.');
  console.log('');
}

// ─── Main ──────────────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  const jsonMode = args.includes('--json');
  const fileIdx = args.indexOf('--file');

  let text = '';
  if (fileIdx !== -1 && args[fileIdx + 1]) {
    text = readFileSync(args[fileIdx + 1], 'utf8');
  } else {
    const inlineArgs = args.filter(a => !a.startsWith('--'));
    if (inlineArgs.length > 0) {
      text = inlineArgs.join(' ');
    } else if (!process.stdin.isTTY) {
      const rl = createInterface({ input: process.stdin });
      const lines = [];
      for await (const line of rl) lines.push(line);
      text = lines.join('\n');
    } else {
      console.error('Usage: node scripts/depth-check.mjs "text" | --file path | stdin pipe');
      process.exit(1);
    }
  }

  if (!text.trim()) { console.error('Error: empty input'); process.exit(1); }
  printResult(text, jsonMode);
}

main().catch(e => { console.error(e.message); process.exit(1); });
