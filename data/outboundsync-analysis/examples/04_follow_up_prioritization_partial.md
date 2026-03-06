# Example 04: Follow-Up Prioritization (PARTIAL, strict)

- Intent ID: `follow_up_prioritization`
- Date window: `last 14 days`
- CRM scope: `HubSpot`
- Platform scope: `Instantly`

## User question
"Who should we prioritize for follow-up this week?"

## Available fields (sample)
- `os_last_open_time`
- `os_last_reply_time`
- Missing: `os_last_link_click_time`

## Compact preflight output
- `Intent:` follow_up_prioritization
- `Mode:` strict
- `Verdict:` PARTIAL
- `Confidence:` medium
- `Missing fields:` `os_last_link_click_time`
- `Fallback plan:` prioritize by opens plus recency; exclude recent repliers

## Example analysis output
- Priority follow-up segments:
  1. Opened recently, no recent reply
  2. Multiple recent opens, no click data available
- Limitation:
  - Click behavior unavailable; ranking uses opens + recency only.
