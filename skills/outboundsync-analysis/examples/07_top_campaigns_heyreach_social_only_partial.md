# Example 07: Top Campaigns By Replies — HeyReach Social Only (PARTIAL, strict)

- Intent ID: `top_campaigns_by_replies_30d`
- Date window: `last 30 days`
- CRM scope: `HubSpot`
- Platform scope: `HeyReach`

## User question
"Top campaigns by replies in the last 30 days."

## Available fields (sample)
- `os_last_campaign_name`
- `os_last_social_campaign_name`
- `os_last_reply_social_time`
- Missing: `os_last_email_campaign_name`, `os_last_reply_time`

## Compact preflight output
- `Intent:` top_campaigns_by_replies_30d
- `Mode:` strict
- `Verdict:` PARTIAL
- `Confidence:` low
- `Missing fields:` `os_last_reply_time`
- `Fallback plan:` rank campaigns by contact volume only; state missing reply-time limitation

## Example analysis output
- Partial strict result (email reply data unavailable for HeyReach):
  - Campaign ranking by contact volume only.
  - `LinkedIn Outreach Q1` -> 87 contacts
  - `VP Eng Social Touch` -> 54 contacts
- Limitation:
  - HeyReach does not sync email reply timestamps for this strict email-focused intent.
- Suggested handoff:
  - Re-run in exploratory mode with social summary intent (`heyreach_social_summary`) if social-only signals are the goal.
