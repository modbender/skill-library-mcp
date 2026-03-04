#!/usr/bin/env python3
import argparse
import shlex
import subprocess
from pathlib import Path


def run(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if p.stdout:
        print(p.stdout.strip())
    if p.returncode != 0:
        if p.stderr:
            print(p.stderr.strip())
        raise SystemExit(p.returncode)


def main():
    parser = argparse.ArgumentParser(description="Execute a gate prompt with selected coding agent")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--agent", required=True, choices=["codex", "claude", "opencode", "pi"])
    parser.add_argument("--prompt-file", required=True, help="Prompt file path")
    parser.add_argument("--spec-ref", default="", help="Spec reference for dispatch safety checks")
    parser.add_argument(
        "--enforce-spec-ref",
        action="store_true",
        help="Fail dispatch if --spec-ref is missing (use for implementation gates)",
    )
    parser.add_argument("--full-auto", action="store_true", help="Use full-auto mode where supported")
    parser.add_argument("--dry-run", action="store_true", help="Print command without executing")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    prompt = Path(args.prompt_file).resolve()
    if not prompt.exists():
        raise SystemExit(f"Prompt file not found: {prompt}")

    if args.enforce_spec_ref and not args.spec_ref.strip():
        raise SystemExit("Dispatch blocked: --spec-ref is required for this run.")

    text = prompt.read_text(encoding="utf-8")

    # Additional dispatch-time guard: do not launch if prompt itself indicates missing spec.
    if args.enforce_spec_ref and "Spec Reference: (not provided for this gate)" in text:
        raise SystemExit("Dispatch blocked: prompt indicates missing spec reference.")

    if args.agent == "codex":
        cmd = ["codex", "exec"]
        if args.full_auto:
            cmd.append("--full-auto")
        cmd.append(text)
    elif args.agent == "claude":
        # Claude CLI generally accepts task text directly
        cmd = ["claude", text]
    elif args.agent == "opencode":
        cmd = ["opencode", "run", text]
    else:  # pi
        cmd = ["pi", "-p", text]

    print("Agent command:")
    print(" ".join(shlex.quote(c) for c in cmd))

    if args.dry_run:
        return

    run(cmd, cwd=str(root))


if __name__ == "__main__":
    main()
