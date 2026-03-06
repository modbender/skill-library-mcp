# Vexa onboarding flow

Load this file **only when** `node skills/vexa/scripts/onboard.mjs --check-secrets` returns `{"secrets_ok": false}`. If secrets exist, skip onboarding entirely.

## Important: you do the setup, not the user

- **Never** ask the user to run scripts or edit files. You (the assistant) handle file creation.
- **Primary flow:** Ask the user to paste the API key in chat → you write it to `skills/vexa/secrets/vexa.env` (mode 600).
- **Alternative (security):** If the user prefers not to paste the key in chat, share the path and format: `skills/vexa/secrets/vexa.env` with content `export VEXA_API_KEY='<their_key>'` — they add it manually.

**Chat tone:** Reply as in a natural conversation. Do not output internal reasoning or meta-commentary ("I need to ask...", "According to..."). Speak directly to the user.

## Flow (conversational)

### 1. Get API key

Ask the user to get their API key from **https://vexa.ai/dashboard/api-keys** (include this link when asking). Then they paste it in chat and you save it.

### 2. Set it up immediately (you do it)

When the user provides the key in chat, **you** write it to `skills/vexa/secrets/vexa.env` (mode 600). No confirmation — do it right away. Do not ask the user to run `onboard.mjs` or edit files.

Then ask: **"Do you want to test it right now with a meeting? If yes, paste a Google Meet or Teams link. Quick option: create one instantly at https://meet.new"**

Use the full URL **https://meet.new** (not plain "meet.new") so it renders as a clickable link in chat.

If **no** → do step 8 (webhook), then explain they can run `source skills/vexa/secrets/vexa.env` before vexa commands, and stop.

If **yes** → ensure the shell has the key (e.g. `source skills/vexa/secrets/vexa.env`) and continue.

### 3. Create a test meeting

Ask the user to create a Google Meet or MS Teams meeting. Suggest the simplest way:

- **Google Meet:** Open **https://meet.new** in the browser — it creates a new meeting instantly. Copy the meeting URL.
- **MS Teams:** Use the Teams app to start a new meeting and copy the meeting URL.

Have the user paste the meeting URL.

### 4. Start the bot

Run:
```bash
node skills/vexa/scripts/vexa.mjs bots:start --meeting_url "<pasted_url>" --bot_name "Claw" --language en
```

Ensure `VEXA_API_KEY` is set (from env or `source skills/vexa/secrets/vexa.env`).

### 5. Test the transcript

Ask the user to **talk for a bit** (e.g. say their name and what they’re testing). Wait a short while, then fetch the transcript:

```bash
node skills/vexa/scripts/vexa.mjs transcripts:get --meeting_url "<same_url>"
```

Summarize what was transcribed so you both confirm it’s working.

### 6. Stop the bot

Always stop the bot when done. Hanging bots are bad practice:

```bash
node skills/vexa/scripts/vexa.mjs bots:stop --meeting_url "<same_url>"
```

Then do step 8 (webhook).

### 7. Key persistence

The key was saved in step 2. No further action needed.

### 8. Webhook (meeting finished → report) — **proactive**

**Always** check and offer webhook setup so that when a Vexa bot finishes a meeting, OpenClaw automatically receives the notification and creates the report. Do not wait for the user to ask.

**First check** if webhook is already configured:

```bash
node skills/vexa/scripts/onboard.mjs --check-webhook
```

- If output is `{"webhook_configured": true}` → hooks mapping exists. Still run step 9 (validate pipeline).
- If `{"webhook_configured": false}` → advise: *"I can set up the webhook so finished meetings auto-trigger reports. Want me to add it?"* Then **you** try to add the vexa webhook config to `openclaw.json`:
  - Set `hooks.transformsDir` to the workspace root (path to the workspace directory).
  - Add the vexa mapping under `hooks.mappings` — see `references/webhook-setup.md` for the exact JSON.

**If you cannot write to openclaw.json** (e.g. file not exposed, no write access): Tell the user that the webhook is **not** set up and that they need to add it manually — share `references/webhook-setup.md` and the exact JSON to add.

**If webhook config is added successfully:** Tell the user the hooks mapping is ready. **Webhook can only be set when the user has a public URL** — Vexa rejects internal URLs (localhost). Run `user:webhook:set` only if the user has a reachable public domain (e.g. cloudflared tunnel):

```bash
node skills/vexa/scripts/vexa.mjs user:webhook:set --webhook_url https://their-public-url/hooks/vexa
```

**Be explicit:** If the user has no public URL or the tunnel is not running, say: *"The webhook can't be set until you have a public URL reachable from the internet (e.g. via cloudflared). Until then, create reports manually with `vexa.mjs report`."* Point them to `references/webhook-setup.md` — section "Publishing the webhook (cloudflared tunnel)" — for steps to run the tunnel and set the Vexa URL.

### 9. Validate pipeline (after bot stopped)

**Proactively** run this to confirm the meeting finalized and a report was created:

```bash
node skills/vexa/scripts/onboard.mjs --validate-webhook --meeting_url "<same_url>"
```

This waits for the meeting to reach "completed" in Vexa (up to ~2 min), creates the report via ingest, and outputs `{"ok": true, "report_file": "..."}`. **If the real webhook was not received** (no public URL / tunnel down), it sends a **mock webhook** to the local hooks endpoint — this validates only the **local pipeline** (transform + report), not webhook delivery from Vexa. **Important (onboarding only):** Tell the user what to expect: *"Report created at [path]. The webhook needs a public URL (e.g. cloudflared) to work — until you have that, I'll create reports manually when you ask."* This sets expectations so the user knows why auto-reports may not fire.
