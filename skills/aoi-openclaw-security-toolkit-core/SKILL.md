---
name: aoi-openclaw-security-toolkit-core
description: "Fail-closed OpenClaw security toolkit (public-safe). Use to
  prevent accidental or unexpected data leakage by running local-only checks:
  default-deny allowlists, lightweight secret/token scans, egress-risk pattern
  scans, and prompt/document injection pattern scans. Use when preparing
  GitHub/ClawHub publishing, reviewing skills/scripts for risky behavior, or
  validating inbound text/doc content before tool execution."
---


# AOI OpenClaw Security Toolkit (Core)

**Why**: Prevent “one bad commit” incidents (accidental file leakage + secret exposure) with a fast, local-only, fail-closed check.
**When**: Before committing/pushing, before publishing a skill, and when reviewing scripts/skills for unexpected egress behavior.
**How**: Run a single command to get PASS/WARN/BLOCK and an optional redaction-safe report.
**Scope**: Detection + reporting only (no auto-fix, no uploads, no auto-posting).
**Quickstart**: `openclaw-sec check --preset repo --diff staged`

This is a **public-safe** toolkit skill.

- **Does:** detect + report risks (PASS/WARN/BLOCK)
- **Does NOT:** auto-fix, auto-upload, auto-post, or exfiltrate data

## CLI

Binary: `openclaw-sec`

Common:

```bash
openclaw-sec check --lang en
openclaw-sec check --lang ko
openclaw-sec scan-secrets
openclaw-sec scan-egress
openclaw-sec scan-prompt --file inbound.txt
```

Exit codes:
- `0` PASS
- `1` WARN
- `2` BLOCK

## Default scan scope

If `--paths` is omitted, it scans existing paths among:
- `.`
- `skills/`
- `scripts/`
- `context/`

## Rules

Rule files live in `rules/`:
- `secret_patterns.txt`
- `egress_patterns.txt`
- `prompt_injection_patterns.txt`

Edit these to tune sensitivity.
