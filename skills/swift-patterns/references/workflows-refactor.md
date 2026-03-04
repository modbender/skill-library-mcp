# Refactor Workflow (SwiftUI)

Use this workflow when the user asks to change code while preserving existing behavior.

**Constraints:** See [SKILL.md Constraints](../SKILL.md#constraints).

## Invariants

These must hold when refactoring:

- **Stable identity:** Use stable IDs for `List`/`ForEach`. No `.indices` for dynamic data.
- **State ownership:** `@State` = view-local, `@Binding` = parent-owned, `@Observable` = shared.
- **Single navigation source:** One `NavigationStack` root, one path source of truth.
- **Cancellable async:** Tie async work to view lifecycle with `.task`.
- **Unidirectional flow:** Data down, events up. No child mutation of parent state.

## Playbooks

Use the playbooks when you need step-by-step guidance for behavior-preserving refactors:

- View extraction (preserve state ownership, stable identity, data flow)
- Navigation migration to `NavigationStack` with a single source of truth
- State hoisting without breaking bindings or async work

See [Refactor playbooks](refactor-playbooks.md).

## Behavior-Preserving Refactor Checklist

### Pre-checks

- Confirm the request is a refactor (code changes, behavior preserved)
- Capture the current behavior that must remain unchanged
- Identify the files and views in scope
- Map the Invariants above to the code being changed

### Changes

- Preserve stable identity for lists and `ForEach` content
- Keep state ownership mapping consistent (`@State`, `@Binding`, `@Observable`)
- Maintain a single navigation source of truth (one root/path)
- Keep data flowing down and events flowing up
- Ensure async work remains cancellable and tied to view lifecycle
- Avoid introducing architecture mandates or tool-specific steps

### Verification

- Re-check invariants after changes
- Confirm behavior matches the captured baseline
- If tests exist, ensure they still pass

## Risk Cues (Split Refactor or Add Tests First)

If any of these are present, split the refactor or ask for tests before proceeding:

- No tests protect the behavior being refactored
- State ownership shifts between views or wrappers
- Navigation path or root changes are required
- List identity or ordering is being changed
- Async work is moved, duplicated, or detached
- Refactor spans multiple screens or shared components
