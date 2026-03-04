# Realignment Protocol

Use this protocol whenever intent may have changed or drift is detected.

## Triggers
- User message changes goals, constraints, priorities, or scope.
- Drift score crosses threshold in the hub.
- Verification fails against acceptance criteria.
- New dependency or auth blocker changes execution path.

## Procedure
1. Capture change candidate and classify it.
2. Build `intent_delta`.
3. Confirm or update strictness mode for affected scope (project/repo/workflow/task).
4. Identify impacted phases/repos only.
5. Re-plan only impacted phases.
6. Preserve completed unaffected phases unless user requests rollback.
7. Ask for confirmation if change affects acceptance criteria or hard constraints.
8. Update hub logs and next check-in time.

## Clarification Loop
When ambiguity remains:
1. Ask targeted clarification questions.
2. Offer a recommended default.
3. Record answer as structured update in `intent_snapshot`.
4. Recompute drift and blockers.

If the user does not answer and autonomy permits progress:
- continue only on low-risk, reversible tasks.
- keep blocked phases paused.

## Check-in Cadence
- Strict: before each phase start.
- Balanced: phase end and on major drift.
- Aggressive: major drift only.
- Exploratory: periodic summaries; block only on critical ambiguity/risk.

## Proactive Improvement Behavior
- At phase end, propose at least one optimization and one risk reduction with evidence.
- If external research suggests improved outcomes, create an `intent_delta` proposal before applying changes.
- In autonomy `3` or `4`, add optional "Propose Changes" phase unless user opts out.
- If `ambiguity_score > 0.2`, ask at least 1 decision-ready question before the next phase.

## Upfront Strictness Prompt
At kickoff, ask:
- preferred default mode (`hard_gate`, `soft_gate`, `advisory`)
- any repo-level override
- any workflow/task override

Apply precedence: `task > workflow > repo > project > default`.
