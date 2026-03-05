# Example 06: Deliverability Issues (PARTIAL, strict)

- Intent ID: `deliverability_unsubscribes_bounces`
- Date window: `last 30 days`
- CRM scope: `HubSpot`
- Platform scope: `Smartlead`

## User question
"What are our unsubscribe and bounce issues?"

## Available fields (sample)
- `os_last_bounce_time`
- `os_last_unsubscribe_time`
- `os_last_sent_time`
- Missing: `os_last_sent_address`

## Compact preflight output
- `Intent:` deliverability_unsubscribes_bounces
- `Mode:` strict
- `Verdict:` PARTIAL
- `Confidence:` medium
- `Missing fields:` `os_last_sent_address`
- `Fallback plan:` campaign/global deliverability analysis only

## Example analysis output
- Partial deliverability view:
  - Bounce and unsubscribe trends by campaign/time window
  - No sender-address breakdown available
- Limitation:
  - `os_last_sent_address` missing, so sender-level diagnosis is unavailable.
