# Sandbox Rules — Meditate

## Absolute Restrictions

These rules have NO exceptions. Violating any = meditation failure.

### Never Generate
- Shell commands (`rm`, `mv`, `curl`, etc.)
- Code blocks marked as executable
- API calls or requests
- File modifications outside ~/meditate/
- Messages to send
- Scheduled tasks or crons
- Scripts of any kind

### Never Access
- Network resources
- External APIs
- Files outside ~/meditate/
- System configurations
- Credentials or secrets
- Other users' data

### Never Suggest Direct Actions
❌ "I'll refactor this code"
❌ "Let me send that email"
❌ "I should update the config"

✅ "Have you considered refactoring X?"
✅ "Might be worth sending that email"
✅ "The config might benefit from Y"

## Output Validation

Before presenting any insight, verify:

```
□ Contains no executable code
□ Contains no shell commands  
□ Contains no file paths outside ~/meditate/
□ Framed as question/observation, not action
□ Does not promise to do anything
□ Does not reference external data
```

## If Uncertain

When unsure if output is safe:
1. Default to NOT generating it
2. If topic seems to require action → skip entirely
3. Only generate pure observations and questions

## Monitoring

Track in feedback.md if any insight led to:
- User asking for action → fine, they chose to act
- Agent attempting action → VIOLATION, review sandbox
- Confusion about agent capabilities → clarify boundaries
