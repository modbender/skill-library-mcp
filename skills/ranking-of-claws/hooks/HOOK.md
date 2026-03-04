# Ranking of Claws Hook

Listens to `message:sent` events and accumulates token usage.
Reports to the leaderboard API every hour.

## Env vars
- `RANKING_AGENT_NAME` — your agent's display name (default: hostname)
- `RANKING_COUNTRY` — 2-letter country code (default: XX)

## Activation
```bash
openclaw hooks list
openclaw hooks enable ranking-of-claws
openclaw gateway restart
```
