---
name: agent-weave
description: Master-Worker Agent Cluster for parallel task execution. Use when building distributed agent systems with parallel processing needs, task orchestration, or MapReduce-style workflows.
---

# Agent-Weave

Master-Worker Agent Cluster with parallel task execution and secure parent-child communication.

## When to Use This Skill

Use agent-weave when you need to:
- Build distributed agent systems with parallel processing
- Orchestrate multiple agents working together
- Implement MapReduce-style workflows
- Scale task execution across worker agents
- Build master-worker architectures

## Quick Start

### Installation

```bash
npm install agent-weave
```

### Basic Usage

```javascript
const { Loom } = require('agent-weave');

// Create cluster
const loom = new Loom();
const master = loom.createMaster('my-cluster');

// Create workers
const workers = loom.spawnWorkers(master.id, 5, async (data) => {
  // Process data
  return { result: data * 2 };
});

// Execute tasks
const results = await master.dispatch([1, 2, 3, 4, 5]);
console.log(results);
```

## CLI Commands

```bash
# Create master
weave loom create-master --name my-cluster

# Spawn workers
weave loom spawn --parent <master-id> --count 5

# List agents
weave loom list --tree
```

## Features

- **Master-Worker Architecture**: Orchestrate multiple worker agents
- **Parallel Execution**: Distribute tasks across workers
- **Secure Communication**: Parent-child relationship enforcement
- **MapReduce Support**: Built-in map-reduce workflows
- **Auto-scaling**: Dynamic worker management
- **Event-driven**: EventEmitter-based communication

## API Reference

### Loom
Factory for creating and managing agents.

### Master
Manages a cluster of worker agents.

### Worker
Executes tasks assigned by the master.

### Thread
Secure communication layer between agents.

### Tapestry
Task orchestration engine for MapReduce workflows.

## License

MIT
