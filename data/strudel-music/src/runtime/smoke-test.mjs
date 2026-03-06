#!/usr/bin/env node
/**
 * Smoke test: verify Strudel loads, mini notation parses, samples exist.
 */
import { existsSync, readdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { createRequire } from 'module';

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = resolve(__dirname, '../..');
let passed = 0, failed = 0;

function check(name, ok) {
  if (ok) { console.log(`  ✅ ${name}`); passed++; }
  else { console.log(`  ❌ ${name}`); failed++; }
}

console.log('Strudel Music — Smoke Test\n');

// 1. Core imports
const core = await import('@strudel/core');
check('@strudel/core loaded', !!core.Pattern);

const mini = await import('@strudel/mini');
check('@strudel/mini loaded', !!mini.mini);

// 2. String parser registration
core.setStringParser(mini.mini);
const p = core.note('c3 e3 g3');
const haps = p.queryArc(0, 1);
check(`Mini notation parsing (got ${haps.length} haps, expected 3)`, haps.length === 3);

// 3. Tonal
try {
  await import('@strudel/tonal');
  check('@strudel/tonal loaded', true);
} catch {
  check('@strudel/tonal loaded', false);
}

// 4. node-web-audio-api
const require = createRequire(import.meta.url);
try {
  const nwa = require('node-web-audio-api');
  check('node-web-audio-api (OfflineAudioContext)', !!nwa.OfflineAudioContext);
} catch (e) {
  check(`node-web-audio-api: ${e.message}`, false);
}

// 5. Samples
const samplesDir = resolve(root, 'samples');
check('Samples directory exists', existsSync(samplesDir));
if (existsSync(samplesDir)) {
  const dirs = readdirSync(samplesDir).filter(d => {
    try { return readdirSync(resolve(samplesDir, d)).some(f => f.endsWith('.wav')); }
    catch { return false; }
  });
  check(`Sample sets loaded (${dirs.length} dirs, need ≥5)`, dirs.length >= 5);
  check('bd (bass drum) samples present', dirs.includes('bd'));
  check('sd (snare) samples present', dirs.includes('sd'));
  check('hh (hihat) samples present', dirs.includes('hh'));
}

// 6. Composition files
const compsDir = resolve(root, 'assets/compositions');
if (existsSync(compsDir)) {
  const comps = readdirSync(compsDir).filter(f => f.endsWith('.js'));
  check(`Compositions found (${comps.length} files, need ≥5)`, comps.length >= 5);
}

// 7. Discord voice deps (optional)
try {
  await import('@discordjs/voice');
  check('@discordjs/voice (VC streaming)', true);
} catch {
  check('@discordjs/voice (VC streaming, optional)', false);
}

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);
