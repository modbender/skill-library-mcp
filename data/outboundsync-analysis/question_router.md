# Question Router (OutboundSync Analysis)

This router maps user questions to analysis intents. It defines six strict intents for core outbound analysis and one exploratory path for HeyReach social signals.

## Modes and verdicts
- Modes: `strict` (default), `exploratory` (explicit opt-in)
- Verdicts: `SUPPORTED`, `PARTIAL`, `UNSUPPORTED`, `EXPERIMENTAL_LIMITED`

## Preflight behavior
- Default output is compact: `Intent`, `Mode`, `Verdict`, `Confidence`, `Missing fields`, `Fallback plan`.
- Full decision trace is emitted only if the user asks for `verbose preflight`.

## Strict verdict rules
Apply in this order:
0. `UNSUPPORTED` if the question does not map to any strict v0.1 intent. State reason `no_matching_intent`, list the six supported intent categories, and suggest exploratory handoff if user wants best-effort analysis.
1. `UNSUPPORTED` if any intent `unsupported_condition` matches.
2. `SUPPORTED` if any `required_fields` set is satisfied.
3. `PARTIAL` if no required set is satisfied but a `fallback_requirements` set is satisfied.
4. `UNSUPPORTED` if neither required nor fallback sets are satisfied.

## Hard rules
- Use HubSpot internal labels and Salesforce API names.
- Do not infer missing required values.
- Run fallback steps exactly as defined.
- If a question could map to more than one strict intent, ask the user to clarify. If clarification is not possible, default to the closest matching intent and state the assumption in preflight.
- Exploratory mode does not relax read-only/security constraints.

---

## Strict intent entries

### 1) Top campaigns by replies (last 30 days)
- `id`: `top_campaigns_by_replies_30d`
- Question examples:
  - "Top campaigns by replies in the last 30 days"
  - "Which campaigns got the most replies this month?"
- Required fields (SUPPORTED):
  - HubSpot: (`os_last_email_campaign_name` OR `os_last_campaign_name`) + `os_last_reply_time`
  - Salesforce: `OSLast CampaignName__c` + `OSLast ReplyTime__c`
- Fallback minimum (PARTIAL):
  - HubSpot: `os_last_email_campaign_name` OR `os_last_campaign_name`
  - Salesforce: `OSLast CampaignName__c`
- Unsupported conditions:
  - none explicit; unresolved data falls to rule #4
- Fallback behavior:
  1. Rank campaigns by contact volume only (not reply rate).
  2. State that reply-time data is missing.

### 2) High opens, low replies
- `id`: `high_opens_low_replies`
- Question examples:
  - "Which campaigns have high opens but low replies?"
  - "Where are opens not converting into replies?"
- Required fields (SUPPORTED):
  - HubSpot: `os_last_campaign_name`, `os_number_of_email_opens`, `os_last_reply_time`
  - Salesforce: `OSLast CampaignName__c`, `OSLast OpenTime__c`, `OSLast ReplyTime__c`
- Fallback minimum (PARTIAL):
  - HubSpot: (`os_last_campaign_name` + `os_number_of_email_opens`) OR (`os_last_campaign_name` + `os_last_reply_time`)
  - Salesforce: (`OSLast CampaignName__c` + `OSLast OpenTime__c`) OR (`OSLast CampaignName__c` + `OSLast ReplyTime__c`)
- Unsupported conditions:
  - none explicit; unresolved data falls to rule #4
- Fallback behavior:
  1. In Salesforce, use open-time presence as engagement proxy.
  2. State open-count limitation when counts are unavailable.

### 3) Fastest replies after first send
- `id`: `fastest_replies_after_first_send`
- Question examples:
  - "Which campaigns get the fastest replies after send?"
  - "What is quickest reply latency by campaign?"
- Required fields (SUPPORTED):
  - HubSpot: `os_last_campaign_name`, `os_last_sent_time`, `os_last_reply_time`
  - Salesforce: `OSLast CampaignName__c`, `OSLast SentTime__c`, `OSLast ReplyTime__c`
- Fallback minimum (PARTIAL):
  - HubSpot: `os_last_campaign_name` + `os_last_reply_time`
  - Salesforce: `OSLast CampaignName__c` + `OSLast ReplyTime__c`
- Unsupported conditions:
  - none explicit; unresolved data falls to rule #4
- Fallback behavior:
  1. Replace latency analysis with reply volume and reply recency.

### 4) Follow-up prioritization
- `id`: `follow_up_prioritization`
- Question examples:
  - "Who should we prioritize for follow-up?"
  - "Which contacts are warm but unanswered?"
- Required fields (SUPPORTED):
  - HubSpot: (`os_last_open_time` OR `os_number_of_email_opens`) + `os_last_link_click_time` + `os_last_reply_time`
  - Salesforce: `OSLast OpenTime__c`, `OSLast LinkClickTime__c`, `OSLast ReplyTime__c`
