# Coder Workspaces Skill for OpenClaw

Manage [Coder](https://coder.com) workspaces and AI coding agent tasks from your OpenClaw agent.

## Features

- **Workspaces**: List, create, start, stop, restart, delete
- **Remote Commands**: SSH into workspaces and run commands
- **AI Tasks**: Create and manage Coder Tasks with Claude Code, Aider, Goose, etc.

## Prerequisites

1. Access to a Coder deployment (self-hosted or Coder Cloud)
2. Coder CLI installed
3. Environment variables configured

## Setup

### 1. Install Coder CLI

Install from your Coder instance to ensure version compatibility:

```bash
# Visit your instance's CLI page for instructions
# https://your-coder-instance.com/cli
```

Or via Homebrew (may not match server version):

```bash
brew install coder
```

See [Coder CLI docs](https://coder.com/docs/install/cli) for all options.

### 2. Set Environment Variables

Add to your OpenClaw config (`~/.openclaw/openclaw.json`):

```json
{
  "env": {
    "CODER_URL": "https://your-coder-deployment.com",
    "CODER_SESSION_TOKEN": "your-session-token"
  }
}
```

Get a token at `https://your-coder-deployment.com/cli-auth` or `/settings/tokens`.

### 3. Authenticate

```bash
coder login --token "$CODER_SESSION_TOKEN" "$CODER_URL"
```

### 4. Verify

```bash
coder whoami
```

## Install the Skill

```bash
clawhub install coder-workspaces
```

## Usage

Ask your OpenClaw agent things like:

- "List my Coder workspaces"
- "Start my dev workspace"
- "Create a task to fix the auth bug"
- "Check status of my running tasks"
- "SSH into backend and run the tests"

## Links

- [Coder Docs](https://coder.com/docs)
- [Coder CLI](https://coder.com/docs/install/cli)
- [Coder Tasks](https://coder.com/docs/ai-coder)
- [OpenClaw](https://openclaw.ai)
- [ClawHub](https://clawhub.com)

## License

MIT
