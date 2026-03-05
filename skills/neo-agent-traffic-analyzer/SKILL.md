---
name: agent-traffic-analyzer
description: Analyzes and visualizes communication patterns between OpenClaw agents to identify bottlenecks and suggest optimization strategies.
version: 1.0.0
triggers:
  - "analyze agent communication patterns"
  - "visualize traffic between my agents"
  - "find bottlenecks in my agent workflow"
  - "show me how my agents are communicating"
  - "optimize agent interactions"
  - "generate communication report"
  - "analyze agent network topology"
  - "identify inefficient agent communication"
---

# Agent Traffic Analyzer

Analyzes and visualizes communication patterns between OpenClaw agents to identify bottlenecks and suggest optimization strategies.

## Installation

```bash
npm install
```

## Usage

```bash
# Analyze a communication log file
agent-traffic-analyzer analyze <logfile.json>

# Generate a network visualization
agent-traffic-analyzer visualize <logfile.json> --format dot

# Generate a full report
agent-traffic-analyzer report <logfile.json> --output report.json

# Show summary statistics
agent-traffic-analyzer summary <logfile.json>

# Find bottlenecks
agent-traffic-analyzer bottlenecks <logfile.json>
```

## Input Format

The tool expects JSON files containing an array of agent communication messages:

```json
[
  {
    "id": "msg-001",
    "from": "agent-alpha",
    "to": "agent-beta",
    "timestamp": "2026-01-15T10:30:00Z",
    "type": "request",
    "payload_size": 1024,
    "latency_ms": 45,
    "status": "delivered"
  }
]
```

## Output Formats

- **JSON** — Structured analysis results
- **CSV** — Tabular data for spreadsheet import
- **DOT** — Graphviz network graph definition

## Capabilities

- Extract and analyze message flow patterns between OpenClaw agents
- Generate visualizations of communication networks and traffic volumes
- Identify bottlenecks and inefficiencies in agent interactions
- Suggest optimization strategies for improved agent coordination
- Export analysis reports in multiple formats (JSON, CSV, DOT)
- Compare historical communication patterns over time
