# Telnyx Skill for Clawdbot

Telnyx API integration for Clawdbot: messaging, phone numbers, webhooks, and more.

## Quick Start

```bash
# 1. Install
npm install -g @telnyx/api-cli

# 2. Setup
telnyx auth setup
# Paste your API key from: https://portal.telnyx.com/#/app/api-keys

# 3. Test
telnyx number list
```

## Usage

```bash
# Send message
telnyx message send --from +1234567890 --to +9876543210 --text "Hello!"

# List numbers
telnyx number list

# Search numbers
telnyx number search --country US --npa 415

# Check webhooks
telnyx debugger list --status failed

# View account
telnyx account get
```

## Companion Skills

This skill coordinates with two companion skills for full account lifecycle management:

| Skill | Purpose | Install |
|-------|---------|---------|
| **telnyx-bot-signup** | Account creation or signin (API key generation) | `clawhub install telnyx-bot-signup` |
| **telnyx-freemium-upgrade** | Upgrade freemium → professional tier | `clawhub install telnyx-freemium-upgrade` |

When used through Clawdbot, handoffs happen automatically:
- **No API key?** → `telnyx-bot-signup` creates one (works for both new and existing accounts)
- **Freemium wall?** → `telnyx-freemium-upgrade` initiates GitHub-based identity verification
- **Key expired?** → `telnyx-bot-signup` generates a fresh key

See `SKILL.md` for the full coordination logic and decision tree.

## For Clawdbot

Once installed, use Telnyx commands directly in Clawdbot:

```bash
telnyx number list
telnyx message send --from +1234567890 --to +9876543210 --text "Hi"
```

See `SKILL.md` for full documentation.