- Fallback minimum (PARTIAL):
  - HubSpot: (`os_last_open_time` OR `os_number_of_email_opens`) + `os_last_reply_time`
  - Salesforce: `OSLast OpenTime__c` + `OSLast ReplyTime__c`
- Unsupported conditions:
  - none explicit; unresolved data falls to rule #4
- Fallback behavior:
  1. Prioritize by opens plus recency when click signal is missing.
  2. Exclude recent repliers unless user requests otherwise.

### 5) Platform engagement attribution
- `id`: `platform_engagement_attribution`
- Question examples:
  - "Which outbound platform drives best engagement?"
  - "Is Instantly or Smartlead performing better?"
- Required fields (SUPPORTED):
  - HubSpot: `os_last_update_source` + (`os_number_of_email_opens` OR `os_last_reply_time`)
  - Salesforce: `OSLast UpdateSource__c` + (`OSLast OpenTime__c` OR `OSLast ReplyTime__c`)
- Fallback minimum (PARTIAL):
  - none
- Unsupported conditions:
  - missing update-source field in selected CRM scope
- Fallback behavior:
  1. Do not attribute by platform.
  2. Return limitation and required missing field.

### 6) Deliverability issues (unsubscribes and bounces)
- `id`: `deliverability_unsubscribes_bounces`
- Question examples:
  - "What are our unsubscribe and bounce issues?"
  - "Where is deliverability failing?"
- Required fields (SUPPORTED):
  - HubSpot: `os_last_bounce_time`, `os_last_unsubscribe_time`, `os_last_sent_time`, `os_last_sent_address`
  - Salesforce: `OSLast BounceTime__c`, `OSLast UnsubscribeTime__c`, `OSLast SentTime__c`, `OSLast SentAddress__c`
- Fallback minimum (PARTIAL):
  - HubSpot: (`os_last_bounce_time` + `os_last_unsubscribe_time` + `os_last_sent_time`) OR (`os_last_bounce_time` + `os_last_sent_time`) OR (`os_last_unsubscribe_time` + `os_last_sent_time`)
  - Salesforce: (`OSLast BounceTime__c` + `OSLast UnsubscribeTime__c` + `OSLast SentTime__c`) OR (`OSLast BounceTime__c` + `OSLast SentTime__c`) OR (`OSLast UnsubscribeTime__c` + `OSLast SentTime__c`)
- Unsupported conditions:
  - none explicit; unresolved data falls to rule #4
- Fallback behavior:
  1. Analyze at campaign/global level when sent address is missing.
  2. If only bounce or unsubscribe data is available, analyze the available signal only and state which signal is missing.

---

## Exploratory-only path

### HeyReach social summary
- `exploratory_id`: `heyreach_social_summary`
- Mode requirement:
  - User must explicitly request `exploratory` mode.
- Scope:
  - HubSpot + HeyReach social-only contexts where strict email-intent outputs are limited or unavailable.
- Minimum signals:
  - (`os_last_social_campaign_name` OR `os_last_campaign_name`) + (`os_last_reply_social_time` OR `os_last_sent_social_time`)
- Verdict:
  - `EXPERIMENTAL_LIMITED`
- Required output shape:
  1. Campaign volume summary.
  2. Social reply recency summary.
  3. Activity trend direction (`up`, `flat`, or `down`) with explicit caveat.
- Required caveats:
  - Exploratory output is non-causal and best-effort.
  - Do not present social exploratory output as equivalent to strict email reply-performance analysis.

---

## Deferred intents (post-v0.1 strict scope)
- sequence step drop-off analysis
- full HeyReach social performance intent (strict-grade)
- Instantly content-level open subject/message analysis

## Conformance matrix

| Sample question | Mode | Intent/Path | Expected verdict | Expected behavior |
|---|---|---|---|---|
| "Top campaigns by replies" with campaign + reply time present | strict | `top_campaigns_by_replies_30d` | SUPPORTED | standard strict analysis |
| "Top campaigns by replies" with campaign only | strict | `top_campaigns_by_replies_30d` | PARTIAL | campaign-volume only; reply-time limitation |
| "High opens low replies" in Salesforce with open+reply times | strict | `high_opens_low_replies` | SUPPORTED | standard strict analysis |
| "Fastest replies" with no sent time | strict | `fastest_replies_after_first_send` | PARTIAL | reply volume + recency |
| "Platform attribution" with missing update source | strict | `platform_engagement_attribution` | UNSUPPORTED | no attribution; list missing field |
| "Deliverability" with no sent address | strict | `deliverability_unsubscribes_bounces` | PARTIAL | campaign/global deliverability view |
| "What are my A/B test results?" | strict | none | UNSUPPORTED | `no_matching_intent`; list supported categories; suggest exploratory handoff |
| "Summarize HeyReach social campaign performance" with social campaign + social reply signals | exploratory | `heyreach_social_summary` | EXPERIMENTAL_LIMITED | volume + recency + trend direction with caveats |
