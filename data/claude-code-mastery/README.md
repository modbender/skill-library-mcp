# Claude Code Mastery 🧑‍💻

A comprehensive skill for mastering Claude Code with setup scripts, dev team subagents, and automated maintenance.

## Why This Skill?

Claude Code is powerful on its own. This skill adds:
- **Specialized subagents** — Route tasks to experts (frontend, backend, PM, etc.)
- **Structured setup** — Scripts that handle installation correctly
- **Self-improvement** — Heartbeat tasks that keep you learning
- **Best practices** — Docs on context management, workflows, pro tips

## Quick Install

```bash
cd ~/clawd/skills/claude-code-mastery/scripts

# Run setup scripts in order
./01-check-dependencies.sh
./02-install-claude-code.sh
./03-first-time-auth.sh
./04-install-subagents.sh           # Starter pack (3 agents) - recommended
./04-install-subagents.sh --full-team  # All 11 agents
./05-setup-claude-mem.sh            # Optional - prompts y/N (default: No)
```

## What's Included

### 🤖 Dev Team Subagents

**Starter Pack (default):**
| Agent | Purpose |
|-------|---------|
| senior-dev | Architecture, complex code, code review |
| project-manager | Task breakdown, timelines, dependencies |
| junior-dev | Quick fixes, simple tasks (fast & cheap) |

**Full Team (`--full-team`):**
| Agent | Purpose |
|-------|---------|
| frontend-dev | React, UI, CSS, client-side |
| backend-dev | APIs, databases, server-side |
| ai-engineer | LLM apps, RAG, prompts, agents |
| ml-engineer | ML models, training, MLOps |
| data-scientist | SQL, analysis, statistics |
| data-engineer | Pipelines, ETL, data infrastructure |
| product-manager | Requirements, user stories, prioritization |
| devops | CI/CD, Docker, K8s, infrastructure, automation |

Each agent includes a **"Learn More"** section with curated links to official docs, tutorials, and best practices.

### 📜 Scripts

| Script | Purpose |
|--------|---------|
| `01-check-dependencies.sh` | Verify system requirements |
| `02-install-claude-code.sh` | Install Claude Code CLI |
| `03-first-time-auth.sh` | Authenticate (browser or API key) |
| `04-install-subagents.sh` | Install subagents (`--minimal` or `--full-team`) |
| `05-setup-claude-mem.sh` | Persistent memory (optional, prompts y/N) |
| `06-diagnostics.sh` | Health check and status report |
| `07-weekly-improvement-cron.sh` | Generate improvement report |
| `08-troubleshoot.sh` | Comprehensive troubleshooting |
| `uninstall.sh` | Clean removal of all components |

### 📚 Documentation

- **SKILL.md** - Complete usage guide
- **docs/best-practices.md** - Context management, verification tips
- **docs/commands.md** - CLI and slash command reference
- **docs/workflows.md** - Real-world workflow examples
- **docs/tips-and-tricks.md** - 30 pro tips from heavy users
- **docs/troubleshooting.md** - Common issues and fixes

### ⚙️ Configuration

Edit `config.sh` to customize:
- `VALID_MODELS` — Add new models as Anthropic releases them
- `HEARTBEAT_DIAGNOSTICS` — Enable/disable in heartbeat
- `INSTALL_MODE` — Default starter vs full team

## Usage

After setup, use Claude Code with your dev team:

```bash
claude

> Use the senior-dev agent to review this code
> Have project-manager create a timeline for this feature
> Ask junior-dev to fix this typo
```

## Self-Improvement

This skill is designed to improve over time. The heartbeat task includes:
- Weekly learning rotation through agent expertise areas
- Instructions to update skill files with new discoveries
- Broken link fixes and best practice updates

Each Clawdbot using this skill can contribute improvements back!

## License

MIT License - See [LICENSE](LICENSE)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
