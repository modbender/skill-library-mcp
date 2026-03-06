# 🔴 RedLine

**Never hit the red line again.** Live usage checkers for Claude.ai (Max/Pro) and OpenAI (Plus/Pro/Codex) that give your agent real-time awareness of remaining budget — so it can go full-send when limits are fresh and automatically conserve when they're running low.

Built for [OpenClaw](https://github.com/openclaw/openclaw) agents but the scripts work standalone too.

## Why this exists

AI agents on subscription plans (Anthropic Max, OpenAI Plus/Pro) have rolling rate windows — but no built-in way to check how much is left. Your agent burns through limits at 2 PM, then sits useless until the window resets. Or worse, it rations everything all day "just in case."

This skill gives your agent **live rate-limit awareness**:
- **`claude-usage`** — 5-hour window, weekly window, extra credits, model-specific buckets (Opus/Sonnet) via the Anthropic OAuth API
- **`openai-usage`** — Primary/secondary rate windows, credits balance via the ChatGPT API
- **4-tier pacing** — Automatic throttle from GREEN (full operations) → YELLOW (skip sub-agents) → ORANGE (essential only) → RED (critical only, warn user)

The result: **maximum token efficiency at all hours.** Your agent runs at full capacity when budget allows and gracefully degrades when it doesn't — no surprises, no dead periods.

## Quick start

```bash
# Claude usage (requires `claude login` for OAuth token)
./scripts/claude-usage

# OpenAI usage (requires OpenClaw auth or manual token setup)
./scripts/openai-usage

# JSON output for programmatic use
./scripts/claude-usage --json
./scripts/openai-usage --json
```

## Sample output

```
  Claude Usage (default_claude_max_5x)
  ────────────────────────────────────────
    5-Hour  ████████░░░░░░░░░░░░ 61% left  resets 09:00 PM Feb 17
    Weekly  ██░░░░░░░░░░░░░░░░░░ 88% left  resets 08:00 PM Feb 23
   Credits  ████████████████████ 0% left  $5044/5000 used

  OpenAI Usage  plan: plus
    5h  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 100% left  resets 10:50 PM MST
   Day  ██████████░░░░░░░░░░░░░░░░░░░░ 66% left  resets 9:15 AM MST
  Credits: $882.99
```

## Pacing tiers

| Tier | Remaining | Agent behavior |
|------|-----------|----------------|
| 🟢 GREEN | >50% | Normal operations |
| 🟡 YELLOW | 25–50% | Skip sub-agents, defer non-urgent work |
| 🟠 ORANGE | 10–25% | Essential replies only |
| 🔴 RED | <10% | Critical only, warn user |

## Requirements

- Python 3.8+
- **Claude checker:** macOS Keychain with Claude Code OAuth token (`claude login`)
- **OpenAI checker:** OpenClaw auth-profiles with `openai-codex` profile, OR manual token

## As an OpenClaw skill

```bash
clawhub install redline
```

Then add the pacing logic to your `HEARTBEAT.md` — see [SKILL.md](SKILL.md) for details.

## License

MIT
