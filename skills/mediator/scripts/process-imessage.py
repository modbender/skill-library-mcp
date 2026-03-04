#!/usr/bin/env python3
"""
Process iMessages from mediated contacts.
Checks for new messages, processes them, sends summaries.
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
SUMMARIZE_SCRIPT = Path(__file__).parent / "summarize.py"


def log(msg):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] [imessage] {msg}\n")


def load_config():
    if not CONFIG_FILE.exists():
        return None
    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f)


def load_state():
    if not STATE_FILE.exists():
        return {"last_check": {}, "processed_ids": [], "imessage_last_ts": {}}
    with open(STATE_FILE) as f:
        return json.load(f)


def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def get_imessage_contacts(config):
    """Get contacts that have imessage channel enabled."""
    contacts = config.get("mediator", {}).get("contacts", [])
    return [c for c in contacts if "imessage" in c.get("channels", [])]


def normalize_phone(phone: str) -> str:
    """Normalize phone number for comparison."""
    return "".join(c for c in phone if c.isdigit())[-10:]


def get_recent_messages(phone: str, limit: int = 10) -> list:
    """Get recent messages from a phone number using imsg CLI."""
    try:
        # Use imsg history command
        result = subprocess.run(
            ["imsg", "history", phone, "--limit", str(limit), "--json"],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode != 0:
            log(f"imsg history failed: {result.stderr}")
            return []
        
        output = result.stdout.strip()
        if not output:
            return []
        
        return json.loads(output)
    except FileNotFoundError:
        log("imsg command not found")
        return []
    except Exception as e:
        log(f"imsg error: {e}")
        return []


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


def send_summary(contact: dict, messages: list, summary: dict, notify_channel: str):
    """Send summary to notification channel."""
    contact_name = contact.get("name", "Unknown")
    msg_count = len(messages)
    
    message_parts = [
        f"💬 **Mediated iMessage from {contact_name}**",
        f"({msg_count} message{'s' if msg_count != 1 else ''})",
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
    log(f"Generated summary for iMessage from {contact_name}")


def check_imessages():
    """Main check routine - scan for iMessages from mediated contacts."""
    config = load_config()
    if not config:
        log("No config found")
        return
    
    state = load_state()
    imessage_contacts = get_imessage_contacts(config)
    
    if not imessage_contacts:
        return
    
    notify_channel = config.get("mediator", {}).get("notify_channel", "telegram")
    last_timestamps = state.get("imessage_last_ts", {})
    
    for contact in imessage_contacts:
        phone = contact.get("phone")
        if not phone:
            continue
        
        normalized = normalize_phone(phone)
        last_ts = last_timestamps.get(normalized, 0)
        
        messages = get_recent_messages(phone)
        if not messages:
            continue
        
        # Filter to new incoming messages only
        new_messages = []
        max_ts = last_ts
        
        for msg in messages:
            msg_ts = msg.get("timestamp", 0)
            is_from_them = not msg.get("is_from_me", True)
            
            if is_from_them and msg_ts > last_ts:
                new_messages.append(msg)
                max_ts = max(max_ts, msg_ts)
        
        if not new_messages:
            continue
        
        log(f"Processing {len(new_messages)} new iMessage(s) from {contact.get('name')}")
        
        # Combine message texts for summarization
        combined_text = "\n".join(m.get("text", "") for m in new_messages)
        
        # Summarize
        summary = summarize_content(contact, combined_text)
        
        # Send summary
        send_summary(contact, new_messages, summary, notify_channel)
        
        # Update timestamp
        last_timestamps[normalized] = max_ts
    
    # Update state
    state["imessage_last_ts"] = last_timestamps
    state["last_check"]["imessage"] = datetime.now().isoformat()
    save_state(state)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        check_imessages()
    else:
        print("Usage: process-imessage.py check")
