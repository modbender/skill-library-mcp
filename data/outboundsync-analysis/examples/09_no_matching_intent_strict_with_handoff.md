# Example 09: No Matching Strict Intent (UNSUPPORTED, strict with exploratory handoff)

- Date window: `last 30 days`
- CRM scope: `HubSpot`
- Platform scope: `Instantly`

## User question
"What are my A/B test results by sequence step?"

## Compact preflight output
- `Intent:` none
- `Mode:` strict
- `Verdict:` UNSUPPORTED
- `Confidence:` high
- `Missing fields:` n/a
- `Fallback plan:` none
- `Reason:` no_matching_intent
- `Supported intents:` top campaigns by replies, high opens low replies, fastest replies after first send, follow-up prioritization, platform engagement attribution, deliverability unsubscribes/bounces

## Suggested handoff output
- Strict no-match detected.
- If the user wants best-effort analysis, offer:
  - "Switch to `Mode: exploratory` and I will analyze available signals with explicit caveats and confidence labels."
