# Orchestrator Architecture Reference

> **Reference only — this file is NOT an active prompt and is NOT called by `run.py`.**
> It documents the design rationale for contributors and developers.

The checkmate orchestrator is `scripts/run.py` — a deterministic Python script, not an LLM.

## Why a script, not an LLM

| LLM as orchestrator | Script as orchestrator |
|---|---|
| Loop in natural language — fragile | Real `while` loop — deterministic |
| Context grows with every iteration | Stateless between iterations |
| Compaction can lose loop state | State persisted in `state.json` |
| Max ~5–10 reliable iterations | Dozens of iterations, hours of runtime |

## How `run.py` works

```python
criteria = run_intake(workspace, task)          # once

for iteration in range(start_iter, max_iter + 1):
    output  = run_worker(...)   # call_llm with worker prompt
    verdict, is_pass = run_judge(...)   # call_llm with judge prompt

    if is_pass:
        deliver(output)
        return

    feedback += extract_gaps(verdict)   # carry forward for next iteration
```

## LLM interface

Each worker/judge call uses an isolated session:
```bash
openclaw agent --session-id checkmate-worker-N-TIMESTAMP \
               --message "PROMPT" \
               --json
```

Reply is at `result.payloads[0].text`. Session is isolated — no shared history between iterations.

## State machine

```
running → (each iteration updates state.json)
        → pass   (PASS verdict received)
        → fail   (max iterations exhausted)
```

Resume: re-run `run.py` with same `--workspace`. Completed steps are skipped.

## Notification

On completion (and at each interactive checkpoint), `run.py` calls:
```bash
openclaw message send \
  --channel CHANNEL \
  --target RECIPIENT \
  --message "RESULT"
```

`RECIPIENT` is the channel-specific target ID passed via `--recipient` (e.g. Telegram user ID, E.164 phone number). Messages are sent directly — no agent turn required.
