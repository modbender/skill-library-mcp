# Error Recovery Patterns

## Timeout Handling

```
Sub-agent silent for >5 minutes:
1. Send ping: "Status check - respond with current progress"
2. Wait 60s
3. If no response: kill session, log last known state
4. Retry with same task + note: "Previous attempt timed out at [state]"
5. If second timeout: escalate to larger model or abort
```

## Escalation Logic

```
attempt = 1
tier = SMALL

while attempt <= 3:
    result = spawn(task, tier)
    
    if result.quality >= threshold:
        return result
    
    if attempt < 3:
        tier = escalate(tier)  # SMALL→MEDIUM→LARGE
        attempt += 1
    else:
        abort("Failed after 3 attempts across all tiers")
```

## Common Failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| Hallucinated files | Small model guessing | Use Medium, provide explicit file list |
| Incomplete output | Context too large | Chunk task, reduce context |
| Wrong format | Ambiguous instructions | Add output example in task |
| Infinite loop | Unclear done condition | Add explicit stop criteria |
| Works locally, fails in spawn | Missing context | Include env vars, paths |

## Recovery Checklist

Before retrying failed task:
- [ ] Was the task actually clear? (re-read it fresh)
- [ ] Did I provide all needed context?
- [ ] Is the model tier appropriate?
- [ ] Should I chunk this into smaller tasks?
- [ ] Is there a blocker the sub-agent can't resolve?

## Abort Criteria

Stop trying when:
- Same error 3 times with different approaches
- Sub-agent requests info only user can provide
- Cost of retries > cost of doing it yourself
- Task fundamentally requires main agent context
