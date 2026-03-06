---
name: sentiment-priority-scorer
description: "Score normalized real-estate leads using sentiment, urgency, intent, recency, and record type to produce deterministic priority rankings and P1-P3 buckets. Use when users ask to prioritize hot leads, rank callback queue, or triage follow-ups without performing writes or outbound sends. Recommended chain: india-location-normalizer then sentiment-priority-scorer then summary-generator and action-suggester."
---

# Sentiment Priority Scorer

Produce deterministic priority scores for leads without mutating any state.

## Quick Triggers

- Rank leads by urgency and tone for callback priority.
- Classify leads into P1/P2/P3 queue.
- Score follow-up priority from normalized lead records.

## Recommended Chain

`india-location-normalizer -> sentiment-priority-scorer -> summary-generator`

## Execute Workflow

1. Accept input from Supervisor containing normalized leads.
2. Validate input with `references/sentiment-priority-input.schema.json`.
3. Score each lead with:
   - `sentiment_score` in range `[-1, 1]`
   - `intent_score` in range `[0, 1]`
   - `recency_score` in range `[0, 1]`
   - mapped `urgency_score` from lead urgency (`high=1.0`, `medium=0.6`, `low=0.3`)
4. Use `record_type` to avoid over-prioritizing generic bulk inventory:
   - `buyer_requirement`: apply +0.10 intent lift (hard demand signal)
   - `inventory_listing`: no lift unless high-action cues are present
5. Boost `intent_score` when high-action cues exist in listing text:
   - `immediately`, `keys at office`, `one day notice`, `possession`, `inspection any time`
6. Compute `priority_score` on a 0-100 scale:
   - `priority_score = 100 * (0.40*urgency_score + 0.30*intent_score + 0.20*recency_score + 0.10*sentiment_risk)`
   - `sentiment_risk = max(0, -sentiment_score)`
7. Assign buckets:
   - `P1` for `priority_score >= 75`
   - `P2` for `priority_score >= 50 and < 75`
   - `P3` for `< 50`
8. Produce plain-language `evidence` tokens that explain the score, including record-type evidence.
9. Validate output with `references/sentiment-priority-output.schema.json`.

## Enforce Boundaries

- Never write to Google Sheets, databases, or files.
- Never send messages or trigger outbound channels.
- Never create reminders or execute actions.
- Never bypass Supervisor routing or approvals.
- Never replace upstream urgency; only derive scoring fields.

## Handle Errors

1. Reject schema-invalid inputs.
2. Return field-level reasons when scoring cannot be computed.
3. Fail closed if required scoring features are missing.
