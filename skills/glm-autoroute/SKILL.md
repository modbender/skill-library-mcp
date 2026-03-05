# GLM Autoroute

Binary model routing for ZAI GLM models - lightweight vs heavyweight tasks.

# Introduction
1. **GLM-4.7** is the default model. Only spawn **GLM-5** when the task actually needs it.
2. Use sessions_spawn to run tasks with GLM-5:
```
sessions_spawn({
  task: "<the full task description>",
  model: "zai/glm-5",
  label: "<short task label>"
})
```
3. After done with GLM-5, the main session continues with GLM-4.7 as default.

# Models

## GLM-4.7 (DEFAULT - zai/glm-4.7)

Use for lightweight tasks:
1. Simple Q&A - What, When, Who, Where
2. Casual chat - No reasoning needed
3. Quick lookups
4. File lookups
5. Simple tasks - repetitive tasks, formatting
6. Cron Jobs - if it needs reasoning, THEN ESCALATE TO GLM-5
7. Status checks
8. Basic confirmations
9. Provide concise output, just plain answer, no explaining

**DO NOT:**
- ❌ DO NOT CODE WITH GLM-4.7
- ❌ DO NOT ANALYZE USING GLM-4.7
- ❌ DO NOT ATTEMPT ANY REASONING USING GLM-4.7
- ❌ DO NOT RESEARCH USING GLM-4.7
- If you think the request does not fall into point 1-8, THEN ESCALATE TO GLM-5
- If you think you will violate the DO NOT list, THEN ESCALATE TO GLM-5

## GLM-5 (zai/glm-5)

Use for heavyweight tasks:
1. Coding (any complexity)
2. Analysis & debugging
3. Multi-step reasoning
4. Research & investigation
5. Critical planning
6. Architecture decisions
7. Complex problem solving
8. Deep research
9. Critical decisions
10. Detailed explanations

# Examples

| Task | Model | Why |
|------|-------|-----|
| "Check calendar" | GLM-4.7 | Simple lookup |
| "What time is it?" | GLM-4.7 | Simple Q&A |
| "Heartbeat check" | GLM-4.7 | Routine |
| "Read this file" | GLM-4.7 | Simple lookup |
| "Summarize this" | GLM-4.7 | Basic task |
| "Write Python script" | GLM-5 | Coding |
| "Debug this error" | GLM-5 | Analysis |
| "Research market trends" | GLM-5 | Deep research |
| "Plan migration" | GLM-5 | Complex planning |
| "Analyze this issue" | GLM-5 | Analysis |

# Other Notes

1. When the user asks to use a specific model, use it
2. **Always mention which model is used in outputs** — example: "(GLM-5)" or "(GLM-4.7)" at the end of responses
3. After done with GLM-5 (via sessions_spawn), continue with GLM-4.7 as default
4. If you think the request does not fall into GLM-4.7 use cases, THEN ESCALATE TO GLM-5
5. If you think you will violate the DO NOT list, THEN ESCALATE TO GLM-5
6. Coding = always GLM-5
7. When in doubt → GLM-5 (better safe than sorry)
8. Heartbeat checks → always GLM-4.7 unless complex analysis needed

# Memory Management with sessions_spawn

When spawning GLM-5 sub-agent sessions for ANY task (coding, research, analysis, planning, etc.), follow this pattern:

## Output Rules

**1. Code Output (Important)**
- **Full code ONLY in files** — do NOT include in announce unless explicitly requested
- Provide summary: what was created, file path, status, dependencies
- Full code disclosure ONLY when:
  - User explicitly requests: "Show me the code"
  - Debugging needs code review
  - User wants to improve/modify it

**2. Full Announce for Other Results**
- Research findings, analysis results, solutions → announce FULLY to user
- Do NOT shorten, summarize, or condense non-code output
- User gets complete findings, not a brief summary

**3. Two-Layer Memory Strategy**

**MEMORY.md (Curated Long-Term)**
- ONLY key insights, decisions, lessons, significant findings, preferences
- Clean, concise, actionable
- Skip routine data, step-by-step reasoning, temporary thoughts

**Detailed Reports (Task-Specific Files)**
- For research: `research/YYYY-MM-DD-topic.md` (full findings, data, analysis)
- For coding: add inline docs/README in code folder if needed
- For analysis: output files in relevant project directories

## Examples

**Research task:**
```
sessions_spawn({
  task: "Research X. Announce full findings to user. Write full report to research/YYYY-MM-DD-X.md, then write ONLY key insights to MEMORY.md (clean, concise).",
  model: "zai/glm-5",
  label: "Research X"
})
```

**Coding task:**
```
sessions_spawn({
  task: "Write Python script for X. Save full code to file. Provide summary (what created, path, status, dependencies) in announce. Write key implementation decisions to MEMORY.md (important only).",
  model: "zai/glm-5",
  label: "Python script X"
})
```

Apply this pattern to ALL GLM-5 spawns. Code in files only, summary in announce, full disclosure on request.
