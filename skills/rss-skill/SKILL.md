---
name: feed-to-md
title: Feed to Markdown
description: Convert RSS or Atom feed URLs into Markdown using the bundled local converter script. Use this when a user asks to turn a feed URL into readable Markdown, optionally limiting items or writing to a file.
metadata: {"clawdbot":{"emoji":"📰","requires":{"bins":["python3"]}}}
---

# RSS/Atom to Markdown

Use this skill when the task is to convert an RSS/Atom feed URL into Markdown.

## What this skill does

- Converts a feed URL to Markdown via a bundled local script
- Supports stdout output or writing to a Markdown file
- Supports limiting article count and summary controls

## Inputs

- Required: RSS/Atom URL
- Optional:
  - output path
  - max item count
  - template preset (`short` or `full`)

## Usage

Run the local script:

```bash
python3 scripts/feed_to_md.py "<feed_url>"
```

Write to file:

```bash
python3 scripts/feed_to_md.py "https://example.com/feed.xml" --output feed.md
```

Limit to 10 items:

```bash
python3 scripts/feed_to_md.py "https://example.com/feed.xml" --limit 10
```

Use full template with summaries:

```bash
python3 scripts/feed_to_md.py "https://example.com/feed.xml" --template full
```

## Security rules (required)

- Never interpolate raw user input into a shell string.
- Always pass arguments directly to the script as separate argv tokens.
- URL must be `http` or `https` and must not resolve to localhost/private addresses.
- Every HTTP redirect target (and final URL) is re-validated and must also resolve to public IPs.
- Output path must be workspace-relative and end in `.md`.
- Do not use shell redirection for output; use `--output`.

Safe command pattern:

```bash
cmd=(python3 scripts/feed_to_md.py "$feed_url")
[[ -n "${output_path:-}" ]] && cmd+=(--output "$output_path")
[[ -n "${limit:-}" ]] && cmd+=(--limit "$limit")
[[ "${template:-short}" = "full" ]] && cmd+=(--template full)
"${cmd[@]}"
```

## Script options

- `-o, --output <file>`: write markdown to file
- `--limit <number>`: max number of articles
- `--no-summary`: exclude summaries
- `--summary-max-length <number>`: truncate summary length
- `--template <preset>`: `short` (default) or `full`
