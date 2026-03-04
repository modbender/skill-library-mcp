'use strict';

/**
 * Core analysis engine for OpenClaw agent communication patterns.
 * Processes message logs to extract flow patterns, detect bottlenecks,
 * and compute network statistics.
 */

class Analyzer {
  constructor(messages = []) {
    this.messages = this._validate(messages);
    this._agentStats = null;
    this._edgeStats = null;
    this._bottlenecks = null;
  }

  _validate(messages) {
    if (!Array.isArray(messages)) {
      throw new Error('Messages must be an array');
    }
    return messages.map((msg, i) => {
      if (!msg.from || !msg.to) {
        throw new Error(`Message at index ${i} missing required "from" or "to" field`);
      }
      return {
        id: msg.id || `msg-${i}`,
        from: String(msg.from),
        to: String(msg.to),
        timestamp: msg.timestamp ? new Date(msg.timestamp) : new Date(),
        type: msg.type || 'request',
        payload_size: Number(msg.payload_size) || 0,
        latency_ms: Number(msg.latency_ms) || 0,
        status: msg.status || 'delivered',
      };
    });
  }

  getAgents() {
    const agents = new Set();
    for (const msg of this.messages) {
      agents.add(msg.from);
      agents.add(msg.to);
    }
    return Array.from(agents).sort();
  }

  getAgentStats() {
    if (this._agentStats) return this._agentStats;

    const stats = {};

    const ensureAgent = (name) => {
      if (!stats[name]) {
        stats[name] = {
          name,
          sent: 0,
          received: 0,
          total: 0,
          sent_bytes: 0,
          received_bytes: 0,
          avg_latency_ms: 0,
          failed: 0,
          timeouts: 0,
          _latencies: [],
        };
      }
    };

    for (const msg of this.messages) {
      ensureAgent(msg.from);
      ensureAgent(msg.to);

      stats[msg.from].sent++;
      stats[msg.from].total++;
      stats[msg.from].sent_bytes += msg.payload_size;

      stats[msg.to].received++;
      stats[msg.to].total++;
      stats[msg.to].received_bytes += msg.payload_size;

      if (msg.latency_ms > 0) {
        stats[msg.to]._latencies.push(msg.latency_ms);
      }

      if (msg.status === 'failed') {
        stats[msg.from].failed++;
      }
      if (msg.status === 'timeout') {
        stats[msg.from].timeouts++;
      }
    }

    for (const agent of Object.values(stats)) {
      if (agent._latencies.length > 0) {
        agent.avg_latency_ms = Math.round(
          agent._latencies.reduce((a, b) => a + b, 0) / agent._latencies.length
        );
      }
      delete agent._latencies;
    }

    this._agentStats = stats;
    return stats;
  }

  getEdgeStats() {
    if (this._edgeStats) return this._edgeStats;

    const edges = {};

    for (const msg of this.messages) {
      const key = `${msg.from}->${msg.to}`;
      if (!edges[key]) {
        edges[key] = {
          from: msg.from,
          to: msg.to,
          count: 0,
          total_bytes: 0,
          avg_latency_ms: 0,
          failed: 0,
          types: {},
          _latencies: [],
        };
      }
      edges[key].count++;
      edges[key].total_bytes += msg.payload_size;
      edges[key]._latencies.push(msg.latency_ms);
      if (msg.status === 'failed' || msg.status === 'timeout') {
        edges[key].failed++;
      }
      edges[key].types[msg.type] = (edges[key].types[msg.type] || 0) + 1;
    }

    for (const edge of Object.values(edges)) {
      if (edge._latencies.length > 0) {
        edge.avg_latency_ms = Math.round(
          edge._latencies.reduce((a, b) => a + b, 0) / edge._latencies.length
        );
      }
      delete edge._latencies;
    }

    this._edgeStats = edges;
    return edges;
  }

  getTimeline() {
    return [...this.messages].sort((a, b) => a.timestamp - b.timestamp);
  }

  getSummary() {
    const agents = this.getAgents();
    const agentStats = this.getAgentStats();
    const edgeStats = this.getEdgeStats();
    const edges = Object.values(edgeStats);

    const totalMessages = this.messages.length;
    const totalBytes = this.messages.reduce((s, m) => s + m.payload_size, 0);
    const failedMessages = this.messages.filter(
      (m) => m.status === 'failed' || m.status === 'timeout'
    ).length;
    const avgLatency = totalMessages > 0
      ? Math.round(
          this.messages.reduce((s, m) => s + m.latency_ms, 0) / totalMessages
        )
      : 0;

    const typeBreakdown = {};
    for (const msg of this.messages) {
      typeBreakdown[msg.type] = (typeBreakdown[msg.type] || 0) + 1;
    }

    const sorted = this.getTimeline();
    const timespan = sorted.length >= 2
      ? sorted[sorted.length - 1].timestamp - sorted[0].timestamp
      : 0;

    return {
      total_agents: agents.length,
      total_messages: totalMessages,
      total_bytes: totalBytes,
      failed_messages: failedMessages,
      failure_rate: totalMessages > 0
        ? Number(((failedMessages / totalMessages) * 100).toFixed(2))
        : 0,
      avg_latency_ms: avgLatency,
      unique_edges: edges.length,
      type_breakdown: typeBreakdown,
      timespan_ms: timespan,
      messages_per_second: timespan > 0
        ? Number(((totalMessages / timespan) * 1000).toFixed(2))
        : 0,
    };
  }

