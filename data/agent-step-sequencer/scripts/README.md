# Scripts

## step-sequencer-check.py

Invoked by heartbeat or agent. Reads `state.json`, invokes runner when work exists.

**Usage:**

```bash
python3 scripts/step-sequencer-check.py [state.json path]
```

**Behavior:**

- No state or status=DONE → do nothing
- Step FAILED → reset to PENDING, invoke runner (immediate retry)
- Step DONE → advance currentStep, invoke runner
- Step PENDING or IN_PROGRESS → invoke runner

---

## step-sequencer-runner.py

Invoked by check script. Runs current step: invokes agent with instruction, waits for exit, marks DONE/FAILED.

**Usage:**

```bash
python3 scripts/step-sequencer-runner.py [state.json path]
```

**Behavior:**

- Reads state, gets current step instruction from plan.steps
- Applies stepDelayMinutes (0 = no delay, 2 = 2 min)
- Invokes agent via STEP_AGENT_CMD
- On retry: uses troubleshoot prompt with previous error
- On FAILED: invokes check script immediately

---

## Configuration

| Env | Description |
|-----|-------------|
| `STEP_AGENT_CMD` | **Required.** Command to invoke agent (space-separated). Prompt appended. Example: `openclaw agent --message` |
| `STEP_RUNNER` | Path to runner script (optional) |
| `STEP_MAX_RETRIES` | Max retries on FAILED before adding to blockers. Default: 3 |

**Security:** Do not set `STEP_AGENT_CMD` to `bash`, `sh`, or `-c`—the runner rejects these to prevent command injection.

---

## Wire

1. Heartbeat calls step-sequencer-check.py on each cycle
2. Agent invokes step-sequencer-check.py immediately after persisting state

---

## Tests

```bash
python3 test/test_step_sequencer.py
```
