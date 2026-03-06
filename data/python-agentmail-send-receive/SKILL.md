---
name: python-agentmail-send-receive
description: python files which are used to send an email and to download received emails from an inbox. The email provider is agentmail.to, which offers an API. This way of email handling is very AI-agent friendly.
homepage: https://github.com/lausser/python-agentmail-send-receive
---

# Skill: Email via agentmail

You can send and receive email as `REPLACE_WITH_IDENTITY@agentmail.to` using two Python scripts.
The scripts live in this skill folder and are deployed to `~/.openclaw/workspace/agentmail/`.
The scripts contain placeholders which need to be replaced with real-life value:
* REPLACE_WITH_IDENTITY
* REPLACE_WITH_THE_HUMANS_EMAIL_ADDRESS

## 1. Setup

### Deploy the skill

Copy the scripts and create the venv in the workspace:

```bash
DEST=~/.openclaw/workspace/agentmail
SKILL_DIR="$(dirname "$(readlink -f "$0")")"    # if running from a script
# or just point SKILL_DIR to this skill folder

mkdir -p "$DEST"
cp "$SKILL_DIR/check_mail.py" "$SKILL_DIR/send_email.py" "$DEST/"

cd "$DEST"

# Create venv (prefer uv, fall back to python)
if command -v uv &>/dev/null; then
  uv venv venv
  uv pip install --python venv/bin/python agentmail python-dotenv
else
  python3 -m venv venv
  venv/bin/pip install agentmail python-dotenv
fi
```

### Create the `.env` file

```bash
cat > ~/.openclaw/workspace/agentmail/.env << 'EOF'
AGENTMAIL_API_KEY=am_us_.....
EOF
```

This is only necessary if you don't have the environment variable in your running environment or if you can't read it from your openclaw.json config file.

### Verify

```bash
cd ~/.openclaw/workspace/agentmail
source venv/bin/activate
python check_mail.py        # should print "No new mail." on a fresh inbox
```

## 2. Receiving Email

### Run

```bash
cd ~/.openclaw/workspace/agentmail
source venv/bin/activate
python check_mail.py
```

This downloads all unread messages as JSON files into the workspace directory and marks them as read. Running it again only fetches new mail.

### Output files

Each message is saved as `MAIL.<YYYYMMDDTHHmmss>.<NNN>` — timestamp from the message, 3-digit sequence number within the batch.

Example: `MAIL.20260226T134244.001`

The JSON inside contains:

```json
{
  "message_id": "<...>",
  "thread_id": "...",
  "timestamp": "2026-02-26 13:42:44+00:00",
  "from": "Sender Name <sender@example.com>",
  "to": ["REPLACE_WITH_IDENTITY@agentmail.to"],
  "cc": null,
  "subject": "Re: Hello",
  "text": "Plain-text body...",
  "html": "<p>HTML body...</p>",
  "labels": ["received", "unread"],
  "in_reply_to": "<original-message-id>",
  "attachments": []
}
```

### Reading downloaded mail

```bash
# List all mail files (oldest first)
ls -1 MAIL.* 2>/dev/null | sort

# Read one
cat MAIL.20260226T134244.001

# Extract just the text body
python -c "import json,sys; print(json.load(open(sys.argv[1]))['text'])" MAIL.20260226T134244.001
```

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success (mail downloaded or inbox empty) |
| 1 | Missing API key |
| 2 | API error on initial listing |
| 3 | Total failure (all messages errored) |

## 3. Sending Email

### Run

```bash
cd ~/.openclaw/workspace/agentmail
source venv/bin/activate
python send_email.py
```

`send_email.py` is a template with hardcoded recipient/subject/body. For real use, modify its parameters or write a one-off script using the same pattern:

```python
import os
from dotenv import load_dotenv
from agentmail import AgentMail

load_dotenv()
client = AgentMail(api_key=os.getenv("AGENTMAIL_API_KEY"))

client.inboxes.messages.send(
    inbox_id="REPLACE_WITH_IDENTITY@agentmail.to",
    to="recipient@example.com",
    subject="Subject line",
    text="Plain-text body.",
)
```

### send() parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `inbox_id` | yes | Always `"REPLACE_WITH_IDENTITY@agentmail.to"` |
| `to` | yes | Recipient email address |
| `subject` | no | Subject line |
| `text` | no | Plain-text body |
| `html` | no | HTML body |
| `cc` | no | CC addresses |
| `bcc` | no | BCC addresses |

## 4. Replying to a Message

To reply in the same thread, use `reply()` with the `message_id` from a downloaded `MAIL.*` file:

```python
import json, os
from dotenv import load_dotenv
from agentmail import AgentMail

load_dotenv()
client = AgentMail(api_key=os.getenv("AGENTMAIL_API_KEY"))

# Load the message you want to reply to
with open("MAIL.20260226T134244.001") as f:
    msg = json.load(f)

client.inboxes.messages.reply(
    inbox_id="REPLACE_WITH_IDENTITY@agentmail.to",
    message_id=msg["message_id"],
    text="This is my reply.",
)
```

This preserves threading — the reply appears in the same conversation as the original.

## 5. Typical Workflow

1. **Check mail**: `python check_mail.py`
2. **Read**: inspect the `MAIL.*` files that were created
3. **Process**: act on the content of each message
4. **Reply** if needed: use the `reply()` pattern from section 4
5. **Clean up**: `rm MAIL.*` when done processing
6. **Repeat**: run `check_mail.py` again later for new messages
