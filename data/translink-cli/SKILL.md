---
name: translink-cli
description: Query, troubleshoot, and explain Translink SEQ GTFS static + realtime data using local translink_* commands or plugin slash commands. Use for schedule lookups, stop/route/trip joins, vehicle/trip realtime checks, alerts, schema drift review, PK/FK reasoning, and paginated filtering.
---

# Translink CLI Skill

Use when working with Translink data in this environment.

## Prerequisite

This skill requires the Translink CLI scripts to be installed and available in PATH.

- CLI repo: `https://github.com/alanburchill/traslink-cli-scripts`
- Expected commands: `translink_*` (or equivalent wrappers that expose the same command names)

If the CLI is not installed, stop and ask the user to install it first.

## Command surfaces

- Shell CLI: `translink_*`
- Plugin slash commands: `/translink_*` and `/translink <command> [args...]`

## Core workflow

1. Refresh or validate cache/schema with `translink_schedule_refresh` when freshness is uncertain.
2. Query with shared parameters (`--where`, `--contains`, `--in`, `--page`, `--per-page`, etc.).
3. On strict field errors, use fuzzy suggestions in the JSON error payload to auto-correct.
4. Use PK/FK references for joins across routes/trips/stops/stop_times/calendar/shapes.
5. For authoritative current schema, read generated schema docs first.

## Shared parameter contract

All commands support:
- `--where field=value` (repeatable)
- `--contains field=text` (repeatable)
- `--in field=v1,v2,...` (repeatable)
- `--fields a,b,c`
- `--sort field`
- `--order asc|desc`
- `--page N`
- `--per-page N` (default 20)
- `--format table|json|csv`
- `--count-only`

Realtime extras:
- `--expand` (include nested JSON fields)
- `--raw` (include full raw entity JSON)
- `--time epoch|iso`

Schedule extras:
- `--refresh`
- `--schema`

## Runtime behavior

- Static cache: `~/.openclaw/cache/translink/`
- TTL: 24h
- Daily refresh cron (example): 5:00 AM local time (`translink:schedule-refresh`)
- Refresh lock prevents concurrent extract races.
- Schema is header-driven and auto-adapts to added columns.

## Read these references as needed

- `references/commands.md` — command/param/error contract
- `references/usage.md` — examples
- `references/relationships.md` — PK/FK joins
- `references/schema-generated.md` — auto-generated live schema (authoritative)
- `references/column-meanings.md` — GTFS field semantics
