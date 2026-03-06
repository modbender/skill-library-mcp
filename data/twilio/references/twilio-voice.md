# Voice (Calls API)

## 1) Create a call
- Endpoint: `POST /2010-04-01/Accounts/{AccountSid}/Calls.json`
- Required fields typically include `To`, `From`, and `Url` (TwiML instructions).

## 2) Call control
- Update or hang up via the Call resource.
- Use status callbacks for call lifecycle events.

## 3) Rate limits
- Calls are subject to CPS limits; plan concurrency accordingly.
