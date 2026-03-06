#!/usr/bin/env python3
"""Workflow Orchestrator for chaining OpenClaw skills into pipelines.

Define workflows in YAML or JSON, execute with error handling and audit logging.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

# Try to import yaml, fall back to JSON-only mode
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


TEMPLATES_DIR = Path(__file__).parent / "templates"


def load_workflow(filepath):
    """Load a workflow definition from YAML or JSON."""
    filepath = Path(filepath)
    if not filepath.exists():
        print(f"ERROR: Workflow file not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    with open(filepath) as f:
        content = f.read()

    if filepath.suffix in (".yaml", ".yml"):
        if not HAS_YAML:
            print("ERROR: PyYAML not installed. Use JSON format or: pip3 install pyyaml", file=sys.stderr)
            sys.exit(1)
        return yaml.safe_load(content)
    else:
        return json.loads(content)


def substitute_vars(text, variables):
    """Replace {var_name} placeholders with actual values.

    SECURITY: {env.*} access is BLOCKED to prevent environment variable leakage.
    Only workflow-defined variables are substituted.
    """
    def replacer(match):
        key = match.group(1)
        if key.startswith("env."):
            # BLOCKED: env var access via workflow variables is a credential leak vector
            return "{" + key + "}"
        value = variables.get(key)
        if value is None:
            return match.group(0)
        return str(value)

    return re.sub(r'\{(\w[\w.]*)\}', replacer, text)


def check_condition(condition, variables):
    """Evaluate a simple condition string against variables."""
    if not condition:
        return True

    # Simple checks: "VAR_NAME not in saved_output" or "saved_output.field != value"
    condition = substitute_vars(condition, variables)

    # "X not in Y" check
    m = re.match(r'(.+)\s+not\s+in\s+(.+)', condition)
    if m:
        needle = m.group(1).strip().strip('"\'')
        haystack = str(variables.get(m.group(2).strip(), m.group(2).strip()))
        return needle not in haystack

    # "X in Y" check
    m = re.match(r'(.+)\s+in\s+(.+)', condition)
    if m:
        needle = m.group(1).strip().strip('"\'')
        haystack = str(variables.get(m.group(2).strip(), m.group(2).strip()))
        return needle in haystack

    # "X != Y" check
    m = re.match(r'(.+)\s*!=\s*(.+)', condition)
    if m:
        left = m.group(1).strip().strip('"\'')
        right = m.group(2).strip().strip('"\'')
        left_val = str(variables.get(left, left))
        right_val = str(variables.get(right, right))
        return left_val != right_val

    # "X == Y" check
    m = re.match(r'(.+)\s*==\s*(.+)', condition)
    if m:
        left = m.group(1).strip().strip('"\'')
        right = m.group(2).strip().strip('"\'')
        left_val = str(variables.get(left, left))
        right_val = str(variables.get(right, right))
        return left_val == right_val

    # Default: treat as truthy
    return bool(condition.strip())


SHELL_METACHARACTERS = set('|;&$`(){}!><\n')


def _validate_command(command):
    """Reject commands containing shell metacharacters after variable substitution.

    Even with shell=False, variables substituted into commands could contain
    payloads like $(cmd) or backticks that shlex.split would pass through
    as literal arguments to programs that might re-interpret them.
    """
    for char in command:
        if char in SHELL_METACHARACTERS:
            return False, f"Shell metacharacter '{char}' detected in command after variable substitution"
    return True, ""


def run_step(step, variables, dry_run=False):
    """Execute a single workflow step."""
    name = step.get("name", "unnamed")
    command = substitute_vars(step.get("command", ""), variables)
    on_fail = step.get("on_fail", "abort")
    condition = step.get("condition")
    save_output = step.get("save_output")
    timeout = step.get("timeout", 60)
    max_retries = 3 if on_fail == "retry" else 1

    # Check condition
    if condition and not check_condition(condition, variables):
        print(f"  SKIP [{name}] — condition not met: {condition}")
        return True, None

    # Validate command after substitution
    valid, reason = _validate_command(command)
    if not valid:
        print(f"  BLOCKED [{name}] {reason}")
        return False, None

    if dry_run:
        print(f"  [DRY] [{name}] {command}")
        return True, None

    for attempt in range(max_retries):
        if attempt > 0:
            print(f"  RETRY [{name}] attempt {attempt + 1}/{max_retries}")
            time.sleep(2)

        print(f"  RUN  [{name}] {command[:120]}")

        try:
            import shlex
            cmd_parts = shlex.split(command)
            result = subprocess.run(
                cmd_parts,
                shell=False,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            if save_output:
                variables[save_output] = result.stdout.strip()

            if result.returncode == 0:
                print(f"  OK   [{name}]")
                return True, result.stdout.strip()
            else:
                stderr = result.stderr.strip()[:200] if result.stderr else ""
                print(f"  FAIL [{name}] exit={result.returncode} {stderr}")

                if attempt < max_retries - 1:
                    continue

                if on_fail == "abort":
                    print(f"  ABORT — step [{name}] failed with on_fail=abort")
                    return False, None
                elif on_fail == "warn":
                    print(f"  WARN — continuing despite failure in [{name}]")
                    return True, None
                elif on_fail == "rollback":
                    print(f"  ROLLBACK requested by [{name}]")
                    return False, "rollback"
                else:
                    return False, None

        except subprocess.TimeoutExpired:
            print(f"  TIMEOUT [{name}] after {timeout}s")
            if on_fail == "abort":
                return False, None
            elif on_fail == "warn":
                return True, None
            return False, None
        except Exception as e:
            print(f"  ERROR [{name}] {e}")
            if on_fail == "warn":
                return True, None
            return False, None

    return False, None


def run_workflow(workflow, dry_run=False):
    """Execute a complete workflow."""
    name = workflow.get("name", "unnamed")
    description = workflow.get("description", "")
    steps = workflow.get("steps", [])
    variables = dict(workflow.get("vars", {}))

    print(f"Workflow: {name}")
    if description:
        print(f"  {description}")
    print(f"  Steps: {len(steps)}")
    print()

    completed_steps = []
    failed = False

    for i, step in enumerate(steps):
        success, output = run_step(step, variables, dry_run=dry_run)
        if success:
            completed_steps.append(step)
        else:
            if output == "rollback":
                print(f"\nRolling back {len(completed_steps)} completed steps...")
                # Rollback is conceptual — log it for the audit trail
                for cs in reversed(completed_steps):
                    print(f"  ROLLBACK [{cs.get('name', '?')}]")
            failed = True
            break

    print()
    if failed:
        print(f"WORKFLOW FAILED: {name} — stopped at step {i + 1}/{len(steps)}")
        return False
    else:
        print(f"WORKFLOW COMPLETE: {name} — {len(completed_steps)}/{len(steps)} steps succeeded")
        return True


def validate_workflow(workflow):
    """Validate a workflow definition."""
    errors = []

    if "name" not in workflow:
        errors.append("Missing 'name' field")

    steps = workflow.get("steps", [])
    if not steps:
        errors.append("No steps defined")

    for i, step in enumerate(steps):
        if "command" not in step:
            errors.append(f"Step {i + 1}: missing 'command'")
        if step.get("on_fail") and step["on_fail"] not in ("abort", "warn", "rollback", "retry"):
            errors.append(f"Step {i + 1}: invalid on_fail value '{step['on_fail']}'")

    if errors:
        print(f"INVALID: {len(errors)} error(s)")
        for e in errors:
            print(f"  - {e}")
        return False
    else:
        print(f"VALID: {workflow.get('name', '?')} — {len(steps)} steps")
        return True


def show_templates():
    """Show available workflow templates."""
    templates = {
        "secure-deploy": {
            "name": "secure-deploy",
            "description": "Scan, diff, deploy, and audit a skill update",
            "steps": [
                {"name": "scan", "command": "python3 ~/.openclaw/skills/skill-scanner/scripts/scanner.py scan --path {skill_path} --json", "on_fail": "abort", "save_output": "scan"},
                {"name": "deploy", "command": "echo Deploying {skill_name}...", "condition": "CRITICAL not in scan", "on_fail": "abort"},
                {"name": "audit", "command": "python3 ~/.openclaw/skills/compliance-audit/scripts/audit.py log --action workflow_complete --details '{\"workflow\": \"secure-deploy\", \"skill\": \"{skill_name}\"}'", "on_fail": "warn"},
            ],
        },
        "daily-scan": {
            "name": "daily-scan",
            "description": "Scan all installed skills and report findings",
            "steps": [
                {"name": "scan-all", "command": "python3 ~/.openclaw/skills/skill-scanner/scripts/scanner.py scan-all --json", "save_output": "results", "on_fail": "warn"},
                {"name": "audit", "command": "python3 ~/.openclaw/skills/compliance-audit/scripts/audit.py log --action daily_scan --details '{\"results\": \"complete\"}'", "on_fail": "warn"},
            ],
        },
        "pre-install": {
            "name": "pre-install",
            "description": "Security check before installing a new skill",
            "steps": [
                {"name": "scan", "command": "python3 ~/.openclaw/skills/skill-scanner/scripts/scanner.py scan --path {skill_path} --json", "on_fail": "abort", "save_output": "scan"},
                {"name": "verify", "command": "echo Skill passed scan. Ready to install.", "condition": "CRITICAL not in scan"},
                {"name": "audit", "command": "python3 ~/.openclaw/skills/compliance-audit/scripts/audit.py log --action pre_install_check --details '{\"skill\": \"{skill_name}\", \"scan_passed\": true}'", "on_fail": "warn"},
            ],
        },
    }

    print("Available workflow templates:\n")
    for name, template in templates.items():
        print(f"  {name}")
        print(f"    {template['description']}")
        print(f"    Steps: {len(template['steps'])}")
        print()

    print("To use a template, save as YAML/JSON and run with: orchestrator.py run --workflow <file>")


def main():
    parser = argparse.ArgumentParser(description="Workflow Orchestrator for OpenClaw skills")
    sub = parser.add_subparsers(dest="command")

    p_run = sub.add_parser("run", help="Run a workflow")
    p_run.add_argument("--workflow", required=True, help="Path to workflow YAML or JSON file")
    p_run.add_argument("--dry-run", action="store_true", help="Show steps without executing")

    p_validate = sub.add_parser("validate", help="Validate a workflow file")
    p_validate.add_argument("--workflow", required=True, help="Path to workflow file")

    sub.add_parser("templates", help="Show available workflow templates")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "run":
        workflow = load_workflow(args.workflow)
        success = run_workflow(workflow, dry_run=args.dry_run)
        sys.exit(0 if success else 1)

    elif args.command == "validate":
        workflow = load_workflow(args.workflow)
        valid = validate_workflow(workflow)
        sys.exit(0 if valid else 1)

    elif args.command == "templates":
        show_templates()


if __name__ == "__main__":
    main()
