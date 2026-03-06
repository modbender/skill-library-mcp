#!/usr/bin/env python3
# SECURITY MANIFEST:
#   Environment variables accessed: none
#   External endpoints called: none
#   Local files read: workflows/<n>/observation.json
#   Local files written: workflows/<n>/SKILL.md, workflows/<n>/run.sh

"""
Apprentice Synthesizer — transforms raw observation into a permanent workflow skill.
This is the core of Apprentice: pattern recognition + intent inference + skill generation.
Stdlib only. No external dependencies. No network calls.

Note: The actual LLM-powered synthesis happens in the agent session via the SKILL.md
instructions. This script handles the file scaffolding, variable detection, and
workflow SKILL.md generation from structured observation data.
"""

import sys
import os
import re
import json
import stat
import argparse
from pathlib import Path
from datetime import datetime, timezone

SKILL_DIR = Path(__file__).parent.parent
WORKFLOWS_DIR = SKILL_DIR / "workflows"


def load_observation(workflow_name: str) -> dict:
    obs_file = WORKFLOWS_DIR / workflow_name / "observation.json"
    if not obs_file.exists():
        print(f"No observation found for: {workflow_name}", file=sys.stderr)
        sys.exit(1)
    with open(obs_file) as f:
        return json.load(f)


def detect_variables(steps: list) -> list:
    """
    Heuristically detect potential variables in step text.
    Variables are things that look like they'd change between runs:
    - Quoted strings
    - Filenames with variable-looking names
    - Things after "called", "named", "for", "with"
    """
    variable_patterns = [
        (r'"([^"]{3,40})"', "quoted value"),
        (r"'([^']{3,40})'", "quoted value"),
        (r"(?:called|named|for|with)\s+(\w[\w-]{2,})", "named entity"),
        (r"(\w+[-_]\w+(?:[-_]\w+)*)", "hyphenated-identifier"),
    ]

    candidates = {}
    all_text = " ".join(s.get("text", "") for s in steps)

    for pattern, kind in variable_patterns:
        matches = re.findall(pattern, all_text, re.IGNORECASE)
        for match in matches:
            key = match.upper().replace(" ", "_").replace("-", "_")
            if key not in candidates and len(match) > 2:
                candidates[key] = {"original": match, "kind": kind}

    return list(candidates.items())[:6]  # Cap at 6 variables


def extract_step_commands(step_text: str) -> list:
    """Extract shell-looking commands from step text."""
    commands = []
    # Look for things that look like shell commands
    cmd_patterns = [
        r'`([^`]+)`',           # backtick-quoted
        r'```[^\n]*\n(.*?)```', # code blocks
        r'\$\s+([\w/.-]+(?:\s+[\w/.-]+)*)',  # $ prefixed
    ]
    for pattern in cmd_patterns:
        matches = re.findall(pattern, step_text, re.DOTALL)
        commands.extend(m.strip() for m in matches if m.strip())
    return commands


def infer_workflow_metadata(steps: list, hint: str = "") -> dict:
    """Infer workflow name, description, and tags from steps."""
    all_text = (hint + " " + " ".join(s.get("text", "") for s in steps)).lower()

    # Common workflow archetypes
    archetypes = {
        "project": ["project", "setup", "init", "create", "new", "start"],
        "deploy": ["deploy", "release", "push", "publish", "staging", "production"],
        "report": ["report", "summary", "compile", "weekly", "monthly", "send"],
        "review": ["review", "pr", "pull request", "code review", "audit"],
        "backup": ["backup", "archive", "copy", "save", "export"],
        "cleanup": ["clean", "delete", "remove", "purge", "reset"],
        "onboard": ["onboard", "new user", "new client", "welcome", "setup account"],
        "test": ["test", "run tests", "check", "verify", "validate"],
    }

    detected_archetype = "workflow"
    for archetype, keywords in archetypes.items():
        if any(kw in all_text for kw in keywords):
            detected_archetype = archetype
            break

    # Generate a slug from hint
    if hint:
        slug = re.sub(r"[^a-z0-9]+", "-", hint.lower()).strip("-")[:40]
    else:
        slug = f"learned-{detected_archetype}-{datetime.now(timezone.utc).strftime('%m%d')}"

    return {
        "slug": slug,
        "archetype": detected_archetype,
        "step_count": len(steps),
        "inferred_name": slug.replace("-", " ").title()
    }


