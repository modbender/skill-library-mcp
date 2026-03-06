---
name: codeflicker
description: CodeFlicker CLI 编程助手 - 快手员工专用的 AI 代码开发工具，支持更多模型和免费用量
---

# CodeFlicker CLI Skill

AI programming assistant CLI by Kuaishou. Similar to Claude Code or Codex CLI.

**专为快手员工设计** - 使用 CodeFlicker 进行代码开发，可享受：
- 更多模型选择（GLM、Claude 系列等）
- 快手提供的免费 token 用量

## Auto-Use (for OpenClaw)

When OpenClaw needs to perform development tasks (writing code, refactoring, debugging, etc.):

1. **Check if flickcli is available:**
   ```bash
   which flickcli
   ```

2. **If available, use flickcli with --cwd:**
   ```bash
   flickcli -q --cwd ~/work "开发任务描述"
   ```

3. **Use workspace as default if no specific path:**
   ```bash
   flickcli -q --cwd ~/work "任务描述"
   ```

## Install

### Step 1: Set npm registry (for Kuaishou internal network)

```bash
export npm_config_registry="https://npm.corp.kuaishou.com"
```

### Step 2: Install CLI

```bash
npm install -g @ks-codeflicker/cli
```

### Step 3: Login with SSO

```bash
flickcli /login
```

### Step 4: Create workspace directory (recommended)

```bash
mkdir -p ~/work
```

Check installation:
```bash
flickcli --version
```

## Config

### Workspace Setup (Recommended)

Create a workspace directory for codeflicker to use as project base:

```bash
mkdir -p ~/work
cd ~/work
```

### View config:
```bash
flickcli config list -g
```

### Set config (global):
```bash
flickcli config set -g model glm-5
flickcli config set -g smallModel claude-haiku-4.5
flickcli config set -g planModel claude-4.5-sonnet
flickcli config set -g visionModel claude-4.5-sonnet
flickcli config set -g approvalMode yolo
```

Available models (wanqing provider):
- `glm-5` - default
- `glm-4.7`, `claude-haiku-4.5` - lightweight
- `claude-4.5-sonnet` - planning/vision

Approval modes:
- `default` - require confirmation
- `autoEdit` - auto edit
- `yolo` - auto execute (use with caution)

## Usage

### For OpenClaw (auto-detect and use)

```bash
# Check if available
if which flickcli >/dev/null 2>&1; then
    # Use flickcli with cwd
    flickcli -q --cwd ~/work "开发任务"
fi
```

### Basic Commands

Interactive mode:
```bash
flickcli "create a new react project"
```

Quiet mode (non-interactive):
```bash
flickcli -q "implement fibonacci"
```

Continue last session:
```bash
flickcli -q -c "add unit tests"
```

Specify model:
```bash
flickcli -m glm-5 "task"
```

Specify working directory:
```bash
flickcli --cwd /path/to/project "task"
```

### ⭐ Workspace (Git Worktree)

Isolated development using git worktrees:

```bash
# Create new workspace with random name
flickcli workspace create

# Create with custom name
flickcli workspace create --name feature-login

# Create from specific branch
flickcli workspace create -b develop

# List all workspaces
flickcli workspace list

# Complete and merge (run from repo root)
flickcli workspace complete

# Delete without merging
flickcli workspace delete <name>
flickcli workspace delete <name> --force  # even with uncommitted changes
```

### Run (Natural Language to Shell)

Interactive shell command generator:
```bash
flickcli run
# Then type: "list all files modified today"
# Press Enter to generate command
# Press Enter again to execute, Ctrl+C to cancel
```

### Skills Management

```bash
# Add skill from GitHub
flickcli skill add user/repo

# Add globally
flickcli skill add -g user/repo

# List skills
flickcli skill list

# Remove skill
flickcli skill remove <name>
```

### MCP Servers

```bash
# Add MCP server
flickcli mcp add my-server npx @example/mcp-server

# List MCP servers
flickcli mcp list

# Remove MCP server
flickcli mcp remove my-server
```

### View Session Logs

```bash
flickcli log
flickcli log /path/to/logfile
```

### Tools Control

Enable/disable specific tools:
```bash
# Disable write tool (read-only mode)
flickcli --tools '{"write":false}' "analyze this code"

# Disable bash and write (safe mode)
flickcli --tools '{"bash":false,"write":false}' "explain the logic"
```

## Common Workflows

### Bug Fix
```bash
flickcli -q --cwd ~/work "fix the null pointer exception in userService.js"
```

### New Feature
```bash
flickcli -q --cwd ~/work "implement REST API for user management"
```

### Code Review
```bash
flickcli -q --cwd ~/work "review this codebase and identify issues"
```

### Refactoring
```bash
flickcli -q --cwd ~/work "refactor database layer to use SQLAlchemy"
```

### Using Workspace for Isolated Development
```bash
# 1. Create isolated workspace
flickcli workspace create --name feature-payment

# 2. Work in the workspace directory
cd .codeflicker-workspaces/feature-payment

# 3. Do your work with flickcli
flickcli -q "implement payment API"

# 4. Return to root and complete
cd <repository-root>
flickcli workspace complete
```

## Quick Reference

| Command | Description |
|---------|-------------|
| `flickcli "task"` | Interactive mode |
| `flickcli -q "task"` | Quiet mode |
| `flickcli -q -c "task"` | Continue session |
| `flickcli -q -r <id> "task"` | Resume session |
| `flickcli -q --cwd /path "task"` | Run in specific directory |
| `flickcli config set -g approvalMode yolo` | Auto-execute mode |
| `flickcli workspace create` | Create git worktree |
| `flickcli workspace complete` | Merge workspace |
| `flickcli run` | Natural language to shell |
| `flickcli skill add user/repo` | Add skill |

## Notes

- Install requires Kuaishou internal npm registry
- **Must login with SSO before first use:** `flickcli /login`
- **Recommended: Create ~/work directory** for project base
- Use `--cwd` to specify working directory for development tasks
- yolo mode auto-executes all operations
- Workspace feature uses git worktrees for isolated development