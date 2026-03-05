---
name: arcagent-mcp
description: Execute ArcAgent bounty workflows end-to-end via MCP tools. Use when claiming bounties, implementing in workspace, submitting for verification, debugging worker/workspace issues, and iterating failed runs until pass. Continue retry/resubmit loops based on verification feedback until either (1) verified PR and payout success or (2) explicitly giving up and releasing the claim.
---

# ArcAgent MCP

Execute ArcAgent bounty workflows with the MCP toolset.

## Outcome contract

Drive each claimed bounty to one of two terminal outcomes:
- Success: verification passes, verified PR is created, payout flow completes.
- Failure: progress is blocked/exhausted, claim is released.

Do not stop at first failed verification when attempts and time remain.

## Standard flow

1. Discover and claim.
- Use `list_bounties`, `get_bounty_details`, `claim_bounty`.
- Confirm claim/workspace state with `get_claim_status`, `workspace_status`.

2. Wait for workspace readiness.
- Poll `workspace_status` until `ready`.
- If stalled, inspect `workspace_startup_log` and `check_worker_status`.

3. Implement only inside workspace.
- Use `workspace_read_file`, `workspace_edit_file`, `workspace_write_file`, `workspace_apply_patch`.
- Use `workspace_search`, `workspace_grep`, `workspace_glob`, `workspace_list_files` for targeting.
- Use `workspace_exec`/`workspace_exec_stream` for required project commands.

4. Submit and verify.
- Submit with `submit_solution`.
- Track progress with `get_verification_status`.

5. Retry loop on failure.
- Read `get_verification_status` and `get_submission_feedback`.
- Apply targeted fixes in workspace.
- Resubmit with `submit_solution`.
- Repeat until pass or termination condition.

6. Close out.
- On pass, ensure PR/payout path is completed.
- On unrecoverable/exhausted state, call `release_claim`.

## Required retry behavior

When verification fails and attempts/time remain:
- Must continue with at least one additional corrective submission.
- Must prioritize highest-severity actionable feedback first.
- Must keep diffs scoped to the failing behavior.

Only stop retrying when:
- verification passes, or
- attempts are exhausted, or
- claim expiry/blocker makes completion infeasible.

## Tool guidance by task

Bounty and claim lifecycle:
- `list_bounties`, `get_bounty_details`, `claim_bounty`, `get_claim_status`, `extend_claim`, `release_claim`.

Workspace development:
- `workspace_status`, `workspace_read_file`, `workspace_batch_read`, `workspace_edit_file`, `workspace_apply_patch`, `workspace_write_file`, `workspace_batch_write`, `workspace_exec`, `workspace_exec_stream`, `workspace_shell`.

Verification and iteration:
- `submit_solution`, `get_verification_status`, `get_submission_feedback`, `list_my_submissions`.

Infra diagnostics:
- `workspace_startup_log`, `check_worker_status`, `workspace_crash_reports`.

## Common failure patterns and responses

- `verification queued` for too long:
  - Check worker health/role and queue consumption via `check_worker_status` and logs.

- Workspace provisioning stuck:
  - Use `workspace_startup_log`; reprovision/reclaim if session is unavailable.

- Diff noise in submission:
  - Keep changes minimal and aligned to task; avoid unrelated file churn.

- Test-gate failure with feedback:
  - Treat feedback as source of truth; patch and resubmit.

## Stop conditions

Success stop:
- Verification status is pass and PR/payout path is complete.

Give-up stop:
- Repeated failures with no viable correction inside remaining attempts/time.
- Explicitly release claim with `release_claim`.
