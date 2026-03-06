# OpenClaw Secrets Integration

This skill aligns to OpenClaw-style secret references instead of maintaining its own credential store.

## Preferred Inputs

- `MASSIVE_API_KEY_REF`: JSON secret reference used by OpenClaw-aware runtimes
- `MASSIVE_API_KEY`: plaintext fallback for local development only
- `MASSIVE_BASE_URL`: optional override; defaults to `https://api.massive.com`

## Supported SecretRef Shapes

The CLI accepts a compact JSON object in `MASSIVE_API_KEY_REF` and resolves it before issuing any network request.

Supported `source` values:

- `env`: read a named environment variable
- `file`: read a file path and trim the trailing newline
- `exec`: execute a command and use stdout as the secret, matching OpenClaw's SecretRef model

Supported keys by source:

- `env`: `name` or `key`
- `file`: `path`
- `exec`: `command` or `cmd`

Example values:

```json
{"source":"env","name":"OPENCLAW_MASSIVE_API_KEY"}
```

```json
{"source":"file","path":"/run/secrets/massive_api_key"}
```

```json
{"source":"exec","command":"op read op://shared/massive/api-key"}
```

## Resolution Rules

1. Parse `MASSIVE_API_KEY_REF` as JSON.
2. Resolve the referenced value.
3. Fail before making the request if the reference cannot be resolved.
4. Fall back to `MASSIVE_API_KEY` only when `MASSIVE_API_KEY_REF` is unset.

## Logging Rules

- Never log `MASSIVE_API_KEY` or the resolved output of a secret ref.
- Never log `MASSIVE_API_KEY_REF` verbatim because `exec` refs can disclose internal tooling.
- Log only the fact that auth was configured, not how it was resolved.

## Alignment Note

`exec` refs are intentionally supported to stay aligned with OpenClaw Secrets Management. Keep that behavior documented and assume the surrounding runtime is responsible for provider sandboxing and policy enforcement.
