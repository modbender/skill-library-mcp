---
name: skill-miner
description: Professional skill discovery and clean-skill creation from ClawHub research. Use when you need to find existing functionality, research approaches, or build new skills based on ClawHub inspiration without downloading external code. Implements safe workflow: Search ClawHub → Inspect metadata → Analyze approach → Build own clean implementation. Prevents security risks while enabling rapid skill development.
---

# skill-miner

**Research. Analyze. Build Clean.**

Systematic approach to discovering skills on ClawHub and building your own implementations. Instead of downloading potentially risky code, use this skill to research existing solutions, understand their approaches, and create your own clean, safe version.

*Trust but verify, built but owned.* 🦞

---

## When to Use This Skill

Use this skill when:
- You need new functionality you don't have
- You want to research how others solve problems
- You find a suspicious skill but like the idea
- You're building a new skill from scratch
- You want to stay ahead of ClawHub trends

---

## Core Philosophy

```
1. NEVER download suspicious skills
2. INSPECT to understand the idea  
3. BUILD your own clean implementation
4. PUBLISH or keep private
```

**Why?**
- Suspicious = potential malware/risk (ew, no thanks)
- Building yourself = 100% clean & safe (sleep well at night)
- Generic = works for everyone (share the love)
- Your code, your rules 🦞

---

## Workflow

### Phase 1: Discovery

```bash
# Search for relevant skills
clawhub search <topic>

# Explore trending
clawhub explore --sort trending --limit 20

# Find gaps
clawhub explore --sort newest --limit 50
```

### Phase 2: Research

```bash
# Inspect without downloading
clawhub inspect <skill-slug>

# Read the SKILL.md to understand:
# - What problem it solves
# - How it triggers
# - What commands/tools it uses
```

### Phase 3: Analysis

Document what you learned:
- **Problem**: What need does it address?
- **Approach**: How does it solve it?
- **Tools**: What commands/APIs does it use?
- **Gaps**: What's missing or could be better?

### Phase 4: Build

Use skill-creator to build your clean version:
- Same problem, different implementation
- Add missing features
- Make it generic and reusable

---

## Search Commands

### Basic Search
```bash
# Task-based
clawhub search "pdf edit"
clawhub search "file transfer"
clawhub search "api github"

# Tool-based
clawhub search github
clawhub search slack

# Concept-based
clawhub search automation
clawhub search monitoring
clawhub search sync
```

### Exploration
```bash
# Trending skills
clawhub explore --sort trending --limit 20

# Most downloaded
clawhub explore --sort downloads --limit 20

# newest
clawhub explore --sort newest --limit 30
```

### Deep Research
```bash
# By category
clawhub search "code"
clawhub search "data"
clawhub search "media"
clawhub search "network"
clawhub search "security"

# By use case
clawhub search "automation workflow"
clawhub search "backup sync"
clawhub search "monitoring alerting"
```

---

## Inspect Without Downloading

Use `clawhub inspect` to read skill metadata:

```bash
# Get skill info
clawhub inspect <slug>

# This shows:
# - name
# - summary/description
# - owner
# - created/updated dates
# - version
# - tags
```

**Never use** `clawhub install` on suspicious skills!

---

## Security Principles

When researching skills, watch for these risk indicators:

- Code execution patterns (eval, exec)
- External API calls without documentation
- Hardcoded credentials
- Shell execution without input validation
- Missing or unclear documentation
- Unknown or unverified publishers

If any indicators are present: inspect the metadata only, then build your own implementation.

---

## Building Clean Skills

### Template Structure

```
my-clean-skill/
├── SKILL.md              # Your clean implementation
├── scripts/              # Your code
├── references/           # Documentation
└── assets/              # Templates (if needed)
```

### SKILL.md Template

```markdown
---
name: my-clean-skill
description: Does X. Use when user wants to Y. Based on ClawHub research but built from scratch.
---

# My Clean Skill

## What It Does

[Clear description]

## When to Use

- Use case 1
- Use case 2

## Commands

[Your commands]

## Implementation

[How you built it - clean, generic]

## Security

[Your security measures]
```

---

## Examples

### Scenario 1: Found Suspicious Shell Skill

**Found:** "shell-commands" (suspicious - has eval)

**Inspect:**
```bash
clawhub inspect shell-commands
# Problem: Execute shell commands
# Tools: bash, ssh
```

**Build Clean:**
```bash
# Write your own safe-shell-skill
# - No eval
# - Predefined safe commands only
# - Input validation
# - Full documentation
```

### Scenario 2: Found Good Crypto Skill

**Found:** "crypto-trader" (risky - real money)

**Inspect:**
```bash
clawhub inspect crypto-trader
# Problem: Trading automation
# Tools: exchange APIs
```

**Build Clean:**
```bash
# Build crypto-monitor instead
# - Read-only data fetching
# - Price alerts
# - No trading (safe)
```

### Scenario 3: Gap Found

**Search:** No good "log-analyzer" skill

**Build:**
```bash
# Create log-analyzer from scratch
# - Parse common log formats
# - Pattern detection
# - Alert on errors
```

---

## Common Gaps to Fill

These skills don't exist or are outdated:

| Gap | Description |
|-----|-------------|
| code-refactor | AI-powered code refactoring |
| system-monitor | Modern system monitoring |
| task-automation | General automation |
| webhook-handler | Webhook processing |
| cron-scheduler | Smart scheduling |
| log-analyzer | Log parsing & analysis |
| backup-scheduler | Intelligent backups |
| api-tester | API testing tool |
| config-manager | Configuration management |

---

## Best Practices

### Building
1. Start simple, add features later
2. Use well-tested tools (curl, jq, etc.)
3. No external dependencies when possible
4. Full error handling
5. Clear documentation

### Publishing
1. Test extensively
2. Clear description
3. Generic (no hardcoded values)
4. Security-first design
5. Include troubleshooting

### Security
1. No eval ever
2. Input validation
3. No secrets in code
4. Use environment variables
5. Minimal permissions

---

## Quality Checklist

Before publishing:

- [ ] Works as documented
- [ ] No hardcoded secrets
- [ ] Cross-platform compatible
- [ ] Error handling included
- [ ] Clear examples
- [ ] Triggers properly
- [ ] No suspicious patterns

---

## Related Skills

- `next-skill` - General skill discovery
- `skill-creator` - Build new skills
- `claw2claw-filetransfer` - Share skills

---

**Guidelines:**
- Inspect before install
- Build your own when in doubt
- Share clean, well-documented skills

---

*From Claws - for Claws.* 🦞
