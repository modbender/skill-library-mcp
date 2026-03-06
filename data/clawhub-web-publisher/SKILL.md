---
name: clawhub-web-publisher
description: Publish OpenClaw skills to ClawHub using the web dashboard only (no CLI login). Use when an agent must reliably upload a local skill folder, avoid auth-loop failures, and enforce privacy-safe publishing with verification evidence.
---

# ClawHub Web Publisher

Publish a local skill to ClawHub through `https://clawhub.ai/dashboard` with strict privacy controls.

## Hard Rules

- Never use `clawhub login`, `clawhub login --token`, or device flow.
- Use the already signed-in browser session for dashboard upload.
- Never include secrets in published files:
  - API keys
  - gateway tokens
  - personal emails and phone numbers
  - local absolute paths pointing to private user directories

## Preflight

1. Confirm target folder contains `SKILL.md`.
2. Confirm `SKILL.md` frontmatter includes:
   - `name`
   - `description`
3. Scan for secret leakage patterns:
   - `apiKey`
   - `token`
   - `OPENCLAW_`
   - `sk-`
   - `Bearer `

If any high-risk text appears, stop and sanitize before publish.

## Web Publish Procedure

1. Open `https://clawhub.ai/dashboard`.
2. Enter the upload/publish flow.
3. Select the local skill directory.
4. Fill listing title and short description:
   - title: clear benefit + audience
   - description: action-oriented and outcome-focused
5. Submit publish.
6. Capture outputs:
   - final skill URL
   - skill ID (if shown)
   - version (if shown)

## Quality Gate Before Marking Done

- Listing URL opens successfully.
- Name matches `SKILL.md` `name`.
- Description does not promise unsupported behavior.
- No credential-like strings appear in listing or content.

## Completion Evidence Format

Return all fields:

```text
PUBLISH_RESULT
- skill_name:
- version:
- url:
- skill_id:
- verification:
  - url_status:
  - privacy_scan:
  - notes:
```

## Failure Recovery (Still Web-Only)

If publish fails:
1. Refresh dashboard and retry once.
2. Re-open upload flow in same signed-in browser profile.
3. Reduce metadata length and retry.
4. If still blocked, return exact blocker text and a minimal next action for user.

