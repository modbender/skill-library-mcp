# Heartbeat Budget Audit Snippet

Add this as a step in your HEARTBEAT.md:

```markdown
### Agent Budget Audit

Run the budget audit to check all agent spending and enforce governance rules:

\```bash
python3 /path/to/workspace/scripts/budget_audit.py
\```

- Automatically resets daily counters at midnight
- Yellow warning at 80%, Red at 100%, Emergency demotion at 200%
- 3 consecutive overbudget days → automatic demotion (loses mesh spawn privileges)
- If any agent is demoted → alert human: "⛔ Agent {name} demoted: {reason}"
- If any agent is in Red → note in daily log
- If all green → silent
```
