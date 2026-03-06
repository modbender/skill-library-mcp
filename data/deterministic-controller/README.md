# Deterministic Controller Starter Kit for OpenClaw

This is a doc-first orchestration pattern for OpenClaw:
- deterministic control cycle (heartbeat/poll/worker-event/manual)
- evidence-gated step completion
- project queue + auto-promotion
- optional Telegram control-plane one-liners
- auto-disarm when portfolio is complete

## Contents
- `templates/HEARTBEAT.md` — controller contract (template; optional Telegram logging via `<TELEGRAM_GROUP_ID>`)
- `templates/ACTIVITIES.md` — lean tracker + queue (template)
- `templates/SPRINT_TEMPLATE.md` — sprint plan template
- `docs/poll_cron_payload.txt` — canonical poll cron payload text (systemEvent)
- `docs/openclaw_config_snippets.md` — config snippets (models, Telegram allowlist, cross-context sends)
- `examples/setup_prompt.md` — “do this for me” setup prompt
- `examples/project_to_sprint_prompt.md` — prompt template to turn a loose spec into a sprint plan + queue row

## Quick Start (manual, step-by-step)

### Step 0 — Put this kit in your workspace
Copy the folder `packages/deterministic-controller-starterkit/` into your OpenClaw workspace.

### Step 1 — Install the two runtime files
Copy:
- `templates/HEARTBEAT.md` → `<WORKSPACE>/HEARTBEAT.md`
- `templates/ACTIVITIES.md` → `<WORKSPACE>/ACTIVITIES.md`
- `templates/SPRINT_TEMPLATE.md` → `<WORKSPACE>/SPRINT_TEMPLATE.md`

### Step 2 — Configure control-plane destination
Edit `<WORKSPACE>/HEARTBEAT.md`:
- Replace `<TELEGRAM_GROUP_ID>` with your Telegram group id.

If you do not want Telegram logs, you can instead change the Logging Contract to your preferred channel/tooling.

### Step 3 — Create required folders
Ensure these exist:
- `<WORKSPACE>/projects/`
- `<WORKSPACE>/docs/completed/sprints/`

### Step 4 — Create (or convert) a project sprint plan file
Create a sprint plan file at a stable path, e.g.:
- `projects/my-project/sprint-plan.md`

It must contain:
- project header
- DoD
- deterministic step table with Evidence/Output paths

### Step 5 — Add it to the queue
Edit `<WORKSPACE>/ACTIVITIES.md` → `## Project Queue (portfolio)`:
- add a new row with `Queue State=BACKLOG`
- set `Plan Path` to your sprint plan markdown path

### Step 6 — Create the poll cron job (disabled by default)
Create a cron job:
- name: `subagent-poll-every-3m`
- schedule: every 3 minutes
- sessionTarget: `main`
- payload.kind: `systemEvent`
- payload.text: contents of `docs/poll_cron_payload.txt` (replace `<WORKSPACE>`)

Leave it **disabled** until you explicitly start.

### Step 7 — Arm / Disarm protocol
Arm (start running):
1) Enable the poll cron job.
2) Ensure your heartbeat prompt is configured (this is required):
   - `agents.defaults.heartbeat.prompt` must start with `TRIGGER=HEARTBEAT_TICK` and instruct: `Execute HEARTBEAT.md exactly`.
   - See: `docs/openclaw_config_snippets.md` → "Heartbeat config (IMPORTANT)".
3) Set heartbeat cadence (`agents.defaults.heartbeat.every`) to something like `30m`.
4) Set the next project row to `ACTIVE` and import its plan (or let the controller promote/import when a prior sprint completes).

Disarm (stop running):
- Disable poll cron.
- Set heartbeat cadence `every=""`.

## Recommended: let OpenClaw do the setup
Use `examples/setup_prompt.md` (copy/paste) and fill in:
- `<WORKSPACE>`
- your `<TELEGRAM_GROUP_ID>`

## Turning a loose spec into a queued sprint
Use `examples/project_to_sprint_prompt.md`.

## Instance-specific values you must set
- `<WORKSPACE>` path
- `<TELEGRAM_GROUP_ID>`
- model ids (optional)

## Safety notes
- This kit is intentionally conservative: no external actions without explicit gates.
- Keep `BLOCKED` only for true human-action dependencies (credentials, approvals, purchases).
- Review `SECURITY.md` before arming automation (cron/heartbeat) or enabling Telegram logging.

## License
MIT (see `LICENSE`).
