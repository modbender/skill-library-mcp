# Automation Signals

How to recognize tasks that should be scripts.

## Red Flags (Script Immediately)

### Exact Repetition
- "Do the same thing as last time"
- Copy-pasting previous output as template
- Same prompt with different inputs

### Deterministic Transformation
- "Convert X to Y format"
- "Extract field Z from this data"
- "Rename files matching pattern"

### Validation Tasks
- "Check if this JSON is valid"
- "Verify all links work"
- "Ensure fields match schema"

### Fixed Workflows
- "Run tests, then deploy if green"
- "Commit, push, open PR"
- "Download, process, upload"

## Yellow Flags (Consider Scripting)

### Mostly Deterministic
- 90% rule-based, 10% judgment
- Solution: Script the 90%, LLM the 10%

### Complex But Stable
- Many steps, but same every time
- Solution: Script the orchestration

### Frequent But Varied
- Same task type, different specifics
- Solution: Parameterized script

## Token Waste Indicators

Calculate if you're burning tokens:

```
Monthly token cost = (tokens per run) × (runs per month) × ($/1M tokens)

If monthly cost > 1 hour of scripting time → script it
```

### Examples
| Task | Tokens/run | Runs/month | Cost | Verdict |
|------|------------|------------|------|---------|
| Format JSON | 500 | 100 | $0.15 | Script (5 min to write) |
| Parse logs | 2000 | 50 | $0.30 | Script (30 min to write) |
| Write email | 1000 | 20 | $0.06 | LLM (needs judgment) |

## Questions to Surface Opportunities

Ask yourself:
- "Have I done this exact thing before?"
- "Could I write instructions a machine could follow?"
- "Am I using the LLM as a fancy regex?"
- "Would a junior dev with a script do this faster?"

## Context Patterns

Notice when you:
- Include examples of desired output → probably scriptable
- Specify exact format requirements → definitely scriptable
- Say "just like before" → should already be scripted
- Provide transformation rules → pure automation candidate
