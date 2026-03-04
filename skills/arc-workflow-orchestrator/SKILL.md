---
name: workflow-orchestrator
description: Chain skills into automated pipelines with conditional logic, error handling, and audit logging. Define workflows in YAML or JSON, then execute them hands-free. Perfect for security-gated deployments, scheduled maintenance, and multi-step agent operations.
user-invocable: true
metadata: {"openclaw": {"emoji": "🔗", "os": ["darwin", "linux"], "requires": {"bins": ["python3"]}}}
---

# Workflow Orchestrator

Chain skills into automated pipelines. Define a sequence of steps, and the orchestrator runs them in order with conditional logic, error handling, and optional audit logging.

## Why This Exists

Agents run multiple skills but manually. Scan a skill, diff against the previous version, deploy if safe, log the result. That's 4 steps, 4 commands, and one missed step means a gap in your process. Workflows automate the sequence and ensure nothing gets skipped.

## Commands

### Run a workflow from a YAML file
```bash
python3 {baseDir}/scripts/orchestrator.py run --workflow workflow.yaml
```

### Run a workflow from JSON
```bash
python3 {baseDir}/scripts/orchestrator.py run --workflow workflow.json
```

### Dry run (show steps without executing)
```bash
python3 {baseDir}/scripts/orchestrator.py run --workflow workflow.yaml --dry-run
```

### List available workflow templates
```bash
python3 {baseDir}/scripts/orchestrator.py templates
```

### Validate a workflow file
```bash
python3 {baseDir}/scripts/orchestrator.py validate --workflow workflow.yaml
```

## Workflow Format (YAML)

```yaml
name: secure-deploy
description: Scan, diff, deploy, and audit a skill update
steps:
  - name: scan
    command: python3 ~/.openclaw/skills/skill-scanner/scripts/scanner.py scan --path {skill_path} --json
    on_fail: abort
    save_output: scan_result

  - name: diff
    command: python3 ~/.openclaw/skills/skill-differ/scripts/differ.py diff {skill_path} {previous_path}
    on_fail: warn

  - name: deploy
    command: python3 ~/.openclaw/skills/skill-gitops/scripts/gitops.py deploy {skill_path}
    condition: scan_result.verdict != "CRITICAL"
    on_fail: rollback

  - name: audit
    command: python3 ~/.openclaw/skills/compliance-audit/scripts/audit.py log --action "skill_deployed" --details '{"skill": "{skill_name}", "scan": "{scan_result.verdict}"}'
    on_fail: warn
```

## Step Options

- **name** — Human-readable step name
- **command** — Shell command to execute (supports variable substitution)
- **on_fail** — What to do if the step fails: `abort` (stop workflow), `warn` (log and continue), `rollback` (undo previous steps), `retry` (retry up to 3 times)
- **condition** — Optional condition to check before running (references saved outputs)
- **save_output** — Save stdout to a named variable for use in later steps
- **timeout** — Max seconds to wait (default: 60)

## Variable Substitution

Use `{variable_name}` in commands to reference:
- Workflow-level variables defined in the `vars` section
- Saved outputs from previous steps
- Environment variables with `{env.VAR_NAME}`

## Built-in Templates

The orchestrator ships with these workflow templates:

1. **secure-deploy** — Scan → Diff → Deploy → Audit
2. **daily-scan** — Scan all installed skills, report findings
3. **pre-install** — Scan → Typosquat check → Install → Audit

## Example: Secure Deploy Pipeline

```yaml
name: secure-deploy
vars:
  skill_path: ~/.openclaw/skills/my-skill
  skill_name: my-skill
steps:
  - name: security-scan
    command: python3 ~/.openclaw/skills/skill-scanner/scripts/scanner.py scan --path {skill_path} --json
    save_output: scan
    on_fail: abort
  - name: deploy
    command: echo "Deploying {skill_name}..."
    condition: "CRITICAL not in scan"
    on_fail: abort
  - name: log
    command: python3 ~/.openclaw/skills/compliance-audit/scripts/audit.py log --action workflow_complete --details '{"workflow": "secure-deploy", "skill": "{skill_name}"}'
```

## Tips

- Start with `--dry-run` to verify your workflow before executing
- Use `on_fail: abort` for security-critical steps
- Chain with the compliance audit skill for full traceability
- Keep workflows in version control for reproducibility
