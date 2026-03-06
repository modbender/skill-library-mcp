#!/usr/bin/env python3
"""
Email Draft Reply Workflow
1. User triggers draft → fetch original email
2. Show original + prompt for reply
3. User provides reply content
4. Show preview with Approve/Decline
5. User approves → send via Resend
"""

import os
import sys
import json
from pathlib import Path
import requests

# Import shared preferences
sys.path.insert(0, str(Path(__file__).parent))
from preferences import get_from_email, get_from_name

API_KEY = os.environ.get("RESEND_API_KEY")
if not API_KEY:
    print("ERROR: RESEND_API_KEY not set")
    print("Run: export RESEND_API_KEY=re_...")
    sys.exit(1)

API_BASE = "https://api.resend.com"

WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace"
STATE_FILE = WORKSPACE_DIR / "memory" / "email-resend-inbound-notified.json"
DRAFT_STATE_FILE = WORKSPACE_DIR / "memory" / "email-draft-state.json"

# Sender info - prefers env var, falls back to preferences file
DEFAULT_FROM_EMAIL = get_from_email()
DEFAULT_FROM_NAME = get_from_name()

# Channel preferences loaded by agent from memory

def load_state():
    """Load the notification state (pending/acknowledged emails)."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"acknowledged_ids": {}, "pending_ids": {}}

def save_state(data):
    """Save the notification state."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def acknowledge_email(email_id):
    """Mark an email as acknowledged."""
    state = load_state()
    pending = state.get("pending_ids", {})
    acknowledged = state.get("acknowledged_ids", {})
    
    if email_id in pending:
        del pending[email_id]
    if email_id not in acknowledged:
        from datetime import datetime
        acknowledged[email_id] = datetime.utcnow().isoformat() + "Z"
    
    state["pending_ids"] = pending
    state["acknowledged_ids"] = acknowledged
    save_state(state)
    return True

def get_default_account():
    """Get default sender from environment variables."""
    if DEFAULT_FROM_EMAIL:
        return {
            "email": DEFAULT_FROM_EMAIL,
            "display_name": DEFAULT_FROM_NAME or "User"
        }
    print("ERROR: DEFAULT_FROM_EMAIL not set")
    print("Run: export DEFAULT_FROM_EMAIL=you@example.com DEFAULT_FROM_NAME='Your Name'")
    sys.exit(1)

def load_draft_state():
    if DRAFT_STATE_FILE.exists():
        with open(DRAFT_STATE_FILE) as f:
            return json.load(f)
    return {}

def save_draft_state(data):
    DRAFT_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DRAFT_STATE_FILE, "w") as f:
        json.dump(data, f, indent=2)


# === CUSTODY CHAIN ===
CUSTODY_CHAIN_FILE = WORKSPACE_DIR / "memory" / "email-custody-chain.json"
MSG_TO_CHAIN_FILE = WORKSPACE_DIR / "memory" / "email-msg-to-chain.json"


def load_custody_chain():
    """Load the full custody chain."""
    CUSTODY_CHAIN_FILE.parent.mkdir(parents=True, exist_ok=True)
    if CUSTODY_CHAIN_FILE.exists():
        with open(CUSTODY_CHAIN_FILE) as f:
            return json.load(f)
    return {}


def save_custody_chain(data):
    """Save custody chain."""
    CUSTODY_CHAIN_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CUSTODY_CHAIN_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_msg_to_chain():
    """Load notification message ID -> chain key mapping."""
    MSG_TO_CHAIN_FILE.parent.mkdir(parents=True, exist_ok=True)
    if MSG_TO_CHAIN_FILE.exists():
        with open(MSG_TO_CHAIN_FILE) as f:
            return json.load(f)
    return {}


def save_msg_to_chain(data):
    """Save message to chain mapping."""
    MSG_TO_CHAIN_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(MSG_TO_CHAIN_FILE, "w") as f:
        json.dump(data, f, indent=2)


