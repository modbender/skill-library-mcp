# Command cheat sheet (audit focus)

Run these on the OpenClaw host.

## Core (recommended minimum)

```bash
openclaw --version
openclaw status --all
openclaw doctor
openclaw security audit
openclaw security audit --deep
openclaw security audit --json
openclaw security audit --deep --json
```

## Helpful context

```bash
openclaw health --json
openclaw skills list --eligible --json
openclaw plugins list --json
```

## Safe targeted config reads (avoid printing tokens/passwords)

```bash
openclaw config get gateway.bind
openclaw config get gateway.auth.mode
openclaw config get discovery.mdns.mode
openclaw config get session.dmScope
```

## Safe sharing

Prefer `openclaw status --all` and `openclaw security audit --json`. Avoid sharing raw config/credentials.

If you must share a config for review, redact it:

```bash
python3 scripts/redact_openclaw_config.py ~/.openclaw/openclaw.json > openclaw.json5.redacted
```

## Network exposure checks

macOS:
```bash
lsof -nP -iTCP -sTCP:LISTEN
```

Linux:
```bash
ss -ltnp
```

Docker:
```bash
docker port openclaw-gateway 18789
```

## After remediation

```bash
openclaw security audit --deep
openclaw doctor
```
