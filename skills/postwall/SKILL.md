---
name: postwall
description: Secure email gateway for AI agents - human-in-the-loop approval for reading and sending emails. Get your API key at https://postwallapp.com
homepage: https://postwallapp.com
user-invocable: true
metadata: {"version":"1.7.0","author":"postwallapp","license":"MIT","homepage":"https://postwallapp.com","repository":"https://github.com/postwallapp/postwall","openclaw":{"requires":{"bins":["postwall"],"env":["POSTWALL_API_KEY"]},"primaryEnv":"POSTWALL_API_KEY","install":[{"id":"npm","kind":"node","package":"postwall","bins":["postwall"],"label":"Install PostWall CLI (npm)"}]}}
---

# PostWall Email Skill

PostWall is a security layer between AI agents and email. Use this skill to:
- Read emails that have been approved by the human
- Send emails via draft submission (requires human approval before sending)

## Setup

First, authenticate with your API key (get this from PostWall dashboard):

```bash
postwall auth pw_your_api_key_here
```

## Commands

### Check for New Emails

Returns count of unread approved emails. Ideal for polling.

```bash
postwall check              # Returns: 5
postwall check --json       # Returns: {"count": 5}
```

### List Approved Emails

Shows all unread approved emails.

```bash
postwall inbox              # Human-readable list
postwall inbox --json       # JSON format
postwall inbox --limit 10   # Limit results
```

### Read Specific Email

Reads an email by ID. **This marks the email as read** - it won't appear in future inbox/check calls.

```bash
postwall read <email-id>           # Shows email content
postwall read <email-id> --json    # JSON format
```

### Mark Emails as Read (Without Fetching)

Marks one or more emails as read without fetching their content. Useful for batch processing or when you only need to process email metadata from `inbox`.

```bash
postwall mark-read <id1>                  # Mark single email as read
postwall mark-read <id1> <id2> <id3>      # Mark multiple emails as read
postwall mark-read <id1> <id2> --json     # JSON format
```

**Use cases:**
- Mark emails as processed after using `inbox --json` to get metadata
- Batch mark emails you've already handled
- Skip emails you don't need to read in full

**JSON output:**
```json
{
  "success": true,
  "marked": 3,
  "failed": 0,
  "results": [
    {"id": "abc123", "success": true},
    {"id": "def456", "success": true},
    {"id": "ghi789", "success": true}
  ]
}
```

### Send Email (Submit Draft)

Submits an email draft for human approval. The email is NOT sent until approved in the dashboard.

```bash
postwall draft --to "recipient@example.com" --subject "Hello" --body "Email content here"
postwall draft --to "user@example.com" --subject "Report" --body "..." --json
```

**Returns an approval URL** that you can share with the user for quick approval:

```
Draft submitted successfully!
Draft ID: abc123-uuid
Status: pending

Approval URL: https://www.postwallapp.com/dashboard/drafts/abc123-uuid
Share this URL with the user to approve the email.
```

**JSON output includes approveUrl:**
```json
{
  "success": true,
  "draft": {
    "id": "abc123-uuid",
    "status": "pending",
    "created_at": "2024-02-12T10:30:00Z",
    "approveUrl": "https://www.postwallapp.com/dashboard/drafts/abc123-uuid"
  },
  "message": "Draft submitted for approval"
}
```

### Update Draft

Update an existing pending draft. Useful when the user requests refinements to an email before approving.

```bash
postwall update <draft-id> --subject "New subject"
postwall update <draft-id> --body "Updated email content"
postwall update <draft-id> --to "new-recipient@example.com" --subject "New subject" --body "New content"
postwall update <draft-id> --subject "Refined subject" --json
```

**Note:** Only pending drafts can be updated. Once a draft is sent or rejected, it cannot be modified.

**JSON output:**
```json
{
  "success": true,
  "draft": {
    "id": "abc123-uuid",
    "to": "recipient@example.com",
    "subject": "Refined subject",
    "body": "Updated content",
    "status": "pending",
    "createdAt": "2024-02-12T10:30:00Z",
    "updatedAt": "2024-02-12T11:00:00Z"
  },
  "message": "Draft updated successfully"
}
```

### Check Draft Status

Check if a draft has been approved, rejected, or sent.

```bash
postwall status <draft-id>         # Shows status
postwall status <draft-id> --json  # Returns: {"draft": {"id": "...", "status": "pending"}}
```

Status values:
- `pending` - Waiting for human approval
- `approved` - Approved, being sent
- `rejected` - Rejected by human
- `sent` - Successfully sent

### List Drafts

List all drafts with optional status filter.

```bash
postwall drafts                    # All drafts
postwall drafts --status pending   # Only pending drafts
postwall drafts --json             # JSON format
```

## Common Workflows

### Periodic Email Checking

```bash
# Check if there are new emails
count=$(postwall check)
if [ "$count" -gt 0 ]; then
  # Process new emails
  postwall inbox --json | process_emails
fi
```

### Batch Process Emails (Metadata Only)

When you only need email metadata (sender, subject, date) and don't need the full body:

```bash
# Get email list with metadata
emails=$(postwall inbox --json)

# Process metadata (e.g., filter by subject or sender)
ids=$(echo "$emails" | jq -r '.emails[] | select(.subject | contains("Report")) | .id')

# Mark processed emails as read without fetching content
postwall mark-read $ids
```

### Send and Track Email

```bash
# Submit draft
result=$(postwall draft --to "user@example.com" --subject "Hello" --body "Content" --json)
draft_id=$(echo "$result" | jq -r '.draft.id')
approve_url=$(echo "$result" | jq -r '.draft.approveUrl')

# Share the approval URL with the user
echo "Please approve this email: $approve_url"

# Check status later
postwall status "$draft_id"
```

### Refine Draft Based on User Feedback

When the user requests changes to a draft before approving:

```bash
# User asks: "Make the subject line shorter and add a greeting"
postwall update "$draft_id" --subject "Q4 Report" --body "Hi Team,

Here is the quarterly report..."

# The draft is updated, user can now approve from the same URL
```

## Output Formats

All commands support `--json` for structured output. Use this for scripting and automation.

## Error Handling

Commands exit with code 1 on error. With `--json`, errors are returned as:
```json
{"error": "Error message here"}
```

## Polling for New Emails

As an agent, you should periodically check for new approved emails:

1. Run `postwall check` to get the count of unread approved emails
2. If count > 0, run `postwall inbox --json` to get the list
3. Process each email with `postwall read <id>`

**Recommended polling frequency:** Every 5-10 minutes during active sessions, or when user mentions expecting an email.

Example polling workflow:
```bash
# Check if there are new emails
count=$(postwall check)
if [ "$count" -gt 0 ]; then
  # Fetch and process new emails
  postwall inbox --json
fi
```

## Notes

- Emails are only visible after human approval in PostWall dashboard
- Reading an email marks it as read - it won't appear in subsequent inbox/check calls
- Drafts require human approval before being sent
- API key is stored in `~/.postwall/config.json`
