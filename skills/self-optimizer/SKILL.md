---
name: self-optimizer
displayName: Self Optimizer
description: Analyzes OpenClaw logs, chat history, and the .openclaw installation to propose self-improvement and optimization suggestions. Use when optimizing or auditing OpenClaw setup.
---

# Self Optimizer

Analyzes OpenClaw logs, chat history, and the .openclaw local root installation folder to propose self-improvement and optimization suggestions.


## Commands

- `self_optimizer.py analyze [--json]` - Runs the analysis and suggests improvements.


## Features

- **Log Analysis**: Scans `gateway.log` and `openclaw.log` for errors, restarts, and performance metrics.
- **Chat History Analysis (Planned)**: Identifies recurring issues, common requests, or areas of confusion from chat transcripts.
- **Root Folder Scan (Planned)**: Examines `openclaw.json`, skill configurations, and `MEMORY.md` for optimization opportunities.
- **Recommendations**: Provides actionable suggestions for performance, stability, and new skill development.
