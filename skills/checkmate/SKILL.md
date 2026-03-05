---
name: checkmate
description: "Enforces task completion: turns your goal into pass/fail criteria, runs a worker, judges the output, feeds back what's missing, and loops until every criterion passes. Nothing ships until it's truly done. Trigger: 'checkmate: TASK'"
requires:
  cli:
    - openclaw  # platform CLI: sessions.list, agent spawn, message send
privileges: high  # spawned workers inherit full host-agent runtime (exec, OAuth, all skills)
---

# Checkmate

A deterministic Python loop (`scripts/run.py`) calls an LLM for worker and judge roles.
Nothing leaves until it passes — and you stay in control at every checkpoint.

## Requirements

- **OpenClaw platform CLI** (`openclaw`) — must be available in `PATH`. Used for:
  - `openclaw gateway call sessions.list` — resolve session UUID for turn injection
  - `openclaw agent --session-id <UUID>` — inject checkpoint messages into the live session
  - `openclaw message send` — fallback channel delivery (e.g. Telegram, Signal)
- **Python 3** — `run.py` is pure stdlib; no pip packages required
- No separate API keys or env vars needed — routes through the gateway's existing OAuth

## Security & Privilege Model

> ⚠️ **This is a high-privilege skill.** Read before using in batch/automated mode.

**Spawned workers and judges inherit full host-agent runtime**, including:
- `exec` (arbitrary shell commands)
- `web_search`, `web_fetch`
- All installed skills (including those with OAuth-bound credentials — Gmail, Drive, etc.)
- `sessions_spawn` (workers can spawn further sub-agents)

This means **the task description you provide directly controls what the worker does** — treat it like code you're about to run, not a message you're about to send.

**Batch mode (`--no-interactive`) removes all human gates.** In interactive mode (default), you approve criteria and each checkpoint before the loop continues. In batch mode, criteria are auto-approved and the loop runs to completion autonomously — only use this for tasks and environments you fully trust.

**User-input bridging writes arbitrary content to disk.** When you reply to a checkpoint, the main agent writes your reply verbatim to `user-input.md` in the workspace. The orchestrator reads it and acts on it. Don't relay untrusted third-party content as checkpoint replies.

## When to Use

Use checkmate when correctness matters more than speed — when "good enough on the first try" isn't acceptable.

**Good fits:**
- Code that must pass tests or meet a spec
- Docs or reports that must hit a defined quality bar
- Research that must be thorough and cover specific ground
- Any task where you'd otherwise iterate manually until satisfied

**Trigger phrases** (say any of these):
- `checkmate: TASK`
- `keep iterating until it passes`
- `don't stop until done`
- `until it passes`
- `quality loop: TASK`
- `iterate until satisfied`
- `judge and retry`
- `keep going until done`

## Architecture

```
scripts/run.py  (deterministic Python while loop — the orchestrator)
  ├─ Intake loop [up to max_intake_iter, default 5]:
  │    ├─ Draft criteria (intake prompt + task + refinement feedback)
  │    ├─ ⏸ USER REVIEW: show draft → wait for approval or feedback
  │    │     approved? → lock criteria.md
  │    │     feedback? → refine, next intake iteration
  │    └─ (non-interactive: criteria-judge gates instead of user)
  │
  ├─ ⏸ PRE-START GATE: show final task + criteria → user confirms "go"
  │         (edit task / cancel supported here)
  │
  └─ Main loop [up to max_iter, default 10]:
       ├─ Worker: spawn agent session → iter-N/output.md
       │          (full runtime: exec, web_search, all skills, OAuth auth)
       ├─ Judge:  spawn agent session → iter-N/verdict.md
       ├─ PASS?  → write final-output.md, notify user, exit
       └─ FAIL?  → extract gaps → ⏸ CHECKPOINT: show score + gaps to user
                     continue?  → next iteration (with judge gaps)
                     redirect:X → next iteration (with user direction appended)
                     stop?      → end loop, take best result so far
```

**Interactive mode** (default): user approves criteria, confirms pre-start, and reviews each FAIL checkpoint.
**Batch mode** (`--no-interactive`): fully autonomous; criteria-judge gates intake, no checkpoints.

### User Input Bridge

When the orchestrator needs user input, it:
1. Writes `workspace/pending-input.json` (kind + workspace path)
2. Sends a notification via `--recipient` and `--channel`
3. Polls `workspace/user-input.md` every 5s (up to `--checkpoint-timeout` minutes)

The main agent acts as the bridge: when `pending-input.json` exists and the user replies, the agent writes their response to `user-input.md`. The orchestrator picks it up automatically.

Each agent session is spawned via:
```bash
openclaw agent --session-id <isolated-id> --message <prompt> --timeout <N> --json
```
Routes through the gateway WebSocket using existing OAuth — no separate API key.
Workers get full agent runtime: exec, web_search, web_fetch, all skills, sessions_spawn.

