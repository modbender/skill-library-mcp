# HITL Protocol — Agent Integration Guide

This guide is for **agent developers** who want to handle HITL responses from services.

## Core Concept

When a service needs human input, it returns HTTP 202 instead of 200. The response body contains a `hitl` object with a `review_url` (for the human) and a `poll_url` (for the agent). The agent forwards the URL, polls for the result, and continues.

## Implementation Checklist

### Minimum (Polling)

- [ ] **Detect HTTP 202** — check `response.status_code == 202`
- [ ] **Check for `hitl` in body** — not all 202s are HITL (standard async exists)
- [ ] **Validate required fields** — `review_url`, `poll_url`, `type`, `prompt`, `case_id`, `created_at`, `expires_at`
- [ ] **Forward review URL** — send `hitl.review_url` to human with `hitl.prompt` as context
- [ ] **Poll for result** — `GET hitl.poll_url` at 30-second to 5-minute intervals
- [ ] **Handle `completed`** — extract `result.action` and `result.data`, continue workflow
- [ ] **Handle `expired`** — execute `hitl.default_action` or inform user
- [ ] **Handle `cancelled`** — inform user, abort or skip
- [ ] **Respect rate limits** — max 60 requests/min per case, check `Retry-After` header

### Enhanced (Optional)

- [ ] **SSE transport** — connect to `hitl.events_url` if present
- [ ] **Callback transport** — include `hitl_callback_url` in original request
- [ ] **Multi-round** — follow `next_case_id` for edit cycles
- [ ] **Input form metadata** — relay form step count/titles to human
- [ ] **Sensitive fields** — do NOT log values for fields with `sensitive: true`
- [ ] **Reminders** — re-send URL at `hitl.reminder_at` timestamps
- [ ] **Progress tracking** — relay `progress` from `in_progress` poll responses

## Complete Polling Implementation

```python
import time
import httpx

def handle_response(response, send_to_user, auth_headers):
    """Handle any HTTP response, detecting HITL when present."""

    if response.status_code != 202:
        return response.json()  # Normal response

    body = response.json()
    hitl = body.get("hitl")
    if not hitl:
        return body  # 202 without HITL (standard async)

    # Validate required fields
    for field in ("review_url", "poll_url", "type", "prompt", "case_id"):
        if field not in hitl:
            raise ValueError(f"HITL object missing required field: {field}")

    # Forward URL to human
    message = body.get("message", hitl["prompt"])
    send_to_user(f"{message}\n\n{hitl['review_url']}")

    # Poll for result
    while True:
        time.sleep(30)
        poll_response = httpx.get(hitl["poll_url"], headers=auth_headers)

        # Handle rate limiting
        if poll_response.status_code == 429:
            retry_after = int(poll_response.headers.get("Retry-After", 60))
            time.sleep(retry_after)
            continue

        poll = poll_response.json()
        status = poll["status"]

        if status == "completed":
            return poll["result"]  # {action: "select", data: {...}}

        if status == "expired":
            default = hitl.get("default_action", "skip")
            send_to_user(f"Review expired. Using default action: {default}")
            return {"action": default, "data": {}, "expired": True}

        if status == "cancelled":
            reason = poll.get("reason", "User cancelled")
            send_to_user(f"Review cancelled: {reason}")
            return {"action": "cancelled", "data": {}, "cancelled": True}

        # pending, opened, in_progress → keep polling
        if status == "opened":
            pass  # Optional: send_to_user("Review page opened")
        if status == "in_progress" and "progress" in poll:
            p = poll["progress"]
            pass  # Optional: send_to_user(f"Step {p['current_step']}/{p['total_steps']}")
```

## URL Delivery Strategies

Choose based on your agent's environment:

| Mode | When | How |
|------|------|-----|
| **Messaging** (default) | Agent is a bot (Telegram, Slack, Discord, WhatsApp) | Send URL as clickable link in chat message |
| **Messaging + Inline** (v0.7) | Bot + Service provides `submit_url` | Native buttons in chat + URL fallback |
| **Desktop CLI** | Agent runs on user's own machine | `webbrowser.open(url)` |
| **Remote CLI** | Agent on remote server (SSH) | Print URL (optionally QR code) |

In most real deployments, the agent is a bot on a server — not on the human's device. The agent sends messages to the human via the messaging platform's API. The human taps the URL link, and the browser opens on **their** device.

