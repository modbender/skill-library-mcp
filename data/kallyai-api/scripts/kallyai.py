#!/usr/bin/env python3
"""
KallyAI Executive Assistant CLI — Full-domain management from the terminal.

Domains: coordination, calls, inbound, phone, actions, messages, search,
         email, channels, outreach, budget, credits, subscription, referrals,
         notifications.

Usage:
    kallyai.py ask "Book a table at Nobu for 4 tonight"
    kallyai.py credits balance
    kallyai.py calls make -p "+15551234567" -t "Ask about hours"
    kallyai.py inbound calls --status completed
    kallyai.py phone list
    kallyai.py coord goals --status active
    kallyai.py messages inbox
"""

import argparse
import http.server
import json
import secrets
import socketserver
import sys
import threading
import time
import urllib.parse
import webbrowser
from pathlib import Path

try:
    import httpx
except ImportError:
    print(json.dumps({"error": {"code": "missing_dependency", "message": "httpx is required. Install with: pip install httpx"}}))
    sys.exit(1)

# =============================================================================
# Configuration
# =============================================================================

API_BASE = "https://api.kallyai.com"
TOKEN_FILE = Path.home() / ".kallyai_token.json"
CALLBACK_PORT_RANGE = (8740, 8760)
USER_AGENT = "KallyAI-CLI/2.0"

# Global for OAuth callback
auth_result = {"access_token": None, "refresh_token": None, "error": None, "state": None}


# =============================================================================
# Output Helpers
# =============================================================================

def output_json(data: dict):
    """Print machine-readable JSON (default mode)."""
    print(json.dumps(data, indent=2, default=str))


def output_human(title: str, rows: list[dict] | None = None, fields: dict | None = None, footer: str | None = None):
    """Print human-friendly formatted output."""
    print(f"\n{title}")
    print("=" * 60)
    if fields:
        max_key = max(len(k) for k in fields) if fields else 0
        for k, v in fields.items():
            print(f"  {k:<{max_key + 2}} {v}")
    if rows:
        for row in rows:
            parts = [str(v) for v in row.values()]
            print(f"  {' | '.join(parts)}")
    if footer:
        print(f"\n  {footer}")
    print("=" * 60)


def output_error(code: str, message: str, suggestion: str | None = None):
    """Print structured error (always JSON for parseability)."""
    err = {"error": {"code": code, "message": message}}
    if suggestion:
        err["error"]["suggestion"] = suggestion
    print(json.dumps(err, indent=2), file=sys.stderr)
    sys.exit(1)


def is_human(args) -> bool:
    """Check if --human flag is set."""
    return getattr(args, "human", False)


# =============================================================================
# Token Management
# =============================================================================

def load_token() -> str | None:
    """Load saved token if valid, refresh if expired."""
    if TOKEN_FILE.exists():
        try:
            data = json.loads(TOKEN_FILE.read_text())
            if data.get("expires_at", 0) > time.time():
                return data.get("access_token")
            if data.get("refresh_token"):
                return _refresh_token(data["refresh_token"])
        except Exception:
            pass
    return None


def save_token(access_token: str, refresh_token: str = None, expires_in: int = 3600):
    """Save token securely (0600 permissions)."""
    TOKEN_FILE.write_text(json.dumps({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": time.time() + expires_in - 60,
    }))
    TOKEN_FILE.chmod(0o600)


def _refresh_token(refresh_tok: str) -> str | None:
    """Refresh an expired access token."""
    with httpx.Client() as client:
        resp = client.post(
            f"{API_BASE}/v1/auth/refresh",
            json={"refresh_token": refresh_tok},
            headers={"User-Agent": USER_AGENT},
        )
        if resp.status_code == 200:
            data = resp.json()
            save_token(data["access_token"], data.get("refresh_token"), data.get("expires_in", 3600))
            return data["access_token"]
    return None


# =============================================================================
# OAuth Authentication
# =============================================================================

class CallbackHandler(http.server.SimpleHTTPRequestHandler):
    """Handle OAuth callback with tokens in URL."""

    def do_GET(self):
        global auth_result
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "access_token" in params:
            auth_result["access_token"] = params["access_token"][0]
            auth_result["refresh_token"] = params.get("refresh_token", [None])[0]
            auth_result["state"] = params.get("state", [None])[0]
            self._send_html("Authentication Successful!", "#00d4ff",
                            "You can close this window and return to your terminal.")
        elif "error" in params:
            import html
            auth_result["error"] = params["error"][0]
            safe_error = html.escape(auth_result["error"])
            self._send_html("Authentication Failed", "#f87171", safe_error)
        else:
            self.send_response(404)
            self.end_headers()

    def _send_html(self, title: str, color: str, message: str):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(f'''<!DOCTYPE html>
<html><head><title>KallyAI - {title}</title></head>
<body style="font-family:system-ui;text-align:center;padding:50px;background:#06080d;color:#e6edf3;">
<h2 style="color:{color};">{title}</h2><p>{message}</p>
<script>setTimeout(() => window.close(), 2000);</script>
</body></html>'''.encode())

    def log_message(self, format, *args):
        pass


def authenticate() -> str:
    """OAuth authentication via browser with CSRF protection."""
    global auth_result
    auth_result = {"access_token": None, "refresh_token": None, "error": None, "state": None}

    csrf_state = secrets.token_urlsafe(32)

    server = None
    callback_port = None
    for port in range(CALLBACK_PORT_RANGE[0], CALLBACK_PORT_RANGE[1]):
        try:
            server = socketserver.TCPServer(("127.0.0.1", port), CallbackHandler)
            callback_port = port
            break
        except OSError:
            continue

    if server is None:
        output_error("port_unavailable", f"No available port in range {CALLBACK_PORT_RANGE}")

    server_thread = threading.Thread(target=lambda: server.serve_forever())
    server_thread.daemon = True
    server_thread.start()

    callback_url = f"http://127.0.0.1:{callback_port}"
    auth_url = f"{API_BASE}/v1/auth/cli?redirect_uri={urllib.parse.quote(callback_url)}&state={csrf_state}"

    print("\nOpening browser for sign-in...", file=sys.stderr)
    print("Sign in with your Google or Apple account.\n", file=sys.stderr)
    webbrowser.open(auth_url)

    timeout = 180
    start = time.time()
    while auth_result["access_token"] is None and auth_result["error"] is None:
        if time.time() - start > timeout:
            server.shutdown()
            output_error("auth_timeout", "Authentication timed out after 180s")
        time.sleep(0.5)

    server.shutdown()

    if auth_result["error"]:
        output_error("auth_failed", f"Authentication failed: {auth_result['error']}")

    if auth_result.get("state") != csrf_state:
        output_error("csrf_mismatch", "CSRF state mismatch (possible attack)")

    save_token(auth_result["access_token"], auth_result["refresh_token"], 3600)
    print("Authentication successful!", file=sys.stderr)
    return auth_result["access_token"]


def require_token() -> str:
    """Get token, authenticating if needed."""
    token = load_token()
    if not token:
        token = authenticate()
    return token


# =============================================================================
# API Client
# =============================================================================

def api_request(method: str, endpoint: str, token: str, retries: int = 1, **kwargs) -> dict:
    """Make authenticated API request with retry and structured errors."""
    last_err = None
    for attempt in range(retries + 1):
        try:
            with httpx.Client(timeout=300.0) as client:
                resp = client.request(
                    method,
                    f"{API_BASE}{endpoint}",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "User-Agent": USER_AGENT,
                        **(kwargs.pop("headers", {})),
                    },
                    **kwargs,
                )

            if resp.status_code == 401:
                TOKEN_FILE.unlink(missing_ok=True)
                output_error("token_expired", "Token expired. Please run again to re-authenticate.")

            if resp.status_code >= 400:
                try:
                    err = resp.json().get("error", {})
                    code = err.get("code", f"http_{resp.status_code}")
                    msg = err.get("message") or err.get("details", {}).get("message", resp.text)
                    output_error(code, msg)
                except json.JSONDecodeError:
                    output_error(f"http_{resp.status_code}", resp.text)

            if resp.text:
                return resp.json()
            return {}

        except httpx.TimeoutException as e:
            last_err = e
            if attempt < retries:
                time.sleep(2 ** attempt)
                continue
            output_error("timeout", f"Request timed out after {retries + 1} attempts")

        except httpx.ConnectError as e:
            output_error("connection_error", f"Cannot connect to {API_BASE}: {e}")

    output_error("request_failed", str(last_err))


# =============================================================================
# ask — The 80% command (routes through coordination AI)
# =============================================================================

def cmd_ask(args):
    """Send a natural language request to the coordination AI."""
    token = require_token()
    message = " ".join(args.message)
    data = api_request("POST", "/v1/coordination/message", token, json={"message": message})
    if is_human(args):
        output_human("KallyAI Response", fields={"Response": data.get("response", ""), "Goal ID": data.get("goal_id", "N/A")})
    else:
        output_json(data)


# =============================================================================
# coord — Coordination & Goals
# =============================================================================

