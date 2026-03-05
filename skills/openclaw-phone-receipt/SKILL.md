---
name: openclaw-phone-receipt
description: Trigger and manage OpenClaw outbound phone receipts via ElevenLabs+Twilio for task completion/failure notifications. Use when user asks to call them after finishing/failing a task, asks to enable/disable fixed command toggles ("phone-receipt=on/off"), asks to test call quality, or asks to persist phone receipt behavior across sessions.
---

# OpenClaw Phone Receipt

Use this skill to manage phone callback notifications.

## Commands to honor

- `phone-receipt=on` → enable phone receipt policy
- `phone-receipt=off` → disable phone receipt policy

State file:
- `memory/phone-receipt-state.json`

## Default behavior

1. If user asks for callback on completion/failure, set `enabled=true`.
2. Default policy is now:
   - `policy.onComplete=false`
   - `policy.onFailure=true`
   - `policy.onUrgent=true`
3. Persist state to `memory/phone-receipt-state.json`.
4. For immediate test call, run `scripts/trigger_call.sh`.

## Delivery strategy (must follow)

- Phone call only when:
  1) task failed, OR
  2) user explicitly marks task as urgent (e.g., “urgent/high-priority”).
- All other non-urgent successful tasks:
  - send Telegram text summary only (no phone call).

When phone is not required by policy, use message delivery (Telegram text) as default receipt path.

## Tools/scripts

- Toggle state:
  - `python3 skills/openclaw-phone-receipt/scripts/set_phone_receipt_state.py on`
  - `python3 skills/openclaw-phone-receipt/scripts/set_phone_receipt_state.py off`
- Trigger call now:
  - `bash skills/openclaw-phone-receipt/scripts/trigger_call.sh`

## Call prerequisites

Requires `.env.elevenlabs-call` with:
- `ELEVENLABS_AGENT_ID`
- `ELEVENLABS_OUTBOUND_PHONE_ID`
- `TO_NUMBER`

`ELEVENLABS_API_KEY` can come from shell env or `.env.elevenlabs-call`.

For full setup (Twilio purchase/verify, ElevenLabs import, key scopes, troubleshooting), read:
- `references/setup.md`

For ClawHub upload checklist (version/changelog/size requirements), read:
- `references/publish-clawhub.md`

## Failure handling

If call fails, return concise root cause and next action:
- unverified target number (Twilio trial)
- missing ConvAI scope (`convai_read`)
- missing agent/phone ids

