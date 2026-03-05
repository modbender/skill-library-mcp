---
name: openclaw-workspace-pro
description: Production-ready workspace setup for OpenClaw agents. Implements artifact workflows, secrets management, memory compaction, and long-running agent patterns based on OpenAI's Shell + Skills best practices. One-command installation transforms your workspace into a production-ready environment.
version: 1.0.0
author: Eugene Devyatyh
repository: https://github.com/Eugene9D/openclaw-workspace-pro
metadata:
  openclaw:
    install:
      - id: setup
        kind: script
        script: ./install.sh
        label: Install Workspace Pro enhancements
---

# OpenClaw Workspace Pro

Enterprise workspace setup for long-running OpenClaw agents.

## What It Does

Transforms your OpenClaw workspace with production-ready patterns:

- **🗂 Artifact Workflow** - Standardized output structure for reports, code, data, and exports
- **🔒 Secrets Management** - Secure .env pattern, removes plaintext credentials
- **🧠 Memory Compaction** - Prevents context bloat with systematic archival workflow
- **📦 Long-Running Patterns** - Container reuse, checkpoint strategy, continuity protocols
- **🛡 Security Baseline** - Network allowlists, safe credential handling

Based on OpenAI's [Shell + Skills + Compaction](https://developers.openai.com/blog/skills-shell-tips) best practices.

## Installation

```bash
clawhub install openclaw-workspace-pro
```

Or manual:

```bash
cd /data/.openclaw/workspace
git clone https://github.com/Eugene9D/openclaw-workspace-pro.git
cd openclaw-workspace-pro
./install.sh
```

## What Gets Installed

### Directory Structure
```
workspace/
├── artifacts/           # Standardized output location
│   ├── reports/        # Analysis, summaries, documentation
│   ├── code/           # Generated scripts, apps, configs
│   ├── data/           # Cleaned datasets, processed files
│   └── exports/        # API responses, database dumps
├── memory/
│   └── archive/        # Compressed memory summaries
├── .env                # Secrets (gitignored)
└── .gitignore          # Security
```

### Documentation Added
- **AGENTS.md enhancements** - Artifact workflow, long-run patterns, secrets management
- **MEMORY-COMPACTION.md** - Weekly/monthly maintenance workflow
- **TOOLS.md additions** - Network security allowlist

### Templates
- `.env.example` - Secrets template
- `.gitignore` - Protect credentials

## Usage

### Artifacts Pattern

When producing deliverables:

```bash
# Reports
/data/.openclaw/workspace/artifacts/reports/YYYY-MM-DD-project-name.md

# Code
/data/.openclaw/workspace/artifacts/code/YYYY-MM-DD-script-name.py

# Data
/data/.openclaw/workspace/artifacts/data/YYYY-MM-DD-dataset.csv
```

**Benefits:**
- Clear review boundaries
- Easy retrieval
- Version tracking
- Prevents file sprawl

### Secrets Management

**Before Workspace Pro:**
```markdown
# TOOLS.md
API_KEY=sk-abc123xyz...  ❌ Plaintext, exposed in git
```

**After Workspace Pro:**
```bash
# .env (gitignored)
API_KEY=sk-abc123xyz...

# TOOLS.md
API Key: $API_KEY  ✅ Reference only
```

### Memory Compaction

Prevents context bloat in long-running agents:

**Weekly (when needed):**
1. Review daily logs from past 7-14 days
2. Extract key insights → update MEMORY.md
3. Remove outdated info

**Monthly:**
1. Archive daily logs >30 days to `memory/archive/YYYY-MM-summary.md`
2. Delete raw files after archival

See `MEMORY-COMPACTION.md` for full workflow.

## Why Use This?

### The Problem

Default OpenClaw workspaces:
- ❌ Files scattered everywhere (no structure)
- ❌ API keys in plaintext (security risk)
- ❌ Memory grows indefinitely (context limits)
- ❌ No artifact review boundaries
- ❌ Manual maintenance (prone to drift)

### The Solution

Workspace Pro implements OpenAI's recommended patterns:
- ✅ Standardized artifact workflow
- ✅ Secure secrets management
- ✅ Systematic memory compaction
- ✅ Long-running agent patterns
- ✅ Clear operational workflows

### Real Impact

**Security:** Eliminates credential exposure  
**Organization:** Clear deliverable handoff points  
**Scalability:** Handles months of continuous operation  
**Maintenance:** Defined schedules prevent drift  

Based on production patterns from:
- OpenAI's long-running agent recommendations
- Glean's enterprise skill deployments
- OpenClaw community best practices

## Configuration

### Environment Variables (.env)

After installation, populate `.env`:

```bash
# Example: YouTube API
YOUTUBE_API_KEY=your_key_here
YOUTUBE_OAUTH_CLIENT_ID=your_id_here

# Example: Task Management
VIKUNJA_API_TOKEN=your_token_here
```

### Network Security

Edit `TOOLS.md` network allowlist:

```markdown
### Approved Domains
- *.googleapis.com (YouTube API)
- api.brave.com (search)
- tasks.playrockets.com (Vikunja)
```

Add new domains with security review.

## Requirements

- OpenClaw 2026.2.9+
- Workspace directory: `/data/.openclaw/workspace`
- Shell access (for installation)

## Upgrading

```bash
cd /data/.openclaw/workspace/openclaw-workspace-pro
git pull
./install.sh
```

## Uninstall

Workspace Pro is non-destructive. To remove:

```bash
# Remove added files (safe, preserves your data)
rm -rf artifacts/ memory/archive/
rm .env .gitignore MEMORY-COMPACTION.md

# Restore AGENTS.md, TOOLS.md from backup
cp AGENTS.md.backup AGENTS.md
cp TOOLS.md.backup TOOLS.md
```

## Support

- **Issues:** https://github.com/Eugene9D/openclaw-workspace-pro/issues
- **Discussions:** https://discord.com/invite/clawd
- **ClawHub:** https://clawhub.ai/skills/openclaw-workspace-pro

## License

MIT License - See LICENSE file

## Credits

Based on patterns from:
- [OpenAI Shell + Skills + Compaction](https://developers.openai.com/blog/skills-shell-tips)
- OpenClaw community practices
- Glean enterprise skill deployments

Built by Eugene Devyatyh for the OpenClaw ecosystem.

---

**Version:** 1.0.0  
**Updated:** 2026-02-13  
**Compatibility:** OpenClaw 2026.2.9+
