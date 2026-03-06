---
name: greptile
description: "Query, search, and manage repositories indexed by Greptile (AI codebase intelligence). Use when asking questions about a codebase, searching for code patterns, indexing repos for Greptile review, or checking Greptile index status. Requires GREPTILE_TOKEN and a GitHub/GitLab token."
metadata:
  openclaw:
    emoji: "🦎"
    publisher: "@iahmadzain"
    requires:
      env: [GREPTILE_TOKEN, GITHUB_TOKEN]
      bins: [curl, jq, gh]
---

# Greptile Skill

Query and manage Greptile-indexed repositories via the REST API.

## Setup

Required environment variables:
- `GREPTILE_TOKEN` — Greptile API token (from https://app.greptile.com)
- `GITHUB_TOKEN` — GitHub PAT with repo access (alternatively set `GREPTILE_GITHUB_TOKEN`, or authenticate via `gh auth login` — the script falls back to `gh auth token`)

## Commands

All commands use `scripts/greptile.sh` (resolve path relative to this skill directory).

### Index a repository

```bash
scripts/greptile.sh index owner/repo [branch] [--remote github|gitlab] [--no-reload] [--no-notify]
```

Default branch: `main`. Use `--no-reload` to skip re-indexing if already processed.

### Check index status

```bash
scripts/greptile.sh status owner/repo [branch] [--remote github|gitlab]
```

Returns: `status` (completed/processing/failed), `filesProcessed`, `numFiles`.

### Query a codebase (AI answer + sources)

```bash
scripts/greptile.sh query owner/repo [branch] "How does auth work?" [--genius] [--remote github|gitlab]
```

- `--genius` — slower but smarter analysis (good for PR reviews, architecture questions)
- Returns: AI-generated answer + source file references with line numbers

### Search a codebase (sources only, no AI answer)

```bash
scripts/greptile.sh search owner/repo [branch] "payment processing" [--remote github|gitlab]
```

Returns: ranked list of relevant files, functions, and snippets with line numbers.

## Tips

- Always `index` a repo before querying/searching it. Check `status` to confirm indexing is complete.
- Use `query --genius` for complex questions (architecture, PR review context, cross-file analysis).
- Use `search` when you just need file locations without an AI explanation.
- For GitLab repos, pass `--remote gitlab`.
- Pipe output through `jq` for formatting: `scripts/greptile.sh query ... | jq .`
- Multi-repo queries: not supported by the wrapper; use the API directly with multiple repositories in the body.
