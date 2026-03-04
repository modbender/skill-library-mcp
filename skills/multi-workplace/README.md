# multi-workplace

An [OpenClaw](https://github.com/openclaw/openclaw) skill for managing multiple project workplaces with multi-agent orchestration, isolated memory, and inter-agent communication.

## What It Does

- **Detect & manage workplaces** — auto-discovers `.git` directories as workplaces, tracks them in a central registry
- **Multi-agent per workspace** — define custom role-based agents (coder, reviewer, devops, etc.) per project
- **Swarm orchestration** — agents hand off tasks to each other with full context (Claude Swarm pattern)
- **Inter-agent communication** — lightweight Rust file-watcher server monitors `chat.md` for real-time message routing
- **Isolated memory** — each workplace gets its own memory, supermemory container, and context
- **IDE integration** — generates context files for Cursor, Claude Code, and OpenCode
- **Export/import** — share workplace configs via ZIP or JSON

## Quick Start

### Install

```bash
# Clone into your OpenClaw skills directory
git clone git@github.com:dickwu/multi-workplace.git ~/.openclaw/workspace/skills/multi-workplace
```

Or install via ClawHub (when published):
```
/skill install multi-workplace
```

### Initialize a Workspace

```
workplace init /path/to/your/project
```

For existing projects, it scans the file structure, reads markdown files, and suggests appropriate agents. For new projects, it walks you through setup.

### Core Commands

```
workplace list              # List all workplaces (clickable switch)
workplace switch my-app     # Switch active workplace
workplace scan ~/projects   # Discover workplaces in subdirectories
workplace status            # Current workplace info + agent status
workplace agents            # List agents in current workplace
workplace agent start coder # Start the coder agent
workplace kernel start      # Start persistent structure watcher
workplace deploy dev        # Show dev deployment instructions
workplace export zip        # Export workplace config
```

## Per-Workplace Structure

Each project gets a `.workplace/` directory:

```
project/
└── .workplace/
    ├── config.json          # UUID, name, settings, linked workplaces
    ├── agents/              # Agent role definitions
    │   ├── kernel.md        # Always present — structure watcher
    │   ├── coder.md         # Custom agents...
    │   └── reviewer.md
    ├── memory/              # Isolated daily logs
    ├── skills/              # Workspace-specific skills (git-managed)
    ├── chat.md              # Inter-agent communication
    ├── structure.json       # Auto-scanned file tree
    ├── full-tree.md         # Full tree with parent + linked workplaces
    ├── process-status.json  # Agent runtime states
    └── deploy/              # Deployment docs
        ├── dev.md
        ├── main.md
        └── pre.md
```

## Agent System

### Defining Agents

Create a `.md` file in `.workplace/agents/`:

```markdown
---
name: coder
role: "Senior backend developer"
triggers: ["code", "implement", "fix", "refactor"]
handoff_to: ["reviewer", "tester"]
---

# Coder Agent

## Role
You are a senior developer working on this project.

## Instructions
- Follow existing patterns in the codebase
- Write tests for new functionality
- Hand off to reviewer when implementation is complete
```

### Swarm Orchestration

Agents communicate via `chat.md` using a simple protocol:

```
[coder-to-reviewer]: Review needed for auth module. Files: src/auth.rs, src/middleware.rs
[reviewer-to-coder] @ [developer, manager]: Approved with suggestions — see inline comments
```

The Rust file-watcher server monitors `chat.md` and triggers the appropriate agent when a message arrives.

## IDE Integration

### Cursor

Run `workplace sync cursor` to generate `.cursor/rules/workplace.mdc` from your workplace config and agent definitions. This gives Cursor awareness of:

- Project structure and file tree
- Agent roles and conventions
- Deployment configs
- Linked workplaces

### Claude Code

Run `workplace sync claude` to generate/update `CLAUDE.md` at your project root with workplace context — structure, agent roles, conventions, and deploy info.

### OpenCode

Run `workplace sync opencode` to add workplace context to your `opencode.jsonc` instructions.

### How It Works

The `workplace sync` command reads your `.workplace/` config and generates IDE-specific context files. Each IDE gets the same information in its native format:

| IDE | Config File | Format |
|-----|------------|--------|
| Cursor | `.cursor/rules/workplace.mdc` | MDC with frontmatter |
| Claude Code | `CLAUDE.md` | Markdown |
| OpenCode | `opencode.jsonc` → instructions | JSONC |

Re-run `workplace sync <ide>` after changing agents or config to keep IDE context updated.

## Rust File-Watcher Server

The inter-agent communication server is a lightweight Rust binary (~1.4MB) that watches `chat.md` for changes and outputs parsed messages as JSON lines.

### Pre-built Binaries

| Platform | Binary |
|----------|--------|
| macOS (Apple Silicon) | `assets/bin/workplace-server-darwin-arm64` |
| macOS (Intel) | `assets/bin/workplace-server-darwin-x86_64` |
| Linux (x86_64) | `assets/bin/workplace-server-linux-x86_64` |
| Linux (ARM64) | `assets/bin/workplace-server-linux-arm64` |

### Build from Source

```bash
# Requires Rust toolchain
scripts/build.sh
```

### Usage

```bash
workplace-server /path/to/project
# Outputs JSON lines:
# {"timestamp":"...","sender":"coder","recipient":"reviewer","broadcast":[],"message":"...","line_number":1}
```

## Central Registry

All workplaces are tracked in `~/.openclaw/workspace/.workplaces/`:

```
.workplaces/
├── registry.json    # All known workplaces
├── current.json     # Currently active workplace
└── shared-skills/   # Skills shared across workplaces
```

## Supermemory

Each workplace uses its UUID as a `containerTag` for supermemory, providing:

- Isolated memory per project
- Cross-session awareness of project state
- Structure summaries maintained by the kernel agent

## Architecture

See the [architecture document](../../multi-workplace-arch.md) for full design details.

## Requirements

- [OpenClaw](https://github.com/openclaw/openclaw) (for agent orchestration and supermemory)
- Git (for workplace detection)
- Rust toolchain (only if building the server from source)

## License

MIT