def add_custody_node(email_id, msg_id, node_type, parent_msg_id=None, content=None):
    """
    Add a node to the custody chain DAG.
    
    Args:
        email_id: Resend email ID (root)
        msg_id: notification message ID for this node
        node_type: notification|reply|preview|confirm|sent
        parent_msg_id: Parent notification message ID (for traversal)
        content: Optional content for reply nodes
    """
    from datetime import datetime, timezone
    
    chain = load_custody_chain()
    msg_map = load_msg_to_chain()
    
    # Initialize chain for this email if needed
    if email_id not in chain:
        chain[email_id] = {
            "email_id": email_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "nodes": {}
        }
    
    # Add node
    node = {
        "type": node_type,
        "msg_id": str(msg_id),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "parent_msg_id": str(parent_msg_id) if parent_msg_id else None
    }
    if content:
        node["content"] = content
    
    chain[email_id]["nodes"][str(msg_id)] = node
    
    # Map notification msg_id to chain
    msg_map[str(msg_id)] = email_id
    
    save_custody_chain(chain)
    save_msg_to_chain(msg_map)
    
    return chain[email_id]


def get_email_from_msg(msg_id):
    """Given a notification message ID, trace back to original email ID."""
    msg_map = load_msg_to_chain()
    email_id = msg_map.get(str(msg_id))
    
    if not email_id:
        return None
    
    chain = load_custody_chain()
    return chain.get(email_id)


def get_chain_for_email(email_id):
    """Get full custody chain for an email."""
    chain = load_custody_chain()
    return chain.get(email_id)


def get_latest_node(email_id):
    """Get the most recent node in the chain."""
    chain_data = get_chain_for_email(email_id)
    if not chain_data:
        return None
    
    nodes = chain_data.get("nodes", {})
    if not nodes:
        return None
    
    # Return node with latest timestamp
    return max(nodes.values(), key=lambda n: n.get("timestamp", ""))


