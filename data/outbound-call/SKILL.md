---
name: outbound-call
description: Make outbound phone calls via ElevenLabs voice agent and Twilio
metadata:
  clawdbot:
    requires:
      env:
        - ELEVENLABS_API_KEY
        - ELEVENLABS_AGENT_ID
        - ELEVENLABS_PHONE_NUMBER_ID
    primaryEnv: ELEVENLABS_API_KEY
---

# Outbound Call

> **Source code and setup guide:** [github.com/humanjesse/hostinger-openclaw-guides](https://github.com/humanjesse/hostinger-openclaw-guides)

Place outbound phone calls using the ElevenLabs voice agent with Twilio. The voice agent on the call uses OpenClaw as its brain — same as inbound calls.

## When to use

When the user asks you to:
- Call someone or phone someone
- Make a phone call
- Dial a number
- Ring someone
- Place a call to a number

## How to use

Run the call script with a phone number in E.164 format:

```bash
python3 skills/outbound-call/call.py +1XXXXXXXXXX
```

With an optional custom first message (what the agent says when the recipient picks up):

```bash
python3 skills/outbound-call/call.py +1XXXXXXXXXX "Hi John, I'm calling about your appointment tomorrow."
```

With optional call context (passed as a dynamic variable to the agent):

```bash
python3 skills/outbound-call/call.py +1XXXXXXXXXX "Hi, this is a quick follow-up call." "Customer requested callback about billing issue #4521"
```

## Phone number format

- US numbers: +1 followed by 10 digits, e.g., +15551234567
- If the user gives a number like 555-123-4567 or (555) 123-4567, reformat it to +15551234567
- Always confirm the formatted number with the user before placing the call

## Rules

- ALWAYS confirm the phone number with the user before placing a call
- NEVER place a call without explicit user consent
- Report the result back to the user (conversation ID on success, error details on failure)
- If the call fails, explain the error and suggest fixes
