# Notion Recipe: Continuous User Research

Use this recipe when Notion is the operational source of truth for participant roster, diary entries, and weekly reports.

Default design:
- Timing mode default: `signal`
- Add event-driven captures for rare moments
- Add interval reflection for high-frequency behaviors

## 1) Notion workspace setup
Create these databases:
1. `Study Briefs`
2. `Participants`
3. `Diary Entries`
4. `Weekly Signals`

Recommended properties:

`Study Briefs`
- `study_id` (title)
- `goal` (text)
- `focus_type` (select)
- `timing_mode` (select)
- `reporting_period_days` (number)
- `privacy_redaction` (checkbox)

`Participants`
- `participant_code` (title)
- `email` (email)
- `timezone` (text)
- `segment` (multi-select)
- `consent_status` (select)
- `status` (select)

`Diary Entries`
- `entry_id` (title)
- `participant_code` (relation)
- `timestamp` (date/time)
- `mode` (select)
- `closed_answers` (json/text)
- `open_text` (text)
- `effort_minutes` (number)
- `attachments_meta` (json/text)

`Weekly Signals`
- `signal_id` (title)
- `study_id` (relation)
- `title` (text)
- `confidence` (select)
- `signal_payload` (json/text)
- `report_week` (date range)

## 2) Import participants (CSV or JSON)
Notion import options:
- Native CSV import into `Participants`.
- API `pages.create` calls for JSON records.

Required fields mapping:
- CSV/JSON `participant_code` -> Notion title
- `email` -> email property
- `timezone` -> text property
- `segment` -> multi-select
- `consent_status` default `pending`

## 3) Invite and consent flow
1. Send invite/consent using chosen channel (email/slack/discord/sms).
2. On explicit consent, update participant record:
- `consent_status=consented`
- `status=active`
- `consented_at=<timestamp>` (add property if desired)
3. Do not schedule prompts for non-consented participants.

## 4) Prompt orchestration
Signal default:
- Trigger one daily prompt in local window.
- Use timezone field in `Participants`.

Event-based capture:
- Product event webhook -> create prompt task for participant.

Interval-based capture:
- Fixed cadence job updates participant prompt queue.

Mixed-mode example:
- Daily signal prompt + event-triggered prompt + weekly reflection.

## 5) Entry capture and storage
Capture paths:
- Form link writes into `Diary Entries`.
- Channel messages parse into entry payload then write to Notion.

Normalization requirements:
- Map incoming records to `diary_entry.schema.json` fields.
- Always capture `effort_minutes`.
- Record attachment metadata only in Notion text/json field.
- Keep raw unredacted assets outside report pages.

## 6) Compliance monitoring
Compute daily status views:
- Missing entries
- Consecutive misses
- Reminder due
- Fallback prompt due

Recommended automations:
- If `missed_streak=1` -> send reminder.
- If `missed_streak=2` -> send fallback short-form prompt.
- If `missed_streak>=3` -> trigger dropout rescue workflow.

## 7) Weekly synthesis in Notion
Synthesis steps:
1. Filter `Diary Entries` by report window.
2. Tag entries by stage, blocker, motivation, and change-over-time.
3. Produce top 3 signal objects.
4. Validate each signal object against `signal.schema.json`.
5. Write weekly summary page and store machine-readable signal payloads in `Weekly Signals`.

Report quality bar:
- Max 1 page
- Top 3 signals only
- Each signal includes redacted evidence, confidence reason, and experiment plan

## 8) Optional Linear/GitHub handoff
When a signal is experiment-ready:
1. Create issue in Linear or GitHub.
2. Include hypothesis, method, metric, decision rule, timebox, and evidence references.
3. Link issue URL back to Notion `Weekly Signals` row.

## 9) Security checklist
- Restrict Notion integration token to required databases only.
- Do not store direct identifiers in `Weekly Signals` descriptions.
- Store raw multimedia in secure external storage; keep only controlled references in Notion.
- Enforce redaction before publishing weekly pages to broader audiences.
