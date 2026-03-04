---
name: clawpost
description: Posts tweets to X (Twitter) via Claw Post API. Use when the user wants to post to X, publish a tweet, or share content on X/Twitter.
metadata: {"openclaw":{"primaryEnv":"CLAWPOST_API_KEY","homepage":"https://clawpost.net/api-docs"}}
---

# Claw Post

Posts tweets to X (Twitter) using the Claw Post API. A paired browser extension publishes from the user's session.

## Prerequisites (instruct the human)

Before posting works, the human must:

1. **Sign up** at clawpost.net
2. **Install** the Claw Post Chrome extension
3. **Pair** the extension in the Dashboard (paste the 6-digit code from the extension popup)
4. **Provide** the API key from the Dashboard to the agent (or download this skill, which includes it)
5. **Log in to X** once at x.com

If the agent gets `EXTENSION_NOT_PAIRED` or `not_logged_in`, direct the human to complete these steps.

## API Base URL

```
https://claw-post-api-ukpr57vsgq-uc.a.run.app
```

Use this exact URL. Do not use api.clawpost.net or other variants.

## Inputs needed

- **API key**: `clawpost-api-key` header (see below; or set `CLAWPOST_API_KEY` in OpenClaw config)
- **Text**: Tweet content (required)

## Workflow

1. Send a POST request to create a tweet job.
2. Poll `GET /v1/jobs/:id` for status until `succeeded` or `failed`.

### Create tweet

```
POST https://claw-post-api-ukpr57vsgq-uc.a.run.app/v1/jobs/tweet
Header: clawpost-api-key: claw_00befabe022666a86f18effea768fd40531b5c132ade52d3
Content-Type: application/json
Body: { "text": "<tweet content>" }
```

Optional body fields:
- `mediaPaths` – array of URLs (upload via `POST https://claw-post-api-ukpr57vsgq-uc.a.run.app/v1/media/upload` first)
- `idempotencyKey` – unique string to prevent duplicates

### Poll job status

```
GET https://claw-post-api-ukpr57vsgq-uc.a.run.app/v1/jobs/:id
```

Status: `queued` → `processing` → `succeeded` | `failed`

## Error handling

| Code | Cause | Action |
|------|-------|--------|
| 401 | Invalid/missing API key | Check `clawpost-api-key` header |
| 503 `EXTENSION_NOT_PAIRED` | No paired extension | User must install Claw Post extension and pair at clawpost.net/dashboard |
| `not_logged_in` | User not logged in to X | User must log in to x.com once |
| `no_x_tab` | Extension could not open X | Retry; extension auto-opens x.com |
| `content_script_unavailable` | Extension could not reach X tab | Ask user to refresh x.com tab |
| `selector_not_found` | X UI changed | Retry later |

On failure, poll `GET /v1/jobs/:id` for `error` and `errorCode`.

## Reference

Full API docs: https://clawpost.net/api-docs
