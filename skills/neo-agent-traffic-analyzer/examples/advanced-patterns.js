#!/usr/bin/env node
'use strict';

/**
 * Advanced example: Analyze complex multi-agent communication patterns,
 * generate multiple output formats, and compare optimization suggestions.
 *
 * Run: node examples/advanced-patterns.js
 */

const path = require('path');
const { Analyzer } = require('../lib/analyzer');
const { Visualizer } = require('../lib/visualizer');
const { Reporter } = require('../lib/reporter');

// Complex communication scenario with 5 agents
const messages = [];
const agents = ['gateway', 'auth-service', 'data-processor', 'cache-layer', 'storage'];
const types = ['request', 'response', 'broadcast'];
const statuses = ['delivered', 'delivered', 'delivered', 'delivered', 'failed', 'timeout'];

// Generate 200 realistic messages
let msgId = 0;
const baseTime = new Date('2026-02-01T08:00:00Z').getTime();

for (let i = 0; i < 200; i++) {
  const from = agents[Math.floor(Math.random() * agents.length)];
  let to = agents[Math.floor(Math.random() * agents.length)];
  while (to === from) {
    to = agents[Math.floor(Math.random() * agents.length)];
  }

  // Make gateway a bottleneck (high traffic hub)
  const useGateway = Math.random() < 0.4;
  const actualFrom = useGateway ? 'gateway' : from;
  const actualTo = useGateway && from === 'gateway' ? to : to;

  // Make data-processor slow
  const isSlowEdge = actualTo === 'data-processor';
  const latency = isSlowEdge
    ? 80 + Math.floor(Math.random() * 200)
    : 10 + Math.floor(Math.random() * 60);

  messages.push({
    id: `msg-${String(++msgId).padStart(4, '0')}`,
    from: actualFrom,
    to: actualTo,
    timestamp: new Date(baseTime + i * 500).toISOString(),
    type: types[Math.floor(Math.random() * types.length)],
    payload_size: Math.floor(Math.random() * 8192),
    latency_ms: latency,
    status: statuses[Math.floor(Math.random() * statuses.length)],
  });
}

console.log(`Generated ${messages.length} messages across ${agents.length} agents\n`);

// Analyze
const analyzer = new Analyzer(messages);
const visualizer = new Visualizer(analyzer);
const reporter = new Reporter(analyzer, visualizer);

// Full text report
console.log(reporter.generateTextSummary());

// Timeline (first 10 messages)
console.log('--- Timeline (excerpt) ---');
const timeline = visualizer.generateTimeline({ width: 100 });
const timelineLines = timeline.split('\n');
console.log(timelineLines.slice(0, 15).join('\n'));
console.log(`  ... (${timelineLines.length - 15} more lines)`);
console.log('');

// DOT graph preview
console.log('--- DOT Graph (first 10 lines) ---');
const dot = visualizer.generateDot({ title: 'Advanced Pattern Analysis' });
console.log(dot.split('\n').slice(0, 10).join('\n'));
console.log('  ...');
console.log('');

// JSON report summary
console.log('--- JSON Report Structure ---');
const jsonReport = JSON.parse(reporter.generateJSON());
console.log(`  Summary keys: ${Object.keys(jsonReport.summary).join(', ')}`);
console.log(`  Agents analyzed: ${Object.keys(jsonReport.agents).length}`);
console.log(`  Edges analyzed: ${Object.keys(jsonReport.edges).length}`);
console.log(`  Bottlenecks found: ${jsonReport.bottlenecks.length}`);
console.log(`  Optimizations suggested: ${jsonReport.optimizations.length}`);
