---
name: blocker-min-input
description: When blocked, report exact blocker + attempts made + minimum user input needed. Enable fast unblock without back-and-forth.
---

# Blocker Minimum Input

When blocked, provide everything needed for fast unblock. No back-and-forth.

## Problem

Agents often:
- Say "blocked" without specifics
- Don't report what was tried
- Ask vague questions
- Require multiple clarifications

## Workflow

### 1. Blocker Report Format

```markdown
**Blocker**: Exact error/blocker text
**Attempts Made**: 
- Attempt 1: what + result
- Attempt 2: what + result
**Minimum Unblock Input**: Smallest user action needed
**Fallback Option**: Alternative if user cannot unblock
```

### 2. Attempt Requirements

Before reporting blocker:
- Retry same approach with corrected parameters (1x)
- Try one fallback path
- If both fail, report with evidence

### 3. Minimum Input Examples

| Blocker | Minimum Input |
|---------|---------------|
| Missing API key | `Run: openclaw configure --section web` |
| Permission denied | `Grant write access to: D:\folder` OR `Use fallback: C:\workspace\folder` |
| Auth failure | `Check token in: openclaw.json` |

## Executable Completion Criteria

| Criteria | Verification |
|----------|-------------|
| Blocker text exact | Quote error message verbatim |
| Attempts listed | At least 2 attempts documented |
| Minimum input specific | Single command or action |
| Fallback provided | Alternative path exists |

## Privacy/Safety

- No credentials in blocker reports
- Redact tokens/keys from error messages
- Use generic paths when sensitive

## Self-Use Trigger

Use when:
- Any tool call fails twice
- User input required to proceed
- Permission/auth issues detected

---

**One report. One input. Unblock fast.**
