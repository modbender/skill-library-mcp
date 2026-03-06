# Processing Rules Reference

Rules are evaluated in priority order (highest first). Each rule matches against
message fields using regex patterns and triggers one or more actions.

## Rule Schema

```yaml
- name: rule_name          # Required: unique identifier
  actions:                  # Required: list of actions to take
    - flag
    - tag
  sender_pattern: "regex"   # Match against sender (case-insensitive)
  subject_pattern: "regex"  # Match against subject
  body_pattern: "regex"     # Match against body text
  mailbox: "INBOX"          # Match exact mailbox name
  account: "work"           # Match only messages from this account
  has_attachments: true     # Match messages with/without attachments
  tag: "label"              # Tag to apply (for "tag" action)
  move_to: "Folder"         # Destination folder (for "move" action)
  forward_to: "addr"        # Forward address (for "forward" action)
  reply_template: "text"    # Reply body (for "auto_reply" action)
  webhook_url: "https://..."  # URL to POST to (for "webhook" action)
  priority: 10              # Higher = evaluated first
  stop_after_match: false   # Stop processing further rules if matched
```

## Available Actions

| Action | Description | Required Fields |
|--------|-------------|-----------------|
| `flag` | Flag the message (IMAP \Flagged) | — |
| `tag` | Add a tag/label to the message | `tag` |
| `mark_read` | Mark the message as read | — |
| `move` | Move message to another folder | `move_to` |
| `archive` | Archive the message | — |
| `forward` | Forward to another address | `forward_to` |
| `auto_reply` | Send an automatic reply via SMTP | `reply_template` |
| `webhook` | POST a JSON payload to a URL | `webhook_url` |
| `skip` | Stop processing further rules | — |

## Pattern Matching

All patterns use Python regex syntax (`re.search`) with `re.IGNORECASE`.
All specified criteria on a single rule must match (AND logic).
Multiple rules matching the same message accumulate actions (OR logic across rules).

### Examples

```yaml
# Match emails from a specific domain
sender_pattern: "@company\\.com$"

# Match urgent subjects
subject_pattern: "urgent|asap|critical|\\bhelp\\b"

# Match emails with invoice attachments
subject_pattern: "invoice"
has_attachments: true
```

## Configuration Examples

### rules.yaml

```yaml
# Priority support routing
- name: vip_support
  sender_pattern: "@bigclient\\.com$"
  actions: [flag, tag]
  tag: vip
  priority: 20

# Flag urgent from boss
- name: boss_urgent
  sender_pattern: "boss@company\\.com"
  subject_pattern: "urgent|asap"
  actions: [flag, tag]
  tag: urgent
  priority: 15

# Move invoices to Finances folder
- name: sort_invoices
  subject_pattern: "invoice|receipt|payment"
  has_attachments: true
  actions: [move, tag]
  move_to: "Finances"
  tag: invoice
  priority: 8

# Move newsletters to a subfolder
- name: sort_newsletters
  sender_pattern: "newsletter@|noreply@|marketing@"
  actions: [move, mark_read, tag]
  move_to: "Newsletters"
  tag: newsletter
  priority: 5
```

### Webhook Rule

```yaml
# POST to Slack when alerts arrive
- name: alert_webhook
  sender_pattern: "alerts@|monitoring@"
  actions: [tag, webhook]
  tag: alert
  webhook_url: "https://hooks.slack.com/services/T00/B00/xxx"
  priority: 50
```

The webhook POSTs a JSON payload with `event`, `message_id`, `subject`,
`sender`, `matched_rules`, and `tags` fields. Results are recorded in
`ProcessingResult.webhook_results`.

### Inline JSON (for CLI)

```bash
python3 scripts/process_mail.py --rules '[
  {"name":"urgent","sender_pattern":"boss@","subject_pattern":"urgent","actions":["flag"],"priority":10},
  {"name":"tag_all","sender_pattern":".*","actions":["tag"],"tag":"processed","priority":0}
]'
```
