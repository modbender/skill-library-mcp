---
name: security-audit
description: Minimal helper to audit skill.md-style instructions for supply-chain risks.
metadata:
  {
    "openclaw": {
      "requires": { "bins": ["python3"] },
      "category": "security"
    }
  }
---

# security-audit

Minimal helper to audit skill.md-style instructions for supply-chain risks.

## Features
- Heuristic scan for exfiltration patterns (HTTP POST, curl to unknown domains, reading ~/.env, credential keywords).
- Permission manifest reminder: lists filesystem/network touches it sees.
- Safe report: markdown summary + risk level.

## Usage
```bash
python audit.py path/to/skill.md > report.md
```
