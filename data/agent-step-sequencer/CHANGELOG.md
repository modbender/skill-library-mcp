# Changelog

## 1.1.0 — 2026-02-10

This release fixes the core execution failures encountered in production and addresses the OpenClaw security scan findings. The sequencer was silently marking steps as completed without performing any real work, and the documented CLI command did not exist. Both issues are now resolved.

### Breaking

- **STEP_AGENT_CMD is now required.**
  Previously defaulted to `echo`, which caused steps to silently pass without invoking the agent. The runner now exits with code 2 and a clear error if this variable is unset.

### Fixed

- **Corrected CLI command references.**
  All documentation and error messages referenced `openclaw ask`, which does not exist. Replaced with the correct `openclaw agent --message` across SKILL.md, README.md, scripts/README.md, and runner validation output.

- **Added binary validation on startup.**
  The runner now checks that the STEP_AGENT_CMD binary exists on PATH before executing any steps. Previously a bad command would silently fail and burn through all retries before surfacing the issue.

- **Step delay now applies between different steps.**
  `stepDelayMinutes` previously only triggered on retries of the same step. It now also applies when advancing to a subsequent step, matching the intended rate-limiting behavior described in the docs.

### Added

- **OpenClaw-compliant metadata in SKILL.md frontmatter.**
  Declares `python3` as a required binary and `STEP_AGENT_CMD` as a required environment variable, with install blocks for apt and brew. The skill will now gate properly during installation and surface missing dependencies.

- **Agent stdout captured in step runs.**
  `stepRuns[step_id].stdout` now stores the first 500 characters of agent output on success. Previously stdout was captured but discarded, making it impossible to observe what a step actually produced.

- **Three new tests added (12 total, all passing).**
  Covers: unset STEP_AGENT_CMD error, nonexistent binary error, and stdout capture on success.

### Security

- **Resolves OpenClaw security scan findings.**
  Python runtime and STEP_AGENT_CMD are now declared in skill metadata. Existing protections (command injection blocking, path traversal prevention, error truncation) are unchanged.

## 1.0.5 — 2026-02-08

Initial public release.

- Required outputs gate: runner marks step DONE only when all listed paths exist.
- Auto-advance: runner invokes check script after step DONE so next step runs immediately.
- Command injection prevention: shell interpreters blocked in STEP_AGENT_CMD.
- Autonomous recovery: agent retries with troubleshoot prompt, alerts user on persistent failure.
