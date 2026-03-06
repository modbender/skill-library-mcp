# Troubleshooting

Use this sequence for failure recovery.

## Baseline Diagnostics

```bash
social --version
social doctor
social auth status
```

If command routing is uncertain:

```bash
social --help
social <group> --help
```

## Common Issues

### `social` command not found

- Install or upgrade:

```bash
npm install -g @vishalgojha/social-cli
```

- On Windows PowerShell, try `social.cmd --help`.

### Authentication errors or missing scopes

```bash
social auth login --api facebook
social auth debug-token
social auth status
```

### Marketing permission error `(#200)`

Likely missing `ads_read` or `ads_management` access, or missing advanced access/app review.
Re-auth with required scopes and verify app configuration.

### Throttling or transient marketing failures

Retry with narrower fields/time window, then re-run after short backoff.
Prefer insights presets and async-friendly command patterns.

### Gateway access issues

- Verify bind host/port.
- Verify local-only default access and API key options.
- Re-run:

```bash
social gateway --host 127.0.0.1 --port 1310 --debug
```

## Safe Retry Pattern

1. Run diagnostics (`doctor`, `auth status`).
2. Run a minimal read-only command in same domain.
3. Re-run target command with explicit IDs and scoped profile/workspace.
