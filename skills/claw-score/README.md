# Claw Score

Get your AI agent's architecture audited. One command, automated submission, email report.

## What is Claw Score?

Claw Score is an agent architecture audit service by [Atlas](https://atlasforge.me). Submit your agent's configuration files and receive a detailed report scoring your agent across six dimensions:

1. **Identity Architecture** — Personality depth, principles, voice
2. **Memory Systems** — Persistence, structure, retrieval patterns  
3. **Security Posture** — Injection defense, trust boundaries
4. **Autonomy Gradients** — Trust levels, escalation patterns
5. **Proactive Patterns** — Heartbeats, background work, initiative
6. **Learning Architecture** — Improvement loops, regression tracking

## Scoring Tiers

| Score | Tier | Description |
|-------|------|-------------|
| 1.0–1.9 | Shrimp | Just getting started |
| 2.0–2.9 | Crab | Structure emerging |
| 3.0–3.9 | Lobster | Solid capability |
| 4.0–4.5 | King Crab | Refined architecture |
| 4.6–5.0 | Mega Claw | Best-in-class |

## Installation

```bash
# Clone into your agent's skills directory
git clone https://github.com/AtlasForgeAI/claw-score skills/claw-score
```

## Usage

Tell your agent:

```
"Run a Claw Score audit and send the report to your@email.com"
```

The skill will:
1. Read your workspace config files (AGENTS.md, SOUL.md, etc.)
2. Automatically sanitize credentials and PII
3. Submit to Atlas for audit
4. You'll receive a detailed report via email within 24-48 hours

## Manual Submission

If you prefer to submit manually:

```bash
./skills/claw-score/submit.sh . your@email.com
```

Or email your files directly to: atlasai@fastmail.com

## What Gets Submitted

- `AGENTS.md` — Main agent instructions
- `SOUL.md` — Personality/identity
- `MEMORY.md` — Long-term memory config
- `TOOLS.md` — Tool configuration
- `SECURITY.md` — Security rules
- `HEARTBEAT.md` — Proactive behavior
- `USER.md` — User context
- `IDENTITY.md` — Agent identity
- File tree listing (structure only)

## What Gets Redacted

Before submission, the skill automatically removes:
- API keys (`sk-*`, `xoxb-*`, `ghp_*`, etc.)
- Email addresses
- Phone numbers
- IP addresses
- Environment variable values

## Privacy

- Files are transmitted directly to Atlas for auditing
- Data is NOT stored beyond the audit session
- Reports are private unless you share them
- No code execution — only .md files analyzed

## Learn More

- **Landing page**: https://atlasforge.me/audit
- **Twitter**: [@AtlasForgeAI](https://x.com/AtlasForgeAI)

## License

MIT
