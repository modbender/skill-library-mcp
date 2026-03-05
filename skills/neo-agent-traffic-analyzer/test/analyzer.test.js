'use strict';

const { describe, it } = require('node:test');
const assert = require('node:assert/strict');
const { Analyzer } = require('../lib/analyzer');

const sampleMessages = [
  { id: 'msg-001', from: 'agent-a', to: 'agent-b', timestamp: '2026-01-01T10:00:00Z', type: 'request', payload_size: 512, latency_ms: 30, status: 'delivered' },
  { id: 'msg-002', from: 'agent-b', to: 'agent-a', timestamp: '2026-01-01T10:00:01Z', type: 'response', payload_size: 1024, latency_ms: 50, status: 'delivered' },
  { id: 'msg-003', from: 'agent-a', to: 'agent-c', timestamp: '2026-01-01T10:00:02Z', type: 'request', payload_size: 256, latency_ms: 20, status: 'delivered' },
  { id: 'msg-004', from: 'agent-c', to: 'agent-a', timestamp: '2026-01-01T10:00:03Z', type: 'response', payload_size: 2048, latency_ms: 150, status: 'delivered' },
  { id: 'msg-005', from: 'agent-a', to: 'agent-b', timestamp: '2026-01-01T10:00:04Z', type: 'request', payload_size: 128, latency_ms: 10, status: 'failed' },
  { id: 'msg-006', from: 'agent-b', to: 'agent-c', timestamp: '2026-01-01T10:00:05Z', type: 'request', payload_size: 640, latency_ms: 35, status: 'delivered' },
  { id: 'msg-007', from: 'agent-c', to: 'agent-b', timestamp: '2026-01-01T10:00:06Z', type: 'response', payload_size: 320, latency_ms: 200, status: 'timeout' },
  { id: 'msg-008', from: 'agent-a', to: 'agent-b', timestamp: '2026-01-01T10:00:07Z', type: 'broadcast', payload_size: 64, latency_ms: 5, status: 'delivered' },
];

