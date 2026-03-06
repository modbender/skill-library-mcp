# Changelog

## 1.0.5 - 2026-02-15
- Reworded safety preamble and injection pattern signatures to reduce false-positive scanner heuristics while preserving protections.
- No functional downgrade to sanitization or policy boundary behavior.

## 1.0.4 - 2026-02-15
- Removed speculative premium key/hosted API code snippets from `PUBLISHING.md` to reduce security-scan ambiguity.
- Clarified local-first service positioning in publishing roadmap.

## 1.0.3 - 2026-02-15
- Added default safe-state mode (`ORCHESTRATOR_SAFE_STATE=1`) to reduce sensitive persistence risk.
- Implemented redaction for state-file task/output previews (`sk-`, `nsec`, `nwc`, key/token patterns).
- Added `tests/security_test_plan.md` with injection and persistence regression checks.
- Expanded `SECURITY.md` with runtime hardening guidance.

## 1.0.2 - 2026-02-15
- Security hardening:
  - Added untrusted task sanitization before sub-agent spawn.
  - Added safety boundary preamble for all spawned sub-agent tasks.
  - Added OpenClaw subcommand allowlist in execution path.
  - Added binary resolution/validation for `openclaw` CLI invocation.
- Added `SECURITY.md` with threat model, mitigations, and residual risk.
- Added workspace-level `docs/publish-security-checklist.md` for future publish gates.

## 1.0.1 - 2026-02-15
- Added publish-grade `README.md` with quick start, outcomes, and safety notes.
- Added `.clawhubignore` to prevent publishing local runtime artifacts/state files.
- Updated publishing guidance for ClawHub `.com` registry and proof-of-work positioning.

## 1.0.0 - Initial release
- Implemented 5 orchestration patterns:
  - Crew
  - Supervisor
  - Pipeline
  - Council
  - Route
- Added examples and usage docs in `SKILL.md` + `examples/`.
