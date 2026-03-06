# Security Model — OpenClaw Dashboard

## Threat Model & Design Philosophy

This dashboard is an **administrative control plane** for OpenClaw — analogous to Terraform, Ansible, or Kubernetes Dashboard. Administrative tools inherently require elevated capabilities (file access, process control, service management). The security model is **defense-in-depth with opt-in escalation**: all sensitive capabilities are disabled by default and require explicit operator consent to activate.

**Key principle:** No sensitive capability is available without the operator explicitly setting an environment variable AND being on localhost.

## Authentication

- **Primary**: HttpOnly + SameSite=Strict cookie (`ds`), set at `/auth` endpoint.
- **Initial handoff**: URL `?token=` parameter accepted once on page load, then immediately stripped from the address bar via `history.replaceState` to prevent leakage in Referer headers, server logs, and browser history.
- **API calls**: All subsequent API requests use `Authorization: Bearer <token>` header — never URL query parameters.
- **No client-side token storage**: Auth tokens are NOT stored in localStorage or sessionStorage. This eliminates XSS-based token theft.
- **Localhost-only by default**: Dashboard binds to `127.0.0.1`. External access requires explicit Tailscale Funnel or reverse proxy setup.

## Capability Escalation Matrix

All elevated capabilities follow the same pattern: **off by default → env flag to enable → localhost-only → input sanitization**.

| Capability | Env Flag Required | Default | Localhost-Only | Input Sanitization |
|---|---|---|---|---|
| File attachment copy | `OPENCLAW_ALLOW_ATTACHMENT_FILEPATH_COPY=1` | ❌ Off | ✅ Yes | `realpathSync` symlink resolution, directory allowlist (`/tmp`, `~/.openclaw`, workspace) |
| Git push / backup | `OPENCLAW_ENABLE_MUTATING_OPS=1` | ❌ Off | ✅ Yes | `execFileSync` with array args (no shell expansion) |
| npm install | `OPENCLAW_ENABLE_MUTATING_OPS=1` | ❌ Off | ✅ Yes | `execFileSync` with array args |
| Service restart | `OPENCLAW_ENABLE_MUTATING_OPS=1` | ❌ Off | ✅ Yes | Proxied via authenticated API endpoint with env-sourced token |
| Task CRUD / notes | `OPENCLAW_AUTH_TOKEN` (always required) | N/A | ✅ Yes | SQL parameterized queries, `escHtml` output encoding |

**Without any flags set**, the dashboard is a **read-only monitoring tool** with zero mutating surface.

### File Copy Path Restrictions

When `OPENCLAW_ALLOW_ATTACHMENT_FILEPATH_COPY=1` is set:
- Paths are resolved via `fs.realpathSync` to prevent symlink traversal attacks
- Only files under these directories are accessible: `/tmp`, `~/.openclaw`, and the configured workspace
- All other paths are rejected with 403

### Process Execution Safety

All `child_process` calls use `execFileSync` with **array arguments** (never string concatenation), which prevents shell injection by design. No user input is ever interpolated into a shell command string.

## Prompt Injection Surface

The dashboard relays task descriptions and cron messages to the OpenClaw agent via `sessions_send`. This is an inherent prompt injection surface in any AI agent system.

**Mitigations in place:**
1. `sanitizeUntrustedText()` strips control characters, trims to max length, and rejects known injection patterns.
2. All task fields are wrapped with `[UNTRUSTED USER INPUT]` markers before reaching the agent.
3. The agent's system prompt instructs it to treat these fields as data, not instructions.

**Residual risk:** A sufficiently crafted payload could still influence agent behavior. This is a fundamental limitation of LLM-based systems, not specific to this dashboard. This risk is equivalent to any system that passes user input to an LLM (e.g., ChatGPT plugins, Slack bots, email assistants).

## XSS Prevention

- **Markdown rendering**: All markdown output (task descriptions, file previews) is sanitized through DOMPurify before injection into the DOM.
- **Static text**: Uses `escHtml()` for all user-supplied strings in non-markdown contexts.
- **Gateway restart**: Proxied through authenticated `/ops/restart` endpoint on the API server — no tokens embedded in client-side code.

## Data Storage

- SQLite database and logs stored under `~/.openclaw/` (not web-accessible)
- No secrets stored in the dashboard's own files
- Dashboard reads `OPENCLAW_AUTH_TOKEN` from environment, never writes it to disk

## Summary of Security Layers

```
Request → Localhost check → Auth (cookie/Bearer) → Env flag gate → Input sanitization → Action
```

Every elevated action passes through **4 independent security checks** before execution. Disabling any single layer does not compromise the others.
