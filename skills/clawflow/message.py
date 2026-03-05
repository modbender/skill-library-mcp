#!/usr/bin/env python3
"""Generate clawflow messages and task files.

All templates produce ready-to-use files with real content passed via arguments.
Agent IDs should match `openclaw agents list` output.

Usage:
    python3 message.py dispatch --from AGENT --to AGENT --title TITLE [OPTIONS]
    python3 message.py reply --from AGENT --task-id ID --subtask-id ID --status done|failed [OPTIONS]
    python3 message.py init-task --title TITLE [--task-id ID] [OPTIONS]

Examples:
    # Create a dispatch message
    python3 message.py dispatch --from analyst --to data-extractor \\
        --title "Extract Q3 sales" \\
        --task-id task-abc123 --subtask-id st-extract \\
        --context "We need Q3 numbers from sales.csv." \\
        --instructions "1. Parse sales.csv\n2. Sum by region\n3. Return markdown table" \\
        --expected-output "Markdown table: Region | Revenue | Change"

    # Create a task.md to track a coordinating task
    python3 message.py init-task --title "Q3 Analysis" --task-id task-abc123 \\
        --from analyst --subtasks st-extract st-analyse st-write

    # Send a dispatch message to a peer via openclaw
    openclaw agent --agent data-extractor --message "$(cat dispatch-st-extract.md)"
"""

import argparse
import uuid
from datetime import datetime, timezone
from pathlib import Path


def gen_id():
    return str(uuid.uuid4())[:8]


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_file(content: str, directory: Path, filename: str):
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / filename
    path.write_text(content)
    print(f"Created {path}")
    return path


# ---------------------------------------------------------------------------
# Dispatch message (parent → peer)
# ---------------------------------------------------------------------------

DISPATCH_TEMPLATE = """---
type:        task
task_id:     {task_id}
subtask_id:  {subtask_id}
from:        {from_agent}
sent_at:     {timestamp}
---

# Task: {title}

## Context
{context}

## Instructions
{instructions}

## Expected Output
{expected_output}
"""


def cmd_dispatch(args):
    task_id = args.task_id or f"task-{gen_id()}"
    subtask_id = args.subtask_id or f"st-{gen_id()}"
    content = DISPATCH_TEMPLATE.format(
        task_id=task_id,
        subtask_id=subtask_id,
        from_agent=args.from_agent,
        title=args.title,
        timestamp=now_iso(),
        context=args.context or "",
        instructions=args.instructions or "",
        expected_output=args.expected_output or "",
    )
    out = Path(args.output) if args.output else Path(".")
    write_file(content, out, f"dispatch-{subtask_id}.md")
    print(f"  Send with: openclaw agent --agent {args.to} "
          f'--message "$(cat dispatch-{subtask_id}.md)"')


# ---------------------------------------------------------------------------
# Completion reply (peer → parent)
# ---------------------------------------------------------------------------

REPLY_DONE_TEMPLATE = """---
type:        reply
task_id:     {task_id}
subtask_id:  {subtask_id}
from:        {from_agent}
status:      done
completed_at: {timestamp}
---

## Results

{results}
"""

REPLY_FAILED_TEMPLATE = """---
type:        reply
task_id:     {task_id}
subtask_id:  {subtask_id}
from:        {from_agent}
status:      failed
completed_at: {timestamp}
---

## Error

{error}

## Partial Results

{partial_results}
"""


def cmd_reply(args):
    if args.status == "done":
        content = REPLY_DONE_TEMPLATE.format(
            task_id=args.task_id,
            subtask_id=args.subtask_id,
            from_agent=args.from_agent,
            timestamp=now_iso(),
            results=args.results or "",
        )
    else:
        content = REPLY_FAILED_TEMPLATE.format(
            task_id=args.task_id,
            subtask_id=args.subtask_id,
            from_agent=args.from_agent,
            timestamp=now_iso(),
            error=args.error or "",
            partial_results=args.partial_results or "None",
        )
    out = Path(args.output) if args.output else Path(".")
    write_file(content, out, f"reply-{args.subtask_id}.md")
    if args.to:
        print(f"  Send with: openclaw agent --agent {args.to} "
              f'--message "$(cat reply-{args.subtask_id}.md)"')


