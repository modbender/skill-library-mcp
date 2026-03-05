---
name: m365-spam-manager
description: Microsoft 365 spam folder manager for Outlook/Exchange mailboxes. Automatically analyzes junk/spam emails, calculates a suspicious score based on structural patterns (missing unsubscribe links, poor language, suspicious domains, wrong character sets, etc.), and helps clean up the junk folder. Supports review mode (default) where user approves each action, and automatic mode for batch processing. Works with shared mailboxes via --mailbox flag. Related keywords: Outlook, Exchange Online, spam filter, junk email, phishing, email security. **Token cost:** ~500-1.5k tokens per use.
---

# M365 Spam Manager (Microsoft Graph)

## Installation

Requires Node.js + npm install in the skill folder:
```bash
cd skills/m365-spam-manager
npm install
```

## Setup

Uses the same profile/credentials as `m365-mailbox`. Ensure you have a profile configured:
```bash
node skills/m365-mailbox/scripts/setup.mjs --profile tom-business ...
```

## Usage

### Review mode (default) — user must approve each action

```bash
# Analyze junk folder and show suspicious scores (review mode - default)
node skills/m365-spam-manager/scripts/analyze.mjs --profile tom-business-mail --mailbox radman@e-ola.com

# Move a false positive to inbox (requires confirmation)
node skills/m365-spam-manager/scripts/move-to-inbox.mjs --profile tom-business-mail --mailbox radman@e-ola.com --id <MSG_ID>

# Move confirmed spam to learning folder
node skills/m365-spam-manager/scripts/move-to-learning.mjs --profile tom-business-mail --mailbox radman@e-ola.com --id <MSG_ID>
```

### Automatic mode (no confirmation)

```bash
# Auto-clean: move high-confidence spam to learning, medium to review
node skills/m365-spam-manager/scripts/auto-clean.mjs --profile tom-business-mail --mailbox radman@e-ola.com --threshold 80
```

## Suspicious Score Calculation

The analyzer calculates a score (0-100) based on:

| Pattern | Points | Description |
|---------|--------|-------------|
| No unsubscribe link | +20 | Legitimate marketing must have one |
| Suspicious sender domain | +15 | Free email, misspellings, random strings |
| All caps subject | +10 | Spam often shouts |
| Excessive punctuation | +10 | !!!, ???, $$$ |
| Suspicious keywords | +15 | crypto, win, free, urgent, verify, bank, password, ... |
| Mismatched language | +10 | Subject in DE, body EN or vice versa |
| Known scam patterns | +25 | "Attention - suspected SPAM", fake invoices |
| Free email provider | +10 | gmail, yahoo, hotmail in From (not Reply-To) |
| No DKIM/SPF indication | +5 | Graph doesn't show auth results |

### Score thresholds

- **0-30**: Low suspicion — likely legitimate
- **31-70**: Medium — review recommended
- **71-100**: High — almost certainly spam

## Policy

This skill respects the same policy as `m365-mailbox`:
- `read`: autonomous (analyze, list)
- `move`: controlled (move to inbox/learning folder)

In review mode, the script always prompts for confirmation before moving emails.
