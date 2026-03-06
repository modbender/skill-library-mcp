# Weather Intelligence Digest Skill

Turn NOAA/NWS data into a polished daily briefing across Markdown, HTML, and JSON with one command.

## Why it matters
- **Executive-ready summaries** – Clean copy for “Today” and “Tonight” with wind + precip context.
- **Alert clarity** – Severity badges, local expiration times, and compressed instructions so nothing urgent gets missed.
- **Structured output** – Markdown for newsletters, HTML for web/email, and JSON for downstream automations.

## What you get
1. `weather_digest.py` CLI (Python 3.10+) powered by public NWS endpoints.
2. Config-driven locations (any latitude/longitude pair worldwide).
3. Styled HTML card layout with three built-in themes (midnight, daybreak, citrus) ready for email/CMS embeds.
4. Landing copy + documentation so you can publish instantly.

## How it works
```bash
python weather_digest.py \
  --config config.json \
  --output digest.md \
  --html digest.html \
  --json digest.json
```
- Rotate as many cities as you like by editing `config.json`.
- Outputs regenerate in ~4 seconds for three metros (cold starts aside).
- No API keys required; the script sets a respectful User-Agent.

## Use cases
- Publish a daily “Weather War Room” briefing to internal comms.
- Feed JSON into automations (Slack bot, SMS alerts, dashboards).
- Bundle HTML into a paid newsletter or embed on a marketing site.

## Ship checklist
- [x] Markdown + HTML refreshed with improved alert copy.
- [x] JSON export flag wired to the CLI.
- [x] Landing copy drafted (this doc).
- [ ] Upload to your storefront of choice.

Need tweaks (branding, additional outputs, cron wiring)? Extend `build_digest` or ping me for follow-up services.