# ---------------------------------------------------------------------------
# Task file (task.md)
# ---------------------------------------------------------------------------

TASK_DIRECT_TEMPLATE = """---
task_id:      {task_id}
mode:         direct
status:       pending
from:         {from_agent}
created_at:   {timestamp}
updated_at:   {timestamp}
---

# Task: {title}

## Instructions
{instructions}

## Working Notes


## Results

"""

TASK_COORDINATING_TEMPLATE = """---
task_id:      {task_id}
mode:         coordinating
status:       planning
from:         {from_agent}
created_at:   {timestamp}
updated_at:   {timestamp}
---

# Task: {title}

## Original Instructions
{instructions}

## DAG

subtasks:
{subtask_entries}

## Subtask Results

{subtask_result_sections}

## Synthesised Output

"""


def cmd_init_task(args):
    task_id = args.task_id or f"task-{gen_id()}"
    ts = now_iso()

    if args.subtasks:
        entries = ""
        result_sections = ""
        for s in args.subtasks:
            entries += f"  {s}:\n"
            entries += f"    agent:        \n"
            entries += f"    description:  \n"
            entries += f"    depends_on:   []\n"
            entries += f"    status:       pending\n"
            result_sections += f"### {s}\n\n"

        content = TASK_COORDINATING_TEMPLATE.format(
            task_id=task_id,
            from_agent=args.from_agent or "",
            title=args.title,
            timestamp=ts,
            instructions=args.instructions or "",
            subtask_entries=entries,
            subtask_result_sections=result_sections,
        )
    else:
        content = TASK_DIRECT_TEMPLATE.format(
            task_id=task_id,
            from_agent=args.from_agent or "",
            title=args.title,
            timestamp=ts,
            instructions=args.instructions or "",
        )

    out = Path(args.output) if args.output else Path(".")
    write_file(content, out, "task.md")
    print(f"  task_id: {task_id}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate clawflow messages and task files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- dispatch ---
    p = sub.add_parser("dispatch", help="Generate a task dispatch message")
    p.add_argument("--from-agent", required=True, help="Sending agent ID (from openclaw agents list)")
    p.add_argument("--to", required=True, help="Receiving agent ID (from openclaw agents list)")
    p.add_argument("--title", required=True, help="Task title")
    p.add_argument("--task-id", default=None, help="Task ID (auto-generated if omitted)")
    p.add_argument("--subtask-id", default=None, help="Subtask ID (auto-generated if omitted)")
    p.add_argument("--context", default=None, help="Context section content")
    p.add_argument("--instructions", default=None, help="Instructions section content")
    p.add_argument("--expected-output", default=None, help="Expected output description")
    p.add_argument("--output", default=None, help="Output directory")

    # --- reply ---
    p = sub.add_parser("reply", help="Generate a completion reply")
    p.add_argument("--from-agent", required=True, help="Replying agent ID")
    p.add_argument("--to", default=None, help="Parent agent ID (for send hint)")
    p.add_argument("--task-id", required=True, help="Task ID from the dispatch message")
    p.add_argument("--subtask-id", required=True, help="Subtask ID from the dispatch message")
    p.add_argument("--status", choices=["done", "failed"], required=True)
    p.add_argument("--results", default=None, help="Results content (for done)")
    p.add_argument("--error", default=None, help="Error description (for failed)")
    p.add_argument("--partial-results", default=None, help="Partial results (for failed)")
    p.add_argument("--output", default=None, help="Output directory")

    # --- init-task ---
    p = sub.add_parser("init-task", help="Generate a task.md file")
    p.add_argument("--title", required=True, help="Task title")
    p.add_argument("--task-id", default=None, help="Task ID (match incoming message)")
    p.add_argument("--from-agent", default=None, help="Parent agent that sent this task")
    p.add_argument("--instructions", default=None, help="Instructions from the task message")
    p.add_argument("--subtasks", nargs="*", help="Subtask IDs (triggers coordinating mode)")
    p.add_argument("--output", default=None, help="Output directory")

    args = parser.parse_args()
    {"dispatch": cmd_dispatch, "reply": cmd_reply, "init-task": cmd_init_task}[args.command](args)


if __name__ == "__main__":
    main()
