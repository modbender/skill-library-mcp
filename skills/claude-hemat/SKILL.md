# ClaudeHemat

# Introduction
1. **Haiku 4.5** is the default model. Only spawn **Sonnet 4.5** or **Opus 4.6** when the task actually needs either of them
2. Check **Model Rules** section to decide which model to use!
2. Use sessions_spawn to use more advanced models
```
sessions_spawn(
  message: "<the full task description>",
  model: "anthropic/claude-sonnet-4-5",
  label: "<short task label>"
)
```
```
sessions_spawn(
  message: "<the full task description>",
  model: "anthropic/claude-opus-4-6",
  label: "<short task label>"
)
```

# Model Rules
## Haiku 4.5
1. Simple Q&A - What, When, Who, Where
2. Casual chat - No reasoning needed
3. Quick lookups
4. File lookups
5. Simple tasks - May but not limited to repetitive tasks
6. Cron Jobs, if it needs reasoning, THEN ESCALATE TO THE NEXT ADVANCED MODEL
6. Basically everything that doesn't need any thinking
7. Provide concise output, just plain answer, no explaining
8. DO NOT CODE WITH HAIKU 4.5
9. DO NOT ANALYZE USING HAIKU 4.5
10. DO NOT ATTEMPT ANY REASONING USING HAIKU 4.5
11. If you think the request does not fall into point 1-6, THEN ESCALATE TO THE NEXT ADVANCED MODEL
11. If you think you will violate point 8-10, THEN ESCALATE TO THE NEXT ADVANCED MODEL

## Sonnet 4.5
1. Analysis - Why, How
2. Code
3. Planning
4. Reasoning
5. Comparisons
6. Reporting
7. If you think the request is pretty critical to the user, THEN ESCALATE TO THE NEXT ADVANCED MODEL

## Opus 4.6
1. Deep research
2. Critical decisions
3. Extreme complex reasoning
4. Extreme complex planning
5. Detailed explanation

# Other Notes
1. When the user asks you to use a specific model, use it
2. Always put which model is used IN EVERY OUTPUTS
3. After you are done with more advanced models (Sonnet 4.5 or Opus 4.6), revert back to Haiku 4.5 as the default model