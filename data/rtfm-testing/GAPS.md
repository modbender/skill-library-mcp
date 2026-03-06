# Gap Report Specification

Standard format for reporting documentation gaps found during RTFM Testing.

## Gap Types

| Type | Description | Example |
|------|-------------|---------|
| `MISSING_STEP` | A required action is not documented | "Run database migrations" never mentioned |
| `MISSING_PREREQ` | A prerequisite is not listed | Requires Docker but doesn't say so |
| `UNCLEAR` | Instructions are ambiguous | "Configure the service" without specifics |
| `INCORRECT` | Documentation is wrong | Says port 3000 but app uses 8080 |
| `MISSING_CONTEXT` | Assumes undocumented knowledge | References "the config file" without path |
| `ORDERING` | Steps are in wrong sequence | Tells you to run app before installing deps |

## Gap Report Format

```
[GAP] <TYPE>
Location: <section/step in docs, or "missing entirely">
Problem: <specific description of the gap>
Impact: <what the user cannot do because of this>
Suggestion: <concrete fix for the docs>
```

## Severity Levels (Optional)

For prioritization:

- **BLOCKING** — Cannot proceed without this information
- **DEGRADED** — Can proceed but with confusion or workarounds
- **MINOR** — Inconvenient but not blocking

## Aggregation

After testing, aggregate gaps into categories for doc maintainers:

```
## Gap Summary

Total gaps: 7
- MISSING_STEP: 2 (both BLOCKING)
- MISSING_PREREQ: 3 (2 BLOCKING, 1 MINOR)  
- UNCLEAR: 2 (both DEGRADED)

Recommended priority:
1. Add prerequisites section (3 gaps)
2. Add explicit commands to steps 2, 5 (2 gaps)
3. Clarify configuration section (2 gaps)
```

## Tracking Improvement

Track Cold Start Score across iterations:

| Iteration | Gaps Found | Blocking | Result |
|-----------|------------|----------|--------|
| 1 | 7 | 5 | FAILURE |
| 2 | 3 | 1 | PARTIAL |
| 3 | 1 | 0 | SUCCESS |

Docs are "RTFM Certified" when a fresh tester achieves SUCCESS with zero blocking gaps.
