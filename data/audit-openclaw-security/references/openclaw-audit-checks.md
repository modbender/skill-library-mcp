# OpenClaw security audit: high-signal checks (quick glossary)

This is a convenience map for interpreting `openclaw security audit --json` results.

> Treat OpenClaw’s own audit output as source of truth. This file is intentionally *not exhaustive*.

| checkId | Typical severity | Why it matters | Primary fix key/path | Auto-fix? |
|---|---:|---|---|---:|
| `fs.state_dir.perms_world_writable` | Critical | Other users/processes can modify OpenClaw state (full compromise) | filesystem perms on `~/.openclaw` | Yes |
| `fs.config.perms_writable` | Critical | Others can change auth/tool policy/config | perms on `~/.openclaw/openclaw.json` | Yes |
| `fs.config.perms_world_readable` | Critical | Config can leak tokens/credentials | perms on config file | Yes |
| `gateway.bind_no_auth` | Critical | Remote bind without shared secret | `gateway.bind`, `gateway.auth.*` | No |
| `gateway.loopback_no_auth` | Critical | Reverse proxy can turn localhost into unauthenticated access | `gateway.auth.*`, proxy setup | No |
| `gateway.tools_invoke_http.dangerous_allow` | Warn/Critical | Dangerous tools exposed via HTTP API | `gateway.tools.allow` | No |
| `gateway.tailscale_funnel` | Critical | Public internet exposure | `gateway.tailscale.mode` | No |
| `gateway.control_ui.insecure_auth` | Critical | Token-only over HTTP; no device identity | `gateway.controlUi.allowInsecureAuth` | No |
| `gateway.control_ui.device_auth_disabled` | Critical | Disables device identity checks entirely | `gateway.controlUi.dangerouslyDisableDeviceAuth` | No |
| `hooks.token_too_short` | Warn | Easier brute force on hook ingress | `hooks.token` | No |
| `hooks.request_session_key_enabled` | Warn/Critical | External caller can choose session keys (persistence/collision risk) | `hooks.allowRequestSessionKey` | No |
| `hooks.request_session_key_prefixes_missing` | Warn/Critical | No bound on external sessionKey shapes | `hooks.allowedSessionKeyPrefixes` | No |
| `logging.redact_off` | Warn | Sensitive values can leak to logs/status | `logging.redactSensitive` | Yes |
| `sandbox.docker_config_mode_off` | Warn | Sandbox config exists but sandboxing is off | `agents.*.sandbox.mode` | No |
| `tools.profile_minimal_overridden` | Warn | Per-agent profile overrides bypass a minimal global profile | `agents.list[].tools.profile` | No |
| `plugins.tools_reachable_permissive_policy` | Warn | Extension tools reachable in permissive contexts | `tools.profile` + tool allow/deny | No |
| `models.small_params` | Critical/Info | Weaker models + tools increase injection risk | model choice + sandbox/tool policy | No |

## Notes for auditors

- “Auto-fix” typically means `openclaw security audit --fix` can repair *some* filesystem/logging issues. It will not safely fix exposure problems (bind/auth/proxy) without you making intent explicit.
- If you see any `gateway.*` critical finding, treat it as **urgent**.
