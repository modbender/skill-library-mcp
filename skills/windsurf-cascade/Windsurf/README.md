# Windsurf Cascade Agent Skill

This repository contains the definition and documentation for the `windsurf-cascade` skill, updated for 2026 features.

## Overview

The `windsurf-cascade` skill encapsulates workflows and commands for the Windsurf IDE and its Cascade AI agent, enabling efficient AI-pair programming with deep codebase awareness. This skill includes all modern features from the Wave 13 update (January 2026).

## What's New in v1.0.0

- **Cascade Agent**: Agentic AI assistant with Write/Chat modes, tool calling, voice input, and real-time awareness
- **Skills System**: Bundle instructions, templates, and supporting files for Cascade to invoke on complex tasks
- **Workflows**: Reusable markdown-based step sequences invoked via `/workflow-name` slash commands
- **Memories & Rules**: Auto-generated memories and user-defined rules at global, workspace, and system levels
- **MCP Integration**: Connect custom tools and services (GitHub, Slack, Stripe, Figma, databases) via MCP servers
- **Model Flexibility**: Switch between SWE-1.5, Claude, GPT-5.x, Gemini 3, and BYOK models
- **Parallel Sessions**: Run multiple Cascade sessions simultaneously with Git worktrees support
- **Dedicated Terminal**: Reliable zsh shell for agent command execution
- **Turbo Mode**: Auto-execute terminal commands without manual confirmation
- **Fast Context**: SWE-grep powered code retrieval up to 20x faster

## Contents

- **SKILL.md**: The core skill definition file containing all features, workflows, and usage instructions
- **README.md**: This file, providing an overview and quick reference

## Quick Start

Download and install Windsurf:
- **macOS / Windows / Linux**: Download from [windsurf.com](https://windsurf.com)
- Optionally install `windsurf` in PATH for CLI access

Open Cascade:
```
Cmd+L (Mac) / Ctrl+L (Windows/Linux)
```

Switch between Write and Chat modes:
```
Cmd+Shift+L (Mac) / Ctrl+Shift+L (Windows/Linux)
```

Open Command Palette:
```
Cmd+Shift+P (Mac) / Ctrl+Shift+P (Windows/Linux)
```

## Usage

Refer to `SKILL.md` for comprehensive instructions on:
- Installation and setup (macOS, Windows, Linux, WSL)
- Cascade Write and Chat modes
- Skills, Workflows, Memories, and Rules configuration
- MCP server management
- Model selection and switching
- Terminal integration and Turbo Mode
- Keyboard shortcuts and @ mentions
- Code review, refactoring, debugging, and deployment workflows
