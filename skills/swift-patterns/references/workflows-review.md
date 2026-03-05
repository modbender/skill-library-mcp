# Review Workflow (SwiftUI)

Use this workflow when the user asks for findings, risks, or assessment without code changes.

**Constraints:** See [SKILL.md Constraints](../SKILL.md#constraints).

For refactor invariants, see [workflows-refactor.md](workflows-refactor.md#invariants).

## Scope and Inputs

Record the scope and inputs before reviewing:

- Files and components reviewed
- Requirements or expected behaviors
- Platform constraints (iOS version, feature flags, availability)

## Findings Taxonomy

Classify findings consistently so review output is stable and comparable:

- **Correctness:** Behavior mismatches, edge cases, crashes, or broken flows
- **Data flow:** Ownership, bindings, and unidirectional flow violations
- **Navigation:** Competing sources of truth, path mismatches, or route handling gaps
- **Identity:** Unstable list identity, incorrect `id:` usage, state loss
- **Performance:** Unnecessary recomputation, heavy work in body, missing lazy containers
- **Accessibility (when required or requested):** Missing labels, contrast, or focus issues

## Review Checklist

See the detailed Review Checklist in [SKILL.md](../SKILL.md#review-checklist).

## Risk Cues (Ask for Tests or Split Work)

Escalate when you see any of these signals:

- No tests cover the behavior being reviewed or changed soon after
- State ownership is changing or being inferred during review
- Navigation path state appears in multiple places or is being redefined
- List identity changes could reset selection or row state
- Async work was moved or detached from view lifecycle
- Refactor scope touches multiple screens or core flows without verification