def cmd_coord_message(args):
    """Send a message to the coordination AI."""
    token = require_token()
    payload = {"message": " ".join(args.text)}
    if args.conversation_id:
        payload["conversation_id"] = args.conversation_id
    data = api_request("POST", "/v1/coordination/message", token, json=payload)
    output_json(data) if not is_human(args) else output_human("Coordination Response", fields={"Response": data.get("response", ""), "Goal ID": data.get("goal_id", "N/A")})


def cmd_coord_history(args):
    """Get coordination conversation history."""
    token = require_token()
    params = {}
    if args.conversation_id:
        params["conversation_id"] = args.conversation_id
    if args.limit:
        params["limit"] = args.limit
    data = api_request("GET", "/v1/coordination/history", token, params=params)
    output_json(data)


def cmd_coord_conversations(args):
    """List coordination conversations."""
    token = require_token()
    data = api_request("GET", "/v1/coordination/conversations", token)
    output_json(data)


def cmd_coord_new(args):
    """Start a new coordination conversation."""
    token = require_token()
    data = api_request("POST", "/v1/coordination/conversations", token)
    output_json(data)


def cmd_coord_goals(args):
    """List goals with optional status filter."""
    token = require_token()
    params = {}
    if args.status:
        params["status"] = args.status
    if args.limit:
        params["limit"] = args.limit
    data = api_request("GET", "/v1/coordination/goals", token, params=params)
    if is_human(args):
        goals = data.get("goals", data.get("items", []))
        rows = [{"ID": g.get("id", "")[:8], "Status": g.get("status", ""), "Title": g.get("title", "")[:40]} for g in goals]
        output_human(f"Goals ({len(rows)})", rows=rows)
    else:
        output_json(data)


def cmd_coord_goal(args):
    """Get goal details."""
    token = require_token()
    data = api_request("GET", f"/v1/coordination/goals/{args.id}", token)
    output_json(data)


def cmd_coord_goal_tree(args):
    """Get goal tree (goal + sub-goals)."""
    token = require_token()
    data = api_request("GET", f"/v1/coordination/goals/{args.id}/tree", token)
    output_json(data)


def cmd_coord_cancel_goal(args):
    """Cancel a goal."""
    token = require_token()
    data = api_request("POST", f"/v1/coordination/goals/{args.id}/cancel", token)
    output_json(data)


def cmd_coord_cascade_cancel(args):
    """Cancel a goal and all sub-goals."""
    token = require_token()
    data = api_request("POST", f"/v1/coordination/goals/{args.id}/cascade-cancel", token)
    output_json(data)


def cmd_coord_escalate(args):
    """Escalate a goal for user attention."""
    token = require_token()
    data = api_request("POST", f"/v1/coordination/goals/{args.id}/escalate", token)
    output_json(data)


def cmd_coord_approve_step(args):
    """Approve the next step of a goal."""
    token = require_token()
    data = api_request("POST", f"/v1/coordination/goals/{args.id}/approve-step", token)
    output_json(data)


def cmd_coord_accept(args):
    """Accept a goal's outcome."""
    token = require_token()
    data = api_request("POST", f"/v1/coordination/goals/{args.id}/accept-outcome", token)
    output_json(data)


def cmd_coord_continue(args):
    """Continue negotiating on a goal."""
    token = require_token()
    data = api_request("POST", f"/v1/coordination/goals/{args.id}/continue-negotiating", token)
    output_json(data)


def cmd_coord_archive(args):
    """Archive a completed goal."""
    token = require_token()
    data = api_request("POST", f"/v1/coordination/goals/{args.id}/archive", token)
    output_json(data)


def cmd_coord_batch_archive(args):
    """Archive multiple goals."""
    token = require_token()
    data = api_request("POST", "/v1/coordination/goals/batch-archive", token, json={"goal_ids": args.ids})
    output_json(data)


def cmd_coord_budget(args):
    """Get budget details for a goal."""
    token = require_token()
    data = api_request("GET", f"/v1/coordination/goals/{args.id}/budget", token)
    output_json(data)


# =============================================================================
# calls — Phone Calls
# =============================================================================

def cmd_calls_make(args):
    """Make a phone call."""
    token = require_token()
    submission = {
        "task_category": args.category,
        "task_description": args.task,
        "respondent_phone": args.phone,
        "language": args.language,
        "call_language": args.language,
    }
    if args.name:
        submission["user_name"] = args.name
    if args.business:
        submission["business_name"] = args.business
    if args.party_size:
        submission["party_size"] = args.party_size
    if args.date:
        submission["appointment_date"] = args.date
    if args.time:
        submission["appointment_time"] = args.time

    result = api_request(
        "POST", "/v1/calls", token,
        json={"submission": submission, "timezone": args.timezone},
        headers={"Idempotency-Key": f"cli-{secrets.token_hex(8)}"},
    )
    if is_human(args):
        output_human("Call Initiated", fields={
            "Call ID": result.get("call_id", ""),
            "Status": result.get("status", ""),
            "Summary": result.get("highlights", ""),
            "Next Steps": result.get("next_steps", ""),
            "Duration": f"{result.get('duration_seconds', 0):.1f}s" if result.get("duration_seconds") else "N/A",
        })
    else:
        output_json(result)


def cmd_calls_history(args):
    """List recent calls."""
    token = require_token()
    params = {"limit": args.limit} if args.limit else {}
    data = api_request("GET", "/v1/calls", token, params=params)
    if is_human(args):
        items = data.get("calls", data.get("items", []))
        rows = []
        for c in items:
            meta = c.get("metadata", {}) or {}
            created = meta.get("created_at", c.get("created_at", ""))[:16].replace("T", " ")
            rows.append({"Created": created, "Status": c.get("status", ""), "ID": c.get("call_id", "")[:8]})
        output_human(f"Call History ({len(rows)})", rows=rows, footer="Use: kallyai.py calls info <ID>")
    else:
        output_json(data)


def cmd_calls_info(args):
    """Get call details."""
    token = require_token()
    data = api_request("GET", f"/v1/calls/{args.id}", token)
    if is_human(args):
        sub = data.get("submission", {}) or {}
        meta = data.get("metadata", {}) or {}
        output_human("Call Details", fields={
            "ID": data.get("call_id", ""),
            "Status": data.get("status", ""),
            "To": sub.get("respondent_phone", ""),
            "Business": sub.get("business_name", ""),
            "Task": sub.get("task_description", ""),
            "Created": meta.get("created_at", ""),
            "Duration": f"{data.get('duration_seconds', 0):.1f}s" if data.get("duration_seconds") else "N/A",
            "Summary": data.get("highlights", ""),
            "Next Steps": data.get("next_steps", ""),
        })
    else:
        output_json(data)


def cmd_calls_transcript(args):
    """Get call transcript."""
    token = require_token()
    data = api_request("GET", f"/v1/calls/{args.id}/transcript", token)
    output_json(data)


def cmd_calls_recording(args):
    """Get call recording URL."""
    token = require_token()
    data = api_request("GET", f"/v1/calls/{args.id}/recording", token)
    output_json(data)


def cmd_calls_calendar(args):
    """Get calendar event for a call."""
    token = require_token()
    data = api_request("GET", f"/v1/calls/{args.id}/calendar.ics", token)
    output_json(data)


def cmd_calls_cancel(args):
    """Cancel a scheduled/in-progress call."""
    token = require_token()
    data = api_request("POST", f"/v1/calls/{args.id}/cancel", token)
    output_json(data)


def cmd_calls_reschedule(args):
    """Reschedule a call."""
    token = require_token()
    payload = {}
    if args.date:
        payload["date"] = args.date
    if args.time:
        payload["time"] = args.time
    data = api_request("POST", f"/v1/calls/{args.id}/reschedule", token, json=payload)
    output_json(data)


def cmd_calls_stop(args):
    """Stop an active call immediately."""
    token = require_token()
    data = api_request("POST", f"/v1/calls/{args.id}/stop", token)
    output_json(data)


# =============================================================================
# actions — Autonomous Actions
# =============================================================================

def cmd_actions_calendar_create(args):
    """Create a calendar event."""
    token = require_token()
    payload = {"title": args.title, "start": args.start}
    if args.end:
        payload["end"] = args.end
    if args.location:
        payload["location"] = args.location
    if args.description:
        payload["description"] = args.description
    data = api_request("POST", "/v1/actions/calendar/events", token, json=payload)
    output_json(data)


def cmd_actions_calendar_slots(args):
    """Get available calendar slots."""
    token = require_token()
    params = {}
    if args.date:
        params["date"] = args.date
    if args.duration:
        params["duration_minutes"] = args.duration
    data = api_request("GET", "/v1/actions/calendar/slots", token, params=params)
    output_json(data)


def cmd_actions_calendar_sync(args):
    """Sync calendar with external provider."""
    token = require_token()
    data = api_request("POST", "/v1/actions/calendar/sync", token)
    output_json(data)


def cmd_actions_calendar_delete(args):
    """Delete a calendar event."""
    token = require_token()
    data = api_request("DELETE", f"/v1/actions/calendar/events/{args.id}", token)
    output_json(data)


