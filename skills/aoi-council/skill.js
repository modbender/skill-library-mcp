#!/usr/bin/env node
/**
 * AOI Council (public-safe)
 * S-DNA: AOI-2026-0215-SDNA-CNSL01
 */

import fs from 'node:fs';
import path from 'node:path';

const __sdna__ = {
  protocol: 'aoineco-sdna-v1',
  id: 'AOI-2026-0215-SDNA-CNSL01',
  org: 'aoineco-co',
  classification: 'public-safe',
};

function listAgents(dir) {
  const full = path.resolve(dir);
  if (!fs.existsSync(full)) return [];
  return fs
    .readdirSync(full)
    .filter((f) => f.toLowerCase().endsWith('.md'))
    .map((f) => ({ name: f.replace(/\.md$/i, ''), file: path.join('agents', f) }));
}

function main() {
  const baseDir = path.dirname(new URL(import.meta.url).pathname);
  const agents = listAgents(path.join(baseDir, 'agents'));
  const template = `Analyze the topic below from multiple perspectives.\n\n` +
`Return:\n1) **Synthesis (TL;DR)**\n2) Per perspective: insights / concerns / recommendations\n3) Open questions + next actions\n\n` +
`Use these perspective files (relative):\n` + agents.map(a => `- ${a.file}`).join('\n');

  console.log(JSON.stringify({ __sdna__, agents, council_template: template }, null, 2));
}

main();
