---
name: openclaw-shield-quickscan
description: "Run a fast OpenClaw Shield scan and summarize actionable findings. Use when users ask to scan a folder or repository for credential theft, data exfiltration patterns, suspicious command execution, risky network behavior, or a quick security triage report."
---

# OpenClaw Shield Quick Scan

Use this skill to run a fast scan and produce a short triage summary.

## Inputs

- `target_path` (required): folder or file to scan.
- `scanner_path` (optional): defaults to `projects/OpenClaw-Shield/src/scanner.py`.
- `output_path` (optional): defaults to `/tmp/openclaw-shield-report.json`.

## Workflow

1. Verify `target_path` exists.
2. Verify `scanner_path` exists. If missing, ask user to install OpenClaw Shield.
3. Run the scanner.
4. Summarize the report with `scripts/summarize_report.py`.
5. Return severity counts, top findings, and next actions.

## Commands

```bash
python3 "projects/OpenClaw-Shield/src/scanner.py" "<target_path>" --output "/tmp/openclaw-shield-report.json"
python3 scripts/summarize_report.py "/tmp/openclaw-shield-report.json"
```

If the scanner is not installed:

```bash
clawhub install openclaw-shield
```

## Response Contract

- Always include total findings and severity breakdown.
- If there are findings, include up to 5 highest-severity items with file path and line.
- If no findings exist, clearly state scan completed with no detected issues.
- Keep output concise and actionable.
