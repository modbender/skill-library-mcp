---
name: sub-agent-factory
description: Rapidly spawn and configure specialized sub-agents. Includes templates for Research, Coding, and Analysis agents. Automates workspace setup and instruction delivery.
---

# Sub-Agent Factory

Don't do everything yourself. Scale your productivity by building a team.

## Capability Matrix

- **Coder Agent**: Optimized for repo exploration and bug fixing.
- **Research Agent**: Expert at web searching and synthesizing deep reports.
- **Analysis Agent**: Focused on processing data, JSON files, and logs.

## Setup Protocol

1. **Define Mission**: Set a clear 1-sentence goal.
2. **Select Template**: Pick the agent type.
3. **Provision**: Run `scripts/create_agent.sh`.
4. **Link**: Configure communication folders (inbox/outbox).

## Installation
```bash
clawhub install sub-agent-factory
```