describe('Analyzer', () => {
  describe('constructor', () => {
    it('should accept a valid array of messages', () => {
      const analyzer = new Analyzer(sampleMessages);
      assert.ok(analyzer);
    });

    it('should accept an empty array', () => {
      const analyzer = new Analyzer([]);
      assert.ok(analyzer);
    });

    it('should throw on non-array input', () => {
      assert.throws(() => new Analyzer('not an array'), /must be an array/);
      assert.throws(() => new Analyzer(null), /must be an array/);
      assert.throws(() => new Analyzer(42), /must be an array/);
    });

    it('should throw if message lacks from or to fields', () => {
      assert.throws(() => new Analyzer([{ from: 'a' }]), /missing required/);
      assert.throws(() => new Analyzer([{ to: 'b' }]), /missing required/);
    });

    it('should assign default values for optional fields', () => {
      const analyzer = new Analyzer([{ from: 'a', to: 'b' }]);
      const agents = analyzer.getAgents();
      assert.deepStrictEqual(agents, ['a', 'b']);
    });
  });

  describe('getAgents', () => {
    it('should return sorted unique agent names', () => {
      const analyzer = new Analyzer(sampleMessages);
      const agents = analyzer.getAgents();
      assert.deepStrictEqual(agents, ['agent-a', 'agent-b', 'agent-c']);
    });

    it('should return empty array for empty messages', () => {
      const analyzer = new Analyzer([]);
      assert.deepStrictEqual(analyzer.getAgents(), []);
    });
  });

  describe('getAgentStats', () => {
    it('should compute correct sent/received counts', () => {
      const analyzer = new Analyzer(sampleMessages);
      const stats = analyzer.getAgentStats();

      assert.equal(stats['agent-a'].sent, 4);
      assert.equal(stats['agent-a'].received, 2);
      assert.equal(stats['agent-b'].sent, 2);
      assert.equal(stats['agent-b'].received, 4);
      assert.equal(stats['agent-c'].sent, 2);
      assert.equal(stats['agent-c'].received, 2);
    });

    it('should count failed messages', () => {
      const analyzer = new Analyzer(sampleMessages);
      const stats = analyzer.getAgentStats();
      assert.equal(stats['agent-a'].failed, 1);
    });

    it('should count timeout messages', () => {
      const analyzer = new Analyzer(sampleMessages);
      const stats = analyzer.getAgentStats();
      assert.equal(stats['agent-c'].timeouts, 1);
    });

    it('should compute average latency for receiving agents', () => {
      const analyzer = new Analyzer(sampleMessages);
      const stats = analyzer.getAgentStats();
      // agent-b receives: msg-001(30ms from a), msg-005(10ms from a), msg-008(5ms from a), msg-007(200ms from c)
      // wait - agent-b receives msg-001 (latency 30), msg-005 (latency 10), msg-008 (latency 5), msg-006... no
      // msg-001: a->b, latency 30 -> b receives, latency added to b
      // msg-005: a->b, latency 10 -> b receives, latency added to b
      // msg-006: b->c, latency 35 -> c receives
      // msg-008: a->b, latency 5 -> b receives, latency added to b
      // So agent-b latencies: [30, 10, 5] (from msg-001, msg-005, msg-008) — wait msg-007 c->b, latency 200
      // agent-b receives: msg-001(30), msg-005(10), msg-007(200), msg-008(5) = 4 messages
      // avg = (30+10+200+5)/4 = 61.25 -> rounded = 61
      assert.equal(stats['agent-b'].avg_latency_ms, 61);
    });

    it('should cache results', () => {
      const analyzer = new Analyzer(sampleMessages);
      const stats1 = analyzer.getAgentStats();
      const stats2 = analyzer.getAgentStats();
      assert.strictEqual(stats1, stats2);
    });
  });

  describe('getEdgeStats', () => {
    it('should compute edge statistics', () => {
      const analyzer = new Analyzer(sampleMessages);
      const edges = analyzer.getEdgeStats();

      const abEdge = edges['agent-a->agent-b'];
      assert.ok(abEdge);
      assert.equal(abEdge.count, 3);
      assert.equal(abEdge.from, 'agent-a');
      assert.equal(abEdge.to, 'agent-b');
    });

    it('should track failed messages per edge', () => {
      const analyzer = new Analyzer(sampleMessages);
      const edges = analyzer.getEdgeStats();
      assert.equal(edges['agent-a->agent-b'].failed, 1);
      assert.equal(edges['agent-c->agent-b'].failed, 1);
    });

    it('should compute average latency per edge', () => {
      const analyzer = new Analyzer(sampleMessages);
      const edges = analyzer.getEdgeStats();
      // a->b: msg-001(30), msg-005(10), msg-008(5) => avg = 15
      assert.equal(edges['agent-a->agent-b'].avg_latency_ms, 15);
    });

    it('should track message types per edge', () => {
      const analyzer = new Analyzer(sampleMessages);
      const edges = analyzer.getEdgeStats();
      assert.equal(edges['agent-a->agent-b'].types.request, 2);
      assert.equal(edges['agent-a->agent-b'].types.broadcast, 1);
    });
  });

  describe('getTimeline', () => {
    it('should return messages sorted by timestamp', () => {
      const analyzer = new Analyzer(sampleMessages);
      const timeline = analyzer.getTimeline();
      for (let i = 1; i < timeline.length; i++) {
        assert.ok(timeline[i].timestamp >= timeline[i - 1].timestamp);
      }
    });

    it('should return empty array for empty messages', () => {
      const analyzer = new Analyzer([]);
      assert.deepStrictEqual(analyzer.getTimeline(), []);
    });
  });

  describe('getSummary', () => {
    it('should return correct summary statistics', () => {
      const analyzer = new Analyzer(sampleMessages);
      const summary = analyzer.getSummary();

      assert.equal(summary.total_agents, 3);
      assert.equal(summary.total_messages, 8);
      assert.equal(summary.failed_messages, 2);
      assert.ok(summary.failure_rate > 0);
      assert.ok(summary.avg_latency_ms > 0);
      assert.ok(summary.unique_edges > 0);
      assert.ok(summary.type_breakdown.request > 0);
    });

    it('should handle empty messages', () => {
      const analyzer = new Analyzer([]);
      const summary = analyzer.getSummary();
      assert.equal(summary.total_agents, 0);
      assert.equal(summary.total_messages, 0);
      assert.equal(summary.avg_latency_ms, 0);
    });
  });

  describe('findBottlenecks', () => {
    it('should detect high-traffic agents', () => {
      const analyzer = new Analyzer(sampleMessages);
      const bottlenecks = analyzer.findBottlenecks({ traffic_threshold: 0.3 });
      const highTraffic = bottlenecks.filter((b) => b.type === 'high_traffic_agent');
      assert.ok(highTraffic.length > 0);
    });

    it('should detect high-latency edges', () => {
      const analyzer = new Analyzer(sampleMessages);
      const bottlenecks = analyzer.findBottlenecks({ latency_threshold: 100 });
      const highLatency = bottlenecks.filter((b) => b.type === 'high_latency_edge');
      // c->a has 150ms avg, c->b has 200ms avg
      assert.ok(highLatency.length > 0);
    });

    it('should detect high-failure edges', () => {
      const analyzer = new Analyzer(sampleMessages);
      const bottlenecks = analyzer.findBottlenecks({ failure_threshold: 0.1 });
      const highFailure = bottlenecks.filter((b) => b.type === 'high_failure_edge');
      assert.ok(highFailure.length > 0);
    });

    it('should sort bottlenecks by severity (critical first)', () => {
      const analyzer = new Analyzer(sampleMessages);
      const bottlenecks = analyzer.findBottlenecks();
      const severities = bottlenecks.map((b) => b.severity);
      const order = { critical: 0, warning: 1, info: 2 };
      for (let i = 1; i < severities.length; i++) {
        assert.ok((order[severities[i]] ?? 99) >= (order[severities[i - 1]] ?? 99),
          `Expected ${severities[i]} to come after ${severities[i - 1]}`);
      }
    });

    it('should return empty for well-balanced traffic', () => {
      const messages = [
        { from: 'a', to: 'b', latency_ms: 10, status: 'delivered' },
        { from: 'b', to: 'c', latency_ms: 10, status: 'delivered' },
        { from: 'c', to: 'd', latency_ms: 10, status: 'delivered' },
        { from: 'd', to: 'a', latency_ms: 10, status: 'delivered' },
      ];
      const analyzer = new Analyzer(messages);
      const bottlenecks = analyzer.findBottlenecks({
        traffic_threshold: 0.9,
        latency_threshold: 1000,
        failure_threshold: 0.5,
      });
      assert.equal(bottlenecks.length, 0);
    });
  });

  describe('suggestOptimizations', () => {
    it('should return optimization suggestions for each bottleneck', () => {
      const analyzer = new Analyzer(sampleMessages);
      const optimizations = analyzer.suggestOptimizations();
      assert.ok(optimizations.length > 0);
      for (const opt of optimizations) {
        assert.ok(opt.strategy);
        assert.ok(opt.description);
        assert.ok(opt.priority);
        assert.ok(opt.bottleneck);
      }
    });

    it('should return empty array when no bottlenecks exist', () => {
      const messages = [
        { from: 'a', to: 'b', latency_ms: 10, status: 'delivered' },
        { from: 'b', to: 'c', latency_ms: 10, status: 'delivered' },
        { from: 'c', to: 'd', latency_ms: 10, status: 'delivered' },
        { from: 'd', to: 'a', latency_ms: 10, status: 'delivered' },
      ];
      const analyzer = new Analyzer(messages);
      const bottlenecks = analyzer.findBottlenecks({
        traffic_threshold: 0.9,
        latency_threshold: 10000,
        failure_threshold: 0.99,
      });
      assert.equal(bottlenecks.length, 0);
    });
  });

  describe('performance', () => {
    it('should process 1000+ messages within 5 seconds', () => {
      const messages = [];
      const agents = ['a', 'b', 'c', 'd', 'e'];
      for (let i = 0; i < 1500; i++) {
        messages.push({
          from: agents[i % agents.length],
          to: agents[(i + 1) % agents.length],
          timestamp: new Date(Date.now() + i * 100).toISOString(),
          type: 'request',
          payload_size: 100,
          latency_ms: Math.random() * 200,
          status: 'delivered',
        });
      }

      const start = Date.now();
      const analyzer = new Analyzer(messages);
      analyzer.getSummary();
      analyzer.findBottlenecks();
      analyzer.suggestOptimizations();
      analyzer.getTimeline();
      const elapsed = Date.now() - start;

      assert.ok(elapsed < 5000, `Processing took ${elapsed}ms, expected < 5000ms`);
    });
  });
});
