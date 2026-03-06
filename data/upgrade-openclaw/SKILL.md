---
name: upgrade-openclaw
description: |
  Upgrade OpenClaw and discover new features, hooks, and config improvements.
  Use when: user explicitly says "upgrade openclaw", "update openclaw", "check for openclaw updates",
  or asks to "see what's new in openclaw". Runs the update, audits current setup, and proposes
  optimizations for user approval.
metadata:
  {
    "openclaw":
      {
        "emoji": "🚀",
        "author": "decentraliser",
        "requires": { "bins": ["openclaw", "curl", "clawhub"] }
      }
  }
---

# Upgrade OpenClaw

**Stay on the edge. Update, audit, discover, propose. Latest features, always.**

## Trigger

This skill activates when the user says:
- "upgrade openclaw"
- "update openclaw"
- "check for openclaw updates"
- "what's new in openclaw"

## Settings

On first run, prompt user for preferred sub-agent model and save to `settings.json`:

```json
{
  "subagentModel": "anthropic/claude-sonnet-4-6"
}
```

> ⚠️ **Privacy note:** If you choose an external provider (e.g. `gpt-4o`, `claude-*`), your local
> OpenClaw config and environment details will be sent to that provider during the upgrade run.
> Prefer a locally-hosted model or your primary trusted provider.

## Procedure

### 1. Check Settings

Look for `settings.json` in this skill's directory. If `subagentModel` not set, ask:

> "Which model for upgrade sub-agents? (e.g., `claude-sonnet-4-6`, `deepseek-chat`). Note: external providers will receive your config data."

Save choice to `settings.json`.

### 2. Check Prerequisites

Verify required binaries are present before proceeding:

```bash
which openclaw && openclaw --version
which curl
which clawhub && clawhub -V
```

Abort and instruct the user to install missing binaries if any are not found.

### 3. Run Update

```bash
openclaw update
```

### 4. Discover What's New

```bash
openclaw --version
curl -s https://docs.openclaw.ai/llms.txt | head -100
```

Check:
- Config templates: `github.com/openclaw/openclaw/tree/main/docs/reference/templates`
- Changelog: GitHub releases

### 5. Audit Current Setup

```bash
openclaw hooks list
openclaw doctor --non-interactive
```

Look for:
- New hooks not enabled
- Doctor recommendations not applied
- Unused config options
- Relevant new ClawHub skills

### 6. Present Findings

```markdown
## 🔍 Post-Upgrade Report

### New Features
- [Feature]: Description

### Recommended Config Changes
| Setting | Current | Recommended | Why |
|---------|---------|-------------|-----|

### New Hooks Available
- hook-name: Description

### New Skills Worth Installing
- skill-name: Description

### Doctor Recommendations
- [Items from openclaw doctor]

---
**Apply these improvements?** (yes/no/select)
```

### 7. Apply with Approval

**Never apply without explicit user approval.**

Wait for the user to reply "yes", "apply", or select specific items. Do not proceed on ambiguous input.

Spawn sub-agent (using model from `settings.json`) to:
- Config changes via `gateway config.patch`
- Hook enablement via `openclaw hooks enable <hook>`
- Skill install via `clawhub install <skill>`
