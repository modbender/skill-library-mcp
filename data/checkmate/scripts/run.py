#!/usr/bin/env python3
"""
checkmate/scripts/run.py

Deterministic Python orchestrator for the checkmate skill.
Real while loop. LLM called as a subprocess via `openclaw agent`.
"""

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent


# ── Utilities ─────────────────────────────────────────────────────────────────

def log(msg: str):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[checkmate {ts}] {msg}", flush=True)


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def load_state(workspace: Path) -> dict:
    p = workspace / "state.json"
    return json.loads(p.read_text()) if p.exists() else {"iteration": 0, "status": "running"}


def save_state(workspace: Path, state: dict):
    write_file(workspace / "state.json", json.dumps(state, indent=2))


# ── LLM interface ─────────────────────────────────────────────────────────────

RETRYABLE_ERRORS = ("cooldown", "rate limit", "timed out", "FailoverError", "503", "529")

def call_agent(prompt: str, session_id: str, timeout_s: int = 3600,
               max_retries: int = 5, base_backoff: int = 60) -> str:
    """
    Spawn an agent session via the OpenClaw gateway (openclaw agent CLI).
    Each session gets the full agent runtime: all tools, all skills, OAuth auth.
    No direct Anthropic API calls — routes through the gateway like any sub-agent.
    Retries with exponential backoff on rate limit / cooldown errors.
    """
    cmd = [
        "openclaw", "agent",
        "--session-id", session_id,
        "--message", prompt,
        "--timeout", str(timeout_s),
        "--json",
    ]
    for attempt in range(1, max_retries + 1):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s + 30)
            if result.returncode != 0:
                err = result.stderr + result.stdout
                if any(e in err for e in RETRYABLE_ERRORS):
                    wait = base_backoff * (2 ** (attempt - 1))
                    log(f"rate limit/cooldown (attempt {attempt}/{max_retries}) — waiting {wait}s")
                    time.sleep(wait)
                    continue
                raise RuntimeError(f"openclaw agent exited {result.returncode}: {result.stderr[:300]}")
            data = json.loads(result.stdout)
            return data["result"]["payloads"][0]["text"]
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"Unexpected response shape: {result.stdout[:200]}") from e
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Agent subprocess timed out after {timeout_s + 30}s")
    raise RuntimeError(f"call_agent failed after {max_retries} retries (persistent rate limit)")


