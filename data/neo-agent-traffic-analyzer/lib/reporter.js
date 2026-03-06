'use strict';

const fs = require('fs');
const path = require('path');

/**
 * Report generation and export module.
 * Exports analysis results in JSON, CSV, and DOT formats.
 */

class Reporter {
  constructor(analyzer, visualizer) {
    this.analyzer = analyzer;
    this.visualizer = visualizer;
  }

  generateJSON() {
    return JSON.stringify(
      {
        summary: this.analyzer.getSummary(),
        agents: this.analyzer.getAgentStats(),
        edges: this.analyzer.getEdgeStats(),
        bottlenecks: this.analyzer.findBottlenecks(),
        optimizations: this.analyzer.suggestOptimizations(),
      },
      null,
      2
    );
  }

  generateCSV() {
    const lines = [];

    // Agent stats section
    lines.push('## Agent Statistics');
    lines.push('agent,sent,received,total,sent_bytes,received_bytes,avg_latency_ms,failed,timeouts');
    const agentStats = this.analyzer.getAgentStats();
    for (const agent of Object.values(agentStats)) {
      lines.push(
        [
          agent.name,
          agent.sent,
          agent.received,
          agent.total,
          agent.sent_bytes,
          agent.received_bytes,
          agent.avg_latency_ms,
          agent.failed,
          agent.timeouts,
        ].join(',')
      );
    }

    lines.push('');

    // Edge stats section
    lines.push('## Edge Statistics');
    lines.push('from,to,count,total_bytes,avg_latency_ms,failed');
    const edgeStats = this.analyzer.getEdgeStats();
    for (const edge of Object.values(edgeStats)) {
      lines.push(
        [edge.from, edge.to, edge.count, edge.total_bytes, edge.avg_latency_ms, edge.failed].join(
          ','
        )
      );
    }

    lines.push('');

    // Bottlenecks section
    lines.push('## Bottlenecks');
    lines.push('type,severity,detail');
    const bottlenecks = this.analyzer.findBottlenecks();
    for (const bn of bottlenecks) {
      lines.push([bn.type, bn.severity, `"${bn.detail}"`].join(','));
    }

    return lines.join('\n');
  }

  generateDot(options) {
    return this.visualizer.generateDot(options);
  }

  generateReport(format = 'json', options = {}) {
    switch (format.toLowerCase()) {
      case 'json':
        return this.generateJSON();
      case 'csv':
        return this.generateCSV();
      case 'dot':
        return this.generateDot(options);
      default:
        throw new Error(`Unsupported format: "${format}". Supported: json, csv, dot`);
    }
  }

  exportToFile(filepath, format = 'json', options = {}) {
    const content = this.generateReport(format, options);
    const dir = path.dirname(filepath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    fs.writeFileSync(filepath, content, 'utf8');
    return filepath;
  }

  generateTextSummary() {
    const summary = this.analyzer.getSummary();
    const bottlenecks = this.analyzer.findBottlenecks();
    const optimizations = this.analyzer.suggestOptimizations();

    const lines = [];
    lines.push('╔══════════════════════════════════════════════╗');
    lines.push('║     Agent Traffic Analysis Report            ║');
    lines.push('╚══════════════════════════════════════════════╝');
    lines.push('');
    lines.push('--- Summary ---');
    lines.push(`  Agents:           ${summary.total_agents}`);
    lines.push(`  Total Messages:   ${summary.total_messages}`);
    lines.push(`  Total Data:       ${formatBytes(summary.total_bytes)}`);
    lines.push(`  Failed Messages:  ${summary.failed_messages} (${summary.failure_rate}%)`);
    lines.push(`  Avg Latency:      ${summary.avg_latency_ms}ms`);
    lines.push(`  Unique Channels:  ${summary.unique_edges}`);
    lines.push(`  Timespan:         ${formatDuration(summary.timespan_ms)}`);
    lines.push(`  Throughput:       ${summary.messages_per_second} msg/s`);
    lines.push('');

    if (Object.keys(summary.type_breakdown).length > 0) {
      lines.push('--- Message Types ---');
      for (const [type, count] of Object.entries(summary.type_breakdown)) {
        lines.push(`  ${type}: ${count}`);
      }
      lines.push('');
    }

    if (bottlenecks.length > 0) {
      lines.push('--- Bottlenecks ---');
      for (const bn of bottlenecks) {
        const icon = bn.severity === 'critical' ? '[!]' : bn.severity === 'warning' ? '[~]' : '[i]';
        lines.push(`  ${icon} ${bn.detail}`);
      }
      lines.push('');
    } else {
      lines.push('--- Bottlenecks ---');
      lines.push('  No bottlenecks detected.');
      lines.push('');
    }

    if (optimizations.length > 0) {
      lines.push('--- Optimization Suggestions ---');
      for (let i = 0; i < optimizations.length; i++) {
        const opt = optimizations[i];
        lines.push(`  ${i + 1}. [${opt.priority}] ${opt.strategy}`);
        lines.push(`     ${opt.description}`);
      }
      lines.push('');
    }

    return lines.join('\n');
  }
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  const idx = Math.min(i, units.length - 1);
  return `${(bytes / Math.pow(1024, idx)).toFixed(1)} ${units[idx]}`;
}

function formatDuration(ms) {
  if (ms === 0) return '0ms';
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  if (ms < 3600000) return `${(ms / 60000).toFixed(1)}m`;
  return `${(ms / 3600000).toFixed(1)}h`;
}

module.exports = { Reporter };
