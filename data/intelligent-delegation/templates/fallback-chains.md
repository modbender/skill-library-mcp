# Fallback Chains — Adaptive Re-routing

## Purpose
When a task fails, don't just report failure — attempt automatic recovery.

## Failure Detection
Task has failed when:
1. Agent reports failure or crashes
2. Verification checks fail (exit code 1)
3. Agent times out (no response past expected + 50% buffer)
4. Output is clearly wrong (empty, truncated, nonsensical)

## Diagnosis Guide

| Symptom | Likely Cause | Response |
|---------|-------------|----------|
| Context overflow | Input too large | Switch to script |
| Timeout | Task too complex | Decompose further |
| Empty output | Lost track of goal | Retry with tighter prompt |
| Wrong format | Ambiguous spec | Retry with explicit example |
| Factually wrong | Hallucination | Try different agent |

## Standard Fallback Chains

### Research Tasks
```
1. Balanced-tier agent
   ↓ failure
2. Retry with tighter scope
   ↓ failure
3. Capable-tier agent
   ↓ failure  
4. Main agent directly
   ↓ failure
5. ESCALATE to human
```

### Code/Build Tasks
```
1. Capable-tier agent
   ↓ failure
2. Retry with error output
   ↓ failure
3. Main agent writes code
   ↓ failure
4. ESCALATE with details
```

### Data Processing
```
1. NEVER delegate large data to LLM agents
2. Write a script directly
   ↓ failure
3. Have coder agent fix script
   ↓ failure
4. ESCALATE
```

## When to Escalate to Human
- All fallback options exhausted
- Irreversible actions (emails, transactions)
- Ambiguity that can't be resolved
- Security concern detected

## Escalation Format
```
⚠️ Task Failed: [TASK_ID]

Tried:
1. [Method] → [Result]
2. [Method] → [Result]

Root cause: [Diagnosis]
Options:
A) [Suggestion]
B) [Suggestion]
```
