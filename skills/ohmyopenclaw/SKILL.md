---
name: ohmyopenclaw
version: 1.0.0
description: AI-native configuration and setup guides for OpenClaw
author: ohmyopenclaw
repository: https://github.com/ohmyopenclaw/ohmyopenclaw
keywords:
  - openclaw
  - configuration
  - setup
  - agent-swarm
  - ai-native
license: MIT
---

# ohmyopenclaw

AI-native configuration and setup guides for OpenClaw.

## What This Skill Provides

This skill helps you configure OpenClaw for various use cases through Setup Guides. Each guide provides step-by-step instructions that the AI can read and apply automatically.

## Available Guides

| Guide | Use Case | Priority |
|-------|----------|----------|
| [agent-swarm](guides/agent-swarm.md) | Multi-agent architecture with Orchestrator + Workers | ⭐⭐⭐ Recommended |
| [memory-optimized](guides/memory-optimized.md) | Enhanced memory with search capabilities | ⭐⭐ |
| [chinese-providers](guides/chinese-providers.md) | Chinese AI provider configuration | ⭐⭐ |
| [cost-optimization](guides/cost-optimization.md) | Cost reduction strategies | ⭐ |
| [monitor](guides/monitor.md) | Proactive monitoring and task discovery | ⭐⭐ |

## Usage

### Apply a Guide

Simply tell the AI which guide to apply:

```
Apply agent-swarm guide
```

```
Setup memory optimization
```

```
Configure for Chinese providers
```

### View Guide Details

```
Show me the agent-swarm guide
```

## Installation

### For New Users

If you don't have OpenClaw installed yet:

```bash
# macOS / Linux
curl -fsSL https://get.ohmyopenclaw.dev | bash

# Windows PowerShell
irm https://get.ohmyopenclaw.dev/install.ps1 | iex
```

### For Existing OpenClaw Users

If you already have OpenClaw installed:

```bash
clawhub install ohmyopenclaw
```

Or ask the AI: "Install ohmyopenclaw skill"

## First-Time Setup

After installation, the AI will remind you about next steps when you first chat with OpenClaw:

1. Install this skill via ClawHub
2. Choose and apply a setup guide
3. Configure additional channels if needed

## How Guides Work

Each guide is a Markdown document that the AI can read and execute. The guide contains:

- **适用场景**: When to use this guide
- **配置变更**: What changes will be made
- **安装命令**: Commands to execute
- **验证步骤**: How to verify success

The AI will:
1. Read the guide content
2. Ask for any required parameters
3. Execute the configuration changes
4. Verify the setup is working
5. Update your workspace files

## Guide Priority

We recommend applying guides in this order:

1. **agent-swarm** - Foundation for multi-agent architecture
2. **memory-optimized** - Enhance memory capabilities
3. **monitor** - Enable proactive task discovery
4. **chinese-providers** or **cost-optimization** - Based on your needs

## Contributing

Found an issue or want to improve a guide?

- GitHub: https://github.com/ohmyopenclaw/ohmyopenclaw
- Issues: https://github.com/ohmyopenclaw/ohmyopenclaw/issues

## License

MIT License - see [LICENSE](../../LICENSE) for details.
