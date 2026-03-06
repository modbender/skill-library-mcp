---
name: ci-whisperer
description: "Analyze GitHub Actions failures and propose fixes. Use when a user shares a failing GitHub Actions run URL/id, says 'CI is failing', asks 'why did this workflow fail', wants logs summarized, wants the minimal fix, or wants an automated PR to address the failure. Uses the GitHub CLI (`gh`) and GitHub API to fetch run metadata/logs safely and produce a concise root-cause + next steps report."
---

# CI Whisperer

Fetch GitHub Actions run details, pinpoint the failure, and propose a minimal fix.

This skill is meant to feel like a senior engineer doing a fast “CI autopsy”.

## Modes

### Read-only mode (default)
- Collect evidence, explain root cause, propose fixes.
- **No pushes, no PRs, no branch creation.**

### PR fix mode (opt-in)
PR fix mode is allowed only when **both** are true:
1) The user explicitly asks to open a PR.
2) A local toggle is enabled (the “on/off button”):
   - env var: `CI_WHISPERER_WRITE=1`

If the toggle is not enabled, refuse politely and explain how to enable it.

## Workflow

### 1) Identify target run
Accept any of:
- workflow run URL
- run id
- PR number (then locate latest run)

Always determine:
- `owner/repo`
- run id

If the user didn’t specify the repo, ask for it (or infer from context).

### 2) Gather evidence (tool-backed)
Prefer deterministic tooling. Use `/usr/bin/gh` when the system has multiple `gh` binaries.

Suggested commands:
- `gh run view <run-id> --repo owner/repo --json status,conclusion,createdAt,updatedAt,event,headBranch,headSha,url,name`
- `gh run view <run-id> --repo owner/repo --log-failed`
- `gh run view <run-id> --repo owner/repo --log` (only if needed; can be noisy)

If `gh` is not authenticated, stop and ask the user to run:
- `/usr/bin/gh auth login`

### 3) Produce a "CI Autopsy" report
Return:
- failing job(s) and step(s)
- the exact error excerpt (short; redact secrets)
- likely root cause(s) ranked
- minimal fix options
- confidence level

### 4) (Optional) Open a PR (only with explicit approval + write toggle)
If the user asks to fix it and `CI_WHISPERER_WRITE=1`:
- create a branch
- apply minimal changes
- run local lint/tests if available
- open PR with a clear description and link to the failing run

If the user asks but write mode is OFF:
- provide the patch/diff instructions, but do not push.

## Safety
- Never print tokens.
- Don’t open PRs or push changes unless explicitly requested.
- If logs contain secrets, redact before quoting.

## Bundled scripts
Use scripts for repeatable fetching and parsing:
- `scripts/ci_autopsy.py` (fetch run metadata + failed logs)
