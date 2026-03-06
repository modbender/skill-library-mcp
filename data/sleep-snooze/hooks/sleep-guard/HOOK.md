---
name: sleep-guard
description: Injects current sleep state into every agent bootstrap context, preventing any agent from sending messages during sleep hours.
metadata:
  openclaw:
    emoji: "🌙"
    events:
      - agent:bootstrap
    export: default
---

# Sleep Guard Hook

Fires on every `agent:bootstrap` event. Reads the current sleep state from `state.json` and — if sleep mode is active — injects a `SLEEP_MODE_ACTIVE.md` bootstrap file into the agent's context.

This ensures every agent, regardless of when its session started, is aware of sleep mode before taking any action.
