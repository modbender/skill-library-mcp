# Jason Zhou Insights

## Key Learnings from Videos

### 1. MCP is About Workflow Automation

MCP isn't just about connecting AI to tools — it's about **automating repetitive workflows** that follow predictable patterns.

Examples:
- Weekly meal planning
- Code review feedback
- Documentation generation
- Report creation

### 2. Resource Templates Enable Scale

Static resources don't scale. Resource templates with parameters do.

**Before:**
```
file://recipes/italian.md
file://recipes/mexican.md
file://recipes/japanese.md
# ... 20 more
```

**After:**
```
file://recipes/{cuisine}.md
# One template, infinite cuisines
```

### 3. Completions Reduce Friction

Nobody remembers exact values. Provide completions:

```javascript
complete: {
  cuisine: (value) => {
    return CUISINES.filter(c => c.startsWith(value));
  }
}
```

Type "ita" → get "italian", "italian-sicilian"

### 4. Prompts Evolve With Context

**Level 1: Static**
```
"Create a meal plan"
```

**Level 2: Parameterized**
```
"Create a meal plan for {cuisine} cuisine"
```

**Level 3: Resource-Embedded**
```
"Create a meal plan" + [embedded recipes resource]
```

The AI works with YOUR data, not general knowledge.

### 5. Cross-Server Workflows

Multiple specialized servers working together:

```
Recipe Server → Print Server → Calendar Server
     ↓              ↓              ↓
  Generate      Physical       Schedule
   Plan          Print          Meals
```

Each server does one thing well.

### 6. Prompt Chains

Break complex tasks into steps:

```
Input → Plan → Generate → Execute → Output
```

Each step feeds into the next.

### 7. Dynamic Prompts

Adapt based on context:

```javascript
if (timeOfDay === 'morning') {
  prompt = 'Plan breakfast-focused meals';
} else {
  prompt = 'Plan dinner-focused meals';
}
```

### 8. External Triggers

Workflows can be activated by:
- Webhooks
- Schedules (cron)
- File changes
- API calls

### 9. Progressive Disclosure

Start simple, reveal complexity as needed:

1. Show file tree (always visible)
2. Show file names (on hover)
3. Show file content (on request)

### 10. Modularity is Key

- Separate servers for separate concerns
- Reusable resources across workflows
- Composable prompts
- Interchangeable components

## Implementation Tips

### Start Small

Don't build the entire system at once:
1. Start with one workflow
2. Add resources as needed
3. Extract reusable components
4. Scale gradually

### Design for Composability

Build components that can be mixed and matched:
- Generic resources
- Parameterized prompts
- Pluggable steps

### Handle Errors Gracefully

```javascript
try {
  const result = await executeStep();
} catch (error) {
  // Fallback
  const result = await fallbackStep();
  // Or retry
  const result = await retryStep();
}
```

### Log Everything

```javascript
console.log({
  step: 'meal-planning',
  input: cuisine,
  output: plan,
  duration: elapsedTime,
  timestamp: new Date()
});
```

## Common Pitfalls

1. **Monolithic Servers**: One server doing everything
2. **Hardcoded Values**: No parameters or templates
3. **Missing Completions**: Users must remember exact values
4. **No Error Handling**: Failures crash the workflow
5. **Tight Coupling**: Steps depend on specific implementations

## Resources

- [Jason Zhou's Channel](https://www.youtube.com/@jasonzhou7824)
- [MCP Official Site](https://modelcontextprotocol.io/)
- [Example Servers](https://github.com/modelcontextprotocol/servers)
