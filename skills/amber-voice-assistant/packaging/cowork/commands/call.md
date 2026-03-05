---
name: call
description: Make an outbound phone call to a contact or phone number
arguments:
  - name: recipient
    description: Phone number (E.164 format) or contact name to call
    required: true
  - name: objective
    description: What you want to accomplish on the call (e.g., "book a table for 4 at 7pm", "confirm appointment")
    required: true
---

# /amber:call

Make an outbound phone call using the Amber voice bridge.

## Usage

```
/amber:call +14165551234 "Book a table for 4 at 7pm tonight"
/amber:call "Luigi's Restaurant" "Confirm our reservation for Saturday"
```

## What happens

1. If a contact name is given, look up the number via the CRM tool
2. Initiate the call via the `make_call` MCP tool
3. Amber handles the conversation autonomously, pursuing the stated objective
4. When the call ends, a full transcript and summary are returned

## Important

- Calls are real — they go through Twilio to actual phone numbers
- Always confirm the recipient and objective before placing the call
- If the objective requires payment or financial commitment, stop and confirm with the user first
