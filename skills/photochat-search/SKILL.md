---
name: photochat-search
description: "Search for photos in PhotoCHAT using natural language via the CLI. Use when the user asks to find, search for, or locate photos/pictures/images using PhotoCHAT. Triggers include phrases like 'find me a photo of...', 'search photochat for...', 'use photochat to find...', or simply 'find me a picture of...'. NOT for browsing the PhotoCHAT GUI, managing albums, or face profile editing."
---

# PhotoCHAT CLI Search

Search the user's photo library using PhotoCHAT's natural language search CLI.

## Command

```powershell
photochat search [options] <natural language query>
```

Uses the MSIX-packaged `photochat` app execution alias (v0.6.0+).

## Options

| Flag | Purpose | Default |
|------|---------|---------|
| `--json` | Machine-readable JSON output | off |
| `--limit N` | Max results | 5 |
| `--show-filters` | Print parsed face/date/exclusion filters | off |
| `--show-scores` | Include similarity scores in plain text | off |
| `--profile NAME` | Force-include a face profile | none |
| `--day-first` | Parse ambiguous dates as DD/MM | off |
| `--dry-run` | Parse query only, skip retrieval | off |

## Workflow

1. Run search with `--json`, `--day-first`, and a reasonable `--limit`:

```powershell
photochat search --json --day-first --limit 10 show me a photo of sarah at the beach
```

2. Parse JSON output:

```json
{
  "query": "original query text",
  "intent": {
    "cleaned_query": "processed query",
    "face_filters": ["sarah"],
    "date_range": null,
    "exclude_terms": []
  },
  "total_results": 25,
  "returned_results": 5,
  "results": [
    { "rank": 1, "path": "I:/Pictures/.../photo.JPG", "score": 0.55 }
  ]
}
```

3. Present results:
   - Show file paths and match count (returned vs total)
   - To display a photo, use the `image` tool with the `path` from results
   - Scores above 0.4 are decent; above 0.5 is a strong match
   - If zero results, suggest simplifying the query or check filters with `--show-filters`

## Query Capabilities

The parser handles rich natural language:
- **Faces:** "Sarah at the beach" auto-filters face profile "Sarah"
- **Dates:** "from 2021", "in March", "before 2015", "from Mar 21"
- **Exclusions:** "without Matt" excludes face or concept
- **Mood/style:** "photos that feel cozy and warm", "vintage film look"
- **Combos:** "Bella standing next to a tall building from Mar 21"

For more examples, read `references/search-examples.txt`.

## Important

- Always use `--day-first` (Australian date format DD/MM)
- Always use `--json` for parseable output
- Default `--limit 5` unless user asks for more
- First search takes 10-30s (model loading); use 60s timeout on first call
- Result paths are absolute file paths; pass directly to the `image` tool

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (includes zero-result searches) |
| 2 | Argument/usage error |
| 3 | Runtime/model init failure |
| 4 | Storage init/access failure |
| 5 | Unexpected failure |
