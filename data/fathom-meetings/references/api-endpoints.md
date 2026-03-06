# Fathom API Endpoints

Base: `https://api.fathom.ai/external/v1`

## GET /meetings

List meetings with optional filters.

| Param | Type | Description |
|-------|------|-------------|
| limit | int | 1-100 (default 10) |
| cursor | string | Pagination cursor from previous response |
| created_after | ISO 8601 | Filter by creation date |
| created_before | ISO 8601 | Filter by creation date |
| recorded_by[] | email | Filter by recorder |
| include_transcript | bool | Include full transcript |
| include_action_items | bool | Include AI action items |
| include_summary | bool | Include AI summary |

## Response Fields

### Meeting Object
- `title` — Fathom-generated title
- `meeting_title` — Calendar event title
- `url` — Link to Fathom call page
- `share_url` — Public shareable link
- `recording_id` — Unique recording ID
- `recording_start_time` / `recording_end_time` — Actual recording times
- `scheduled_start_time` / `scheduled_end_time` — Calendar event times
- `transcript` — Full transcript (if requested)
- `transcript_language` — e.g. "en"
- `default_summary` — AI-generated summary (if requested)
- `action_items` — AI-generated action items (if requested)
- `calendar_invitees` — Array of {name, email, email_domain, is_external, matched_speaker_display_name}
- `calendar_invitees_domains_type` — "internal_only" | "one_or_more_external"
- `recorded_by` — {name, email, email_domain, team}
- `crm_matches` — CRM integration matches (if configured)

### Pagination
- `next_cursor` — Pass as `cursor` param for next page
- `limit` — Echoed back
