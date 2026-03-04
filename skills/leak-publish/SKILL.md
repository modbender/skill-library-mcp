---
name: leak-publish
description: Publish local files behind an x402 payment gate with explicit public-exposure consent using a preinstalled leak CLI.
compatibility: Requires access to the internet
version: 2026.2.17
metadata:
  openclaw:
    emoji: 📡
    os: ["darwin", "linux"]
    requires:
      env:
      bins: ["leak"]
    install:
      - kind: node
        package: leak-cli
        bins: ["leak"]
        label: "Install leak-cli via npm"
  author: eucalyptus-viminalis
---

# leak-publish

## Overview

This skill operates publish workflows only:
- Publish a local file behind an x402 gate.
- Optionally expose with `--public` after explicit consent.
- Keep process alive using detached supervisors.

## Safety policy (required)

1. Require explicit user confirmation of the file path.
2. Require explicit user consent before `--public` exposure.
3. Reject symlink paths.
4. Reject directories and non-regular files.
5. Block sensitive paths:
  - `~/.ssh`
  - `~/.aws`
  - `~/.gnupg`
  - `~/.config/gcloud`
  - `/etc`
  - `/private/etc`
  - `/proc`
  - `/sys`
  - `/var/run/secrets`
  - `/private/var/run/secrets`

## Dependency policy (required)

1. Require `leak` binary on PATH.
2. Do not execute `npx` or dynamic package install at runtime.

## Runtime policy (required)

1. Treat publish as persistent-by-default for all sale windows.
2. Use `--run-mode auto` unless user explicitly asks for foreground.
3. Detached supervisor order:
  - `systemd --user` (Linux)
  - `launchd` (macOS)
  - `tmux`
  - `screen`
  - `nohup` fallback
4. After background launch, report control details:
  - supervisor/session or PID
  - log file
  - stop command

## Required inputs

1. File path.
2. Price in USDC.
3. Sale window.
4. Seller payout address (`--pay-to`).
5. Public exposure choice (`--public` or local only).

## Local publish

```bash
bash skills/leak-publish/scripts/publish.sh \
  --run-mode auto \
  --file ./protected/asset.bin \
  --price 0.01 \
  --window 15m \
  --pay-to 0xSELLER_ADDRESS \
  --network eip155:84532
```

## Public publish

```bash
bash skills/leak-publish/scripts/publish.sh \
  --run-mode auto \
  --file ./protected/asset.bin \
  --price 0.01 \
  --window 15m \
  --pay-to 0xSELLER_ADDRESS \
  --public
```

## Runtime smoke check

```bash
bash skills/leak-publish/scripts/smoke_persistent_runner.sh --mode auto --sleep-seconds 8
```

Expected result: `PASS` and selected backend.

## Troubleshooting

- `leak` missing:
  - install: `npm i -g leak-cli`
- public confirmation failed:
  - rerun with exact confirmation phrase when prompted
