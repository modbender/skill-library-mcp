#!/usr/bin/env python3
import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DOC_UPDATE_FILES = [
    "docs/tasks.md",
    "docs/change-log.md",
    "docs/traceability.md",
    "docs/test-results.md",
    "docs/progress.md",
    "docs/agent-handoff.md",
]

BROWNFIELD_ONBOARD_FILES = [
    "docs/as-is-architecture.md",
    "docs/system-inventory.md",
    "docs/dependency-map.md",
    "docs/legacy-risk-register.md",
    "docs/compatibility-matrix.md",
    "docs/migration-plan.md",
    "docs/characterization-tests.md",
]

ASSUMPTION_MARKERS = [
    "i assumed",
    "we assumed",
    "assumed that",
    "probably",
    "likely",
    "guessed",
    "defaulted to",
    "for convenience",
]

def run(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if p.stdout:
        print(p.stdout.strip())
    if p.returncode != 0:
        if p.stderr:
            print(p.stderr.strip())
        raise SystemExit(p.returncode)


def run_capture(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    out = (p.stdout or "") + ("\n" + p.stderr if p.stderr else "")
    return p.returncode, out.strip()


def file_hash(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def snapshot_files(root: Path, files: list[str]):
    snap = {}
    for rel in files:
        snap[rel] = file_hash(root / rel)
    return snap


def changed_files(root: Path, files: list[str], before: dict):
    changed = []
    for rel in files:
        if before.get(rel) != file_hash(root / rel):
            changed.append(rel)
    return changed


def load_context(root: Path):
    p = root / ".orchestrator" / "context.json"
    if not p.exists():
        raise SystemExit(f"Missing context file: {p}. Run init_project_docs.py first.")
    return p, json.loads(p.read_text(encoding="utf-8"))


def save_context(path: Path, ctx):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ctx, indent=2), encoding="utf-8")


def append_validation_log(root: Path, gate: str, lines: list[str]):
    log_path = root / "docs" / "validation-log.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"\n## {gate} Validation\n")
        for line in lines:
            f.write(f"- {line}\n")


def set_gate_state(root: Path, gate: str, state: str, note: str):
    run(
        [
            "python3",
            str(ROOT / "gate_status.py"),
            "set",
            "--root",
            str(root),
            "--gate",
            gate,
            "--state",
            state,
            "--note",
            note,
        ]
    )


def check_g4_task_plan(root: Path):
    path = root / "docs" / "g4-task-plan.md"
    if not path.exists():
        raise SystemExit("G4 requires docs/g4-task-plan.md with task breakdown.")
    text = path.read_text(encoding="utf-8", errors="ignore")
    if "[ ]" not in text and "[x]" not in text and "[X]" not in text:
        raise SystemExit("G4 task plan must use checklist format ([ ] and [x]).")


def check_g4_ready_for_pass(root: Path):
    path = root / "docs" / "g4-task-plan.md"
    text = path.read_text(encoding="utf-8", errors="ignore")
    if "[ ]" in text:
        raise SystemExit("Cannot mark G4 PASS while unchecked tasks remain in docs/g4-task-plan.md")


def build_fix_prompt(
    proj_root: Path,
    gate: str,
    task: str,
    spec_ref: str,
    failing_cmd: str,
    failure_output: str,
    retry_num: int,
    max_retries: int,
):
    prompt_path = proj_root / "docs" / f"prompt-{gate}-fix-{retry_num}.txt"
    safe_out = (failure_output or "(no output)")[:1200]
    spec_line = spec_ref if spec_ref else "requirements.md#relevant-section"
    prompt = f"""You are fixing Gate {gate} after validation failure.

## SPEC-DRIVEN RULES (NON-NEGOTIABLE)
1. Implement ONLY what is specified.
2. Do NOT add unrequested features.
3. Do NOT guess at requirements.
4. If ambiguity remains, document open questions and stop.

## TASK CONTEXT
- Task: {task}
- Spec reference: {spec_line}
- Retry attempt: {retry_num}/{max_retries}

## FAILURE TO FIX
- Command: {failing_cmd}
- Output:
{safe_out}

## REQUIRED ACTIONS
1. Fix the concrete failure above.
2. Re-run the relevant local checks you can run.
3. Update these docs yourself:
   - docs/tasks.md
   - docs/progress.md
   - docs/change-log.md
   - docs/traceability.md
   - docs/test-results.md
   - docs/agent-handoff.md
4. In docs/agent-handoff.md include:
   - What you changed
   - Why it failed
   - Exact CLI checks for OpenClaw agent to run
   - Exact browser checks for OpenClaw agent to run (or N/A)

When fully done, run:
openclaw gateway wake --text "Done: {gate} fix attempt {retry_num} complete | verify: docs/agent-handoff.md" --mode now
"""
    prompt_path.write_text(prompt, encoding="utf-8")
    return prompt_path


def execute_agent(agent_cmd_base: list[str], prompt_file: str):
    cmd = list(agent_cmd_base) + ["--prompt-file", str(prompt_file)]
    run(cmd)


def run_validation_commands(validate_cmds: list[str], proj_root: Path):
    lines = []
    for cmd in validate_cmds:
        code, out = run_capture(["bash", "-lc", cmd], cwd=str(proj_root))
        snippet = (out[:500] + "...") if len(out) > 500 else out
        if code != 0:
            lines.append(f"FAIL `{cmd}` exit={code}")
            if snippet:
                lines.append(f"Output: {snippet}")
            return False, lines, cmd, snippet
        lines.append(f"PASS `{cmd}`")
        if snippet:
            lines.append(f"Output: {snippet}")
    return True, lines, "", ""


def check_assumption_markers(proj_root: Path):
    handoff = proj_root / "docs" / "agent-handoff.md"
    if not handoff.exists():
        return True, []
    text = handoff.read_text(encoding="utf-8", errors="ignore").lower()
    hits = [m for m in ASSUMPTION_MARKERS if m in text]
    if hits:
        return False, hits
    return True, []


def parse_spec_acceptance_criteria(spec_file: Path):
    if not spec_file.exists():
        return []
    lines = spec_file.read_text(encoding="utf-8", errors="ignore").splitlines()
    ids = []
    for line in lines:
        s = line.strip()
        if s.startswith("AC-") and ":" in s:
            ids.append(s.split(":", 1)[0].strip())
    return sorted(set(ids))


def collect_g4_task_spec_refs(root: Path):
    path = root / "docs" / "g4-task-plan.md"
    if not path.exists():
        return []
    refs = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = line.strip()
        if not s.startswith("-"):
            continue
        marker = "(Spec: "
        if marker in s and ")" in s.split(marker, 1)[1]:
            ref = s.split(marker, 1)[1].split(")", 1)[0].strip()
            if ref:
                refs.append(ref)
    return refs


def validate_spec_coverage_for_g4(root: Path, spec_ref: str):
    refs = collect_g4_task_spec_refs(root)
    if not refs:
        return False, "G4 spec coverage check failed: docs/g4-task-plan.md has no '(Spec: ...)' references."
    if spec_ref and spec_ref not in refs:
        return False, f"G4 spec coverage check failed: {spec_ref} not present in docs/g4-task-plan.md task refs."
    return True, ""


def validate_ac_mapping(proj_root: Path, spec_ref: str):
    if not spec_ref:
        return True, []
    spec_rel = spec_ref.split("#", 1)[0]
    spec_file = proj_root / "docs" / spec_rel
    ac_ids = parse_spec_acceptance_criteria(spec_file)
    if not ac_ids:
        return True, []
    handoff = proj_root / "docs" / "agent-handoff.md"
    if not handoff.exists():
        return False, ["AC mapping check failed: docs/agent-handoff.md missing."]
    text = handoff.read_text(encoding="utf-8", errors="ignore")
    missing = [ac for ac in ac_ids if ac not in text]
    if missing:
        return False, ["AC mapping missing in agent handoff: " + ", ".join(missing)]
    return True, []


def get_git_changed_files(proj_root: Path):
    code, out = run_capture(["git", "status", "--porcelain"], cwd=str(proj_root))
    if code != 0:
        return []
    changed = []
    for line in out.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip() if len(line) > 3 else ""
        if path:
            changed.append(path)
    return changed


def parse_allowed_scope_from_spec(spec_file: Path):
    if not spec_file.exists():
        return []
    lines = spec_file.read_text(encoding="utf-8", errors="ignore").splitlines()
    allowed = []
    capture = False
    for line in lines:
        s = line.strip()
        lower = s.lower()
        if lower.startswith("##") and "allowed scope files" in lower:
            capture = True
            continue
        if capture and s.startswith("##") and "allowed scope files" not in lower:
            break
        if capture and s.startswith("-"):
            candidate = s.lstrip("-").strip().strip("`")
            if candidate:
                allowed.append(candidate)
    return allowed


def validate_drift_against_spec(proj_root: Path, spec_ref: str):
    if not spec_ref:
        return True, []
    spec_rel = spec_ref.split("#", 1)[0]
    spec_file = proj_root / "docs" / spec_rel
    allowed = parse_allowed_scope_from_spec(spec_file)
    if not allowed:
        return True, []
    changed = get_git_changed_files(proj_root)
    if not changed:
        return True, []

    violations = []
    for path in changed:
        if path.startswith("docs/") or path.startswith(".orchestrator/"):
            continue
        if not any(path == a or path.startswith(a.rstrip("/") + "/") for a in allowed):
            violations.append(path)

    if violations:
        return False, ["Spec drift detected (changed outside allowed scope): " + ", ".join(sorted(set(violations)))]
    return True, []


def write_validation_artifact(
    proj_root: Path,
    gate: str,
    task: str,
    spec_ref: str,
    validate_cmds: list[str],
    validation_lines: list[str],
    ui_review_note: str,
    status: str,
):
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = proj_root / "docs" / "validation-artifacts"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{gate}-{ts}.json"
    payload = {
        "timestamp": ts,
        "gate": gate,
        "task": task,
        "specRef": spec_ref,
        "status": status,
        "validateCmds": validate_cmds,
        "uiReviewNote": ui_review_note,
        "results": validation_lines,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def main():
    parser = argparse.ArgumentParser(description="Single-task gate runner (agent-executed, evidence-driven)")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--gate", required=True, choices=["G1", "G2", "G3", "G4", "G5", "G6", "G7"])
    parser.add_argument(
        "--agent",
        required=True,
        choices=["codex", "claude", "opencode", "pi"],
        help="Coding agent to execute implementation work",
    )
    parser.add_argument(
        "--fallback-agent",
        choices=["codex", "claude", "opencode", "pi"],
        help="Fallback coding agent (required first time if context has no fallback)",
    )
    parser.add_argument("--project-mode", choices=["greenfield", "brownfield"], default="greenfield")
    parser.add_argument("--execution-mode", choices=["autonomous", "gated"], default="gated")
    parser.add_argument("--research-mode", choices=["true", "false"], default="false")
    parser.add_argument("--task", required=True, help="Single task summary (one task per run)")
    parser.add_argument("--evidence", default="", help="Evidence summary")
    parser.add_argument(
        "--status",
        default="IN_PROGRESS",
        choices=["IN_PROGRESS", "PASS", "FAIL", "BLOCKED"],
        help="Gate status to set for this run",
    )
    parser.add_argument("--prompt-out", help="Optional prompt output path")
    parser.add_argument("--full-auto", action="store_true", help="Pass full-auto to codex in agent_exec")
    parser.add_argument("--agent-dry-run", action="store_true", help="Print coding-agent command without executing it")
    parser.add_argument(
        "--validate-cmd",
        action="append",
        default=[],
        help="Validation command to run after agent execution (repeatable). Required when status=PASS.",
    )
    parser.add_argument(
        "--ui-review-note",
        default="",
        help="Manual browser/UI verification notes produced by OpenClaw agent after checks.",
    )
    parser.add_argument(
        "--requires-browser-check",
        action="store_true",
        help="Require explicit browser/manual review note for this task.",
    )
    parser.add_argument(
        "--spec-ref",
        default="",
        help="Spec reference for this task (required for G3/G4). Format: specs/feature.md#section or requirements.md#feature",
    )
    parser.add_argument(
        "--auto-fix-retries",
        type=int,
        default=2,
        help="Autonomous mode: retries with fix prompts after failed validations (default: 2).",
    )
    parser.add_argument(
        "--auto-block-on-retry-exhaust",
        action="store_true",
        help="When retries are exhausted, auto-set gate state to BLOCKED with failure reason before exit.",
    )
    args = parser.parse_args()

    proj_root = Path(args.root).resolve()
    prompt_out = args.prompt_out or str(proj_root / "docs" / f"prompt-{args.gate}.txt")

    # Context + agent persistence
    ctx_path, ctx = load_context(proj_root)
    ctx.setdefault("primaryAgent", "")
    ctx.setdefault("fallbackAgent", "")

    if not ctx["primaryAgent"]:
        ctx["primaryAgent"] = args.agent
    elif ctx["primaryAgent"] != args.agent:
        print(f"[warn] overriding primaryAgent from {ctx['primaryAgent']} to {args.agent}")
        ctx["primaryAgent"] = args.agent

    if not ctx["fallbackAgent"]:
        if not args.fallback_agent:
            raise SystemExit("Missing fallback agent. Provide --fallback-agent for first run.")
        ctx["fallbackAgent"] = args.fallback_agent
    elif args.fallback_agent and args.fallback_agent != ctx["fallbackAgent"]:
        print(f"[warn] overriding fallbackAgent from {ctx['fallbackAgent']} to {args.fallback_agent}")
        ctx["fallbackAgent"] = args.fallback_agent

    ctx["projectMode"] = args.project_mode
    ctx["executionMode"] = args.execution_mode
    ctx["researchMode"] = True if args.research_mode == "true" else False
    save_context(ctx_path, ctx)

    # Evidence and manual-check policy
    if args.status == "PASS" and not args.validate_cmd:
        raise SystemExit("status=PASS requires at least one --validate-cmd to prove working behavior.")
    if args.status == "PASS" and args.agent_dry_run:
        raise SystemExit("status=PASS is not allowed with --agent-dry-run. Execute the coding agent for real.")

    # Every task should include validation activity (CLI and/or browser)
    if args.status in ("IN_PROGRESS", "PASS") and not args.validate_cmd and not args.ui_review_note:
        raise SystemExit(
            "Each task must include post-task validation evidence. Provide --validate-cmd and/or --ui-review-note."
        )

    if args.requires_browser_check and not args.ui_review_note:
        raise SystemExit("This task requires browser checks. Provide --ui-review-note after manual browser validation.")

    # Spec-driven enforcement: G3/G4 require spec reference
    if args.gate in ("G3", "G4") and not args.spec_ref:
        raise SystemExit(
            f"{args.gate} requires --spec-ref. No implementation without a spec.\n"
            "Format: --spec-ref specs/feature.md#section or --spec-ref requirements.md#feature"
        )

    # Verify spec file exists
    if args.spec_ref:
        spec_path = args.spec_ref.split("#")[0]
        full_spec_path = proj_root / "docs" / spec_path
        if not full_spec_path.exists():
            raise SystemExit(f"Spec file not found: {full_spec_path}. Create the spec before implementation.")

    if args.gate == "G4":
        check_g4_task_plan(proj_root)
        if args.status == "PASS":
            check_g4_ready_for_pass(proj_root)

    # 1) Generate initial gate prompt
    run(
        [
            "python3",
            str(ROOT / "generate_gate_prompt.py"),
            "--gate",
            args.gate,
            "--agent",
            args.agent,
            "--project-mode",
            args.project_mode,
            "--execution-mode",
            args.execution_mode,
            "--research-mode",
            args.research_mode,
            "--task",
            args.task,
            "--spec-ref",
            args.spec_ref,
            "--output",
            prompt_out,
        ]
    )

    # Build agent command base (prompt-file added per attempt)
    agent_cmd_base = [
        "python3",
        str(ROOT / "agent_exec.py"),
        "--root",
        str(proj_root),
        "--agent",
        args.agent,
        "--spec-ref",
        args.spec_ref,
    ]
    if args.gate in ("G3", "G4"):
        agent_cmd_base.append("--enforce-spec-ref")
    if args.full_auto:
        agent_cmd_base.append("--full-auto")
    if args.agent_dry_run:
        agent_cmd_base.append("--dry-run")

    max_fix_retries = args.auto_fix_retries if args.execution_mode == "autonomous" else 0
    attempt = 0
    current_prompt = prompt_out
    all_validation_lines = []

    while True:
        before_docs = snapshot_files(proj_root, DOC_UPDATE_FILES)
        before_brownfield = snapshot_files(proj_root, BROWNFIELD_ONBOARD_FILES)

        # 2) Execute coding agent
        execute_agent(agent_cmd_base, current_prompt)

        # 3) Verify docs were updated by coding agent (every task, every run)
        changed = changed_files(proj_root, DOC_UPDATE_FILES, before_docs)
        if not args.agent_dry_run and args.status in ("IN_PROGRESS", "PASS") and not changed:
            raise SystemExit(
                "Coding agent did not update required docs (tasks/change-log/traceability/test-results/progress/agent-handoff). "
                "Docs updates must be done by the coding agent after each task."
            )

        # Brownfield onboarding (G1/G2) must also be authored by coding agent
        changed_brownfield = []
        if args.project_mode == "brownfield" and args.gate in ("G1", "G2") and not args.agent_dry_run:
            changed_brownfield = changed_files(proj_root, BROWNFIELD_ONBOARD_FILES, before_brownfield)
            if not changed_brownfield:
                raise SystemExit(
                    "Brownfield onboarding docs were not updated by the coding agent during this run. "
                    "Agent must update onboarding artifacts directly."
                )

        # 4) CLI/manual validations by orchestrator
        ok, validation_lines, failing_cmd, failure_snippet = run_validation_commands(args.validate_cmd, proj_root)

        assumptions_ok, assumption_hits = check_assumption_markers(proj_root)
        if not assumptions_ok:
            ok = False
            failing_cmd = "assumption-detector:docs/agent-handoff.md"
            failure_snippet = "Assumption language detected: " + ", ".join(assumption_hits)
            validation_lines.append("FAIL assumption detector: " + ", ".join(assumption_hits))

        if args.gate == "G4":
            coverage_ok, coverage_msg = validate_spec_coverage_for_g4(proj_root, args.spec_ref)
            if not coverage_ok:
                ok = False
                failing_cmd = "g4-spec-coverage:docs/g4-task-plan.md"
                failure_snippet = coverage_msg
                validation_lines.append("FAIL " + coverage_msg)

        if args.gate in ("G3", "G4") and args.spec_ref:
            ac_ok, ac_msgs = validate_ac_mapping(proj_root, args.spec_ref)
            if not ac_ok:
                ok = False
                failing_cmd = "ac-mapping:docs/agent-handoff.md"
                failure_snippet = " | ".join(ac_msgs)
                validation_lines.extend(["FAIL " + msg for msg in ac_msgs])

            drift_ok, drift_msgs = validate_drift_against_spec(proj_root, args.spec_ref)
            if not drift_ok:
                ok = False
                failing_cmd = "spec-drift:git-status"
                failure_snippet = " | ".join(drift_msgs)
                validation_lines.extend(["FAIL " + msg for msg in drift_msgs])

        if args.ui_review_note:
            validation_lines.append(f"UI review: {args.ui_review_note}")
        if changed:
            validation_lines.append("Docs updated by agent: " + ", ".join(changed))
        if changed_brownfield:
            validation_lines.append("Brownfield onboarding docs updated by agent: " + ", ".join(changed_brownfield))

        all_validation_lines.extend(validation_lines)

        if ok:
            break

        # Validation failed: autonomous fix-retry loop
        if args.agent_dry_run:
            append_validation_log(proj_root, args.gate, all_validation_lines)
            raise SystemExit(f"Validation failed in dry-run mode: `{failing_cmd}`")

        if attempt >= max_fix_retries:
            append_validation_log(proj_root, args.gate, all_validation_lines)
            failure_note = (
                f"Retry exhausted after {attempt} attempts. Last failed command: {failing_cmd}. "
                f"Failure: {failure_snippet[:240]}"
            )
            if args.auto_block_on_retry_exhaust:
                set_gate_state(proj_root, args.gate, "BLOCKED", failure_note)
                append_validation_log(proj_root, args.gate, ["Auto-classified as BLOCKED due to retry exhaustion."])
            raise SystemExit(
                f"Validation failed after {attempt} fix retries. Last failed command: `{failing_cmd}`"
            )

        attempt += 1
        all_validation_lines.append(
            f"Auto-fix retry {attempt}/{max_fix_retries}: re-invoking coding agent with failure details."
        )

        fix_prompt_path = build_fix_prompt(
            proj_root=proj_root,
            gate=args.gate,
            task=args.task,
            spec_ref=args.spec_ref,
            failing_cmd=failing_cmd,
            failure_output=failure_snippet,
            retry_num=attempt,
            max_retries=max_fix_retries,
        )
        current_prompt = str(fix_prompt_path)

    # 5) Persist validation evidence log + machine artifact
    if all_validation_lines:
        append_validation_log(proj_root, args.gate, all_validation_lines)

    artifact_path = write_validation_artifact(
        proj_root=proj_root,
        gate=args.gate,
        task=args.task,
        spec_ref=args.spec_ref,
        validate_cmds=args.validate_cmd,
        validation_lines=all_validation_lines,
        ui_review_note=args.ui_review_note,
        status=args.status,
    )
    append_validation_log(proj_root, args.gate, [f"Validation artifact: {artifact_path.relative_to(proj_root)}"])

    # 6) Gate status + dashboard
    set_gate_state(proj_root, args.gate, args.status, args.task)

    run(["python3", str(ROOT / "progress_dashboard.py"), "--root", str(proj_root)])


if __name__ == "__main__":
    main()
