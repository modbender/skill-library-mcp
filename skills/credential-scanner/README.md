# Secret Scanner

🔐 Scan your code for leaked secrets, API keys, tokens, passwords, and credentials before they end up in production.

## Features

- **40+ secret patterns** — AWS, Azure, GCP, GitHub, OpenAI, Stripe, Slack, databases, SSH keys, and more
- **Smart filtering** — Skips placeholders, examples, binary files, and lock files
- **Secret masking** — Findings show masked previews so reports are safe to share
- **Multiple outputs** — Markdown reports or JSON for CI/CD integration
- **Zero dependencies** — Uses only Python standard library
- **Severity levels** — Critical, High, Medium, Low with remediation guidance

## Quick Start

```bash
# Scan a project directory
python secret_scanner.py /path/to/project

# JSON output for CI/CD
python secret_scanner.py /path/to/project --json

# Save report to file
python secret_scanner.py /path/to/project -o report.md
```

## What It Detects

| Category | Patterns |
|----------|----------|
| **Cloud** | AWS keys, Azure storage keys/SAS/connection strings, GCP API keys/service accounts |
| **AI/LLM** | OpenAI, Anthropic, Hugging Face API keys |
| **Git Platforms** | GitHub PAT/OAuth, GitLab PAT |
| **Payments** | Stripe live/test keys |
| **Messaging** | Slack tokens/webhooks, Twilio, SendGrid |
| **Databases** | MongoDB, PostgreSQL, MySQL, Redis connection strings |
| **Auth** | JWT tokens, Bearer tokens, Basic auth headers |
| **Crypto** | SSH private keys, PEM certificates |
| **Generic** | Hardcoded passwords, secrets, tokens in config |
| **Package Registries** | NPM auth tokens, PyPI API tokens |
| **Azure Services** | Service Bus connection strings, client secrets |

## Use as Agent Skill

Install this as a Clawdbot/Copilot Agent skill and ask:

- *"Scan this project for leaked secrets"*
- *"Check if there are any API keys in the codebase"*
- *"Audit this repo before I push to GitHub"*

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Clean — no critical or high findings |
| 1 | High severity secrets found |
| 2 | Critical severity secrets found |

## Requirements

- Python 3.7+
- No additional dependencies

## Author

**nirwandogra** — Built for the open agent skills ecosystem.

## License

MIT
