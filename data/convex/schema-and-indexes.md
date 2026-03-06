# Convex Schema and Indexes

Use this file when defining or refactoring table and index design.

## Modeling Checklist

1. List core entities and invariants before coding.
2. Define tenant boundaries in each table early.
3. Specify required uniqueness constraints.
4. Decide soft-delete behavior up front.
5. Map each user-visible feature to an expected query path.

## Index Design Heuristics

- Create indexes for frequent filters first, then sort order.
- Prefer explicit index names that reveal intent.
- Keep write amplification in mind for high-churn tables.
- Avoid indexes that only support one rare admin query unless critical.

## Query Alignment Rules

- Every production query should match a known index path.
- If a query needs post-filtering often, redesign schema or index strategy.
- Re-check index coverage after each product surface expansion.

## Migration-Safe Changes

- Additive changes first, removals later.
- Keep compatibility shims during rollout windows.
- Document old and new read/write paths before cleanup.

## Review Before Merge

- Which query becomes slower with this change?
- Which tenant boundary could be bypassed?
- Which retry path can now duplicate writes?
- Which dashboards or alerts must change?
