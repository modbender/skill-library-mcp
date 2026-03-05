---
name: nasdaq-api
description: Query Nasdaq public market APIs from scripts or agent workflows. Use when you need Nasdaq stock screener pulls, symbol lists, pagination over screener rows, or guidance on official Nasdaq Data Link public API docs (authentication, API types, and rate limits).
---

# Nasdaq API Skill

Use this skill to fetch stock-universe data from Nasdaq's public screener endpoint and to ground API decisions in official Nasdaq Data Link docs.

## Workflow

1. Confirm scope before calling APIs:
- If the task is stock screener rows/symbol lists, use `scripts/nasdaq-screener.sh`.
- If the task is product/API selection, auth, or limits, read `references/api_docs.md` first.

2. Use the CLI instead of ad-hoc curl when possible:
- Run `scripts/nasdaq-screener.sh --help` for options.
- Start with `--limit` and `--offset` for deterministic pagination.
- Use `--format symbols` for ticker-only output, or `--format rows` for JSON row objects.

3. Handle reliability constraints:
- Include browser-like headers (script does this by default).
- Prefer retries in caller workflows for transient failures.
- Keep requests paced; avoid burst loops.

4. Validate result shape before downstream logic:
- Expect top-level `data.rows` for screener queries.
- Fail fast if `status.bCodeMessage` is present or `data.rows` is missing.

## Bundled Resources

- `references/api_docs.md`
  - Official Nasdaq public docs and practical screener notes.
- `scripts/nasdaq-screener.sh`
  - Bash CLI wrapper around `https://api.nasdaq.com/api/screener/stocks`.
- `agents/openai.yaml`
  - UI metadata for skill display and invocation prompt.