def cmd_actions_restaurant_search(args):
    """Search for restaurants."""
    token = require_token()
    payload = {"query": " ".join(args.query)}
    if args.location:
        payload["location"] = args.location
    if args.party_size:
        payload["party_size"] = args.party_size
    if args.date:
        payload["date"] = args.date
    if args.time:
        payload["time"] = args.time
    data = api_request("POST", "/v1/actions/bookings/restaurants/search", token, json=payload)
    output_json(data)


def cmd_actions_booking_create(args):
    """Create a booking/reservation."""
    token = require_token()
    payload = {"type": args.type}
    if args.restaurant_id:
        payload["restaurant_id"] = args.restaurant_id
    if args.date:
        payload["date"] = args.date
    if args.time:
        payload["time"] = args.time
    if args.party_size:
        payload["party_size"] = args.party_size
    if args.name:
        payload["name"] = args.name
    if args.notes:
        payload["notes"] = args.notes
    data = api_request("POST", "/v1/actions/bookings", token, json=payload)
    output_json(data)


def cmd_actions_booking_cancel(args):
    """Cancel a booking."""
    token = require_token()
    data = api_request("DELETE", f"/v1/actions/bookings/{args.id}", token)
    output_json(data)


def cmd_actions_bill_analyze(args):
    """Analyze a bill for savings/errors."""
    token = require_token()
    payload = {"description": " ".join(args.description)}
    if args.amount:
        payload["amount"] = args.amount
    if args.provider:
        payload["provider"] = args.provider
    data = api_request("POST", "/v1/actions/bills/analyze", token, json=payload)
    output_json(data)


def cmd_actions_bill_dispute(args):
    """Dispute a bill charge."""
    token = require_token()
    payload = {"description": " ".join(args.description)}
    if args.amount:
        payload["amount"] = args.amount
    if args.provider:
        payload["provider"] = args.provider
    if args.reason:
        payload["reason"] = args.reason
    data = api_request("POST", "/v1/actions/bills/dispute", token, json=payload)
    output_json(data)


def cmd_actions_ride(args):
    """Request a ride."""
    token = require_token()
    payload = {"pickup": args.pickup, "destination": args.destination}
    if args.time:
        payload["pickup_time"] = args.time
    data = api_request("POST", "/v1/actions/tasks/ride", token, json=payload)
    output_json(data)


def cmd_actions_food(args):
    """Order food delivery."""
    token = require_token()
    payload = {"description": " ".join(args.description)}
    if args.address:
        payload["delivery_address"] = args.address
    data = api_request("POST", "/v1/actions/tasks/food", token, json=payload)
    output_json(data)


def cmd_actions_errand(args):
    """Run a general errand."""
    token = require_token()
    payload = {"description": " ".join(args.description)}
    data = api_request("POST", "/v1/actions/tasks/errand", token, json=payload)
    output_json(data)


def cmd_actions_email_send(args):
    """Send an email (queues for approval)."""
    token = require_token()
    payload = {"to": args.to, "subject": args.subject, "body": " ".join(args.body)}
    if args.cc:
        payload["cc"] = args.cc
    data = api_request("POST", "/v1/actions/email/send", token, json=payload)
    output_json(data)


def cmd_actions_email_approve(args):
    """Approve a queued email."""
    token = require_token()
    data = api_request("POST", f"/v1/actions/email/{args.id}/approve", token)
    output_json(data)


def cmd_actions_email_cancel(args):
    """Cancel a queued email."""
    token = require_token()
    data = api_request("POST", f"/v1/actions/email/{args.id}/cancel", token)
    output_json(data)


def cmd_actions_email_outbox(args):
    """List queued/sent emails."""
    token = require_token()
    data = api_request("GET", "/v1/actions/email/outbox", token)
    output_json(data)


def cmd_actions_email_replies(args):
    """Get replies to a sent email."""
    token = require_token()
    data = api_request("GET", f"/v1/actions/email/{args.id}/replies", token)
    output_json(data)


def cmd_actions_log(args):
    """List action log entries."""
    token = require_token()
    params = {}
    if args.type:
        params["type"] = args.type
    if args.limit:
        params["limit"] = args.limit
    data = api_request("GET", "/v1/actions/log", token, params=params)
    output_json(data)


def cmd_actions_undo(args):
    """Undo an action."""
    token = require_token()
    data = api_request("POST", f"/v1/actions/{args.id}/undo", token)
    output_json(data)


# =============================================================================
# messages — Unified Inbox
# =============================================================================

def cmd_messages_inbox(args):
    """List inbox messages."""
    token = require_token()
    params = {}
    if args.channel:
        params["channel"] = args.channel
    if args.limit:
        params["limit"] = args.limit
    if args.unread:
        params["unread"] = "true"
    data = api_request("GET", "/v1/messages/inbox", token, params=params)
    if is_human(args):
        items = data.get("messages", data.get("items", []))
        rows = [{"From": m.get("from", "")[:20], "Subject": m.get("subject", "")[:30], "Channel": m.get("channel", "")} for m in items]
        output_human(f"Inbox ({len(rows)})", rows=rows)
    else:
        output_json(data)


def cmd_messages_read(args):
    """Read a specific message."""
    token = require_token()
    data = api_request("GET", f"/v1/messages/inbox/{args.id}", token)
    output_json(data)


def cmd_messages_thread(args):
    """Get a conversation thread."""
    token = require_token()
    data = api_request("GET", f"/v1/messages/conversation/{args.id}", token)
    output_json(data)


def cmd_messages_mark_read(args):
    """Mark messages as read."""
    token = require_token()
    data = api_request("POST", "/v1/messages/mark-read", token, json={"message_ids": args.ids})
    output_json(data)


# =============================================================================
# search — Research
# =============================================================================

def cmd_search(args):
    """Search for information."""
    token = require_token()
    payload = {"query": " ".join(args.query)}
    if args.location:
        payload["location"] = args.location
    data = api_request("POST", "/v1/search", token, json=payload)
    output_json(data)


def cmd_search_quick(args):
    """Quick search (faster, less detailed)."""
    token = require_token()
    payload = {"query": " ".join(args.query)}
    data = api_request("POST", "/v1/search/quick", token, json=payload)
    output_json(data)


def cmd_search_history(args):
    """List search history."""
    token = require_token()
    data = api_request("GET", "/v1/search/history", token)
    output_json(data)


def cmd_search_sources(args):
    """List available search sources."""
    token = require_token()
    data = api_request("GET", "/v1/search/sources", token)
    output_json(data)


# =============================================================================
# email — Email Account Management
# =============================================================================

def cmd_email_accounts(args):
    """List connected email accounts."""
    token = require_token()
    data = api_request("GET", "/v1/email/accounts", token)
    output_json(data)


def cmd_email_connect_gmail(args):
    """Get Gmail OAuth URL for connecting."""
    token = require_token()
    data = api_request("GET", "/v1/email/oauth/gmail/url", token)
    url = data.get("url", "")
    if url and is_human(args):
        webbrowser.open(url)
        output_human("Gmail Connection", fields={"URL": url}, footer="Browser opened for Gmail sign-in")
    else:
        output_json(data)


def cmd_email_connect_outlook(args):
    """Get Outlook OAuth URL for connecting."""
    token = require_token()
    data = api_request("GET", "/v1/email/oauth/outlook/url", token)
    url = data.get("url", "")
    if url and is_human(args):
        webbrowser.open(url)
        output_human("Outlook Connection", fields={"URL": url}, footer="Browser opened for Outlook sign-in")
    else:
        output_json(data)


def cmd_email_disconnect(args):
    """Disconnect an email account."""
    token = require_token()
    data = api_request("DELETE", f"/v1/email/accounts/{args.id}", token)
    output_json(data)


def cmd_email_list(args):
    """List email messages."""
    token = require_token()
    params = {}
    if args.classification:
        params["classification"] = args.classification
    if args.limit:
        params["limit"] = args.limit
    data = api_request("GET", "/v1/email/messages", token, params=params)
    output_json(data)


def cmd_email_read(args):
    """Read a specific email."""
    token = require_token()
    data = api_request("GET", f"/v1/email/messages/{args.id}", token)
    output_json(data)


def cmd_email_respond(args):
    """Generate/send a response to an email."""
    token = require_token()
    payload = {}
    if args.instructions:
        payload["instructions"] = " ".join(args.instructions)
    data = api_request("POST", f"/v1/email/messages/{args.id}/respond", token, json=payload)
    output_json(data)


def cmd_email_voice_profile(args):
    """Get email voice profile."""
    token = require_token()
    data = api_request("GET", "/v1/email/voice-profile", token)
    output_json(data)


def cmd_email_train_voice(args):
    """Train email voice profile from samples."""
    token = require_token()
    data = api_request("POST", "/v1/email/voice-profile/train", token)
    output_json(data)


# =============================================================================
# budget — Cost Management
# =============================================================================

def cmd_budget_estimate(args):
    """Estimate cost for a task."""
    token = require_token()
    payload = {"type": args.type, "description": " ".join(args.description)}
    data = api_request("POST", "/v1/goals/estimate", token, json=payload)
    if is_human(args):
        output_human("Cost Estimate", fields={
            "Type": args.type,
            "Estimated Credits": data.get("estimated_credits", "N/A"),
            "Breakdown": json.dumps(data.get("breakdown", {}), indent=2),
        })
    else:
        output_json(data)


