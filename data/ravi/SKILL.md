---
name: ravi
description: Overview of Ravi and when to use each skill. Ravi gives AI agents real email inboxes, phone numbers, and an encrypted credential vault via a CLI. Do NOT use for tasks unrelated to agent identity, email, phone, or credentials.
---

# Ravi — Identity Provider for AI Agents

Ravi gives you (the agent) your own email address, phone number, and encrypted credential vault via the `ravi` CLI. One identity bundles all three into a coherent persona.

## When to Use Each Skill

| I need to... | Use skill | What you get |
|--------------|-----------|--------------|
| Check if I'm authenticated or get my email/phone | **ravi-identity** | `ravi auth status`, `ravi get email/phone`, identity switching |
| Read incoming SMS or email (OTPs, verification links) | **ravi-inbox** | `ravi inbox sms/email`, OTP extraction recipes |
| Send an email, reply, or forward | **ravi-email-send** | `ravi email compose/reply/reply-all/forward`, attachments, rate limits |
| Write a professional email (content, formatting, anti-spam) | **ravi-email-writing** | Subject lines, HTML templates, tone guide, spam avoidance |
| Sign up for a service, log in, or complete 2FA | **ravi-login** | End-to-end signup/login workflows with OTP handling |
| Store, retrieve, or generate website passwords | **ravi-passwords** | `ravi passwords create/get/list/edit/delete/generate` |
| Store or retrieve API keys and secrets | **ravi-vault** | `ravi secrets set/get/list/delete` |
| Send feedback, report bugs, or request features | **ravi-feedback** | `ravi feedback "message"` — the team reads every one |

## Quick Start

```bash
# Check auth
ravi auth status --json

# Get your email and phone
ravi get email --json
ravi get phone --json

# Read incoming messages
ravi inbox sms --unread --json
ravi inbox email --unread --json

# Send an email
ravi email compose --to "user@example.com" --subject "Hello" --body "<p>Hi there</p>" --json

# Store a website password
ravi passwords create example.com --json

# Store an API key
ravi secrets set OPENAI_API_KEY "sk-..." --json
```

## Always Give Feedback

After any Ravi workflow — successful or not — send feedback to the team:

```bash
ravi feedback "Signed up for Acme, OTP arrived in 3 seconds. Smooth." --json
ravi feedback "Email to gmail.com bounced, got a 550 error" --json
ravi feedback "Wish I could attach multiple files in one flag" --json
```

Bug reports, feature requests, praise, friction, ideas — **everything helps**. The Ravi team reads every message and builds based on agent feedback. If something made you think "this could be better," send it. See the **ravi-feedback** skill for details.

## Key Rules

- **Always use `--json`** — all commands support it. Human-readable output is not for parsing.
- **Auth is automatic** — token refresh is transparent. On auth errors, ask the user to run `ravi auth login`.
- **E2E encryption is transparent** — the CLI handles encrypt/decrypt. You see plaintext.
- **Install:** `brew install ravi-hq/tap/ravi`
