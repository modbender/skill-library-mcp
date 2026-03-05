#!/usr/bin/env python3
"""
init_pipeline.py — Initialize a new skill-factory workspace

Usage:
    init_pipeline.py "<skill idea>" --workspace <path>

Examples:
    init_pipeline.py "A skill for managing Stripe subscriptions" --workspace /tmp/sf-stripe
    init_pipeline.py "PDF table extractor" --workspace ~/skill-builds/pdf-tables

Creates the workspace directory and writes idea.md with a structured template.
Edit idea.md before running pipeline.sh.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

IDEA_TEMPLATE = """\
# Skill Idea

**Created:** {date}

## Core Idea

{idea}

## Problem it solves

[TODO: What pain point does this skill address? Who feels that pain?]

## Target users

[TODO: Who will use this skill? What tools/workflows do they already use?]

## Key capabilities

[TODO: List 3-5 concrete things the skill enables an agent to do]
-
-
-

## Similar / competing skills

[TODO: What exists already? How is this different?]

## Success criteria

[TODO: How do you know the skill is complete and useful?]
- The skill triggers correctly when users describe [...]
- An agent using the skill can [...]
- The skill produces outputs that [...]

## Notes

[TODO: Anything else relevant — constraints, known limitations, ideas to explore]
"""

STAGES = ["market", "planner", "arch", "builder", "auditor", "docs", "pricer"]


def init_pipeline(idea: str, workspace_path: Path) -> bool:
    # Reject if workspace already exists and is non-empty
    if workspace_path.exists():
        contents = list(workspace_path.iterdir())
        if contents:
            print(f"[ERROR] Workspace already exists and is not empty: {workspace_path}")
            print("  Use a different path, or remove the existing workspace first.")
            return False

    workspace_path.mkdir(parents=True, exist_ok=True)
    print(f"[OK] Created workspace: {workspace_path}")

    # Write idea.md
    idea_path = workspace_path / "idea.md"
    idea_content = IDEA_TEMPLATE.format(
        idea=idea.strip(),
        date=datetime.now().strftime("%Y-%m-%d"),
    )
    idea_path.write_text(idea_content)
    print(f"[OK] Created idea.md")

    # Write pipeline state file (tracks which stages have run)
    state_path = workspace_path / ".pipeline_state"
    state_path.write_text("# pipeline state — do not edit manually\n")
    print(f"[OK] Created .pipeline_state")

    print()
    print(f"Workspace ready: {workspace_path}")
    print()
    print("Next steps:")
    print(f"  1. Edit {idea_path} — fill in the TODOs")
    print(f"  2. Run the pipeline:")
    print(f"       bash pipeline.sh --workspace {workspace_path}")
    print(f"  3. Or run a single stage:")
    print(f"       bash pipeline.sh --workspace {workspace_path} --from market --to market")
    print()
    print(f"Pipeline stages: {' → '.join(STAGES)}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a skill-factory workspace for a new skill idea.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("idea", help="One-sentence description of the skill idea")
    parser.add_argument("--workspace", required=True, help="Path to create the workspace directory")
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    success = init_pipeline(args.idea, workspace)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
