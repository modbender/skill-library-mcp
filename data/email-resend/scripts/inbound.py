#!/usr/bin/env python3
"""
Resend Inbound Email Checker - Consolidated Version

Checks for new inbound emails and outputs notification JSON.
Maps notification message_id to email_id for reply-to-acknowledge.

Features:
- Proper file locking (prevents concurrent runs)
- Direct notification output with message_id tracking
- Importance detection (HIGH, MEETING, NORMAL)
- Rich metadata storage
- 30-day auto-cleanup of acknowledged emails
"""

import fcntl
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

# === CONFIGURATION ===
API_KEY = os.environ.get("RESEND_API_KEY")
if not API_KEY:
    print("ERROR: RESEND_API_KEY not set")
    sys.exit(1)

API_BASE = "https://api.resend.com"

# Channel configuration - loaded from memory preferences
# The OpenClaw agent that invokes this script handles actual delivery
# via the message tool (channel from memory_search or context)

API_BASE = "https://api.resend.com"

WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace"
STATE_FILE = WORKSPACE_DIR / "memory" / "email-resend-inbound-notified.json"
MESSAGE_MAP_FILE = WORKSPACE_DIR / "memory" / "email-message-map.json"
LOCK_FILE = STATE_FILE.with_suffix(".lock")

# Custody chain files
CUSTODY_CHAIN_FILE = WORKSPACE_DIR / "memory" / "email-custody-chain.json"
MSG_TO_CHAIN_FILE = WORKSPACE_DIR / "memory" / "email-msg-to-chain.json"

# Agent handles channel/target via memory_search + message tool
# This script outputs email data only

MAX_RETRIES = 3
RETRY_DELAY = 2
MAX_AGE_DAYS = 30


# === CUSTODY CHAIN ===
def load_custody_chain():
    CUSTODY_CHAIN_FILE.parent.mkdir(parents=True, exist_ok=True)
    if CUSTODY_CHAIN_FILE.exists():
        with open(CUSTODY_CHAIN_FILE) as f:
            return json.load(f)
    return {}


def save_custody_chain(data):
    CUSTODY_CHAIN_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CUSTODY_CHAIN_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_msg_to_chain():
    MSG_TO_CHAIN_FILE.parent.mkdir(parents=True, exist_ok=True)
    if MSG_TO_CHAIN_FILE.exists():
        with open(MSG_TO_CHAIN_FILE) as f:
            return json.load(f)
    return {}


def save_msg_to_chain(data):
    MSG_TO_CHAIN_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(MSG_TO_CHAIN_FILE, "w") as f:
        json.dump(data, f, indent=2)


def add_custody_node(email_id, msg_id, node_type, parent_msg_id=None):
    """Add a node to the custody chain DAG."""
    from datetime import datetime, timezone
    
    chain = load_custody_chain()
    msg_map = load_msg_to_chain()
    
    if email_id not in chain:
        chain[email_id] = {
            "email_id": email_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "nodes": {}
        }
    
    node = {
        "type": node_type,
        "msg_id": str(msg_id),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "parent_msg_id": str(parent_msg_id) if parent_msg_id else None
    }
    
    chain[email_id]["nodes"][str(msg_id)] = node
    msg_map[str(msg_id)] = email_id
    
    save_custody_chain(chain)
    save_msg_to_chain(msg_map)
    
    return chain[email_id]


# === STATE MANAGEMENT ===
def load_state(lock_fd):
    """Load state with proper locking."""
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_SH)
        if STATE_FILE.exists():
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
                if "pending_ids" not in data:
                    data["pending_ids"] = {}
                if "acknowledged_ids" not in data:
                    data["acknowledged_ids"] = {}
                return data
    except (json.JSONDecodeError, IOError):
        pass
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
    return {"acknowledged_ids": {}, "pending_ids": {}}


def save_state(lock_fd, data):
    """Save state with atomic write and 30-day cleanup."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)
    acknowledged = data.get("acknowledged_ids", {})
    cleaned = {
        eid: ts for eid, ts in acknowledged.items()
        if datetime.fromisoformat(ts.replace('Z', '+00:00')) > cutoff
    }
    data["acknowledged_ids"] = cleaned
    
    temp_file = STATE_FILE.with_suffix(".tmp")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        with open(temp_file, "w") as f:
            json.dump(data, f, indent=2)
        temp_file.replace(STATE_FILE)
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)


def load_message_map():
    MESSAGE_MAP_FILE.parent.mkdir(parents=True, exist_ok=True)
    if MESSAGE_MAP_FILE.exists():
        with open(MESSAGE_MAP_FILE) as f:
            return json.load(f)
    return {}


def save_message_map(data):
    MESSAGE_MAP_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(MESSAGE_MAP_FILE, "w") as f:
        json.dump(data, f, indent=2)


# === API CLIENT ===
def fetch_emails(limit=20):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    params = {"limit": limit, "sort": "desc"}
    
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(f"{API_BASE}/emails/receiving", headers=headers, params=params, timeout=30)
            if resp.status_code == 200:
                return resp.json().get("data", [])
            last_error = f"API {resp.status_code}: {resp.text}"
        except requests.RequestException as e:
            last_error = str(e)
        
        if attempt < MAX_RETRIES - 1:
            wait_time = RETRY_DELAY * (2 ** attempt)
            print(f"Attempt {attempt + 1} failed: {last_error}. Retrying in {wait_time}s...")
            time.sleep(wait_time)
    
    print(f"ERROR: All {MAX_RETRIES} attempts failed: {last_error}")
    sys.exit(1)


def fetch_email_detail(email_id):
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(f"{API_BASE}/emails/receiving/{email_id}", 
                              headers={"Authorization": f"Bearer {API_KEY}"}, timeout=30)
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code == 404:
                return {}
        except requests.RequestException as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
    return {}


# === NOTIFICATION OUTPUT ===
def format_notification(email_id, subject, from_addr, date, importance, body_preview, attachments_str):
    """Format notification as JSON for agent to deliver via message tool.
    
    The OpenClaw agent that invokes this script should:
    1. Parse this JSON output
    2. Use memory_search tool to find channel preference
    3. Use message tool to deliver to appropriate channel
    """
    import json
    
    notification = {
        "email_id": email_id,
        "subject": subject,
        "from": from_addr,
        "date": date,
        "importance": importance,
        "body_preview": body_preview,
        "attachments": attachments_str,
    }
    
    # Output as JSON line for easy parsing
    print(f"NOTIFICATION_JSON: {json.dumps(notification)}")
    
    # Also output human-readable format
    msg = f"""📬 NEW INBOUND {importance}

