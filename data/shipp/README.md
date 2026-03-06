# Shipp Skill

Teaches AI agents how to integrate with the [Shipp](https://shipp.ai) real-time data connector — the fastest way to get live event streams into your app.

## What This Skill Provides

The `SKILL.md` file gives your agent full context on:

- **Authentication** — Multiple methods supported (Bearer token, query parameter, headers)
- **Connections** — Create reusable live-data queries with natural-language `filter_instructions`
- **Running Connections** — Poll for real-time events with cursor-based pagination
- **Schedule** — Discover upcoming and recent games by sport
- **Data Shape** — Schema-flexible `data[]` responses and how to handle them defensively
- **Error Handling** — Status codes, hints, and retry strategies

## When to Use This Skill

Use the Shipp skill when your agent needs to:

- Fetch real-time event data (sports play-by-play, scoring, game state)
- Discover upcoming games and schedules
- Build live dashboards, alert systems, or agent loops powered by fresh data
- Feed real-time context into AI decision-making pipelines

## Getting Started

### 1. Get an API Key

Sign up at [platform.shipp.ai](https://platform.shipp.ai/signup) and create an API key from the dashboard.

### 2. Environment Variables

Never hardcode API keys. Store them as environment variables or in a `.env` file:

```
SHIPP_API_KEY=shipp_01JK2MF5A9NQR7WX3YGVB8DTCH
```

### 3. Core Workflow

The integration pattern is intentionally simple:

1. **Discover** — Use the schedule endpoint to find games and IDs
2. **Create a connection** — Describe what you want in plain English via `filter_instructions`
3. **Run the connection** — Poll for events, using `since_event_id` for efficient cursor-based pagination
4. **Process data defensively** — Every field in `data[]` is optional; handle missing keys gracefully

## Example Project: Alph Bot

[**Alph Bot**](https://gitlab.com/outsharp/shipp/alph-bot) is an open-source automated trading bot that uses Shipp for real-time sports data, Claude AI for probability estimation, and Kalshi for prediction market trading.

### How Alph Bot Uses Shipp

1. **Game discovery** — Lists available games via `GET /api/v1/sports/{sport}/schedule`
2. **Connection creation** — Creates a Shipp connection scoped to a specific game with targeted `filter_instructions`
3. **Live polling** — Runs the connection on an interval, passing `since_event_id` to receive only new events
4. **AI analysis** — Feeds schema-flexible event data directly to Claude, which analyzes game state and estimates outcome probabilities
5. **Action** — Uses those probabilities to identify and execute value bets on Kalshi

### Running Alph Bot

```
git clone https://gitlab.com/outsharp/shipp/alph-bot.git
cd alph-bot

cp .env.example .env
# Add your Shipp, Kalshi, and Anthropic API keys

yarn migrate

# List available games
./index.ts available-games --sport NBA

# Run value betting in demo/paper mode
./index.ts value-bet -d --paper --game <GAME_ID>
```

> **Warning:** Alph Bot involves real money when not in paper/demo mode. Always test thoroughly first.

### Key Patterns from Alph Bot

- **Reuse connections** — Create once, poll repeatedly. Avoids unnecessary creation overhead and credit spend.
- **Cursor pagination** — Always pass `since_event_id` so each poll returns only new events.
- **Defensive data handling** — All fields treated as optional since shape varies by sport, game phase, and event type.
- **Schedule-first** — Discover game IDs from the schedule endpoint before creating connections.

## Tips

- Keep `filter_instructions` short, explicit, and scoped (mention sport/league/team/game)
- Store and reuse `connection_id` — creating connections has time and credit overhead
- Polling interval of 5–30 seconds works well for most use cases
- Deduplicate events by tracking seen event IDs
- Log unknown data shapes during development to refine your `filter_instructions`
- Surface error `hint` messages to users when limits are hit
- Include `Accept-Encoding` header for compressed responses on large payloads

## Resources

| Resource | URL |
|---|---|
| Full Documentation | [docs.shipp.ai](https://docs.shipp.ai) |
| How-To Guides | [docs.shipp.ai/how-to](https://docs.shipp.ai/how-to/) |
| Setup Instructions | [docs.shipp.ai/instructions/setup](https://docs.shipp.ai/instructions/setup/) |
| API Reference | [docs.shipp.ai/api-reference](https://docs.shipp.ai/api-reference/) |
| Dashboard / Signup | [platform.shipp.ai](https://platform.shipp.ai/signup) |
| Billing | [platform.shipp.ai/billing](https://platform.shipp.ai/billing) |
| Alph Bot (example) | [gitlab.com/outsharp/shipp/alph-bot](https://gitlab.com/outsharp/shipp/alph-bot) |