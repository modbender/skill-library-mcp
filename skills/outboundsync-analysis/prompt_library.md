# Prompt Library (OutboundSync Analysis)

Source: OutboundSync Help Center references plus OutboundSync v0.1 router contract.

## Priming prompt (recommended)

HubSpot:
> You are analyzing outbound performance using OutboundSync-synced properties in HubSpot. Do not invent fields. If data is missing, state it explicitly. Honor strict or exploratory mode exactly.

Salesforce:
> You are analyzing outbound performance using OutboundSync-synced custom fields in Salesforce. Do not invent fields. If data is missing, state it explicitly. Honor strict or exploratory mode exactly.

## How to use
1. Include the relevant field dictionary in context (`hubspot_properties.md` or `salesforce_fields.md`).
2. Use any prompt below directly, or adapt for your CRM, platform, and date window.

## Prompt registry

| Prompt ID | Mode | Mapping Type | Mapping | Prompt |
|---|---|---|---|---|
| SP-01 | strict | intent_id | top_campaigns_by_replies_30d | CRM: HubSpot. Platform: Smartlead. Date window: last 30 days. Question: Rank campaigns by replies and include limitations if reply-time coverage is incomplete. Mode: strict. |
| SP-02 | strict | intent_id | high_opens_low_replies | CRM: Salesforce. Platform: Instantly. Date window: last 30 days. Question: Identify campaigns with high engagement but low reply conversion. Mode: strict. |
| SP-03 | strict | intent_id | fastest_replies_after_first_send | CRM: HubSpot. Platform: EmailBison. Date window: last 30 days. Question: Compare campaigns by send-to-reply latency and report fallback if sent time is missing. Mode: strict. |
| SP-04 | strict | intent_id | follow_up_prioritization | CRM: HubSpot. Platform: Smartlead. Date window: last 14 days. Question: Prioritize contacts for follow-up using open, click, and reply signals. Mode: strict. |
| SP-05 | strict | intent_id | platform_engagement_attribution | CRM: Salesforce. Platform: Instantly, Smartlead. Date window: last 30 days. Question: Compare platform engagement and include explicit limitation if update source is missing. Mode: strict. |
| SP-06 | strict | intent_id | deliverability_unsubscribes_bounces | CRM: HubSpot. Platform: Instantly. Date window: last 30 days. Question: Analyze unsubscribe and bounce issues and provide fallback when sent address is missing. Mode: strict. |
| EP-01 | exploratory | exploratory_path | heyreach_social_summary | CRM: HubSpot. Platform: HeyReach. Date window: last 30 days. Question: Provide a social campaign summary with campaign volume, social reply recency, and trend direction. Mode: exploratory. |
| EP-02 | exploratory | category | no_match_handoff | CRM: HubSpot. Platform: Instantly. Date window: last 30 days. Question: If strict routing returns no_matching_intent, continue with best-effort exploratory analysis and list observed signals, missing signals, confidence, and non-causal caveat. Mode: exploratory. |
