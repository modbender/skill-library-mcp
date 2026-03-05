# OpenClaw Phone Receipt Setup (ElevenLabs + Twilio)

Use this guide to enable automatic phone callback receipts for OpenClaw.

## Required parameters

### Twilio
- `TWILIO_ACCOUNT_SID` (example: `AC...`)
- `TWILIO_AUTH_TOKEN`
- `TWILIO_PHONE_NUMBER` (example: `+1812...`)
- Optional: `TWILIO_PHONE_NUMBER_SID` (example: `PN...`)

### ElevenLabs Agents
- `ELEVENLABS_API_KEY` (must include ConvAI scope, at least `convai_read`)
- `ELEVENLABS_AGENT_ID` (example: `agent_...`)
- `ELEVENLABS_OUTBOUND_PHONE_ID` (example: `phnum_...`)
- `TO_NUMBER` (target number in E.164, example: `+639178688896`)

## End-to-end setup flow

### 1) Buy a voice-enabled number in Twilio
Twilio Console -> Phone Numbers -> Buy a number.

### 2) Verify your target number (Trial accounts)
Twilio Console -> Phone Numbers -> Verified Caller IDs.

If not verified, outbound calls fail with:
`The number ... is unverified. Trial accounts may only make calls to verified numbers.`

### 3) Import number into ElevenLabs
ElevenLabs -> Agents Platform -> Phone Numbers -> Import number -> From Twilio.

Fill:
- Label
- Twilio Number (`+1...`)
- Twilio Account SID (`AC...`)
- Twilio Auth Token

After import, copy the generated `Outbound Phone ID` (`phnum_...`).

### 4) Configure Agent
ElevenLabs -> Agents -> select your agent.

Recommended:
- Set First Message
- Select a Primary voice
- Ensure Text-only mode is disabled for voice calls
- Publish changes

### 5) Configure OpenClaw env file

```bash
cp /Users/huang/.openclaw/workspace/skills/openclaw-phone-receipt/references/env-example.txt \
   /Users/huang/.openclaw/workspace/.env.elevenlabs-call
```

Set:
- `ELEVENLABS_API_KEY`
- `ELEVENLABS_AGENT_ID`
- `ELEVENLABS_OUTBOUND_PHONE_ID`
- `TO_NUMBER`

### 6) Test outbound call

```bash
bash /Users/huang/.openclaw/workspace/skills/openclaw-phone-receipt/scripts/trigger_call.sh
```

Success example:
`[OK] outbound call initiated, conversation_id=conv_...`

## Common pitfalls

1. Number format must be E.164
- Wrong: `0063...`
- Correct: `+63...`

2. Twilio Trial number not verified
- Calls to unverified targets fail

3. Missing ElevenLabs key scope
- Missing `convai_read` causes API failure

4. Agent in Text-only mode
- Call connects but no voice output

5. Not publishing agent changes
- Agent edits only take effect after Publish

## Runtime policy (default)

- Call only when task fails or is marked urgent
- Normal successful tasks send Telegram text summary only
- Toggle commands: `phone-receipt=on` / `phone-receipt=off`
