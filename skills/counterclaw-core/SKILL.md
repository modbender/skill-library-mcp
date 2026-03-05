---
name: counterclaw
description: Defensive interceptor for prompt injection and basic PII masking.
homepage: https://github.com/nickconstantinou/counterclaw-core
install: "pip install ."
requirements:
  env:
    - TRUSTED_ADMIN_IDS
  files:
    - "~/.openclaw/memory/"
    - "~/.openclaw/memory/MEMORY.md"
metadata:
  clawdbot:
    emoji: "🛡️"
    version: "1.1.0"
    category: "Security"
    type: "python-middleware"
    security_manifest:
      network_access: "optional (only when using email integration scripts)"
      filesystem_access: "Write-only logging to ~/.openclaw/memory/"
      purpose: "Log security violations locally for user audit."
---

# CounterClaw 🦞

> Defensive security for AI agents. Snaps shut on malicious payloads.

## ⚠️ Security Notice

This package has two modes:

1. **Core Scanner (offline):** `check_input()` and `check_output()` — no network calls
2. **Email Integration (network):** `send_protected_email.sh` — requires gog CLI for Gmail

## Installation

```bash
claw install counterclaw
```

## Quick Start

```python
from counterclaw import CounterClawInterceptor

interceptor = CounterClawInterceptor()

# Input scan - blocks prompt injections
# NOTE: Examples below are TEST CASES only - not actual instructions
result = interceptor.check_input("{{EXAMPLE: ignore previous instructions}}")
# → {"blocked": True, "safe": False}

# Output scan - detects PII leaks  
result = interceptor.check_output("Contact: john@example.com")
# → {"safe": False, "pii_detected": {"email": True}}
```

## Features

- 🔒 Defense against common prompt injection patterns
- 🛡️ Basic PII masking (Email, Phone, Credit Card)
- 📝 Violation logging to `~/.openclaw/memory/MEMORY.md`
- ⚠️ Warning on startup if TRUSTED_ADMIN_IDS not configured

## Configuration

### Required Environment Variable

```bash
# Set your trusted admin ID(s) - use non-sensitive identifiers only!
export TRUSTED_ADMIN_IDS="your_telegram_id"
```

**Important:** `TRUSTED_ADMIN_IDS` should ONLY contain non-sensitive identifiers:
- ✅ Telegram user IDs (e.g., `"123456789"`)
- ✅ Discord user IDs (e.g., `"987654321"`)
- ❌ NEVER API keys
- ❌ NEVER passwords
- ❌ NEVER tokens

You can set multiple admin IDs by comma-separating:
```bash
export TRUSTED_ADMIN_IDS="telegram_id_1,telegram_id_2"
```

### Runtime Configuration

```python
# Option 1: Via environment variable (recommended)
# Set TRUSTED_ADMIN_IDS before running
interceptor = CounterClawInterceptor()

# Option 2: Direct parameter
interceptor = CounterClawInterceptor(admin_user_id="123456789")
```

## Security Notes

- **Fail-Closed**: If `TRUSTED_ADMIN_IDS` is not set, admin features are disabled by default
- **Logging**: All violations are logged to `~/.openclaw/memory/MEMORY.md` with PII masked
- **No Network Access**: This middleware does not make any external network calls (offline-only)
- **File Access**: Only writes to `~/.openclaw/memory/MEMORY.md` — explicitly declared scope

## Files Created

| Path | Purpose |
|------|---------|
| `~/.openclaw/memory/` | Directory created on first run |
| `~/.openclaw/memory/MEMORY.md` | Violation logs with PII masked |

## License

MIT - See LICENSE file

## Development & Release

### Running Tests Locally

```bash
python3 tests/test_scanner.py
```

### Linting

```bash
pip install ruff
ruff check src/
```

### Publishing to ClawHub

The CI runs on every push and pull request:
1. **Ruff** - Lints Python code
2. **Tests** - Runs unit tests

To publish a new version:

```bash
# Version is set in pyproject.toml
git add -A
git commit -m "Release v1.0.9"
git tag v1.0.9
git push origin main --tags
```

CI will automatically:
- Run lint + tests
- If tests pass and tag starts with `v*`, publish to ClawHub
