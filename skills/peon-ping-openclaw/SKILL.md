---
name: peonping-alerts
description: Install and configure PeonPing with an opinionated default (Orc Peon voice) so alerts work immediately with minimal user friction. Use when the user asks for hassle-free completion sounds for coding/agent workflows.
---

# PeonPing Alerts Skill

Make PeonPing work out-of-the-box with **Orc Peon** as default.

## Default behavior (do this first)

Run this exact flow with `exec`:

```bash
brew install PeonPing/tap/peon-ping
peon-ping-setup
peon packs install orc-peon || true
peon packs use orc-peon
peon volume 0.45
peon notifications on
peon preview
peon status
```

If Homebrew is unavailable, use:

```bash
curl -fsSL https://raw.githubusercontent.com/PeonPing/peon-ping/main/install.sh | bash
peon-ping-setup
peon packs install orc-peon || true
peon packs use orc-peon
peon volume 0.45
peon notifications on
peon preview
peon status
```

## What to tell the user after setup

Use this message pattern:

- "PeonPing is installed and set to **Orc Peon** by default."
- "If you want a different voice/pack, tell me and I’ll switch it."

## Customization on request

- List packs: `peon packs list --registry`
- Switch pack: `peon packs use <pack_name>`
- Cycle packs: `peon packs next`
- Adjust volume: `peon volume <0.0-1.0>`
- Test notifications: `peon notifications test`

## Quick recovery (if no sound)

Run, in order:

```bash
peon status
peon preview
peon notifications test
peon-ping-setup
```

Then re-apply default:

```bash
peon packs use orc-peon
peon volume 0.45
peon notifications on
```

## Guardrails

- Prefer Homebrew path when possible.
- Only use official project URLs.
- Do not claim a pack is active before confirming with `peon status` and `peon preview`.