def notify(recipient: str, message: str, channel: str):
    """
    Deliver a plain message directly to the user via `openclaw message send`.
    recipient is the channel-specific target (e.g. channel user ID, phone number in E.164).
    Uses direct channel delivery — no agent runtime involved.
    """
    if not recipient:
        log("No recipient — result written to workspace/final-output.md only")
        return
    # Most channels have a ~4096 char limit; truncate with a note if needed
    MAX_MSG = 3800
    if len(message) > MAX_MSG:
        message = message[:MAX_MSG] + f"\n\n…_(truncated — see workspace for full content)_"

    cmd = [
        "openclaw", "message", "send",
        "--channel", channel,
        "--target", recipient,
        "--message", message,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            log(f"📨 delivered to {recipient} via {channel}")
        else:
            log(f"⚠️  delivery failed (rc={result.returncode}): {(result.stderr or result.stdout)[:200]}")
    except Exception as e:
        log(f"⚠️  delivery failed ({e})")


# ── User input / checkpoint system ────────────────────────────────────────────

def inject_agent_turn(session_uuid: str, message: str, timeout_s: int = 120) -> bool:
    """
    Inject a message into the agent's live session using its UUID.
    Returns True on success, False on failure.
    The agent processes the message in context, sees routing instructions,
    and naturally presents the checkpoint to the user via the configured channel.
    """
    cmd = [
        "openclaw", "agent",
        "--session-id", session_uuid,
        "--message", message,
        "--json",
        "--timeout", str(timeout_s),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s + 10)
        if result.returncode == 0:
            log(f"⏸  checkpoint injected into agent session (UUID={session_uuid[:8]}…)")
            return True
        else:
            log(f"⚠️  agent-turn injection failed (rc={result.returncode}): {result.stderr[:150]}")
            return False
    except Exception as e:
        log(f"⚠️  agent-turn injection failed ({e})")
        return False


def request_user_input(
    workspace: Path,
    recipient: str,
    channel: str,
    message: str,
    kind: str = "input",          # "input" | "confirm" | "checkpoint"
    timeout_min: int = 60,
    default_response: str = "",   # returned on timeout (empty = proceed as-is)
    session_uuid: str = "",       # agent session UUID for direct injection (preferred)
) -> str:
    """
    Pause the run, deliver a checkpoint to the user, then poll for their reply.

    Notification strategy (two-layer):
      PRIMARY — agent-turn injection via session UUID: injects an ACTION COMMAND
        into the agent's live session instructing it to (1) relay the checkpoint
        to the user via the message tool, and (2) bridge the user's next reply
        to user-input.md. The agent's tool calls execute even in --json one-shot
        mode, so the message send happens as a side-effect of the injection.
        Requires --session-uuid (UUID from `openclaw gateway call sessions.list`).

      FALLBACK — openclaw message send: sends directly to the channel if injection
        is unavailable or fails. Message includes bridge instruction for the agent
        to write the user's reply to user-input.md on next contact.

    The orchestrator polls user-input.md every 5s.
    pending-input.json is written as a safety net for heartbeat-based routing.
    """
    response_file  = workspace / "user-input.md"
    pending_marker = workspace / "pending-input.json"

    # Remove any stale response from a prior checkpoint
    if response_file.exists():
        response_file.unlink()

    # Write marker (safety net: agent can check this on any turn if routing context was lost)
    marker = {
        "kind": kind,
        "waiting_since": datetime.now(timezone.utc).isoformat(),
        "timeout_min": timeout_min,
        "workspace": str(workspace),
    }
    write_file(pending_marker, json.dumps(marker, indent=2))

    if not recipient and not session_uuid:
        log("No recipient or session UUID — cannot send checkpoint; proceeding with default")
        return default_response

    bridge_instruction = (
        f"When the user replies to this checkpoint in any upcoming message, "
        f"immediately write their verbatim reply to `{workspace}/user-input.md` "
        f"before doing anything else. The checkmate orchestrator polls that file every 5 seconds."
    )

    # ── Primary: agent-turn injection — action command to relay + bridge ──
    # The injection tells the agent to actively SEND the checkpoint to the user
    # (via the message tool) and to bridge the next user reply to user-input.md.
    # The agent's tool calls (message send) execute even in --json one-shot mode.
    injected = False
    if session_uuid:
        recipient_clause = f"Send it to: channel={channel}, target={recipient}." if recipient else \
                           "Send it via whatever channel you have configured."
        agent_msg = (
            f"[checkmate {kind}]\n\n"
            f"The checkmate orchestrator is paused and needs user input. "
            f"Do the following immediately:\n\n"
            f"1. **Relay this checkpoint to the user** using the message tool (or `openclaw message send`). "
            f"{recipient_clause}\n\n"
            f"2. **Bridge their reply**: {bridge_instruction}\n\n"
            f"--- CHECKPOINT TO RELAY ---\n\n"
            f"{message}\n\n"
            f"--- END CHECKPOINT ---"
        )
        injected = inject_agent_turn(session_uuid, agent_msg)

    # ── Fallback: direct message send (injection unavailable) ──
    if not injected and recipient:
        fallback_msg = (
            f"{message}\n\n"
            f"---\n"
            f"_(checkmate — {'agent injection failed, ' if session_uuid else ''}direct notification)_\n\n"
            f"⚙️ **{bridge_instruction}**"
        )
        log(f"⏸  checkpoint ({kind}) — sending direct message to {recipient} via {channel}")
        notify(recipient, fallback_msg, channel)

    log(f"polling for user reply (every 5s, up to {timeout_min} min)...")
    polls = timeout_min * 12  # every 5s
    for _ in range(polls):
        if response_file.exists():
            response = response_file.read_text().strip()
            response_file.unlink(missing_ok=True)
            pending_marker.unlink(missing_ok=True)
            log(f"▶  user replied ({len(response)} chars) — resuming")
            return response
        time.sleep(5)

    pending_marker.unlink(missing_ok=True)
    log(f"user input timeout after {timeout_min} min — proceeding with default: '{default_response or 'proceed'}'")
    return default_response


def is_approval(response: str) -> bool:
    """Treat empty, 'yes', 'ok', 'approve', 'lgtm', 'continue', 'proceed', 'go' as approval."""
    if not response.strip():
        return True
    return bool(re.match(r"^\s*(yes|ok|okay|approve|approved|lgtm|continue|proceed|go|good|looks good|ship it)\s*[.!]?\s*$",
                         response.strip(), re.IGNORECASE))


# ── Stages ────────────────────────────────────────────────────────────────────

def run_intake_draft(task: str, feedback: str, iteration: int) -> str:
    """Generate a criteria draft, optionally with refinement feedback."""
    template = read_file(SKILL_DIR / "prompts" / "intake.md")
    prompt = f"{template}\n\n---\n\n## Task\n\n{task}"
    if feedback.strip():
        prompt += f"\n\n## Refinement Feedback (fix these issues)\n\n{feedback}"
    return call_agent(prompt, f"checkmate-intake-draft-{iteration}-{int(time.time())}", timeout_s=120)


def run_criteria_judge(task: str, criteria: str, iteration: int) -> tuple[str, bool]:
    """Judge whether the criteria themselves are good enough."""
    template = read_file(SKILL_DIR / "prompts" / "criteria-judge.md")
    prompt = (
        f"{template}\n\n---\n\n"
        f"## Original Task\n\n{task}\n\n"
        f"## Proposed Criteria (intake iteration {iteration})\n\n{criteria}"
    )
    reply = call_agent(prompt, f"checkmate-criteria-judge-{iteration}-{int(time.time())}", timeout_s=120)
    approved = bool(re.search(r"\*\*Result:\*\*\s*APPROVED", reply, re.IGNORECASE))
    return reply, approved


def extract_criteria_feedback(verdict: str) -> str:
    """Extract issues + suggested fixes from a goal-clarity judge verdict."""
    issues_m = re.search(r"## Issues\n(.*?)(?=\n## |\Z)", verdict, re.DOTALL)
    fixes_m = re.search(r"## Suggested Fixes\n(.*?)(?=\n## |\Z)", verdict, re.DOTALL)
    parts = []
    if issues_m:
        parts.append(issues_m.group(1).strip())
    if fixes_m:
        parts.append(fixes_m.group(1).strip())
    return "\n\n".join(parts) if parts else verdict.strip()


def run_intake(workspace: Path, task: str, max_intake_iter: int = 5,
               recipient: str = "", channel: str = "telegram",
               interactive: bool = True, session_uuid: str = "") -> str:
    criteria_path = workspace / "criteria.md"
    if criteria_path.exists():
        log("intake: criteria.md already exists, skipping")
        return criteria_path.read_text()

    feedback = ""
    criteria = ""
    _criteria_approved = False

    for i in range(1, max_intake_iter + 1):
        # Re-read task each iteration (may have been updated with user clarification)
        task = read_file(workspace / "task.md") or task

        log(f"intake: iteration {i}/{max_intake_iter} — drafting goal...")
        criteria = run_intake_draft(task, feedback, i)

        intake_dir = workspace / f"intake-{i:02d}"
        intake_dir.mkdir(parents=True, exist_ok=True)
        write_file(intake_dir / "goal-draft.md", criteria)

        # Pause for user review after each draft (interactive mode)
        if interactive and recipient:
            user_msg = (
                f"🎯 *checkmate: goal draft (intake {i}/{max_intake_iter})*\n\n"
                f"{criteria}\n\n"
                f"---\n"
                f"Reply with:\n"
                f"• **ok / approve** — lock this goal and proceed\n"
                f"• **feedback or edits** — I'll revise before moving on\n\n"
                f"Workspace: `{workspace}`"
            )
            response = request_user_input(
                workspace, recipient, channel,
                message=user_msg,
                kind="confirm-goal",
                timeout_min=60,
                default_response="proceed",
                session_uuid=session_uuid,
            )

            if is_approval(response):
                log(f"intake: user approved goal on iteration {i}")
                _criteria_approved = True
                break
            else:
                # User gave feedback — append it and continue refining
                log(f"intake: user requested changes — refining goal")
                feedback = f"User review feedback:\n{response}"
                write_file(intake_dir / "user-feedback.md", response)
                continue

        # Non-interactive: use goal-clarity judge as gatekeeper
        # (Interactive mode skips judge since user approval is the real gate)
        log(f"intake: judging goal clarity (iter {i})...")
        verdict, approved = run_criteria_judge(task, criteria, i)
        write_file(intake_dir / "goal-verdict.md", verdict)

        if approved:
            log(f"intake: goal APPROVED on iteration {i}")
            _criteria_approved = True
            break

        feedback = extract_criteria_feedback(verdict)
        log(f"intake: goal needs refinement — iterating (iter {i})")

    if not _criteria_approved:
        log(
            f"WARNING: intake: reached max iterations ({max_intake_iter}) without approval — "
            f"proceeding with best-effort criteria"
        )
        if recipient:
            notify(
                recipient,
                (
                    f"⚠️ checkmate: goal intake hit max iterations ({max_intake_iter}) without approval.\n"
                    f"Proceeding with best-effort goal statement — results may be less reliable.\n"
                    f"Workspace: {workspace}"
                ),
                channel,
            )

    write_file(criteria_path, criteria)
    log(f"intake: locked goal statement ({len(criteria)} chars)")
    return criteria


def confirm_prestart(workspace: Path, task: str, criteria: str,
                     recipient: str, channel: str,
                     timeout_min: int = 60, session_uuid: str = "") -> bool:
    """
    Show the user the final task + criteria and ask for explicit go-ahead before the main loop.
    Returns True if approved, False if user cancelled.
    Interactive gate — skipped if recipient is empty.
    """
    if not recipient and not session_uuid:
        return True

    task_preview = task.strip().splitlines()[0][:200]
    goal_preview = criteria.strip().splitlines()[0][:150]  # first line of goal statement
    msg = (
        f"✅ *checkmate: ready to start*\n\n"
        f"**Task:** {task_preview}{'…' if len(task.strip()) > 200 else ''}\n"
        f"**Goal:** {goal_preview}{'…' if len(criteria.strip()) > 150 else ''}\n"
        f"**Workspace:** `{workspace}`\n\n"
        f"Reply: **go** to start · **cancel** to abort · **edit task: ...** to revise"
    )

    response = request_user_input(
        workspace, recipient, channel,
        message=msg,
        kind="prestart-confirm",
        timeout_min=timeout_min,
        default_response="go",
        session_uuid=session_uuid,
    )

    if re.match(r"^\s*cancel\s*$", response.strip(), re.IGNORECASE):
        log("pre-start: user cancelled — aborting")
        return False

    if re.match(r"^\s*edit task:\s*(.+)", response.strip(), re.IGNORECASE | re.DOTALL):
        m = re.match(r"^\s*edit task:\s*(.+)", response.strip(), re.IGNORECASE | re.DOTALL)
        new_task = m.group(1).strip()
        write_file(workspace / "task.md", new_task)
        log(f"pre-start: user updated task ({len(new_task)} chars)")
        notify(recipient, f"✏️ Task updated. Starting worker loop with revised task.", channel)

    log("pre-start: user confirmed — starting main loop")
    return True


def run_iteration_checkpoint(workspace: Path, iteration: int, max_iter: int,
                              output: str, verdict: str, gaps: str,
                              recipient: str, channel: str,
                              timeout_min: int = 30, session_uuid: str = "") -> str:
    """
    After a FAIL verdict, pause and show the user a summary.
    Returns additional feedback from user (empty = continue as-is).
    Skipped if recipient and session_uuid are both empty.
    """
    if not recipient and not session_uuid:
        return gaps

    # Extract score for the summary
    score_m = re.search(r"\*\*Score:\*\*\s*(\d+)/(\d+)", verdict)
    score = score_m.group(0) if score_m else ""

    msg = (
        f"🔄 *checkmate: iteration {iteration}/{max_iter} — FAIL*\n\n"
        f"{score}\n\n"
        f"**Top gaps:**\n{gaps[:800] if gaps else '(none extracted)'}\n\n"
        f"---\n"
        f"Reply with:\n"
        f"• **continue** — proceed with next iteration using judge's feedback\n"
        f"• **redirect: ...** — add your own direction for the next worker\n"
        f"• **stop** — end the loop and take the best result so far\n\n"
        f"Workspace: `{workspace}`"
    )

    response = request_user_input(
        workspace, recipient, channel,
        message=msg,
        kind="iteration-checkpoint",
        timeout_min=timeout_min,
        default_response="continue",
        session_uuid=session_uuid,
    )

    if re.match(r"^\s*stop\s*$", response.strip(), re.IGNORECASE):
        log(f"checkpoint: user requested stop after iteration {iteration}")
        return "__STOP__"

    if re.match(r"^\s*redirect:\s*(.+)", response.strip(), re.IGNORECASE | re.DOTALL):
        m = re.match(r"^\s*redirect:\s*(.+)", response.strip(), re.IGNORECASE | re.DOTALL)
        user_direction = m.group(1).strip()
        log(f"checkpoint: user redirected — adding to feedback")
        return f"{gaps}\n\n## User Direction (iteration {iteration})\n{user_direction}"

    # "continue" or timeout → use judge's gaps as-is
    log(f"checkpoint: continuing with judge feedback")
    return gaps


def run_worker(workspace: Path, task: str, criteria: str, feedback: str,
               iteration: int, max_iter: int, worker_timeout: int = 3600) -> str:
    iter_dir = workspace / f"iter-{iteration:02d}"
    iter_dir.mkdir(parents=True, exist_ok=True)
    output_path = iter_dir / "output.md"

    if output_path.exists():
        log(f"iter {iteration}: output.md already exists, skipping worker (resume)")
        return output_path.read_text()

    template = read_file(SKILL_DIR / "prompts" / "worker.md")
    prompt = (
        template
        .replace("{{TASK}}", task)
        .replace("{{CRITERIA}}", criteria)
        .replace("{{FEEDBACK}}", feedback.strip() or "(none — this is the first attempt)")
        .replace("{{ITERATION}}", str(iteration))
        .replace("{{MAX_ITER}}", str(max_iter))
        .replace("{{OUTPUT_PATH}}", str(output_path))
    )

    log(f"iter {iteration}/{max_iter}: calling worker (timeout={worker_timeout}s)...")
    call_agent_reply = call_agent(
        prompt, f"checkmate-worker-{iteration}-{int(time.time())}", timeout_s=worker_timeout
    )

    # Prefer output_path if the worker wrote it (primary output mechanism per prompt).
    # call_agent() may return early planning text or a partial response — the file
    # written by the worker itself is the authoritative output.
    # Poll briefly in case the worker session is still flushing writes.
    deadline = time.time() + 30
    while time.time() < deadline:
        if output_path.exists() and output_path.stat().st_size > 0:
            mtime = output_path.stat().st_mtime
            time.sleep(3)
            if output_path.stat().st_mtime == mtime:  # stable (no further writes)
                content = output_path.read_text()
                log(f"iter {iteration}: worker wrote output.md ({len(content)} chars) — using file output")
                return content
        time.sleep(3)

    # Fallback: worker did not write output_path — use call_agent's return value
    log(f"WARNING: iter {iteration}: worker did not write output.md — falling back to session reply ({len(call_agent_reply)} chars)")
    write_file(output_path, call_agent_reply)
    return call_agent_reply


def run_judge(workspace: Path, criteria: str, output: str,
              iteration: int, max_iter: int, judge_timeout: int = 300) -> tuple[str, bool]:
    iter_dir = workspace / f"iter-{iteration:02d}"
    verdict_path = iter_dir / "verdict.md"

    template = read_file(SKILL_DIR / "prompts" / "judge.md")
    prompt = (
        f"{template}\n\n---\n\n"
        f"## Criteria\n\n{criteria}\n\n"
        f"## Worker Output\n\n{output}\n\n"
        f"## Context\n\nThis is iteration {iteration} of {max_iter}."
    )

    log(f"iter {iteration}: running judge (timeout={judge_timeout}s)...")
    reply = call_agent(prompt, f"checkmate-judge-{iteration}-{int(time.time())}", timeout_s=judge_timeout)
    write_file(verdict_path, reply)

    is_pass = bool(re.search(r"\*\*Result:\*\*\s*PASS", reply, re.IGNORECASE))
    is_fail = bool(re.search(r"\*\*Result:\*\*\s*FAIL", reply, re.IGNORECASE))
    if not is_pass and not is_fail:
        log(f"WARNING: iter {iteration}: malformed judge output — neither PASS nor FAIL detected; treating as FAIL")
    log(f"iter {iteration}: judge → {'PASS ✅' if is_pass else 'FAIL ❌'}")
    return reply, is_pass


def extract_gaps(verdict: str) -> str:
    m = re.search(r"## Gap Summary\n(.*?)(?=\n## |\Z)", verdict, re.DOTALL)
    return m.group(1).strip() if m else ""


def find_best_iteration(workspace: Path) -> tuple[int, str]:
    best_iter, best_score, best_output = 1, -1, ""
    for iter_dir in sorted(workspace.glob("iter-*")):
        m = re.search(r"\*\*Score:\*\*\s*(\d+)/\d+",
                      read_file(iter_dir / "verdict.md"))
        if m and int(m.group(1)) > best_score:
            best_score = int(m.group(1))
            best_iter = int(iter_dir.name.split("-")[1])
            best_output = read_file(iter_dir / "output.md")
    return best_iter, best_output


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Checkmate — deterministic LLM iteration loop")
    parser.add_argument("--workspace",        required=True, help="Workspace directory path")
    parser.add_argument("--task",             default="",    help="Task text (or read from workspace/task.md)")
    parser.add_argument("--max-iter",         type=int, default=10)
    parser.add_argument("--recipient",      default="",    help="Channel recipient ID (e.g. channel user ID or phone number in E.164); fallback notification target")
    parser.add_argument("--session-uuid",   default="",    help="Agent session UUID for direct turn injection (from `openclaw gateway call sessions.list`); preferred over --recipient for routing")
    parser.add_argument("--channel",          default="")
    parser.add_argument("--worker-timeout",   type=int, default=3600, help="Seconds per worker turn (default: 3600)")
    parser.add_argument("--judge-timeout",    type=int, default=300,  help="Seconds per judge turn (default: 300)")
    parser.add_argument("--max-intake-iter",  type=int, default=5,    help="Max intake refinement iterations (default: 5)")
    parser.add_argument("--no-interactive",   action="store_true",    help="Disable user checkpoints (batch mode)")
    parser.add_argument("--checkpoint-timeout", type=int, default=60, help="Minutes to wait for user response at each checkpoint (default: 60)")
    args = parser.parse_args()

    workspace = Path(args.workspace)
    workspace.mkdir(parents=True, exist_ok=True)

    interactive = not args.no_interactive

    task = args.task or read_file(workspace / "task.md")
    if not task:
        print("Error: --task is required (or write task to workspace/task.md)", file=sys.stderr)
        sys.exit(1)
    write_file(workspace / "task.md", task)

    state = load_state(workspace)
    if state.get("status") in ("pass", "fail"):
        log(f"workspace already completed with status={state['status']} — exiting")
        return

    start_iter    = state.get("iteration", 0) + 1
    max_iter      = args.max_iter
    recipient     = args.recipient
    session_uuid  = args.session_uuid

    log(f"starting — iterations {start_iter}–{max_iter}, workspace={workspace}, interactive={interactive}")
    if session_uuid:
        log(f"agent injection: session UUID={session_uuid[:8]}… (primary notification path)")
    elif recipient:
        log(f"direct message: recipient={recipient} channel={args.channel} (fallback-only mode)")

    # ── Intake ────────────────────────────────────────────────────────────────
    criteria = run_intake(
        workspace, task,
        max_intake_iter=args.max_intake_iter,
        recipient=recipient,
        channel=args.channel,
        interactive=interactive,
        session_uuid=session_uuid,
    )

    # ── Pre-start confirmation gate ────────────────────────────────────────────
    if interactive:
        task = read_file(workspace / "task.md") or task  # user may have edited it
        approved = confirm_prestart(
            workspace, task, criteria,
            recipient=recipient,
            channel=args.channel,
            timeout_min=args.checkpoint_timeout,
            session_uuid=session_uuid,
        )
        if not approved:
            save_state(workspace, {"iteration": 0, "status": "cancelled"})
            log("aborted by user before main loop")
            return
        # Re-read criteria in case user edited task (intake locked criteria before edit)
        criteria = read_file(workspace / "criteria.md")

    # ── Loop ──────────────────────────────────────────────────────────────────
    feedback = read_file(workspace / "feedback.md")

    for iteration in range(start_iter, max_iter + 1):
        log(f"────── Iteration {iteration}/{max_iter} ──────")
        save_state(workspace, {"iteration": iteration, "status": "running"})

        # Worker
        try:
            output = run_worker(workspace, task, criteria, feedback, iteration, max_iter,
                                worker_timeout=args.worker_timeout)
        except RuntimeError as exc:
            log(f"WARNING: iter {iteration}: worker call failed ({exc}) — skipping to next iteration")
            gaps = f"Worker failed with error: {exc}"
            entry = f"\n## Iteration {iteration} worker error\n{gaps}\n"
            with open(workspace / "feedback.md", "a") as f:
                f.write(entry)
            feedback += entry
            continue

        if "[BLOCKED]" in output:
            log(f"worker BLOCKED — skipping judge this iteration")
            gaps = f"Worker was blocked:\n{output}"
        else:
            # Judge
            verdict, is_pass = run_judge(workspace, criteria, output, iteration, max_iter,
                                         judge_timeout=args.judge_timeout)

            if is_pass:
                write_file(workspace / "final-output.md", output)
                save_state(workspace, {"iteration": iteration, "status": "pass"})
                log(f"✅ PASSED on iteration {iteration}/{max_iter}")
                notify(
                    args.recipient,
                    f"✅ checkmate: PASSED on iteration {iteration}/{max_iter}\n\n{output}",
                    args.channel,
                )
                return

            gaps = extract_gaps(verdict)

            # ── Per-iteration checkpoint (interactive) ──────────────────────
            if interactive and (recipient or session_uuid) and iteration < max_iter:
                gaps = run_iteration_checkpoint(
                    workspace, iteration, max_iter,
                    output, verdict, gaps,
                    recipient=recipient,
                    channel=args.channel,
                    timeout_min=args.checkpoint_timeout,
                    session_uuid=session_uuid,
                )
                if gaps == "__STOP__":
                    break

        # Accumulate feedback for next worker
        if gaps and gaps != "__STOP__":
            ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            entry = f"\n## Iteration {iteration} gaps ({ts})\n{gaps}\n"
            with open(workspace / "feedback.md", "a") as f:
                f.write(entry)
            feedback += entry

    # ── Max iterations reached / stopped ──────────────────────────────────────
    best_iter, best_output = find_best_iteration(workspace)
    write_file(workspace / "final-output.md", best_output)
    save_state(workspace, {"iteration": max_iter, "status": "fail"})

    best_verdict = read_file(workspace / f"iter-{best_iter:02d}" / "verdict.md")
    log(f"⚠️ max iterations reached — best attempt was iter {best_iter}")
    notify(
        args.recipient,
        (
            f"⚠️ checkmate: max iterations ({max_iter}) reached without full PASS\n\n"
            f"Best attempt: iteration {best_iter}\n\n{best_output}\n\n"
            f"---\nFinal judge report:\n{best_verdict}"
        ),
        args.channel,
    )


if __name__ == "__main__":
    main()
