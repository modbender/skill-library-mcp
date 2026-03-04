# calendar-hold-sync

Generic calendar hold sync skill for preventing double-booking by mirroring source Google Calendar events into private Busy holds in target calendars.

## Supports

- OpenClaw
- Claude Code
- Gemini
- Codex

## What It Does

- Config-driven source -> target calendar mappings
- SYNC metadata in hold descriptions: `SYNCV1:<base64url(json)>`
- Idempotent reconcile (create/update/delete)
- Backfill legacy holds into `SYNCV1`
- Safety controls: `dryRun`, `maxChangesPerRun`, excludes, overlap policy

## Prerequisite

- `gog` CLI installed and OAuth already configured by the user

## gog Setup (Adapted)

If `gog` is not already set up, use this baseline flow:

1. Install `gog` (example: Homebrew formula `steipete/tap/gogcli`).
2. Add OAuth client credentials:
   - `gog auth credentials /path/to/client_secret.json`
3. Add your Google account with required services:
   - `gog auth add you@gmail.com --services calendar`
4. Verify account setup:
   - `gog auth list`

Add non-calendar services only if you explicitly need them.

Optional quality-of-life:

- Set `GOG_ACCOUNT=you@gmail.com` to avoid repeating `--account`.
- Prefer `--json` output in scripts.

Official `gog` references:

- Homepage: https://gogcli.sh/
- Source: https://github.com/steipete/gogcli

## Config

Start from:

- `skills/calendar-hold-sync/config/sample.config.json`

No account emails or calendar IDs are hardcoded in code.

Security default:

- custom command templates (`gog.*Cmd`) are disabled unless `gog.allowCustomCommands=true`.

Custom command behavior when enabled:

- only `gog` commands are accepted
- placeholders are expanded into argument values
- commands are executed as argv tokens (no shell interpolation)

### Watch Cadence (Configurable)

Fast sync cadence is configurable in skill config:

- `scheduling.watchIntervalSeconds`: watch poll interval
- `mappings[].lookaheadDays`: rolling source window to watch/reconcile

Recommended baseline:

- `watchIntervalSeconds: 900` (15 minutes)
- `lookaheadDays: 1` (24 hours)

`hold-sync watch` also supports runtime override with `--interval-seconds <n>`.

## Working Model

- `hold-sync watch` is polling-based sync.
- It checks configured source calendars on each interval and reconciles holds on detected change.
- Expected update delay is approximately `watchIntervalSeconds`.
- This skill is self-hosted/operator-run and debugged through command output/logs.

## Manual Smoke Test

Use a dedicated test mapping and test calendars before normal use.

1. Validate config:
   - `hold-sync --config <path> validate-config`
2. Dry-run baseline reconcile:
   - `hold-sync --config <path> reconcile --mapping <name> --dry-run`
3. Apply baseline reconcile:
   - `hold-sync --config <path> reconcile --mapping <name>`
4. Create a source event in lookahead window and verify one new Busy hold appears in target.
5. Update the source event time/title and verify target hold updates.
6. Delete the source event and verify target hold is removed.
7. Run watch loop:
   - `hold-sync --config <path> watch --mapping <name> --interval-seconds 900`
8. Create one additional source change and verify reconcile runs within the next interval.

## Known Limits

- No Google push/webhook subscription is built into this skill currently; watch mode is polling.
- Sync accuracy and latency depend on `gog` + Google Calendar API behavior and chosen polling interval.
- Recommended safety net is periodic reconcile via `install-cron` even when using watch mode.

## Build Provider Variants

```bash
moon run skill-build:build-skill
```

Generated outputs:

- `skills/calendar-hold-sync/dist/codex/SKILL.md`
- `skills/calendar-hold-sync/dist/claude/SKILL.md`
- `skills/calendar-hold-sync/dist/gemini/SKILL.md`
- `skills/calendar-hold-sync/dist/openclaw/SKILL.md`

## Install

1. Pick the target provider variant from `dist/<provider>/SKILL.md`.
2. Copy that `SKILL.md` into your provider's skill install location.
3. Use the sample config as a template and set your real mappings/accounts/calendars.

## CLI Surface

- `hold-sync validate-config`
- `hold-sync reconcile --mapping <name>|--all [--dry-run]`
- `hold-sync backfill --mapping <name>|--all [--dry-run]`
- `hold-sync status --mapping <name>|--all`
- `hold-sync install-cron --mapping <name>|--all`
- `hold-sync watch --mapping <name>|--all [--dry-run] [--interval-seconds <n>]`

## Credits

Setup flow above is adapted from the `gog` skill by steipete:

- https://clawhub.ai/steipete/gog
- https://github.com/steipete/gogcli
- https://gogcli.sh/
