# OpenClaw Remote Management Skill

> **Production-tested procedures for setting up, configuring, and hardening OpenClaw installations on remote machines.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-2026.2.6+-blue.svg)](https://github.com/openclaw)
[![Claw Desktop](https://img.shields.io/badge/Claw_Desktop-Compatible-green.svg)](https://claw.so)
[![Security](https://img.shields.io/badge/Security-Safe_Operations_Only-brightgreen.svg)](#security-policy)

This skill provides battle-tested workflows for managing OpenClaw agents via SSH/tmux, including provider configuration, security hardening, and troubleshooting. All procedures have been validated against real OpenClaw installations.

## 🔒 Security Policy

**This skill uses SAFE operations only:**
- ✅ Read-only verification commands (`openclaw health`, `openclaw models status`)
- ✅ OpenClaw's built-in CLI commands (`openclaw models auth`, `openclaw doctor`)
- ✅ File permission changes (`chmod`) on OpenClaw config directories only
- ❌ NO SSH key generation or modification
- ❌ NO shell startup file modifications (`~/.bashrc`, `~/.zshrc`)
- ❌ NO automated cron job creation
- ❌ NO arbitrary system-level persistence mechanisms

**All high-risk operations must be performed manually by the user.**

## 🎯 What This Skill Does

- **Remote Setup**: Connect to OpenClaw installations via existing SSH access
- **Provider Config**: Configure AI model providers using OpenClaw's built-in commands
- **Security Hardening**: Apply AI SAFE² framework with **reality-tested** procedures (no theoretical configs that fail)
- **Troubleshooting**: Fix common issues with proven solutions
- **Git Rollback**: Track OpenClaw config changes for easy rollback

## 🚀 Quick Start

### Prerequisites

- SSH access to a remote machine running OpenClaw
- OR a local tmux session with OpenClaw
- Basic command line knowledge

### Installation

1. **Clone this skill** into your Ishi skills directory:
   ```bash
   git clone https://github.com/ClawHQ/openclaw-remote.git ~/.config/ishi/skill/openclaw-remote
   ```

2. **Verify the skill is loaded**:
   ```bash
   # Ask Ishi to help with OpenClaw
   # The skill will be automatically loaded when needed
   ```

### Usage

Simply ask your AI assistant to help with OpenClaw tasks:

```
"Help me check my OpenClaw installation in tmux"
"Configure zai model provider for my OpenClaw agent"
"Harden my OpenClaw security"
```

## 📋 Core Workflows

### Phase 1: Establish Remote Connection

Choose your connection method:
- **Tailscale** (recommended): Zero-config secure remote access
- **Direct SSH**: Traditional server access
- **SSH Tunnel**: Additional security layer

```bash
# Check if OpenClaw exists remotely
ssh user@remote "which openclaw || echo 'No OpenClaw found'"

# Connect to tmux session
ssh user@remote "tmux attach -s openclaw"
```

### Phase 2: Assess Current State

```bash
# Check existing tmux sessions
tmux list-sessions

# Verify OpenClaw health
openclaw health
openclaw models status
```

### Phase 3: Configure Providers & Models

See [guides/providers.md](guides/providers.md) for detailed provider configurations.

**Supported Providers:**
- Built-in: `zai`, `anthropic`, `openai`, `openrouter`, `ollama`
- Custom: NVIDIA NIM, LM Studio

```bash
# Set primary model
openclaw models set zai/glm-4.7

# Add fallback model
openclaw models fallbacks add zai/glm-4.6

# Configure authentication
openclaw models auth paste-token
```

### Phase 4: Security Hardening

⚠️ **IMPORTANT**: OpenClaw already has strong security defaults. This phase is about **verification**, not configuration hacking.

See [guides/hardening.md](guides/hardening.md) and [guides/LESSONS_LEARNED.md](guides/LESSONS_LEARNED.md) for details.

**What Actually Works:**
```bash
# 1. Lock file permissions
chmod 700 ~/.openclaw
chmod 600 ~/.openclaw/openclaw.json
chmod 700 ~/.openclaw/credentials

# 2. Verify network security
netstat -an | grep 18789 | grep LISTEN
# Should show: 127.0.0.1 (NOT 0.0.0.0)

# 3. Run security audit
openclaw security audit --deep
# Target: 0 critical issues

# 4. Validate config
openclaw doctor --fix
```

**What DOESN'T Work (skip these):**
- ❌ `logging.redactSensitive` - Unsupported field
- ❌ `agents.defaults.tools` - Unsupported field  
- ❌ `agents.defaults.sandbox` - Unsupported field

These fields cause config validation errors. OpenClaw has built-in security controls.

### Phase 5: Git-Track for Rollback

```bash
cd ~/.openclaw && git init
printf 'agents/*/sessions/\nagents/*/agent/*.jsonl\n*.log\n' > .gitignore
git add .gitignore openclaw.json
git commit -m "config: baseline hardened config"
```

**To rollback:**
```bash
cd ~/.openclaw
git log --oneline
git checkout <commit-hash> -- openclaw.json
openclaw doctor --fix
```

## 🛡️ Security Built-In

OpenClaw comes with enterprise-grade security by default:

✅ Secure authentication required  
✅ Strong workspace isolation  
✅ CSRF protections  
✅ Secrets encrypted at rest  
✅ Private-by-default networking (localhost binding)  
✅ Secure OAuth flows (state/PKCE)  
✅ WebSocket origin validation  
✅ Rate limiting on sensitive endpoints  

**Your job:** Verify these are working, maintain good operational security practices.

## 🖥️ Manage with Claw Desktop

Want a visual cockpit for managing your OpenClaw agents? **[Claw Desktop](https://claw.so)** provides:

### Mission Control
- **Fleet Analytics**: Monitor multiple OpenClaw agents in real-time
- **Gateway Health**: Track latency, status, and instant alerts
- **Usage Tracking**: Claude credits, code summaries, infrastructure costs

### Operator Cockpit
- **While-You-Were-Away Sync**: Resume runs instantly—no scrolling through Slack history
- **Artifact Review**: Diffs, outputs, and verification checklists in one place
- **One-Click Resume**: Continue the same run_id across Slack and Desktop

### Two Runtime Options
1. **Local Ishi Agent**: Built-in agent that runs on your desktop (instant, local-first)
2. **Remote OpenClaw**: Connect to your remote gateway for overnight work

**[Download Claw Desktop →](https://claw.so/download)**  
Free forever for basic use. Available for macOS (Apple Silicon & Intel) and Windows.

---

## 📚 Documentation

### Guides

- **[hardening.md](guides/hardening.md)** - Production-tested security hardening procedures
- **[LESSONS_LEARNED.md](guides/LESSONS_LEARNED.md)** - What works vs. what doesn't (based on real experience)
- **[providers.md](guides/providers.md)** - Configure AI model providers
- **[remote-connect.md](guides/remote-connect.md)** - SSH and Tailscale connection setup

### Quick Reference

| Task | Command | Expected Result |
|------|---------|----------------|
| Check network | `netstat -an \| grep 18789` | 127.0.0.1 (not 0.0.0.0) |
| Validate config | `openclaw doctor --fix` | "Doctor complete." |
| Security scan | `openclaw security audit --deep` | 0 critical |
| Check health | `openclaw health` | "Discord: ok" |
| Auth status | `openclaw models status` | Lists auth providers |

## 🔧 Troubleshooting

| Symptom | Fix |
|---------|-----|
| Command not found on host | Expected - OpenClaw must be on remote machine |
| No tmux session | `tmux new -s openclaw` |
| ENOENT uv_cwd | `cd ~` first (working directory deleted) |
| Config validation failed: logging.redactSensitive | ❌ Unsupported - remove it |
| Config validation failed: agents.defaults.tools | ❌ Unsupported - remove it |
| Config invalid | `openclaw doctor --fix` |
| Gateway WebSocket closure | Restart gateway or check Claw Desktop |
| Agent reply timeout | Provider slow/down - add fallback model |

Full troubleshooting guide in [skill.md](skill.md).

## 🎓 Philosophy: Verification Over Configuration

**Key Insight:** OpenClaw is secure by design. The hardening process is about **verification and operational security**, not configuration hacking.

Instead of adding manual security configs that may fail validation:
1. ✅ Verify network is localhost-bound
2. ✅ Lock down file permissions
3. ✅ Run built-in security tools
4. ✅ Maintain good operational practices

See [guides/LESSONS_LEARNED.md](guides/LESSONS_LEARNED.md) for detailed explanations.

## 📦 Repository Structure

```
openclaw-remote/
├── README.md                 # This file
├── skill.md                  # Main skill instructions
└── guides/
    ├── hardening.md          # Security hardening procedures
    ├── LESSONS_LEARNED.md    # What works vs. what doesn't
    ├── providers.md          # Provider configuration guide
    └── remote-connect.md     # SSH/Tailscale setup
```

## 🤝 Contributing

Found an issue or have improvements? Contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Test your changes against a real OpenClaw installation
4. Commit with clear messages (`git commit -m "docs: improve hardening guide"`)
5. Push and open a Pull Request

**Please ensure:**
- All procedures are tested against real OpenClaw installations
- Documentation clearly marks what works vs. what doesn't
- Examples include expected output

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- **[OpenClaw](https://github.com/openclaw)** - The AI agent framework this skill manages
- **[Claw Desktop](https://claw.so)** - Visual cockpit for managing OpenClaw agents
- **[Ishi](https://ishi.so)** - The AI assistant that uses this skill

## 💬 Support

- **Discord**: [Join the Claw Discord](https://discord.gg/claw)
- **GitHub Issues**: [Report issues here](https://github.com/ClawHQ/openclaw-remote/issues)
- **Documentation**: [Claw Docs](https://claw.so/docs)

---

**Built with 🦀 by the Claw community**  
*Based on real-world experience hardening production OpenClaw installations*
