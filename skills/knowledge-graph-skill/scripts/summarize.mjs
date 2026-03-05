#!/usr/bin/env node
// summarize.mjs — Regenerate kg-summary.md (frequency-ranked, budget-capped)
// Does NOT modify AGENTS.md/CLAUDE.md/GEMINI.md — keeps them cache-friendly.

import { writeFileSync, realpathSync } from 'fs';
import { join, dirname, resolve } from 'path';
import { fileURLToPath } from 'url';
import { toKGMLAsync } from '../lib/serialize.mjs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SKILL_DIR = realpathSync(resolve(join(__dirname, '..')));
const SUMMARY_PATH = join(SKILL_DIR, 'data', 'kg-summary.md');

try {
  const kgml = await toKGMLAsync();
  writeFileSync(SUMMARY_PATH, kgml);
  const lines = kgml.split('\n').filter(l => l.trim()).length;
  console.log(`✅ Summary regenerated: ${SUMMARY_PATH} (${lines} lines)`);
} catch (e) {
  console.error('❌', e.message);
  process.exit(1);
}
