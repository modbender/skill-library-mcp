---
name: hide-openclaw-banner
description: Suppress the OpenClaw CLI banner message. Use when the user says "hide openclaw banner", "disable openclaw banner", "suppress openclaw banner", "remove openclaw banner", "openclaw banner is annoying", "turn off the lobster", or wants to stop seeing the OpenClaw startup tagline on every command invocation.
---

# Hide OpenClaw Banner

The OpenClaw CLI banner is emitted during CLI bootstrap (Commander.js `preAction` hook) before the plugin system initializes. A plugin cannot suppress it. Use the built-in env var instead.

## How to Apply

Add to the user's shell config (`~/.zshrc` or `~/.bashrc`):

```bash
export OPENCLAW_HIDE_BANNER=1
```

Place it near any existing OpenClaw config (e.g., after the completions `source` line).

After editing, remind the user to run `source ~/.zshrc` or open a new terminal.

## How to Revert

Remove the `OPENCLAW_HIDE_BANNER` line from the shell config, then `source ~/.zshrc`.
