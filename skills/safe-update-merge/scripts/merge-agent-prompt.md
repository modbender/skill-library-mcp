# Merge Conflict Resolution Prompt

You are resolving a git merge conflict for a file in the OpenClaw project.
Your fork has custom features that MUST be preserved while integrating upstream changes.

## Context

**File:** {{FILE_PATH}}
**Intent of our changes:** {{INTENT}}
**Must preserve these patterns:** {{MUST_PRESERVE}}

## Three-Way Input

> **Note:** Secrets and credentials have been redacted with `[REDACTED]` placeholders.
> Preserve the redaction markers in your output — they will be restored after merge.

### MERGE BASE (common ancestor)
```
{{BASE_CONTENT}}
```

### OURS (our fork's version)
```
{{OURS_CONTENT}}
```

### THEIRS (upstream's version)
```
{{THEIRS_CONTENT}}
```

## Your Task

1. **Understand upstream's changes**: What did they add, remove, or refactor?
2. **Understand our changes**: What did we add? (Described in "Intent" above)
3. **Merge both**: Produce a resolved file that includes BOTH:
   - All upstream improvements (new features, bug fixes, refactors)
   - All our custom additions (described in intent)
4. **Verify preservation**: Every item in "Must preserve" MUST appear in your output.

## Rules

- If upstream renamed/moved something we depend on, update our code to use the new name
- If upstream deleted something we extend, keep our extension but adapt it to the new structure
- If upstream added imports we don't have, include them
- If we added imports upstream doesn't have, keep them
- Prefer upstream's code style if it changed (formatting, semicolons, etc.)
- NEVER output merge conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
- NEVER remove `[REDACTED]` placeholders — they will be restored post-merge
- Output ONLY the resolved file content, no explanation

## Output

The complete resolved file content, ready to write to disk.
