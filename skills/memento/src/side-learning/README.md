# Side Learning — Ingest Knowledge from Claude Code Sessions

Side Learning extends Memento's input sources beyond OpenClaw conversations to include
Claude Code (Claude Cowork) project sessions. It captures architectural decisions,
patterns discovered, gotchas, and preferences that would otherwise evaporate.

## Architecture

```
Claude Code Session
    │
    ├── /memento-export (slash command)
    │   └── Generates structured JSON fact file
    │
    └── Drops into ~/.engram/staging/<project>/<timestamp>.json
                │
                ├── Ingest pipeline (periodic or on-demand)
                │   ├── Parse staging files
                │   ├── Run through existing dedup pipeline
                │   └── Promote to main facts table (confidence: 0.7)
                │
                └── Processed files moved to ~/.engram/staging/.processed/
```

## Components

1. **Export prompt** — A Claude Code slash command (`.claude/commands/memento-export.md`)
   that generates a structured memory export at session end.

2. **Staging format** — JSON files with Memento-compatible fact schema, plus
   source metadata (project, session, timestamp).

3. **Ingest CLI** — `src/cli/ingest-staging.ts` reads staging files, runs dedup,
   and promotes facts. Can run from cron or manually.

## Usage

In any Claude Code project:
```
/memento-export
```

Then from OpenClaw (cron or manual):
```bash
npx tsx src/cli/ingest-staging.ts
```
