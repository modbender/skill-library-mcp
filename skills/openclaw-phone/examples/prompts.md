# Example Prompts

## Start a Call

User:
"Call +46700000000 and confirm my appointment for Tuesday at 2pm."

Expected behavior:
- Resolve API key from `CALLMYCALL_API_KEY`, then `~/.openclaw/openclaw.json` (`skills.openclaw-phone.apiKey`), and only then prompt once with confirmation before persisting.
- Use layered gating to collect any missing details (language, call brief).
- Present a review summary and ask for confirmation.
- Call `POST /v1/start-call` with `phone_number` and `task`.
- Save the returned `sid` in `recent_calls`.
- Confirm in chat with call ID.

---

## List Recent Calls

User:
"Show my recent calls."

Expected behavior:
- Read `recent_calls`.
- Optionally refresh status via `GET /v1/calls/:callId`.
- Return numbered list.

---

## End a Call

User:
"End call 1."

Expected behavior:
- Map list index to `callSid`.
- Call `POST /v1/end-call`.
- Confirm success.

---

## Fetch Results

User:
"Show results for call 2."

Expected behavior:
- Call `GET /v1/calls/:callId`.
- Call `GET /v1/calls/:callId/transcripts/stream` if needed.
- If recording exists, fetch `GET /v1/calls/:callSid/recording`.
- Summarize result + transcript excerpt + recording URL.
