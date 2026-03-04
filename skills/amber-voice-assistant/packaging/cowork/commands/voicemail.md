---
name: voicemail
description: Check voicemails and messages left by callers
arguments:
  - name: action
    description: "list" to see all, "unread" for new only, "play <id>" for a specific message
    required: false
---

# /amber:voicemail

Check messages left by callers during screening.

## Usage

```
/amber:voicemail
/amber:voicemail unread
```

## Output

For each message:
- Caller name and number
- Date and time
- Message summary
- Full transcript
- Caller sentiment (friendly, urgent, neutral, etc.)
