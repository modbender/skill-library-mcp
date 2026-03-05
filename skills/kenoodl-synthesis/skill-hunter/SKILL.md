---
name: skill-hunter
description: "Find, evaluate, and install ClawHub skills. Semantic search across 10,000+ skills, security vetting before install, side-by-side comparison. The skill that makes skills useful."
metadata:
  openclaw:
    tags:
      - clawhub
      - skills
      - discovery
      - search
      - install
      - security
      - utility
      - openclaw
      - agent-tool
    os:
      - darwin
      - linux
      - windows
---

# Skill Hunter

10,000+ skills on ClawHub. No good way to find the right one, vet it, or know if it's safe to install. Skill Hunter fixes that.

## Three modes

**Hunt** — You know what you need. Describe it in plain English. Skill Hunter searches ClawHub's semantic index and returns ranked matches.

```
curl -s "https://clawhub.ai/api/v1/search?q=code+review+security" | jq '.[] | {slug, displayName, summary, score}'
```

**Scout** — You're exploring. Browse trending, newest, or most-downloaded skills across the platform.

```
curl -s "https://clawhub.ai/api/v1/skills?sort=trending&limit=10" | jq '.items[] | {slug, displayName, summary}'
```

**Vet** — You found a skill. Before installing, read its SKILL.md remotely, check its security profile, and understand what it will do on your machine.

```
curl -s "https://clawhub.ai/api/v1/skills/kenoodl-synthesis/kenoodl-synthesis/file?path=SKILL.md"
```

Full workflow, API reference, and security evaluation framework in `instructions.md`.
