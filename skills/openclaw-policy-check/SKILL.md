---
name: openclaw-policy-check
description: "Scan repositories for risky security patterns before execution. Use when users ask for a quick preflight security check, policy enforcement scan, suspicious code triage, or detection of unsafe commands, secret leakage, and dangerous shell behavior."
---

# OpenClaw Policy Check

Run a lightweight policy scan to catch common high-risk patterns in code and scripts.

## Inputs

- `target_path` (required): file or directory to scan.
- `fail_on` (optional): severity threshold for non-zero exit. One of `critical`, `high`, `medium`, `low`.
- `json_output` (optional): print raw JSON output.

## Workflow

1. Run `scripts/policy_check.py` on the target path.
2. Review severity counts and top findings.
3. If findings exist, prioritize `critical` and `high` items first.
4. Suggest concrete fixes for each flagged pattern.

## Commands

```bash
python3 scripts/policy_check.py "<target_path>"
python3 scripts/policy_check.py "<target_path>" --json
python3 scripts/policy_check.py "<target_path>" --fail-on high
```

## Response Contract

- Always include total findings and severity breakdown.
- Include top findings with `file:line`, rule id, and reason.
- If no findings exist, explicitly state that no policy violations were detected.
- Keep remediation guidance concrete and brief.
