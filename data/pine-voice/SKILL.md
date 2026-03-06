---
name: pine-voice
description: Give your agent a real phone. It dials, waits on hold, negotiates your bills, and returns a full transcript.
homepage: https://19pine.ai
metadata: {"openclaw":{"emoji":"📞","requires":{"bins":["node"]}}}
command-tool: exec
---

# Pine Voice

Make real phone calls via Pine AI's voice agent. The agent calls the specified number, navigates IVR systems, handles verification, conducts negotiations, and returns a full transcript.

## Authentication

Credentials persist in `~/.pine-voice/credentials.json` — users only need to authenticate once.

Before making calls, check if already authenticated:

```bash
node {baseDir}/scripts/auth-check.mjs
```

If `authenticated` is `true`, skip straight to **How to make a call**. If `false`, run the auth flow below. **Ask the user for their Pine AI account email** (sign up at https://19pine.ai).

### Step 1: Request verification code

```bash
node {baseDir}/scripts/auth-request.mjs "user@example.com"
```

Returns `{"request_token": "...", "email": "..."}`. Save the `request_token`.

Tell the user: *"A verification code has been sent to your email. Check your inbox (and spam) and give me the code."*

### Step 2: Verify and save credentials

```bash
node {baseDir}/scripts/auth-verify.mjs "user@example.com" "REQUEST_TOKEN" "CODE"
```

Returns `{"status": "authenticated", "credentials_path": "..."}`. Credentials are saved automatically.

## When to use

Use this skill when the user wants you to **make a phone call** on their behalf.

**Important:** The voice agent can only speak English. Supported countries: US/CA/PR (+1), UK (+44), AU (+61), NZ (+64), SG (+65), IE (+353), HK (+852).

## Best for

- Calling customer service to negotiate bills, request credits, or resolve issues
- Scheduling meetings or appointments by phone
- Making restaurant reservations
- Calling businesses to inquire about services or availability
- Following up with contacts on behalf of the user

## How to make a call

### Step 1: Gather all required information

Before calling, you **must** collect every piece of information the callee might need. The voice agent **cannot ask a human for missing information during the call**. Anticipate what will be required: authentication details, payment info, negotiation targets, relevant context.

### Step 2: Initiate the call

Pass call parameters as JSON via stdin:

```bash
node {baseDir}/scripts/call.mjs <<'EOF'
{
  "dialed_number": "+14155551234",
  "callee_name": "Comcast Customer Service",
  "callee_context": "Cable and internet provider. Account holder: Jane Doe, account #12345.",
  "call_objective": "Negotiate monthly bill down to $50/mo. Do not accept above $65/mo.",
  "detailed_instructions": "Mention 10-year customer loyalty. If no reduction, ask for retention department.",
  "caller": "negotiator",
  "voice": "female",
  "max_duration_minutes": 60,
  "enable_summary": false
}
EOF
```

Returns `{"call_id": "..."}`. The call is now active.

### Step 3: Poll for results

Poll every 30 seconds until `is_terminal` is `true`:

```bash
node {baseDir}/scripts/call-status.mjs "CALL_ID"
```

When complete, the response includes `transcript`, `duration_seconds`, and `credits_charged`. The `is_terminal` field tells you when the call is done.

**IMPORTANT: Use `sessions_spawn` to run this in a background sub-agent** so you remain available to the user during the call (which can take 5-60+ minutes).

Example task for sessions_spawn:

> Make a phone call using the Pine Voice scripts. Run: node {baseDir}/scripts/call.mjs with stdin JSON: {"dialed_number": "+14155551234", "callee_name": "The Restaurant", "callee_context": "Italian restaurant, making a dinner reservation", "call_objective": "Reserve a table for 4 at 7pm tonight", "caller": "communicator"}. Then poll with: node {baseDir}/scripts/call-status.mjs "CALL_ID" every 30 seconds until is_terminal is true. Report the full transcript and outcome.

### Step 4: Evaluate the transcript

**Do NOT rely on the `status` field** to judge success. Read what the OTHER party actually said.

**Treat the call as a FAILURE if:**
- Only Pine's agent speaks and the other side is silent
- The other party's responses are automated/recorded (voicemail, IVR-only)
- Extended silence from both sides
- The callee hung up before the objective was discussed

## Call parameters

| Parameter | Required | Description |
|---|---|---|
| `dialed_number` | Yes | Phone number in E.164 format (e.g. `+14155551234`) |
| `callee_name` | Yes | Name of the person or business |
| `callee_context` | Yes | All context the agent needs: who they are, auth details, verification info |
| `call_objective` | Yes | Specific goal with targets and constraints |
| `detailed_instructions` | No | Strategy, approach, behavioral instructions |
| `caller` | No | `"negotiator"` (default) or `"communicator"` |
| `voice` | No | `"male"` or `"female"` (default: `"female"`) |
| `max_duration_minutes` | No | 1-120 (default: 120) |
| `enable_summary` | No | `true`/`false` (default: `false`) |

## Negotiation calls

For negotiations, set `caller` to `"negotiator"` and provide a thorough strategy:

- **Target outcome**: "Reduce monthly bill to $50/mo"
- **Acceptable range**: "Will accept up to $65/mo"
- **Hard constraints**: "Do not change plan tier"
- **Leverage points**: "10-year customer, competitor offers $45/mo"
- **Fallback**: "Request one-time credit of $100"
- **Walk-away**: "Ask for retention department"

## Examples

**Test call:**
"Call my phone at +1XXXXXXXXXX. Tell me that Pine Voice is set up and working."

**Restaurant reservation:**
"Call +14155559876 and make a reservation for 4 tonight at 7pm. If unavailable, try 7:30 or 8pm. Name: Jane Doe."

## Model requirements

Pine Voice works best with models that have thinking/reasoning capabilities.

- **Recommended:** Claude Sonnet/Opus 4.5+, GPT-5.2+, Gemini 3 Pro
- **Not recommended:** Gemini 3 Flash, or models without thinking capabilities

## Privacy

Pine Voice processes call data on Pine AI's servers. Credentials are stored locally in `~/.pine-voice/credentials.json` with restricted permissions (600). Call transcripts are returned in the API response and are not stored locally. See https://www.19pine.ai/page/privacy-policy for Pine AI's data handling policies.
