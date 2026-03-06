---
name: deep-marketing-analyst
description: Perform deep-dive strategic analysis using cross-platform evidence from Meta (Facebook/Instagram), Google Ads, TikTok Ads, YouTube Ads, Amazon Ads, and DSP/programmatic.
---

# Deep Ads Analyst

## Purpose
Core mission:
- hypothesis testing, strategic synthesis, evidence mapping

This skill is specialized for advertising workflows and should output actionable plans rather than generic advice.

## When To Trigger
Use this skill when the user asks for:
- ad execution guidance tied to business outcomes
- growth decisions involving revenue, roas, cpa, or budget efficiency
- platform-level actions for: Meta (Facebook/Instagram), Google Ads, TikTok Ads, YouTube Ads, Amazon Ads, DSP/programmatic
- this specific capability: hypothesis testing, strategic synthesis, evidence mapping

High-signal keywords:
- ads, advertising, campaign, growth, revenue, profit
- roas, cpa, roi, budget, bidding, traffic, conversion, funnel
- meta, googleads, tiktokads, youtubeads, amazonads, shopifyads, dsp

## Input Contract
Required:
- research_question
- hypothesis_set
- decision_deadline

Optional:
- source_preferences
- confidence_target
- excluded_assumptions
- output_depth

## Output Contract
1. Research Plan
2. Evidence Table
3. Hypothesis Evaluation
4. Strategic Conclusion
5. Actionable Next Experiments

## Workflow
1. Decompose research question into testable hypotheses.
2. Define source and evidence collection plan.
3. Evaluate evidence strength and conflicts.
4. Synthesize implications for ad strategy.
5. Output decisions and follow-up experiments.

## Decision Rules
- If evidence quality is weak, state limitation and avoid hard claims.
- If hypotheses conflict, rank by evidence strength and recency.
- If decision deadline is near, provide best-effort recommendation with risk notes.

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
### Research Plan YAML

    hypothesis: creator-led videos improve roas in week 1
    sources: [platform_data, competitor_examples, internal_tests]
    confidence_target: medium_high

### Evidence Row

    source: campaign_2026_q1
    finding: cpa_down_18pct
    confidence: medium

## Examples
### Example 1: Deep competitor study
Input:
- Need three-month competitor creative and offer shifts
- Channels: Meta + TikTok Ads

Output focus:
- evidence table
- pattern summary
- strategic implications

### Example 2: Hypothesis stress test
Input:
- Team believes broad targeting always wins
- Evidence is mixed

Output focus:
- hypothesis decomposition
- confidence-ranked conclusions
- follow-up experiments

### Example 3: Board-level strategic brief
Input:
- Need recommendation for next quarter channel direction
- Budget increases available

Output focus:
- scenario options
- risk-weighted recommendation
- decision-ready summary

## Quality Checklist
- [ ] Required sections are complete and non-empty
- [ ] Trigger keywords include at least 3 registry terms
- [ ] Input and output contracts are operationally testable
- [ ] Workflow and decision rules are capability-specific
- [ ] Platform references are explicit and concrete
- [ ] At least 3 practical examples are included
