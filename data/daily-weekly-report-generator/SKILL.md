---
name: daily-weekly-report-generator
description: Produce daily and weekly performance reports for Meta (Facebook/Instagram), Google Ads, TikTok Ads, YouTube Ads, Amazon Ads, and DSP/programmatic campaigns.
---

# Ads Report Generator

## Purpose
Core mission:
- report assembly, narrative summarization, action recommendation

This skill is specialized for advertising workflows and should output actionable plans rather than generic advice.

## When To Trigger
Use this skill when the user asks for:
- ad execution guidance tied to business outcomes
- growth decisions involving revenue, roas, cpa, or budget efficiency
- platform-level actions for: Meta (Facebook/Instagram), Google Ads, TikTok Ads, YouTube Ads, Amazon Ads, DSP/programmatic
- this specific capability: report assembly, narrative summarization, action recommendation

High-signal keywords:
- ads, advertising, campaign, growth, revenue, profit
- roas, cpa, roi, budget, bidding, traffic, conversion, funnel
- meta, googleads, tiktokads, youtubeads, amazonads, shopifyads, dsp

## Input Contract
Required:
- question_or_report_goal
- metric_scope: KPI, dimensions, and date range
- data_source_scope

Optional:
- attribution_window
- benchmark_reference
- dashboard_filters
- confidence_threshold

## Output Contract
1. Metric Definition Clarification
2. Query Plan
3. Result Summary
4. Interpretation and Caveats
5. Decision Recommendation

## Workflow
1. Disambiguate metric definitions and time window.
2. Build query slices by platform, funnel, and audience.
3. Compute trend deltas and variance drivers.
4. Summarize findings with confidence level.
5. Propose concrete next actions.

## Decision Rules
- If metric definitions conflict, lock one canonical definition before analysis.
- If sample size is small, mark result as directional not conclusive.
- If attribution changes materially alter result, show both views.

## Platform Notes
Primary scope:
- Meta (Facebook/Instagram), Google Ads, TikTok Ads, YouTube Ads, Amazon Ads, DSP/programmatic

Platform behavior guidance:
- Keep recommendations channel-aware; do not collapse all channels into one generic plan.
- For Meta and TikTok Ads, prioritize creative testing cadence.
- For Google Ads and Amazon Ads, prioritize demand-capture and query/listing intent.
- For DSP/programmatic, prioritize audience control and frequency governance.

## Constraints And Guardrails
- Never fabricate metrics or policy outcomes.
- Separate observed facts from assumptions.
- Use measurable language for each proposed action.
- Include at least one rollback or stop-loss condition when spend risk exists.

## Failure Handling And Escalation
- If critical inputs are missing, ask for only the minimum required fields.
- If platform constraints conflict, show trade-offs and a safe default.
- If confidence is low, mark it explicitly and provide a validation checklist.
- If high-risk issues appear (policy, billing, tracking breakage), escalate with a structured handoff payload.

## Code Examples
### Query Spec Example

    metric: roas
    dimensions: [platform, campaign]
    date_range: last_30d

### Result Schema

    {
      "platform": "Meta",
      "spend": 12000,
      "revenue": 42000,
      "roas": 3.5
    }

## Examples
### Example 1: Daily report automation
Input:
- Need 9AM daily summary for key campaigns
- KPI: spend, cpa, roas

Output focus:
- report schema
- anomaly highlights
- top next actions

### Example 2: Attribution window comparison
Input:
- 1d click vs 7d click disagreement
- Decision needed for budget shift

Output focus:
- side-by-side metric table
- interpretation caveats
- decision recommendation

### Example 3: Traffic structure diagnosis
Input:
- Revenue flat but traffic rising
- Suspected quality decline

Output focus:
- source mix decomposition
- quality signal changes
- corrective action plan

## Quality Checklist
- [ ] Required sections are complete and non-empty
- [ ] Trigger keywords include at least 3 registry terms
- [ ] Input and output contracts are operationally testable
- [ ] Workflow and decision rules are capability-specific
- [ ] Platform references are explicit and concrete
- [ ] At least 3 practical examples are included
