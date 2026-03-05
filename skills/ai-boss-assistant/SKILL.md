---
name: ai-boss-assistant
description: Transform any AI into a professional executive assistant with battle-tested personas and workflows. Complete templates for Google Workspace integration (Gmail, Calendar, Drive), milestone delivery system, and security guidelines.
homepage: https://github.com/jacky6658/ai-boss-assistant
metadata:
  {
    "openclaw":
      {
        "emoji": "💼",
        "requires": { "bins": ["node"] },
      },
  }
---

# AI Boss Assistant

> Transform any AI into a professional executive assistant with battle-tested personas and workflows.

## Overview

This skill provides complete templates to train an AI agent as your personal boss assistant. It includes:

- **Persona Framework**: Define how your AI thinks, communicates, and behaves
- **Milestone Delivery**: Break big tasks into manageable stages
- **Google Workspace Integration**: Gmail, Calendar, Drive automation
- **Security Guidelines**: Built-in privacy and permission rules

## Quick Usage

### Train Your AI

Ask the AI to read and learn from these files in order:

```
Please read and learn from:
1. agent-persona/PERSONA.md - Core personality
2. agent-persona/COMMUNICATION.md - How to communicate
3. agent-persona/WORKFLOW.md - Milestone delivery system
4. agent-persona/RULES.md - Behavioral rules
```

### Example Commands

After training, you can say:

```
"Check my calendar for tomorrow and summarize"
"Help me draft a reply to the latest email from [client]"
"Create a project plan for [task] with milestones"
"What's on my todo list today?"
```

## Key Concepts

### AI Employee vs Chatbot

This template creates an "AI Employee" that:
- ✅ Proactively executes tasks
- ✅ Provides complete solutions
- ✅ Has judgment and opinions
- ✅ Delivers results, not just answers

### Milestone Delivery

Big tasks are broken into stages:
```
Task → M1 → Deliver → OK → M2 → Deliver → OK → Done
```

This prevents "black box" operations and allows review at each stage.

### Externalized Memory

Important info is written to files:
- `MEMORY.md` - Long-term memory
- `memory/YYYY-MM-DD.md` - Daily logs

## Requirements

- OpenClaw 1.0+
- Node.js 18+
- Google Account (for Workspace integration)
- gog CLI (for Google Workspace)

## Installation

```bash
# Install gog for Google Workspace
npm install -g gog
gog auth login --services gmail,calendar,drive
```

## Files Structure

```
agent-persona/     - Core persona templates
setup/             - Installation guides  
examples/          - Conversation examples
security/          - Security guidelines
tasks/             - Task management templates
```

## Links

- **GitHub**: https://github.com/jacky6658/ai-boss-assistant
- **Documentation**: See README.md for full documentation
- **Issues**: https://github.com/jacky6658/ai-boss-assistant/issues