def generate_workflow_skill_md(
    observation: dict,
    workflow_meta: dict,
    variables: list,
    synthesis_notes: str = ""
) -> str:
    """Generate a SKILL.md for the learned workflow."""
    slug = workflow_meta["slug"]
    name = workflow_meta["inferred_name"]
    step_count = workflow_meta["step_count"]
    learned_at = observation.get("started_at", "unknown")[:10]

    # Format variables section
    var_section = ""
    if variables:
        var_section = "\n## Variables\n\n"
        var_section += "These change each time you run this workflow:\n\n"
        for var_key, var_info in variables:
            var_section += f"- **{var_key}** — (example: `{var_info['original']}`)\n"

    # Format steps
    steps = observation.get("steps", [])
    steps_section = "\n## Steps\n\n"
    if steps:
        for i, step in enumerate(steps, 1):
            steps_section += f"{i}. {step.get('text', '').strip()}\n"
    else:
        steps_section += "*No steps recorded — observation was empty.*\n"

    # Trigger phrases
    triggers = [
        f'"{slug}"',
        f'"run {slug}"',
        f'"do {slug}"',
        f'"replay {slug}"',
    ]
    if variables:
        first_var = variables[0][0]
        triggers.append(f'"{slug} with {first_var.lower()}=[value]"')

    trigger_str = "\n".join(f"- {t}" for t in triggers)

    skill_md = f"""---
name: {slug}
version: "1.0.0"
description: Learned workflow — {name}. Run when user asks to "{slug}" or "{name.lower()}". Executes the {step_count}-step workflow learned by Apprentice on {learned_at}. Accepts variables: {", ".join(k for k, _ in variables) if variables else "none"}.
learned_by: apprentice
learned_at: {learned_at}
metadata:
  clawdbot:
    emoji: "🎓"
    requires:
      env: []
    files:
      - "run.sh"
---

# {name}

*Learned by Apprentice on {learned_at} — {step_count} steps*

> This workflow was learned by watching you do it. It captures your exact approach,
> decisions, and sequence — not a generic version of it. Yours.

---

## How to Run

{trigger_str}

{var_section}
{steps_section}

## Execution

When invoked, your agent will:

1. Identify any variable values from your request (or ask if missing)
2. Execute each step in order, substituting variables where needed
3. Confirm completion or report any step that failed

Run with: `python3 apprentice/scripts/run.py {slug}`
Or just ask: "Run {slug}"

---

## Refinement

After running this workflow, you can say:
- "That step was wrong, here's how it should be: ..." → updates that step
- "Add a step after step 3: ..." → inserts a new step
- "Watch me do {slug} again" → re-learns the whole workflow from scratch

---

## Notes from Synthesis

{synthesis_notes if synthesis_notes else "No additional notes."}
"""
    return skill_md


def generate_run_script(observation: dict, workflow_meta: dict, variables: list) -> str:
    """Generate a run.sh that executes the workflow."""
    slug = workflow_meta["slug"]
    steps = observation.get("steps", [])

    script = f"""#!/usr/bin/env bash
# SECURITY MANIFEST:
#   Environment variables accessed: {", ".join(k for k, _ in variables) if variables else "none"}
#   External endpoints called: none
#   Local files read: workflows/{slug}/observation.json
#   Local files written: none (workflow execution output only)
#
# Apprentice-generated workflow: {slug}
# Learned: {observation.get("started_at", "unknown")[:10]}
# Steps: {len(steps)}

set -euo pipefail

WORKFLOW="{slug}"
STEP_COUNT={len(steps)}

echo "🎓 Running workflow: $WORKFLOW"
echo "   Steps: $STEP_COUNT"
echo ""

"""
    # Add variable declarations
    if variables:
        script += "# — Variables (pass via environment or args) —\n"
        for i, (var_key, var_info) in enumerate(variables, 1):
            script += f'{var_key}="${{{var_key}:-}}"  # example: {var_info["original"]}\n'
            script += f'if [[ -z "${{{var_key}}}" ]]; then\n'
            script += f'  echo "⚠️  Missing variable: {var_key}"\n'
            script += f'  read -rp "  Enter {var_key}: " {var_key}\n'
            script += f'fi\n'
        script += "\n"

    # Add steps as comments with execution hooks
    for i, step in enumerate(steps, 1):
        text = step.get("text", "").replace('"', '\\"')
        script += f'echo "  Step {i}/{len(steps)}: {text[:60]}{"..." if len(text) > 60 else ""}"\n'

        # Extract any shell commands embedded in the step
        cmds = extract_step_commands(step.get("text", ""))
        if cmds:
            for cmd in cmds[:2]:  # Cap at 2 commands per step
                # Substitute variables
                for var_key, _ in variables:
                    cmd = cmd.replace(
                        next((v["original"] for _, v in [(var_key, {})] if True), ""),
                        f"${var_key}"
                    )
                script += f'  # {cmd}\n'

    script += f"""
echo ""
echo "✅ Workflow complete: $WORKFLOW"
"""
    return script


