---
name: Detailed auto-implement Issue
description: High-precision Issue template for maximum output quality
---

# [auto] <TITLE>

## Context
<Why this task exists. What problem it solves.>

## Agent Instructions (optional)
Read agents/<agent-name>/AGENTS.md and SOUL.md first.
Read skills/<skill-name>/SKILL.md for domain-specific instructions.

## File Structure
- `path/to/new-file.ext` — <description>
- `path/to/existing-file.ext` — <what to modify>

## Detailed Specification

### Function/Module Signatures
```
function_name(param1: type, param2: type) → return_type
  - description of behavior
  - error handling: <what to do on failure>
```

### Integration Points
- <which existing files/functions this connects to>
- <specific line numbers or function names if known>

### Test Cases
1. Input: X → Expected output: Y
2. Input: Z → Expected output: W
3. Edge case: <description> → Expected: <behavior>

## Acceptance Criteria
- [ ] All specified files created/modified
- [ ] All test cases pass
- [ ] No regressions in existing tests
- [ ] Code follows project conventions

## Constraints
- Max diff size: ~300 lines
- Timeout: 15 minutes
- Dependencies: <list any required packages or tools>
