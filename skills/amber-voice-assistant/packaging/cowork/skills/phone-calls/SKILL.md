---
name: phone-calls
description: >
  Make and manage real phone calls through Twilio. Handles outbound calls
  with a stated objective, monitors call progress, and returns transcripts
  and summaries. Use when the user wants to call someone, check on a call,
  or review call history.
---

# Phone Calls

Amber can make and receive real phone calls via Twilio. This skill covers
the core telephony capabilities.

## MCP Tools

### make_call
Initiate an outbound phone call.
- `to` (string, required): Phone number in E.164 format (e.g., +14165551234)
- `objective` (string, required): What to accomplish on the call
- `mode` (string): "conversation" (default) or "message" (one-way delivery)

### get_call_status
Check the status of an active or recent call.
- `callId` (string, required): The call ID returned by make_call

### end_call
Terminate an active call.
- `callId` (string, required): The call ID to end

### get_call_history
Retrieve recent call logs with transcripts.
- `filter` (string): "all", "inbound", "outbound", "missed"
- `limit` (number): Number of calls to return (default: 10)

## Guidelines

- Always confirm the recipient number and call objective with the user before dialing
- If the objective involves payment, deposits, or financial commitments, explicitly ask the user for approval first
- After each call, provide a summary including: who was called, outcome, key information exchanged, and caller sentiment
- For outbound calls, Amber pursues the stated objective autonomously — she's not just reading a script
- Calls have real-world consequences. Treat every call as if you're representing the user professionally
