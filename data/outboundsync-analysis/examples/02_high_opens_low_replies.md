# Example 02: High Opens, Low Replies (SUPPORTED, strict)

- Intent ID: `high_opens_low_replies`
- Date window: `last 30 days`
- CRM scope: `Salesforce`
- Platform scope: `EmailBison`

## User question
"Which campaigns show high opens but low replies?"

## Available fields (sample)
- `OSLast CampaignName__c`
- `OSLast OpenTime__c`
- `OSLast ReplyTime__c`
- `OSLast LinkClickTime__c`

## Compact preflight output
- `Intent:` high_opens_low_replies
- `Mode:` strict
- `Verdict:` SUPPORTED
- `Confidence:` medium
- `Missing fields:` `open counts` (not available in Salesforce field set)
- `Fallback plan:` none

## Example analysis output
- Campaigns with high engagement but weak reply conversion:
  1. `RevOps NA MidMarket` -> strong open activity, low reply activity
  2. `PLG Security Persona` -> strong open activity, low reply activity
- Limitation:
  - Salesforce schema does not expose open counts; open-time presence is used as the engagement signal.
