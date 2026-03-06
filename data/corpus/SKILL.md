---
name: corpus
description: Access a user's Corpus library from OpenClaw. Use when the user asks to search saved content, fetch item details, save links into Corpus, or create reminders from Corpus content.
homepage: https://github.com/zdonino/Corpus
metadata: {"openclaw":{"primaryEnv":"CORPUS_API_TOKEN","requires":{"env":["CORPUS_API_TOKEN"],"bins":["python3"]}}}
---

# Corpus Skill

Use this skill to read and write a user's Corpus data through the Corpus API.

## Required environment variables

- `CORPUS_API_TOKEN`: user token for Corpus API access.

## Generate `CORPUS_API_TOKEN`

1. Install Corpus AI for iPhone: `https://apps.apple.com/us/app/corpus-ai/id6748364607`
2. Open the app and sign in.
3. Go to `Integrations` -> `OpenClaw`.
4. Create an API token and copy it (the full value is shown once).
5. Set that value as `CORPUS_API_TOKEN` in your OpenClaw skill env.

## Optional environment variables

- `CORPUS_API_BASE_URL`: API base URL (default: `https://corpusai.app`).
- `CORPUS_TIMEOUT_SECONDS`: HTTP timeout in seconds (default: `30`).

## OpenClaw config example

```json
{
  "skills": {
    "entries": {
      "corpus": {
        "path": "/absolute/path/to/skills/corpus",
        "env": {
          "CORPUS_API_TOKEN": "csk_live_or_jwt_token_here",
          "CORPUS_API_BASE_URL": "https://corpusai.app"
        }
      }
    }
  }
}
```

## Commands

Run all commands through:

`python3 {baseDir}/scripts/corpus_api.py <command> [options]`

Available commands:

- `profile`
- `list-content --limit 20 --cursor <cursor>`
- `search --query "<text>" --limit 8`
- `content --user-content-id <id>`
- `save-url --url <url> [--user-note "<note>"]`
- `create-reminder --title "<title>" --description "<desc>" --scheduled-date-utc "2026-02-18T16:00:00Z" [--user-content-id <id>]`

## Recommended workflow for implementation tasks

When a user asks for "find items in Corpus and implement":

1. Use `search` with a focused query.
2. Use `content` for top hits to collect concrete steps.
3. Produce an implementation plan with explicit file changes.
4. Apply code changes in the current working repository after user confirmation.

## Safety rules

- Never print or log `CORPUS_API_TOKEN`.
- Prefer read operations before write operations.
- Before write operations (`save-url`, `create-reminder`), confirm user intent if the instruction is ambiguous.
