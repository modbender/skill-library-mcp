# CodeFlicker CLI Skill

AI programming assistant skill for OpenClaw. Integrates with CodeFlicker CLI by Kuaishou.

**快手员工专用** - 使用 CodeFlicker 进行代码开发，可享受更多模型选择和免费 token 用量。

## Features

- Install and configure CodeFlicker CLI
- Execute coding tasks with flickcli
- Configure models (glm-5, claude-haiku-4.5, etc.)
- Set approval mode (default, autoEdit, yolo)
- Continue sessions
- Auto-use from OpenClaw with --cwd support
- **Workspace** - Git worktree based isolated development
- **Run** - Natural language to shell command
- **MCP** - MCP server management
- **Skills** - Skill management system

## Installation

```bash
# Install via ClawHub
clawhub install codeflicker
```

Or clone from GitHub:
```bash
git clone https://github.com/LeeGoDamn/codeflicker-skill.git
```

## Usage

### Auto-Use from OpenClaw

When OpenClaw needs to perform development tasks:

```bash
# Check if flickcli is available
if which flickcli >/dev/null 2>&1; then
    # Use flickcli with --cwd
    flickcli -q --cwd ~/work "开发任务描述"
fi
```

### Check Installation

```bash
codeflicker/scripts/check.sh
```

### Run Task

```bash
codeflicker/scripts/run.sh "write a hello world program"
```

### Configure

```bash
# Set default model
codeflicker/scripts/config.sh model glm-5

# Set auto-execute mode
codeflicker/scripts/config.sh approvalMode yolo

# View all config
codeflicker/scripts/config.sh list
```

### Continue Conversation

```bash
codeflicker/scripts/continue.sh "add unit tests"
```

### ⭐ Workspace (Git Worktree)

```bash
# Create isolated development workspace
flickcli workspace create --name feature-x

# List workspaces
flickcli workspace list

# Complete and merge
flickcli workspace complete

# Delete without merge
flickcli workspace delete <name>
```

## Requirements

- Node.js >= 22
- npm or pnpm
- Kuaishou internal network access

## Installation Steps

### 1. Set npm registry (Kuaishou internal network)

```bash
export npm_config_registry="https://npm.corp.kuaishou.com"
```

### 2. Install CLI

```bash
npm install -g @ks-codeflicker/cli
```

### 3. Create workspace directory (recommended)

```bash
mkdir -p ~/work
```

### 4. Login with SSO

```bash
flickcli /login
```

## License

MIT
