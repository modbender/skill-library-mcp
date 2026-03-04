# WhatsApp FAQ Bot

Turn markdown files into a searchable FAQ knowledge base for your WhatsApp assistant.

## Features

- **Markdown Import** — H2 headings = questions, body = answers
- **Fuzzy Search** — TF-IDF-like matching finds answers even with typos
- **Confidence Scores** — Know how well each match fits (0.0-1.0)
- **Tags** — Organize FAQs by category
- **Export** — JSON or Markdown export for backup/sharing
- **No Dependencies** — Pure Python, no external libraries needed
- **No API Keys** — Works entirely offline

## Installation

### As an OpenClaw/ClawHub skill

```bash
clawhub install whatsapp-faq-bot
```

### Standalone

```bash
git clone https://github.com/YOUR_USERNAME/whatsapp-faq-bot.git
cd whatsapp-faq-bot
# No dependencies needed — pure Python 3.10+
```

## Usage

```bash
# Create knowledge base
python scripts/faqbot.py init

# Import from markdown
python scripts/faqbot.py import company-faqs.md

# Search
python scripts/faqbot.py search "how do I contact support"
```

## Use Cases

- **Business FAQ bots** — Auto-answer common customer questions on WhatsApp
- **Internal knowledge base** — Team onboarding Q&A
- **Support deflection** — Answer tier-1 questions automatically
- **Documentation search** — Quick lookup across multiple FAQ documents

## Data Storage

Data is stored in `~/.faq-bot/` by default. Override with `FAQ_BOT_DIR` environment variable.

## License

MIT

## Author

Built by OpenClaw Setup Services — Professional AI agent configuration and custom skill development.

**Need a custom FAQ bot for your business?** Contact us for tailored WhatsApp automation.
