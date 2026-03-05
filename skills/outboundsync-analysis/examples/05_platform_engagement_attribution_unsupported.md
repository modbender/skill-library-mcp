# Example 05: Platform Engagement Attribution (UNSUPPORTED, strict)

- Intent ID: `platform_engagement_attribution`
- Date window: `last 30 days`
- CRM scope: `Salesforce`
- Platform scope: `Instantly, Smartlead`

## User question
"Is Instantly or Smartlead driving better engagement?"

## Available fields (sample)
- `OSLast OpenTime__c`
- `OSLast ReplyTime__c`
- Missing: `OSLast UpdateSource__c`

## Compact preflight output
- `Intent:` platform_engagement_attribution
- `Mode:` strict
- `Verdict:` UNSUPPORTED
- `Confidence:` high
- `Missing fields:` `OSLast UpdateSource__c`
- `Fallback plan:` none

## Example response output
- Unsupported for strict platform attribution.
- Required data to proceed: `OSLast UpdateSource__c`.
- No platform ranking is produced.
