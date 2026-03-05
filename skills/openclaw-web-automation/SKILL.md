---
name: openclaw-web-automation-basic
description: Use this skill when the user wants quick, no-credential browser automation against public websites (summaries, keyword checks, simple page facts). Runs the local OpenClaw Automation Kit query path and returns structured results.
---

# OpenClaw Web Automation (No Credentials)

This skill is the fastest path for public-site automation tasks.

Use this for requests like:
- "Summarize https://www.yahoo.com"
- "Check whether https://example.com mentions pricing"
- "Count mentions of 'news' on a public page"

Do not use this skill for login-required tasks. Use award/login flows instead.

## Preconditions

- Repository is available locally.
- Python environment is installed (`pip install -e .`).
- No credentials are required for this skill.

## Command to run

From repo root:

```bash
python skills/openclaw-web-automation-basic/scripts/run_query.py --query "<user request>"
```

The script routes to `examples/public_page_check` and returns JSON.

## Output handling

- Return a concise summary to the user:
  - page title
  - keyword
  - keyword count
  - 1-3 highlights
- If the query has no URL, default to `https://www.yahoo.com`.
- If parsing fails, ask the user for a URL and what text to check.

## Safety

- Public websites only.
- No credential collection.
- No anti-bot bypass guidance.
