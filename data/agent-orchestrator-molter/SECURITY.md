# Security Notes

## Threat model (known risks)
This skill orchestrates sub-agents using user-provided task input. Core risks:
- Prompt injection attempts embedded in task input
- Unsafe task propagation to spawned sessions
- Trust on external `openclaw` CLI behavior

## Mitigations implemented (v1.0.2)
- Untrusted task sanitization before spawn (`sanitize_untrusted_task`)
- Safety boundary preamble prepended to all spawned sub-agent tasks
- Allowlist for OpenClaw subcommands (`sessions_spawn`, `sessions_list`, `sessions_history`)
- Binary path resolution/validation via `shutil.which("openclaw")`

## Residual risk
- Prompt injection cannot be reduced to zero in LLM systems.
- Safety still depends on OpenClaw runtime policies and model compliance.

## Recommended operating mode
- Keep tasks scoped and explicit.
- Do not pass secrets in task text.
- Use least-privilege permissions in host environment.
- Review generated outputs before high-impact actions.

## Runtime hardening
- Safe-state persistence is enabled by default (`ORCHESTRATOR_SAFE_STATE=1`).
- State files persist redacted previews rather than full task/output payloads.
- Only disable safe-state (`ORCHESTRATOR_SAFE_STATE=0`) for controlled debugging.
- Run in sandbox/test environment first when introducing new workflow prompts.
