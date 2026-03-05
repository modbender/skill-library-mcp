---
name: cyber-security-engineer
description: Security engineering workflow for OpenClaw privilege governance and hardening. Use for least-privilege execution, approval-first privileged actions, idle timeout controls, port + egress monitoring, and ISO 27001/NIST-aligned compliance reporting with mitigations.
---

# Cyber Security Engineer

## Requirements

**Env vars (optional, but documented):**
- `OPENCLAW_REQUIRE_POLICY_FILES`
- `OPENCLAW_REQUIRE_SESSION_ID`
- `OPENCLAW_TASK_SESSION_ID`
- `OPENCLAW_APPROVAL_TOKEN`
- `OPENCLAW_UNTRUSTED_SOURCE`
- `OPENCLAW_VIOLATION_NOTIFY_CMD`
- `OPENCLAW_VIOLATION_NOTIFY_ALLOWLIST`

**Tools:** `python3` and one of `lsof`, `ss`, or `netstat` for port/egress checks.

**Policy files (admin reviewed):**
- `~/.openclaw/security/approved_ports.json`
- `~/.openclaw/security/command-policy.json`
- `~/.openclaw/security/egress_allowlist.json`
- `~/.openclaw/security/prompt-policy.json`

Implement these controls in every security-sensitive task:

1. Keep default execution in normal (non-root) mode.
2. Request explicit user approval before any elevated command.
3. Scope elevation to the minimum command set required for the active task.
4. Drop elevated state immediately after the privileged command completes.
5. Expire elevated state after 30 idle minutes and require re-approval.
6. Monitor listening network ports and flag insecure or unapproved exposure.
7. Monitor outbound connections and flag destinations not in the egress allowlist.
8. If no approved baseline exists, generate one with `python3 scripts/generate_approved_ports.py`, then review and prune.
9. Benchmark controls against ISO 27001 and NIST and report violations with mitigations.

## Non-Goals (Web Browsing)

- Do not use web browsing / web search as part of this skill. Keep assessments and recommendations based on local host/OpenClaw state and the bundled references in this skill.

## Files To Use

- `references/least-privilege-policy.md`
- `references/port-monitoring-policy.md`
- `references/compliance-controls-map.json`
- `references/approved_ports.template.json`
- `references/command-policy.template.json`
- `references/prompt-policy.template.json`
- `references/egress-allowlist.template.json`
- `scripts/preflight_check.py`
- `scripts/root_session_guard.py`
- `scripts/audit_logger.py`
- `scripts/command_policy.py`
- `scripts/prompt_policy.py`
- `scripts/guarded_privileged_exec.py`
- `scripts/install-openclaw-runtime-hook.sh`
- `scripts/port_monitor.py`
- `scripts/generate_approved_ports.py`
- `scripts/egress_monitor.py`
- `scripts/notify_on_violation.py`
- `scripts/compliance_dashboard.py`
- `scripts/live_assessment.py`

## Behavior

- Never keep root/elevated access open between unrelated tasks.
- Never execute root commands without an explicit approval step in the current flow.
- Enforce command allow/deny policy when configured.
- Require confirmation when untrusted content sources are detected (`OPENCLAW_UNTRUSTED_SOURCE=1` + prompt policy).
- Enforce task session id scoping when configured (`OPENCLAW_REQUIRE_SESSION_ID=1`).
- If timeout is exceeded, force session expiration and approval renewal.
- Log privileged actions to `~/.openclaw/security/privileged-audit.jsonl` (best-effort).
- Flag listening ports not present in the approved baseline and recommend secure alternatives for insecure ports.
- Flag outbound destinations not present in the egress allowlist.

## Output Contract

When reporting status, include:

- The specific `check_id`(s) affected, `status`, `risk`, and concise evidence.
- Concrete mitigations (what to change, where) and any owners/due dates if present.
- For network findings: port, bind address, process/service, and why it is flagged (unapproved/insecure/public).
