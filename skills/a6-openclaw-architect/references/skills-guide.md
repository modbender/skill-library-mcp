# How to Build OpenClaw Skills

## What Is a Skill?

A skill is a knowledge + tools bundle that extends an OpenClaw agent. It lives in `workspace/skills/<name>/` and is auto-discovered by the agent.

## Directory Structure

```
skills/my-skill/
├── SKILL.md           # Required: metadata + documentation
├── scripts/           # Optional: executable scripts
│   ├── main.py
│   └── helper.sh
└── references/        # Optional: additional docs loaded on demand
    ├── api-docs.md
    └── examples.md
```

## SKILL.md Format

### Frontmatter (YAML)
```yaml
---
name: my-skill
description: "One-line description for search and discovery"
homepage: https://example.com
license: MIT
compatibility: Python 3.10+
metadata: {"openclaw": {"emoji": "🔧", "primaryEnv": "MY_API_KEY"}}
---
```

**Required fields:**
- `name` — kebab-case, unique identifier
- `description` — Clear, searchable description

**Optional fields:**
- `homepage` — Link to docs or project
- `license` — MIT, Apache-2.0, etc.
- `compatibility` — Runtime requirements
- `metadata.openclaw.emoji` — Display emoji
- `metadata.openclaw.primaryEnv` — Main API key env var name
- `metadata.openclaw.requires.env` — Required env vars array

### Body (Markdown)
After frontmatter, write clear documentation:

1. **When to Use** — Clear trigger conditions
2. **Quick Start** — Fastest path to value
3. **Commands** — All CLI commands with examples
4. **Configuration** — Setup steps
5. **Examples** — Real-world usage
6. **Troubleshooting** — Common issues

## Script Design Rules

### Use stdlib only (Python)
```python
#!/usr/bin/env python3
"""Skill script — stdlib only, no pip dependencies."""
import json, os, sys, urllib.request, subprocess
```

**Why?** Skills must work without `pip install`. Use only Python standard library. If you need HTTP, use `urllib.request`. If you need JSON, use `json`. No `requests`, no `httpx`, no `click`.

### CLI Pattern
```python
import argparse

def main():
    parser = argparse.ArgumentParser(description="My skill CLI")
    sub = parser.add_subparsers(dest="command")
    
    list_cmd = sub.add_parser("list", help="List items")
    list_cmd.add_argument("--format", choices=["json", "table"], default="table")
    
    get_cmd = sub.add_parser("get", help="Get an item")
    get_cmd.add_argument("id", help="Item ID")
    
    args = parser.parse_args()
    # ... handle commands

if __name__ == "__main__":
    main()
```

### Environment Variables
```python
API_KEY = os.environ.get("MY_API_KEY")
if not API_KEY:
    print("Error: MY_API_KEY not set. Configure in openclaw.json skills.entries", file=sys.stderr)
    sys.exit(1)
```

### Output Format
- Default: human-readable table
- `--json` flag: machine-readable JSON
- Errors to stderr, data to stdout

## Publishing to ClawHub

### Naming Convention
Use a prefix for branding: `a6-my-skill` (we use `a6-` for AgxntSix).

### Quality Checklist
- [ ] SKILL.md has proper frontmatter
- [ ] Description is searchable and clear
- [ ] All commands documented with examples
- [ ] Scripts use stdlib only
- [ ] Error handling is comprehensive
- [ ] Works without any pip install

### Batch Publishing
```bash
# Publish a single skill
openclaw skills publish my-skill

# Or use the publisher script for batches
$PY tools/publish_batch.sh
```

### Competitive Analysis
Before building, check what exists:
1. Search ClawHub for similar skills
2. Study top-ranking skills' SKILL.md format
3. Match or exceed their documentation quality
4. Add unique value (real-world examples, better error handling)

## Skill Config in openclaw.json

```json
{
  "skills": {
    "entries": {
      "my-skill": {
        "enabled": true,
        "env": {
          "MY_API_KEY": "key-here"
        }
      }
    }
  }
}
```

## How Skills Are Loaded

1. Agent starts → scans `workspace/skills/*/SKILL.md`
2. Frontmatter parsed for metadata
3. When relevant to a conversation, SKILL.md content is loaded into context
4. Agent can execute scripts via `exec` tool
5. References in `references/` loaded on demand

## Common Patterns

### API Wrapper Skill
```
skills/my-api/
├── SKILL.md          # API docs, auth setup, examples
└── scripts/
    └── my_api.py     # CLI: list, get, create, update, delete
```

### Knowledge Skill (No Scripts)
```
skills/my-knowledge/
├── SKILL.md          # When to use, key concepts
└── references/
    ├── guide.md      # Detailed guide
    └── faq.md        # Common questions
```

### Internal Skill (Not Published)
Add `"isInternal": true` to metadata — won't be published to ClawHub.
```yaml
metadata: {"openclaw": {"isInternal": true}}
```
