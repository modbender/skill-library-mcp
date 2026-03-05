---
name: truth-first
description: Evidence-first verification for status, config, file contents, actions, connectivity, mounts, and model selection. Use before answering any such claim.
---

# Truth First

## Core Rule

Require evidence before answering. Do not rely on memory or assumptions for claims about system state, files, configs, execution, connectivity, mounts, or model selection.

## Response Framework (Strict)

1. List claims to verify.
2. For each claim, gather evidence using tools (read/status/rg/logs).
3. Classify each claim as `Verified`, `Inferred`, or `Unknown`.
4. For each `Unknown`, provide the next-step command(s) needed.
5. Always cite evidence (paths, key lines, or command outputs).

## Workflow

1. Parse the user request and extract every factual claim that would change your response.
2. Decide the minimum set of checks needed to verify each claim.
3. Run evidence commands or open files. Prefer direct sources over indirect signals.
4. Summarize findings with classifications and evidence citations.
5. Only then provide the answer or recommended next steps.

## Evidence Standards

- Prefer primary evidence: files, logs, command outputs, or tool responses.
- Use `rg` for targeted searches and `ls`/`stat` for existence and timestamps.
- When a claim could be true but is not verified, mark it `Inferred` and state why.
- Never upgrade an `Unknown` to `Verified` without direct evidence.
- If evidence cannot be gathered (missing tools, permissions, or files), state the limitation and stop short of a definitive answer.

## Common Claim Types

- Status: service running, gateway connected, connectivity, mount status, disk usage.
- Configuration: values in config files or environment variables.
- File contents: presence, specific lines, or recent modifications.
- Actions: whether a command ran, tests passed, or a file was edited.
- Model selection: which model is configured or currently in use.

## References

- Use `references/patterns.md` for reusable templates and evidence commands.
