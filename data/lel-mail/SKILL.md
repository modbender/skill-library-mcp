---
name: lel-mail
description: Send and read email via a combination of python and bash scripts which makes use of the main agent for reasoning and logic. This skill enables the agent to write to memory based on contents in the email and to reach out to the user either to notify them of happenings or to request inputs to respond. This skill also contains a python script to read and manage the email queue containing functionality to list pending outgoing emails and delete emails before they can be sent out. Please note that this skill enables the agent to act upon received emails by adding to agent memory and sending responses
metadata: {"clawdbot":{"emoji":"📧","requires":{"bins":["python3"]}}}
---

# Lel Mail

## Important Note If Running On the Cloud/VPS
- Some cloud providers explicitly disable email leading to failiure of these scripts, services like tailscale will be needed to bypass these blocks

## Setup
### Setting up the Config File

Create `~/.config/lel-mail/config.json`:
```json
[
  {
    "provider": "gmail",
    "config": {
        "smtp": {
        "server": "smtp.gmail.com", //Default url
        "port": 587 //Default port
      },
      "imap": {
        "server": "imap.gmail.com", //Default url
        "port": 993 //Default port
      }
    },
    "auth": {
      "user": "example@gmail.com",
      "password": "XXXX XXXX XXXX XXXX" //Gmail Requires App Specific Password Rather Than Your Normal Password
    },
    "can_send": true,
    "can_read": true
  }
]
```

### Setting up cron job
Set up a simple cron job which runs the following command every 5 minutes with a randomised 30-90 second delay. Confirm with user the interval to be used:
 ```~/.openclaw/workspace/skills/lel-mail/scripts/email_sender_daemon.sh```


## Quick Reference

### Read Email

1. Make sure config exists, if not create it with input of user
2. Reference USERS.md (or whatever USER reference file your system uses) to see what email(s) you need to check unless user explicitly defines the email(s)
3. Run the following command ```~/.openclaw/workspace/skills/lel-mail/scripts/check_email.sh <USER_EMAIL>```

### Send Email
# Note, this script does not send the data directly but sends it to a scheduler which will automatically send it in approximately 5.5 minutes
1. Make sure you have the necessary data to send the email from the user, that includes sender, recipient and body, everything else is optional
2. Run the following command ```~/.openclaw/workspace/skills/lel-mail/scripts/email_send.sh --sender <sender> --recipient <recipient> --subject <subject> --body <body> [--cc ...] [--bcc ...]``` Note: if using BCC/CC note that CC/BCC are comma-separated lists


### 3. Manage Outgoing Queue
Outgoing emails are scheduled to send with a random delay (30-90 seconds). You can list or delete these before they are sent.

**List all queued emails**:
```bash
python3 ~/.openclaw/workspace/skills/lel-mail/scripts/manage_queue.py --list
```

**Delete a specific email by ID**:
```bash
python3 ~/.openclaw/workspace/skills/lel-mail/scripts/manage_queue.py --delete <ID>
```

## Troubleshooting
Prompt user to assist when errors occur due to missing/invalid credentials/configuration
- If emails aren't sending at all check that a cron job for the daemon is running
