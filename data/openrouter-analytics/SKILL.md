---
name: openrouter-analytics
description: Review OpenRouter usage, analytics, and troubleshooting data via API. Use when the user asks for spend/usage monitoring, activity trends, per-key management reporting, or deep investigation of specific request IDs (latency, provider fallback, finish reason, token/cost breakdown).
---

# OpenRouter Analytics

Use this skill to pull **management-level usage data** and **request-level troubleshooting details** from OpenRouter.

## Quick Start

Run from this skill folder:

```bash
cd ~/clawd/skills/openrouter-analytics
```

Management key operations (set `OPENROUTER_MANAGEMENT_KEY`):

```bash
python3 scripts/openrouter_analytics.py activity --limit 20
python3 scripts/openrouter_analytics.py activity --date 2026-02-18
python3 scripts/openrouter_analytics.py activity --from 2026-02-01 --to 2026-02-18 --summary --csv /tmp/activity.csv
python3 scripts/openrouter_analytics.py credits
python3 scripts/openrouter_analytics.py keys --limit 50 --summary
python3 scripts/openrouter_analytics.py report --from 2026-02-01 --to 2026-02-18 --format markdown
```

Request-level troubleshooting (set `OPENROUTER_API_KEY`):

```bash
python3 scripts/openrouter_analytics.py generation --id <generation_id>
```

Use `--raw` on any command to print full JSON.

## Workflow

1. **Check macro activity**
   - Run `activity` for daily spend/traffic patterns.
2. **Check account-level usage**
   - Run `credits` to review consumed vs remaining credits.
3. **Find key-level consumers**
   - Run `keys` to identify which keys are driving usage.
4. **Investigate incidents**
   - Run `generation --id ...` for detailed logs on one request (latency, fallback providers, finish reason, token and cost details).

## Notes

- `activity`, `credits`, `keys`, and `report` require a **Management API key**.
- `generation` uses a standard **OpenRouter API key** and requires the request `id`.
- The script auto-loads `~/.openclaw/.env` and current-directory `.env` before execution.
- Use `--retries` and `--timeout` to tune robustness under transient API/network issues.
- Keep generation IDs in your application logs to support reliable post-incident analysis.

## Resources

- Endpoint reference and field guide: `references/endpoints.md`
- CLI helper script: `scripts/openrouter_analytics.py`
