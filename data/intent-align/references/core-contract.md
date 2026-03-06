# Core Contract

Use this file as the required execution contract for intent alignment.

## Required Objects
Use these objects in the alignment hub and phase loop.

```yaml
intent_snapshot:
  user_goal: string
  non_goals: [string]
  constraints: [string]
  acceptance_criteria: [string]
  priorities: [string]
  assumptions: [string]

intent_lint:
  ambiguity_score: 0.0
  critical_ambiguities: [string]
  warnings: [string]

intent_delta:
  reason: string
  changed_fields: [goal|constraints|acceptance_criteria|priorities|scope]
  impact: {phases_affected: [string], repos_affected: [string]}
  requires_replan: true

phase_gate:
  phase: string
  status: blocked|ready|in_progress|verify|done
  blocker_type: none|ambiguity|dependency|auth|risk

verification_evidence:
  phase: string
  artifacts: [string]
  checks_run: [string]
  result: pass|fail|partial
  notes: string

capability_matrix:
  required: [string]
  available: [string]
  missing: [string]
  adapters_selected: [string]
  adapters_dynamic: [string]

strictness_policy:
  default_mode: hard_gate|soft_gate|advisory
  project_mode: hard_gate|soft_gate|advisory
  repo_overrides: [{repo: string, mode: hard_gate|soft_gate|advisory}]
  workflow_overrides: [{workflow: string, mode: hard_gate|soft_gate|advisory}]
  task_overrides: [{task: string, mode: hard_gate|soft_gate|advisory}]
```

## Intent Quality Gate
Run before planning.

1. Build `intent_snapshot`.
2. Run `intent_lint`.
3. Ask user for strictness preference at project/repo/workflow/task scope when missing.
4. Resolve effective strictness with precedence: `task > workflow > repo > project > default`.
5. Evaluate ambiguity action using severity + strictness + risk class.
6. Classify ambiguities as critical, major, or minor.
7. If ambiguity remains, ask targeted questions before proceeding or continuing.
8. Validate capability IDs using `references/capability-taxonomy.md`.

## Ambiguity Classes
- Missing acceptance criteria.
- Conflicting constraints.
- Undefined scope boundaries.
- Unclear priority tradeoffs.
- Missing environment/tool access assumptions.

## Clarification Question Rules
- Ask 1-3 high-impact questions.
- Ask questions in decision-ready form (pick A vs B, define threshold, set priority).
- Propose a default when confidence is high enough; request explicit override.
- If `ambiguity_score > 0.2`, ask at least 1 clarification question before next phase.

## Pre-Execution Clarification Gate
Run before each phase starts.

1. Re-run lint on latest intent state.
2. Resolve effective strictness for this phase/task scope.
3. Check new blockers (including auth/capability blockers).
4. Confirm `strictness_policy` and `effective_strictness` are populated for this phase.
5. If blocked, request clarification or authorization path.
6. Resume only when phase gate is `ready`.

## Ambiguity Action Matrix
Use this matrix to set `blocked_by_clarification` and phase readiness.

- `hard_gate`: block on critical and major ambiguities.
- `soft_gate`: block on critical; allow major with assumptions and timed check-in.
- `advisory`: allow critical/major only if risk is not high; require explicit user-visible notice.
- Any mode + `high` risk: treat as at least `soft_gate`.

## Flexible Mode Guardrails
When proceeding under ambiguity, always:
- log explicit assumptions tied to each open ambiguity.
- emit user-visible notice that work is proceeding with ambiguity.
- set `clarifications_needed_by` and `next_user_checkin`.
- constrain execution to low-risk, reversible steps until ambiguity is resolved.

## Capability Binding Rules
- Match required capabilities to available adapters.
- If a capability is missing, create an ad-hoc adapter from `references/adapters/adapter-template.md`.
- Validate ad-hoc adapter required fields before use.
- Register validated adapter in `capability_matrix.adapters_selected`.
- If capability remains unresolved, switch to degraded mode and notify the user.
- Never fabricate unavailable tool access.
- Use core capability IDs from `references/capability-taxonomy.md`.
- Use custom capability IDs only with namespace `x.<agent_or_team>.<capability>`.
- Ensure all `adapters_selected` entries exist in hub `adapters` registry.

## Output Conformance Rules
Validate hub output before phase close and project close:
- Render full hub snapshot; do not use placeholders such as `(unchanged)`.
- Keep list-structured fields as explicit lists (`repos`, `phases`, `adapters`, logs).
- Use fenced code blocks for Mermaid (` ```mermaid ... ``` `).

On conformance failure:
- In `hard_gate` mode: block current phase until fixed.
- In `soft_gate` or `advisory`: allow `partial` with remediation notes and next check-in.

## Ad-Hoc Adapter Rules
- Create adapters only for current task/repo/workflow scope.
- Reuse existing validated adapters when capability and environment match.
- Include provenance metadata for all ad-hoc adapters:
  - `created_by`
  - `created_at`
  - `environment_assumptions`
  - `tool_access_required`
