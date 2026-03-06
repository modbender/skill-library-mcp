---
name: openclaw-whisperer
description: Comprehensive diagnostic, error-fixing, and skill recommendation tool for OpenClaw
license: MIT
version: 1.2.0
homepage: https://github.com/PhenixStar/openclaw-skills-collection
user-invocable: true
disable-model-invocation: false
metadata:
  openclaw:
    emoji: "🏥"
    requires:
      bins:
        - python3
      env: []
    install:
      - id: pip-deps
        kind: shell
        command: "pip install click rich requests beautifulsoup4"
        label: Install Python dependencies
---

# OpenClaw Whisperer

Ultimate diagnostic, error-fixing, and skill recommendation tool for OpenClaw.

## What's New in v1.1.0

- **Complementary Skills** - Discover skills that work together (10 skill relationships)
- **Diagnostic Hooks** - GitHub/Slack/Discord integration for error notifications (9 hook configs)
- **Recovery Tracking** - Track fix execution history and success rates
- **Smart Scoring** - Enhanced recommendations with complementary skill bonus scoring
- **Rich Display** - Improved CLI panels and formatting for suggestions

## When to Use

Activate when user wants to:
- Diagnose OpenClaw errors or issues
- Auto-fix common problems
- Find and recommend ClawHub skills with complementary suggestions
- Run extended health checks
- Setup OpenClaw for first time
- Update documentation and caches
- Track fix execution history

## Available Tools

### Error Fixer
Diagnose and auto-fix OpenClaw errors with diagnostic hooks and recovery tracking.
```bash
# Diagnose by error code (triggers diagnostic hooks if configured)
python3 {baseDir}/scripts/error-fixer.py --error 401

# Analyze log file with recovery suggestions
python3 {baseDir}/scripts/error-fixer.py --input /path/to/log

# Auto-fix safe issues (tracks execution history)
python3 {baseDir}/scripts/error-fixer.py --error EADDRINUSE --auto-fix

# List errors by category with fix history
python3 {baseDir}/scripts/error-fixer.py --category authentication

# View fix execution history
python3 {baseDir}/scripts/error-fixer.py --show-history

# Test notification hooks (GitHub/Slack/Discord)
python3 {baseDir}/scripts/error-fixer.py --test-hooks
```

### Skill Recommender
Smart ClawHub skill recommendations with complementary skill detection.
```bash
# Recommend for channel (includes complementary skills)
python3 {baseDir}/scripts/skill-recommender.py --channel whatsapp --top 5

# Recommend by use case with bonus scoring
python3 {baseDir}/scripts/skill-recommender.py --use-case "image generation"

# Auto-detect from config (enriched with complementary metadata)
python3 {baseDir}/scripts/skill-recommender.py --auto-detect

# Check for updates
python3 {baseDir}/scripts/skill-recommender.py --check-updates

# View complementary skills for installed skill
python3 {baseDir}/scripts/skill-recommender.py --complementary-for image-generator-pro
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

## Data Files (v1.1.0)
- [complementary-skills.json](data/complementary-skills.json) - 10 skill relationships
- [integration-hooks.json](data/integration-hooks.json) - 9 notification hook configs
- [fix-execution-history.json](data/fix-execution-history.json) - Fix tracking metadata

## Templates
- [Error Report](templates/error-report.md) - Diagnostic output format
- [Recommendation Report](templates/recommendation-report.md) - Skill suggestions format