## Your Job (main agent)

When checkmate is triggered:

1. **Get your session UUID** (for direct agent-turn injection):
   ```bash
   openclaw gateway call sessions.list --params '{"limit":1}' --json \
     | python3 -c "import json,sys; s=json.load(sys.stdin)['sessions'][0]; print(s['sessionId'])"
   ```
   Also note your `--recipient` (channel user/chat ID) and `--channel` as fallback.

2. **Create workspace**:
   ```bash
   bash <skill-path>/scripts/workspace.sh /tmp "TASK"
   ```
   Prints the workspace path. Write the full task to `workspace/task.md` if needed.

3. **Run the orchestrator** (background exec):
   ```bash
   python3 <skill-path>/scripts/run.py \
     --workspace /tmp/checkmate-TIMESTAMP \
     --task "FULL TASK DESCRIPTION" \
     --max-iter 10 \
     --session-uuid YOUR_SESSION_UUID \
     --recipient YOUR_RECIPIENT_ID \
     --channel <your-channel>
   ```
   Use `exec` with `background=true`. This runs for as long as needed.
   Add `--no-interactive` for fully autonomous runs (no user checkpoints).

4. **Tell the user** checkmate is running, what it's working on, and that they'll receive criteria drafts and checkpoint messages via your configured channel to review and approve.

5. **Bridge user replies**: When user responds to a checkpoint message, check for `pending-input.json` and write their response to `workspace/user-input.md`.

## Bridging User Input

**When a checkpoint message arrives** (the orchestrator sent the user a criteria/approval/checkpoint request), bridge their reply:

```bash
# Find active pending input
cat <workspace-parent>/checkmate-*/pending-input.json 2>/dev/null

# Route user's reply
echo "USER REPLY HERE" > /path/to/workspace/user-input.md
```

The orchestrator polls for this file every 5 seconds. Once written, it resumes automatically and deletes the file.

**Accepted replies at each gate:**

| Gate | Continue | Redirect | Cancel |
|------|----------|----------|--------|
| Criteria review | "ok", "approve", "lgtm" | any feedback text | — |
| Pre-start | "go", "start", "ok" | "edit task: NEW TASK" | "cancel" |
| Iteration checkpoint | "continue", (empty) | "redirect: DIRECTION" | "stop" |

## Parameters

| Flag | Default | Notes |
|------|---------|-------|
| `--max-intake-iter` | 5 | Intake criteria refinement iterations |
| `--max-iter` | 10 | Main loop iterations (increase to 20 for complex tasks) |
| `--worker-timeout` | 3600s | Per worker session |
| `--judge-timeout` | 300s | Per judge session |
| `--session-uuid` | — | Agent session UUID (from `sessions.list`); used for direct turn injection — primary notification path |
| `--recipient` | — | Channel recipient ID (e.g. user/chat ID, E.164 phone number); fallback if injection fails |
| `--channel` | — | Delivery channel for fallback notifications (e.g. `telegram`, `whatsapp`, `signal`) |
| `--no-interactive` | off | Disable user checkpoints (batch mode) |
| `--checkpoint-timeout` | 60 | Minutes to wait for user reply at each checkpoint |

## Workspace layout

```
memory/checkmate-YYYYMMDD-HHMMSS/
├── task.md               # task description (user may edit pre-start)
├── criteria.md           # locked after intake
├── feedback.md           # accumulated judge gaps + user direction
├── state.json            # {iteration, status} — resume support
├── pending-input.json    # written when waiting for user; deleted after response
├── user-input.md         # agent writes user's reply here; read + deleted by orchestrator
├── intake-01/
│   ├── criteria-draft.md
│   ├── criteria-verdict.md  (non-interactive only)
│   └── user-feedback.md     (interactive: user's review comments)
├── iter-01/
│   ├── output.md         # worker output
│   └── verdict.md        # judge verdict
└── final-output.md       # written on completion
```

## Resume

If the script is interrupted, just re-run it with the same `--workspace`. It reads `state.json` and skips completed steps. Locked `criteria.md` is reused; completed `iter-N/output.md` files are not re-run.

## Prompts

Active prompts called by `run.py`:

- `prompts/intake.md` — converts task → criteria draft
- `prompts/criteria-judge.md` — evaluates criteria quality (APPROVED / NEEDS_WORK) — used in non-interactive mode
- `prompts/worker.md` — worker prompt (variables: TASK, CRITERIA, FEEDBACK, ITERATION, MAX_ITER, OUTPUT_PATH)
- `prompts/judge.md` — evaluates output against criteria (PASS / FAIL)

Reference only (not called by `run.py`):

- `prompts/orchestrator.md` — architecture documentation explaining the design rationale
