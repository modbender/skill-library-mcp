---
name: snitch-message-guard
description: "Warn when an incoming message references a blocklisted term"
metadata:
  {
    "openclaw":
      {
        "emoji": "🚨",
        "events": ["message:received"],
      },
  }
---

# Snitch Message Guard

Intercepts incoming messages referencing blocklisted terms and pushes
a policy-violation notice before the agent processes the message.
