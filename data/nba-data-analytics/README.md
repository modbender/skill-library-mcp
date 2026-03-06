# Daredevil NBA Sports Data (OpenClaw Skill)

Request NBA schedule, scores, boxscore, standings, injuries, roster, and more. Payment per request via x402. The agent can also **synthesize** analysis and predictions from this data using your LLM (synthesis runs on your side).

## What it does

- **Schedule** — Games for a date or date range, optional team filter.
- **Next game** — Upcoming game(s) for a team.
- **Boxscore / live score / play-by-play** — Game-level data (by game ID or team for today).
- **Standings** — NBA standings.
- **Injuries** — Current injury report.
- **Team roster** — Roster for a team.
- **Player stats** — Player statistics in context of a game.
- **Analysis / prediction** — For questions like "What do you think about the LAL and CHI game?", the agent fetches the relevant raw data via x402, then uses the prompt template in the skill to synthesize an answer with your LLM (no LLM on the seller).

## How to use

1. Install this skill into your OpenClaw workspace (e.g. via ClawHub: `clawhub install daredevil-nba-sportsdata` or copy the skill folder into your workspace `skills/`).
2. Ask your OpenClaw agent for NBA data or analysis, e.g.:
   - "What's the Lakers schedule this week?"
   - "When is the Celtics' next game?"
   - "NBA standings"
   - "Current injuries"
   - "What do you think about the Lakers vs Bulls game?" (agent fetches data, then synthesizes with your LLM)
3. For raw data, the agent calls the Daredevil API and pays via x402, then returns the data. For analysis/prediction, the agent fetches the needed data first, then uses the skill’s synthesis prompt (see `SKILL.md` and `prompts/analyze-game.md`) to produce an answer.

## Requirements

- OpenClaw workspace with network access.
- Ability to perform x402-paid HTTP requests (wallet on Base Sepolia testnet or Base mainnet, depending on seller config). The skill describes the endpoint and body; the agent needs an x402 client or tool to add payment and send the request.

## Base URL

The skill uses the public Daredevil seller:

**https://daredevil-acp-seller-production.up.railway.app**

- `GET /health` — Health check (no payment).
- `POST /v1/data` — Data request (x402 payment required).

## Request body (POST /v1/data)

JSON with at least `dataType`. Optional: `teamName`, `date`, `endDate`, `daysAhead`, `maxDaysAhead`, `nextGameLimit`, `gameId`. See `SKILL.md` for full schema.

## Troubleshooting

- **402 Payment Required** — Expected when no payment is sent. The agent must retry with x402 payment headers.
- **503** — x402 is unavailable on the server; try again later.
- **400** — Invalid body (e.g. missing or invalid `dataType`). Use one of: schedule, next_game, boxscore, live_score, play_by_play, standings, injuries, team_roster, player_stats.
