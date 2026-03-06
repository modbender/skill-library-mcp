#!/usr/bin/env python3
"""
Process emails from mediated contacts.
Checks for new emails, processes them, archives originals, sends summaries.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    os.system(f"{sys.executable} -m pip install -q pyyaml")
    import yaml

CONFIG_FILE = Path.home() / ".clawdbot" / "mediator.yaml"
STATE_FILE = Path.home() / ".clawdbot" / "mediator-state.json"
LOG_FILE = Path.home() / ".clawdbot" / "logs" / "mediator.log"
GOG_SCRIPT = Path.home() / "clawd" / "scripts" / "gog-read.sh"
SUMMARIZE_SCRIPT = Path(__file__).parent / "summarize.py"


def log(msg):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] [email] {msg}\n")


def load_config():
    if not CONFIG_FILE.exists():
        return None
    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f)


def load_state():
    if not STATE_FILE.exists():
        return {"last_check": {}, "processed_ids": []}
    with open(STATE_FILE) as f:
        return json.load(f)


def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def get_email_contacts(config):
    """Get contacts that have email channel enabled."""
    contacts = config.get("mediator", {}).get("contacts", [])
    return [c for c in contacts if "email" in c.get("channels", [])]


def search_emails(account: str, sender_email: str) -> list:
    """Search for unread emails from a specific sender."""
    query = f"is:unread from:{sender_email}"
    
    # Determine account flag
    account_flag = "--work" if "doxy" in account else ""
    
    cmd = [str(GOG_SCRIPT), "gmail", "search", query]
    if account_flag:
        cmd.insert(1, account_flag)
    cmd.extend(["--json", "--limit", "10"])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            log(f"Email search failed: {result.stderr}")
            return []
        
        # Parse JSON output
        output = result.stdout.strip()
        if not output or output == "[]":
            return []
        
        return json.loads(output)
    except Exception as e:
        log(f"Email search error: {e}")
        return []


def get_email_content(account: str, message_id: str) -> dict:
    """Get full email content."""
    account_flag = "--work" if "doxy" in account else ""
    
    cmd = [str(GOG_SCRIPT), "gmail", "get", message_id]
    if account_flag:
        cmd.insert(1, account_flag)
    cmd.append("--json")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            log(f"Email get failed: {result.stderr}")
            return {}
        
        return json.loads(result.stdout)
    except Exception as e:
        log(f"Email get error: {e}")
        return {}


def archive_email(account: str, message_id: str, thread_id: str):
    """Archive email (add Mediator/Raw label, mark read)."""
    # This needs to go through SAL for write operations
    # For now, log that we would archive
    log(f"Would archive email {message_id} (requires SAL for write ops)")
    
    # TODO: Implement via SAL request
    # sal_request = {
    #     "action": "email.modify",
    #     "account": account,
    #     "params": {
    #         "message_id": message_id,
    #         "add_labels": ["Mediator/Raw"],
    #         "mark_read": True
    #     }
    # }


def summarize_content(contact: dict, content: str) -> dict:
    """Use LLM to summarize/neutralize content."""
    try:
        result = subprocess.run(
            [sys.executable, str(SUMMARIZE_SCRIPT), 
             "--mode", contact.get("summarize", "facts-only"),
             "--content", content],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            log(f"Summarize failed: {result.stderr}")
            return {"summary": content, "action_required": False, "suggested_response": ""}
    except Exception as e:
        log(f"Summarize error: {e}")
        return {"summary": content, "action_required": False, "suggested_response": ""}


def send_summary(contact: dict, email_data: dict, summary: dict, notify_channel: str):
    """Send summary to notification channel."""
    contact_name = contact.get("name", "Unknown")
    subject = email_data.get("subject", "(no subject)")
    
    message_parts = [
        f"📨 **Mediated Email from {contact_name}**",
        f"Subject: {subject}",
        "",
        "**Summary:**",
        summary.get("summary", "(no summary)"),
    ]
    
    if summary.get("action_required"):
        message_parts.append("")
        message_parts.append("⚡ **Action Required:** Yes")
    
    if summary.get("suggested_response"):
        message_parts.append("")
        message_parts.append("**Suggested Response:**")
        message_parts.append(f"> {summary['suggested_response']}")
    
    message = "\n".join(message_parts)
    
    # For now, print to stdout (caller can route appropriately)
    print(f"=== MEDIATOR SUMMARY ===\n{message}\n========================")
    log(f"Generated summary for email from {contact_name}")


def check_emails():
    """Main check routine - scan for emails from mediated contacts."""
    config = load_config()
    if not config:
        log("No config found")
        return
    
    state = load_state()
    email_contacts = get_email_contacts(config)
    
    if not email_contacts:
        return
    
    accounts = config.get("mediator", {}).get("gmail_accounts", [
        "dylan.turner22@gmail.com",
        "dylan@doxy.me"
    ])
    
    notify_channel = config.get("mediator", {}).get("notify_channel", "telegram")
    processed_ids = set(state.get("processed_ids", []))
    new_processed = []
    
    for contact in email_contacts:
        email = contact.get("email")
        if not email:
            continue
        
        for account in accounts:
            emails = search_emails(account, email)
            
            for email_data in emails:
                msg_id = email_data.get("id")
                if not msg_id or msg_id in processed_ids:
                    continue
                
                log(f"Processing email {msg_id} from {contact.get('name')}")
                
                # Get full content
                full_email = get_email_content(account, msg_id)
                if not full_email:
                    continue
                
                # Summarize
                body = full_email.get("body", full_email.get("snippet", ""))
                summary = summarize_content(contact, body)
                
                # Archive if intercept mode
                if contact.get("mode") == "intercept":
                    archive_email(account, msg_id, full_email.get("thread_id", ""))
                
                # Send summary
                send_summary(contact, full_email, summary, notify_channel)
                
                new_processed.append(msg_id)
    
    # Update state
    if new_processed:
        state["processed_ids"] = list(processed_ids | set(new_processed))[-500:]  # Keep last 500
        state["last_check"]["email"] = datetime.now().isoformat()
        save_state(state)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        check_emails()
    else:
        print("Usage: process-email.py check")
