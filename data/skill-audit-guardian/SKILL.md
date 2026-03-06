---
name: skill-audit-guardian
description: "Audit dropped ClawHub skill ZIPs, classify risk (SAFE/CAUTION/REMOVE), auto-sort files, and generate a plain-English security dashboard."
version: "1.0.0"
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["bash", "python3", "unzip", "rg"] }
      }
  }
---

# Skill Audit Guardian

Security helper for reviewing skill ZIPs before production install.

## What it does

1. Watches a drop folder for `.zip` files
2. Audits each ZIP for suspicious patterns
3. Scores and classifies into:
   - SAFE
   - CAUTION
   - REMOVE
4. Auto-moves files into risk folders
5. Generates a dashboard with plain-English reasoning per flagged line

## Included scripts

- `scripts/skill-zip-audit.sh`
  - One-shot ZIP auditor
- `scripts/skill-zip-watch.sh`
  - Continuous watcher + auto-sorter
- `scripts/generate-skill-audit-pro.py`
  - Dashboard generator (`~/Desktop/skill-audit-pro.html`)

## Quick start

```bash
# One-shot audit
bash scripts/skill-zip-audit.sh ~/Desktop/skill-drop/example.zip

# Continuous mode (recommended)
bash scripts/skill-zip-watch.sh ~/Desktop/skill-drop
```

## Folder output (watch mode)

- `~/Desktop/skill-drop/safe`
- `~/Desktop/skill-drop/caution`
- `~/Desktop/skill-drop/remove`
- `~/Desktop/skill-drop/failed`

## Dashboard

```bash
open ~/Desktop/skill-audit-pro.html
```

## Notes

- This is heuristic scanning, not a full malware sandbox.
- Always test CAUTION/REMOVE skills in isolated environment first.
