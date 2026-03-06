# briefing

A daily briefing skill for OpenClaw. Gathers calendar events, active todos, and weather into a single concise message — optimized for mobile chat.

## What it does

When invoked (typically via `/briefing`), the agent:

1. Checks which companion skills are available.
2. Determines whether the briefing covers **today** or **tomorrow** (based on current time and remaining events).
3. Fetches data from each available source (calendar, todos, weather).
4. Composes a single, skimmable message with emoji-prefixed sections.

If a companion skill is missing, that section is simply omitted. If none are available, the agent tells the user and stops — it never fabricates data.

## Companion skills

This skill orchestrates three companion skills. All are optional — the briefing adapts to whatever is available.

- [**`gcalcli-calendar`**](https://clawhub.ai/lstpsche/gcalcli-calendar) — Calendar events via [gcalcli](https://github.com/insanum/gcalcli). Provides today's agenda and upcoming events.
- [**`todo-management`**](https://clawhub.ai/lstpsche/todo-management) — Active/pending todo items. Provides task list for the briefing.
- [**`openmeteo-sh-weather-simple`**](https://clawhub.ai/lstpsche/openmeteo-sh-weather-simple) — Current weather and forecast via [openmeteo-sh](https://github.com/lstpsche/openmeteo-sh) CLI. Requires a default city in the user's session context.

### Using different companion skills

The companion skill names are hardcoded in `SKILL.md`. If you use different skills for calendar, todos, or weather, edit the `## Sources` section and the corresponding `## Gather` subsections to match your skill names and CLI commands.

For example, to use a different weather skill:
1. Replace `openmeteo-sh-weather-simple` in the Sources list.
2. Update the weather commands in the `### Weather` gather section.

## Model requirements

**This skill requires a capable model.** It involves multi-step tool orchestration: the agent must detect available skills, read their docs, make 3+ tool calls, and compose structured output.

Tested and working:
- Grok 4.1 Fast — works well
- Gemini 2.5 Flash — works (may need retries on weather CLI syntax)

Not recommended:
- Small/nano models (GPT-5 Nano, OLMo 32B, etc.) — struggle with multi-tool orchestration
- Search-optimized models (Perplexity Sonar) — not designed for agent workflows

If the briefing produces poor results, try a more capable model before adjusting the skill.

## Commands executed

The skill instructs the agent to run:

- **`openmeteo weather`** — fetches current conditions and forecast from the [Open-Meteo API](https://open-meteo.com/) via the `openmeteo-sh` CLI. Uses `--llm` for compact, token-efficient output. The city name is quoted in the command to prevent shell interpretation.
- Calendar and todo commands are delegated to their respective companion skills (the agent reads their `SKILL.md` for instructions).

## Network access

Indirect, via companion skills:
- `openmeteo-sh` connects to `api.open-meteo.com` (free, no API key required).
- `gcalcli` connects to Google Calendar API (requires user's own OAuth credentials, configured outside this skill).
- `todo-management` is local (SQLite database, no network).

This skill itself makes no network requests and reads no files directly.

## Invocation

This skill is triggered by the user via `/briefing` command. It is also available for the agent to invoke when contextually appropriate (e.g. as part of a scheduled cron job).

## Recommended: scheduled daily briefing

This skill works best as a **scheduled cron job** that fires every morning at your wake time. Instead of manually typing `/briefing` each day, let OpenClaw send it for you.

### Setup via CLI

```
openclaw cron add \
  --name "Morning briefing" \
  --cron "0 7 * * *" \
  --tz "Europe/London" \
  --session isolated \
  --message 'Use the "briefing" skill for this request.' \
  --deliver \
  --channel telegram
```

Adjust to your needs:
- `--cron "0 7 * * *"` — 07:00 daily. Change the hour/minute to match your wake time. Uses standard [cron syntax](https://crontab.guru/).
- `--tz` — your IANA timezone (e.g. `America/New_York`, `Asia/Tokyo`).
- `--session isolated` — runs in a fresh session, so it doesn't interfere with ongoing conversations.
- `--channel` — the channel where the briefing should be delivered (e.g. `telegram`, `discord`, `slack`).
- `--deliver` — ensures the output is sent to your channel.

### Verify

```
openclaw cron list
```

### Notes

- This uses OpenClaw's built-in cron scheduler — no external tools or system crontabs needed.
- The cron job sends `/briefing` as a user message, which triggers the skill normally.
- The job runs with the same agent permissions as a regular session. No elevated access is granted.
- If the gateway restarts, cron jobs are reloaded automatically from `~/.openclaw/cron/jobs.json`.

## License

MIT
