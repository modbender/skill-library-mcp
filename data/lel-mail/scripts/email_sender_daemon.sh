#!/usr/bin/env bash
# /root/.openclaw/workspace/email_sender_daemon.sh

set -euo pipefail

# ----------- Send via Python’s smtplib -----------------
python3 - <<PY
import os, sys, json, ssl, smtplib
from datetime import datetime, timezone
from email.message import EmailMessage
import random
import time

QUEUE_FILE  = os.path.expanduser("~/.config/lel-mail/queue.json")
CONFIG_FILE = os.path.expanduser("~/.config/lel-mail/config.json")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json_atomic(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)


# --- Load queue ---
if not os.path.exists(QUEUE_FILE):
    print("Queue file not found, terminating")
    sys.exit(1)

QUEUE_DATA = load_json(QUEUE_FILE)

remaining = QUEUE_DATA.get("remaining") or []
if not isinstance(remaining, list) or len(remaining) == 0:
    print("Queue is empty, no emails to send for now")
    sys.exit(0)

# --- Load config accounts ---
if not os.path.exists(CONFIG_FILE):
    print("Configuration file not found, will terminate for now and check later")
    sys.exit(1)

config = load_json(CONFIG_FILE)  # expected list of accounts

def find_account_for_sender(sender_email: str):
    for item in config:
        if item.get("auth", {}).get("user") == sender_email:
            return item
    return None

# --- Pick first sendable email (skip entries with unknown sender) ---
idx_to_send = None
email_to_send = None
config_data = None

for i, entry in enumerate(remaining):
    sender = entry.get("SENDER")  # stored queue format
    if not sender:
        continue
    acct = find_account_for_sender(sender)

    if (acct.get("can_send", False) == False):
        continue

    if acct is not None:
        idx_to_send = i
        email_to_send = entry
        config_data = acct
        break

if config_data is None:
    print("No valid users found in queue (no matching SENDER in config).")
    sys.exit(1)

# --- Extract stored email fields (your stored format) ---
sender    = email_to_send.get("SENDER")
recipient = email_to_send.get("RECIPIENT")
subject   = email_to_send.get("SUBJECT", "")
body      = email_to_send.get("BODY", "")
cc_list   = email_to_send.get("CC") or []
bcc_list  = email_to_send.get("BCC") or []

if not recipient:
    print("Queued item missing recipient; skipping.")
    # remove bad entry so it doesn't block
    remaining.pop(idx_to_send)
    save_json_atomic(QUEUE_FILE, QUEUE_DATA)
    sys.exit(1)

# --- SMTP credentials come from the sender’s account config ---
server   = config_data["config"]["smtp"]["server"]
port     = int(config_data["config"]["smtp"]["port"])
user     = config_data["auth"]["user"]
password = config_data["auth"]["password"]

# --- Build RFC822 message correctly ---
msg = EmailMessage()
msg["From"] = sender  # or user; usually same, but keep sender explicit
msg["To"] = recipient
msg["Subject"] = subject
if cc_list:
    msg["Cc"] = ", ".join(cc_list)
# IMPORTANT: do NOT add Bcc header (it should be hidden)
msg.set_content(body)

# SMTP envelope recipients must include To + Cc + Bcc
rcpt_to = [recipient] + list(cc_list) + list(bcc_list)

delay_seconds = random.randint(30, 90)
time.sleep(delay_seconds)

context = ssl.create_default_context()
with smtplib.SMTP(server, port) as smtp:
    smtp.starttls(context=context)
    smtp.login(user, password)
    smtp.sendmail(sender, rcpt_to, msg.as_string())

# --- Update queue after successful send ---
remaining.pop(idx_to_send)
QUEUE_DATA["last_sent"] = datetime.now(timezone.utc).isoformat()

save_json_atomic(QUEUE_FILE, QUEUE_DATA)

print(f"Sent queued email from {sender} to {recipient}. Remaining: {len(remaining)}")
PY

echo "✅ Email sent"
