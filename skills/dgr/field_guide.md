# DGR Field Guide — How to Interpret Artifact Fields

This guide explains how to read and act on DGR (Decision-Grade Reasoning) artifacts.

## Core Sections

### `meta`
**Purpose:** Artifact metadata for tracking and governance
- `artifact_id` — Unique identifier for this decision record
- `spec_version` — DGR format version (currently 1.0.0)
- `created_at` — Timestamp when analysis was performed
- `mode` — Analysis depth: `dgr_min` (fast), `dgr_full` (detailed), `dgr_strict` (conservative)

### `input`
**Purpose:** Captures what was analyzed
- `query_summary` — Human-readable description of the decision request
- `query_hash` — Stable identifier for the exact request (for deduplication/linking)

### `clarifications` (optional)
**Purpose:** Questions that need answers before proceeding
- `question` — What specific information is missing
- `why_needed` — Why this information affects the decision
- `blocking` — Whether decision should be delayed until clarified

**Action:** Address blocking clarifications before implementing recommendations.

### `assumptions`
**Purpose:** Explicit assumptions underlying the reasoning
- `statement` — What is being assumed to be true
- `impact_if_wrong` — Risk if this assumption proves incorrect

**Action:** Validate critical assumptions before acting on recommendations.

### `risks`
**Purpose:** Potential negative outcomes and their handling
- `risk` — Description of what could go wrong
- `severity` — Impact level: `low`, `medium`, `high`
- `mitigation` — How to reduce likelihood or impact

**Action:** Implement mitigations for high-severity risks; monitor medium/low risks.

### `recommendation`
**Purpose:** The actual decision guidance
- `action` — Recommended course of action
- `rationale` — Why this action is recommended
- `confidence` — Certainty level (0.0-1.0, where 1.0 = completely confident)
- `review_required` — Whether human review is needed before acting
- `next_steps` — Concrete actions to implement the recommendation

**Action:** If `review_required = true`, seek appropriate stakeholder approval before proceeding.

### `consistency_check`
**Purpose:** Internal validation of the reasoning
- `checks` — List of consistency verifications performed
- `passed` — Whether all checks succeeded
- `notes` — Additional context on the validation

**Action:** If `passed = false`, investigate inconsistencies before using the recommendation.

## Governance Guidelines

### High-Stakes Decisions
- Always honor `review_required = true`
- Validate assumptions for decisions with broad impact
- Document any deviations from recommendations

### Confidence Interpretation
- **0.8-1.0:** High confidence, proceed with normal review
- **0.5-0.8:** Moderate confidence, consider additional validation
- **0.0-0.5:** Low confidence, seek expert input or additional data

### Risk Management
- **High severity risks:** Must have mitigation plans in place
- **Medium severity risks:** Monitor closely during implementation
- **Low severity risks:** Acceptable risk level for most contexts

## Usage Patterns

### For Decision Makers
1. Check `review_required` and `consistency_check.passed`
2. Review high-severity risks and their mitigations
3. Validate critical assumptions
4. Implement recommended action with appropriate safeguards

### For Auditors
1. Verify artifact completeness (required fields present)
2. Assess assumption reasonableness
3. Check risk identification and mitigation adequacy
4. Review consistency check results

### For Teams
1. Use artifacts as decision documentation
2. Reference `artifact_id` in related work
3. Update assumptions/risks as context changes
4. Conduct post-decision reviews using the artifact structure