# Refactor Playbooks (SwiftUI)

Goal-based playbooks for behavior-preserving refactors. Each playbook starts from a baseline, preserves refactor invariants, and ends with verification against the original behavior.

**Invariants:** See [workflows-refactor.md](workflows-refactor.md#invariants). These are non-negotiables for every step.

## Playbook: View extraction

**Goal**
Extract a view to improve readability while preserving state ownership, stable identity, and data flow.

**Pre-checks**
- Capture the current behavior baseline (visual output, interactions, state changes).
- Identify state owners vs editors using [State ownership](state.md).
- Map data-flow paths using [View composition](view-composition.md).
- Confirm any list content uses stable identity per Invariants.

**Steps**
1) Mark the source of truth for each value (owner vs editor). Keep ownership in the current owner.
2) Extract the new view with immutable inputs for display-only data.
3) Pass editable values via `@Binding` and events via callbacks.
4) Preserve list identity by passing stable IDs (do not swap to indices).
5) Keep async work in the same lifecycle hook (`.task`, `.onChange`) unless you are intentionally relocating it.
6) Re-evaluate invariants after extraction: identity, ownership, navigation source, async lifecycle.

**Verify**
- Behavior baseline still matches (same visuals, same interactions).
- Invariants remain true (identity, ownership, navigation, async).
- Data flow is still down, events up (no child mutation of parent state).

**Risk cues**
- State ownership moves to the new child view.
- `ForEach` identity changes or becomes index-based.
- Async work moves from `.task`/`.onChange` to `body`.

## Playbook: Navigation migration to NavigationStack

**Goal**
Migrate legacy navigation APIs to `NavigationStack` while keeping a single navigation source of truth.

**Pre-checks**
- Capture navigation baseline (start screen, push/pop behavior, deep-link entry if present).
- Identify the current navigation owner (root view or shared model).
- Review [NavigationStack guidance](navigation.md) and Invariants.

**Steps**
1) Define a route enum or path model that represents current destinations.
2) Create a single `NavigationStack` at the flow root with a single path source of truth.
3) Replace legacy links with `NavigationLink(value:)` and add `navigationDestination(for:)`.
4) Keep navigation state in one place (root view or shared model) and pass bindings down.
5) Preserve existing presentation behavior for sheets and full-screen covers.
6) Re-check invariants: single navigation source of truth, stable identity, state ownership.

**Verify**
- Navigation baseline unchanged (push, back, restore, modal presentation).
- Invariants hold for navigation source and data flow.
- State updates still drive navigation correctly (no duplicated path state).

**Risk cues**
- Multiple `NavigationStack` instances in the same flow.
- Path state duplicated across views.
- Navigation state stored in both view state and shared model.

## Playbook: State hoisting

**Goal**
Move state up the hierarchy without breaking bindings, updates, or async work.

**Pre-checks**
- Capture behavior baseline (what changes when state updates).
- Identify the current owner and consumers using [State ownership](state.md).
- Review [View composition](view-composition.md) for data flow rules.

**Steps**
1) Choose the new owner based on lifetime and sharing needs (parent or shared model).
2) Move the source of truth to the new owner; keep the previous view as an editor via `@Binding`.
3) Update child inputs to use bindings or immutable values (no duplicated state).
4) Keep async work tied to the view that still owns the lifecycle or to the new owner if its lifetime changed.
5) Verify identity and navigation invariants remain intact after moving state.

**Verify**
- Behavior baseline unchanged (updates propagate, UI stays in sync).
- Invariants hold for ownership and data flow.
- Async work still cancels and restarts correctly when inputs change.

**Risk cues**
- Multiple sources of truth emerge (old and new owners both mutate state).
- Bindings no longer update the UI or update the wrong instance.
- Async work no longer tied to the correct lifecycle owner.

## Related references

- `workflows-refactor.md` for invariants and refactor checklist.
- `state.md` for ownership and wrapper selection.
- `navigation.md` for NavigationStack patterns and migration details.
- `view-composition.md` for extraction and data flow patterns.
