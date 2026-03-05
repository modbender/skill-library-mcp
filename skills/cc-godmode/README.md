# 🚀 OpenClaw GodMode Skill

> **Self-Orchestrating Multi-Agent Development Workflows for Claude Code**
>
> *You say WHAT, the AI decides HOW.*

[![ClawHub](https://img.shields.io/badge/ClawHub-cc--godmode-blue)](https://clawhub.ai/skills/cc-godmode)
[![Version](https://img.shields.io/badge/version-5.11.1-green)](./CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-blue)](./LICENSE)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-compatible-orange)](https://openclaw.ai)
[![Claude Code](https://img.shields.io/badge/Claude_Code-required-purple)](https://claude.ai/code)

---

## ⚠️ Important: Requirements

### 🔧 Claude Code Required
This skill **requires [Claude Code](https://claude.ai/code)** (Anthropic's CLI agent). It will not work with the web interface or API alone.

### 💳 Paid Account Recommended
GodMode spawns multiple sub-agents that consume tokens quickly. We **strongly recommend**:

| Plan | Recommendation |
|------|----------------|
| Free | ❌ Not recommended (tokens exhaust very quickly) |
| Pro ($20/mo) | ✅ Good for smaller projects |
| **Max ($200/mo)** | ⭐ **Recommended** for heavy use |

The multi-agent orchestration is powerful but token-intensive. With a free account, you'll hit limits within minutes.

---

## 🔀 Two Versions of GodMode

### This Repo: OpenClaw GodMode Skill
**Optimized for [OpenClaw](https://openclaw.ai)** — the AI agent framework that extends Claude Code with messaging, cron jobs, and more.

- 📦 Installable via ClawHub
- 🔗 Integrates with OpenClaw's skill system
- 💬 Works with Telegram, WhatsApp, Discord channels
- ⏰ Can be triggered via cron jobs

### Original: [ClawdBot-GodMode](https://github.com/cubetribe/ClawdBot-GodMode)
**The standalone CLAUDE.md version** — perfect for server administration from your local machine.

- 🖥️ Ideal for managing VPS and remote servers
- 🔧 Great for administering machines running OpenClaw
- 📝 Documentation-first approach with excellent versioning
- 🚀 Battle-tested on multiple production servers

**Both repos are valuable** — choose based on your use case:
- Running OpenClaw? → Use this skill
- Managing servers via Claude Code locally? → Use the [original GodMode](https://github.com/cubetribe/ClawdBot-GodMode)

---

## ✨ What is GodMode?

GodMode transforms your **Claude Code** agent into a **multi-agent development orchestrator**. Instead of manually managing every step of development, you simply describe what you want — and a team of specialized AI agents figures out how to build it.

This isn't just another coding assistant. It's a complete **autonomous development workflow** that has been battle-tested over multiple weeks in real-world production projects.

### 🎯 The Magic

```
You: "Add user authentication with JWT and refresh tokens"

GodMode: *spawns @researcher to evaluate best practices*
         *@architect designs the system*
         *@builder implements it*
         *@validator + @tester run quality checks in parallel*
         *@scribe updates documentation*
         
Result: Production-ready feature with tests, docs, and proper architecture.
```

---

## 🤖 Meet the Team

GodMode orchestrates **8 specialized agents**, each with a specific role:

| Agent | Role | What They Do |
|-------|------|--------------|
| 🔬 **@researcher** | Knowledge Discovery | Web research, tech evaluation, best practices |
| 🏗️ **@architect** | System Design | Architecture decisions, ADRs, system design |
| 🛡️ **@api-guardian** | API Lifecycle | Breaking change detection, versioning |
| 👷 **@builder** | Implementation | Code writing, refactoring |
| ✅ **@validator** | Code Quality | TypeScript, linting, security checks |
| 🧪 **@tester** | UX Quality | E2E tests, visual regression, a11y |
| 📝 **@scribe** | Documentation | Changelog, README, API docs |
| 🐙 **@github-manager** | GitHub Ops | Issues, PRs, releases, CI/CD |

---

## 📦 Installation

### Via ClawHub (Recommended)

```bash
clawdhub install cc-godmode
```

### Manual Installation

```bash
# Clone this repository
git clone https://github.com/cubetribe/openclaw-godmode-skill.git

# Copy to your OpenClaw skills directory
cp -r openclaw-godmode-skill ~/.openclaw/skills/cc-godmode

# Or for Clawdbot:
cp -r openclaw-godmode-skill ~/.clawdbot/skills/cc-godmode

# Verify installation
ls ~/.openclaw/skills/cc-godmode/SKILL.md
```

---

## 🎮 Usage

Once installed, just describe what you want in natural language:

### New Feature
```
New Feature: Add user authentication with JWT
```

### Bug Fix
```
Bug Fix: Login form validation not working
```

### API Change
```
API Change: Add email field to User type
```

### Research Task
```
Research: Best practices for React state management 2025
```

### Release
```
Prepare Release
```

---

## 🔄 Workflows

GodMode automatically selects the right workflow based on your request:

### 🆕 New Feature (Full Pipeline)
```
You → @researcher* → @architect → @builder → [@validator + @tester] → @scribe
                                                   (parallel)
```

### 🐛 Bug Fix (Quick)
```
You → @builder → [@validator + @tester] → done
```

### ⚠️ API Change (Critical Path)
```
You → @architect → @api-guardian → @builder → [@validator + @tester] → @scribe
```

### 🔬 Research Only
```
You → @researcher → Report
```

*Agents marked with `*` are optional and context-dependent*

---

## 🏆 Why GodMode?

### Battle-Tested
This system has been developed and refined over **multiple weeks** of intensive real-world testing. It's not theoretical — it's proven to work on production projects.

### True Autonomy
Unlike simple prompt chains, GodMode agents make intelligent decisions about:
- Which agents to involve
- When to parallelize tasks
- How to handle failures and edge cases
- What quality gates to apply

### Documentation-First
Every change is documented. Every decision is recorded. The versioning and documentation workflow is **extremely reliable** — crucial for maintaining production systems.

### Dual Quality Gates
Every feature passes through **two independent quality checks** running in parallel — because catching bugs early saves hours of debugging later.

---

## ⚙️ Requirements

### Required
- **[Claude Code](https://claude.ai/code)** — Anthropic's CLI agent
- **Paid Claude Account** — Pro ($20) or Max ($200) recommended

### Required MCP Servers
- `playwright` — For @tester E2E testing
- `github` — For @github-manager operations

### Optional (Enhanced Features)
- `lighthouse` — Performance audits
- `a11y` — Accessibility testing
- `memory` — Context persistence across sessions

Check your MCP status:
```bash
openclaw mcp list
# or
claude mcp list
```

---

## 🔒 Security

This skill is **documentation-only** and contains no executable code:

- ✅ No bash scripts that run automatically
- ✅ No external API calls from the skill itself
- ✅ No file modifications without explicit agent action
- ✅ Full source transparency — read every line
- ✅ MIT licensed

All orchestration happens through your existing Claude Code agent using standard tool calls.

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [SKILL.md](./SKILL.md) | Main skill documentation (loaded by OpenClaw) |
| [docs/WORKFLOWS.md](./docs/WORKFLOWS.md) | Detailed workflow documentation |
| [docs/AGENTS.md](./docs/AGENTS.md) | Complete agent specifications |
| [docs/TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md) | FAQ and problem solving |
| [docs/MIGRATION.md](./docs/MIGRATION.md) | Migrating from CLAUDE.md |

---

## 🔗 Links

- **Original GodMode:** [ClawdBot-GodMode](https://github.com/cubetribe/ClawdBot-GodMode) — Standalone version for server administration
- **OpenClaw:** [openclaw.ai](https://openclaw.ai) — The AI agent framework
- **ClawHub:** [clawhub.ai](https://clawhub.ai) — Skill marketplace
- **Claude Code:** [claude.ai/code](https://claude.ai/code) — Anthropic's CLI agent

---

## 🤝 Contributing

Contributions are welcome! This project is open source and we'd love your help making it even better.

1. Fork this repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Test locally by copying to your skills directory
5. Submit a pull request

---

## 📄 License

MIT License — see [LICENSE](./LICENSE)

---

## 💬 A Note from the Creator

> I've been working on GodMode for weeks, testing it on real projects, refining the agent interactions, and optimizing the workflows. The results have been **sensational** — tasks that used to take hours now complete in minutes with higher quality.
>
> I use the original GodMode daily to manage multiple VPS and production servers. The documentation-first approach and reliable versioning make it a dream for server administration. This OpenClaw version brings the same power to the OpenClaw ecosystem.
>
> I'm sharing this with the open-source community because I believe this approach to AI-assisted development is the future. Try it, break it, improve it, and let's build something amazing together.
>
> **Pro tip:** Get the Max plan ($200/mo) if you're serious about multi-agent workflows. The token headroom makes all the difference.
>
> — Dennis @ [cubetribe](https://github.com/cubetribe)

---

**Built with 🚀 by humans and Claude Code working together**
