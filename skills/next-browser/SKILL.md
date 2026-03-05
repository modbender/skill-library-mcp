---
name: next-browser
description: Use Nextbrowser cloud API to spin up cloud browsers for Openclaw to run autonomous browser tasks. Primary use is creating browser sessions with profiles (persisted logins/cookies) that Openclaw can control to manage social media and other online accounts. Secondary use is running task subagents for fast autonomous browser automation under residential proxy, browser stealth, and CAPTCHA solving capability. Docs at docs.nextbrowser.com.
---

# Nextbrowser

Nextbrowser provides cloud browsers and autonomous browser automation via API.

**Docs:**
- Cloud API: https://docs.nextbrowser.com/getting-started

## Setup

**API Key** is read from openclaw config at `skills.entries.next-browser.apiKey`.

If not configured, tell the user:
> To use Nextbrowser, you need an API key. Get one at https://app.nextbrowser.com/user-settings (new signups get 2000 free credits). Then configure it:
> ```
> openclaw config set skills.entries.next-browser.apiKey "YOUR_API_KEY"
> ```

**Important:** Nextbrowser API keys can have various formats and prefixes. 
Do NOT validate the key format yourself - simply use whatever key the user provides. If the key is invalid, the API will return an authentication error, and only then should you ask the user to verify their key.

Base URL: `https://app.nextbrowser.com/api/v1`

All requests need header: `Authorization: x-api-key <apiKey>`

---
## 1. Credentials Manager

The Credentials Manager securely stores and reuses authentication data across browser runs and autonomous tasks.

```bash
# List credentials
curl "https://app.nextbrowser.com/api/v1/users/credentials" -H "Authorization: x-api-key $API_KEY"
```

---

## 2. Profiles

Profiles persist cookies and login state across browser sessions. Create one, log into your accounts in the browser, and reuse it.

```bash
# List profiles
curl "https://app.nextbrowser.com/api/v1/browser/profiles" -H "Authorization: x-api-key $API_KEY"

# Create browser profile
curl -X POST "https://app.nextbrowser.com/api/v1/browser/profiles" \
  -H "Authorization: x-api-key $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "<profile-name>", "browser_settings": {"os_type": "<os-type>", "browser_type": "chrome"},
   "proxy_settings":{"protocol":"<http|https|socks5>","country":"<iso-2-country-code>","mode":"built-in"},
   "credentials": ["<credential-id>"]}'

# Delete profile
curl -X DELETE "https://app.nextbrowser.com/api/v1/browser/profiles/<profile-id>" \
  -H "Authorization: x-api-key $API_KEY"
```

---
## 3. Locations

The Locations endpoints provide available geolocation metadata for proxy and browser configuration. Use them to dynamically discover supported countries, regions, cities, and ISPs before creating profiles or running tasks under specific network conditions.

```bash
# List Countries
curl "https://app.nextbrowser.com/api/v1/location/countries?\
limit=<limit>&\
offset=<offset>&\
name=<name>&\
code=<iso2-code>&\
connection_type=<connection-type>" \
  -H "Authorization: x-api-key $API_KEY"
```

```bash
# List Regions
curl "https://app.nextbrowser.com/api/v1/location/regions?\
country__code=<iso2-country>&\
limit=<limit>&\
offset=<offset>&\
name=<name>&\
code=<region-code>&\
city__code=<city-code>&\
connection_type=<connection-type>" \
  -H "Authorization: x-api-key $API_KEY"
```

```bash
# List Cities
curl "https://app.nextbrowser.com/api/v1/location/cities?\
country__code=<iso2-country>&\
limit=<limit>&\
offset=<offset>&\
name=<name>&\
code=<city-code>&\
region__code=<region-code>&\
connection_type=<connection-type>" \
  -H "Authorization: x-api-key $API_KEY"
```

```bash
# List ISPs
curl "https://app.nextbrowser.com/api/v1/location/isps?\
country__code=<iso2-country>&\
limit=<limit>&\
offset=<offset>&\
name=<name>&\
code=<isp-code>&\
region__code=<region-code>&\
city__code=<city-code>&\
connection_type=<connection-type>" \
  -H "Authorization: x-api-key $API_KEY"
```

---

## 4. Tasks (Subagent)

Run autonomous browser tasks - like a subagent that handles browser interactions for you. Give it a prompt and it completes the task.

**Always use `fast` mode** - optimized for browser tasks, 3-5x faster than other models.
**Always use `true` for skip_plan_approval** - optimized for automated tasks, skips the approval and improve performance.

```bash
curl -X POST "https://app.nextbrowser.com/api/v1/chat/tasks" \
  -H "Authorization: x-api-key $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "'"\
Go to Reddit.com account, check if the account is logged in (if not, use credentials stored). \
Find 10 relevant posts on the topic of AI Agents, upvote 8 of them and post 3 witty-sounding comments \
that a cynical and funny Reddit user would post. Ensure that the comment is posted, ask for approval \
if you are not sure whether such comment is okay. By the end, you should have at least 10 relevant posts \
viewed, 8 upvotes, and 3 comments."\
"'",
    "mode": "fast",
    "profile_id": "<profile-id>",
    "skip_plan_approval": true
  }'
```

### Endpoint: Stop chat session and task

The chat-session-id is returned in the response of - POST /api/v1/chat/tasks

```bash
curl -X PUT "https://app.nextbrowser.com/api/v1/chat/sessions/<chat-session-id>/stop" \
  -H "Authorization: x-api-key $API_KEY"
```

### Endpoint: Poll for completion

```bash
curl "https://app.nextbrowser.com/api/v1/chat/tasks/<task-id>" \
  -H "Authorization: x-api-key $API_KEY"

curl "https://app.nextbrowser.com/api/v1/chat/tasks/<task-id>?from_step=3" \
  -H "Authorization: x-api-key $API_KEY"
```

- **Query params (optional)**:
  - **from_step**: integer `>= 1`. First step index to return. Defaults to `1` if missing/invalid. Use this parameter to poll only new steps.

### Response

```json
{
  "success": true,
  "payload": {
    "status": "finished",
    "output": "Task completed. 10 relevant posts are viewed, 8 upvotes are done and 3 comments posted.",
    "isSuccess": true,
    "steps": [
      {
        "created_at": "2025-01-01T10:00:00Z",
        "finished_at": "2025-01-01T10:00:05Z",
        "description": "Opened Reddit search page",
        "status": "completed",
        "step_number": 1
      }
      // ... more steps starting from from_step
    ],
    "total_steps": 5
  },
  "errors": {},
  "description": "Task retrieved successfully"
}
```

### Field semantics

- **status**: high-level task status: `"processing" | "finished" | "failed"`.
- **output**: final task output (if available).
- **isSuccess**: `true` if task finished successfully, otherwise `false`.
- **steps**: list of task steps starting from `from_step` (or from `1` by default).
- **step_number**: sequential number of the step within the task, always starting at `1` in this array.
- **total_steps**: total number of steps the task has, independent of `from_step`.

### Task options

| Option | Description            |
|--------|------------------------|
| `task_description` | Your prompt (required) |
| `mode` | Always use `fast` |
| `profile_id` | Use a profile for auth |
| `skip_plan_approval` | Always use `true`|

---

## Full API Reference

See [references/api.md](references/api.md) for all endpoints including Sessions, Files, Skills, and Skills Marketplace.
