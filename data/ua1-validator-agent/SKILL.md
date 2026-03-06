---
name: ua1-validator-agent
description: Validate PDFs against PDF/UA-1 using ua1.dev or api.ua1.dev from AI coding agents (OpenClaw, Claude Code, Codex, OpenCode). Use when an agent needs deterministic accessibility checks, compact machine-readable verdicts, CI gating, or structured remediation loops for PDF files.
---

# UA1 Validator Agent Skill

Use this skill to run deterministic PDF/UA-1 checks from an agent workflow.

## Endpoints

- Health: `GET https://api.ua1.dev/api/health`
- Validate: `POST https://api.ua1.dev/api/validate`
- Compact mode: `POST https://api.ua1.dev/api/validate?format=compact`
- Metrics: `GET https://api.ua1.dev/api/metrics`

## Required contract

Send multipart form-data with field name `file`.

- Accepted: `.pdf`
- Typical outcomes:
  - `200` validation response
  - `415` unsupported type
  - `413` file too large
  - `429` rate-limited

## Minimal workflow for agents

1. Run health check once before batch validation.
2. Validate each PDF using compact mode for deterministic parsing.
3. If verdict is `fail`, capture findings and group by `rule_id`.
4. Produce remediation plan sorted by rule frequency.
5. Re-run validation after fixes and compare counts.

## Use script

Run:

```bash
bash scripts/validate_pdf.sh /absolute/or/relative/path/to/file.pdf
```

Optional env:

- `UA1_API_BASE` (default: `https://api.ua1.dev`)
- `UA1_FORMAT` (`compact` by default; set `full` for full payload)

## CI gate pattern

Treat non-pass verdict as a failed quality gate.

- Exit `0` only when verdict is `pass`
- Exit `2` when verdict is `fail`
- Exit `1` for transport/API errors

Use the script’s exit codes directly in pipelines.