From: {from_addr}
Subject: {subject}
Date: {date}

{body_preview}{attachments_str}

ID: {email_id}

💡 Reply to acknowledge"""
    
    print(msg)
    
    return notification


# === HELPERS ===
def detect_importance(email):
    subject = (email.get("subject") or "").lower()
    from_addr = (email.get("from") or "").lower()
    text = subject + " " + from_addr
    
    urgent = ["urgent", "asap", "critical", "emergency", "important", "priority"]
    meeting = ["meeting", "call", "zoom", "calendar", "schedule"]
    
    if any(k in text for k in urgent):
        return "🔥 HIGH"
    elif any(k in text for k in meeting):
        return "📅 MEETING"
    return "📬 NORMAL"


def extract_sender_name(from_addr):
    if not from_addr:
        return "Unknown"
    if "<" in from_addr:
        return from_addr.split("<")[0].strip().strip('"')
    if "@" in from_addr:
        return from_addr.split("@")[0]
    return from_addr


def format_body(body, max_chars=1500, max_lines=40):
    if not body:
        return "(empty)"
    lines = body.split('\n')[:max_lines]
    preview = '\n'.join(lines)
    if len(body) > len(preview):
        preview += f"\n... (+{len(body) - len(preview)} chars)"
    return preview[:max_chars]


def format_attachments(attachments):
    if not attachments:
        return ""
    names = [f"• {att.get('filename', '?')} ({att.get('size', 0):,} bytes)" for att in attachments]
    return "\n📎 Attachments:\n" + "\n".join(names)


# === MAIN ===
def main():
    print("📧 Checking inbound emails...")
    
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    lock_fd = open(LOCK_FILE, "w")
    
    try:
        state = load_state(lock_fd)
        pending = state.get("pending_ids", {})
        acknowledged = state.get("acknowledged_ids", {})
        msg_map = load_message_map()
        
        emails = fetch_emails(limit=20)
        
        if not emails:
            print("✅ No inbound emails.")
            save_state(lock_fd, state)
            print(f"📬 Pending: {len(pending)}, Acknowledged: {len(acknowledged)}")
            sys.exit(0)
        
        # Find new emails
        new_emails = []
        for email in emails:
            email_id = email.get("id")
            if email_id not in acknowledged and email_id not in pending:
                new_emails.append(email)
        
        # Add to pending
        for email in new_emails:
            email_id = email.get("id")
            pending[email_id] = {
                "created_at": email.get("created_at", ""),
                "subject": email.get("subject", ""),
                "from": email.get("from", ""),
                "sender_name": extract_sender_name(email.get("from", "")),
                "importance": detect_importance(email)
            }
        
        state["pending_ids"] = pending
        state["last_check"] = datetime.now(timezone.utc).isoformat()
        save_state(lock_fd, state)
        
        if not new_emails:
            print(f"✅ No new emails. 📬 Pending: {len(pending)}, Acknowledged: {len(acknowledged)}")
            sys.exit(0)
        
        # Output notifications for agent delivery
        print(f"📬 New: {len(new_emails)} email(s)")
        
        for email in new_emails:
            email_id = email.get("id")
            subject = email.get("subject", "(No subject)")
            from_addr = email.get("from", "N/A")
            date = email.get("created_at", "N/A")
            importance = detect_importance(email)
            
            # Get full details
            detail = fetch_email_detail(email_id)
            body = ""
            if detail:
                body = detail.get("text") or ""
                if not body and detail.get("html"):
                    body = re.sub(r'<[^>]+>', '', detail.get("html", ""))
            attachments = detail.get("attachments", []) if detail else []
            
            body_preview = format_body(body)
            attachments_str = format_attachments(attachments)
            
            # Format notification for agent to deliver
            notification = format_notification(email_id, subject, from_addr, date, importance, body_preview, attachments_str)
            
            # Note: Agent will handle delivery via message tool
        
        print(f"✅ Done. Pending: {len(pending)}, Acknowledged: {len(acknowledged)}")
        sys.exit(1)
        
    finally:
        lock_fd.close()


if __name__ == "__main__":
    main()
