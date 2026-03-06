#!/usr/bin/env node
const path = require('path');
const { decide } = require('./decide');

const command = process.argv.slice(2).join(' ').trim();
if (!command) {
  console.error('Usage: node skills/openclaw/guardrails/src/cli.js "<command>"');
  process.exit(1);
}

const policyPath = path.resolve(__dirname, '..', 'policy.baseline.json');
const output = decide({ command }, policyPath);
console.log(JSON.stringify(output, null, 2));
