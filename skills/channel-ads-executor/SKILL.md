---
name: channel-ads-executor
description: Translate strategy into channel-specific execution plans for Meta (Facebook/Instagram), Google Ads, TikTok Ads, YouTube Ads, Amazon Ads, Shopify Ads, and DSP/programmatic.
---

# Multi-Platform Ads Executor

## Purpose
Core mission:
- execution sequencing, setup checklist, rollout control

This skill is specialized for advertising workflows and should output actionable plans rather than generic advice.

## When To Trigger
Use this skill when the user asks for:
- ad execution guidance tied to business outcomes
- growth decisions involving revenue, roas, cpa, or budget efficiency
- platform-level actions for: Meta (Facebook/Instagram), Google Ads, TikTok Ads, YouTube Ads, Amazon Ads, Shopify Ads, DSP/programmatic
- this specific capability: execution sequencing, setup checklist, rollout control

High-signal keywords:
- ads, advertising, campaign, growth, revenue, profit
- roas, cpa, roi, budget, bidding, traffic, conversion, funnel
- meta, googleads, tiktokads, youtubeads, amazonads, shopifyads, dsp

## Input Contract
Required:
- objective: growth target and KPI priority
- budget_frame: test budget and scale budget
- channel_scope: channels to include

Optional:
- audience_segments
- creative_inventory
- seasonality_window
- policy_constraints

## Output Contract
1. Strategy Snapshot
2. Channel Role Definition
3. Budget and Bidding Plan
4. Test Matrix
5. Scale and Kill Rules

## Workflow
1. Define objective hierarchy (primary and secondary KPI).
2. Assign channel roles by funnel stage.
3. Allocate budget by expected signal and risk.
4. Design test cells and learning windows.
5. Set scale, hold, and stop rules.

## Decision Rules
- If KPI conflict exists, prioritize revenue efficiency over volume.
- If channel evidence is weak, allocate minimum test budget first.
- If audience is broad, start with modular creatives and layered targeting.

## Platform Notes
Primary scope:
- Meta (Facebook/Instagram), Google Ads, TikTok Ads, YouTube Ads, Amazon Ads, Shopify Ads, DSP/programmatic

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
### Strategy Matrix (YAML)

    objective: improve_roas
    channels:
      - name: Meta
        role: demand_creation
      - name: Google Ads
        role: demand_capture
    budget_split:
      Meta: 0.55
      Google Ads: 0.45

### Test Cell Example

    cell_id: T1
    variable: audience_segment
    success_metric: cpa

## Examples
### Example 1: Channel mix reset
Input:
- Budget fixed at 50k
- ROAS dropped for two weeks

Output focus:
- reallocation plan
- test matrix
- stop-loss conditions

### Example 2: Creator-led expansion strategy
Input:
- Goal: scale traffic without ROAS collapse
- Channels: TikTok Ads + YouTube Ads

Output focus:
- funnel role split
- budget pacing logic
- creative cadence

### Example 3: Retargeting-heavy recovery
Input:
- Prospecting unstable
- Strong existing customer base

Output focus:
- retargeting architecture
- audience exclusion design
- two-phase launch plan

## Quality Checklist
- [ ] Required sections are complete and non-empty
- [ ] Trigger keywords include at least 3 registry terms
- [ ] Input and output contracts are operationally testable
- [ ] Workflow and decision rules are capability-specific
- [ ] Platform references are explicit and concrete
- [ ] At least 3 practical examples are included
