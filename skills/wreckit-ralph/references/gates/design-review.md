# Gate: Design Review

**Question:** Is the architecture well-structured, low-coupling, and fit for purpose?

## What to Check

- **Circular dependencies:** modules that import each other in a cycle indicate tangled design
- **God modules (high fan-in):** files imported by many others (fan-in > 8) are fragile single points of failure
- **God modules (high fan-out):** files that import many others (fan-out > 10) often do too much
- **Orphan files:** source files not imported by anything and not an entry point — likely dead code
- **Layering violations:** e.g., data layer importing from presentation layer
- **Clear data flow:** inputs → transform → outputs should be traceable without circular reads

## How to Run

```bash
scripts/design-review.sh [project-path]
```

The script auto-detects language and runs appropriate analysis:
- **JS/TS:** attempts `npx madge --circular --json .`, falls back to manual import graph scan
- **Python:** scans `import` / `from ... import` statements
- **Go:** scans `import` blocks

Output is JSON to stdout. Human summary goes to stderr.

### Manual interpretation (if script unavailable)

1. List all source files
2. For each file, extract all imports (require/import/from)
3. Build dependency graph: `{file → [files it depends on]}`
4. Compute fan-in: count how many files import each file
5. Compute fan-out: count how many files each file imports
6. Run DFS to detect cycles
7. Flag any file with fan-in > 8 as a potential god module

## Pass / Fail Criteria

### PASS ✅
- No circular dependencies detected
- No god modules (fan-in ≤ 8 for all files)
- Clear, acyclic data flow
- Orphan files < 5% of total

### WARN ⚠️
- God modules exist (fan-in > 8) but no circular deps
- Orphan files present (5–15% of total)
- High fan-out modules (fan-out > 10) suggesting bloated responsibilities

### FAIL ❌
- Any circular dependency found
- God modules with fan-in > 10
- Orphan files > 15% of total

## Example Output

```json
{
  "project": "/path/to/project",
  "language": "ts",
  "total_files": 42,
  "circular_deps": [],
  "god_modules": [{"file": "src/utils/helpers.ts", "fan_in": 9}],
  "orphan_files": [],
  "avg_fan_in": 2.1,
  "avg_fan_out": 1.8,
  "verdict": "WARN",
  "summary": "No circular deps. 1 god module (helpers.ts, fan-in=9)."
}
```
