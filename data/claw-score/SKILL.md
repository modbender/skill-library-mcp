---
name: Claw Score - Agent Architecture Audit
description: This skill packages your agent's configuration files, sanitizes
  them (removes credentials/PII), and submits them for a Claw Score audit.
  You'll receive a detailed report via email within 24-48 hours.
---

# Claw Score - Agent Architecture Audit

> Get your agent's architecture audited by Atlas. One command, automated submission, email report.

## What This Does

This skill packages your agent's configuration files, sanitizes them (removes credentials/PII), and submits them for a Claw Score audit. You'll receive a detailed report via email within 24-48 hours.

## Usage

Tell your agent:

```
"Run a Claw Score audit and send the report to [your-email@example.com]"
```

Or more specifically:

```
"Submit my workspace for a Claw Score audit. Email: [your-email@example.com]"
```

## What Gets Submitted

The skill reads these files if they exist:
- `AGENTS.md` — Main agent instructions
- `SOUL.md` — Personality/identity
- `MEMORY.md` — Long-term memory config
- `TOOLS.md` — Tool configuration
- `SECURITY.md` — Security rules
- `HEARTBEAT.md` — Proactive behavior
- `USER.md` — User context
- `IDENTITY.md` — Agent identity

Plus a file tree listing of your workspace structure.

## What Gets Sanitized (Automatically Removed)

Before submission, the skill strips:
- API keys (patterns like `sk-`, `xoxb-`, etc.)
- Email addresses
- Phone numbers
- IP addresses
- URLs containing tokens
- Environment variable values
- Anything matching common credential patterns

You'll see a preview of what's being sent before confirmation.

## Privacy

- Files are transmitted directly to Atlas for auditing
- Data is NOT stored beyond the audit session
- Reports are private unless you share them
- No code execution — only .md files analyzed

## What You'll Receive

An email report containing:
- **Overall Claw Score** (1-5) with tier (Shrimp → Mega Claw)
- **Per-dimension scores** across 6 categories
- **Detailed findings** for each dimension
- **Top 3 recommendations** with copy-paste implementation examples
- **Quick wins** you can implement immediately

## Installation

This skill should be installed in your agent's workspace:

```bash
# If using OpenClaw skill system
cp -r /path/to/claw-score skills/

# Or download from ClawhHub (coming soon)
npx clawhub install claw-score
```

## Manual Submission

If automated submission fails, you can manually send your files to:
- Email: atlasai@fastmail.com
- Subject: "Claw Score Audit Request"

Include your sanitized .md files and desired response email.

## Learn More

- Landing page: https://atlasforge.me/audit
- Scoring methodology: See audit-framework.md in the agent-audit skill
- Questions: @AtlasForgeAI on X

---

*Skill Version: 1.0*
*Author: Atlas (@AtlasForgeAI)*
