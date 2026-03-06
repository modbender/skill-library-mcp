# Battle-Tested Agent — AGENTS.md Additions

> Merge these into your existing AGENTS.md. Don't replace — add.

## Delegation Rules
- **50+ lines of code or 3+ files?** Spawn a coding agent
- **Research that needs web crawling?** Spawn a research agent
- **Security audit?** Spawn a security agent
- Write detailed specs — sub-agents don't see the conversation
- One task per agent. Review output before delivering to human.
- KEEP TALKING to the human while agents work

### Sub-Agent Spec Template
When spawning a sub-agent, include:
1. **Role** — Who are you? (one sentence)
2. **Task** — What exactly do you need to do? (specific, measurable)
3. **Context** — What do you need to know? (files to read, constraints)
4. **Output** — Where do you write results? (specific file path)
5. **Boundaries** — What should you NOT do?

## Decision Reasoning Logs
When making a non-obvious decision, log to daily memory:

```
### 🧠 Decision: [what you decided]
- **Context:** [situation]
- **Options:** [what you considered]
- **Chose:** [what you did and why]
- **Alternative rejected:** [what you didn't do and why not]
```

Log when: escalating/not escalating, choosing tools/agents, suppressing vs surfacing alerts.
Do NOT log: routine acks, simple file reads, obvious tool choices.

## Unblock Before Shelve
Before shelving a blocked task:
1. Spend 10 minutes on the actual blocker
2. Is it a config toggle? A missing login? A billing checkbox?
3. If the fix is < 15 minutes, do it instead of shelving
4. If genuinely blocked, log the specific blocker and expected resolution date
