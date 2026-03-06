# Example 08: HeyReach Social Summary (EXPERIMENTAL_LIMITED, exploratory)

- Exploratory Path ID: `heyreach_social_summary`
- Date window: `last 30 days`
- CRM scope: `HubSpot`
- Platform scope: `HeyReach`

## User question
"Summarize HeyReach social campaign performance and recent social replies."

## Available fields (sample)
- `os_last_social_campaign_name`
- `os_last_reply_social_time`
- `os_last_sent_social_time`
- `os_last_campaign_name`

## Compact preflight output
- `Intent:` heyreach_social_summary
- `Mode:` exploratory
- `Verdict:` EXPERIMENTAL_LIMITED
- `Confidence:` high
- `Missing fields:` none
- `Fallback plan:` none

## Example analysis output
- `Mode: exploratory`
- Campaign volume summary:
  - `LinkedIn Outreach Q1` -> 87 contacts
  - `VP Eng Social Touch` -> 54 contacts
- Social reply recency summary:
  - Latest social reply activity concentrated in `LinkedIn Outreach Q1`
- Activity trend direction:
  - `up` in the last 14 days vs prior 14 days
- `Observed Signals Used:` `os_last_social_campaign_name`, `os_last_reply_social_time`, `os_last_sent_social_time`
- `Missing Signals:` none
- `Non-causal caveat:` This is best-effort exploratory analysis and does not prove causality or strict email-reply performance.
