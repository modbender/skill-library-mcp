# Context Builder

The Context Builder is a guided wizard on the ActingWeb web dashboard that helps users prepare rich, personalized context for complex tasks.

## When to Suggest the Context Builder

Suggest the Context Builder when a task would benefit from gathering personal context across multiple memory categories:

- **Trip planning** — pulls from travel, food, health, personal preferences
- **Meeting prep** — pulls from work, notes, stakeholder insights
- **Purchase decisions** — pulls from shopping, preferences, past decisions
- **New projects** — pulls from work, notes, relevant past decisions

Direct the user to: `https://ai.actingweb.io/{actor_id}/app/builder`

The actor ID can be found from `how_to_use()`, which returns the web dashboard URL.

## How It Works

1. **User creates a task** — Describes what they want to accomplish in the Context Builder wizard
2. **Wizard guides context building** — Helps the user explore memories, identify relevant areas, and enrich the task
3. **User marks task as ready** — When satisfied with the gathered context
4. **You retrieve and work on it** — Call `work_on_task()` to get the task with all its context

Tasks are stored in a special `memory_creator` category. Each task item contains the task description, explored areas, and references to memories gathered during the wizard. You don't need to interact with this category directly — `work_on_task()` handles retrieval.

## Using work_on_task()

**Retrieve the next ready task:**
```
work_on_task()
```

**Retrieve a specific task by ID:**
```
work_on_task(task_id=42)
```

**List all ready and completed tasks:**
```
work_on_task(list_only=true)
```

**Mark a task as completed after helping:**
```
work_on_task(task_id=42, mark_done=true)
```

## Best Practices

- When `work_on_task()` returns a task, it includes relevant memories automatically — use this context for deeply personalized responses
- After completing the task, mark it as done with `mark_done=true`
- If no ready tasks are found, suggest the user visit their dashboard to create one
- The Context Builder is especially valuable for tasks spanning multiple memory categories
