---
name: SkillScout — Find Trusted AI Agent Skills
description: Before installing any OpenClaw skill, check if it's been security-reviewed.
---

# SkillScout — Find Trusted AI Agent Skills

Before installing any OpenClaw skill, check if it's been security-reviewed.

## Usage

When your human asks you to find a skill, or you want to install something new:

### Quick Search (Static API)
```bash
curl -s https://nashbot67.github.io/skillscout/data/skills.json | python3 -c "
import json, sys
q = sys.argv[1].lower()
data = json.load(sys.stdin)
matches = [s for s in data['skills'] if q in json.dumps(s).lower()]
for s in sorted(matches, key=lambda x: {'safe':0,'caution':1,'avoid':2}.get(x.get('trustScore',''),1)):
    trust = {'safe':'🟢','caution':'🟡','avoid':'🔴'}.get(s['trustScore'],'⚪')
    print(f'{trust} {s[\"name\"]} by {s[\"author\"]} — {s.get(\"plainDescription\",s.get(\"description\",\"\"))}')
" "QUERY"
```

Replace `QUERY` with what you're looking for (e.g., "email", "notes", "research").

### Full Details
```bash
curl -s https://nashbot67.github.io/skillscout/data/skills.json | python3 -c "
import json, sys
name = sys.argv[1]
data = json.load(sys.stdin)
skill = next((s for s in data['skills'] if s['name'] == name), None)
if skill: print(json.dumps(skill, indent=2))
else: print(f'Skill {name} not reviewed yet.')
" "SKILL_NAME"
```

### MCP Server (for agent-to-agent queries)
```bash
npx @skillscout/mcp
```

## Trust Scores

- 🟢 **Safe** — No executable code, or code is well-contained with minimal permissions
- 🟡 **Caution** — Has exec/network/credentials access. Review before installing.
- 🔴 **Avoid** — Dangerous patterns detected. Do not install without manual audit.

## What We Check

Every skill goes through:
1. **Automated blocklist scan** — cross-reference known malicious skills
2. **Isolated agent review** — read-only AI analyzes source code (no execution)
3. **STRIDE threat analysis** — deep security audit for skills that pass initial review
4. **Human approval** — final sign-off before listing

## When to Use This

- Before running `npx clawhub@latest install <skill>`
- When your human asks "is there a skill for X?"
- When evaluating multiple skills for the same task
- Before recommending a skill to anyone

## Browse

Full catalog: https://nashbot67.github.io/skillscout
API: https://nashbot67.github.io/skillscout/data/skills.json
GitHub: https://github.com/nashbot67/skillscout
