---
name: email-processor
description: |
  Automate Gmail inbox processing - categorizes unread emails, marks marketing/newsletters/promotions as read, and surfaces important emails requiring attention.
  
  USE WHEN: User asks to "check my emails", "process unread emails", "clean up my inbox", "mark newsletters as read", or any Gmail automation task.
  
  REQUIRES: gog CLI (brew install steipete/tap/gogcli) + Google Cloud OAuth credentials
---

# Email Processor

Automates Gmail inbox triage by categorizing unread emails and marking low-priority items as read.

## What It Does

1. Fetches all unread emails
2. Identifies marketing, newsletters, promotions, and news
3. Marks low-priority emails as read
4. Surfaces important emails (GitHub, security alerts, direct communications)
5. Generates a summary report

## Prerequisites

### 1. Install gog CLI

```bash
brew install steipete/tap/gogcli
```

Verify installation:
```bash
gog --version
```

### 2. Google Cloud OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable the Gmail API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API" and enable it
4. Create OAuth credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Desktop app" as application type
   - Download the JSON file

### 3. Authenticate gog

```bash
# Set credentials
gog auth credentials /path/to/client_secret.json

# Add your Gmail account
gog auth add your@gmail.com --services gmail

# Verify
gog auth list
```

## Usage

### Quick Process

```bash
bash ~/.openclaw/workspace/skills/email-processor/scripts/process-emails.sh
```

### Manual Processing (via Codex)

1. **Fetch unread emails:**
   ```bash
   gog gmail search 'is:unread' --json --max 100
   ```

2. **Mark specific thread as read:**
   ```bash
   gog gmail thread modify <thread-id> --remove UNREAD --force
   ```

3. **Mark marketing emails (batch):**
   ```bash
   gog gmail search 'is:unread' --json --max 100 | \
     jq -r '.threads[] | select(.labels | contains(["CATEGORY_PROMOTIONS"])) | .id' | \
     while read id; do gog gmail thread modify "$id" --remove UNREAD --force; done
   ```

## Email Categories

### Auto-Marked as Read

- `CATEGORY_PROMOTIONS` - Promotional emails
- `[Superhuman]/AI/News` - Newsletters
- `[Superhuman]/AI/Marketing` - Marketing emails
- `[Superhuman]/AI/Pitch` - Cold outreach/pitches
- `[Superhuman]/AI/AutoArchived` - Auto-categorized low priority

### Preserved (Important)

- GitHub notifications (PRs, issues, security alerts)
- Direct personal communications
- Financial/transaction emails
- Security alerts
- Calendar invites

## Verification

Check setup is working:

```bash
# Test gog connectivity
gog gmail search 'is:unread' --max 5

# Check account
gog auth list

# Test modify (dry run - just list what would be marked)
gog gmail search 'is:unread' --json --max 10 | \
  jq -r '.threads[] | select(.labels | contains(["CATEGORY_PROMOTIONS"])) | {id: .id, subject: .subject}'
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `gog: command not found` | Run `brew install steipete/tap/gogcli` |
| `authentication required` | Run `gog auth credentials` and `gog auth add` |
| `token expired` | Run `gog auth refresh your@gmail.com` |
| `Gmail API not enabled` | Enable at https://console.cloud.google.com/apis/library/gmail.googleapis.com |
| Rate limit errors | Add delays between requests or reduce batch size |

## Labels Reference

Gmail automatically applies these labels:
- `CATEGORY_PERSONAL` - Personal emails
- `CATEGORY_SOCIAL` - Social notifications
- `CATEGORY_PROMOTIONS` - Promotions
- `CATEGORY_UPDATES` - Updates/notifications
- `CATEGORY_FORUMS` - Forum messages
- `IMPORTANT` - Marked important
- `UNREAD` - Unread status

Superhuman AI labels (if using Superhuman):
- `[Superhuman]/AI/News` - Newsletters
- `[Superhuman]/AI/Marketing` - Marketing
- `[Superhuman]/AI/Pitch` - Pitches
- `[Superhuman]/AI/AutoArchived` - Auto-archived
