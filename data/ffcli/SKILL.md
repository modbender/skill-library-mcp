---
name: ffcli
description: Query Fireflies.ai meeting data. Use when searching meetings, viewing transcripts, reading AI summaries, extracting action items, or looking up what was discussed in a call. Triggers on "meeting notes", "transcript", "action items from meeting", "what was discussed", "fireflies", "meeting summary".
metadata: {"openclaw":{"requires":{"bins":["ffcli"],"env":["FIREFLIES_API_KEY"]},"primaryEnv":"FIREFLIES_API_KEY","install":[{"id":"brew","kind":"brew","formula":"ruigomeseu/tap/ffcli","bins":["ffcli"],"label":"Install ffcli (Homebrew tap)"},{"id":"npm","kind":"node","package":"@ruigomeseu/ffcli","bins":["ffcli"],"label":"Install ffcli (npm)"}]}}
---

# ffcli — Fireflies.ai CLI

Query meeting recordings, transcripts, and AI summaries from Fireflies.ai.

## Setup

Install via Homebrew or npm:

```bash
brew install ruigomeseu/tap/ffcli
# or
npm install -g @ruigomeseu/ffcli
```

Authenticate with your Fireflies API key (get it from [Settings → Developer Settings](https://app.fireflies.ai/settings)):

```bash
ffcli auth <your-api-key>    # Store key locally (~/.config/ffcli/)
ffcli auth --check           # Verify it works
```

Alternatively, set the `FIREFLIES_API_KEY` environment variable (takes precedence over stored config). In OpenClaw, configure it via `skills.entries.ffcli.apiKey` in `openclaw.json`.

**Note:** `ffcli` is a third-party CLI by @ruigomeseu (Homebrew tap or npm). Verify the source before installing: check the [npm package](https://www.npmjs.com/package/@ruigomeseu/ffcli) or [Homebrew tap repo](https://github.com/ruigomeseu/homebrew-tap) for code review and publish history.

## Commands

### List meetings
```bash
ffcli list --limit 10 --md                           # Recent meetings
ffcli list --from 2026-02-01 --to 2026-02-12 --md    # Date range
ffcli list --participant vinney@opennode.com --md     # By participant
ffcli list --search "standup" --md                    # By title keyword
ffcli list --limit 5 --include-summaries              # With AI summaries (JSON)
```

### Show meeting detail
```bash
ffcli show <id> --md                    # Full detail (markdown)
ffcli show <id> --summary-only --md     # Just AI summary
ffcli show <id> --transcript-only --md  # Just transcript
ffcli show <id> --include-transcript --md  # Detail + transcript
```

### User info
```bash
ffcli me --md                           # Account info, transcript count
```

### Scripting patterns
```bash
# Action items from recent meetings
ffcli list --limit 10 --include-summaries | jq '.[].summary.action_items'

# All meeting IDs from a date range
ffcli list --from 2026-02-01 --to 2026-02-07 | jq -r '.[].id'

# Export a summary to file
ffcli show <id> --summary-only --md > meeting-summary.md
```

## Notes
- Default output is JSON. Use `--md` for readable output.
- `--include-summaries` on `list` adds AI summaries (increases response size).
- Meeting IDs are needed for `show` — get them from `list` first.
- Dates are UTC in JSON output.
