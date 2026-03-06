# Gate: Cross-Verify (BUILD mode only)

**Question:** If you only had the tests and the PRD, would you write the same code?

## Process

1. Take the final test suite + PRD
2. In a **fresh session** (different model if possible): generate a new implementation from ONLY tests and PRD
3. Diff the two implementations
4. Small diffs (style, naming) = fine
5. Large diffs (different algorithms, missing features) = investigate

## Pass/Fail

- **Pass:** Core logic is structurally similar. No missing features in either version.
- **Fail:** Re-generated version is fundamentally different → tests don't specify behavior well enough, or original took a wrong path.
