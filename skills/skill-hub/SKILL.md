---
name: skill-hub
description: "OpenClaw skill discovery, security vetting & install. Searches 3000+ curated skills from ClawHub registry and awesome-openclaw-skills catalog. Scores credibility, detects prompt injection & malicious patterns, manages installations. Quick-checks GitHub for new skills."
license: MIT
version: 1.0.0
homepage: https://github.com/PhenixStar/openclaw-skills-collection
user-invocable: true
disable-model-invocation: false
auto_activate:
  - "find skill"
  - "install skill"
  - "search skills"
  - "what skills exist"
  - "skill for"
  - "discover skill"
  - "vet skill"
  - "scan skill"
  - "skill security"
  - "new skills"
  - "skill updates"
  - "browse skills"
allowed-tools:
  - Bash
  - Read
  - Write
---

# Skill Hub

Unified skill discovery, security vetting, and installation for OpenClaw.

## Commands

### Search Skills
Find skills by keyword, category, or credibility score.

```bash
python3 scripts/skill-hub-search.py --query "spreadsheet"
python3 scripts/skill-hub-search.py --category "DevOps" --min-score 60
python3 scripts/skill-hub-search.py --query "auth" --live        # include live ClawHub results
python3 scripts/skill-hub-search.py --installed                  # show only installed
python3 scripts/skill-hub-search.py --not-installed --limit 20   # discovery mode
```

### Install Skills
After finding a skill, install via ClawHub:

```bash
npx clawhub@latest install <skill-slug>
```

### Vet Skills (Security Scan)
Scan a skill for malicious patterns, prompt injection, and logic weaknesses.

```bash
python3 scripts/skill-hub-vet.py --slug google-sheets     # vet single skill
python3 scripts/skill-hub-vet.py --all-installed           # vet all installed
python3 scripts/skill-hub-vet.py --category "DevOps"       # vet category
python3 scripts/skill-hub-vet.py --top 10                  # vet top N unvetted
```

### Status Dashboard
See installed vs catalog coverage, unvetted warnings, recommendations.

```bash
python3 scripts/skill-hub-status.py
```

### Quick Check (GitHub API)
Fast check if new skills were added since last sync. Uses `gh` CLI — no full download needed.

```bash
python3 scripts/skill-hub-quick-check.py              # check for updates
python3 scripts/skill-hub-quick-check.py --sync        # auto-sync if updates found
python3 scripts/skill-hub-quick-check.py --query "ai"  # check + search new skills
```

### Browse Full Catalog
Export catalog as formatted table (terminal or markdown), grouped by category.

```bash
python3 scripts/skill-hub-table-export.py                          # terminal table
python3 scripts/skill-hub-table-export.py --format markdown        # markdown table
python3 scripts/skill-hub-table-export.py --category "AI"          # filter category
```

### Sync Catalog
Full re-fetch from GitHub awesome-list. Computes credibility, preserves vet results, shows diff.

```bash
python3 scripts/skill-hub-sync.py
```

## Credibility Scores (0-100)

| Tier | Score | Meaning |
|------|-------|---------|
| Trusted | 85-100 | Curated + vetted + mature |
| Good | 60-84 | Curated or vetted, some signals |
| Unvetted | 30-59 | Exists in registry, not scanned |
| Caution | 0-29 | Missing signals or security warnings |

## Security Checks

Code-level: eval/exec, shell injection, obfuscation, network access, env harvesting, destructive ops.

NLP/Prompt-level: hidden instructions, role hijacking, invisible unicode, exfiltration prompts, authority escalation, social engineering.

## When to Use

- User asks "find a skill for X" or "is there a skill that can..."
- User wants to extend capabilities with new tools
- User wants to check if installed skills are safe
- Before installing unknown skills from registry