  findBottlenecks(options = {}) {
    if (this._bottlenecks) return this._bottlenecks;

    const latencyThreshold = options.latency_threshold || 100;
    const trafficThreshold = options.traffic_threshold || 0.3;
    const failureThreshold = options.failure_threshold || 0.1;

    const bottlenecks = [];
    const agentStats = this.getAgentStats();
    const edgeStats = this.getEdgeStats();
    const totalMessages = this.messages.length;

    // High-traffic agents
    for (const agent of Object.values(agentStats)) {
      const trafficShare = totalMessages > 0 ? agent.total / totalMessages : 0;
      if (trafficShare > trafficThreshold) {
        bottlenecks.push({
          type: 'high_traffic_agent',
          agent: agent.name,
          severity: trafficShare > 0.5 ? 'critical' : 'warning',
          detail: `Agent "${agent.name}" handles ${(trafficShare * 100).toFixed(1)}% of all traffic (${agent.total} messages)`,
          metric: { traffic_share: Number(trafficShare.toFixed(3)), total: agent.total },
        });
      }
    }

    // High-latency edges
    for (const edge of Object.values(edgeStats)) {
      if (edge.avg_latency_ms > latencyThreshold) {
        bottlenecks.push({
          type: 'high_latency_edge',
          from: edge.from,
          to: edge.to,
          severity: edge.avg_latency_ms > latencyThreshold * 2 ? 'critical' : 'warning',
          detail: `Communication from "${edge.from}" to "${edge.to}" averages ${edge.avg_latency_ms}ms latency (threshold: ${latencyThreshold}ms)`,
          metric: { avg_latency_ms: edge.avg_latency_ms, count: edge.count },
        });
      }
    }

    // High failure rate edges
    for (const edge of Object.values(edgeStats)) {
      const failRate = edge.count > 0 ? edge.failed / edge.count : 0;
      if (failRate > failureThreshold) {
        bottlenecks.push({
          type: 'high_failure_edge',
          from: edge.from,
          to: edge.to,
          severity: failRate > 0.3 ? 'critical' : 'warning',
          detail: `Communication from "${edge.from}" to "${edge.to}" has ${(failRate * 100).toFixed(1)}% failure rate (${edge.failed}/${edge.count})`,
          metric: { failure_rate: Number(failRate.toFixed(3)), failed: edge.failed, total: edge.count },
        });
      }
    }

    // Unbalanced communication (agents that only send or only receive)
    for (const agent of Object.values(agentStats)) {
      if (agent.total >= 5) {
        const ratio = agent.sent / agent.total;
        if (ratio > 0.9) {
          bottlenecks.push({
            type: 'unbalanced_communication',
            agent: agent.name,
            severity: 'info',
            detail: `Agent "${agent.name}" is almost exclusively a sender (${agent.sent} sent, ${agent.received} received)`,
            metric: { sent: agent.sent, received: agent.received, ratio: Number(ratio.toFixed(3)) },
          });
        } else if (ratio < 0.1) {
          bottlenecks.push({
            type: 'unbalanced_communication',
            agent: agent.name,
            severity: 'info',
            detail: `Agent "${agent.name}" is almost exclusively a receiver (${agent.sent} sent, ${agent.received} received)`,
            metric: { sent: agent.sent, received: agent.received, ratio: Number(ratio.toFixed(3)) },
          });
        }
      }
    }

    bottlenecks.sort((a, b) => {
      const sevOrder = { critical: 0, warning: 1, info: 2 };
      const aOrder = sevOrder[a.severity] ?? 99;
      const bOrder = sevOrder[b.severity] ?? 99;
      return aOrder - bOrder;
    });

    this._bottlenecks = bottlenecks;
    return bottlenecks;
  }

  suggestOptimizations() {
    const bottlenecks = this.findBottlenecks();
    const suggestions = [];

    for (const bn of bottlenecks) {
      switch (bn.type) {
        case 'high_traffic_agent':
          suggestions.push({
            bottleneck: bn,
            strategy: 'load_balancing',
            description: `Consider distributing the workload of "${bn.agent}" across multiple agents using a load-balancing pattern. Introduce a dispatcher agent or use round-robin routing to reduce the traffic concentration.`,
            priority: bn.severity === 'critical' ? 'high' : 'medium',
          });
          break;

        case 'high_latency_edge':
          suggestions.push({
            bottleneck: bn,
            strategy: 'caching_or_batching',
            description: `Reduce latency between "${bn.from}" and "${bn.to}" by caching frequently requested data, batching multiple small messages into fewer larger ones, or introducing an intermediary cache agent.`,
            priority: bn.severity === 'critical' ? 'high' : 'medium',
          });
          break;

        case 'high_failure_edge':
          suggestions.push({
            bottleneck: bn,
            strategy: 'retry_and_circuit_breaker',
            description: `Implement retry logic with exponential backoff for communication from "${bn.from}" to "${bn.to}". Consider adding a circuit breaker pattern to prevent cascade failures when "${bn.to}" is unresponsive.`,
            priority: bn.severity === 'critical' ? 'high' : 'medium',
          });
          break;

        case 'unbalanced_communication':
          suggestions.push({
            bottleneck: bn,
            strategy: 'bidirectional_flow',
            description: `Agent "${bn.agent}" has highly asymmetric communication. Consider whether acknowledgment messages or status updates could improve coordination and error detection.`,
            priority: 'low',
          });
          break;
      }
    }

    return suggestions;
  }
}

module.exports = { Analyzer };
