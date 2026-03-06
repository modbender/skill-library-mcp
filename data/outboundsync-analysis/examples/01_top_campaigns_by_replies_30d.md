# Example 01: Top Campaigns By Replies (SUPPORTED, strict)

- Intent ID: `top_campaigns_by_replies_30d`
- Date window: `last 30 days`
- CRM scope: `HubSpot`
- Platform scope: `Instantly, Smartlead`

## User question
"Top campaigns by replies in the last 30 days."

## Available fields (sample)
- `os_last_email_campaign_name`
- `os_last_campaign_name`
- `os_last_reply_time`
- `os_last_sent_time`

## Compact preflight output
- `Intent:` top_campaigns_by_replies_30d
- `Mode:` strict
- `Verdict:` SUPPORTED
- `Confidence:` high
- `Missing fields:` none
- `Fallback plan:` none

## Example analysis output
- Top campaigns by reply count (30d):
  1. `Q1 Outbound - VP Sales` -> 42 replies
  2. `Demand Gen Directors` -> 31 replies
  3. `Ecom Founders` -> 19 replies
- Notes:
  - Analysis uses observed reply timestamps only.
  - No inferred replies were added.
