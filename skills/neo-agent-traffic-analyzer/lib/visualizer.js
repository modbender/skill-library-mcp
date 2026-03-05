'use strict';

const fs = require('fs');
const path = require('path');

/**
 * Visualization generator for agent communication patterns.
 * Produces DOT graphs, ASCII network diagrams, and timeline views.
 */

class Visualizer {
  constructor(analyzer) {
    this.analyzer = analyzer;
  }

  generateDot(options = {}) {
    const title = options.title || 'Agent Communication Network';
    const edgeStats = this.analyzer.getEdgeStats();
    const agentStats = this.analyzer.getAgentStats();
    const edges = Object.values(edgeStats);

    const maxCount = Math.max(...edges.map((e) => e.count), 1);
    const maxLatency = Math.max(...edges.map((e) => e.avg_latency_ms), 1);

    const lines = [];
    lines.push('digraph AgentNetwork {');
    lines.push(`  label="${title}";`);
    lines.push('  rankdir=LR;');
    lines.push('  node [shape=box, style="rounded,filled", fontname="Helvetica"];');
    lines.push('  edge [fontname="Helvetica", fontsize=10];');
    lines.push('');

    // Node definitions with coloring based on traffic volume
    for (const agent of Object.values(agentStats)) {
      const intensity = Math.min(agent.total / (maxCount * 0.5), 1);
      const r = Math.round(255 - intensity * 100);
      const g = Math.round(255 - intensity * 50);
      const b = 255;
      const color = `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;

      const label = `${agent.name}\\nsent:${agent.sent} recv:${agent.received}`;
      lines.push(`  "${agent.name}" [label="${label}", fillcolor="${color}"];`);
    }

    lines.push('');

    // Edge definitions with weight based on message count
    for (const edge of edges) {
      const penwidth = Math.max(1, Math.round((edge.count / maxCount) * 5));
      const color = edge.avg_latency_ms > maxLatency * 0.7 ? '#cc0000' : '#333333';
      const label = `${edge.count} msgs\\n${edge.avg_latency_ms}ms`;
      lines.push(
        `  "${edge.from}" -> "${edge.to}" [label="${label}", penwidth=${penwidth}, color="${color}"];`
      );
    }

    lines.push('}');
    return lines.join('\n');
  }

  generateTimeline(options = {}) {
    const maxWidth = options.width || 80;
    const timeline = this.analyzer.getTimeline();
    if (timeline.length === 0) return 'No messages to display.';

    const agents = this.analyzer.getAgents();
    const maxNameLen = Math.max(...agents.map((a) => a.length));

    const lines = [];
    lines.push('=== Agent Communication Timeline ===');
    lines.push('');

    // Header with agent columns
    const colWidth = Math.max(12, Math.floor((maxWidth - maxNameLen - 4) / agents.length));
    let header = ' '.repeat(maxNameLen + 2) + '| ';
    for (const agent of agents) {
      header += agent.substring(0, colWidth - 1).padEnd(colWidth);
    }
    lines.push(header);
    lines.push('-'.repeat(header.length));

    // Messages as rows
    for (const msg of timeline) {
      const ts = msg.timestamp instanceof Date
        ? msg.timestamp.toISOString().substring(11, 19)
        : '??:??:??';

      const fromIdx = agents.indexOf(msg.from);
      const toIdx = agents.indexOf(msg.to);

      let row = ts.padEnd(maxNameLen + 2) + '| ';
      for (let i = 0; i < agents.length; i++) {
        if (i === fromIdx && i === toIdx) {
          row += '[SELF]'.padEnd(colWidth);
        } else if (i === fromIdx) {
          const arrow = fromIdx < toIdx ? '--->' : '<---';
          row += arrow.padEnd(colWidth);
        } else if (i === toIdx) {
          const statusMark = msg.status === 'delivered' ? '*' : 'X';
          row += `[${statusMark}]`.padEnd(colWidth);
        } else if (
          (i > fromIdx && i < toIdx) ||
          (i > toIdx && i < fromIdx)
        ) {
          row += '----'.padEnd(colWidth);
        } else {
          row += '.'.padEnd(colWidth);
        }
      }
      lines.push(row);
    }

    lines.push('');
    lines.push('Legend: ---> = message sent, [*] = delivered, [X] = failed/timeout');
    return lines.join('\n');
  }

  generateAsciiNetwork() {
    const agentStats = this.analyzer.getAgentStats();
    const edgeStats = this.analyzer.getEdgeStats();
    const agents = Object.values(agentStats);
    const edges = Object.values(edgeStats);

    if (agents.length === 0) return 'No agents to display.';

    const lines = [];
    lines.push('=== Agent Network Topology ===');
    lines.push('');

    // Display each agent with its connections
    for (const agent of agents) {
      const box = `[${agent.name}]`;
      const stats = `(sent:${agent.sent} recv:${agent.received} avg:${agent.avg_latency_ms}ms)`;
      lines.push(`  ${box} ${stats}`);

      // Show outgoing connections
      const outgoing = edges.filter((e) => e.from === agent.name);
      for (let i = 0; i < outgoing.length; i++) {
        const isLast = i === outgoing.length - 1;
        const prefix = isLast ? '  └──>' : '  ├──>';
        const failInfo = outgoing[i].failed > 0 ? ` (${outgoing[i].failed} failed)` : '';
        lines.push(
          `${prefix} ${outgoing[i].to}: ${outgoing[i].count} msgs, ${outgoing[i].avg_latency_ms}ms avg${failInfo}`
        );
      }

      lines.push('');
    }

    return lines.join('\n');
  }

  generateNetworkDotFromTemplate() {
    const templatePath = path.join(__dirname, '..', 'assets', 'templates', 'network.dot');
    let template;
    try {
      template = fs.readFileSync(templatePath, 'utf8');
    } catch {
      return this.generateDot();
    }

    const agentStats = this.analyzer.getAgentStats();
    const edgeStats = this.analyzer.getEdgeStats();

    let nodesBlock = '';
    for (const agent of Object.values(agentStats)) {
      nodesBlock += `  "${agent.name}" [label="${agent.name}\\nsent:${agent.sent} recv:${agent.received}"];\n`;
    }

    let edgesBlock = '';
    for (const edge of Object.values(edgeStats)) {
      edgesBlock += `  "${edge.from}" -> "${edge.to}" [label="${edge.count} msgs"];\n`;
    }

    return template
      .replace('{{NODES}}', nodesBlock.trimEnd())
      .replace('{{EDGES}}', edgesBlock.trimEnd());
  }
}

module.exports = { Visualizer };
