# Pipeline Pattern

Sequential chain where each agent's output feeds the next.

## When to Use

- Multi-stage processing (research → analyze → write)
- Workflows with natural handoff points
- When each stage transforms or builds on the previous

## Implementation

```python
stages = [
    {"label": "stage-1-research", "task": "Research the topic: {topic}"},
    {"label": "stage-2-analyze", "task": "Analyze this research and identify key themes:\n\n{prev_result}"},
    {"label": "stage-3-write", "task": "Write a report based on this analysis:\n\n{prev_result}"},
]

prev_result = ""

for i, stage in enumerate(stages):
    # Inject previous result into task
    task = stage["task"].format(topic=topic, prev_result=prev_result)
    
    # Spawn and wait
    sessions_spawn(task=task, label=stage["label"])
    wait_for_completion(stage["label"])
    
    # Extract result for next stage
    prev_result = get_agent_result(stage["label"])
```

## Checkpoint Files

For long pipelines, write intermediate results to files:

```
pipeline-state/
├── stage-1-research.md    # Research output
├── stage-2-analysis.md    # Analysis output
└── stage-3-report.md      # Final report
```

Benefits:
- Resume from checkpoint on failure
- Human can review intermediate stages
- Debugging visibility

## Error Handling

```python
for stage in stages:
    try:
        run_stage(stage)
    except StageFailure:
        # Options:
        # 1. Retry this stage
        # 2. Rollback to previous checkpoint
        # 3. Escalate to human with partial progress
        # 4. Skip and continue (if stage is optional)
        pass
```

## Example: Content Pipeline

```
Input: "Write a blog post about AI agents"

Stage 1 - Research Agent:
  Task: "Research current trends in AI agents"
  Output: Research notes (saved to research.md)

Stage 2 - Outline Agent:
  Task: "Create a blog post outline from this research: {research}"
  Output: Outline (saved to outline.md)

Stage 3 - Draft Agent:
  Task: "Write a draft blog post following this outline: {outline}"
  Output: Draft (saved to draft.md)

Stage 4 - Edit Agent:
  Task: "Edit and polish this draft: {draft}"
  Output: Final post (saved to final.md)
```

## vs Fan-Out

| Pipeline | Fan-Out |
|----------|---------|
| Sequential | Parallel |
| Each stage depends on previous | Independent tasks |
| Slower but structured | Faster but no dependencies |
| Natural for transformation workflows | Natural for divide-and-conquer |
