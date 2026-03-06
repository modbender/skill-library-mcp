# Checkmate

**Iterative task completion with a judge loop.**

Checkmate converts a vague task into machine-checkable criteria, calls an LLM worker to produce output, judges the result, and loops with accumulated feedback until the work passes — or max iterations are reached. The orchestrator is a real Python script with a deterministic `while` loop. LLM is used only as worker and judge. Designed for long-running tasks: supports dozens of iterations over hours.

Use when:
- A task needs quality guarantees, not just best-effort
- Output must meet specific criteria before delivery
- You want autonomous iteration until something is truly done

Triggers: `checkmate: TASK`, `until it passes`, `keep iterating until done`, `quality loop`, `judge and retry`

---

## What It Is

Checkmate is a **deterministic Python orchestration loop** that wraps LLM calls for worker and judge roles. The Python script (`scripts/run.py`) maintains state, persists progress to disk, and drives the loop — it never "forgets" its place. LLM sessions are isolated per-call; no shared history bleeds between iterations.

The intake stage first converts the task into machine-checkable acceptance criteria (with a criteria-quality judge loop of its own). Only when criteria are approved does the main worker→judge loop begin.

Workers get the full OpenClaw agent runtime: `exec`, `web_search`, `web_fetch`, all skills, OAuth auth. They can browse, run code, fetch URLs — anything the main agent can do.

---

## Requirements

- **OpenClaw platform CLI** (`openclaw`) in `PATH` — used for session UUID lookup, agent-turn injection, and fallback channel delivery
- **Python 3** — `run.py` uses stdlib only; no pip packages needed
- No separate API keys or env vars — routes through the gateway's existing OAuth

---

## Security & Privilege Model

> ⚠️ **High-privilege skill** — read this before using in batch or automated mode.

**Workers and judges inherit full host-agent runtime:**
- Shell access (`exec`)
- Network access (`web_search`, `web_fetch`)
- All installed skills, including OAuth-bound ones (Gmail, Drive, etc.)
- Ability to spawn further sub-agents (`sessions_spawn`)

The task description you provide **directly controls** what workers do — treat it like code you're about to run, not a prompt you're typing.

**Batch mode (`--no-interactive`) removes all human gates.** In interactive mode (default) you approve criteria and each checkpoint. In batch mode the loop runs to completion with no human review — only use this for tasks and environments you fully trust.

**Checkpoint bridging writes your replies verbatim to disk.** Don't relay untrusted third-party content as checkpoint replies.

---

## Architecture

```
scripts/run.py  (deterministic Python while loop — the real orchestrator)
  │
  ├─ Intake loop [up to --max-intake-iter, default 5]:
  │    ├─ Draft criteria  (intake prompt + task + refinement feedback)
  │    ├─ ⏸ USER REVIEW (interactive): show draft → wait for approval/feedback
  │    │     approved? → lock criteria.md
  │    │     feedback? → refine, next intake iteration
  │    └─ (batch mode --no-interactive: criteria-judge gates instead of user)
  │
  ├─ ⏸ PRE-START GATE (interactive): show final task + criteria → user confirms "go"
  │         (edit task / cancel supported here)
  │
  └─ Main loop [up to --max-iter, default 10]:
       ├─ Worker: spawn agent session → writes iter-N/output.md
       │          (full runtime: exec, web_search, all skills, OAuth auth)
       ├─ Judge:  spawn agent session → writes iter-N/verdict.md
       ├─ PASS?  → write final-output.md, notify user via --recipient, exit
       └─ FAIL?  → extract gap summary → ⏸ CHECKPOINT (interactive): show score + gaps
                     continue?    → next iteration (with judge gaps)
                     redirect: X  → next iteration (with user direction appended)
                     stop?        → end loop, take best result so far
```

**Interactive mode** (default): user approves criteria, confirms pre-start, and reviews each FAIL checkpoint.
**Batch mode** (`--no-interactive`): fully autonomous; criteria-judge gates intake, no checkpoints.

### User input bridge

When the orchestrator needs user input, it:
1. Writes `workspace/pending-input.json` (kind + workspace path + channel)
2. Sends a notification via `--recipient` and `--channel`
3. Polls `workspace/user-input.md` every 5 seconds (up to `--checkpoint-timeout` minutes)