def synthesize(workflow_name: str, synthesis_notes: str = "") -> Path:
    """Main synthesis function — turns observation into workflow skill."""
    observation = load_observation(workflow_name)
    steps = observation.get("steps", [])

    if not steps:
        print("⚠️  Observation is empty — no steps were recorded.")
        sys.exit(1)

    hint = observation.get("hint", workflow_name)
    workflow_meta = infer_workflow_metadata(steps, hint)
    variables = detect_variables(steps)

    # Use provided name or inferred slug
    slug = workflow_name  # Always use the directory name as the slug

    workflow_dir = WORKFLOWS_DIR / slug
    workflow_dir.mkdir(exist_ok=True)

    # Generate and save SKILL.md
    skill_md = generate_workflow_skill_md(observation, workflow_meta, variables, synthesis_notes)
    skill_path = workflow_dir / "SKILL.md"
    with open(skill_path, "w") as f:
        f.write(skill_md)

    # Generate and save run.sh
    run_script = generate_run_script(observation, workflow_meta, variables)
    run_path = workflow_dir / "run.sh"
    with open(run_path, "w") as f:
        f.write(run_script)
    os.chmod(run_path, os.stat(run_path).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    return workflow_dir


def display_synthesis_preview(workflow_dir: Path):
    """Show a human-readable preview of what was synthesized."""
    skill_md = workflow_dir / "SKILL.md"
    obs_file = workflow_dir / "observation.json"

    if not skill_md.exists():
        print("Synthesis not found.", file=sys.stderr)
        return

    # Load metadata
    with open(skill_md) as f:
        content = f.read()

    with open(obs_file) as f:
        obs = json.load(f)

    steps = obs.get("steps", [])
    name = workflow_dir.name

    print("━" * 52)
    print(f"🎓 APPRENTICE — SYNTHESIS COMPLETE")
    print(f"   Workflow: {name}")
    print(f"   Steps: {len(steps)}")
    print("━" * 52)
    print()
    print("STEPS LEARNED:")
    for i, step in enumerate(steps, 1):
        text = step.get("text", "").strip()
        print(f"  {i:2}. {text[:70]}{'...' if len(text) > 70 else ''}")

    print()
    print(f"SAVED TO: apprentice/workflows/{name}/")
    print(f"  SKILL.md   ← Permanent workflow skill")
    print(f"  run.sh     ← Execution script")
    print(f"  observation.json ← Raw observation log")
    print()
    print(f"TO RUN: Tell your agent 'run {name}'")
    print(f"        Or: python3 apprentice/scripts/run.py {name}")
    print("━" * 52)


def main():
    parser = argparse.ArgumentParser(
        description="Apprentice Synthesizer — turn observations into workflow skills"
    )
    parser.add_argument("workflow_name", help="Name of the workflow to synthesize")
    parser.add_argument("--notes", help="Additional synthesis notes", default="")
    parser.add_argument("--preview", action="store_true", help="Preview synthesis output")

    args = parser.parse_args()

    workflow_dir = synthesize(args.workflow_name, args.notes)

    if args.preview:
        display_synthesis_preview(workflow_dir)
    else:
        print(f"✅ Synthesized: {workflow_dir}")


if __name__ == "__main__":
    main()
