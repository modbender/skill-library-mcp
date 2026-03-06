# Deslop Heuristics

Use this as a review checklist against branch diffs.

## Core heuristics

- Extra comments a human would not add in this codebase.
- Extra defensive checks or `try/catch` blocks that are abnormal for trusted/validated code paths.
- Type escapes like `as any`, broad `any`, or cast chains used to bypass type errors.
- Style inconsistent with the file/module’s existing patterns.

## Additional heuristics

- Unused or cargo-cult hooks: `useMemo`/`useCallback`/`useRef` added without real need.
- Guard refs/flags that only paper over async flow issues and can be simplified.
- Silent catches that swallow errors without user feedback, logging, or recovery value.
- Over-abstracted wrappers/helpers that hide one-liners and reduce readability.
- Runtime checks duplicating existing schema/type validation.
- Placeholder artifacts (`FIX`, `TODO` with no owner/context, temporary text, dead stubs).
- Debug leftovers (`console.log`, temporary banners, dead debug API branches).
- Lint-disable comments that justify weak patterns instead of fixing root causes.
- Inconsistent async style (`void` vs awaited navigation/mutations) within the same file.
- Defensive null/undefined branches that contradict invariant data contracts nearby.
- Redundant local state that mirrors query/mutation state without added behavior.
- Copy/paste drift: same logic repeated with slight inconsistent naming/behavior.
- Overly broad error normalization that hides actionable backend error details.

## Keep (not slop) when true

- Boundary checks at external trust edges: query params, request payloads, OAuth callbacks.
- Error handling needed for real user-facing recovery or observability.
- Compatibility guards required by framework/library behavior.
- Explicit typing that tightens contracts and improves safety.