def cmd_budget_approve(args):
    """Approve budget for a goal."""
    token = require_token()
    data = api_request("POST", f"/v1/goals/{args.goal_id}/approve-budget", token)
    output_json(data)


def cmd_budget_breakdown(args):
    """Get cost breakdown for a goal."""
    token = require_token()
    data = api_request("GET", f"/v1/goals/{args.goal_id}/cost-breakdown", token)
    output_json(data)


def cmd_budget_ack_cap(args):
    """Acknowledge soft cap for a goal."""
    token = require_token()
    data = api_request("POST", f"/v1/goals/{args.goal_id}/acknowledge-soft-cap", token)
    output_json(data)


# =============================================================================
# credits — Balance & History
# =============================================================================

def cmd_credits_balance(args):
    """Check credits balance."""
    token = require_token()
    data = api_request("GET", "/v1/credits/balance", token)
    if is_human(args):
        output_human("Credits Balance", fields={
            "Remaining": f"{data.get('credits_remaining', 0)} credits",
            "Used": f"{data.get('credits_used', 0)} credits",
            "Allocated": f"{data.get('credits_allocated', 0)} credits",
            "Plan": data.get("plan_type", ""),
            "Period End": data.get("period_end", ""),
        })
    else:
        output_json(data)


def cmd_credits_history(args):
    """View credits usage history."""
    token = require_token()
    params = {}
    if args.limit:
        params["limit"] = args.limit
    data = api_request("GET", "/v1/credits/history", token, params=params)
    output_json(data)


def cmd_credits_costs(args):
    """View credit cost reference."""
    token = require_token()
    data = api_request("GET", "/v1/credits/costs", token)
    output_json(data)


# =============================================================================
# Global auth commands
# =============================================================================

def cmd_login(args):
    """Force re-authentication."""
    authenticate()
    output_json({"status": "authenticated"})


def cmd_logout(args):
    """Clear credentials."""
    TOKEN_FILE.unlink(missing_ok=True)
    output_json({"status": "logged_out"})


def cmd_auth_status(args):
    """Check authentication status."""
    token = load_token()
    if token:
        output_json({"authenticated": True})
    else:
        output_json({"authenticated": False})


def cmd_billing(args):
    """Open Stripe billing portal."""
    token = require_token()
    data = api_request("GET", "/v1/stripe/billing-portal", token)
    url = data.get("url", "")
    if url:
        webbrowser.open(url)
    output_json(data)


# =============================================================================
# Inbound (AI Receptionist) Commands
# =============================================================================

def cmd_inbound_calls(args):
    token = require_token()
    params = {"limit": getattr(args, "limit", 20)}
    if getattr(args, "status", None):
        params["status"] = args.status
    if getattr(args, "vip_only", False):
        params["vip_only"] = "true"
    if getattr(args, "date_from", None):
        params["date_from"] = args.date_from
    if getattr(args, "date_to", None):
        params["date_to"] = args.date_to
    data = api_request("GET", "/v1/inbound/calls", token, params=params)
    if is_human(args):
        calls = data.get("calls", [])
        output_human("Inbound Calls", [{"id": c.get("id", "")[:8], "from": c.get("caller_number", ""), "status": c.get("status", ""), "time": c.get("created_at", "")} for c in calls], footer=f"Total: {data.get('total', len(calls))}")
    else:
        output_json(data)


def cmd_inbound_call(args):
    token = require_token()
    data = api_request("GET", f"/v1/inbound/calls/{args.id}", token)
    output_json(data)


def cmd_inbound_transcript(args):
    token = require_token()
    data = api_request("GET", f"/v1/inbound/calls/{args.id}/transcript", token)
    output_json(data)


def cmd_inbound_recording(args):
    token = require_token()
    data = api_request("GET", f"/v1/inbound/calls/{args.id}/recording", token)
    output_json(data)


def cmd_inbound_summary(args):
    token = require_token()
    data = api_request("GET", "/v1/inbound/calls/summary", token)
    output_json(data)


def cmd_inbound_analytics(args):
    token = require_token()
    params = {}
    if getattr(args, "date_from", None):
        params["date_from"] = args.date_from
    if getattr(args, "date_to", None):
        params["date_to"] = args.date_to
    data = api_request("GET", "/v1/inbound/calls/analytics", token, params=params)
    output_json(data)


def cmd_inbound_transfer(args):
    token = require_token()
    data = api_request("POST", f"/v1/inbound/calls/{args.id}/transfer", token, json={"target_number": args.to})
    output_json(data)


def cmd_inbound_takeover(args):
    token = require_token()
    data = api_request("POST", f"/v1/inbound/calls/{args.id}/takeover", token)
    output_json(data)


def cmd_inbound_reject(args):
    token = require_token()
    body = {}
    if getattr(args, "reason", None):
        body["reason"] = args.reason
    data = api_request("POST", f"/v1/inbound/calls/{args.id}/reject", token, json=body)
    output_json(data)


def cmd_inbound_action_item(args):
    token = require_token()
    data = api_request("PATCH", f"/v1/inbound/calls/{args.call_id}/action-items/{args.index}", token, json={"status": args.status})
    output_json(data)


def cmd_inbound_rules(args):
    token = require_token()
    data = api_request("GET", "/v1/inbound/rules", token)
    output_json(data)


def cmd_inbound_add_rule(args):
    token = require_token()
    body = {"name": args.name, "action": args.action, "priority": getattr(args, "priority", 100), "is_active": True}
    if getattr(args, "conditions", None):
        body["conditions"] = json.loads(args.conditions)
    data = api_request("POST", "/v1/inbound/rules", token, json=body)
    output_json(data)


def cmd_inbound_update_rule(args):
    token = require_token()
    body = {}
    if getattr(args, "name", None):
        body["name"] = args.name
    if getattr(args, "action", None):
        body["action"] = args.action
    if getattr(args, "priority", None) is not None:
        body["priority"] = args.priority
    data = api_request("PUT", f"/v1/inbound/rules/{args.id}", token, json=body)
    output_json(data)


def cmd_inbound_delete_rule(args):
    token = require_token()
    data = api_request("DELETE", f"/v1/inbound/rules/{args.id}", token)
    output_json(data)


def cmd_inbound_voicemails(args):
    token = require_token()
    data = api_request("GET", "/v1/inbound/voicemails", token)
    output_json(data)


def cmd_inbound_voicemail(args):
    token = require_token()
    data = api_request("GET", f"/v1/inbound/voicemails/{args.id}", token)
    output_json(data)


def cmd_inbound_voicemail_playback(args):
    token = require_token()
    data = api_request("GET", f"/v1/inbound/voicemails/{args.id}/playback", token)
    output_json(data)


def cmd_inbound_contacts(args):
    token = require_token()
    data = api_request("GET", "/v1/inbound/contacts", token)
    output_json(data)


def cmd_inbound_add_contact(args):
    token = require_token()
    body = {"name": args.name, "phone_number": args.phone}
    if getattr(args, "vip", False):
        body["is_vip"] = True
    if getattr(args, "notes", None):
        body["notes"] = args.notes
    data = api_request("POST", "/v1/inbound/contacts", token, json=body)
    output_json(data)


def cmd_inbound_update_contact(args):
    token = require_token()
    body = {}
    if getattr(args, "name", None):
        body["name"] = args.name
    if getattr(args, "phone", None):
        body["phone_number"] = args.phone
    if getattr(args, "vip", None) is not None:
        body["is_vip"] = args.vip
    data = api_request("PUT", f"/v1/inbound/contacts/{args.id}", token, json=body)
    output_json(data)


def cmd_inbound_delete_contact(args):
    token = require_token()
    data = api_request("DELETE", f"/v1/inbound/contacts/{args.id}", token)
    output_json(data)


def cmd_inbound_import_contacts(args):
    token = require_token()
    data = api_request("POST", "/v1/inbound/contacts/import", token, json={"source": args.source})
    output_json(data)


def cmd_inbound_events(args):
    token = require_token()
    params = {}
    if getattr(args, "date_from", None):
        params["from"] = args.date_from
    if getattr(args, "date_to", None):
        params["to"] = args.date_to
    data = api_request("GET", "/v1/inbound/events", token, params=params)
    output_json(data)


# =============================================================================
# Phone Number Management Commands
# =============================================================================

def cmd_phone_list(args):
    token = require_token()
    data = api_request("GET", "/v1/phone-numbers", token)
    if is_human(args):
        numbers = data.get("phone_numbers", [])
        output_human("Phone Numbers", [{"id": n.get("id", "")[:8], "number": n.get("phone_number", ""), "country": n.get("iso_country", "")} for n in numbers])
    else:
        output_json(data)


def cmd_phone_info(args):
    token = require_token()
    data = api_request("GET", f"/v1/phone-numbers/{args.id}/details", token)
    output_json(data)


def cmd_phone_countries(args):
    token = require_token()
    data = api_request("GET", "/v1/phone-numbers/supported-countries", token)
    output_json(data)


def cmd_phone_available(args):
    token = require_token()
    params = {"country": args.country}
    if getattr(args, "area_code", None):
        params["area_code"] = args.area_code
    data = api_request("GET", "/v1/phone-numbers/available", token, params=params)
    output_json(data)


