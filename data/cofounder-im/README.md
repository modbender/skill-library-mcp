# CoFounder.im Skill for AI Coding Agents

[![Publish to ClawHub](https://github.com/cofounder-im/openclaw-cofounder-skill/actions/workflows/publish.yml/badge.svg)](https://github.com/cofounder-im/openclaw-cofounder-skill/actions/workflows/publish.yml)
[![ClawHub](https://img.shields.io/badge/ClawHub-cofounder--im-blue?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHRleHQgeT0iMjAiIGZvbnQtc2l6ZT0iMjAiPvCfmoA8L3RleHQ+PC9zdmc+)](https://clawhub.ai/alexfilatov/cofounder-im)
[![skills.sh](https://img.shields.io/badge/skills.sh-cofounder--im-8A2BE2)](https://skills.sh/cofounder-im/openclaw-cofounder-skill/cofounder-im)
[![Install](https://img.shields.io/badge/npx_skills_add-cofounder--im-green)](https://github.com/cofounder-im/openclaw-cofounder-skill)

An [Agent Skill](https://agentskills.io) that connects to [CoFounder.im](https://cofounder.im) to pull AI-validated startup projects and autonomously build them. Works with **Claude Code, OpenClaw, Cursor, Codex CLI, Gemini CLI, Windsurf, Cline, Copilot**, and [35+ other agents](https://skills.sh).

## What it does

CoFounder.im runs 20+ AI agents that validate your startup idea:

- Market research & competitor analysis
- MVP planning & tech stack recommendation
- UI/UX design system
- Implementation plan for coding assistants
- **OpenClaw Builder** — a multi-agent build specification designed for OpenClaw

This skill lets OpenClaw fetch those results via REST API and execute the build plan by spawning coordinated sub-agents.

## Setup

### 1. Get your API token

1. Sign up at [cofounder.im](https://cofounder.im)
2. Create a project and run the AI agents (wait for all to complete)
3. Go to [Settings](https://cofounder.im/users/settings) and generate an API token

### 2. Install the skill

**Any agent** (Claude Code, Cursor, Codex, Gemini CLI, Windsurf, Cline, etc.):

```bash
npx skills add cofounder-im/openclaw-cofounder-skill
```

**OpenClaw** (via [ClawHub](https://clawhub.ai/alexfilatov/cofounder-im)):

```bash
npx clawhub install cofounder-im
```

### 3. Configure your API token

Set the `COFOUNDER_API_TOKEN` environment variable for your agent. For OpenClaw:

```bash
openclaw config set skills.entries.cofounder-im.env.COFOUNDER_API_TOKEN "cfr_your_token_here"
openclaw gateway restart
```

For other agents, set it as an environment variable:

```bash
export COFOUNDER_API_TOKEN="cfr_your_token_here"
```

### 4. Verify the installation

For OpenClaw:
```bash
openclaw skills info cofounder-im
```

## Usage

Once installed, ask OpenClaw:

> "List my CoFounder.im projects"

> "Build my FreelancerInvoice project from CoFounder.im"

> "Pull the build spec for my latest CoFounder.im project and start building"

OpenClaw will:
1. Fetch your projects via the API
2. Let you pick which one to build
3. Pull the full build specification
4. Parse the OpenClaw Builder output into sub-agent tasks
5. Spawn sub-agents to build each component
6. Coordinate phases until the project is complete

## API endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/projects` | List your projects |
| `GET /api/v1/projects/:id/build-spec` | Get project + all agent outputs |

Authentication via `Authorization: Bearer cfr_...` header.

## How it works

```
CoFounder.im                          OpenClaw
┌─────────────────────┐               ┌──────────────────────┐
│                     │               │                      │
│  20+ AI Agents      │  REST API     │  CoFounder Skill     │
│  ├─ Market Research │◄─────────────►│  ├─ List projects    │
│  ├─ MVP Planner     │               │  ├─ Fetch build spec │
│  ├─ UI/UX Design    │               │  └─ Parse & execute  │
│  ├─ Tech Stack      │               │                      │
│  ├─ Impl Plan       │               │  Sub-Agents          │
│  └─ OpenClaw Builder│               │  ├─ Backend dev      │
│                     │               │  ├─ Frontend dev     │
│  Build Spec ────────┼──────────────►│  ├─ Database setup   │
│                     │               │  ├─ Testing          │
└─────────────────────┘               │  └─ DevOps           │
                                      └──────────────────────┘
```

## Requirements

- `curl` and `jq` must be installed
- `COFOUNDER_API_TOKEN` environment variable must be set

## License

MIT
