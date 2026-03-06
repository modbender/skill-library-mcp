# 🛡️ skill-trust-auditor

**Audit any ClawHub skill for security risks BEFORE you install it.**

## 🛠️ Installation

### 1. Ask OpenClaw (Recommended)
Tell OpenClaw: *"Install the skill-trust-auditor skill."* The agent will handle the installation and configuration automatically.

### 2. Manual Installation (CLI)
If you prefer the terminal, run:
```bash
clawhub install skill-trust-auditor
```

## What it does

1. Fetches the target skill's `SKILL.md` + all referenced scripts
2. Runs 52 regex-based pattern checks against known attack vectors
3. Calculates a **Trust Score (0-100)** with detailed findings
4. Optionally uses **LLM-as-judge** (Claude Haiku) for ambiguous curl intent

## Trust Score

| Score | Verdict | Action |
|-------|---------|--------|
| 90-100 | ✅ SAFE | Install freely |
| 70-89 | ⚠️ CAUTION | Review flagged items |
| 50-69 | 🟠 RISKY | Only if you understand the risks |
| 0-49 | 🔴 DO NOT INSTALL | High probability of malicious intent |

## Risk patterns detected

- **HIGH** (-30 pts): `process.env` access, `curl | bash`, reverse shells, base64 payloads, reading `~/.openclaw` secrets, data exfiltration via POST
- **MEDIUM** (-10 pts): External API calls, file writes outside workspace, reading MEMORY.md
- **LOW** (-3 pts): Standard web fetches, workspace-only reads

## Usage

Just tell your agent:

> "Audit steipete/some-skill before I install it"

Or integrate into your install flow:

```bash
bash scripts/audit.sh steipete/some-skill
bash scripts/audit.sh steipete/some-skill --llm    # with LLM analysis
bash scripts/audit.sh steipete/some-skill --json-only  # machine-readable
```

## Requirements

- Python 3.10+
- `clawhub` CLI (optional, for fetching skill content)
- Anthropic API key (optional, for `--llm` mode)

## Philosophy

- **Zero trust by default** — every skill must prove it's safe
- **Explainable** — every deduction shows exact file, line, and match
- **White Box** — no black-box scoring; all rules are in `patterns.json`
- **ClawHavoc-aware** — patterns specifically target known Feb 2026 attack vectors

## License

MIT
