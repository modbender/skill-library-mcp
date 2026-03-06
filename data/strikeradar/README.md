# StrikeRadar - monitor US-Iran strike probability in real time

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-purple)

> **[Agent Skills](https://agentskills.io) format** - works with OpenClaw, Claude Code, Cursor, Codex, and other compatible clients

[StrikeRadar](https://usstrikeradar.com/) by [Yonatan Back](https://buymeacoffee.com/back.yonatan) tracks US-Iran tension across 8 data sources and aggregates them into a single risk score. This skill wraps that data so you can check it from the terminal or let your AI agent query it directly.

## Installation

```bash
npx skills add alexpolonsky/agent-skill-strikeradar
```

Or clone manually:

```bash
# OpenClaw
git clone https://github.com/alexpolonsky/agent-skill-strikeradar ~/.openclaw/skills/strikeradar

# Claude Code
git clone https://github.com/alexpolonsky/agent-skill-strikeradar ~/.claude/skills/strikeradar

# Cursor
git clone https://github.com/alexpolonsky/agent-skill-strikeradar ~/.cursor/skills/strikeradar
```

## Requirements

- Node.js 18+
- No dependencies

## Quick start

Ask your AI agent:
> "What's the current Iran strike risk?"

Or run it as a standalone CLI:
```bash
npx tsx scripts/strikeradar.ts status
```

For quick access, add an alias to your shell profile (adjust the path to where you cloned it):
```bash
alias strikeradar='npx tsx ~/path/to/strikeradar/scripts/strikeradar.ts'
```

Then just:
```bash
strikeradar status
strikeradar signal news
strikeradar pulse
```

Timestamps are in UTC.

## Commands

| Command | Description |
|---------|-------------|
| `status` | All 8 signals with risk scores and total risk |
| `signal <name>` | Deep dive into one signal with history and raw data |
| `pulse` | Live viewer count and activity by country |

Valid signal names: `news`, `connectivity`, `energy`, `flight`, `tanker`, `weather`, `polymarket`, `pentagon`

<details>
<summary>Signal details</summary>

| Signal | Source | What it tracks |
|--------|--------|---------------|
| news | BBC, Al Jazeera | Article alerts, critical count |
| connectivity | Cloudflare Radar | Iran internet status and trend |
| energy | Financial APIs | Brent crude price, volatility |
| flight | OpenSky Network | Aircraft count near Iran, key airlines |
| tanker | OpenSky Network | Military refueling tanker detection |
| weather | OpenWeatherMap | Visibility and conditions over Iran |
| polymarket | Polymarket | Betting odds for US strike |
| pentagon | Location data | Pentagon building activity patterns |
</details>

<details>
<summary>Example output</summary>

```
  US Strike Radar  2026-02-20T07:35:47Z

  Total Risk: 32%
  ██████░░░░░░░░░░░░░░

  news            48%  23 articles, 11 critical
  connectivity    76%  CRITICAL (-61.6%)
  energy           0%  STABLE - $69.77 (+0.0%)
  flight           4%  87 aircraft, 8/8 key airlines
  tanker          10%  1 detected in region
  weather        100%  clear sky
  polymarket       4%  4% odds
  pentagon        10%  Low Activity
```
</details>

## What you can ask

The API returns enough data for questions beyond "what's the overall risk score?":

- "Is something happening with Iran right now? Should I be worried?"
- "How many airlines are still flying over Iran?"
- "Is Iran's internet being shut down? Is it recovering or getting worse?"
- "How many people are watching the strike radar right now?" (a surge usually means something is developing)
- "What are the latest headlines about a US strike on Iran?"
- "Is the situation escalating or calming down?"
- "Are there military refueling tankers near Iran right now?"
- "What do Polymarket bettors think about a US strike on Iran?"
- "Is there unusual late-night activity near the Pentagon?" (the famous Pizza Index)
- "Is the oil price spiking right now?"

## Automation examples

With agents that support scheduled tasks (e.g., OpenClaw cron), you can set up ongoing monitoring:

- "Alert me if the Iran strike risk crosses 50%"
- "Send me a morning briefing every day with all signals and what changed overnight"
- "Warn me at 50%, 65%, and 80% risk levels"
- "Let me know when the situation calms down after a spike"
- "Notify me if Iran's internet starts going down" (often a precursor to escalation)
- "Tell me if there's unusual late-night Pentagon activity"

## How it works

Calls the public API at `api.usstrikeradar.com` and formats the response. No scraping, no auth, no API key needed. Outputs human-readable text in the terminal and JSON with `next_actions` when piped.

## Limitations

- Data refreshes roughly every 30 minutes on the server side
- Risk scores are algorithmic estimates, not intelligence assessments
- No historical data beyond the rolling history array per signal
- Viewer pulse data is approximate

## License

MIT - see [LICENSE](LICENSE).

## Author

[Alex Polonsky](https://alexpolonsky.com) - [GitHub](https://github.com/alexpolonsky) - [Twitter/X](https://x.com/alexpo) - [LinkedIn](https://www.linkedin.com/in/alexpolonsky/)

## References

- [StrikeRadar](https://usstrikeradar.com/) by Yonatan Back - [support his work](https://buymeacoffee.com/back.yonatan)
- [Agent Skills specification](https://agentskills.io/specification)
- [Agent Skills catalog](https://github.com/alexpolonsky/agent-skills)

---

Probability scores are algorithmic estimates from publicly available data, not intelligence assessments. Do not use for personal, financial, or safety decisions.
