# Email Recipe: Continuous User Research

Use this recipe when participants are best reached by email and diary replies can be captured via structured reply formats or linked forms.

Default design:
- Timing mode default: `signal`
- Use `event` triggers for rare/high-value moments
- Use `interval` prompts for routine behavior

## 1) Prerequisites
- Email provider API integration (for example SendGrid, SES, Postmark)
- Inbound reply webhook handling
- Participant registry with consent and timezone fields
- Entry storage destination (Notion/Airtable/Sheets)

## 2) Import participants (CSV or JSON)
Required import fields:
- `participant_code`
- `email`
- `first_name`
- `timezone`
- `segment`
- `preferred_window`

Bulk import endpoint example:
- `POST /study/participants:bulkImport`

Validation rules:
- Unique `participant_code`
- Valid email format
- `status=draft` until consent

## 3) Send invites and consent
1. Send invite/consent message using template in `prompts/consent_message.md`.
2. Require explicit consent confirmation sentence in reply.
3. Mark participant active only on explicit consent.

Outbound payload shape:
```json
{
  "to": "participant@example.test",
  "template": "consent_message",
  "variables": {
    "first_name": "Alex",
    "study_days": 7,
    "min_entries_required": 5,
    "max_entries_allowed": 8
  }
}
```

Inbound consent event shape:
```json
{
  "participant_code": "P01",
  "consent_status": "consented",
  "consented_at": "2026-03-04T10:25:00Z",
  "source": "email_reply",
  "message_id": "<provider-message-id>"
}
```

## 4) Prompt scheduling
Signal-based default:
- Daily check-in email in participant local window.

Event-based option:
- Trigger an immediate check-in email after product webhook events.

Interval-based option:
- Fixed cadence (daily/every 2 days/weekly reflection).

Mixed-mode option:
- Daily signal + event trigger + weekly reflection.

## 5) Capture entries
Recommended pattern:
- Send structured prompt with compact response format.
- Accept freeform narrative plus optional rating lines.
- Parse inbound emails into `closed_answers` and `open_text`.

Example reply format block for participants:
- Frequency: [0|1|2-3|4+]
- Duration: [<5|5-15|16-30|30+]
- Friction: [1-5]
- What happened today:
- Why it happened:
- Effort minutes: [number]

Attachment handling:
- Accept screenshot/photo/audio attachments.
- Store metadata only in analysis outputs.
- Keep raw files in restricted storage.

## 6) Compliance monitoring
Track per participant:
- prompts_sent
- entries_received
- reminders_sent
- fallback_used
- missed_streak

Reminder and recovery sequence:
1. Reminder after first miss.
2. Reduced-effort fallback prompt after second miss.
3. Dropout rescue after third miss.

Fallback prompt (email-safe):
- "Short 2-minute check-in: what happened, what mattered most, and what did you do next?"

## 7) Store entries
Data flow:
1. Inbound email webhook payload -> secure ingest log.
2. Parse to `diary_entry` shape.
3. Persist raw and normalized records separately.
4. Redact before synthesis and report generation.

## 8) Generate weekly report
Report process:
1. Pull entries in reporting window.
2. Code by themes, stages, blockers, and changes over time.
3. Produce exactly 3 signals.
4. Require each signal to include evidence, confidence + reason, and one experiment plan.
5. Keep report to max 1 page.

## 9) Optional ticket sync
Linear/GitHub ticket creation rules:
- Create ticket only for high-confidence or medium-confidence experiment-ready recommendations.
- Include evidence references and decision rule in issue body.
- Label with `research-signal` and scope tag.

## 10) Security checklist
- Avoid sending sensitive participant details in shared inboxes.
- Use dedicated sender identities per study workspace.
- Encrypt raw response storage at rest.
- Remove direct identifiers from weekly report output.
- Do not expose provider API secrets in prompts or logs.
