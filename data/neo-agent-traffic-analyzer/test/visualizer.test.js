'use strict';

const { describe, it } = require('node:test');
const assert = require('node:assert/strict');
const { Analyzer } = require('../lib/analyzer');
const { Visualizer } = require('../lib/visualizer');
const { Reporter } = require('../lib/reporter');

const sampleMessages = [
  { id: 'msg-001', from: 'alpha', to: 'beta', timestamp: '2026-01-01T10:00:00Z', type: 'request', payload_size: 512, latency_ms: 30, status: 'delivered' },
  { id: 'msg-002', from: 'beta', to: 'alpha', timestamp: '2026-01-01T10:00:01Z', type: 'response', payload_size: 1024, latency_ms: 50, status: 'delivered' },
  { id: 'msg-003', from: 'alpha', to: 'gamma', timestamp: '2026-01-01T10:00:02Z', type: 'request', payload_size: 256, latency_ms: 20, status: 'delivered' },
  { id: 'msg-004', from: 'gamma', to: 'beta', timestamp: '2026-01-01T10:00:03Z', type: 'response', payload_size: 640, latency_ms: 120, status: 'failed' },
];

describe('Visualizer', () => {
  describe('generateDot', () => {
    it('should produce valid DOT format output', () => {
      const analyzer = new Analyzer(sampleMessages);
      const vis = new Visualizer(analyzer);
      const dot = vis.generateDot();

      assert.ok(dot.startsWith('digraph AgentNetwork {'));
      assert.ok(dot.endsWith('}'));
      assert.ok(dot.includes('->'));
    });

    it('should include all agents as nodes', () => {
      const analyzer = new Analyzer(sampleMessages);
      const vis = new Visualizer(analyzer);
      const dot = vis.generateDot();

      assert.ok(dot.includes('"alpha"'));
      assert.ok(dot.includes('"beta"'));
      assert.ok(dot.includes('"gamma"'));
    });

    it('should include all edges', () => {
      const analyzer = new Analyzer(sampleMessages);
      const vis = new Visualizer(analyzer);
      const dot = vis.generateDot();

      assert.ok(dot.includes('"alpha" -> "beta"'));
      assert.ok(dot.includes('"beta" -> "alpha"'));
      assert.ok(dot.includes('"alpha" -> "gamma"'));
      assert.ok(dot.includes('"gamma" -> "beta"'));
    });

    it('should support custom title', () => {
      const analyzer = new Analyzer(sampleMessages);
      const vis = new Visualizer(analyzer);
      const dot = vis.generateDot({ title: 'My Custom Title' });
      assert.ok(dot.includes('My Custom Title'));
    });

    it('should color high-latency edges red', () => {
      const analyzer = new Analyzer(sampleMessages);
      const vis = new Visualizer(analyzer);
      const dot = vis.generateDot();
      assert.ok(dot.includes('#cc0000'));
    });
  });

  describe('generateTimeline', () => {
    it('should produce timeline output', () => {
      const analyzer = new Analyzer(sampleMessages);
      const vis = new Visualizer(analyzer);
      const timeline = vis.generateTimeline();

      assert.ok(timeline.includes('Timeline'));
      assert.ok(timeline.includes('alpha'));
      assert.ok(timeline.includes('beta'));
    });

    it('should handle empty messages', () => {
      const analyzer = new Analyzer([]);
      const vis = new Visualizer(analyzer);
      const timeline = vis.generateTimeline();
      assert.ok(timeline.includes('No messages'));
    });

    it('should include legend', () => {
      const analyzer = new Analyzer(sampleMessages);
      const vis = new Visualizer(analyzer);
      const timeline = vis.generateTimeline();
      assert.ok(timeline.includes('Legend'));
    });
  });

  describe('generateAsciiNetwork', () => {
    it('should show all agents', () => {
      const analyzer = new Analyzer(sampleMessages);
      const vis = new Visualizer(analyzer);
      const ascii = vis.generateAsciiNetwork();

      assert.ok(ascii.includes('[alpha]'));
      assert.ok(ascii.includes('[beta]'));
      assert.ok(ascii.includes('[gamma]'));
    });

    it('should show connections', () => {
      const analyzer = new Analyzer(sampleMessages);
      const vis = new Visualizer(analyzer);
      const ascii = vis.generateAsciiNetwork();

      assert.ok(ascii.includes('beta:'));
      assert.ok(ascii.includes('msgs'));
    });

    it('should handle empty messages', () => {
      const analyzer = new Analyzer([]);
      const vis = new Visualizer(analyzer);
      const ascii = vis.generateAsciiNetwork();
      assert.ok(ascii.includes('No agents'));
    });

    it('should show failed message counts', () => {
      const analyzer = new Analyzer(sampleMessages);
      const vis = new Visualizer(analyzer);
      const ascii = vis.generateAsciiNetwork();
      assert.ok(ascii.includes('failed'));
    });
  });

  describe('generateNetworkDotFromTemplate', () => {
    it('should produce valid DOT output from template', () => {
      const analyzer = new Analyzer(sampleMessages);
      const vis = new Visualizer(analyzer);
      const dot = vis.generateNetworkDotFromTemplate();

      assert.ok(dot.includes('digraph'));
      assert.ok(dot.includes('alpha'));
    });
  });
});

