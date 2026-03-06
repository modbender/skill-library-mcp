---
name: hercycle
description: Women's cycle intelligence companion. Reads Whoop biometric data (HRV, recovery, sleep, skin temperature) and menstrual cycle phase to understand which hormonal "season" the user is in — and takes smart, phase-aware actions. Use when the user asks about their cycle phase, energy, mood, what to eat, how hard to train, when to schedule important meetings, or wants any Whoop-powered recommendation tailored to their hormonal cycle. NOT a period tracker — a biometric intelligence layer that treats the cycle as a source of power, not a problem.
---

# HerCycle — Women's Cycle Intelligence

Built on the insight that women's biology is cyclical, not linear. Every month has four distinct hormonal seasons — each unlocking different cognitive, emotional, and physical capabilities. HerCycle reads your biometrics and tells you which season you're in, then takes action accordingly.

## The Four Seasons

| Season | Phase | Days | What's Amplified |
|--------|-------|------|-----------------|
| 🌑 Winter | Menstrual | 1–5 | Introspection, pattern recognition, deep insight, rest & recovery |
| 🌱 Spring | Follicular | 6–14 | Creativity, optimism, new ideas, social energy, starting things |
| ☀️ Summer | Ovulation | ~14 | Communication, charisma, negotiation, peak performance, visibility |
| 🍂 Autumn | Luteal | 15–28 | Detail orientation, completion, editing, boundaries, deep focus |

## Data Sources

HerCycle reads from:
- **Whoop API** — HRV, recovery score, sleep quality, skin temperature (ovulation signal)
- **Cycle tracking** — stored in WhoopClaw DB (`cycle_tracking` table), or inferred from skin temp patterns
- **Phase inference** — if no explicit cycle log, estimate phase from skin temp trend + HRV patterns

See `references/whoop-api.md` for data access patterns.

## Action Modules

Actions are pluggable. Each module takes the current phase + biometrics and returns a recommendation or triggers an action.

Current modules:
- **🎵 Music** — Spotify mood matching via a phase-aware playlist engine (see your WhoopClaw `spotify_engine.py` or bring your own)
- **💪 Training** — Push hard (follicular/ovulation) vs restore (menstrual/luteal)
- **🥗 Nutrition** — Iron-rich (menstrual), protein/carb cycling (luteal), light & fresh (ovulation)
- **📅 Calendar** — Phase-aware scheduling nudges (big meetings → ovulation, deep work → luteal)
- **💬 Social** — Energy level signal ("high charisma window" vs "protect your bandwidth")

To add a new action module: see `references/action-modules.md`.

## Usage

**Check current phase:**
> "What phase am I in?" / "What's my cycle season today?"

**Phase-aware recommendation:**
> "Should I push hard at the gym today?"
> "What should I eat this week?"
> "Is this a good week for a big presentation?"

**Trigger an action:**
> "Play music for my phase" / "Give me a playlist for my cycle phase"

## Setup Requirements

HerCycle requires a running WhoopClaw instance — an open-source FastAPI backend that handles Whoop OAuth, cycle tracking, and biometric storage. Search GitHub for "WhoopClaw" to find an implementation, or build your own against the Whoop Developer API.

**Prerequisites:**
1. **Whoop API credentials** — register at [developer-dashboard.whoop.com](https://developer-dashboard.whoop.com) to get your `WHOOP_CLIENT_ID` and `WHOOP_CLIENT_SECRET`
2. **WhoopClaw running locally** — clone, configure `.env`, and start the server (`uvicorn main:app`)
3. **Whoop account connected** — complete the OAuth flow via WhoopClaw's `/whoop/authorize` endpoint

Once running, configure `WHOOPLAW_BASE_URL` to point to your instance (default: `http://localhost:8000`).

Key endpoints HerCycle uses:
- `GET /whoop/recovery` — latest recovery + HRV
- `GET /cycle/current-phase?telegram_id=<id>` — current cycle phase
- `GET /cycle/predictions?telegram_id=<id>` — next period prediction
- `GET /whoop/metrics/skin-temp` — skin temperature trend (ovulation signal)

Always pull live data before making recommendations. Do not rely on stale cached values.

## Philosophy

> *"Every month I experience four seasons... in this season, certain sensitivity and capacity is amplified."* — Chloé Zhao, Oscar-winning director (BBC 100 Women)

The goal is not to manage around the cycle. It's to move with it — scheduling, eating, training, socialising, and creating in alignment with what's naturally amplified. The cycle is the intelligence. HerCycle makes it legible.
