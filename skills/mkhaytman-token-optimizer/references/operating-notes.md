# Token Optimizer Operating Notes

## What It Optimizes

- Context pressure: detects sessions approaching context limits.
- Tool-call redundancy: estimates duplicate tool calls from transcript history.
- Verbose outputs: flags oversized `toolResult` payloads.
- Model fit: identifies simple tasks running on expensive models.
- Session hygiene: finds stuck/urgent sessions and proposes safe cleanup actions.

## Safety Model

- `--cleanup` is plan-only by default.
- `--cleanup --apply` currently performs only one automated action:
  - `openclaw gateway restart` if stuck sessions are detected.
- It does not delete files, reset state, or remove sessions.

## Compression Behavior

`--compress` does not mutate the live session transcript.
It creates an external compressed context file that can be reused in new sessions.

## Limits and Heuristics

- Tool token attribution is estimated from assistant `usage.totalTokens` split across tool calls in the same assistant message.
- Preflight estimates are coarse-grained and intended for planning, not billing.
- Model optimization recommendations are heuristic (keyword complexity + model choice).
