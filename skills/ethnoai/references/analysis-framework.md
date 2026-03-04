# Analysis Framework for Daily Distillation — v2.0

## Methodology

The daily distillation follows a verbatim-first qualitative analysis approach enriched with ethnographic analysis, cost data, and retrospective case studies. User quotes are the primary evidence; researcher interpretation layers on top. Every insight in the report must be traceable to at least one verbatim or quantitative data point.

## Step 1: Data Assembly

Read all files for the target date:
- `~/.uxr-observer/sessions/YYYY-MM-DD/observations.jsonl`
- `~/.uxr-observer/sessions/YYYY-MM-DD/surveys.jsonl`

Parse each JSONL file line-by-line. Separate post-task surveys from end-of-day surveys.

## Step 2: Task-Level Pairing

For each task observed, create a paired record:
- The **observation** (what you saw: intent, approach, outcome, friction signals, sentiment, verbatims, cost, use case, inferred needs)
- The **task context summary** (the narrative of what happened)
- The **ethnographic analysis** (use case, workflow pattern, capabilities, effort/value, inferred needs)
- The **post-task survey** (the user's self-reported rating and verbatim responses)

This pairing is the atomic unit of analysis. Each task should be presentable as a self-contained story: here's what happened, here's the deeper analysis, here's how the user felt about it, here's what they said, and here's what it cost.

## Step 3: Verbatim Organization

Collect ALL verbatims from the day — from observations and from survey responses. For each verbatim, verify the researcher summary header accurately interprets the quote.

Organize into thematic categories:

### Positive Experiences
Quotes expressing satisfaction, delight, surprise at quality, appreciation for speed, etc.

### Pain Points & Frustrations
Quotes expressing frustration, confusion, disappointment, unmet expectations.

### Expectations & Mental Models
Quotes that reveal what the user expected to happen, how they think the tool should work, or gaps between their mental model and reality.

### Suggestions & Wishes
Quotes where the user explicitly or implicitly suggests improvements or alternatives.

### Workflow & Context
Quotes that reveal the user's broader workflow, goals, or constraints that inform how they use the tool.

If a quote fits multiple categories, include it in the most salient one and cross-reference.

## Step 4: Quantitative Summary

Calculate:
- Total tasks observed
- Post-task survey completion rate (completed / total tasks)
- Average post-task satisfaction rating
- End-of-day overall rating
- Frustration rate (% of post-task surveys where friction = yes)
- Delight rate (% of tasks with positive/delighted sentiment signals)
- Friction event count and type distribution
- Total daily cost (actual vs. estimated, broken down by model and category)
- Average cost per task
- Cost per task category
- PII redaction counts by category

## Step 5: Use-Case Synthesis

From the Ethnographer's data:
- List all use cases active today with their task counts
- For each use case, calculate aggregate satisfaction and cost
- Identify the use case with the best and worst satisfaction scores
- Note workflow patterns (iterative_refinement tends to correlate with what satisfaction levels?)
- Surface any use cases that span multiple days (cross-reference prior reports)

## Step 6: Survey Cross-Reference

Compare post-task survey responses with observation data:

- **Rating vs. friction signals**: Does the user's self-reported rating align with the friction you observed? Divergences are interesting — a high rating despite observed friction suggests high tolerance or low expectations. A low rating despite no observed friction suggests an unmet need you didn't detect.
- **Frustration reported vs. detected**: Did the user report frustration on tasks where you didn't observe friction signals? This reveals invisible pain points.
- **Improvement suggestions**: What themes emerge across improvement_suggestion responses? Pattern these.
- **Cost vs. satisfaction**: Do higher-cost tasks correlate with higher or lower satisfaction? Is there a sweet spot?

## Step 7: End-of-Day Integration

The end-of-day survey is the user's reflective summary. Compare it with the task-level data:

- Does their overall rating match the average of their task ratings? If lower, the day felt worse than individual moments suggest (cumulative fatigue). If higher, good moments outweighed the bad.
- Do their highlights match the tasks with highest ratings? Do their lowlights match the highest-friction tasks?
- Their "one thing I'd change" response is high-signal — it's the user's prioritized pain point after a full day.

## Step 8: Needs & Capability Analysis

From the Ethnographer's inferred needs:
- Deduplicate and rank needs by frequency (how many tasks surfaced this need)
- Cross-reference with verbatims — did the user ever explicitly state this need, or is it purely behavioral?
- Note capability gaps: things users don't know about that could help them

## Step 9: Pattern Identification

Look across all task records for:

- **Capability clusters**: Task categories that consistently get high or low ratings
- **Friction hotspots**: Specific tools, file types, or interaction patterns correlating with frustration
- **Delight drivers**: What all highly-rated tasks have in common
- **Recovery patterns**: Tasks that started with friction but ended positively (and vice versa)
- **Verbatim echoes**: Similar language across multiple survey responses (strong theme signal)
- **Cost patterns**: Which task types are expensive? Are expensive tasks more satisfying?
- **Need patterns**: Which inferred needs appear most frequently?

## Step 10: Trend Analysis (multi-day)

If previous days' reports exist in `~/.uxr-observer/reports/`, look for:

- Rating trajectories (improving? declining? volatile?)
- Persistent vs. one-off pain points
- Evolving usage patterns (new task categories appearing, old ones dropping)
- Cost trends (spending increasing, decreasing, or stable?)
- Survey fatigue indicators (declining response length, more one-word answers)
- Need evolution (are inferred needs being addressed or accumulating?)

## Step 11: Super Summary Integration

After the Super Summary Miner has produced case studies:
- List all selected notable tasks in the report's Attachments section
- Reference specific case studies when they support insights in the Patterns section
- Note the selection criteria each case study met

## Step 12: Recommendations

Generate 2-4 actionable recommendations grounded in today's data:

- Each recommendation must cite specific verbatims and/or quantitative data
- Prioritize by frequency x severity (a frustration hitting 4/7 tasks outranks one hitting 1)
- Include at least one recommendation related to cost efficiency if cost data is available
- Include at least one recommendation related to unmet needs from ethnographic analysis
- Frame constructively: "Users valued X; extending this to Y could address the friction seen in Z"

## Step 13: PII & Sensitive Work Summary

Aggregate PII redaction data:
- How many tasks involved sensitive data?
- What categories of PII appeared most frequently?
- What does this tell us about how users interact with sensitive content through OpenClaw?
- Are there patterns (e.g., financial tasks always have friction, communication tasks always involve names)?

## Quality Checks

Before finalizing:

1. Every insight traceable to a verbatim or data point? ✓
2. Task context summaries written for an outside reader? ✓
3. Verbatim headers accurately interpret quotes without editorializing? ✓
4. Both positive and negative findings represented? ✓
5. Uncertainty flagged where sample is small? ✓
6. End-of-day survey fully integrated, not just appended? ✓
7. Cost data included and labeled (actual vs. estimated)? ✓
8. Use-case analysis synthesized? ✓
9. Inferred needs listed with supporting evidence? ✓
10. PII fully redacted in all output? ✓
11. Super summary case studies referenced where relevant? ✓
