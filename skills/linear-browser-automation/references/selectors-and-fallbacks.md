# Selectors and Fallbacks

## Primary strategy

- Use fresh `snapshot` refs before each interaction.
- Prefer ARIA-based refs for stability.
- Keep target tab stable via returned `targetId`.
- Prefer existing authenticated Linear tab over opening a new one.

## Fallback strategy

- If a ref is stale: snapshot again and resolve new ref.
- If navigation changed layout: re-identify main container before actions.
- If modal not visible: trigger the UI entry point again and re-snapshot.
- If unauthenticated state/public landing appears:
  - navigate to `/login`
  - trigger a browser alert requesting login
  - wait for dashboard/workspace elements, then resume automatically.

## Verification strategy

- After submit actions, snapshot and verify expected signal:
  - Success toast/banner
  - New issue identifier visible
  - Updated field value visible
  - New comment present in timeline
