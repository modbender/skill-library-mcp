# Skill Audit Guardian

Ready-to-upload ClawHub package.

## Purpose
Provide a practical pre-install security gate for skill ZIP files:
- static pattern scan
- risk classification
- automatic folder segregation
- plain-English dashboard explanation

## Included
- SKILL.md
- scripts/skill-zip-audit.sh
- scripts/skill-zip-watch.sh
- scripts/generate-skill-audit-pro.py

## Publish example (CLI)
```bash
clawhub publish /Users/gascomp/Desktop/skill-audit-guardian \
  --slug skill-audit-guardian \
  --name "Skill Audit Guardian" \
  --version 1.0.0 \
  --changelog "Initial release: ZIP audit, auto-sort by risk, and plain-English dashboard"
```
