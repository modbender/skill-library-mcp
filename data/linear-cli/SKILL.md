---
name: linear-cli
description: Linear CLI skill for OpenClaw workflows, powered by Api2Cli (a2c) against Linear's GraphQL API. Provides a wrapper script that generates its a2c workspace config at runtime (no custom HTTP client code).
---

# Linear (CLI)

This skill provides a tiny, deterministic CLI surface for Linear using **Api2Cli (a2c)** + a declarative GraphQL request config.

## What you get

- `scripts/linear` wrapper (recommended entrypoint)
- `a2c/config.xfer` request definitions (GraphQL queries/mutations)

## Requirements

- `a2c` installed and available on `PATH`
- A Linear API key exported as `LINEAR_API_KEY`

## Quick start

```bash
export LINEAR_API_KEY="<your_linear_api_key>"

./scripts/linear --help
./scripts/linear whoami
```

## Smoke test

1) Verify dependencies:

```bash
command -v a2c
```

2) Verify help renders:

```bash
./scripts/linear --help
```

3) Verify auth works:

```bash
LINEAR_API_KEY=... ./scripts/linear whoami
```