describe('Reporter', () => {
  describe('generateJSON', () => {
    it('should produce valid JSON', () => {
      const analyzer = new Analyzer(sampleMessages);
      const vis = new Visualizer(analyzer);
      const reporter = new Reporter(analyzer, vis);
      const json = reporter.generateJSON();

      const parsed = JSON.parse(json);
      assert.ok(parsed.summary);
      assert.ok(parsed.agents);
      assert.ok(parsed.edges);
      assert.ok(parsed.bottlenecks);
      assert.ok(parsed.optimizations);
    });
  });

  describe('generateCSV', () => {
    it('should produce CSV output with sections', () => {
      const analyzer = new Analyzer(sampleMessages);
      const vis = new Visualizer(analyzer);
      const reporter = new Reporter(analyzer, vis);
      const csv = reporter.generateCSV();

      assert.ok(csv.includes('## Agent Statistics'));
      assert.ok(csv.includes('## Edge Statistics'));
      assert.ok(csv.includes('## Bottlenecks'));
      assert.ok(csv.includes('alpha'));
    });
  });

  describe('generateReport', () => {
    it('should generate report in different formats', () => {
      const analyzer = new Analyzer(sampleMessages);
      const vis = new Visualizer(analyzer);
      const reporter = new Reporter(analyzer, vis);

      const json = reporter.generateReport('json');
      assert.ok(JSON.parse(json));

      const csv = reporter.generateReport('csv');
      assert.ok(csv.includes('agent'));

      const dot = reporter.generateReport('dot');
      assert.ok(dot.includes('digraph'));
    });

    it('should throw for unsupported format', () => {
      const analyzer = new Analyzer(sampleMessages);
      const vis = new Visualizer(analyzer);
      const reporter = new Reporter(analyzer, vis);

      assert.throws(() => reporter.generateReport('xml'), /Unsupported format/);
    });
  });

  describe('generateTextSummary', () => {
    it('should produce human-readable text', () => {
      const analyzer = new Analyzer(sampleMessages);
      const vis = new Visualizer(analyzer);
      const reporter = new Reporter(analyzer, vis);
      const text = reporter.generateTextSummary();

      assert.ok(text.includes('Agent Traffic Analysis Report'));
      assert.ok(text.includes('Summary'));
      assert.ok(text.includes('Agents:'));
      assert.ok(text.includes('Total Messages:'));
    });
  });

  describe('exportToFile', () => {
    it('should write file to disk', () => {
      const fs = require('fs');
      const path = require('path');
      const tmpFile = path.join(__dirname, '..', 'test-output-tmp.json');

      const analyzer = new Analyzer(sampleMessages);
      const vis = new Visualizer(analyzer);
      const reporter = new Reporter(analyzer, vis);

      reporter.exportToFile(tmpFile, 'json');
      assert.ok(fs.existsSync(tmpFile));

      const content = JSON.parse(fs.readFileSync(tmpFile, 'utf8'));
      assert.ok(content.summary);

      // Cleanup
      fs.unlinkSync(tmpFile);
    });
  });
});
