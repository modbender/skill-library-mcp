# Security Audit Response — OpenClaw Scan

**Date**: 2025-02  
**Scanner**: OpenClaw  
**Result**: Suspicious (medium confidence)  
**Status**: Reviewed and mitigated

---

## Summary of Findings

The OpenClaw security scanner flagged two medium-confidence items:

1. **Instruction Scope**: Scripts use `exec` and `sessions_spawn` but the SKILL.md did not show the enforcement mechanism for safelists.
2. **Persistence & Privilege**: The skill does not set `disableModelInvocation: true`, so the model may invoke it autonomously, combined with powerful tools.

Three items passed cleanly:
- ✅ **Purpose & Capability**: Name/description align with scripts.
- ✅ **Install Mechanism**: No external installer or network download.
- ✅ **Credentials**: No credentials or environment variables requested.

---

## Finding 1 — Instruction Scope

### Concern
> Runtime instructions call local scripts and OpenClaw tools: read, write, exec, sessions_spawn. The doc asserts only safelisted helper scripts are invoked and model output is treated as data, but the SKILL.md does not show the enforcement mechanism.

### Analysis
The concern is valid: prior to this update, enforcement of the safelist was a documented policy but was not technically enforced in the code itself. While the scripts were already deterministic (they do not parse model output to generate exec/spawn calls), the lack of visible validation made this difficult to audit.

### Mitigations Applied

| Mitigation | File | Effect |
|-----------|------|--------|
| Hard-coded tool name for emissions | `rlm_emit_toolcalls.py` | Tool emissions are restricted to the single hard-coded constant `EMITTED_TOOL = "sessions_spawn"`; no dynamic tool name from model output is used |
| Explicit `ALLOWED_ACTIONS` check on spawn manifest entries | `rlm_emit_toolcalls.py` | Manifest entries with unexpected action types are rejected |
| Required field and type validation | `rlm_emit_toolcalls.py` | Manifest entries missing `batch` (int) or `prompt_file` (non-empty string) are rejected |
| Path traversal checks on `prompt_file` | `rlm_emit_toolcalls.py` | Manifest entries with `..` path segments in `prompt_file` are rejected |
| `ALLOWED_ACTION` constant and limit enforcement | `rlm_async_spawn.py` | Only `sessions_spawn` action is written; `MAX_SUBCALLS` and `MAX_BATCHES` enforced |
| `MAX_SUBCALLS` enforcement at emission time | `rlm_emit_toolcalls.py` | Spawn manifests exceeding 32 entries are rejected |
| Path normalization and traversal checks | `rlm_ctx.py` | `os.path.realpath` normalizes paths; explicit `..` segment checks prevent directory traversal; `--ctx-dir` validated before directory creation |
| Named constants for all limits | `rlm_ctx.py` | `MAX_PEEK_LENGTH`, `MAX_SEARCH_RESULTS`, `MAX_CHUNKS` replace magic numbers |
| Explicit safelisted scripts list | `docs/policy.md` | Documents exactly which scripts may be invoked via `exec` |
| Enforcement mechanism documentation | `docs/security.md` | New "Enforcement Mechanisms" section details per-script validation |

### Residual Risk
- **Low**: The scripts are deterministic data processors. They accept structured CLI arguments and produce JSON/text output. No script interprets model output as code.
- The toolcall pipeline (`rlm_auto → rlm_async_plan → rlm_async_spawn → rlm_emit_toolcalls`) is driven by the initial plan from keyword extraction, not by model output.

### Usability Impact
- **None**: Enforcement adds validation that was implicit before. Valid workflows are unaffected.

---

## Finding 2 — Persistence & Privilege (Autonomous Invocation)

### Concern
> The skill does not set `disableModelInvocation: true`, so the model may invoke it autonomously. Combined with use of sessions_spawn and exec, that enables the model to trigger powerful actions unless policy enforcement prevents it.

### Analysis
This is a design trade-off, not a deficiency. The skill is intended to process large inputs that require many subcalls (up to 32). Requiring explicit user confirmation for each subcall would make the skill impractical for its primary use case.

### Mitigations Applied

| Mitigation | Effect |
|-----------|--------|
| Documented `disableModelInvocation` option in SKILL.md and docs/security.md | Operators can enable this setting based on their threat model |
| All operations bounded by hard limits (max 32 subcalls, max 8 batches, max 16k chars per slice) | Even autonomous invocation cannot exceed resource bounds |
| Sub-agents cannot spawn sub-agents (OpenClaw platform constraint) | Prevents recursive fan-out regardless of invocation mode |

### Recommendation
- **Default (keep as-is)**: For most deployments, autonomous invocation is appropriate because all operations are bounded and deterministic.
- **High-security deployments**: Set `disableModelInvocation: true` in OpenClaw configuration to require explicit user approval. Accept the usability cost of manual confirmation per batch.

### Usability Impact of Setting `disableModelInvocation: true`
- User must confirm each invocation of the skill
- For a typical run with 4 batches of 4 subcalls, this means 4+ confirmations
- Acceptable for high-security environments, impractical for daily use with large inputs

---

## Additional Findings Addressed

### SKILL.md Wording
The scanner noted "SKILL.md says 'No install spec — instruction-only', yet several executable scripts are bundled." Updated SKILL.md to explicitly state that scripts are bundled helpers (not downloaded at runtime), and that `exec` invokes only these safelisted scripts.

### cleanup.sh Reliability
The scanner recommended verifying that `cleanup.sh` reliably purges temporary artifacts. The script:
- Uses `set -euo pipefail` for strict error handling
- Targets only `scratch/rlm_prototype/{ctx,logs}/` paths
- Respects ignore patterns from `docs/cleanup_ignore.txt`
- Supports retention mode (`CLEAN_RETENTION=N`) to keep last N files
- Added cleanup verification step to `docs/security_checklist.md`

---

## Conclusion

The OpenClaw scanner's findings were reasonable for an automated scan. The skill's architecture is sound — scripts are deterministic data processors that do not interpret model output as code. The mitigations applied add **technical enforcement** (code-level safelist validation) to complement the existing **policy enforcement** (documented rules). The `disableModelInvocation` trade-off is now explicitly documented so operators can choose based on their threat model.

**Overall risk after mitigations: Low**
