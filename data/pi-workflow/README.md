# Pi Workflow Orchestration Skill

A structured workflow framework for AI agents (Pi) designed to manage task execution, self-improvement, and code quality.

## Credits

This workflow orchestration is inspired by **Srishti Codes' Claude Agent workflow framework** ([X/Twitter](https://x.com/srishticodes/status/2025254119636959701)). The approach of using plan mode, subagents, verification gates, and autonomous bug fixing for building better AI workflows has been adapted and implemented for Pi's task management system.

## Overview

This skill provides a complete orchestration framework for:

- **Planning & Execution** - Enter plan mode for non-trivial tasks, write detailed specs upfront
- **Parallel Processing** - Use subagents liberally to offload research and keep context clean
- **Self-Improvement** - Capture lessons from mistakes to prevent repeated errors
- **Quality Gates** - Verify work before marking complete, demand elegant solutions
- **Autonomous Bug Fixing** - Fix issues without hand-holding, point at logs then resolve

## Quick Start

The skill is triggered when you need to:
- Plan a multi-step task (3+ steps or architectural decisions)
- Start a new project with structured tracking
- Fix bugs and improve code autonomously
- Review code quality and elegance
- Capture and learn from mistakes

## Core Components

### 6 Disciplines

1. **Plan Node Default** - Structured planning for complex tasks
2. **Subagent Strategy** - Parallel execution and research offloading
3. **Self-Improvement Loop** - Lessons capture and iteration
4. **Verification Before Done** - Quality gates and proof of work
5. **Demand Elegance** - Balanced refinement and code quality
6. **Autonomous Bug Fixing** - Self-directed problem solving

### Task Management

- `tasks/todo.md` - Active sprint tracking
- `tasks/lessons.md` - Reusable patterns (permanent)
- `memory/YYYY-MM-DD.md` - Session logs
- `MEMORY.md` - Curated long-term memory

## Core Principles

- **Simplicity First**: Minimal code impact, make changes as simple as possible
- **No Laziness**: Find root causes, no temporary fixes, senior developer standards
- **Minimal Impact**: Only touch what's necessary, avoid introducing bugs

## Usage

Load this skill when starting new projects or managing complex tasks with Pi (the AI assistant).

## License

MIT
