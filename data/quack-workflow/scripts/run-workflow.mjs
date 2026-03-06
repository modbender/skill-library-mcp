#!/usr/bin/env node

/**
 * Workflow Engine — Run multi-step workflows via Orchestrate
 * Usage: node run-workflow.mjs --file workflow.yaml
 */

import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { parseArgs } from 'node:util';

const { values: args } = parseArgs({
  options: {
    file: { type: 'string', short: 'f' },
    dry:  { type: 'boolean', default: false },
  },
  strict: false,
});

if (!args.file) {
  console.error('Usage: node run-workflow.mjs --file workflow.yaml');
  process.exit(1);
}

const workflowPath = resolve(args.file);
const content = await readFile(workflowPath, 'utf8');

// Simple YAML-like parser for workflow files
const lines = content.split('\n');
console.log(`Loaded workflow from ${args.file}`);
console.log(`Content length: ${content.length} bytes`);

if (args.dry) {
  console.log('Dry run — workflow parsed but not executed.');
  console.log(content);
  process.exit(0);
}

const BASE_URL = 'https://orchestrate.us.com';

const res = await fetch(`${BASE_URL}/api/v1/workflows/run`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/yaml' },
  body: content,
});

if (!res.ok) {
  console.error(`Error ${res.status}: ${await res.text()}`);
  process.exit(1);
}

const data = await res.json();
console.log(JSON.stringify(data, null, 2));
