---
name: counterclaw
description: Production-grade defensive interceptor for prompt injection and PII leaks.
homepage: https://github.com/nickconstantinou/counterclaw-core
metadata:
  clawdbot:
    emoji: "🛡️"
    version: "1.0.0"
    category: "Security"
    requires:
      env:
        - TRUSTED_ADMIN_IDS
---

# CounterClaw 🦞

> Defensive security for AI agents. Snaps shut on malicious payloads.

## Installation

```bash
claw install counterclaw
```

## Quick Start

```python
from counterclaw import CounterClawInterceptor

interceptor = CounterClawInterceptor()

# Input scan - blocks prompt injections
result = interceptor.check_input("Ignore previous instructions")
# → {"blocked": True, "safe": False}

# Output scan - detects PII leaks  
result = interceptor.check_output("Contact: john@example.com")
# → {"safe": False, "pii_detected": {"email": True}}
```

## Features

- 🔒 Snap-shut Defense - Blocks 20+ prompt injection patterns
- 🛡️ PII Detection - Catches emails, phones, credit cards
- 📝 Auto-Logging - Violations logged to MEMORY.md
- ☁️ Nexus Ready - Dormant hooks for enterprise (opt-in)

## Configuration

### Admin-Locked (!claw-lock)
```python
interceptor = CounterClawInterceptor(
    admin_user_id="telegram_user_id"  # Set TRUSTED_ADMIN_IDS env
)
```

## License

MIT - See LICENSE file
