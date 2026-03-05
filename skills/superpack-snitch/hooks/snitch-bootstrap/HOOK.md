---
name: snitch-bootstrap
description: "Inject a standing security directive for all blocklisted terms into every agent context"
metadata:
  {
    "openclaw":
      {
        "emoji": "🔒",
        "events": ["agent:bootstrap"],
      },
  }
---

# Snitch Bootstrap

Injects a security directive into every agent bootstrap context prohibiting
invocation of any skill or tool matching the configured blocklist.
