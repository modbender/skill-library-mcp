---
name: telegram-ascii-table
description: Format tabular data as ASCII box tables for Telegram. Stdin-only input eliminates shell injection risks. Handles smart column sizing, text wrapping, and proper padding for monospace display.
---

# Telegram ASCII Tables

Format tabular data as ASCII box-drawing tables that render correctly in Telegram code blocks.

## Quick Start

```bash
{baseDir}/scripts/ascii-table.py <<'EOF'
Name|Value|Status
Server|web-01|Online
Database|db-01|Syncing
EOF
```

Wrap output in triple backticks when sending to Telegram.

## Usage

### Heredoc (recommended)

```bash
# Desktop mode (default): Unicode box chars, 58 char width
ascii-table <<'EOF'
Server|Status|Uptime
web-01|Online|14d 3h
db-01|Syncing|2d 12h
EOF

# Mobile mode: ASCII chars, 48 char width
ascii-table --mobile <<'EOF'
Task|Status
Deploy|Done
Test|Pending
EOF

# Custom width
ascii-table --width 80 <<'EOF'
Column|Another Column
data|more data
EOF
```

### Pipe

```bash
cat data.txt | ascii-table
echo -e 'Name|Value\nRow1|Data1' | ascii-table
some-command | ascii-table --mobile
```

## Options

```
┌───────────┬───────┬────────────────────────────────────────────┐
│ Flag      │ Short │ Description                                │
├───────────┼───────┼────────────────────────────────────────────┤
│ --desktop │ -d    │ Unicode box chars, 58 char width (DEFAULT) │
├───────────┼───────┼────────────────────────────────────────────┤
│ --mobile  │ -m    │ ASCII chars, 48 char width                 │
├───────────┼───────┼────────────────────────────────────────────┤
│ --width N │ -w N  │ Override default width                     │
└───────────┴───────┴────────────────────────────────────────────┘
```

## Mode Comparison

```
┌───────────────┬──────────────────────┬─────────────────────┐
│ Aspect        │ Desktop (default)    │ Mobile              │
├───────────────┼──────────────────────┼─────────────────────┤
│ Characters    │ Box drawing          │ ASCII (+ - chars)   │
├───────────────┼──────────────────────┼─────────────────────┤
│ Default width │ 58 chars             │ 48 chars            │
├───────────────┼──────────────────────┼─────────────────────┤
│ Rendering     │ Clean on desktop     │ Reliable everywhere │
├───────────────┼──────────────────────┼─────────────────────┤
│ Use when      │ Recipient on desktop │ Recipient on mobile │
└───────────────┴──────────────────────┴─────────────────────┘
```

Unicode box-drawing characters render at inconsistent widths on mobile Telegram. Use `--mobile` for mobile recipients.

## Input Format

- One row per line via stdin
- Columns separated by `|`
- Empty lines ignored
- Whitespace around cells trimmed

## Output Examples

### Desktop
```
┌──────────┬──────────┬──────────┐
│ Server   │ Status   │ Uptime   │
├──────────┼──────────┼──────────┤
│ web-01   │ Online   │ 14d 3h   │
├──────────┼──────────┼──────────┤
│ db-01    │ Syncing  │ 2d 12h   │
└──────────┴──────────┴──────────┘
```

### Mobile
```
+------------+----------+----------+
| Server     | Status   | Uptime   |
+------------+----------+----------+
| web-01     | Online   | 14d 3h   |
+------------+----------+----------+
| db-01      | Syncing  | 2d 12h   |
+------------+----------+----------+
```

### With Wrapping
```
┌─────────┬────────┬──────────────────────────────────────┐
│ Task    │ Status │ Notes                                │
├─────────┼────────┼──────────────────────────────────────┤
│ Deploy  │ Done   │ Rolled out to prod successfully      │
│ API     │        │                                      │
├─────────┼────────┼──────────────────────────────────────┤
│ Fix bug │ WIP    │ Waiting on upstream OAuth fix        │
└─────────┴────────┴──────────────────────────────────────┘
```

## Design Note: Stdin-Only Input

This script intentionally does not accept row data as CLI arguments.

Shell argument parsing happens *before* any script runs. Characters like `` ` ``, `$`, and `!` in double-quoted args get executed or expanded by the shell — not by the script receiving them. For example, `` `whoami` `` would execute and substitute its output before the script ever sees it.

By requiring stdin input, user data bypasses shell parsing entirely. A quoted heredoc (`<<'EOF'`) passes everything through literally — no escaping needed, no execution possible.

## Limitations

- **Pipe delimiter** — `|` separates columns (cannot appear in cell content)
- **Word breaks** — long words may split mid-word
- **Wide characters** — emoji/CJK may cause alignment issues
- **Left-aligned only** — no numeric right-alignment