def cmd_phone_provision(args):
    token = require_token()
    body = {"country": args.country}
    if getattr(args, "area_code", None):
        body["area_code"] = args.area_code
    data = api_request("POST", "/v1/phone-numbers/provision", token, json=body)
    output_json(data)


def cmd_phone_forwarding(args):
    token = require_token()
    data = api_request("PUT", f"/v1/phone-numbers/{args.id}/forwarding", token, json={"forwarding_number": args.target})
    output_json(data)


def cmd_phone_remove_forwarding(args):
    token = require_token()
    data = api_request("DELETE", f"/v1/phone-numbers/{args.id}/forwarding", token)
    output_json(data)


def cmd_phone_verify_start(args):
    token = require_token()
    data = api_request("POST", "/v1/phone-numbers/verify/start", token, json={"phone_number": args.number})
    output_json(data)


def cmd_phone_verify_check(args):
    token = require_token()
    data = api_request("POST", "/v1/phone-numbers/verify/check", token, json={"phone_number": args.number, "code": args.code})
    output_json(data)


def cmd_phone_caller_id(args):
    token = require_token()
    data = api_request("PUT", f"/v1/phone-numbers/{args.id}/caller-id", token, json={"caller_id_name": args.name})
    output_json(data)


def cmd_phone_release(args):
    token = require_token()
    data = api_request("DELETE", f"/v1/phone-numbers/{args.id}", token)
    output_json(data)


# =============================================================================
# Channels Commands
# =============================================================================

def cmd_channels_status(args):
    token = require_token()
    data = api_request("GET", "/v1/channels/status", token)
    output_json(data)


def cmd_channels_email_add(args):
    token = require_token()
    body = {"email_address": args.address}
    if getattr(args, "name", None):
        body["display_name"] = args.name
    if getattr(args, "primary", False):
        body["is_primary"] = True
    data = api_request("POST", "/v1/channels/email/add", token, json=body)
    output_json(data)


def cmd_channels_email_list(args):
    token = require_token()
    data = api_request("GET", "/v1/channels/email/list", token)
    output_json(data)


def cmd_channels_email_update(args):
    token = require_token()
    body = {}
    if getattr(args, "name", None):
        body["display_name"] = args.name
    if getattr(args, "primary", False):
        body["is_primary"] = True
    data = api_request("PUT", f"/v1/channels/email/{args.id}", token, json=body)
    output_json(data)


def cmd_channels_email_delete(args):
    token = require_token()
    api_request("DELETE", f"/v1/channels/email/{args.id}", token)
    output_json({"success": True})


def cmd_channels_mailbox(args):
    token = require_token()
    data = api_request("GET", "/v1/channels/mailbox", token)
    output_json(data)


def cmd_channels_connect(args):
    token = require_token()
    data = api_request("POST", f"/v1/channels/webhook/{args.channel}/connect", token, json={})
    output_json(data)


def cmd_channels_test(args):
    token = require_token()
    data = api_request("POST", f"/v1/channels/webhook/{args.channel}/test", token)
    output_json(data)


def cmd_channels_disconnect(args):
    token = require_token()
    data = api_request("POST", f"/v1/channels/disconnect/{args.channel}", token)
    output_json(data)


# =============================================================================
# Outreach Commands
# =============================================================================

def cmd_outreach_tasks(args):
    token = require_token()
    params = {}
    if getattr(args, "status", None):
        params["status"] = args.status
    data = api_request("GET", "/v1/outreach/tasks", token, params=params)
    output_json(data)


def cmd_outreach_task(args):
    token = require_token()
    data = api_request("GET", f"/v1/outreach/tasks/{args.id}", token)
    output_json(data)


def cmd_outreach_create(args):
    token = require_token()
    body = {"channel": args.channel, "target": args.target, "description": " ".join(args.description)}
    data = api_request("POST", "/v1/outreach/tasks", token, json=body)
    output_json(data)


def cmd_outreach_retry(args):
    token = require_token()
    data = api_request("POST", f"/v1/outreach/tasks/{args.id}/retry", token)
    output_json(data)


def cmd_outreach_cancel(args):
    token = require_token()
    data = api_request("POST", f"/v1/outreach/tasks/{args.id}/cancel", token)
    output_json(data)


# =============================================================================
# Subscription Commands
# =============================================================================

def cmd_subscription_status(args):
    token = require_token()
    data = api_request("GET", "/v1/subscriptions/status", token)
    if is_human(args):
        output_human("Subscription", fields={"Plan": data.get("plan_type", ""), "Status": data.get("status", ""), "Period End": data.get("current_period_end", "")})
    else:
        output_json(data)


def cmd_subscription_change(args):
    token = require_token()
    data = api_request("POST", "/v1/subscriptions/change-plan", token, json={"target_plan": args.plan})
    output_json(data)


def cmd_subscription_cancel_change(args):
    token = require_token()
    data = api_request("DELETE", "/v1/subscriptions/pending-change", token)
    output_json(data)


# =============================================================================
# Referrals Commands
# =============================================================================

def cmd_referrals_code(args):
    token = require_token()
    data = api_request("GET", "/v1/referrals/code", token)
    output_json(data)


def cmd_referrals_stats(args):
    token = require_token()
    data = api_request("GET", "/v1/referrals/stats", token)
    output_json(data)


def cmd_referrals_history(args):
    token = require_token()
    data = api_request("GET", "/v1/referrals/history", token)
    output_json(data)


# =============================================================================
# Notifications Commands
# =============================================================================

def cmd_notifications_pending(args):
    token = require_token()
    data = api_request("GET", "/v1/notifications/pending", token)
    output_json(data)


# =============================================================================
# Credits — Additional Commands
# =============================================================================

def cmd_credits_breakdown(args):
    token = require_token()
    data = api_request("GET", "/v1/credits/breakdown", token)
    output_json(data)


def cmd_credits_plans(args):
    token = require_token()
    data = api_request("GET", "/v1/credits/plans", token)
    output_json(data)


