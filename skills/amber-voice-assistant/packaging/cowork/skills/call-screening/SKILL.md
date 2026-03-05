---
name: call-screening
description: >
  Screen incoming phone calls with an AI receptionist. Amber answers calls,
  identifies the caller, determines the purpose, takes a message, and
  delivers a structured summary. Use when the user wants to set up call
  screening, check screened call results, or customize screening behavior.
---

# Call Screening

Amber acts as an AI receptionist for inbound calls. She answers professionally,
gathers information, and delivers structured summaries — so you only pick up
calls that matter.

## Screening Flow

1. **Greeting** — Amber answers with a customizable greeting
2. **Identification** — Asks who's calling and what it's regarding
3. **Information gathering** — Collects caller name, callback number, message
4. **CRM lookup** — Checks if the caller is a known contact (auto-enriches context)
5. **Calendar check** — If the caller wants to book time, checks availability
6. **Summary delivery** — Sends a structured summary with all captured details

## MCP Tools

### start_screening
Enable inbound call screening on the configured Twilio number.

### stop_screening
Disable screening (calls ring through normally).

### get_screening_status
Check whether screening is currently active.

## Customization

The screening personality, greeting, and behavior are defined in AGENT.md.
Users can edit this file to:
- Change the assistant's name and personality
- Customize the greeting message
- Set business hours and after-hours behavior
- Define which callers should be put through vs. screened
- Add organization-specific context (company name, services, etc.)
