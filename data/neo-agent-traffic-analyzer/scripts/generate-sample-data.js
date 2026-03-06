#!/usr/bin/env node
'use strict';

/**
 * Generates sample agent communication data for testing and demonstration.
 * Usage: node scripts/generate-sample-data.js [count] [agents]
 *   count  - Number of messages to generate (default: 100)
 *   agents - Comma-separated list of agent names
 */

const fs = require('fs');
const path = require('path');

const count = parseInt(process.argv[2], 10) || 100;
const agentInput = process.argv[3];
const agents = agentInput
  ? agentInput.split(',').map((a) => a.trim())
  : ['agent-alpha', 'agent-beta', 'agent-gamma', 'agent-delta'];

const types = ['request', 'response', 'broadcast'];
const statuses = ['delivered', 'delivered', 'delivered', 'delivered', 'failed', 'timeout'];

const messages = [];
const baseTime = new Date('2026-02-01T08:00:00Z').getTime();

for (let i = 0; i < count; i++) {
  let from = agents[Math.floor(Math.random() * agents.length)];
  let to = agents[Math.floor(Math.random() * agents.length)];
  while (to === from && agents.length > 1) {
    to = agents[Math.floor(Math.random() * agents.length)];
  }

  messages.push({
    id: `msg-${String(i + 1).padStart(4, '0')}`,
    from,
    to,
    timestamp: new Date(baseTime + i * 1000).toISOString(),
    type: types[Math.floor(Math.random() * types.length)],
    payload_size: Math.floor(Math.random() * 8192),
    latency_ms: Math.floor(Math.random() * 300) + 5,
    status: statuses[Math.floor(Math.random() * statuses.length)],
  });
}

const output = JSON.stringify(messages, null, 2);

if (process.argv[4]) {
  const outPath = path.resolve(process.argv[4]);
  fs.writeFileSync(outPath, output, 'utf8');
  console.log(`Generated ${count} messages to ${outPath}`);
} else {
  console.log(output);
}