# =============================================================================
# Argparse — Subcommand Definitions
# =============================================================================

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kallyai.py",
        description="KallyAI Executive Assistant CLI — Manage calls, goals, email, bookings, and more.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--human", action="store_true", help="Human-friendly output instead of JSON")

    # Backward compatibility shim for old --phone --task flags
    parser.add_argument("--phone", "-p", dest="_compat_phone", help=argparse.SUPPRESS)
    parser.add_argument("--task", "-t", dest="_compat_task", help=argparse.SUPPRESS)
    parser.add_argument("--category", "-c", dest="_compat_category", default="general", help=argparse.SUPPRESS)
    parser.add_argument("--language", "-l", dest="_compat_language", default="es", help=argparse.SUPPRESS)
    parser.add_argument("--name", dest="_compat_name", help=argparse.SUPPRESS)
    parser.add_argument("--business", dest="_compat_business", help=argparse.SUPPRESS)
    parser.add_argument("--party-size", dest="_compat_party_size", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--date", dest="_compat_date", help=argparse.SUPPRESS)
    parser.add_argument("--time", dest="_compat_time", help=argparse.SUPPRESS)
    parser.add_argument("--usage", "--stats", dest="_compat_usage", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--subscription", "--sub", dest="_compat_subscription", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--history", "--list", dest="_compat_history", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--call-info", dest="_compat_call_info", metavar="ID", help=argparse.SUPPRESS)
    parser.add_argument("--transcript", dest="_compat_transcript", metavar="ID", help=argparse.SUPPRESS)

    sub = parser.add_subparsers(dest="domain", help="Command domain")

    # --- ask ---
    ask_p = sub.add_parser("ask", help="Send natural language request to KallyAI")
    ask_p.add_argument("message", nargs="+", help="What you want KallyAI to do")
    ask_p.set_defaults(func=cmd_ask)

    # --- coord ---
    coord_p = sub.add_parser("coord", help="Coordination & goal management")
    coord_sub = coord_p.add_subparsers(dest="coord_cmd")

    c = coord_sub.add_parser("message", help="Send message to coordination AI")
    c.add_argument("text", nargs="+")
    c.add_argument("--conversation-id", help="Conversation to continue")
    c.set_defaults(func=cmd_coord_message)

    c = coord_sub.add_parser("history", help="Get conversation history")
    c.add_argument("--conversation-id")
    c.add_argument("--limit", type=int)
    c.set_defaults(func=cmd_coord_history)

    c = coord_sub.add_parser("conversations", help="List conversations")
    c.set_defaults(func=cmd_coord_conversations)

    c = coord_sub.add_parser("new", help="Start new conversation")
    c.set_defaults(func=cmd_coord_new)

    c = coord_sub.add_parser("goals", help="List goals")
    c.add_argument("--status", choices=["active", "completed", "cancelled", "pending", "archived"])
    c.add_argument("--limit", type=int)
    c.set_defaults(func=cmd_coord_goals)

    c = coord_sub.add_parser("goal", help="Get goal details")
    c.add_argument("id")
    c.set_defaults(func=cmd_coord_goal)

    c = coord_sub.add_parser("goal-tree", help="Get goal + sub-goals tree")
    c.add_argument("id")
    c.set_defaults(func=cmd_coord_goal_tree)

    c = coord_sub.add_parser("cancel-goal", help="Cancel a goal")
    c.add_argument("id")
    c.set_defaults(func=cmd_coord_cancel_goal)

    c = coord_sub.add_parser("cascade-cancel", help="Cancel goal + all sub-goals")
    c.add_argument("id")
    c.set_defaults(func=cmd_coord_cascade_cancel)

    c = coord_sub.add_parser("escalate", help="Escalate goal for attention")
    c.add_argument("id")
    c.set_defaults(func=cmd_coord_escalate)

    c = coord_sub.add_parser("approve-step", help="Approve next step")
    c.add_argument("id")
    c.set_defaults(func=cmd_coord_approve_step)

    c = coord_sub.add_parser("accept", help="Accept goal outcome")
    c.add_argument("id")
    c.set_defaults(func=cmd_coord_accept)

    c = coord_sub.add_parser("continue", help="Continue negotiating")
    c.add_argument("id")
    c.set_defaults(func=cmd_coord_continue)

    c = coord_sub.add_parser("archive", help="Archive a goal")
    c.add_argument("id")
    c.set_defaults(func=cmd_coord_archive)

    c = coord_sub.add_parser("batch-archive", help="Archive multiple goals")
    c.add_argument("ids", nargs="+")
    c.set_defaults(func=cmd_coord_batch_archive)

    c = coord_sub.add_parser("budget", help="Get goal budget")
    c.add_argument("id")
    c.set_defaults(func=cmd_coord_budget)

    # --- calls ---
    calls_p = sub.add_parser("calls", help="Phone call management")
    calls_sub = calls_p.add_subparsers(dest="calls_cmd")

    c = calls_sub.add_parser("make", help="Make a phone call")
    c.add_argument("-p", "--phone", required=True, help="Phone number (E.164)")
    c.add_argument("-t", "--task", required=True, help="What to accomplish")
    c.add_argument("-c", "--category", default="general", choices=["restaurant", "clinic", "hotel", "general"])
    c.add_argument("-l", "--language", default="es", choices=["en", "es"])
    c.add_argument("--name", help="Your name")
    c.add_argument("--business", help="Business name")
    c.add_argument("--party-size", type=int, help="Party size")
    c.add_argument("--date", help="Date (YYYY-MM-DD)")
    c.add_argument("--time", help="Time (HH:MM)")
    c.add_argument("--timezone", default="Europe/Madrid")
    c.set_defaults(func=cmd_calls_make)

    c = calls_sub.add_parser("history", help="List recent calls")
    c.add_argument("--limit", type=int, default=10)
    c.set_defaults(func=cmd_calls_history)

    c = calls_sub.add_parser("info", help="Get call details")
    c.add_argument("id")
    c.set_defaults(func=cmd_calls_info)

    c = calls_sub.add_parser("transcript", help="Get call transcript")
    c.add_argument("id")
    c.set_defaults(func=cmd_calls_transcript)

    c = calls_sub.add_parser("recording", help="Get call recording")
    c.add_argument("id")
    c.set_defaults(func=cmd_calls_recording)

    c = calls_sub.add_parser("calendar", help="Get calendar event for call")
    c.add_argument("id")
    c.set_defaults(func=cmd_calls_calendar)

    c = calls_sub.add_parser("cancel", help="Cancel a call")
    c.add_argument("id")
    c.set_defaults(func=cmd_calls_cancel)

    c = calls_sub.add_parser("reschedule", help="Reschedule a call")
    c.add_argument("id")
    c.add_argument("--date", help="New date (YYYY-MM-DD)")
    c.add_argument("--time", help="New time (HH:MM)")
    c.set_defaults(func=cmd_calls_reschedule)

    c = calls_sub.add_parser("stop", help="Stop an active call")
    c.add_argument("id")
    c.set_defaults(func=cmd_calls_stop)

    # --- actions ---
    actions_p = sub.add_parser("actions", help="Autonomous actions (calendar, bookings, bills, tasks, email)")
    actions_sub = actions_p.add_subparsers(dest="actions_cmd")

    # actions calendar
    cal_p = actions_sub.add_parser("calendar", help="Calendar management")
    cal_sub = cal_p.add_subparsers(dest="cal_cmd")

    c = cal_sub.add_parser("create", help="Create calendar event")
    c.add_argument("--title", required=True)
    c.add_argument("--start", required=True, help="Start time (ISO 8601)")
    c.add_argument("--end", help="End time (ISO 8601)")
    c.add_argument("--location")
    c.add_argument("--description")
    c.set_defaults(func=cmd_actions_calendar_create)

    c = cal_sub.add_parser("slots", help="Get available slots")
    c.add_argument("--date", help="Date (YYYY-MM-DD)")
    c.add_argument("--duration", type=int, help="Duration in minutes")
    c.set_defaults(func=cmd_actions_calendar_slots)

    c = cal_sub.add_parser("sync", help="Sync calendar")
    c.set_defaults(func=cmd_actions_calendar_sync)

    c = cal_sub.add_parser("delete", help="Delete calendar event")
    c.add_argument("id")
    c.set_defaults(func=cmd_actions_calendar_delete)

    # actions restaurant
    rest_p = actions_sub.add_parser("restaurant", help="Restaurant search")
    rest_sub = rest_p.add_subparsers(dest="rest_cmd")

    c = rest_sub.add_parser("search", help="Search for restaurants")
    c.add_argument("query", nargs="+")
    c.add_argument("--location")
    c.add_argument("--party-size", type=int)
    c.add_argument("--date")
    c.add_argument("--time")
    c.set_defaults(func=cmd_actions_restaurant_search)

    # actions booking
    book_p = actions_sub.add_parser("booking", help="Booking management")
    book_sub = book_p.add_subparsers(dest="book_cmd")

    c = book_sub.add_parser("create", help="Create a booking")
    c.add_argument("--type", required=True, choices=["restaurant", "hotel", "service", "other"])
    c.add_argument("--restaurant-id")
    c.add_argument("--date")
    c.add_argument("--time")
    c.add_argument("--party-size", type=int)
    c.add_argument("--name")
    c.add_argument("--notes")
    c.set_defaults(func=cmd_actions_booking_create)

    c = book_sub.add_parser("cancel", help="Cancel a booking")
    c.add_argument("id")
    c.set_defaults(func=cmd_actions_booking_cancel)

    # actions bill
    bill_p = actions_sub.add_parser("bill", help="Bill analysis & disputes")
    bill_sub = bill_p.add_subparsers(dest="bill_cmd")

    c = bill_sub.add_parser("analyze", help="Analyze a bill")
    c.add_argument("description", nargs="+")
    c.add_argument("--amount", type=float)
    c.add_argument("--provider")
    c.set_defaults(func=cmd_actions_bill_analyze)

    c = bill_sub.add_parser("dispute", help="Dispute a bill")
    c.add_argument("description", nargs="+")
    c.add_argument("--amount", type=float)
    c.add_argument("--provider")
    c.add_argument("--reason")
    c.set_defaults(func=cmd_actions_bill_dispute)

    # actions ride/food/errand
    c = actions_sub.add_parser("ride", help="Request a ride")
    c.add_argument("--pickup", required=True)
    c.add_argument("--destination", required=True)
    c.add_argument("--time", help="Pickup time")
    c.set_defaults(func=cmd_actions_ride)

    c = actions_sub.add_parser("food", help="Order food delivery")
    c.add_argument("description", nargs="+")
    c.add_argument("--address")
    c.set_defaults(func=cmd_actions_food)

    c = actions_sub.add_parser("errand", help="Run an errand")
    c.add_argument("description", nargs="+")
    c.set_defaults(func=cmd_actions_errand)

    # actions email (via actions, not email domain)
    aemail_p = actions_sub.add_parser("email", help="Email actions (send, approve, cancel)")
    aemail_sub = aemail_p.add_subparsers(dest="aemail_cmd")

    c = aemail_sub.add_parser("send", help="Draft and queue email")
    c.add_argument("--to", required=True)
    c.add_argument("--subject", required=True)
    c.add_argument("body", nargs="+")
    c.add_argument("--cc")
    c.set_defaults(func=cmd_actions_email_send)

    c = aemail_sub.add_parser("approve", help="Approve queued email")
    c.add_argument("id")
    c.set_defaults(func=cmd_actions_email_approve)

    c = aemail_sub.add_parser("cancel", help="Cancel queued email")
    c.add_argument("id")
    c.set_defaults(func=cmd_actions_email_cancel)

    c = aemail_sub.add_parser("outbox", help="List outbox")
    c.set_defaults(func=cmd_actions_email_outbox)

    c = aemail_sub.add_parser("replies", help="Get email replies")
    c.add_argument("id")
    c.set_defaults(func=cmd_actions_email_replies)

    # actions log/undo
    c = actions_sub.add_parser("log", help="View action log")
    c.add_argument("--type", choices=["calendar", "booking", "bill", "ride", "food", "errand", "email"])
    c.add_argument("--limit", type=int)
    c.set_defaults(func=cmd_actions_log)

    c = actions_sub.add_parser("undo", help="Undo an action")
    c.add_argument("id")
    c.set_defaults(func=cmd_actions_undo)

    # --- messages ---
    msgs_p = sub.add_parser("messages", help="Unified inbox")
    msgs_sub = msgs_p.add_subparsers(dest="msgs_cmd")

    c = msgs_sub.add_parser("inbox", help="List inbox messages")
    c.add_argument("--channel", choices=["email", "sms", "call", "chat"])
    c.add_argument("--limit", type=int)
    c.add_argument("--unread", action="store_true")
    c.set_defaults(func=cmd_messages_inbox)

    c = msgs_sub.add_parser("read", help="Read a message")
    c.add_argument("id")
    c.set_defaults(func=cmd_messages_read)

    c = msgs_sub.add_parser("thread", help="Get conversation thread")
    c.add_argument("id", help="Conversation ID")
    c.set_defaults(func=cmd_messages_thread)

    c = msgs_sub.add_parser("mark-read", help="Mark messages as read")
    c.add_argument("ids", nargs="+")
    c.set_defaults(func=cmd_messages_mark_read)

    # --- search ---
    search_p = sub.add_parser("search", help="Research & search")
    search_sub = search_p.add_subparsers(dest="search_cmd")

    c = search_sub.add_parser("run", help="Search for information")
    c.add_argument("query", nargs="+")
    c.add_argument("--location")
    c.set_defaults(func=cmd_search)

    c = search_sub.add_parser("quick", help="Quick search")
    c.add_argument("query", nargs="+")
    c.set_defaults(func=cmd_search_quick)

    c = search_sub.add_parser("history", help="Search history")
    c.set_defaults(func=cmd_search_history)

    c = search_sub.add_parser("sources", help="Available search sources")
    c.set_defaults(func=cmd_search_sources)

    # --- email ---
    email_p = sub.add_parser("email", help="Email account management")
    email_sub = email_p.add_subparsers(dest="email_cmd")

    c = email_sub.add_parser("accounts", help="List connected accounts")
    c.set_defaults(func=cmd_email_accounts)

    c = email_sub.add_parser("connect", help="Connect email provider")
    c.add_argument("provider", choices=["gmail", "outlook"])
    c.set_defaults(func=lambda args: cmd_email_connect_gmail(args) if args.provider == "gmail" else cmd_email_connect_outlook(args))

    c = email_sub.add_parser("disconnect", help="Disconnect account")
    c.add_argument("id")
    c.set_defaults(func=cmd_email_disconnect)

    c = email_sub.add_parser("list", help="List email messages")
    c.add_argument("--classification", choices=["important", "actionable", "informational", "spam"])
    c.add_argument("--limit", type=int)
    c.set_defaults(func=cmd_email_list)

    c = email_sub.add_parser("read", help="Read an email")
    c.add_argument("id")
    c.set_defaults(func=cmd_email_read)

    c = email_sub.add_parser("respond", help="Respond to an email")
    c.add_argument("id")
    c.add_argument("instructions", nargs="*", help="Instructions for response")
    c.set_defaults(func=cmd_email_respond)

    c = email_sub.add_parser("voice-profile", help="Get writing voice profile")
    c.set_defaults(func=cmd_email_voice_profile)

    c = email_sub.add_parser("train-voice", help="Train voice profile")
    c.set_defaults(func=cmd_email_train_voice)

    # --- budget ---
    budget_p = sub.add_parser("budget", help="Cost management")
    budget_sub = budget_p.add_subparsers(dest="budget_cmd")

    c = budget_sub.add_parser("estimate", help="Estimate task cost")
    c.add_argument("--type", required=True, choices=["call", "email", "search", "booking", "ride", "food", "errand"])
    c.add_argument("description", nargs="+")
    c.set_defaults(func=cmd_budget_estimate)

    c = budget_sub.add_parser("approve", help="Approve goal budget")
    c.add_argument("goal_id")
    c.set_defaults(func=cmd_budget_approve)

    c = budget_sub.add_parser("breakdown", help="Get cost breakdown")
    c.add_argument("goal_id")
    c.set_defaults(func=cmd_budget_breakdown)

    c = budget_sub.add_parser("ack-cap", help="Acknowledge soft cap")
    c.add_argument("goal_id")
    c.set_defaults(func=cmd_budget_ack_cap)

    # --- credits ---
    credits_p = sub.add_parser("credits", help="Credits balance & history")
    credits_sub = credits_p.add_subparsers(dest="credits_cmd")

    c = credits_sub.add_parser("balance", help="Check credits balance")
    c.set_defaults(func=cmd_credits_balance)

    c = credits_sub.add_parser("history", help="Credits usage history")
    c.add_argument("--limit", type=int)
    c.set_defaults(func=cmd_credits_history)

    c = credits_sub.add_parser("costs", help="Credit cost reference")
    c.set_defaults(func=cmd_credits_costs)

    c = credits_sub.add_parser("breakdown", help="Spending breakdown by action type")
    c.set_defaults(func=cmd_credits_breakdown)

    c = credits_sub.add_parser("plans", help="Available credit plans")
    c.set_defaults(func=cmd_credits_plans)

    # --- inbound (AI receptionist) ---
    inbound_p = sub.add_parser("inbound", help="AI receptionist — incoming call management")
    inbound_sub = inbound_p.add_subparsers(dest="inbound_cmd")

    c = inbound_sub.add_parser("calls", help="List incoming calls")
    c.add_argument("--status", choices=["active", "completed", "missed", "rejected"])
    c.add_argument("--vip-only", action="store_true")
    c.add_argument("--from", dest="date_from", help="Start date")
    c.add_argument("--to", dest="date_to", help="End date")
    c.add_argument("--limit", type=int, default=20)
    c.set_defaults(func=cmd_inbound_calls)

    c = inbound_sub.add_parser("call", help="Get inbound call details")
    c.add_argument("id")
    c.set_defaults(func=cmd_inbound_call)

    c = inbound_sub.add_parser("transcript", help="Get inbound call transcript")
    c.add_argument("id")
    c.set_defaults(func=cmd_inbound_transcript)

    c = inbound_sub.add_parser("recording", help="Get inbound call recording")
    c.add_argument("id")
    c.set_defaults(func=cmd_inbound_recording)

    c = inbound_sub.add_parser("summary", help="Incoming call summary stats")
    c.set_defaults(func=cmd_inbound_summary)

    c = inbound_sub.add_parser("analytics", help="Inbound call analytics")
    c.add_argument("--from", dest="date_from")
    c.add_argument("--to", dest="date_to")
    c.set_defaults(func=cmd_inbound_analytics)

    c = inbound_sub.add_parser("transfer", help="Transfer live call")
    c.add_argument("id")
    c.add_argument("--to", required=True, dest="to", help="Target phone number")
    c.set_defaults(func=cmd_inbound_transfer)

    c = inbound_sub.add_parser("takeover", help="Take over live call")
    c.add_argument("id")
    c.set_defaults(func=cmd_inbound_takeover)

    c = inbound_sub.add_parser("reject", help="Reject incoming call")
    c.add_argument("id")
    c.add_argument("--reason")
    c.set_defaults(func=cmd_inbound_reject)

    c = inbound_sub.add_parser("rules", help="List routing rules")
    c.set_defaults(func=cmd_inbound_rules)

    c = inbound_sub.add_parser("add-rule", help="Create routing rule")
    c.add_argument("--name", required=True)
    c.add_argument("--action", required=True)
    c.add_argument("--priority", type=int, default=100)
    c.add_argument("--conditions", help="JSON conditions")
    c.set_defaults(func=cmd_inbound_add_rule)

    c = inbound_sub.add_parser("update-rule", help="Update routing rule")
    c.add_argument("id")
    c.add_argument("--name")
    c.add_argument("--action")
    c.add_argument("--priority", type=int)
    c.set_defaults(func=cmd_inbound_update_rule)

    c = inbound_sub.add_parser("delete-rule", help="Delete routing rule")
    c.add_argument("id")
    c.set_defaults(func=cmd_inbound_delete_rule)

    c = inbound_sub.add_parser("voicemails", help="List voicemails")
    c.set_defaults(func=cmd_inbound_voicemails)

    c = inbound_sub.add_parser("voicemail", help="Get voicemail details")
    c.add_argument("id")
    c.set_defaults(func=cmd_inbound_voicemail)

    c = inbound_sub.add_parser("voicemail-playback", help="Get voicemail audio")
    c.add_argument("id")
    c.set_defaults(func=cmd_inbound_voicemail_playback)

    c = inbound_sub.add_parser("contacts", help="List contacts")
    c.set_defaults(func=cmd_inbound_contacts)

    c = inbound_sub.add_parser("add-contact", help="Add contact")
    c.add_argument("--name", required=True)
    c.add_argument("--phone", required=True)
    c.add_argument("--vip", action="store_true")
    c.add_argument("--notes")
    c.set_defaults(func=cmd_inbound_add_contact)

    c = inbound_sub.add_parser("update-contact", help="Update contact")
    c.add_argument("id")
    c.add_argument("--name")
    c.add_argument("--phone")
    c.add_argument("--vip", type=bool)
    c.set_defaults(func=cmd_inbound_update_contact)

    c = inbound_sub.add_parser("delete-contact", help="Delete contact")
    c.add_argument("id")
    c.set_defaults(func=cmd_inbound_delete_contact)

    c = inbound_sub.add_parser("import-contacts", help="Import contacts")
    c.add_argument("source", help="Import source (e.g., google, csv)")
    c.set_defaults(func=cmd_inbound_import_contacts)

    c = inbound_sub.add_parser("events", help="Inbound event log")
    c.add_argument("--from", dest="date_from")
    c.add_argument("--to", dest="date_to")
    c.set_defaults(func=cmd_inbound_events)

    # --- phone (number management) ---
    phone_p = sub.add_parser("phone", help="Phone number management")
    phone_sub = phone_p.add_subparsers(dest="phone_cmd")

    c = phone_sub.add_parser("list", help="List your phone numbers")
    c.set_defaults(func=cmd_phone_list)

    c = phone_sub.add_parser("info", help="Phone number details")
    c.add_argument("id")
    c.set_defaults(func=cmd_phone_info)

    c = phone_sub.add_parser("countries", help="Supported countries")
    c.set_defaults(func=cmd_phone_countries)

    c = phone_sub.add_parser("available", help="Search available numbers")
    c.add_argument("--country", required=True)
    c.add_argument("--area-code")
    c.set_defaults(func=cmd_phone_available)

    c = phone_sub.add_parser("provision", help="Provision new number")
    c.add_argument("--country", required=True)
    c.add_argument("--area-code")
    c.set_defaults(func=cmd_phone_provision)

    c = phone_sub.add_parser("forwarding", help="Set call forwarding")
    c.add_argument("id")
    c.add_argument("--target", required=True, help="Forwarding target number")
    c.set_defaults(func=cmd_phone_forwarding)

    c = phone_sub.add_parser("remove-forwarding", help="Remove call forwarding")
    c.add_argument("id")
    c.set_defaults(func=cmd_phone_remove_forwarding)

    c = phone_sub.add_parser("verify-start", help="Start phone verification")
    c.add_argument("number")
    c.set_defaults(func=cmd_phone_verify_start)

    c = phone_sub.add_parser("verify-check", help="Check verification code")
    c.add_argument("number")
    c.add_argument("--code", required=True)
    c.set_defaults(func=cmd_phone_verify_check)

    c = phone_sub.add_parser("caller-id", help="Set caller ID name")
    c.add_argument("id")
    c.add_argument("--name", required=True)
    c.set_defaults(func=cmd_phone_caller_id)

    c = phone_sub.add_parser("release", help="Release phone number")
    c.add_argument("id")
    c.set_defaults(func=cmd_phone_release)

    # --- channels ---
    chan_p = sub.add_parser("channels", help="Multi-channel management")
    chan_sub = chan_p.add_subparsers(dest="chan_cmd")

    c = chan_sub.add_parser("status", help="All channel statuses")
    c.set_defaults(func=cmd_channels_status)

    c = chan_sub.add_parser("email-add", help="Add email contact")
    c.add_argument("address")
    c.add_argument("--name")
    c.add_argument("--primary", action="store_true")
    c.set_defaults(func=cmd_channels_email_add)

    c = chan_sub.add_parser("email-list", help="List email contacts")
    c.set_defaults(func=cmd_channels_email_list)

    c = chan_sub.add_parser("email-update", help="Update email contact")
    c.add_argument("id")
    c.add_argument("--name")
    c.add_argument("--primary", action="store_true")
    c.set_defaults(func=cmd_channels_email_update)

    c = chan_sub.add_parser("email-delete", help="Delete email contact")
    c.add_argument("id")
    c.set_defaults(func=cmd_channels_email_delete)

    c = chan_sub.add_parser("mailbox", help="Get KallyAI mailbox address")
    c.set_defaults(func=cmd_channels_mailbox)

    c = chan_sub.add_parser("connect", help="Connect messaging channel")
    c.add_argument("channel", choices=["whatsapp", "telegram"])
    c.set_defaults(func=cmd_channels_connect)

    c = chan_sub.add_parser("test", help="Test channel connection")
    c.add_argument("channel", choices=["whatsapp", "telegram"])
    c.set_defaults(func=cmd_channels_test)

    c = chan_sub.add_parser("disconnect", help="Disconnect channel")
    c.add_argument("channel", choices=["whatsapp", "telegram", "email"])
    c.set_defaults(func=cmd_channels_disconnect)

    # --- outreach ---
    outreach_p = sub.add_parser("outreach", help="Multi-channel outreach")
    outreach_sub = outreach_p.add_subparsers(dest="outreach_cmd")

    c = outreach_sub.add_parser("tasks", help="List outreach tasks")
    c.add_argument("--status")
    c.set_defaults(func=cmd_outreach_tasks)

    c = outreach_sub.add_parser("task", help="Get outreach task details")
    c.add_argument("id")
    c.set_defaults(func=cmd_outreach_task)

    c = outreach_sub.add_parser("create", help="Create outreach task")
    c.add_argument("--channel", required=True, choices=["call", "email", "whatsapp", "telegram"])
    c.add_argument("--target", required=True, help="Phone number or email")
    c.add_argument("description", nargs="+")
    c.set_defaults(func=cmd_outreach_create)

    c = outreach_sub.add_parser("retry", help="Retry failed outreach")
    c.add_argument("id")
    c.set_defaults(func=cmd_outreach_retry)

    c = outreach_sub.add_parser("cancel", help="Cancel outreach task")
    c.add_argument("id")
    c.set_defaults(func=cmd_outreach_cancel)

    # --- subscription ---
    subs_p = sub.add_parser("subscription", help="Plan management")
    subs_sub = subs_p.add_subparsers(dest="subs_cmd")

    c = subs_sub.add_parser("status", help="Current plan status")
    c.set_defaults(func=cmd_subscription_status)

    c = subs_sub.add_parser("change-plan", help="Change subscription plan")
    c.add_argument("plan", choices=["starter", "pro", "power", "business"])
    c.set_defaults(func=cmd_subscription_change)

    c = subs_sub.add_parser("cancel-change", help="Cancel pending plan change")
    c.set_defaults(func=cmd_subscription_cancel_change)

    # --- referrals ---
    ref_p = sub.add_parser("referrals", help="Referral program")
    ref_sub = ref_p.add_subparsers(dest="ref_cmd")

    c = ref_sub.add_parser("code", help="Get your referral code")
    c.set_defaults(func=cmd_referrals_code)

    c = ref_sub.add_parser("stats", help="Referral statistics")
    c.set_defaults(func=cmd_referrals_stats)

    c = ref_sub.add_parser("history", help="Referral history")
    c.set_defaults(func=cmd_referrals_history)

    # --- notifications ---
    notif_p = sub.add_parser("notifications", help="Notifications")
    notif_sub = notif_p.add_subparsers(dest="notif_cmd")

    c = notif_sub.add_parser("pending", help="Pending notification counts")
    c.set_defaults(func=cmd_notifications_pending)

    # --- login/logout/auth-status/billing ---
    c = sub.add_parser("login", help="Force re-authentication")
    c.set_defaults(func=cmd_login)

    c = sub.add_parser("logout", help="Clear credentials")
    c.set_defaults(func=cmd_logout)

    c = sub.add_parser("auth-status", help="Check login status")
    c.set_defaults(func=cmd_auth_status)

    c = sub.add_parser("billing", help="Open Stripe billing portal")
    c.set_defaults(func=cmd_billing)

    return parser


# =============================================================================
# Backward Compatibility Shim
# =============================================================================

def handle_compat(args):
    """Map old --phone --task flags to new subcommand style."""
    if getattr(args, "_compat_phone", None) and getattr(args, "_compat_task", None):
        args.phone = args._compat_phone
        args.task = args._compat_task
        args.category = args._compat_category
        args.language = args._compat_language
        args.name = args._compat_name
        args.business = args._compat_business
        args.party_size = args._compat_party_size
        args.date = args._compat_date
        args.time = args._compat_time
        args.timezone = "Europe/Madrid"
        cmd_calls_make(args)
        return True

    if getattr(args, "_compat_usage", False):
        token = require_token()
        data = api_request("GET", "/v1/credits/balance", token)
        output_json(data)
        return True

    if getattr(args, "_compat_subscription", False):
        token = require_token()
        data = api_request("GET", "/v1/users/me/subscription", token)
        output_json(data)
        return True

    if getattr(args, "_compat_history", False):
        args.limit = 10
        cmd_calls_history(args)
        return True

    if getattr(args, "_compat_call_info", None):
        args.id = args._compat_call_info
        cmd_calls_info(args)
        return True

    if getattr(args, "_compat_transcript", None):
        args.id = args._compat_transcript
        cmd_calls_transcript(args)
        return True

    return False


# =============================================================================
# Main
# =============================================================================

def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        # Try compat shim first
        if handle_compat(args):
            return

        # Dispatch to subcommand
        if hasattr(args, "func"):
            args.func(args)
        else:
            parser.print_help()
            sys.exit(0)

    except SystemExit:
        raise
    except Exception as e:
        output_error("unexpected_error", str(e))


if __name__ == "__main__":
    main()