```python
from urllib.parse import urlparse

def handle_hitl(hitl: dict, send_to_user) -> None:
    """Forward a HITL review to the human."""
    review_url = hitl["review_url"]

    # Validate URL
    parsed = urlparse(review_url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("Invalid review URL: must be HTTPS with a valid host")

    # v0.7: Inline buttons for simple decisions (messaging platforms)
    if "submit_url" in hitl and "submit_token" in hitl:
        send_inline_buttons(
            prompt=hitl["prompt"],
            actions=hitl.get("inline_actions", []),
            review_url=review_url,       # Always include URL fallback
        )
    else:
        # Standard: send URL as clickable link
        send_to_user(f"{hitl['prompt']}\n{review_url}")
```

> **Desktop CLI agents** (running on the user's machine, e.g. Claude Code): Use `webbrowser.open(review_url)` to open the URL directly in the user's browser. This only applies when agent and human share the same device.

> **Remote CLI agents** (SSH): Print the URL for manual opening. Optionally render a QR code with `qrencode -t ANSI <url>` if installed.

## SSE Event Stream

If `hitl.events_url` is present, use SSE for real-time updates instead of polling:

```python
import httpx_sse, json

def handle_hitl_sse(hitl, send_to_user, auth_headers):
    events_url = hitl.get("events_url")
    if not events_url:
        return handle_hitl_polling(hitl, send_to_user, auth_headers)

    try:
        with httpx_sse.connect(events_url, headers=auth_headers) as sse:
            for event in sse:
                if event.event == "review.completed":
                    data = json.loads(event.data)
                    return data["result"]

                elif event.event == "review.expired":
                    data = json.loads(event.data)
                    return {"action": data["default_action"], "expired": True}

                elif event.event == "review.cancelled":
                    data = json.loads(event.data)
                    return {"action": "cancelled", "reason": data.get("reason")}

                elif event.event == "review.opened":
                    send_to_user("Review page opened")

                elif event.event == "review.reminder":
                    send_to_user(f"Reminder: {hitl['review_url']}")

    except ConnectionError:
        return handle_hitl_polling(hitl, send_to_user, auth_headers)
```

Support reconnection via `Last-Event-ID` header. Always fall back to polling on failure.

### SSE Event Types

| Event | Payload | When |
|-------|---------|------|
| `review.opened` | `{case_id, opened_at}` | Human opens URL |
| `review.in_progress` | `{case_id, progress}` | Human interacts |
| `review.completed` | `{case_id, completed_at, result}` | Human submits |
| `review.expired` | `{case_id, expired_at, default_action}` | Timeout |
| `review.cancelled` | `{case_id, cancelled_at, reason}` | Human cancels |
| `review.reminder` | `{case_id, review_url}` | Reminder triggered |

## Callback/Webhook

For agents with a publicly reachable endpoint:

1. Include `hitl_callback_url` in your original API request
2. Expose `POST /webhooks/hitl` on your server
3. Verify signature: `X-HITL-Signature: sha256=<hmac>`

```python
import hmac, hashlib

def verify_hitl_signature(body: bytes, signature_header: str, secret: str) -> bool:
    expected = "sha256=" + hmac.new(
        secret.encode(), body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header)
```

Still maintain polling as fallback — the poll endpoint is the source of truth.

## Multi-Round Reviews

Approval-type reviews may involve edit cycles:

```
Round 1: case_id="review_draft1"
  → Human: action="edit", data={feedback: "Fix the intro"}
  → Poll: next_case_id="review_draft2"

Round 2: case_id="review_draft2", previous_case_id="review_draft1"
  → Agent revises artifact based on feedback
  → Human: action="approve"
  → Workflow continues
```

After `completed` with `action="edit"`:
1. Check `poll.next_case_id` for the follow-up case
2. Revise your artifact based on `result.data.feedback`
3. Poll the new case until it completes

## Input Form Handling

When `type` is `"input"`, the `context.form` tells you about the form structure:

```python
hitl = response.json()["hitl"]

if hitl["type"] == "input" and "form" in hitl.get("context", {}):
    form = hitl["context"]["form"]

    if "steps" in form:
        # Multi-step wizard
        step_titles = [s["title"] for s in form["steps"]]
        total_fields = sum(len(s["fields"]) for s in form["steps"])
        send_to_user(
            f"{len(form['steps'])}-step form ({', '.join(step_titles)}). "
            f"{total_fields} fields total.\n{hitl['review_url']}"
        )
    elif "fields" in form:
        # Single-step form
        required = [f for f in form["fields"] if f.get("required")]
        send_to_user(
            f"Please fill {len(form['fields'])} fields "
            f"({len(required)} required).\n{hitl['review_url']}"
        )
```

### Sensitive Fields

Fields with `sensitive: true` (like salary, passwords) MUST NOT be logged or displayed by the agent. Only the human sees these values in the browser.

## Reminders

If `hitl.reminder_at` is present:

```python
import datetime

reminder_at = hitl.get("reminder_at")
if reminder_at:
    # Can be a single timestamp or array
    timestamps = [reminder_at] if isinstance(reminder_at, str) else reminder_at

    for ts in timestamps:
        reminder_time = datetime.datetime.fromisoformat(ts)
        # Schedule: if case is still pending/opened at reminder_time,
        # re-send the review URL to the human
```

Do NOT send reminders for terminal states (`completed`, `expired`, `cancelled`).

## Channel-Native Inline Actions (v0.7)

When a service includes `submit_url` and `submit_token` in the HITL object, the agent MAY render native messaging buttons for simple decisions instead of (or in addition to) a URL link.

### Detection

```python
def has_inline_submit(hitl: dict) -> bool:
    return "submit_url" in hitl and "submit_token" in hitl
```

### Rendering Decision

```python
def render_hitl_message(hitl: dict, platform: str):
    review_type = hitl["type"]
    inline_actions = hitl.get("inline_actions")

    if not has_inline_submit(hitl):
        # No inline submit → URL-only (v0.5 behavior)
        return render_url_button(hitl["review_url"], "Review")

    if review_type == "confirmation":
        # 2 buttons: Confirm + Cancel — works on ALL platforms (incl. WhatsApp max 3)
        return render_inline_plus_url(
            actions=inline_actions or ["confirm", "cancel"],
            url=hitl["review_url"],
            url_label="View Details"
        )

    if review_type == "escalation":
        # 3 buttons: Retry + Skip + Abort — fits WhatsApp max 3
        # But if 'retry' is NOT in inline_actions, show only skip/abort inline
        return render_inline_plus_url(
            actions=inline_actions or ["retry", "skip", "abort"],
            url=hitl["review_url"],
            url_label="View Error Details"
        )

    if review_type == "approval":
        if inline_actions and "edit" not in inline_actions:
            # Simple approve/reject inline
            return render_inline_plus_url(
                actions=inline_actions,
                url=hitl["review_url"],
                url_label="Review & Edit"
            )
        else:
            # Edit needs browser → URL only
            return render_url_button(hitl["review_url"], "Review & Approve")

    if review_type in ("selection", "input"):
        # Always needs full review page
        if platform == "telegram":
            return render_webapp_button(hitl["review_url"], "Open")
        else:
            return render_url_button(hitl["review_url"], "Open")
```

### Inline Submit Handler

```python
import httpx

async def handle_inline_action(case_mapping: dict, action: str, user_info: dict):
    """Called when a human taps a native messaging button."""

    response = await httpx.AsyncClient().post(
        case_mapping["submit_url"],
        headers={
            "Authorization": f"Bearer {case_mapping['submit_token']}",
            "Content-Type": "application/json"
        },
        json={
            "action": action,
            "data": {},
            "submitted_via": user_info["submitted_via"],
            "submitted_by": {
                "platform": user_info["platform"],
                "platform_user_id": user_info["platform_user_id"],
                "display_name": user_info.get("display_name")
            }
        }
    )

    if response.status_code == 200:
        return {"success": True, "result": response.json()}
    elif response.status_code == 403:
        # Action not permitted inline → direct to review_url
        error = response.json()
        return {"success": False, "redirect_url": error.get("review_url")}
    elif response.status_code == 409:
        return {"success": False, "reason": "already_responded"}
    elif response.status_code == 410:
        return {"success": False, "reason": "expired"}
    else:
        return {"success": False, "reason": f"http_{response.status_code}"}
```

### Platform-Specific Callback Data Encoding

Each messaging platform has different limits for action callback data. The agent must encode enough information to identify the case and action when a button is tapped.

| Platform | Field | Limit | Strategy |
|----------|-------|-------|----------|
| **Telegram** | `callback_data` | 64 bytes | `hitl:{sha256(case_id)[:6]}:{action}` + agent-side mapping table |
| **Slack** | `value` | 2000 chars | Full JSON: `{"case_id":"...","action":"..."}` — no mapping needed |
| **Discord** | `custom_id` | 100 chars | `hitl:{case_id}:{action}` — usually fits directly |
| **WhatsApp** | `reply.id` | 256 chars | `hitl_{case_id}_{action}` — usually fits directly |
| **MS Teams** | `Action.Submit data` | Unbounded JSON | Full metadata in card action data |

**Telegram mapping table example:**

```python
import hashlib

# Agent-side in-memory mapping (or Redis/SQLite for persistence)
case_store: dict[str, dict] = {}

def register_case(hitl: dict) -> str:
    """Generate a 6-char short ID and store the case mapping."""
    short_id = hashlib.sha256(hitl["case_id"].encode()).hexdigest()[:6]
    case_store[short_id] = {
        "case_id": hitl["case_id"],
        "submit_url": hitl["submit_url"],
        "submit_token": hitl["submit_token"],
        "review_url": hitl["review_url"]
    }
    return short_id

def callback_data(short_id: str, action: str) -> str:
    """Generate Telegram callback_data (max 64 bytes)."""
    return f"hitl:{short_id}:{action}"  # e.g., "hitl:a1b2c3:confirm" = 20 bytes

def resolve_callback(data: str) -> tuple[dict, str] | None:
    """Parse callback_data and return (case_mapping, action)."""
    if not data.startswith("hitl:"):
        return None
    parts = data.split(":")
    short_id, action = parts[1], parts[2]
    case = case_store.get(short_id)
    return (case, action) if case else None
```

### Security: Never Leak submit_token

The `submit_token` MUST NOT appear in:
- Telegram `callback_data` (transits Telegram servers)
- Discord `custom_id` (transits Discord servers)
- Slack `action_id` or `value` (transits Slack servers)
- WhatsApp `reply.id` (transits WhatsApp servers)
- Any client-side or third-party visible field

Store `submit_token` only in the agent's own memory/database. Look it up using the case mapping when a button callback arrives.

### Enhanced Checklist (v0.7)

- [ ] **Detect `submit_url`** — check if `submit_url` and `submit_token` are present in the HITL object
- [ ] **Render native buttons** — for confirmation, escalation, simple approval when inline submit is available
- [ ] **Always include URL fallback** — render a URL button to `review_url` alongside inline buttons
- [ ] **Handle inline submit response** — `200` OK, `403` action not inline, `409` duplicate, `410` expired
- [ ] **Update message after action** — edit original message, remove buttons, show result
- [ ] **Never leak submit_token** — store only agent-side, never in callback data
- [ ] **Respect inline_actions** — only render buttons for actions listed in `inline_actions`
- [ ] **Fallback to URL** — if platform doesn't support buttons or submit_url is absent, use URL-only delivery

## What NOT to Do

- **Do NOT render the review UI** — the service hosts the review page. The agent is a messenger.
- **Do NOT submit responses on behalf of the human** — unless the human explicitly triggered a native messaging button and `submit_url` is available.
- **Do NOT ignore HTTP 202 + HITL** — proceeding without human input violates the protocol.
- **Do NOT poll too frequently** — respect rate limits (max 60/min). Check `Retry-After` header.
- **Do NOT store review URLs long-term** — they contain time-limited tokens that expire.
- **Do NOT log sensitive field values** — fields marked `sensitive: true` are for human eyes only.
- **Do NOT put `submit_token` in callback data** — it must never transit through third-party messaging servers.

## Decision Tree

```
Agent receives HTTP response
│
├── Status 200 → Use result directly
│
├── Status 202 + "hitl" in body
│   ├── Forward hitl.review_url to human with hitl.prompt
│   ├── Poll hitl.poll_url (or connect SSE / register callback)
│   │
│   ├── completed → use result.action + result.data
│   │   └── Check next_case_id for multi-round
│   ├── expired → execute default_action, inform human
│   └── cancelled → inform human, skip/abort
│
├── Status 202 without "hitl" → standard async (not HITL)
│
├── Status 429 → wait Retry-After seconds, retry
├── Status 4xx → handle client error
└── Status 5xx → retry with exponential backoff
```

## Detailed Agent Checklist

For the complete implementation guide with pseudocode for all transport modes, multi-round reviews, input forms, reminders, and delivery modes, see [agents/checklist.md](../../agents/checklist.md).
