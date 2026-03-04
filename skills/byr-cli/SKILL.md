---
name: byr-cli
description: Use BYR CLI for auth, search, detail inspection, and safe torrent download planning with JSON envelopes.
metadata:
  {
    "openclaw":
      {
        "skillKey": "byr-cli",
        "homepage": "https://clawhub.ai",
        "requires": { "bins": ["byr"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "byr-pt-cli",
              "tap": "1MoreBuild/tap",
              "bins": ["byr"],
              "label": "Install byr CLI (Homebrew)",
            },
            {
              "id": "node",
              "kind": "node",
              "package": "byr-pt-cli",
              "bins": ["byr"],
              "label": "Install byr CLI (npm fallback)",
            },
          ],
      },
  }
---

# BYR CLI Skill

## When To Use

Use this skill when a task needs any BYR operation via CLI:

- authenticate/check auth state
- search torrents with filters
- browse latest torrents with filters
- inspect torrent details
- plan or execute torrent downloads
- fetch BYR metadata and user info
- run local diagnostics before live calls

## Boundaries

- Work only through the `byr` binary.
- Prefer `--json` for machine-readable output.
- Do not infer missing IDs/paths or silently mutate files.
- Keep read-only commands non-destructive.

## Auth Notes

- Support both cookie formats in `auth import-cookie`:
  - `uid=...; pass=...`
  - `session_id=...; auth_token=...` (optional `refresh_token=...`)
- Browser import:
  - `chrome` (macOS path/decrypt flow)
  - `safari` best effort with manual fallback
- Always check status before live operations:
  - `byr auth status --verify --json`

## Commands (JSON First)

Read-only:

- `byr check --json`
- `byr whoami --json`
- `byr doctor [--verify] --json`
- `byr browse [--limit <n>] [--category <alias|id>] [--incldead <alias|id>] [--spstate <alias|id>] [--bookmarked <alias|id>] [--page <n>] --json`
- `byr search --query "<text>" --limit <n> --json`
- `byr search --imdb <tt-id> [--category <alias|id>] [--spstate <alias|id>] --json`
- `byr get --id <torrent-id> --json`
- `byr user info --json`
- `byr meta categories --json`
- `byr meta levels --json`
- `byr auth status [--verify] --json`
- `byr auth import-cookie --cookie "<cookie-header>" --json`
- `byr auth import-cookie --from-browser <chrome|safari> [--profile <name>] --json`
- `byr auth logout --json`

Write side effect:

- Dry run first: `byr download --id <torrent-id> --output <path> --dry-run --json`
- Actual write: `byr download --id <torrent-id> --output <path> --json`

## Search/Browse Semantics

- `search` and `browse` return paged list data.
- JSON fields:
  - `matchedTotal`: estimated total hits inferred from BYR pagination range blocks.
  - `returned`: number of items returned in current payload.
  - `total`: backward-compatible alias of `returned`.
- If `--page` is omitted, list commands auto-fetch subsequent pages until `--limit` is reached.
- If `--page` is provided, only that page is fetched.

## Side-Effect Policy

Before non-dry-run `download`:

1. verify `--id` and `--output` are explicit
2. run dry-run and inspect `sourceUrl/fileName`
3. confirm intent for the output path

If parameters are missing, ask for explicit values.

## Error handling

- Surface `error.code` and `error.message`.
- For `E_ARG_*`: request corrected flags/arguments.
- For `E_AUTH_*`: re-auth guidance (`auth import-cookie` or credential refresh).
- For `E_NOT_FOUND_*`: request different query/torrent ID.
- For `E_UPSTREAM_*`: suggest retry and capture command/context.

## Response Style

- Keep result summaries short.
- Include key fields for search/get: `id`, `title`, `size`, `seeders`, `leechers`.
- For list commands include both `matchedTotal` and `returned` when present.
- Include key fields for download: `outputPath`, `sourceUrl`, `dryRun`, `bytesWritten`.
