# Task Routing

## Routing Decision Flow

```
Request arrives
    │
    ├─ Explicit mention: "Luna, do X"
    │   └─ Route to Luna directly
    │
    ├─ Explicit self: "I'll handle this"
    │   └─ Main agent handles
    │
    └─ No mention: analyze request
         │
         ├─ Matches employee role?
         │   ├─ High confidence → suggest: "Want Luna to handle this?"
         │   └─ Auto-route if user enabled auto-delegation
         │
         └─ Generic/orchestration?
             └─ Main agent handles
```

## Role Matching

Load `registry.json` on each request. Match against:

1. **Role keywords**: "research" → Research Assistant
2. **File patterns**: reviewing `.py` files → Code Reviewer
3. **Task type**: "write tests" → Test Writer

## Auto-Delegation Rules

User can enable per-employee:

```json
"autoDelegation": {
  "enabled": true,
  "confidenceThreshold": 0.8,
  "excludePatterns": ["urgent", "confidential"]
}
```

## Execution Flow

When routing to employee:

```
1. Load employee.json → get config
2. Load skill (linked/embedded/clawhub)
3. Inject memory/context.md as context
4. Spawn as subagent with employee's model
5. Execute task
6. Log to logs/YYYY-MM-DD.md
7. Update stats in employee.json
8. Return result to main agent
```

## Handoff Protocol

When employee needs to escalate:

```
1. Employee recognizes escalation trigger
2. Returns: "ESCALATE: [reason] | context: [summary]"
3. Main agent receives, presents to user
4. User decides: handle manually or redirect
```

## Multi-Employee Tasks

For complex tasks requiring multiple employees:

```
1. Main agent decomposes task
2. Route subtasks to relevant employees
3. Collect results
4. Synthesize and present
```

Example:
- "Research X and write a report"
- → Research Assistant: gather information
- → Writer: draft report from research
- → Main agent: review and deliver

## Routing Anti-Patterns

- ❌ Routing to inactive/retired employees
- ❌ Routing outside employee's permissions
- ❌ Auto-delegating without checking autonomy level
- ❌ Routing urgent tasks to shadow-level employees
