---
name: poku
description: Makes outbound phone calls on the user's behalf using the Poku API via the `exec` tool. Example use cases include: when the user wants to call a restaurant, business, doctor's office, or any phone number to handle errands such as reservations, appointments, reminders, follow-ups, or bill disputes.
metadata: { "openclaw": { "required": { "env": ["POKU_API_KEY"] }, "primaryEnv": "POKU_API_KEY", "homepage": "https://pokulabs.com" } }
---

# Poku — Outbound Phone Calls

## Step 1: Resolve the Phone Number

- **Raw number** (e.g. `917-257-7580`) — strip formatting, prepend +1 (US default). Result: `+19172577580`.
- **Personal contact name** — ask the user for the number directly; do not guess.
- **Business name only** — use the search tool to find the number, then confirm with the user before proceeding.

The result of this step is the <normalized number> passed to Step 4.

---

## Step 2: Gather Details and Confirm Intent

Read `references/EXAMPLES.md` now. Each template shows exactly which details are required for that call type. Use the matching template to identify what is missing, then ask the user for only those details.

If no template matches the call type, ask the user for: the specific goal, any names or reference numbers needed.

Infer reasonable defaults and state them to the user. Do not ask for details already provided.

Before moving to step 3, you MUST share the plan and receive user confirmation.

> "I'm going to call [place] at [number] to [goal]. 
I'll mention I'm calling on behalf of you -- [user name]. 
If no one answers, I'll leave a voicemail: [one sentence]. 
Ok to proceed? If yes, I'll step away for a few minutes to make the call." 

**At this stage, gather any extra details that would help the call (e.g. address, insurance info, reference numbers).**

---

## Step 3: Draft the `message` Prompt

If a template in `references/EXAMPLES.md` matches the call type, use it as the base and fill in all placeholders with real values. Never leave a placeholder unfilled.

If no template matches, construct the message using this structure:
1. **Identity** — who the agent is and who they are calling on behalf of
2. **Goal** — the specific objective with branching logic for likely responses
3. **Voicemail script** — exact words to leave if no one answers

---

## Step 4: Place the Call

Use the `exec` tool to execute the curl command and place the call (always `background: false`, and explicitly set `yieldMs` (backgroundMs) to 300000).

```bash
curl -s -X POST \
  -H "Authorization: Bearer $POKU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "<drafted message from Step 3>", "to": "<normalized number>"}' \
  https://api.pokulabs.com/phone/call
```

Never retry while a request is pending — calls can stay open up to 5 minutes. If `POKU_API_KEY` is not set, stop and tell the user. For error codes, see `references/API.md`.

---

## Step 5: Report the Outcome

As soon as the tool call returns a "response" immediately inform the user. Example: "I just completed the call. I spoke to Kristin and she was able to help confirm the table for you for tomorrow at 7 pm."
Lead with the details that matter: confirmed date/time, name, reference number, next steps. If the response contains `"human did not respond"`, stop the tool call and report immediately. On any error, report the raw message and do not retry.

---

## References

- `references/EXAMPLES.md` — templates for each call type; read in Step 2
- `references/API.md` — full parameter reference and error codes; read in Step 4 if needed
