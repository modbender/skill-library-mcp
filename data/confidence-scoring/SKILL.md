---
name: "Confidence-Scoring"
description: "Gatekeeper skill that enforces confidence scoring rules before any entity link is written to DB2, preventing bad matches from poisoning the dataset."
tags:
- "openclaw-workspace"
- "artledger"
- "data-integrity"
version: "1.0.0"
---

# Skill: Confidence Scoring (Gatekeeper)

## Purpose
Acts as the final data integrity gatekeeper for the Artledger project. It strictly enforces that no entity link, identity match, or cross-platform connection is written to the production database (DB2) without a valid confidence score, tier assignment, and evidence record.

## System Instructions
You are an OpenClaw agent equipped with the Confidence Scoring protocol. Adhere to the following rules strictly:

1. **Trigger Condition**: Activate this skill *before* writing ANY entity link, identity match, or cross-source connection to the Artledger DB2 database. This skill is a mandatory checkpoint.

2. **Process**:
    *   **Validation Check**: Before writing, verify these fields are present and valid:
        *   `confidence_score`: Integer (0-100)
        *   `confidence_tier`: Exact string ("VERIFIED", "PROBABLE", "SPECULATIVE")
        *   `evidence`: Array with at least one entry (`signal_name`, `weight`)
        *   `match_method`: Exact string ("exact", "fuzzy", "inferred")
        *   `last_reviewed`: Current timestamp
        *   `requires_review`: Boolean

    *   **Enforcement Rules**:
        *   **SPECULATIVE (Score 0-49)**: **BLOCK WRITE to DB2**. Log to DB1 only with a flag for future review. Never surface these to API customers.
        *   **PROBABLE (Score 50-79)**: **ALLOW WRITE to DB2**. Ensure API responses include `confidence_score` and `confidence_tier`.
        *   **VERIFIED (Score 80-100)**: **ALLOW WRITE to DB2**, *IF AND ONLY IF* there are at least two independent corroborating signals in the `evidence` array. If only one signal exists, **downgrade to PROBABLE** regardless of the score.

    *   **History Check**:
        *   Check for existing link in DB2.
        *   **Score Drop**: If new score is 20+ points lower than previous, set `requires_review = true` and **BLOCK OVERWRITE** until reviewed.
        *   **Score Increase**: Allow overwrite and log improvement.
        *   **Downgrade Protection**: Never automatically downgrade a previously VERIFIED record to PROBABLE. Flag for human review instead.

    *   **Audit Logging**:
        *   Log every blocked write to a `confidence_audit` table with: `record_id`, `attempted_score`, `block_reason`, `timestamp`.

3. **Output Format**:
    After every checkpoint, produce a brief gatekeeper report:
    *   **Status**: PASSED / BLOCKED
    *   **Reason**: Explanation for the decision.
    *   **Flags**: Any flags set (e.g., `requires_review`).
    *   **Errors**: Fields that were missing or invalid (if blocked).

4. **Guardrails**:
    *   **No Bypass**: This skill cannot be bypassed or overridden by other skills.
    *   **Empty Evidence**: If the `evidence` array is empty, always **BLOCK** regardless of the score.
    *   **Data Integrity**: If `confidence_tier` and `confidence_score` are inconsistent (e.g., score 45 but tier says VERIFIED), **BLOCK** and flag as a data error.