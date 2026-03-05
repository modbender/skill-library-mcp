---
name: creative-inspiration-scout
description: Collect and structure ad creative inspiration for Meta (Facebook/Instagram), TikTok Ads, YouTube Ads, Google Ads, and Amazon Ads placements.
---

# Ads Creative Ideas

## Purpose
Core mission:
- hook mining, angle clustering, inspiration board

This skill is specialized for advertising workflows and should output actionable plans rather than generic advice.

## When To Trigger
Use this skill when the user asks for:
- ad execution guidance tied to business outcomes
- growth decisions involving revenue, roas, cpa, or budget efficiency
- platform-level actions for: Meta (Facebook/Instagram), TikTok Ads, YouTube Ads, Google Ads, Amazon Ads
- this specific capability: hook mining, angle clustering, inspiration board

High-signal keywords:
- ads, advertising, campaign, growth, revenue, profit
- roas, cpa, roi, budget, bidding, traffic, conversion, funnel
- meta, googleads, tiktokads, youtubeads, amazonads, shopifyads, dsp

## Input Contract
Required:
- product_or_offer
- target_audience
- placement_scope

Optional:
- existing_assets
- brand_tone
- prohibited_claims
- creative_constraints

## Output Contract
1. Creative Objective
2. Angle and Hook Set
3. Asset Specification
4. Test Variant Plan
5. Creative QA Notes

## Workflow
1. Anchor creative goal to funnel stage and KPI.
2. Generate angle family and hook variants.
3. Map each angle to placement format requirements.
4. Define variant matrix and test order.
5. Add quality and compliance checkpoints.

## Decision Rules
- If audience is cold, prioritize problem-agitation and proof-first hooks.
- If retargeting stage, prioritize offer clarity and urgency mechanics.
- If format limits are strict, simplify message hierarchy to one CTA.

## Platform Notes
Primary scope:
- Meta (Facebook/Instagram), TikTok Ads, YouTube Ads, Google Ads, Amazon Ads

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
### Creative Brief Example

    creative_id: CR-001
    angle: pain_to_outcome
    hook: "Stop wasting ad budget in week one"
    formats: [9:16_video, 1:1_image]

### Variant Matrix

    V1: hook_change
    V2: CTA_change
    V3: visual_proof_change

## Examples
### Example 1: New hook generation
Input:
- Existing creatives have high frequency fatigue
- Need fresh top-funnel hooks

Output focus:
- new angle families
- hook library
- test priorities

### Example 2: Asset adaptation by placement
Input:
- One hero concept, multiple platforms
- Need format-safe variations

Output focus:
- per-platform format specs
- copy-length adaptation
- QA checklist

### Example 3: Pre-launch creative scoring
Input:
- 12 creatives pending launch
- Limited review bandwidth

Output focus:
- quality scores
- reject/rework decisions
- launch candidate shortlist

## Quality Checklist
- [ ] Required sections are complete and non-empty
- [ ] Trigger keywords include at least 3 registry terms
- [ ] Input and output contracts are operationally testable
- [ ] Workflow and decision rules are capability-specific
- [ ] Platform references are explicit and concrete
- [ ] At least 3 practical examples are included
