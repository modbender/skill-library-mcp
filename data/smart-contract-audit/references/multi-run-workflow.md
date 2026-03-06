# Multi-Run Consolidation Workflow

## Why Multiple Runs?

LLM-based audits suffer from **attention variability** — each run focuses on slightly different code paths, patterns, and edge cases. A single run typically catches 60-80% of findable issues. Running 2-3 times and taking the UNION of all findings significantly improves coverage.

## Process

### 1. Run the Full Audit 2-3 Times
Each run should be independent — don't seed findings from previous runs into specialist agents (this biases attention toward known issues and away from new ones).

### 2. Collect All Findings
After all runs, gather every Medium+ finding from each run into a single list.

### 3. Deduplicate
Two findings are duplicates if they:
- Reference the same contract and function/line
- Describe the same vulnerability mechanism
- Have the same attack scenario

Minor wording differences don't make findings unique.

### 4. Resolve Severity Conflicts
If the same finding appears at different severities across runs:
- The Triager reviews the evidence from all runs
- Higher severity wins IF the higher-severity argument is well-reasoned
- If the higher severity was based on incorrect assumptions, use the lower severity
- Document the conflict and resolution in Multi-Run Notes

### 5. Union Unique Findings
Findings that appear in only ONE run are NOT automatically dismissed. They may represent:
- Edge cases that one run's attention pattern caught
- Valid issues that other runs' agents happened to miss
- False positives that one run generated

The Triager validates all unique findings with extra scrutiny.

## Consolidation Notes Template

```markdown
## Multi-Run Consolidation Notes

### Run Summary
| Run | Date | Findings (M+) | New Unique |
|-----|------|---------------|------------|
| 1   | ...  | X             | X          |
| 2   | ...  | Y             | Z          |
| 3   | ...  | W             | V          |

### Duplicates Merged
- [Finding ID]: Appeared in runs [1, 2]. Severity: [agreed/conflicted]. Resolution: [...]

### Unique Findings (Single Run)
- [Finding ID]: Only in run [N]. Triager verdict: [VALID/DISMISSED]. Reason: [...]

### Severity Conflicts
- [Finding ID]: Run 1 said [High], Run 2 said [Medium]. Resolution: [Medium — because ...]
```

## Referencing Previous Run Reports

When consolidating, read previous run reports from the audit output directory. Look for:
- The findings section (severity, location, description)
- The triager verdicts
- Coverage evidence sections (negative evidence is valuable across runs)

Previous reports are typically at paths like:
- `test-report-*-v1.md`
- `test-report-*-v2.md`
- Or specified by the user
