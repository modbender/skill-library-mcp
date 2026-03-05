# 🔍 Sightglass — Agent Supply Chain Intelligence

Your AI coding agent just added 47 dependencies to your project. Do you know why it picked any of them?

**Sightglass instruments AI coding agents** to capture every tool selection, dependency install, and architectural choice — then surfaces risks, biases, and better alternatives you never saw.

## Why This Matters

When a human developer picks a dependency, there's a reasoning trail: blog posts read, alternatives compared, team discussions had. When an AI agent picks one, that trail is invisible. The agent "just knows" packages from training data — which means it's biased toward:

- Whatever was popular when training data was cut off
- Packages with the most Stack Overflow mentions (not the best packages)
- Dependencies it's seen in similar projects (not necessarily right for yours)

Sightglass makes this invisible decision-making visible.

## Discovery Classification

Sightglass classifies **how** your agent found each dependency:

| Classification | What It Means | Risk Level |
|---|---|---|
| **TRAINING_RECALL** | Agent just "knew" it from training data — no search performed | 🟡 Medium |
| **CONTEXT_INHERITANCE** | Found in existing project files (package.json, imports, etc.) | 🟢 Low |
| **REACTIVE_SEARCH** | Agent hit a problem and searched for a solution | 🟡 Medium |
| **PROACTIVE_SEARCH** | Agent actively compared alternatives before choosing | 🟢 Low |
| **USER_DIRECTED** | Human explicitly told the agent what to use | ⚪ None |

High `TRAINING_RECALL` percentages are a red flag — it means your agent is on autopilot, not thinking.

## Quick Start

### 1. Setup

```bash
./skills/sightglass/setup.sh
```

This installs the CLI (`@sightglass/cli`), runs initial configuration, and checks the watcher daemon.

### 2. Login

```bash
sightglass login
```

Authenticate with [sightglass.dev](https://sightglass.dev) to enable cloud analysis and history.

### 3. Watch

```bash
sightglass watch
```

Starts the background watcher that monitors agent sessions — file changes, package installs, tool calls.

### 4. Analyze

```bash
sightglass analyze
# or
./skills/sightglass/analyze.sh --since "1 hour ago" --format json
```

## OpenClaw Integration

### Automatic Session Tracking

Sightglass provides pre/post hooks for coding agent sessions:

**Before a session** — `hooks/pre-spawn.sh`:
- Records start time and project context
- Ensures the watcher daemon is running

**After a session** — `hooks/post-session.sh`:
- Runs analysis on everything that happened
- Outputs a summary: risks found, training recall %, alternatives missed

### Using with a Coding Agent

When you spawn a coding agent through OpenClaw, wrap it with Sightglass:

```bash
# Before spawning
source ./skills/sightglass/hooks/pre-spawn.sh /path/to/project

# ... agent does its work ...

# After session ends
./skills/sightglass/hooks/post-session.sh
```

The post-session output looks like:

```
📊 Session Summary
  Dependencies added: 12
  Risks found: 3
  Training recall: 67%
  Alternatives missed: 5

  ⚠️  Run 'sightglass analyze --since ...' for details
```

67% training recall means two-thirds of the packages were grabbed from memory with zero comparison shopping. Sightglass will show you what alternatives existed.

## Commands Reference

### CLI (`@sightglass/cli`)

| Command | Description |
|---|---|
| `sightglass init` | Initialize Sightglass in a project directory |
| `sightglass login` | Authenticate with sightglass.dev |
| `sightglass setup` | Interactive first-time configuration |
| `sightglass watch` | Start the watcher daemon |
| `sightglass analyze` | Analyze agent sessions and dependency decisions |

### Skill Scripts

| Script | Description |
|---|---|
| `setup.sh` | Install CLI, configure, verify watcher |
| `analyze.sh` | Standalone analysis with `--since`, `--session`, `--format`, `--push` flags |
| `hooks/pre-spawn.sh` | Pre-session hook — records start, ensures watcher |
| `hooks/post-session.sh` | Post-session hook — analyzes and summarizes |

### analyze.sh Flags

```
--since <time>     Analysis window start (ISO timestamp or relative like "1 hour ago")
--session <id>     Analyze a specific session by ID
--format <fmt>     Output format: text (default), json, markdown
--push             Push results to https://sightglass.dev
```

## What Sightglass Surfaces

For each agent session, you get:

- **Dependency inventory** — every package added, removed, or upgraded
- **Discovery method** — how the agent found each one (training recall vs. searched)
- **Risk flags** — known vulnerabilities, unmaintained packages, better alternatives
- **Alternatives report** — what the agent *could* have chosen but didn't consider
- **Bias indicators** — patterns showing training data influence over reasoned choice

## API

All data syncs to [sightglass.dev](https://sightglass.dev) when authenticated. Use `--push` with analyze or configure auto-push in setup.

---

*Your agent's dependencies are your dependencies. Know where they came from.*
