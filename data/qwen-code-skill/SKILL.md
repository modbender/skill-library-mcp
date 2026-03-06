---
name: qwen-code
description: Run Alibaba Cloud Qwen Code CLI via background process for task execution, code review, and automation.
metadata: {"clawdbot":{"emoji":"🦌","requires":{"anyBins":["qwen"]}}}
author: UserB1ank
---

# Qwen Code Skill (background-first)

Use **bash background mode** for non-interactive coding work with Qwen Code CLI.

## The Pattern: workdir + background

```bash
# Start Qwen Code in target directory
bash workdir:~/project background:true yieldMs:30000 command:"qwen -p 'Build a Flask API'"
# Returns sessionId for tracking

# Monitor progress
process action:log sessionId:XXX

# Check if done
process action:poll sessionId:XXX

# Send input (if Qwen asks a question)
process action:write sessionId:XXX data:"y"

# Kill if needed
process action:kill sessionId:XXX
```

**Why workdir matters:** Agent wakes up in a focused directory, doesn't wander off reading unrelated files.

---

## Quick Start

### Prerequisites

```bash
# Install Qwen Code CLI
npm install -g @qwen-code/qwen-code@latest

# Verify installation
qwen --version

# Authenticate (Option 1: OAuth)
qwen auth login

# Or Option 2: API Key
export DASHSCOPE_API_KEY="sk-xxx"
```

### Basic Usage

```bash
# Check status
scripts/qwen-code.js status

# Run a task
scripts/qwen-code.js run "Create a Flask API"

# Code review
scripts/qwen-code.js review src/app.ts

# Headless mode (JSON output)
scripts/qwen-code.js headless "Analyze code" -o json
```

---

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `status` | Check Qwen Code status and authentication | `scripts/qwen-code.js status` |
| `run <task>` | Execute programming task | `scripts/qwen-code.js run "Create REST API"` |
| `review <file>` | Code review and analysis | `scripts/qwen-code.js review src/main.py` |
| `headless <task>` | Headless mode (JSON output) | `scripts/qwen-code.js headless "Analyze" -o json` |
| `help` | Show help information | `scripts/qwen-code.js help` |

---

## OpenClaw Integration

### Background Execution

```bash
# Basic task
bash workdir:~/project background:true yieldMs:30000 \
  command:"qwen -p 'Create Python Flask API'"

# Specify model
bash workdir:~/project background:true yieldMs:30000 \
  command:"qwen -p 'Analyze code structure' -m qwen3-coder-plus"

# YOLO mode (auto-approve)
bash workdir:~/project background:true yieldMs:30000 \
  command:"qwen -p 'Refactor this function' -y"
```

### Process Management

```bash
# View logs
process action:log sessionId:XXX

# Check completion
process action:poll sessionId:XXX

# Send input (if Qwen asks)
process action:write sessionId:XXX data:"y"
```

### Headless Mode (Automation/CI/CD)

```bash
# JSON output
qwen -p "Analyze code structure" --output-format json

# Pipeline operations
git diff | qwen -p "Generate commit message"

# Batch processing
find src -name "*.ts" | xargs -I {} qwen -p "Review {}"
```

---

## Models

Qwen Code supports Alibaba Cloud models:

- `qwen3.5-plus` - General purpose (default)
- `qwen3-coder-plus` - Coding specialized
- `qwen3-coder-next` - Latest coding model
- `qwen3-max-2026-01-23` - Most capable

**Specify model:**
```bash
bash workdir:~/project background:true yieldMs:30000 \
  command:"qwen -p 'Refactor this' -m qwen3-coder-plus"
```

---

## Authentication

### OAuth (Recommended)

```bash
qwen auth login
```

Opens browser for OAuth flow. Token auto-refreshes.

### API Key

```bash
export DASHSCOPE_API_KEY="sk-xxx"
```

Get key from: https://dashscope.console.aliyun.com/

---

## ⚠️ Rules

1. **Respect tool choice** — if user asks for Qwen, use Qwen. NEVER offer to build it yourself!
2. **Be patient** — don't kill sessions because they're "slow"
3. **Monitor with process:log** — check progress without interfering
4. **YOLO mode for building** — `--yolo` auto-approves changes (use in workspace only)
5. **Review mode for safety** — production code should use review mode
6. **Parallel is OK** — run many Qwen processes at once for batch work
7. **NEVER start Qwen in ~/clawd/** — it'll read your soul docs! Use target project dir or /tmp
8. **Workspace safety** — YOLO mode is safe in `agents.defaults.workspace`, not elsewhere

---

## For

- Developers using Qwen Code for programming tasks
- Teams needing code review and analysis
- Automation scripts and CI/CD integration
- OpenClaw Sub-Agent and Skills management
- Batch code analysis and refactoring

## Not For

- Environments without Qwen Code CLI installed
- GUI-based interaction requirements
- Non-Alibaba Cloud LLM users
- Offline environments (requires network connection)

---

## Security & Boundaries

| Component | Behavior | Executes Shell Commands? |
|-----------|----------|-------------------------|
| `scripts/qwen-code.js` | Wraps Qwen Code CLI commands | Yes (via `qwen` command) |
| `references/qwen-cli-commands.md` | Command reference documentation | No (plain text) |
| `assets/examples/` | Example code files | No (static files) |

### ⚠️ Security Notes

- This Skill does not execute code directly, only calls Qwen Code CLI
- All code generation and modifications require user confirmation
- Use review mode in production environments
- Disable YOLO mode for sensitive projects

---

## Examples

See [`assets/examples/`](assets/examples/) for complete examples:

| Example | Description |
|---------|-------------|
| `basic-task.example.sh` | Basic task execution |
| `code-review.example.sh` | Code review workflow |
| `ci-cd.example.yml` | GitHub Actions integration |
| `headless-mode.example.js` | Node.js automation example |

---

## References

- [📖 Qwen Code Official Docs](https://qwenlm.github.io/qwen-code-docs/zh/)
- [📝 Command Reference](references/qwen-cli-commands.md)
- [📦 Example Code](assets/examples/)
- [🦌 OpenClaw Documentation](https://openclaw.ai)

---

## Troubleshooting

### "qwen: command not found"

```bash
npm install -g @qwen-code/qwen-code@latest
```

### "Authentication required"

```bash
qwen auth login
# Or set API key
export DASHSCOPE_API_KEY="sk-xxx"
```

### Session stuck/waiting for input

```bash
# Check what Qwen is asking
process action:log sessionId:XXX

# Send approval
process action:write sessionId:XXX data:"y"
```

### Kill stuck session

```bash
process action:kill sessionId:XXX
```

---

*Qwen Code Skill 🦌 - Your AI coding partner powered by Alibaba Cloud*