The main agent acts as the bridge: when `pending-input.json` exists and the user replies, the agent writes their response to `user-input.md`. The orchestrator picks it up automatically and resumes.

Each LLM call is an isolated OpenClaw agent session:

```bash
openclaw agent --session-id checkmate-worker-N-TIMESTAMP \
               --message "PROMPT" \
               --timeout 3600 \
               --json
```

Result is read from `result.payloads[0].text`. Sessions are stateless — no shared history between iterations.

### Prompt roles

| File | Role | Called by |
|------|------|-----------|
| `prompts/intake.md` | Converts task → criteria draft | `run_intake_draft()` |
| `prompts/criteria-judge.md` | Evaluates criteria quality (APPROVED / NEEDS_WORK) — batch mode only | `run_criteria_judge()` |
| `prompts/worker.md` | Performs the actual task | `run_worker()` |
| `prompts/judge.md` | Evaluates output against criteria (PASS / FAIL) | `run_judge()` |

`prompts/orchestrator.md` is architecture reference documentation only — **not called by `run.py`**.

---

## Installation

Install via the [ClawhHub CLI](https://clawhub.ai):

```bash
clawhub install checkmate
```

This adds the skill to your OpenClaw workspace. Requires OpenClaw to be running.

Manual install (clone into your skills directory):

```bash
cd <your-skills-dir>
git clone https://github.com/InsipidPoint/checkmate checkmate
```

---

## Quick Start

### 1. Get your session UUID and recipient ID

The session UUID enables direct agent-turn injection — the preferred notification path:

```bash
openclaw gateway call sessions.list --params '{"limit":1}' --json \
  | python3 -c "import json,sys; s=json.load(sys.stdin)['sessions'][0]; print(s['sessionId'], s['lastTo'])"
```

This prints your `sessionId` (UUID) and `lastTo` (channel:recipient_id). Use both in the run command.

### 2. Create a workspace

```bash
WORKSPACE=$(bash <skill-path>/scripts/workspace.sh /tmp "Your task description")
echo "Workspace: $WORKSPACE"
```

Replace `<skill-path>` with the path to your checkmate skill directory.

### 3. Run the orchestrator

```bash
python3 <skill-path>/scripts/run.py \
  --workspace "$WORKSPACE" \
  --task "Your task description" \
  --max-iter 10 \
  --session-uuid YOUR_SESSION_UUID \
  --recipient YOUR_RECIPIENT_ID \
  --channel YOUR_CHANNEL
```

Run in background for long tasks:

```bash
nohup python3 <skill-path>/scripts/run.py \
  --workspace "$WORKSPACE" \
  --task "Your task description" \
  --max-iter 20 \
  --session-uuid YOUR_SESSION_UUID \
  --recipient YOUR_RECIPIENT_ID \
  --channel YOUR_CHANNEL \
  > "$WORKSPACE/run.log" 2>&1 &

echo "Running as PID $! — tail $WORKSPACE/run.log"
```

### 4. Find your output

On PASS or after max iterations, the best output is written to:

```
$WORKSPACE/final-output.md
```

You will also receive a notification on your configured channel (if `--recipient` and `--channel` are set).

---

## Invocation Examples

**Basic usage:**
```bash
python3 scripts/run.py \
  --workspace /tmp/checkmate-20260222-120000 \
  --task "Write a README for the checkmate skill"
```

**Long-running research task (20 iterations, 2h worker timeout):**
```bash
python3 scripts/run.py \
  --workspace /tmp/checkmate-20260222-120000 \
  --task "Deep analysis of NVDA vs AMD for 2026 AI infrastructure spend" \
  --max-iter 20 \
  --worker-timeout 7200 \
  --session-uuid YOUR_SESSION_UUID \
  --recipient YOUR_RECIPIENT_ID \
  --channel YOUR_CHANNEL
```

**Resume an interrupted run:**
```bash
# Just re-run with the same --workspace — it picks up from state.json
python3 scripts/run.py \
  --workspace /tmp/checkmate-20260222-120000 \
  --task "same task text"
```

**Triggered from the main agent (via checkmate skill):**
When the user says `checkmate: <task>` or `until it passes`, the main agent:
1. Looks up its session UUID via `openclaw gateway call sessions.list`
2. Creates a workspace via `workspace.sh`
3. Spawns `run.py` via `exec` with `background=true`, passing `--session-uuid` and `--recipient`
4. Tells the user it's running; checkpoints arrive as direct agent turns

---

## Parameters

| Flag | Default | Description |
|------|---------|-------------|
| `--workspace` | *(required)* | Workspace directory path |
| `--task` | `""` | Task text (or write to `workspace/task.md` before running) |
| `--max-intake-iter` | `5` | Max intake criteria refinement iterations |
| `--max-iter` | `10` | Max main loop iterations (increase to 20 for complex tasks) |
| `--worker-timeout` | `3600` | Seconds per worker agent call |
| `--judge-timeout` | `300` | Seconds per judge agent call |
| `--session-uuid` | `""` | Agent session UUID (from `sessions.list`); primary notification path via direct turn injection |
| `--recipient` | `""` | Channel recipient ID (e.g. user/chat ID or E.164 phone); fallback if injection unavailable |
| `--channel` | `""` | Delivery channel for fallback notifications (e.g. `telegram`, `whatsapp`, `signal`) |
| `--no-interactive` | off | Disable user checkpoints; fully autonomous batch mode |
| `--checkpoint-timeout` | `60` | Minutes to wait for user reply at each interactive checkpoint |

---

## Workspace Layout

```
<workspace>/checkmate-YYYYMMDD-HHMMSS/
├── task.md                  # Original task description
├── criteria.md              # Locked acceptance criteria (written by intake)
├── feedback.md              # Accumulated judge gap summaries
├── state.json               # {iteration, status} — used for resume
├── run.log                  # Orchestrator stdout (if redirected)
│
├── intake-01/               # Intake iterations (one per refinement round)
│   ├── criteria-draft.md    # Draft criteria from intake agent
│   └── criteria-verdict.md  # Criteria-judge verdict
│
├── iter-01/                 # Main loop iterations
│   ├── output.md            # Worker output
│   └── verdict.md           # Judge verdict (PASS/FAIL + score + gap summary)
│
├── iter-02/ ...             # Additional iterations if needed
│
└── final-output.md          # Best output — written on PASS or max iterations
```

`state.json` values:
- `status: "running"` — iteration in progress
- `status: "pass"` — task passed, `final-output.md` contains the result
- `status: "fail"` — max iterations reached, best attempt saved to `final-output.md`

---

## Resume Support

Checkmate is designed to survive interruptions. If `run.py` is killed (crash, timeout, manual stop), re-run it with the **same `--workspace` path**:

```bash
python3 scripts/run.py \
  --workspace /tmp/checkmate-20260222-120000 \
  --task "original task"
```

The script reads `state.json` to find where it left off:
- **Intake:** If `criteria.md` already exists, intake is skipped entirely
- **Worker:** If `iter-N/output.md` already exists, the worker call is skipped (uses cached output)
- **Judge:** Always re-runs (verdict may differ on retry — this is intentional)
- **Already completed:** If `state.status` is `"pass"` or `"fail"`, the script exits immediately

This means you can safely re-run after a network blip, rate-limit crash, or system restart.

### Interactive checkpoints

In interactive mode (default), the orchestrator pauses at three gates: criteria review, pre-start confirmation, and each FAIL iteration. When paused, it writes `workspace/pending-input.json` and sends you a notification via `--channel`.

The main agent acts as a bridge: when you reply to the notification, it writes your response to `workspace/user-input.md`. The orchestrator detects the file within 5 seconds and resumes.

**Accepted replies at each gate:**

| Gate | Approve / continue | Redirect | Cancel |
|------|--------------------|----------|--------|
| Criteria review | `ok`, `approve`, `lgtm` | any feedback text | — |
| Pre-start | `go`, `start`, `ok` | `edit task: NEW TASK` | `cancel` |
| Iteration checkpoint | `continue`, (empty) | `redirect: DIRECTION` | `stop` |

To inject a response manually (e.g., after a notification was missed):

```bash
echo "continue" > /tmp/checkmate-TIMESTAMP/user-input.md
```

The orchestrator polls every 5 seconds and resumes automatically.
