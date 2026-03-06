# Slack Recipe: Continuous User Research

Use this recipe to run a diary study through Slack while keeping channels as delivery plumbing, not the research outcome.

Default design:
- Timing mode default: `signal`
- Add `event` prompts for rare/high-value moments
- Add `interval` prompts for routine/high-frequency behavior

## 1) Prerequisites
- Slack app with minimal scopes:
- `chat:write`
- `chat:write.public` (only if posting in channels)
- `users:read.email` (only if mapping by email)
- `commands` (optional for manual event logging shortcuts)
- `channels:history` and `groups:history` only if explicit ingestion from channels is needed
- Secure participant registry with consent status and timezone
- Storage target for diary entries (Notion/Airtable/Sheets)

## 2) Import participants (CSV or JSON)
Input fields:
- `participant_code`
- `email`
- `first_name`
- `timezone`
- `segment`
- `preferred_window`

CSV to JSON mapping example:
```json
{
  "participant_code": "P01",
  "email": "participant@example.test",
  "first_name": "Alex",
  "timezone": "America/New_York",
  "segment": "new_trial",
  "preferred_window": "09:00-20:00"
}
```

API-first import pattern:
- `POST /study/participants:bulkImport`
- Validate duplicates by `participant_code` and `email`
- Store `status=draft` until consent is explicit

## 3) Send invite + consent
1. Resolve Slack user by email when needed.
2. Open DM channel.
3. Send consent template from `prompts/consent_message.md`.
4. Parse explicit consent sentence.
5. Set participant status to `active` only after consent.

Slack API calls:
- `users.lookupByEmail`
- `conversations.open`
- `chat.postMessage`

Consent capture event payload:
```json
{
  "study_id": "onboarding-weekly-01",
  "participant_code": "P01",
  "consent_status": "consented",
  "consented_at": "2026-03-04T10:21:00Z",
  "consent_source": "slack_dm",
  "source_message_ts": "1772610060.123456"
}
```

## 4) Schedule prompts
Signal-based default:
- Use `chat.scheduleMessage` in participant local windows.
- One daily signal prompt plus reminder logic.

Event-based add-on:
- Trigger prompt when product telemetry posts an event webhook (for example `onboarding_exit_before_completion`).
- Send event prompt within 5-15 minutes after event.

Interval-based add-on:
- Fixed cadence (for example every evening at 19:00 local).

Mixed mode template:
- Daily signal prompt
- Event prompt on target events
- Weekly interval reflection prompt

## 5) Capture entries
Recommended methods:
- Slack message reply in DM thread.
- Slack shortcut form for structured closed answers.
- Optional media attachment upload in DM.

Entry normalization rules:
- Parse closed questions into structured fields.
- Parse open narrative into `open_text`.
- Save attachment metadata only (ID/reference), not raw URLs in reports.
- Capture self-reported `effort_minutes`.

## 6) Compliance monitoring
Track daily per participant:
- prompt sent
- entry received
- reminder sent
- fallback used
- missed streak

Reminder sequence:
1. Gentle reminder after first miss.
2. Fallback short-form prompt after second consecutive miss.
3. Dropout rescue message after third consecutive miss.

Fallback prompt example:
- "Quick 2-minute check-in: what happened today related to [scope], and what most influenced your next step?"

## 7) Store entries
Store raw entries separately from report artifacts.

Suggested data flow:
1. Raw Slack payload -> secure ingestion table.
2. Normalize to `diary_entry` object.
3. Persist to primary store (Notion/Airtable/Sheets).
4. Apply redaction before synthesis output.

## 8) Generate weekly report
Weekly synthesis pipeline:
1. Pull entries for reporting window.
2. Code/tag entries by behavior, stage, blocker, change-over-time.
3. Produce top 3 signals only.
4. Enforce report quality bar:
- max 1 page
- each signal includes redacted evidence
- confidence + reason
- one experiment plan per signal

Report output model:
- `signals[]` where each item validates against `schemas/signal.schema.json`

## 9) Optional ticket creation (Linear/GitHub)
Create only when recommendation is experiment-ready.

Linear GraphQL create issue payload (shape):
```json
{
  "title": "Experiment: Reduce Step-2 onboarding abandonment",
  "description": "Hypothesis, method, metric, decision rule, evidence refs",
  "labels": ["research-signal", "onboarding"],
  "teamId": "<linear-team-id>"
}
```

GitHub issue create payload (shape):
```json
{
  "title": "Experiment: Step-2 helper text A/B",
  "body": "## Hypothesis\n...\n## Metric\n...\n## Evidence\n- P03 ...",
  "labels": ["research", "experiment"]
}
```

## 10) Security checklist
- Redact identifiers in summaries.
- Keep raw attachments in restricted storage.
- Avoid posting participant PII in shared Slack channels.
- Restrict API tokens to least privilege.
- Log all outbound participant messages for audit.
