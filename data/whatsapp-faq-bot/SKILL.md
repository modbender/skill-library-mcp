---
name: whatsapp-faq-bot
description: Build and query a FAQ knowledge base from markdown files. Use when asked to create a FAQ bot, set up automatic answers, build a knowledge base, add FAQ entries, search FAQs, or answer common questions from a knowledge base. Perfect for WhatsApp business bots.
---

# WhatsApp FAQ Bot

Build a searchable knowledge base from markdown files. Match incoming questions to the best FAQ answer using fuzzy text matching.

## Quick Start

```bash
# Initialize a new FAQ knowledge base
python scripts/faqbot.py init

# Add a FAQ entry interactively
python scripts/faqbot.py add -q "What are your business hours?" -a "We are open Monday to Friday, 9 AM to 6 PM CET."

# Import FAQs from a markdown file
python scripts/faqbot.py import faq-source.md

# Search for the best matching answer
python scripts/faqbot.py search "when are you open"

# List all FAQ entries
python scripts/faqbot.py list

# Export all FAQs to markdown
python scripts/faqbot.py export --format md -o faqs-export.md

# Export as JSON
python scripts/faqbot.py export --format json -o faqs.json

# Remove a FAQ entry by ID
python scripts/faqbot.py remove 3

# Get stats about the knowledge base
python scripts/faqbot.py stats
```

## Commands

| Command | Args | Description |
|---------|------|-------------|
| `init` | | Create a new empty knowledge base |
| `add` | `-q QUESTION -a ANSWER [-t TAGS]` | Add a single FAQ entry |
| `import` | `<file.md>` | Import FAQs from markdown (H2 = question, body = answer) |
| `search` | `<query> [--top N] [--threshold T]` | Find best matching answer(s) |
| `list` | `[--tag TAG]` | List all FAQ entries |
| `remove` | `<id>` | Remove a FAQ entry |
| `export` | `[--format md\|json] [-o FILE]` | Export knowledge base |
| `stats` | | Show knowledge base statistics |

## Markdown Import Format

```markdown
## What are your business hours?
We are open Monday to Friday, 9 AM to 6 PM CET.
Weekend support is available via email only.

## How do I reset my password?
Go to Settings > Account > Reset Password.
You will receive an email with a reset link.

## What payment methods do you accept?
We accept:
- Credit/debit cards (Visa, Mastercard)
- PayPal
- Bank transfer (EU only)
```

Each H2 heading becomes a question, the body below becomes the answer.

## Search Scoring

- Uses TF-IDF-like fuzzy matching on question text
- Returns confidence score (0.0 to 1.0)
- Default threshold: 0.3 (adjustable with `--threshold`)
- Returns top 3 matches by default (adjustable with `--top`)

## Integration with OpenClaw

This skill is designed to work as a WhatsApp FAQ bot. When a user asks a question, the agent can use the `search` command to find the best match and respond automatically. Configure it in your cron or agent system prompt.
