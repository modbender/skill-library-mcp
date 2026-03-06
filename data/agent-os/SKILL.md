---
name: agent-os
description: Persistent agent operating system for OpenClaw. Agents remember across sessions, learn from experience, coordinate on complex projects without duplicate work.
---

# Agent OS — Persistent Agent Operating System

Agents that remember. Learn. Coordinate.

## What It Does

Agent OS enables multi-agent project execution with persistent memory:

- **Agent Memory** — Each agent remembers past tasks, lessons learned, success rates
- **Task Decomposition** — Break high-level goals into executable task sequences
- **Smart Routing** — Assign tasks to agents based on capability fit
- **Execution Tracking** — Live progress board showing what every agent is doing
- **State Persistence** — Project state survives restarts (resume mid-project)

## Quick Start

### Installation

```bash
clawhub install nova/agent-os
```

### Basic Usage

```javascript
const { AgentOS } = require('agent-os');

const os = new AgentOS('my-project');

// Register agents with capabilities
os.registerAgent('research', '🔍 Research', ['research', 'planning']);
os.registerAgent('design', '🎨 Design', ['design', 'planning']);
os.registerAgent('dev', '💻 Development', ['development']);

os.initialize();

// Run a project
const result = await os.runProject('Build a feature', [
  'planning',
  'design',
  'development',
]);

console.log(result.progress); // 100
```

## Core Concepts

### Agent
Persistent worker with:
- **Memory** — Past tasks, lessons learned, success rates
- **State** — Current task, progress, blockers
- **Capabilities** — What it's good at (research, design, development, etc.)

### TaskRouter
Decomposes goals into executable tasks:
- Breaks "Build a feature" into: plan → design → develop → test
- Matches tasks to agents based on capability fit
- Tracks dependencies (task A must finish before task B)

### Executor
Runs tasks sequentially:
- Assigns tasks to agents
- Tracks progress in real-time
- Persists state so projects survive restarts
- Handles blockers and errors

### AgentOS
Orchestrates everything:
- Register agents
- Initialize system
- Run projects
- Get status

## Architecture

```
AgentOS (top-level orchestration)
├── Agent (persistent worker)
│   ├── Memory (lessons, capabilities, history)
│   └── State (current task, progress)
├── TaskRouter (goal decomposition)
│   ├── Templates (planning, design, development, etc.)
│   └── Matcher (task → agent assignment)
└── Executor (task execution)
    ├── Sequential runner
    ├── Progress tracking
    └── State persistence
```

## State Persistence

All state is saved to the `data/` directory:

- `[agent-id]-memory.json` — Agent knowledge base
- `[agent-id]-state.json` — Current agent status
- `[project-id]-project.json` — Project task list + status

**This means:**
✅ Projects survive restarts
✅ Agents remember past work
✅ Resume mid-project seamlessly

## File Structure

```
agent-os/
├── core/
│   ├── agent.js          # Agent class
│   ├── task-router.js    # Task decomposition
│   ├── executor.js       # Execution scheduler
│   └── index.js          # AgentOS class
├── ui/
│   ├── dashboard.html    # Live progress UI
│   ├── dashboard.js      # Dashboard logic
│   └── style.css         # Styling
├── examples/
│   └── research-project.js  # Full working example
├── data/                 # Auto-created (persistent state)
└── package.json
```

## API Reference

### AgentOS

```javascript
new AgentOS(projectId?)
registerAgent(id, name, capabilities)
initialize()
runProject(goal, taskTypes)
getStatus()
getAgentStatus(agentId)
toJSON()
```

### Agent

```javascript
startTask(task)
updateProgress(percentage, message)
completeTask(output)
setBlocker(message)
recordError(error)
learnLesson(category, lesson)
reset()
getStatus()
```

### TaskRouter

```javascript
decompose(goal, taskTypes)
matchAgent(taskType)
getTasksForAgent(agentId, tasks)
canExecuteTask(task, allTasks)
getNextTask(tasks)
completeTask(taskId, tasks, output)
getProjectStatus(tasks)
```

### Executor

```javascript
initializeProject(goal, taskTypes)
execute()
executeTask(task)
getStatus()
```

## Example: Research + Design + Development

See `examples/research-project.js` for the canonical example:

```bash
npm start
```

This demonstrates:
- ✅ 3 agents with different capabilities
- ✅ 12 tasks across 3 phases (planning, design, development)
- ✅ Sequential execution with progress tracking
- ✅ State persistence to disk
- ✅ Final status report

Expected output:
```
✅ Registered 3 agents
📋 Task Plan: 12 tasks
🚀 Starting execution...
✅ [Task 1] Complete
✅ [Task 2] Complete
...
📊 PROJECT COMPLETE - 100% progress
```

## What's Coming (v0.2+)

- HTTP server + live dashboard
- Parallel task execution (DAG solver)
- Capability learning system (auto-score agents)
- Smart agent routing (match to best agent)
- Failure recovery + retry logic
- Cost tracking (token usage per agent)
- Human checkpoints (review high-risk outputs)

## Philosophy

**Agents should remember what they learn.**

Most agent frameworks are stateless. Agent OS keeps persistent memory so agents:
1. **Remember** — No redundant context resets
2. **Learn** — Capability scores improve over time
3. **Coordinate** — Shared state prevents duplication
4. **Cost less** — Less context = cheaper API calls

## License

MIT

---

**Built with ❤️ by Nova for OpenClaw**

See README.md and ARCHITECTURE.md for complete documentation.
