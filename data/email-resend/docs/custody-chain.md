# Email Custody Chain Design

## Overview

Track the full lineage from original email → notification → all interactions.

## Data Structure (DAG)

```json
{
  "email_id": "resend-uuid-123",
  "email_metadata": {
    "subject": "Original Subject",
    "from": "sender@example.com",
    "created_at": "2026-02-21T00:00:00Z"
  },
  "notification_msg_id": "1234",
  "chain": {
    "1234": {
      "type": "notification",
      "email_id": "resend-uuid-123",
      "timestamp": "2026-02-21T00:00:01Z",
      "parent": null
    },
    "1235": {
      "type": "user_reply",
      "content": "Yes, Thu 4pm?",
      "timestamp": "2026-02-21T00:05:00Z",
      "parent": "1234"
    },
    "1236": {
      "type": "preview",
      "timestamp": "2026-02-21T00:05:01Z",
      "parent": "1235"
    },
    "1237": {
      "type": "user_confirm",
      "timestamp": "2026-02-21T00:06:00Z",
      "parent": "1236"
    },
    "1238": {
      "type": "sent",
      "timestamp": "2026-02-21T00:06:01Z",
      "parent": "1237"
    }
  },
  "status": "completed"
}
```

## Lookup Functions

### Given notification message ID → Email ID
```
chain[msg_id] → ... → root → email_id
```

### Given Email ID → Full Chain
```
email_chains[email_id] → full DAG
```

## Usage

1. **Inbound email** → Create chain node (notification)
2. **User replies** → Add node, link to parent
3. **Preview** → Add node
4. **User confirms** → Add node
5. **Sent** → Mark chain completed

## Files

- `memory/email-custody-chain.json` — All chains indexed by email_id
- `memory/email-msg-to-chain.json` — notification msg_id → chain key
