# OpenClaw Doctor Pro

Comprehensive diagnostic, error-fixing, and skill recommendation tool for OpenClaw.

## What is OpenClaw Doctor Pro?

OpenClaw Doctor Pro is an advanced troubleshooting suite for [OpenClaw](https://github.com/openclaw/openclaw) - a self-hosted AI gateway that connects messaging apps (WhatsApp, Telegram, Discord, Slack, Signal) to AI agents.

**Key Features:**
- 🔍 Automated error diagnosis across 10 error categories
- 🔧 Auto-fix capabilities for 40+ common issues
- 💡 Smart skill recommendations from ClawHub (5,700+ skills)
- 📊 Deep health checks and performance monitoring
- 📚 Comprehensive reference documentation
- 🎯 Interactive setup wizard for first-time users

## Quick Start

### Installation

```bash
# Install dependencies
pip install click rich requests beautifulsoup4

# Run diagnostic
python3 scripts/enhanced-doctor.py

# Fix errors automatically
python3 scripts/error-fixer.py --fix-all-safe

# Get skill recommendations
python3 scripts/skill-recommender.py --auto-detect
```

### First-Time Setup

```bash
# Interactive setup wizard
python3 scripts/setup-wizard.py

# Or check prerequisites only
python3 scripts/setup-wizard.py --check-only
```

## Tools Overview

### 1. Enhanced Doctor
Extended diagnostic checks beyond built-in `openclaw doctor`.

```bash
# Full diagnostics
python3 scripts/enhanced-doctor.py

# Deep scan with log analysis
python3 scripts/enhanced-doctor.py --deep

# JSON output
python3 scripts/enhanced-doctor.py --json
```

### 2. Error Fixer
Diagnose and auto-fix OpenClaw errors.

```bash
# Diagnose by error code
python3 scripts/error-fixer.py --error 401

# Analyze log file
python3 scripts/error-fixer.py --input /path/to/log

# Auto-fix safe issues
python3 scripts/error-fixer.py --error EADDRINUSE --auto-fix

# List errors by category
python3 scripts/error-fixer.py --category authentication
```

### 3. Skill Recommender
Smart ClawHub skill recommendations.

```bash
# Recommend for channel
python3 scripts/skill-recommender.py --channel whatsapp --top 5

# Recommend by use case
python3 scripts/skill-recommender.py --use-case "image generation"

# Auto-detect from config
python3 scripts/skill-recommender.py --auto-detect

# Check for updates
python3 scripts/skill-recommender.py --check-updates
```

### 4. Self-Updater
Keep references and caches current.

```bash
# Check what's outdated
python3 scripts/self-updater.py --check

# Update everything
python3 scripts/self-updater.py --update

# Update only skill cache
python3 scripts/self-updater.py --update --skills-only
```

### 5. Setup Wizard
Interactive first-time setup.

```bash
# Interactive setup
python3 scripts/setup-wizard.py

# Check prerequisites only
python3 scripts/setup-wizard.py --check-only
```

## Documentation Structure

### Reference Documentation (`references/`)

Comprehensive guides covering all aspects of OpenClaw troubleshooting:

| File | Description |
|------|-------------|
| [error-catalog.md](references/error-catalog.md) | Master index of all error types (10 categories, 50+ errors) |
| [authentication-errors.md](references/authentication-errors.md) | 401, API keys, tokens, env vars |
| [rate-limiting-errors.md](references/rate-limiting-errors.md) | 429, quotas, throttling, retry strategies |
| [gateway-errors.md](references/gateway-errors.md) | 502, port conflicts, network issues |
| [channel-errors.md](references/channel-errors.md) | WhatsApp, Telegram, Discord, Slack, Signal |
| [sandbox-errors.md](references/sandbox-errors.md) | Docker, containers, OOM, timeouts |
| [configuration-errors.md](references/configuration-errors.md) | Config validation, schema, types |
| [installation-errors.md](references/installation-errors.md) | Node.js, pnpm, PATH, dependencies |
| [diagnostic-commands.md](references/diagnostic-commands.md) | CLI command reference |
| [clawhub-integration.md](references/clawhub-integration.md) | Skill management, publishing |
| [auto-fix-capabilities.md](references/auto-fix-capabilities.md) | What can be auto-fixed |
| [troubleshooting-workflow.md](references/troubleshooting-workflow.md) | Decision trees and flows |

### Templates (`templates/`)

Report templates for consistent output:

| File | Purpose |
|------|---------|
| [error-report.md](templates/error-report.md) | Error diagnostic report format |
| [recommendation-report.md](templates/recommendation-report.md) | Skill recommendation report format |

## Error Categories

OpenClaw Doctor Pro handles 10 error categories:

1. **Authentication** - API keys, tokens, credentials
2. **Rate Limiting** - Quotas, throttling, burst limits
3. **Gateway** - Network, ports, connectivity
4. **Channels** - WhatsApp, Telegram, Discord, Slack, Signal
5. **Sandbox** - Docker, containers, execution
6. **Configuration** - Schema, validation, types
7. **Installation** - Dependencies, versions, PATH
8. **Plugins** - Loading, initialization, versions
9. **Skills** - ClawHub, execution, manifests
10. **System** - Disk, memory, permissions

## Auto-Fix Capabilities

### Safety Levels

- ✅ **Safe** - Fully automated, no user confirmation needed
- ⚠️ **Moderate** - Automated with optional confirmation
- 🔴 **Risky** - Requires explicit user confirmation
- ❌ **Manual** - Cannot auto-fix, guidance provided

### Examples

**Safe Auto-Fixes:**
- Increase sandbox timeout
- Enable retry strategy
- Convert config value types
- Migrate deprecated keys
- Refresh auth tokens

**Moderate Auto-Fixes:**
- Kill process on port (EADDRINUSE)
- Fix workspace permissions
- Install missing packages
- Re-set webhooks

**Risky Auto-Fixes:**
- Regenerate gateway token
- Start Docker daemon
- Install Signal CLI
- Modify firewall rules

See [auto-fix-capabilities.md](references/auto-fix-capabilities.md) for complete list.

## Common Workflows

### Gateway Won't Start
```bash
# 1. Run diagnostics
python3 scripts/enhanced-doctor.py

# 2. Fix common issues
python3 scripts/error-fixer.py --fix-all-safe

# 3. Check port
lsof -i :18789

# 4. Fix port conflict if needed
python3 scripts/error-fixer.py --error EADDRINUSE --auto-fix
```

### Channel Not Working
```bash
# 1. Check channel status
openclaw channels status whatsapp

# 2. View channel-specific errors
python3 scripts/error-fixer.py --category channel

# 3. Test channel
openclaw channels test whatsapp

# 4. Follow channel-specific guide
# See references/channel-errors.md
```

### API Rate Limits
```bash
# 1. Check quota
openclaw quota show

# 2. Enable retry strategy
python3 scripts/error-fixer.py --error 429 --auto-fix

# 3. Enable fallback provider
openclaw config set ai.fallback.enabled true
```

### Find Relevant Skills
```bash
# 1. Auto-detect needs
python3 scripts/skill-recommender.py --auto-detect

# 2. Install recommended
openclaw skills install skill-name

# 3. Check updates
python3 scripts/skill-recommender.py --check-updates
```

## ClawHub Integration

Access to 5,700+ skills across categories:

**Categories:**
- AI & Machine Learning (image gen, embeddings, sentiment)
- Automation (workflows, schedulers, triggers)
- Utilities (PDF, image tools, converters)
- Integrations (Google, GitHub, Zapier)
- Communication (email, SMS, notifications)
- Data (databases, analytics, visualization)

**Popular Skills:**
- `image-generator-pro` - Multi-provider image generation
- `pdf-toolkit` - Complete PDF manipulation
- `workflow-builder` - Visual automation
- `google-workspace` - Google integration
- `auto-responder` - Smart responses

See [clawhub-integration.md](references/clawhub-integration.md) for details.

## Project Structure

```
openclaw-doctor-pro/
├── SKILL.md                          # ClawHub manifest
├── README.md                         # This file
├── scripts/
│   ├── enhanced-doctor.py           # Extended diagnostics
│   ├── error-fixer.py               # Auto-fix errors
│   ├── skill-recommender.py         # Skill recommendations
│   ├── self-updater.py              # Update tool
│   └── setup-wizard.py              # First-time setup
├── references/
│   ├── error-catalog.md             # Error index
│   ├── authentication-errors.md     # Auth issues
│   ├── rate-limiting-errors.md      # Rate limits
│   ├── gateway-errors.md            # Gateway issues
│   ├── channel-errors.md            # Channel issues
│   ├── sandbox-errors.md            # Sandbox issues
│   ├── configuration-errors.md      # Config issues
│   ├── installation-errors.md       # Install issues
│   ├── diagnostic-commands.md       # CLI reference
│   ├── clawhub-integration.md       # Skill management
│   ├── auto-fix-capabilities.md     # Fix reference
│   └── troubleshooting-workflow.md  # Decision trees
├── templates/
│   ├── error-report.md              # Error report template
│   └── recommendation-report.md     # Recommendation template
├── data/
│   ├── error-patterns.json          # Error definitions
│   └── skills-cache.json            # ClawHub cache
└── cache/
    └── skill-recommendations.json   # Cached recommendations
```

## Requirements

- Python 3.8+
- OpenClaw installed
- Dependencies: `click`, `rich`, `requests`, `beautifulsoup4`

## Installation

```bash
# Clone or download
git clone https://github.com/username/openclaw-doctor-pro.git
cd openclaw-doctor-pro

# Install dependencies
pip install click rich requests beautifulsoup4

# Run setup wizard
python3 scripts/setup-wizard.py
```

## Contributing

Contributions welcome! Areas to improve:

- Add more error patterns
- Enhance auto-fix recipes
- Improve skill recommendations
- Add more platform support
- Update documentation

## License

MIT License - See LICENSE file for details.

## Support

- GitHub Issues: https://github.com/openclaw/openclaw/issues
- OpenClaw Docs: https://docs.openclaw.io
- Community Discord: https://discord.gg/openclaw

## Acknowledgments

Built for the OpenClaw community. Special thanks to:
- OpenClaw core team
- ClawHub contributors
- Community testers and feedback providers

---

**OpenClaw Doctor Pro** - Because every gateway needs a doctor 🏥
