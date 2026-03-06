# OpenClaw Workspace Pro

> **Production-ready workspace setup for long-running OpenClaw AI agents**

Transform your OpenClaw workspace from basic to production-ready in minutes. Implements battle-tested patterns for artifact management, secrets security, memory optimization, and continuous operation.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-2026.2.9%2B-blue)](https://openclaw.ai)
[![ClawHub](https://img.shields.io/badge/ClawHub-Published-green)](https://clawhub.ai/skills/openclaw-workspace-pro)

---

## 🎯 Why Workspace Pro?

**Default OpenClaw workspaces struggle with:**
- ❌ Files scattered across directories (no standardization)
- ❌ API keys exposed in plaintext (security vulnerability)
- ❌ Memory grows indefinitely (context limit crashes)
- ❌ No clear artifact handoff boundaries
- ❌ Manual maintenance prone to drift

**Workspace Pro solves this with:**
- ✅ **Artifact workflow** - Standardized output structure
- ✅ **Secrets management** - Secure .env pattern, git-safe
- ✅ **Memory compaction** - Systematic archival prevents bloat
- ✅ **Long-running patterns** - Container reuse, checkpointing
- ✅ **Security baseline** - Network allowlists, safe credentials

Based on [OpenAI's Shell + Skills + Compaction](https://developers.openai.com/blog/skills-shell-tips) recommendations and proven in production environments.

---

## 🚀 Quick Start

### Installation

**Via ClawHub (recommended):**
```bash
clawhub install openclaw-workspace-pro
```

**Manual:**
```bash
cd /data/.openclaw/workspace
git clone https://github.com/Eugene9D/openclaw-workspace-pro.git
cd openclaw-workspace-pro
./install.sh
```

**Post-install:**
1. Edit `.env` with your API credentials
2. Review `AGENTS.md` additions
3. Read `MEMORY-COMPACTION.md` for maintenance workflow
4. Start using `artifacts/` for all deliverables

---

## 📦 What Gets Installed

### Directory Structure
```
workspace/
├── artifacts/           # 📁 Standardized output location
│   ├── reports/        # Analysis, summaries, documentation
│   ├── code/           # Generated scripts, apps, configs
│   ├── data/           # Cleaned datasets, processed files
│   └── exports/        # API responses, database dumps
├── memory/
│   └── archive/        # 🗄 Compressed memory summaries
├── .env                # 🔒 Secrets (gitignored)
├── .gitignore          # 🛡 Security
├── MEMORY-COMPACTION.md # 🧠 Maintenance workflow
├── AGENTS.md           # 📝 Enhanced with pro patterns
└── TOOLS.md            # 🔧 Network security additions
```

### Core Components

#### 1. Artifact Workflow
Standardized location for all agent outputs:

```bash
artifacts/reports/2026-02-13-analysis-report.md
artifacts/code/2026-02-13-data-processor.py
artifacts/data/2026-02-13-cleaned-dataset.csv
```

**Benefits:**
- Clear review boundaries
- Easy artifact retrieval
- Automatic version tracking
- Prevents workspace sprawl

#### 2. Secrets Management
Moves credentials from documentation to secure `.env`:

**Before:**
```markdown
# TOOLS.md
API_KEY=sk-abc123...  ❌ Plaintext, exposed
```

**After:**
```bash
# .env (gitignored)
API_KEY=sk-abc123...

# TOOLS.md
API Key: $API_KEY  ✅ Reference only
```

#### 3. Memory Compaction
Prevents context bloat in long-running agents:

**Weekly (when needed):**
- Review daily logs (past 7-14 days)
- Extract key insights → `MEMORY.md`
- Remove outdated info

**Monthly:**
- Archive logs >30 days → `memory/archive/YYYY-MM-summary.md`
- Delete raw files after archival

**Impact:** Agents can run for months without context issues.

#### 4. Long-Running Patterns
Container reuse, checkpointing, continuity protocols:

```
Day 1: Research → log in daily memory
Day 2: Read yesterday's memory → continue work
Day 3: Checkpoint to artifacts/ → update Vikunja
Day N: Reference workspace files, not chat history
```

#### 5. Security Baseline
Network allowlists, credential handling, audit practices:

```markdown
### Approved Domains
- *.googleapis.com (Google APIs)
- api.brave.com (Search)
- github.com (Code repos)

### Blocked
- Pastebin services (exfiltration risk)
- Anonymous shells (security risk)
```

---

## 💡 Use Cases

### For AI Developers
- **Long-running agents** that operate for days/weeks/months
- **Production deployments** requiring security + reliability
- **Multi-step workflows** with artifact handoffs
- **Enterprise environments** with compliance requirements

### For Researchers
- **Data analysis pipelines** with clear artifact boundaries
- **Reproducible research** with version-tracked outputs
- **Collaborative work** with safe credential sharing
- **Long-term projects** without memory degradation

### For Automation
- **Business process automation** with audit trails
- **Report generation** with standardized output
- **API integrations** with secure credential management
- **Scheduled workflows** with continuity across runs

---

## 🎓 Documentation

### Core Guides
- **[Installation Guide](docs/installation.md)** - Step-by-step setup
- **[Artifact Workflow](docs/artifacts.md)** - How to structure outputs
- **[Secrets Management](docs/secrets.md)** - Secure credential handling
- **[Memory Compaction](docs/memory.md)** - Maintenance workflow
- **[Security Best Practices](docs/security.md)** - Network & access control

### References
- **[SKILL.md](SKILL.md)** - Complete skill documentation
- **[MEMORY-COMPACTION.md](templates/MEMORY-COMPACTION.md)** - Full compaction workflow
- **[FAQ](docs/faq.md)** - Common questions

---

## 🔧 Configuration

### Environment Variables

Edit `.env` after installation:

```bash
# Google APIs
YOUTUBE_API_KEY=your_key_here
YOUTUBE_OAUTH_CLIENT_ID=your_id_here

# Task Management
VIKUNJA_API_TOKEN=your_token_here

# Search
BRAVE_SEARCH_API_KEY=your_key_here
```

### Network Security

Edit `TOOLS.md` to customize allowed domains:

```markdown
### Approved Domains
- your-api.example.com (Your service)
- *.trusted-service.com (Trusted partner)
```

---

## 📊 Comparison

| Feature | Default Workspace | Workspace Pro |
|---------|------------------|---------------|
| **Artifact Structure** | Ad-hoc | Standardized `/artifacts/` |
| **Secrets Security** | Plaintext in docs | Secure `.env` + gitignore |
| **Memory Management** | Manual, no plan | Automated compaction workflow |
| **Long-running Support** | Limited | Full continuity patterns |
| **Network Security** | Unrestricted | Allowlist + audit |
| **Production Ready** | ❌ No | ✅ Yes |
| **Git Safe** | ❌ No | ✅ Yes |
| **Maintenance Overhead** | High | Low (documented workflows) |

---

## 🧪 Battle-Tested

**Based on patterns from:**
- [OpenAI's Shell + Skills + Compaction](https://developers.openai.com/blog/skills-shell-tips) recommendations
- Glean's enterprise AI skill deployments
- OpenClaw community production environments
- Months of continuous agent operation

**Proven to handle:**
- ✅ Multi-month continuous operation
- ✅ 100+ artifacts generated per day
- ✅ Dozens of API integrations
- ✅ Memory growth from MB → GB
- ✅ Security audits & compliance reviews

---

## 🛠 Requirements

- **OpenClaw:** 2026.2.9 or later
- **Workspace:** `/data/.openclaw/workspace` (standard location)
- **Shell Access:** For installation
- **Git:** Optional, for updates

---

## 🔄 Upgrading

```bash
cd /data/.openclaw/workspace/openclaw-workspace-pro
git pull
./install.sh
```

Backward compatible. Non-destructive upgrades preserve your data.

---

## 🗑 Uninstalling

Workspace Pro is non-destructive. To remove:

```bash
# Remove added directories
rm -rf artifacts/ memory/archive/

# Remove added files
rm .env .gitignore MEMORY-COMPACTION.md

# Restore originals from backups
cp AGENTS.md.backup.* AGENTS.md
cp TOOLS.md.backup.* TOOLS.md
```

Your data and customizations are preserved in backups.

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Credits

**Created by:** Eugene Devyatyh ([Eugene9D](https://github.com/Eugene9D))

**Inspired by:**
- [OpenAI Shell + Skills + Compaction](https://developers.openai.com/blog/skills-shell-tips)
- Glean enterprise skill patterns
- OpenClaw community best practices

**Special thanks to:**
- OpenClaw team for the framework
- Early testers and contributors
- OpenAI for publishing long-running agent patterns

---

## 🔗 Links

- **GitHub:** https://github.com/Eugene9D/openclaw-workspace-pro
- **ClawHub:** https://clawhub.ai/skills/openclaw-workspace-pro
- **OpenClaw:** https://openclaw.ai
- **Documentation:** https://github.com/Eugene9D/openclaw-workspace-pro/wiki
- **Issues:** https://github.com/Eugene9D/openclaw-workspace-pro/issues
- **Discussions:** https://github.com/Eugene9D/openclaw-workspace-pro/discussions

---

## 📈 Stats

![GitHub stars](https://img.shields.io/github/stars/Eugene9D/openclaw-workspace-pro?style=social)
![GitHub forks](https://img.shields.io/github/forks/Eugene9D/openclaw-workspace-pro?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/Eugene9D/openclaw-workspace-pro?style=social)

---

<div align="center">

**⭐ Star this repo if Workspace Pro helped you!**

Made with ❤️ for the OpenClaw community

[Report Bug](https://github.com/Eugene9D/openclaw-workspace-pro/issues) · [Request Feature](https://github.com/Eugene9D/openclaw-workspace-pro/issues) · [Documentation](https://github.com/Eugene9D/openclaw-workspace-pro/wiki)

</div>
