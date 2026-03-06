# Example 03: Fastest Replies After First Send (PARTIAL, strict)

- Intent ID: `fastest_replies_after_first_send`
- Date window: `last 30 days`
- CRM scope: `HubSpot`
- Platform scope: `Smartlead`

## User question
"Which campaigns get replies fastest after first send?"

## Available fields (sample)
- `os_last_campaign_name`
- `os_last_reply_time`
- Missing: `os_last_sent_time`

## Compact preflight output
- `Intent:` fastest_replies_after_first_send
- `Mode:` strict
- `Verdict:` PARTIAL
- `Confidence:` medium
- `Missing fields:` `os_last_sent_time`
- `Fallback plan:` replace latency analysis with reply volume and reply recency

## Example analysis output
- Partial result (latency unavailable):
  - `Security Buyers Q1` -> highest reply volume in window
  - `Operations Leaders` -> most recent reply activity trend
- Limitation:
  - Cannot compute send-to-reply latency without `os_last_sent_time`.
