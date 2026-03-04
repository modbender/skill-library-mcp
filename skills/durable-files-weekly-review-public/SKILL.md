---
name: durable-files-weekly-review-public
description: Run a weekly token-optimization audit for durable instruction files in any OpenClaw workspace, generate a markdown report, and propose approval-gated cleanup actions. Use when users want to keep AGENTS/USER/TOOLS/MEMORY-style docs lean without silent deletions.
---

# Durable Files Weekly Review (Sanitized / ClawHub)

Use this skill to audit durable instruction files and prepare cleanup proposals.

## Default scope
Audit these files relative to a workspace root:
- `AGENTS.md`
- `SOUL.md`
- `USER.md`
- `TOOLS.md`
- `MEMORY.md`
- `IDENTITY.md`
- `PRIORITIES.md`
- `SKILLS.md`
- `projects.md`

## Run
```bash
python3 scripts/durable_files_review_generic.py --root .
```

Optional:
```bash
python3 scripts/durable_files_review_generic.py --root /path/to/workspace --out knowledge/reports/durable-files
```

## Workflow
1. Run scanner.
2. Open generated report.
3. Summarize top token-heavy files + stale markers.
4. Propose cleanup in batches.
5. **Require explicit user approval before any deletions.**
6. Apply approved edits and post concise changelog.

## Success output
- Dated markdown report with metrics/findings
- Clear approval queue for removals
- No silent content removal
