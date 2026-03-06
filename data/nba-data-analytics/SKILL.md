---
name: daredevil_nba_sportsdata
description: Request NBA sports data (schedule, boxscore, standings, injuries, roster, etc.) from the Daredevil seller. Payment per request via x402.
---

# Daredevil NBA Sports Data

Use this skill in two ways:

1. **Raw data** — When the user asks for NBA schedule, scores, boxscore, standings, injuries, team roster, or player stats, request data from the Daredevil seller. Each request is paid via x402 (small fee per query).
2. **Analysis / prediction** — When the user asks for an opinion, recommendation, or "what do you think?" about a game or matchup (e.g. "What do you think about the LAL and CHI game?"), first retrieve the necessary raw data via this skill, then **synthesize** an answer using your LLM. Synthesis runs on your side (the buyer); the seller only returns raw data.

## Base URL

**https://daredevil-acp-seller-production.up.railway.app**

- Health check (no payment): `GET /health`
- Data (payment required): `POST /v1/data` with JSON body and x402 payment headers

## Request (POST /v1/data)

Send a JSON body with:

| Field | Required | Description |
|-------|----------|-------------|
| `dataType` | Yes | One of: `schedule`, `next_game`, `boxscore`, `live_score`, `play_by_play`, `standings`, `injuries`, `team_roster`, `player_stats` |
| `teamName` | No | Team alias (e.g. LAL, BOS) or full name (Lakers, Celtics) |
| `date` | No | Date in YYYY-MM-DD format |
| `endDate` | No | End date for schedule range (YYYY-MM-DD) |
| `daysAhead` | No | For schedule: number of days ahead (e.g. 7 for one week) |
| `maxDaysAhead` | No | For next_game: max days to look ahead (default 14) |
| `nextGameLimit` | No | For next_game: max number of games to return (default 1) |
| `gameId` | No | Sportradar game ID when you need a specific game (boxscore, live_score, play_by_play) |

## Data types

- **schedule** — NBA games for a date or range (use `date`, `endDate`, or `daysAhead`; optional `teamName` to filter).
- **next_game** — Next upcoming game(s) for a team (`teamName` required; optional `nextGameLimit`, `maxDaysAhead`).
- **boxscore** — Full boxscore for a game (`gameId` or `teamName` for today’s game).
- **live_score** — Live score for a game (`gameId` or `teamName` for today’s game).
- **play_by_play** — Play-by-play for a game (`gameId` or `teamName` for today’s game).
- **standings** — NBA standings (optional `date`).
- **injuries** — Current injury report.
- **team_roster** — Team roster (`teamName` required).
- **player_stats** — Player stats (typically requires `gameId` or context from a game).

## Payment (x402)

The server requires payment for `POST /v1/data`. Use an x402-capable HTTP client:

1. First request without payment → server responds **402 Payment Required** with payment details in the `Payment-Required` header (or equivalent).
2. Create payment payload and sign with the user’s wallet (same network as server: Base Sepolia testnet `eip155:84532` or Base mainnet `eip155:8453`).
3. Retry `POST /v1/data` with the same body plus the x402 payment header(s). On success you get **200** and a JSON body with `dataType`, `result` (JSON string), and `timestamp`.

If your environment has a tool or script that performs x402-paid HTTP requests, use it with the base URL and request body above. Otherwise you may need to use `bash` with a CLI or script that supports x402 (e.g. Node script using `@x402/core` client).

## Response

Success (200) body shape:

```json
{
  "dataType": "schedule",
  "result": "<JSON string of the actual data>",
  "timestamp": "2025-02-21T...",
  "gameStatus": "optional for live games"
}
```

Parse `result` as JSON to get the underlying schedule, boxscore, standings, etc.

## Examples (raw data)

- "What's the Lakers schedule this week?" → `dataType: "schedule", teamName: "LAL", daysAhead: 7`
- "When is the Celtics' next game?" → `dataType: "next_game", teamName: "BOS"`
- "NBA standings" → `dataType: "standings"`
- "Lakers roster" → `dataType: "team_roster", teamName: "LAL"`
- "Current NBA injuries" → `dataType: "injuries"`

## Analysis and synthesis workflow

When the user asks for an **analysis**, **prediction**, or **opinion** (e.g. "What do you think about the LAL and CHI game?", "Who do you think will win Lakers vs Celtics?", "Should I bet on the Bulls tonight?"):

1. **Determine required data** — For a matchup or game question, typically fetch:
   - `next_game` for each team (or `schedule` with `teamName` and `daysAhead`) to get game time and matchup.
   - `standings` for context on team records.
   - `injuries` for key absences (optional but recommended).
   - `boxscore` or `live_score` if the game is today and you need current state.
   - `team_roster` only if roster context is relevant.
2. **Request that data** — Call `POST /v1/data` (with x402 payment) for each needed `dataType`. Parse each `result` as JSON.
3. **Synthesize** — Using your LLM, produce a short analysis or prediction based **only** on the retrieved data. Do not invent stats or facts. Use the prompt template below (or see `prompts/analyze-game.md`) with the user's question and the concatenated/summarized retrieved data.

### Synthesis prompt template

After you have the raw data, call your LLM with a prompt like this (fill in the placeholders):

```
You are an NBA analyst. The user asked: "{{user_question}}"

Below is raw data from the Daredevil NBA API (schedule, boxscore, standings, injuries, etc.). Use only this data to produce a short, clear analysis or prediction. Do not invent facts or stats.

---
{{retrieved_data}}
---

Provide your analysis or prediction in a few sentences.
```

- `{{user_question}}` — The user's exact question (e.g. "What do you think about the LAL and CHI game?").
- `{{retrieved_data}}` — The JSON or a concise summary of the API responses you received (schedules, standings, injuries, boxscore, etc.). If large, summarize key fields (teams, dates, scores, records, notable injuries) rather than pasting entire payloads.

Then return the LLM's synthesized answer to the user.

### Examples (analysis)

- "What do you think about the LAL and CHI game?" → Fetch `next_game` for LAL and CHI, `standings`, and optionally `injuries`; then run the synthesis prompt with that data.
- "Who wins Lakers vs Celtics?" → Same: next games / schedule for both, standings, injuries; then synthesize.
- "Give me a pick for tonight's games" → Fetch `schedule` for today (or `daysAhead: 1`), `standings`, `injuries`; then synthesize picks from the data.

Always use the base URL above and include x402 payment when calling `POST /v1/data`.