def fetch_email(email_id):
    """Fetch full email details from Resend."""
    resp = requests.get(
        f"{API_BASE}/emails/receiving/{email_id}",
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()

def start_draft(email_id):
    """Start a draft reply for the given email."""
    email = fetch_email(email_id)
    if not email:
        return f"❌ Email {email_id} not found"
    
    # Extract sender from "From" header or email field
    from_addr = email.get("from") or email.get("headers", {}).get("From", "unknown")
    subject = email.get("subject", "No subject")
    
    # CRITICAL: Use the actual Message-ID from email headers for threading, NOT Resend ID
    # This is what Gmail/email clients need to thread correctly
    message_id = email.get("message_id", "") or email.get("id", "")
    
    # Build the reply - preserve Re: if already present
    account = get_default_account()
    reply_to = from_addr
    
    # Don't double "Re:" - strip if already present
    if subject.lower().startswith("re:"):
        reply_subject = subject
    else:
        reply_subject = f"Re: {subject}"
    
    # Create draft state
    created_at = email.get("created_at", "earlier")
    draft = {
        "email_id": email_id,
        "from": account["email"],
        "to": reply_to,
        "subject": reply_subject,
        "in_reply_to": message_id,
        "original_subject": subject,
        "original_from": from_addr,
        "created_at": created_at,
        "reply_content": None,
        "status": "waiting_for_reply"  # waiting_for_reply, pending_approval
    }
    
    save_draft_state(draft)
    
    # Show original email + prompt
    body = email.get("body", "No body")
    if len(body) > 1000:
        body = body[:1000] + "..."
    
    return f"""📝 DRAFT REPLY

Original:
From: {from_addr}
Subject: {subject}
---
{body}
---

Reply to this message with your reply content.
I'll show a preview before sending."""

def set_reply_content(content):
    """User provided reply content."""
    draft = load_draft_state()
    if not draft:
        return "❌ No draft in progress. Type 'draft <email_id>' to start."
    
    if draft.get("status") != "waiting_for_reply":
        return "❌ Draft already submitted. Wait for approval or start new draft."
    
    draft["reply_content"] = content
    draft["status"] = "pending_approval"
    save_draft_state(draft)
    
    # Show preview - text only (no buttons)
    return f"""📤 DRAFT PREVIEW

To: {draft['to']}
Subject: {draft['subject']}
---
{draft['reply_content']}
---

Reply: send | edit | cancel"""
    
    resp = requests.post(url, json=data)
    if resp.status_code != 200:
        # Fallback to text-only
        return preview_msg
    
    return None  # Message sent with buttons

def send_draft():
    """Send the draft email."""
    draft = load_draft_state()
    if not draft:
        return "❌ No draft to send. Start with 'draft <email_id>'"
    
    if draft.get("status") != "pending_approval":
        return "❌ No approved draft. Use 'draft <email_id>' to start a new one."
    
    # Fetch original email for quoting
    original_email = fetch_email(draft.get("email_id"))
    original_body = ""
    if original_email:
        original_body = original_email.get("text") or ""
        if not original_body and original_email.get("html"):
            import re
            original_body = re.sub(r'<[^>]+>', '', original_email.get("html", ""))
    
    # Build email body with quoted original
    reply_content = draft["reply_content"]
    
    if original_body:
        # Quote the original with > prefix
        quoted_original = "\n".join(["> " + line for line in original_body.split("\n")])
        email_body = f"""{reply_content}

---

On {draft.get('created_at', 'earlier')} wrote:
{quoted_original}"""
    else:
        email_body = reply_content
    
    # Send via Resend
    account = get_default_account()
    
    payload = {
        "from": f"{account['display_name']} <{account['email']}>",
        "to": [draft["to"]],
        "subject": draft["subject"],
        "text": email_body,
        "headers": {
            "In-Reply-To": draft["in_reply_to"],
            "References": draft["in_reply_to"]
        }
    }
    
    resp = requests.post(
        f"{API_BASE}/emails",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json=payload
    )
    
    if resp.status_code >= 400:
        return f"❌ Send failed: {resp.text}"
    
    # Automatically acknowledge the email after sending
    email_id = draft.get("email_id")
    if email_id:
        acknowledge_email(email_id)
    
    # Mark as sent instead of deleting - allows multiple replies to same thread
    draft["status"] = "sent"
    draft["sent_at"] = resp.json().get("created_at", "")
    save_draft_state(draft)
    
    return f"""✅ Email sent!

To: {draft['to']}
Subject: {draft['subject']}

💡 Reply again with 'resume' or start a new draft to continue this thread."""

def cancel_draft():
    """Cancel the current draft."""
    if DRAFT_STATE_FILE.exists():
        os.remove(DRAFT_STATE_FILE)
    return "❌ Draft cancelled."

def show_status():
    """Show current draft status."""
    draft = load_draft_state()
    if not draft:
        return "No active draft. Type 'draft <email_id>' to start."
    
    status = draft.get("status")
    if status == "waiting_for_reply":
        return f"📝 Waiting for your reply to: {draft['original_subject']}"
    elif status == "pending_approval":
        return f"""📤 Draft ready:
To: {draft['to']}
Subject: {draft['subject']}
---
{draft['reply_content'][:200]}...

Reply: send | edit | cancel"""
    elif status == "sent":
        return f"""📬 Thread active - last reply sent to: {draft['to']}
Subject: {draft['subject']}

Reply again with 'resume' to continue this thread."""
    return "Unknown draft state"


def resume_draft():
    """Resume a sent draft to reply again to the same thread."""
    draft = load_draft_state()
    if not draft:
        return "❌ No draft to resume. Start with 'draft <email_id>'"
    
    if draft.get("status") != "sent":
        return "❌ No sent draft to resume. Start a new draft or wait for a reply."
    
    # Re-use the same threading headers to keep the thread together
    draft["reply_content"] = None
    draft["status"] = "waiting_for_reply"
    save_draft_state(draft)
    
    return f"""📝 RESUMING THREAD

To: {draft['to']}
Subject: {draft['subject']}
(Replying to previous message in this thread)

Enter your reply content..."""

def main():
    if len(sys.argv) < 2:
        return show_status()
    
    cmd = sys.argv[1]
    
    if cmd == "start" and len(sys.argv) >= 3:
        return start_draft(sys.argv[2])
    elif cmd == "resume":
        return resume_draft()
    elif cmd == "content" and len(sys.argv) >= 3:
        # Everything after "content" is the reply
        content = " ".join(sys.argv[2:])
        return set_reply_content(content)
    elif cmd == "send":
        return send_draft()
    elif cmd == "cancel":
        return cancel_draft()
    elif cmd == "status":
        return show_status()
    else:
        return f"""Email Draft Commands:
python3 draft-reply.py status          - Show current draft
python3 draft-reply.py start <email_id> - Start draft for email
python3 draft-reply.py resume          - Resume sent draft to reply again
python3 draft-reply.py content "reply"  - Set reply content  
python3 draft-reply.py send            - Send approved draft
python3 draft-reply.py cancel           - Cancel draft"""

if __name__ == "__main__":
    print(main())