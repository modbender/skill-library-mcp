---
name: vexa
description: "Send Vexa bots to meetings and operate transcript workflows end-to-end (during and after meetings): parse meeting links, request/stop bots, read live/final transcripts, create basic meeting reports, set webhook delivery, and enrich meeting metadata. Use when a user drops a Google Meet/Teams link, asks to auto-join meetings from calendar events, or needs transcript retrieval/summarization/knowledge updates from Vexa. After a meeting ends, create a report with meeting info, transcript, and placeholders for summary/decisions/action items. Treat transcript purge (meeting delete) as destructive and require explicit confirmation."
---

## Chat-oriented interactions

Speak **directly to the user** as in a natural chat. Do not output internal reasoning, plan summaries, or procedural notes ("I need to...", "According to the skill...", "I will inform..."). Reply with only what you would say to the user — conversational, warm, and to the point.

Use the bundled CLI:
- `node skills/vexa/scripts/vexa.mjs ...`
- `node skills/vexa/scripts/onboard.mjs ...`
- `node skills/vexa/scripts/ingest.mjs ...`
- `node skills/vexa/scripts/audit.mjs`

## Environment

Set for the OpenClaw process (or shell):
- `VEXA_API_KEY` (required)
- `VEXA_BASE_URL` (optional, default `https://api.cloud.vexa.ai`)

## Secrets-first check (before any onboarding)

**Always check first:** `node skills/vexa/scripts/onboard.mjs --check-secrets`

- If output is `{"secrets_ok": true}` → secrets exist. Skip onboarding. Use normal flows.
- If output is `{"secrets_ok": false}` → run onboarding. Load `references/onboarding-flow.md`.

**Webhook — proactive setup:** Whenever secrets exist and you're working with Vexa, run `node skills/vexa/scripts/onboard.mjs --check-webhook`. If `webhook_configured` is false, advise adding the vexa mapping (see `references/webhook-setup.md`). For onboarding-only details (webhook requirements, pipeline validation, mock webhook), load `references/onboarding-flow.md`.

**When secrets are missing:** Ask them to get their key from https://vexa.ai/dashboard/api-keys and paste it in chat — you write it to `skills/vexa/secrets/vexa.env`. Alternatively, share the path and format so they can add it manually (better for security if they prefer not to paste the key).

**Secrets location:** `skills/vexa/secrets/` holds `vexa.env` (API key) and `vexa-state.json`. This dir is gitignored. When publishing the skill to ClawHub, ensure `secrets/` is excluded.

Non-interactive (for scripting): `onboard.mjs --api_key <key> --persist yes --meeting_url "<url>" --language en --wait_seconds 60 --poll_every_seconds 10`

## Quick workflows

### 1) User drops a meeting link → send bot

- After successfully sending the bot, **proactively** run `--check-webhook`. If not configured, offer to set it up so finished meetings auto-trigger reports.
- Parse/normalize link (or pass explicit ID):
  - `node skills/vexa/scripts/vexa.mjs parse:meeting-url --meeting_url "https://meet.google.com/abc-defg-hij"`
- Start bot directly from URL:
  - `node skills/vexa/scripts/vexa.mjs bots:start --meeting_url "https://meet.google.com/abc-defg-hij" --bot_name "Claw" --language en`
  - `node skills/vexa/scripts/vexa.mjs bots:start --meeting_url "https://teams.live.com/meet/9387167464734?p=qxJanYOcdjN4d6UlGa" --bot_name "Claw" --language en`

### 2) Start bot from calendar meeting links

If a calendar tool/skill is available (for example `gog`):
1. Fetch upcoming events.
2. Extract meeting links (Google Meet/Teams).
3. For each selected event, call `bots:start --meeting_url ...`.
4. Optionally save event title into Vexa metadata:
   - `meetings:update --name "<calendar title>" --notes "source: calendar"`

### 3) Read transcript during meeting or after meeting

- Poll current transcript:
  - `node skills/vexa/scripts/vexa.mjs transcripts:get --platform google_meet --native_meeting_id abc-defg-hij`
- For near real-time streaming, use Vexa WebSocket API (see `references/user-api-guide-notes.md` for endpoints and notes).
- After transcript is available, summarize and store key updates.

### 4) Stop bot

- `node skills/vexa/scripts/vexa.mjs bots:stop --meeting_url "<url>"`

### 5) Create meeting report (after meeting finished)

After stopping the bot (or once the meeting has ended and transcript is finalized), create a basic meeting report:

- `node skills/vexa/scripts/vexa.mjs report --meeting_url "https://meet.google.com/abc-defg-hij"`
- or `node skills/vexa/scripts/ingest.mjs --meeting_url "<url>"`

Writes to `memory/meetings/YYYY-MM-DD-<slug>.md` with: meeting info, summary placeholders, key decisions, action items, and full transcript.

## Core commands

- Bot status:
  - `node skills/vexa/scripts/vexa.mjs bots:status`
- Request bot (explicit fields):
  - `node skills/vexa/scripts/vexa.mjs bots:start --platform google_meet --native_meeting_id abc-defg-hij --bot_name "Claw" --language en`
- Update active bot language:
  - `node skills/vexa/scripts/vexa.mjs bots:config:update --platform google_meet --native_meeting_id abc-defg-hij --language es`
- List meetings:
  - `node skills/vexa/scripts/vexa.mjs meetings:list`
- Update metadata (title/participants/languages/notes):
  - `node skills/vexa/scripts/vexa.mjs meetings:update --platform google_meet --native_meeting_id abc-defg-hij --name "Weekly Product Sync" --participants "Alice,Bob" --languages "en" --notes "Action items captured"`
- Generate share URL:
  - `node skills/vexa/scripts/vexa.mjs transcripts:share --platform google_meet --native_meeting_id abc-defg-hij --ttl_seconds 3600`
- Set Vexa user webhook URL:
  - `node skills/vexa/scripts/vexa.mjs user:webhook:set --webhook_url https://your-public-url/hooks/vexa`

## Webhook (meeting finished → report)

When Vexa sends a "meeting finished" webhook, the transform (`scripts/vexa-transform.mjs`) instructs the agent to create a report. See `references/webhook-setup.md` for hooks mapping config. Requires `hooks.transformsDir` = workspace root and `transform.module` = `skills/vexa/scripts/vexa-transform.mjs`.

## OpenClaw ingestion helpers

- Create basic meeting report (meeting info, transcript, placeholders for summary/decisions/actions):
  - `node skills/vexa/scripts/vexa.mjs report --meeting_url "<url>"`
  - `node skills/vexa/scripts/ingest.mjs --meeting_url "<url>"` (or `--platform` + `--native_meeting_id`)
- Audit meetings for likely test calls / cleanup candidates:
  - `node skills/vexa/scripts/audit.mjs`

## Platform rules

- Supported: `google_meet`, `teams`
- Teams `native_meeting_id` must be numeric ID only.
- Teams bot join requires passcode (from `?p=` in Teams URL).

## Deletion safety (strict)

`DELETE /meetings/{platform}/{native_meeting_id}` purges transcripts and anonymizes data.

Rules:
1. Never call delete without explicit user request for that exact meeting.
2. Verify `platform` + `native_meeting_id` first.
3. Prefer non-destructive cleanup (`meetings:update`) whenever possible.
4. Require guard flag:
   - `node skills/vexa/scripts/vexa.mjs meetings:delete --platform google_meet --native_meeting_id abc-defg-hij --confirm DELETE`
