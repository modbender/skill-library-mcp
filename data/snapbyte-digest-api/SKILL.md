---
name: snapbyte-digest-api
description: Fetch personalized developer news digests from Snapbyte External API with API-key auth. Use for Hacker News digest, Reddit digest, Lobsters digest, and DEV.to digest workflows.
homepage: https://api.snapbyte.dev/docs
metadata: {"openclaw":{"emoji":"📰","requires":{"bins":["python3","curl"],"env":["SNAPBYTE_API_KEY"]},"primaryEnv":"SNAPBYTE_API_KEY"}}
---

# Snapbyte Digest API

Use this skill to fetch user-scoped digests from Snapbyte and present them as clean, high-signal markdown.

## When to use

- User asks for their latest digest.
- User asks for digest history.
- User asks for a digest's items or summary from Snapbyte API.
- User asks for a developer news digest API workflow in OpenClaw.

## Auth

- Requires `SNAPBYTE_API_KEY`.
- Send `Authorization: Bearer <SNAPBYTE_API_KEY>` to Snapbyte API.

## Base URL

- `https://api.snapbyte.dev`

## Command patterns

Run the helper script from this skill folder:

```bash
python3 scripts/snapbyte_digest.py configurations
python3 scripts/snapbyte_digest.py latest
python3 scripts/snapbyte_digest.py latest --configuration-id 12
python3 scripts/snapbyte_digest.py history --configuration-id 12 --page 1 --limit 10
python3 scripts/snapbyte_digest.py digest --id dst_abc123
python3 scripts/snapbyte_digest.py items --digest-id dst_abc123 --page 1 --limit 10
```

## Output rules

- Prefer formatted markdown output from script by default.
- If user asks for raw payload, pass `--raw`.
- Keep links intact and do not invent fields not returned by API.

## Failure handling

- `401`: tell user key is missing/invalid/revoked/expired and ask them to update `SNAPBYTE_API_KEY`.
- `404`: tell user digest/configuration was not found.
- Validation errors: show a short fix and rerun with corrected arguments.

## References

- See `references/quickstart.md` for setup and examples.
