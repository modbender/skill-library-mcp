#!/usr/bin/env node
'use strict';

/**
 * Basic usage example: Analyze a set of agent communication messages
 * and display summary statistics with bottleneck detection.
 *
 * Run: node examples/basic-analysis.js
 */

const { Analyzer } = require('../lib/analyzer');
const { Visualizer } = require('../lib/visualizer');
const { Reporter } = require('../lib/reporter');

// Sample communication log between three agents
const messages = [
  { id: 'msg-001', from: 'coordinator', to: 'worker-1', timestamp: '2026-01-15T10:00:00Z', type: 'request', payload_size: 512, latency_ms: 25, status: 'delivered' },
  { id: 'msg-002', from: 'coordinator', to: 'worker-2', timestamp: '2026-01-15T10:00:01Z', type: 'request', payload_size: 480, latency_ms: 30, status: 'delivered' },
  { id: 'msg-003', from: 'worker-1', to: 'coordinator', timestamp: '2026-01-15T10:00:02Z', type: 'response', payload_size: 2048, latency_ms: 150, status: 'delivered' },
  { id: 'msg-004', from: 'worker-2', to: 'coordinator', timestamp: '2026-01-15T10:00:03Z', type: 'response', payload_size: 1800, latency_ms: 45, status: 'delivered' },
  { id: 'msg-005', from: 'coordinator', to: 'worker-1', timestamp: '2026-01-15T10:00:04Z', type: 'request', payload_size: 256, latency_ms: 20, status: 'delivered' },
  { id: 'msg-006', from: 'worker-1', to: 'coordinator', timestamp: '2026-01-15T10:00:05Z', type: 'response', payload_size: 4096, latency_ms: 200, status: 'delivered' },
  { id: 'msg-007', from: 'coordinator', to: 'worker-2', timestamp: '2026-01-15T10:00:06Z', type: 'request', payload_size: 128, latency_ms: 15, status: 'timeout' },
];

// Create analyzer and process messages
const analyzer = new Analyzer(messages);
const visualizer = new Visualizer(analyzer);
const reporter = new Reporter(analyzer, visualizer);

// Display the full text report
console.log(reporter.generateTextSummary());

// Show ASCII network topology
console.log(visualizer.generateAsciiNetwork());
