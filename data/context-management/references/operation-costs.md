# Operation Cost Reference

Estimates from production use. Actual costs vary by model, tokenizer, and content type. Use as order-of-magnitude guidance, not exact numbers.

## Fixed Baseline

These components are loaded every turn, before any conversation:

| Component | Typical Range | Notes |
|-----------|--------------|-------|
| System prompt | 3,000-6,000 | Varies by OpenClaw version |
| Workspace files | 500-5,000 | Depends on file count and size (AGENTS.md, MEMORY.md, etc.) |
| Skill descriptions | 50-150 per skill | Scales with number of installed skills |
| Tool definitions | 2,000-5,000 | Depends on enabled tools |

**Total baseline**: typically 5-15% of context. Check `session_status` for yours.

To reduce baseline: trim MEMORY.md, disable unused skills, keep workspace files concise.

## Per-Operation Costs

| Operation | Tokens | Context Impact |
|-----------|--------|---------------|
| Ask a question, get answer | 500-1,500 | Negligible |
| Read a file (small, <100 lines) | 500-2,000 | Low |
| Read a file (large, >500 lines) | 2,000-10,000 | Moderate-High |
| Edit a file | 500-1,500 | Low |
| exec (simple command) | 200-800 | Negligible |
| exec (verbose output) | 2,000-10,000 | High |
| Web search | 1,000-2,000 | Low |
| Web fetch | 2,000-8,000 | Moderate-High |
| Browser snapshot | 1,000-5,000 | Moderate |
| Run test suite (per test) | 2,000-5,000 | High |

## Session Burn Rates

| Activity | Tokens/minute | Approx. time to 85% (200k context) |
|----------|--------------|-------------------------------------|
| Casual conversation | 500-1,000 | 5-6 hours |
| Planning/discussion | 1,000-2,000 | 2-3 hours |
| Active coding/editing | 2,000-4,000 | 1-1.5 hours |
| Heavy testing/debugging | 3,000-6,000 | 30-60 min |
| Bulk operations | 5,000-10,000 | 20-30 min |

Scale proportionally for different context window sizes.

## Spawn Decision Heuristic

Sub-agents have their own baseline overhead (~5-15% of their context window). Only worth spawning if the task would consume significantly more than that in main context:

- **<5 tool calls**: Keep in main (not worth spawn overhead)
- **5-10 tool calls**: Spawn if context above 50%
- **>10 tool calls**: Always spawn

## Compaction Summary Costs

Each compaction produces a summary that persists in context:
- First compaction: ~2,000-4,000 tokens
- Second compaction: ~4,000-8,000 tokens (cumulative — includes prior summary)
- Third compaction: ~6,000-12,000 tokens
- After 5+ compactions: summaries alone may consume 20-30% of context

This is the death spiral: each compaction frees less space because the summary from the previous compaction keeps growing.
