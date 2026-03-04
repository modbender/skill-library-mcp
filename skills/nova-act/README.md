# Nova Act Browser Automation Skill

AI-powered browser automation using Amazon Nova Act with built-in safety guardrails.

## Data & Privacy Notice

**What this skill accesses:**
- **Reads:** `NOVA_ACT_API_KEY` environment variable or `~/.openclaw/openclaw.json` (your API key)
- **Writes:** Nova Act trace files in the current working directory (screenshots, session recordings)

**Trace files may contain:** Screenshots of visited pages, full page content, browser actions and AI decisions. Review and delete trace files after use if they contain sensitive content.

## Safety Guardrails

This skill implements robust safety guardrails to prevent unintended real-world actions.

**ALWAYS stop before actions that cause monetary impact, external communication, account creation, or data modification.**

### Material Impact Detection

The bundled script (`scripts/nova_act_runner.py`) defines `MATERIAL_IMPACT_KEYWORDS` covering:
- **Monetary**: buy, purchase, checkout, pay, subscribe, donate, order
- **Communication**: post, publish, share, send, email, message, tweet
- **Account creation**: sign up, register, create account, join
- **Submissions**: submit, apply, enroll, book, reserve
- **Destructive**: delete, remove, cancel

When detected, `apply_safety_guardrails()` appends safety instructions to the actual task prompt sent to Nova Act, preventing it from completing irreversible actions. This is an active behavioral gate, not just a warning.

### Safety Guarantees

The skill will **NEVER:**
- Complete actual purchases or financial transactions
- Create real accounts or sign up for services
- Post content publicly on any platform
- Send emails, messages, or communications
- Submit forms that cause irreversible real-world actions

The skill will **ALWAYS:**
- Stop before any action that could have material real-world impact
- Ask for explicit user confirmation before taking irreversible actions
- Report findings rather than completing destructive operations
- Document safety stops in output when material-impact actions are detected

### Cookbook

See `references/nova-act-cookbook.md` for detailed safety patterns, including:
- ALWAYS stop testing before actions that cause monetary impact, external communication, account creation, or data modification
- Safe workflow examples (flight search, e-commerce, form testing, booking flows)
- Best practices for Nova Act usage

## Installation

### Requirements

| Requirement | Details |
|-------------|---------|
| **Runtime** | `uv` (Python package runner) |
| **API Key** | `NOVA_ACT_API_KEY` environment variable |
| **Get Key** | https://nova.amazon.com/dev/api |

### Setup

1. Install uv: `brew install uv`
2. Get a free API key from https://nova.amazon.com/dev/api
3. Set the environment variable: `export NOVA_ACT_API_KEY="your-key-here"`

## Usage

Ask your AI assistant to perform browser automation tasks:

```
Search for flights from SFO to JFK next week
Extract product prices from example.com
Check if the contact form on example.com works
```

The skill will automate a real browser, extract data, and report results — stopping before any action with material impact.

## Files

```
nova-act/
├── SKILL.md                          # AI agent instructions
├── README.md                         # This file
├── _meta.json                        # Skill metadata
├── scripts/
│   └── nova_act_runner.py            # Bundled automation runner with safety guardrails
└── references/
    └── nova-act-cookbook.md           # Best practices and safety patterns
```

## License

MIT
