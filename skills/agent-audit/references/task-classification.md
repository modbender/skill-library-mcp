# Task Classification Heuristics

## Signal-Based Classification

The audit classifies tasks by analyzing multiple signals from cron history and config.

### Simple Task Signals (→ cheapest model)
- **Output length**: Consistently under 500 tokens
- **Name patterns**: "health check", "status", "monitor", "ping", "reminder", "notify", "alert"
- **Runtime**: Under 30 seconds average
- **Token ratio**: Input tokens >> output tokens (reading a lot, writing little)
- **Success rate**: >95% (task is predictable/deterministic)
- **Payload type**: `systemEvent` payloads are almost always simple
- **No tool use**: Tasks that don't call external tools

### Medium Task Signals (→ mid-tier model)
- **Output length**: 500-2000 tokens
- **Name patterns**: "draft", "research", "summary", "analysis", "report", "brief", "scan", "digest"
- **Runtime**: 30 seconds to 3 minutes
- **Some creativity**: Content generation, but with templates/guidelines
- **Tool use**: 1-3 tool calls per run
- **Moderate reasoning**: Needs to make decisions but within clear parameters

### Complex Task Signals (→ top-tier model)
- **Output length**: 2000+ tokens consistently
- **Name patterns**: "code", "build", "architect", "security", "audit", "review", "fix", "debug"
- **Runtime**: Over 3 minutes
- **Heavy reasoning**: Multi-step planning, code generation, nuanced analysis
- **Tool use**: 4+ tool calls per run
- **Low tolerance for error**: Security, financial, or production-critical tasks
- **Previous failures**: Any task that failed on a lower-tier model should stay at current tier

## Override Rules (NEVER downgrade)

1. **Coding tasks** — any task that generates, modifies, or reviews code
2. **Security tasks** — any task involving security review, vulnerability scanning, access control
3. **Financial tasks** — any task involving trading, payments, or financial analysis
4. **User-explicit model choice** — if the user set a specific model in config, respect it
5. **Previously failed downgrades** — if a task was upgraded after failing, don't suggest downgrading again
6. **Main session model** — never recommend changing the user's default interactive model
7. **Tasks with thinking enabled** — if thinking/reasoning is turned on, the task needs it

## Confidence Scoring

| Confidence | Meaning | When to Apply |
|------------|---------|---------------|
| HIGH | Very confident this change is safe | Simple tasks with clear patterns, large cost savings |
| MEDIUM | Likely safe but monitor after change | Medium tasks being suggested for downgrade, less history |
| LOW | Uncertain, proceed with caution | Limited run history, borderline complexity, mixed signals |

## Edge Cases

- **New cron jobs** (<5 runs): Mark as "insufficient data" — don't recommend changes
- **Inconsistent output length**: If output varies wildly, classify at the HIGHER tier
- **Mixed tasks in one cron**: If a cron does both simple and complex work, classify as complex
- **Crons with errors**: If error rate >10%, don't recommend downgrading — it may need MORE capability
