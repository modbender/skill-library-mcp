#!/usr/bin/env python3
import argparse
from pathlib import Path

TEMPLATES = {
    "G1": """Objective: Complete planning artifacts.
Tasks:
1) Finalize requirements with testable acceptance criteria.
2) Capture Definition of Done.
3) List assumptions and risks.
4) If research_mode=true, produce docs/research-notes.md with options and recommendation.
Validations:
- requirements are testable and unambiguous
- acceptance criteria map to tests
Done condition:
- docs/requirements.md, docs/plan.md, docs/progress.md updated""",
    "G2": """Objective: Complete architecture baseline and ADR.
Tasks:
1) Update docs/architecture.md.
2) Update docs/adr/ADR-0001-initial-architecture.md.
3) For brownfield, ensure onboarding artifacts are complete.
Validations:
- architecture supports must-have journeys
- ADR has alternatives + trade-offs
Done condition:
- G2 docs complete and traceability updated""",
    "G3": """Objective: Deliver and verify first vertical slice.
Tasks:
1) Implement first slice for top priority journey.
2) Add unit + integration tests.
3) Run manual smoke test.
Validations:
- unit/integration pass
- manual smoke recorded
Done condition:
- slice works end-to-end with evidence""",
    "G4": """Objective: Complete full build and baseline verification.
Tasks:
1) Implement remaining v1 scope.
2) Run full validation suite.
3) Resolve failures or document blockers.
Validations:
- lint/type/build pass
- unit/integration/e2e pass
Done condition:
- in-scope v1 complete with evidence""",
    "G5": """Objective: Execute security and quality gate.
Tasks:
1) Run secret/dependency checks.
2) Verify auth/input/error handling.
3) Run performance smoke checks.
Validations:
- no unresolved critical/high findings
Done condition:
- security evidence captured""",
    "G6": """Objective: Prepare and verify release candidate.
Tasks:
1) Complete release checklist.
2) Validate rollback instructions.
3) Confirm monitoring/alerts baseline.
Validations:
- release checklist complete
- rollback validated
Done condition:
- RC ready for approval/deploy""",
    "G7": """Objective: Complete handover.
Tasks:
1) Run post-deploy smoke tests.
2) Finalize handover notes.
3) Create next-iteration backlog.
Validations:
- critical journeys pass in deployed env
Done condition:
- progress=100% and handover complete""",
}

HEADER = """You are implementing Gate {gate} for this project.

## SPEC-DRIVEN RULES (NON-NEGOTIABLE)
1. You are implementing ONLY what is specified in the spec document.
2. Do NOT add features, abstractions, or "improvements" not in the spec.
3. If the spec is unclear or incomplete, STOP and ask for clarification.
4. Do NOT guess at requirements. Ever.
5. Your output will be verified against the acceptance criteria from the spec.
6. No spec = No implementation. Period.

## TASK-LEVEL DOC UPDATE RULES (NON-NEGOTIABLE)
After THIS task, you MUST directly update all relevant docs yourself:
- docs/tasks.md
- docs/progress.md
- docs/change-log.md
- docs/traceability.md
- docs/test-results.md
- docs/agent-handoff.md

In docs/agent-handoff.md include:
- Task summary (what you changed)
- Spec reference used
- CLI checks for OpenClaw agent to run
- Browser/manual checks for OpenClaw agent to run (or N/A)
- Known risks / caveats

## OUTPUT CONTRACT (STRICT)
Return a final completion block that includes:
- STATUS: DONE | BLOCKED
- TASK: <exact task>
- SPEC_REF: <exact spec ref>
- FILES_CHANGED: <list>
- VALIDATION_RUN: <commands and outcomes>
- OPENCLAW_VERIFY: <cli checks + browser checks or N/A>
- RISKS: <explicit list or NONE>

If any required input is missing (especially spec), output STATUS: BLOCKED and do not implement.

## CONSTRAINTS
- Follow AGENTS.md workflow rules exactly.
- This run is for ONE task only; do not attempt whole-project implementation in one pass.
- Do not claim completion without evidence.
- Implementation must match spec acceptance criteria exactly.
"""


def main():
    parser = argparse.ArgumentParser(description="Generate gate-specific coding-agent prompt")
    parser.add_argument("--gate", required=True, choices=["G1", "G2", "G3", "G4", "G5", "G6", "G7"])
    parser.add_argument("--agent", required=True, choices=["codex", "claude", "opencode", "pi"])
    parser.add_argument("--project-mode", choices=["greenfield", "brownfield"], default="greenfield")
    parser.add_argument("--execution-mode", choices=["autonomous", "gated"], default="gated")
    parser.add_argument("--research-mode", choices=["true", "false"], default="false")
    parser.add_argument("--task", required=True, help="Single task summary")
    parser.add_argument("--spec-ref", default="", help="Spec reference for this task")
    parser.add_argument("--output", help="Write prompt to file")
    args = parser.parse_args()

    body = TEMPLATES[args.gate]
    if args.gate == "G4":
        body += "\nTask slicing requirement:\n- Read docs/g4-task-plan.md and execute only one unchecked task for this run.\n- Mark only that task as done, leave others untouched.\n"
    mode_note = f"Coding agent: {args.agent}\nProject mode: {args.project_mode}\nExecution mode: {args.execution_mode}\nResearch mode: {args.research_mode}\n"

    if args.project_mode == "brownfield" and args.gate in ("G2", "G4"):
        mode_note += "Brownfield emphasis: preserve compatibility, run parity and rollback checks.\n"
    if args.project_mode == "brownfield" and args.gate in ("G1", "G2"):
        mode_note += (
            "Brownfield onboarding requirement: you (coding agent) must directly update onboarding docs: "
            "as-is-architecture, system-inventory, dependency-map, legacy-risk-register, "
            "compatibility-matrix, migration-plan, characterization-tests.\n"
        )

    spec_section = ""
    if args.spec_ref:
        spec_section = f"\n## TASK INPUTS\n- Task: {args.task}\n- Spec Reference: {args.spec_ref}\n"
    else:
        spec_section = f"\n## TASK INPUTS\n- Task: {args.task}\n- Spec Reference: (not provided for this gate)\n"

    handoff_instruction = (
        "\n## WAKE HANDOFF FORMAT (MANDATORY)\n"
        "When done, run exactly one wake command that includes: task done + check instructions.\n"
        "Format:\n"
        "openclaw gateway wake --text \"Done: <gate> | task: <short> | handoff: see docs/agent-handoff.md for CLI+Browser checks\" --mode now\n"
    )

    prompt = (
        HEADER.format(gate=args.gate)
        + "\n"
        + mode_note
        + spec_section
        + "\n"
        + body
        + "\n"
        + handoff_instruction
    )

    if args.output:
        Path(args.output).write_text(prompt, encoding="utf-8")
        print(f"Prompt written to {args.output}")
    else:
        print(prompt)


if __name__ == "__main__":
    main()
