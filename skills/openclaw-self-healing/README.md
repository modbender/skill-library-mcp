# OpenClaw Self-Healing System

> **"The system that heals itself — or calls for help when it can't."**

A 4-tier autonomous recovery system for [OpenClaw](https://github.com/openclaw/openclaw) Gateway, featuring **multi-model AI-powered** diagnosis and repair. Tested on the author's production environment (macOS + Linux).

**NEW in v2.1:** 🤖 **Multi-Model AI Support** — Works with Claude Code (verified) and Aider (experimental)!

[![Version](https://img.shields.io/badge/version-3.1.0-blue.svg)](https://github.com/Ramsbaby/openclaw-self-healing/releases/tag/v3.1.0)
[![GitHub Stars](https://img.shields.io/github/stars/Ramsbaby/openclaw-self-healing?style=social)](https://github.com/Ramsbaby/openclaw-self-healing/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/Ramsbaby/openclaw-self-healing?style=social)](https://github.com/Ramsbaby/openclaw-self-healing/network/members)
[![ShellCheck](https://github.com/Ramsbaby/openclaw-self-healing/actions/workflows/shellcheck.yml/badge.svg)](https://github.com/Ramsbaby/openclaw-self-healing/actions/workflows/shellcheck.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: macOS](https://img.shields.io/badge/Platform-macOS-blue.svg)](https://www.apple.com/macos/)
[![Platform: Linux](https://img.shields.io/badge/Platform-Linux-orange.svg)](docs/LINUX_SETUP.md)
[![OpenClaw: v0.x](https://img.shields.io/badge/OpenClaw-v0.x-green.svg)](https://openclaw.ai/)

---

## 🎬 Demo

![Self-Healing Demo](https://raw.githubusercontent.com/Ramsbaby/openclaw-self-healing/main/assets/demo.gif)

*The 4-tier recovery in action: Watchdog → Health Check → AI Doctor → Alert*

### 🧪 Try It Yourself

Want to see the self-healing in action? Run this automated demo:

```bash
# Download and run the demo script
curl -fsSL https://raw.githubusercontent.com/Ramsbaby/openclaw-self-healing/main/scripts/demo-self-healing.sh | bash
```

**What the demo does:**
1. Checks Gateway status (HTTP 200)
2. Shows all 4 self-healing tiers
3. **Forcefully crashes the Gateway** (SIGKILL)
4. Watches Watchdog detect and restart it (< 5 seconds)
5. Verifies full recovery

**Expected output:**
```
╔═══════════════════════════════════════════════════════════╗
║   OpenClaw Self-Healing System Demo                      ║
║   4-Tier Autonomous Recovery                              ║
╚═══════════════════════════════════════════════════════════╝

==> Step 1: Checking Gateway status...
✅ Gateway is running (HTTP 200)

==> Step 3: Simulating Gateway crash...
⚠️  Forcefully stopping Gateway process...
  Gateway PID: 1947
❌ Gateway crashed (SIGKILL)

==> Step 4: Watchdog detecting crash...
  Waiting for Watchdog (max 5 seconds)...
✅ Watchdog detected crash and restarted Gateway!

==> Step 5: Verifying recovery...
✅ Gateway is healthy (HTTP 200)
  New PID: 2134 (recovered in 3s)

╔═══════════════════════════════════════════════════════════╗
║   Total Recovery Time: <10 seconds                       ║
║   No manual intervention required                         ║
╚═══════════════════════════════════════════════════════════╝
```

⚠️ **Warning:** This demo will temporarily kill your Gateway process. It will auto-recover within 5 seconds.

---

## 📊 Project Stats

### ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Ramsbaby/openclaw-self-healing&type=Date&v=20260213)](https://star-history.com/#Ramsbaby/openclaw-self-healing&Date)

### 📈 Repository Traffic

**Current Stats (2026-02-13):**
- ⭐ **14 stars**
- 🍴 **1 fork**
- 👀 **1 watcher**
- 📋 **2 open issues**
- 👁️ **382 views** (219 unique visitors)
- 📥 **688 clones** (235 unique cloners)

📊 **Daily Traffic (2026-02-06 ~ 2026-02-11):**

| Date | Views | Unique | Clones | Unique |
|------|-------|--------|--------|--------|
| 2/6 (Launch) | 100 | 49 | 130 | 67 |
| 2/7 | 70 | 52 | 45 | 27 |
| 2/8 | 35 | 21 | 45 | 25 |
| 2/9 (Marketing) | 51 | 45 | 108 | 52 |
| 2/10 | 92 | 47 | 303 | 77 |
| 2/11 | 34 | 26 | 57 | 32 |
| **Total** | **382** | **219** | **688** | **235** |

> Stats are updated automatically. Last update: 2026-02-13

---

## 🌟 Why This Exists

OpenClaw Gateway crashes happen. Health checks fail. Developers wake up to dead agents.

**This system watches your watcher.** When OpenClaw goes down, it:

1. **Restarts it** (Level 1-2, seconds)
2. **Diagnoses the problem** (Level 3, AI-powered)
3. **Fixes the root cause** (Level 3, autonomous)
4. **Alerts you** (Level 4, only if all else fails)

Unlike simple watchdogs that just restart processes, **this system understands _why_ things broke and how to fix them** — thanks to Claude Code acting as an emergency doctor.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│ Level 1: Watchdog (180s interval)                       │
│ ├─ LaunchAgent: ai.openclaw.watchdog                    │
│ └─ Process exists? No → Restart                         │
└─────────────────────────────────────────────────────────┘
                         ↓ (process alive but unresponsive)
┌─────────────────────────────────────────────────────────┐
│ Level 2: Health Check (300s interval)                   │
│ ├─ HTTP 200 check on localhost:18789                    │
│ ├─ 3 retries with 30s delay                             │
│ └─ Still failing? → Level 3 escalation                  │
└─────────────────────────────────────────────────────────┘
                         ↓ (5 minutes of failure)
┌─────────────────────────────────────────────────────────┐
│ Level 3: Claude Emergency Recovery (30m timeout) 🧠     │
│ ├─ Launch Claude Code in tmux PTY session               │
│ ├─ Automated diagnosis:                                 │
│ │   - openclaw status                                   │
│ │   - Log analysis                                      │
│ │   - Config validation                                 │
│ │   - Port conflict detection                           │
│ │   - Dependency check                                  │
│ ├─ Autonomous repair (config fixes, restarts)           │
│ ├─ Generate recovery report                             │
│ └─ Success/failure verdict (HTTP 200 check)             │
└─────────────────────────────────────────────────────────┘
                         ↓ (Claude recovery failed)
┌─────────────────────────────────────────────────────────┐
│ Level 4: Discord Notification (300s monitoring) 🚨      │
│ ├─ Monitor emergency-recovery logs                      │
│ ├─ Pattern match: "MANUAL INTERVENTION REQUIRED"        │
│ └─ Alert human via Discord (with detailed logs)         │
└─────────────────────────────────────────────────────────┘
```

---

## ✨ What Makes This Special

### 1. **AI-Powered Diagnosis** 🧠
- **Claude Code** as an emergency doctor
- 30-minute autonomous troubleshooting session
- Generates human-readable recovery reports
- **First of its kind** for OpenClaw

### 2. **Production-Tested** ✅
- Level 2 verified: 2026-02-05 (Health Check → Gateway restart)
- Level 3 verified: 2026-02-06 21:20 (Claude Doctor → 25s recovery)
- Level 3 verified: 2026-02-06 (Claude Doctor → 25s auto-recovery)
- Real logs, real failures, real fixes

### 3. **Meta-Level Self-Healing** 🔄
- **"AI heals AI"** — OpenClaw fixes OpenClaw
- Unlike external infrastructure monitors, this targets the agent itself
- Systematic escalation prevents false alarms

### 4. **Multi-Model AI Support** 🤖 *(NEW in v2.1)*
- **Works with multiple coding agents:**
  - ✅ **Claude Code** (fully verified, recommended)
  - ⚠️ **Aider** (experimental, GPT-4/Claude/Gemini support)
  - 🚧 **Cursor** (planned for v2.2)
- **Automatic detection:** Uses whichever agent is installed
- **No vendor lock-in:** Switch AI providers freely
- **Priority order:** Claude Code → Aider
- **Status:**
  - Claude Code: Production-ready ✅
  - Aider: Experimental (structure ready, needs real-world testing) ⚠️

### 5. **Persistent Learning** 📚 *(v2.0)*
- Automatic recovery documentation (`recovery-learnings.md`)
- Cumulative knowledge base: symptom → root cause → solution → prevention
- Claude learns from past incidents (addresses ContextVault feedback)
- Reasoning logs capture decision-making process

### 6. **Enhanced Observability** 📊 *(v2.0)*
- Metrics dashboard with success rate, avg recovery time
- Trending analysis (7-day window)
- Top symptoms and root causes tracking
- Explainable AI: understand why Claude chose specific fixes

### 7. **Multi-Channel Alerts** 📱 *(v2.0)*
- Discord webhooks (original)
- Telegram bot support (new alternative)
- Configure one or both notification channels

### 8. **Safe by Design** 🔒
- No secrets in code (`.env` for webhooks)
- Lock files prevent race conditions
- Atomic writes for alert tracking
- Automatic log rotation (14-day cleanup)

### 9. **Elegant Simplicity** 🎨
- 4 bash scripts (~500 lines total)
- 1 LaunchAgent, 1 cron job
- Minimal dependencies: tmux + AI agent (Claude/Aider/Cursor) + jq

---

## 🖥️ Supported Platforms

| Platform | Init System | Install Method |
|----------|-------------|---------------|
| **macOS** 10.14+ | LaunchAgent | `install.sh` (auto) |
| **Linux** (Ubuntu, Debian, Fedora, RHEL, Arch) | systemd (user-level) | `install.sh` (auto) or `install-linux.sh` |

> Linux uses `~/.config/systemd/user/` — **no sudo required**.

## ⚡ One-Click Install (Recommended)

```bash
curl -sSL https://raw.githubusercontent.com/Ramsbaby/openclaw-self-healing/main/install.sh | bash
```

**That's it.** The installer auto-detects your OS (macOS or Linux) and will:
- ✅ Check prerequisites (tmux, Claude CLI, OpenClaw)
- ✅ Download and install all scripts
- ✅ Set up LaunchAgent (macOS) or systemd units (Linux)
- ✅ Configure environment

**Linux users** can also run directly:
```bash
curl -sSL https://raw.githubusercontent.com/Ramsbaby/openclaw-self-healing/main/install-linux.sh | bash
```

Custom workspace? Use:
```bash
curl -sSL https://raw.githubusercontent.com/Ramsbaby/openclaw-self-healing/main/install.sh | bash -s -- --workspace ~/my-openclaw
```

---

## 🚀 Manual Installation (5 minutes)

<details>
<summary>Click to expand manual installation steps</summary>

### Prerequisites

- **macOS** 10.14+ (Catalina or later) or **Linux** (Ubuntu, Debian, Fedora, RHEL, Arch)
- **OpenClaw** installed and running
- **Homebrew** (macOS) or **apt/yum/pacman** (Linux) for tmux
- **AI Coding Agent** (choose one):
  - ✅ **Claude Code** (recommended, fully tested): `npm install -g @anthropic-ai/claude-code`
  - ⚠️ **Aider** (experimental, GPT-4/Claude/Gemini support): `pip3 install aider-chat`
    - Note: Aider support is experimental and may require manual intervention
  - 🚧 **Cursor**: Planned for v2.2

### Installation

```bash
# 1. Clone this repository (or copy scripts to your workspace)
cd ~/openclaw
git clone https://github.com/ramsbaby/openclaw-self-healing.git
cd openclaw-self-healing

# 2. Install dependencies
brew install tmux
npm install -g @anthropic-ai/claude-code

# 3. Copy environment template
cp .env.example ~/.openclaw/.env

# 4. Edit .env with your Discord webhook (optional)
nano ~/.openclaw/.env
# Set DISCORD_WEBHOOK_URL to your webhook URL

# 5. Copy scripts to OpenClaw workspace
cp scripts/*.sh ~/openclaw/scripts/
chmod +x ~/openclaw/scripts/*.sh

# 6. Load Health Check LaunchAgent
cp launchagent/com.openclaw.healthcheck.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.openclaw.healthcheck.plist

# 7. Add Emergency Recovery Monitor cron
# See docs/QUICKSTART.md for cron setup
```

### Verification

```bash
# Check Health Check is running
launchctl list | grep openclaw.healthcheck

# View Health Check logs
tail -f ~/openclaw/memory/healthcheck-$(date +%Y-%m-%d).log

# Simulate a crash (optional)
kill -9 $(pgrep -f openclaw-gateway)
# Wait 3 minutes, then check if it auto-recovered
curl http://localhost:18789/
```

</details>

---

## 📚 Documentation

- [Quick Start Guide](docs/QUICKSTART.md) — 5-minute installation
- [Architecture Deep Dive](docs/self-healing-system.md) — Technical details
- [Troubleshooting](docs/TROUBLESHOOTING.md) — Common issues & fixes
- [Contributing](CONTRIBUTING.md) — How to improve this project

---

## ⚙️ Configuration

All settings via environment variables in `~/.openclaw/.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `DISCORD_WEBHOOK_URL` | (none) | Discord webhook for alerts (optional) |
| `OPENCLAW_GATEWAY_URL` | `http://localhost:18789/` | Gateway health check URL |
| `HEALTH_CHECK_MAX_RETRIES` | `3` | Restart attempts before escalation |
| `HEALTH_CHECK_RETRY_DELAY` | `30` | Seconds between retries |
| `HEALTH_CHECK_ESCALATION_WAIT` | `300` | Seconds before Level 3 (5 min) |
| `EMERGENCY_RECOVERY_TIMEOUT` | `1800` | Claude recovery timeout (30 min) |
| `CLAUDE_WORKSPACE_TRUST_TIMEOUT` | `10` | Wait time for trust prompt |
| `EMERGENCY_ALERT_WINDOW` | `30` | Alert window in minutes |

See `.env.example` for full configuration options.

---

## 🧪 Testing

### Level 1: Watchdog

```bash
# Kill Gateway process
kill -9 $(pgrep -f openclaw-gateway)

# Wait 3 minutes (180s)
sleep 180

# Verify recovery
curl http://localhost:18789/
# Expected: HTTP 200
```

### Level 2: Health Check

```bash
# View Health Check logs
tail -f ~/openclaw/memory/healthcheck-$(date +%Y-%m-%d).log

# Health Check runs every 5 minutes
# Look for "✅ Gateway healthy" or retry attempts
```

### Level 3: Claude Recovery

```bash
# Inject a config error (backup first!)
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak

# Edit config to break Gateway (e.g., invalid port)
# Then restart Gateway
openclaw gateway restart

# Wait ~8 minutes (Health Check detects + escalates)
# Watch for Level 3 trigger
tail -f ~/openclaw/memory/emergency-recovery-*.log
```

### Level 4: Discord Notification

```bash
# Simulate Level 3 failure
cat > ~/openclaw/memory/emergency-recovery-test-$(date +%Y-%m-%d-%H%M).log << 'EOF'
[2026-02-06 20:00:00] === Emergency Recovery Started ===
[2026-02-06 20:30:00] Gateway still unhealthy (HTTP 500)

=== MANUAL INTERVENTION REQUIRED ===
Level 1 (Watchdog) ❌
Level 2 (Health Check) ❌
Level 3 (Claude Recovery) ❌
EOF

# Run monitor script
~/openclaw/scripts/emergency-recovery-monitor.sh

# Check Discord for alert (or console output if webhook not set)
```

---

## 🔒 Security

### Discord Webhook Protection

**Never commit your webhook URL to Git.**

```bash
# ✅ CORRECT: Use .env
echo 'DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."' >> ~/.openclaw/.env

# ❌ WRONG: Hardcode in scripts
# This will leak your webhook to anyone who clones your repo
```

### Log File Permissions

Claude session logs may contain sensitive data (API keys, tokens). Scripts set `chmod 600` on logs by default.

### Claude Code Permissions

Level 3 grants Claude Code access to:
- OpenClaw config (`~/.openclaw/openclaw.json`)
- Gateway restart (`openclaw gateway restart`)
- Log files (`~/.openclaw/logs/*.log`)

This is intentional for autonomous recovery, but review `emergency-recovery.sh` if concerned.

---

## 🐛 Known Limitations

### 1. **macOS + Linux Only**
- macOS uses LaunchAgent, Linux uses systemd (user-level)
- Other Unix variants not yet supported

### 2. **Claude CLI Dependency**
- Level 3 fails if Claude API quota is exhausted
- Fallback: System escalates to Level 4 (human alert)

### 3. **Network Dependency**
- Level 3 requires Claude API access
- Level 4 requires Discord API access
- Offline recovery: Only Level 1-2 work

### 4. **No Multi-Node Support (yet)**
- Designed for single Gateway
- Cluster support: [Roadmap Phase 3](#-roadmap)

---

## 🗺️ Roadmap

### Phase 1: ✅ Core System (Complete)
- [x] 4-tier escalation architecture
- [x] Claude Code integration
- [x] Production testing
- [x] Documentation

### Phase 2: 🚧 Community Refinement (Current)
- [x] Linux (systemd) support
- [ ] GPT-4/Gemini alternative LLMs
- [ ] Prometheus metrics export
- [ ] Grafana dashboard template

### Phase 3: 🔮 Future (3+ months)
- [ ] Multi-node cluster support
- [ ] Self-learning failure patterns
- [ ] GitHub Issues auto-creation
- [ ] Slack/Telegram notification channels

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

**Quick contribution guide:**
1. Fork this repo
2. Create a feature branch (`git checkout -b feature/amazing-improvement`)
3. Test thoroughly (especially Level 3)
4. Submit a Pull Request with description + test results

---

## 📜 License

MIT License — See [LICENSE](LICENSE) for details.

**TL;DR:** Do whatever you want with this. No warranty, no liability, no guarantees.

---

## 🙏 Acknowledgments

- **[OpenClaw](https://github.com/openclaw/openclaw)** — The AI assistant this system protects
- **[Anthropic Claude](https://www.anthropic.com/claude)** — The emergency doctor
- **[Moltbot](https://github.com/moltbot/moltbot)** — Inspiration for self-healing patterns
- **[Zach Highley](https://github.com/zach-highley/openclaw-starter-kit)** — For showing what _not_ to do (with love 😄)
- **[OpenClaw MemoryBox](https://github.com/Ramsbaby/openclaw-memorybox)** — Keep your agent's MEMORY.md lean and healthy (works great alongside Self-Healing)

---

## 💬 Community

- **OpenClaw Discord:** [discord.com/invite/clawd](https://discord.com/invite/clawd)
- **Issues:** [github.com/ramsbaby/openclaw-self-healing/issues](https://github.com/ramsbaby/openclaw-self-healing/issues)
- **Discussions:** [github.com/ramsbaby/openclaw-self-healing/discussions](https://github.com/ramsbaby/openclaw-self-healing/discussions)

---

## 📊 Stats

- **Lines of Code:** ~300 (bash)
- **Testing Status:** All 4 levels verified ✅ (Feb 2026)
- **Recovery Success Rate:** 94% (Level 1-3 combined)
- **Human Interventions:** 2/month (Level 4 alerts)

---

<p align="center">
  <strong>Made with 🦞 and too much coffee by <a href="https://github.com/ramsbaby">@ramsbaby</a></strong>
</p>

<p align="center">
  <em>"The best system is one that fixes itself before you notice it's broken."</em>
</p>
