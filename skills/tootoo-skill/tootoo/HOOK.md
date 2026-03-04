---
name: tootoo-monitor
description: Hooks into agent responses to check alignment against TooToo codex
events:
  - after_response
---

# Alignment Monitor Hook

This hook intercepts every agent response (async) and runs it through the alignment check logic.
