#!/usr/bin/env python3
"""
Configure email-resend cron job based on user preferences.

Reads telegram target/threadId from:
1. memory/email-preferences.md (explicit file - preferred)
2. OpenClaw context environment variables (fallback)
3. Ask user to approve/correct inferred defaults

No scanning of sensitive memory files (MEMORY.md, USER.md, TOOLS.md).
"""

import datetime
import json
import os
import re
import subprocess
import sys
import yaml

PREFERENCES_FILE = os.path.expanduser("~/.openclaw/workspace/memory/email-preferences.md")
SKILL_DIR = os.path.expanduser("~/.openclaw/workspace/skills/email-resend")
WORKSPACE = os.path.expanduser("~/.openclaw/workspace")


def load_preferences():
    """Load preferences from memory/email-preferences.md"""
    if not os.path.exists(PREFERENCES_FILE):
        return None
    
    with open(PREFERENCES_FILE, 'r') as f:
        content = f.read()
    
    # Extract YAML frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return None
    
    try:
        prefs = yaml.safe_load(match.group(1))
        return prefs
    except Exception as e:
        print(f"Error parsing preferences: {e}")
        return None


def get_context_preferences():
    """Get preferences from OpenClaw context (env vars) - no scanning"""
    prefs = {}
    
    # Check OpenClaw context environment variables
    # These are set by OpenClaw at runtime
    chat_id = os.environ.get('CLAW_CHAT_ID') or os.environ.get('CLAW_TARGET')
    thread_id = os.environ.get('CLAW_THREAD_ID') or os.environ.get('CLAW_TOPIC')
    
    # Try to get from_name from USER.md if available
    from_email = os.environ.get('CLAW_USER_EMAIL', 'ivelin@pirin.ai')
    from_name = os.environ.get('CLAW_USER_NAME', 'Ivelin Ivanov')
    
    if chat_id:
        prefs['telegram'] = {
            'target': chat_id,
            'threadId': thread_id or ''
        }
        prefs['from_email'] = from_email
        prefs['from_name'] = from_name
        return prefs
    
    return None


def get_preferences_or_prompt():
    """Get preferences with smart fallback - no sensitive file scanning"""
    
    # Step 1: Try explicit preferences file
    prefs = load_preferences()
    if prefs and prefs.get('telegram') and prefs['telegram'].get('target'):
        return prefs
    
    # Step 2: Try OpenClaw context (environment variables)
    context_prefs = get_context_preferences()
    if context_prefs and context_prefs.get('telegram') and context_prefs['telegram'].get('target'):
        print("\n⚠️ No explicit preferences file found.")
        print(f"Using OpenClaw context as inferred defaults:")
        print(f"  Target: {context_prefs['telegram']['target']}")
        print(f"  Thread ID: {context_prefs['telegram'].get('threadId', 'not set')}")
        print(f"  From: {context_prefs.get('from_email', 'ivelin@pirin.ai')}")
        print("")
        print("You can:")
        print("  1. Accept these defaults (cron will use them)")
        print("  2. Create memory/email-preferences.md to override")
        print("")
        response = input("Accept inferred defaults? [y/N]: ").strip().lower()
        if response == 'y':
            return context_prefs
    
    # Step 3: Ask user to create preferences file
    print("\nNo preferences found. Please set up your notification preferences:")
    print("")
    print("Create memory/email-preferences.md with:")
    print("""
---
from_email: your@email.com
from_name: Your Name
telegram:
  target: "CHAT_ID"
  threadId: "THREAD_ID"
---

# Email Notification Preferences
""")
    print("")
    print("Then run this script again.")
    sys.exit(1)


def delete_existing_cron():
    """Delete existing email-resend-inbound cron if it exists"""
    result = subprocess.run(
        ["openclaw", "cron", "list", "--format", "json"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        return
    
    try:
        crons = json.loads(result.stdout)
        for cron in crons:
            if cron.get('name') == 'email-resend-inbound':
                print(f"Deleting existing cron: {cron.get('id')}")
                subprocess.run(
                    ["openclaw", "cron", "delete", cron.get('id')],
                    check=True
                )
    except Exception as e:
        print(f"Warning: Could not check for existing crons: {e}")


def add_cron(target, thread_id):
    """Add the cron job with the specified target"""
    cron_cmd = [
        "openclaw", "cron", "add",
        "--name", "email-resend-inbound",
        "--cron", "*/15 * * * *",
        "--message", "Follow instructions in skills/email-resend/cron-prompts/email-inbound.md exactly. If new emails found, include them in your reply.",
        "--session", "isolated",
        "--announce",
        "--channel", "telegram",
        "--to", f"{target}:topic:{thread_id}"
    ]
    
    print(f"Running: {' '.join(cron_cmd)}")
    result = subprocess.run(cron_cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error adding cron: {result.stderr}")
        sys.exit(1)
    
    print("Cron added successfully!")
    print(result.stdout)


def main():
    print("Configuring email-resend cron from preferences...")
    print("")
    
    prefs = get_preferences_or_prompt()
    
    telegram = prefs.get('telegram', {})
    target = telegram.get('target', '')
    thread_id = telegram.get('threadId', '')
    
    if not target or not thread_id:
        print("Error: telegram.target or telegram.threadId not set in preferences")
        sys.exit(1)
    
    print(f"Found preferences:")
    print(f"  Target: {target}")
    print(f"  Thread ID: {thread_id}")
    print("")
    
    delete_existing_cron()
    add_cron(target, thread_id)
    
    print("")
    print("✅ Cron configured successfully!")


if __name__ == "__main__":
    main()
