---
name: clawcall-ai
description: Run AI-powered outbound phone calls with Telnyx + Deepgram Voice Agent. Use when the user wants real phone outreach (follow-ups, confirmations, reminders, callbacks) with configurable personality, task context, model, and voice.
metadata: {"openclaw": {"emoji": "📞", "requires": {"bins": ["node", "npm"], "env": ["TELNYX_API_KEY", "TELNYX_CONNECTION_ID", "TELNYX_PHONE_NUMBER", "DEEPGRAM_API_KEY"]}, "primaryEnv": "TELNYX_API_KEY", "os": ["darwin", "linux"]}}
---

# ClawCall AI - Outbound Calls

Make realistic AI phone calls with natural conversation flow.

## IMPORTANT: Providing Context

When invoking this skill, you MUST provide rich, detailed context. The voice agent will NOT assume any information - it only uses what you explicitly provide.

### Required Information to Gather:
1. **Phone number** (E.164 format: +15551234567)
2. **Personality** - Who is the agent? Be specific:
   - BAD: "a receptionist"
   - GOOD: "Emma, a warm veterinary receptionist at Pawsitive Care Animal Hospital who has worked there for 5 years and knows all the vets by name"
3. **Task** - What is the call about? Include ALL relevant details:
   - BAD: "follow up about their pets"
   - GOOD: "Follow up with the Hendersons about Max (golden retriever, had knee surgery last week, needs post-op checkup, should be taking Rimadyl twice daily). Also remind them about the three hundred twenty-five dollar balance. Available slots: Wednesday 2pm, Thursday 10am or 4pm."

### Context Checklist:
- [ ] Names (caller's name, business name, contact's name)
- [ ] Dates and times (be specific: "Tuesday January 15th at 3:00 PM")
- [ ] Relevant details (appointment type, order number, service details)
- [ ] Fallback options if needed (reschedule times, alternative actions)
- [ ] Any reference numbers or IDs the agent might need

## Prerequisites

Install JavaScript dependencies (one-time):
```bash
npm --prefix {baseDir} install
```

If using `--ngrok`, `NGROK_AUTH_TOKEN` must be configured and the ngrok account must be verified.
If not using `--ngrok`, set `PUBLIC_WS_URL` to a reachable `wss://.../telnyx` endpoint.

## Commands

### Basic call:
```bash
node {baseDir}/telnyx_voice_agent.js --to "+15551234567" --ngrok \
  --personality "<detailed personality>" \
  --task "<detailed task with all context>"
```

### Full example (complex multi-topic call):
```bash
node {baseDir}/telnyx_voice_agent.js \
  --to "+15551234567" \
  --ngrok \
  --personality "Emma, a warm and experienced veterinary receptionist at Pawsitive Care Animal Hospital. You've worked there for 5 years and genuinely love animals. You know all the vets by name - Dr. Chen specializes in surgery, Dr. Patel handles general wellness, and Dr. Morrison is the exotic animals expert. You're organized but personable." \
  --task "Call to follow up with the Hendersons about their pets. They have three animals at your clinic: 1) Max, a 7-year-old golden retriever who had knee surgery last week - need to schedule his two-week post-op checkup and confirm he's been taking his pain medication (Rimadyl, twice daily with food). 2) Whiskers, a 12-year-old tabby cat due for her senior blood panel and dental cleaning - Dr. Patel recommended this at her last visit in October. 3) Pickles, their bearded dragon who needs his annual wellness exam. Also remind them that Max's surgery bill of eight hundred fifty dollars has a remaining balance of three hundred twenty-five dollars after insurance. Payment plans are available if needed. If they want to schedule, available slots this week: Wednesday 2pm, Thursday 10am or 4pm, Friday 9am." \
  --greeting "Hi there! This is Emma calling from Pawsitive Care Animal Hospital. Is this the Henderson household?"
```

### Follow-up calls with transcript context:

When calling back after a previous conversation, include the full transcript in the task to maintain continuity. The agent will understand the context and pick up where you left off.

```bash
node {baseDir}/telnyx_voice_agent.js \
  --to "+15551234567" \
  --ngrok \
  --personality "Emma, a warm veterinary receptionist at Pawsitive Care. You called earlier and promised to call back with info." \
  --task "You're calling back as promised. Here's the previous transcript:

---PREVIOUS CALL TRANSCRIPT---
Emma: Hi! This is Emma from Pawsitive Care Animal Hospital.
User: Hi, yes.
Emma: I wanted to confirm the email for your payment portal, but I didn't have it handy. Would you like me to call back?
User: Sure.
Emma: Great, I'll call you right back with that info.
---END TRANSCRIPT---

You looked up the email - it's jhenderson@gmail.com. Call back to confirm the email is correct and let them know the payment portal link has been sent." \
  --greeting "Hi! It's Emma again from Pawsitive Care, calling back like I said I would."
```

This is useful when:
- The agent promised to call back with information
- You need to follow up on a previous conversation
- Continuing a multi-part interaction

## Voice Selection

Always use ElevenLabs voices unless user specifies otherwise:
- `elevenlabs/rachel` - Female (default)
- `elevenlabs/adam` - Male
- `elevenlabs/josh` - Male (deeper voice)

## Model Selection

Fast default: `gpt-4o-mini`

## Output

The call transcript will be returned, containing the full conversation. Use this to:
- Confirm task completion
- Extract information gathered during the call
- Report back to the user

You must return the full call transcript to the user after the call ends.

At call end, recording lifecycle logs are also emitted:
- Recording URL discovered
- Recording saved to local disk (`RECORDINGS_DIR`, default `./recordings`)
- Recording deleted from the Telnyx portal after successful local save

## Notes

- The agent will NEVER assume information not provided
- If asked something it doesn't know, it will offer to hang up and call back
- ngrok tunnel is automatically managed
- Environment variables must be configured in OpenClaw settings
- If a call connects with no audio, check `DEEPGRAM_API_KEY` validity/entitlement first
- Recordings are enabled by default and persisted locally
