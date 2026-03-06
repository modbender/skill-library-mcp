---
name: openclaw-doctor-pro
description: Comprehensive diagnostic, error-fixing, and skill recommendation tool for OpenClaw
license: MIT
version: 1.0.0
homepage: https://github.com/PhenixStar/openclaw-doctor-pro
user-invocable: true
disable-model-invocation: false
metadata:
  {
    "openclaw": {
      "emoji": "🏥",
      "requires": {
        "bins": ["python3"],
        "env": []
      },
      "install": [
        {
          "id": "pip-deps",
          "kind": "shell",
          "command": "pip install click rich requests beautifulsoup4",
          "label": "Install Python dependencies"
        }
      ]
    }
  }
---

# OpenClaw Doctor Pro

Ultimate diagnostic, error-fixing, and skill recommendation tool for OpenClaw.

## When to Use

Activate when user wants to:
- Diagnose OpenClaw errors or issues
- Auto-fix common problems
- Find and recommend ClawHub skills
- Run extended health checks
- Setup OpenClaw for first time
- Update documentation and caches

## Available Tools

### Error Fixer
Diagnose and auto-fix OpenClaw errors.
```bash
# Diagnose by error code
python3 {baseDir}/scripts/error-fixer.py --error 401

# Analyze log file
python3 {baseDir}/scripts/error-fixer.py --input /path/to/log

# Auto-fix safe issues
python3 {baseDir}/scripts/error-fixer.py --error EADDRINUSE --auto-fix

# List errors by category
python3 {baseDir}/scripts/error-fixer.py --category authentication
```

### Skill Recommender
Smart ClawHub skill recommendations.
```bash
# Recommend for channel
python3 {baseDir}/scripts/skill-recommender.py --channel whatsapp --top 5

# Recommend by use case
python3 {baseDir}/scripts/skill-recommender.py --use-case "image generation"

# Auto-detect from config
python3 {baseDir}/scripts/skill-recommender.py --auto-detect

# Check for updates
python3 {baseDir}/scripts/skill-recommender.py --check-updates
```

### Enhanced Doctor
Extended diagnostic checks.
```bash
# Full diagnostics
python3 {baseDir}/scripts/enhanced-doctor.py

# Deep scan with log analysis
python3 {baseDir}/scripts/enhanced-doctor.py --deep

# JSON output
python3 {baseDir}/scripts/enhanced-doctor.py --json
```

### Self-Updater
Keep references and caches current.
```bash
# Check what's outdated
python3 {baseDir}/scripts/self-updater.py --check

# Update everything
python3 {baseDir}/scripts/self-updater.py --update

# Update only skill cache
python3 {baseDir}/scripts/self-updater.py --update --skills-only
```

### Setup Wizard
Interactive first-time setup.
```bash
# Interactive setup
python3 {baseDir}/scripts/setup-wizard.py

# Check prerequisites only
python3 {baseDir}/scripts/setup-wizard.py --check-only
```

## Reference Files
- [Error Catalog](references/error-catalog.md) - Master error index
- [Auto-Fix Capabilities](references/auto-fix-capabilities.md) - Safe vs manual fixes
- [Diagnostic Commands](references/diagnostic-commands.md) - CLI quick reference
- [Troubleshooting Workflow](references/troubleshooting-workflow.md) - Decision tree
- [Authentication Errors](references/authentication-errors.md) - Auth issues
- [Rate Limiting Errors](references/rate-limiting-errors.md) - Quota management
- [Gateway Errors](references/gateway-errors.md) - Network issues
- [Channel Errors](references/channel-errors.md) - Channel-specific
- [Sandbox Errors](references/sandbox-errors.md) - Docker issues
- [Configuration Errors](references/configuration-errors.md) - Config problems
- [Installation Errors](references/installation-errors.md) - Setup issues
- [ClawHub Integration](references/clawhub-integration.md) - Skill management

## Templates
- [Error Report](templates/error-report.md) - Diagnostic output format
- [Recommendation Report](templates/recommendation-report.md) - Skill suggestions format
