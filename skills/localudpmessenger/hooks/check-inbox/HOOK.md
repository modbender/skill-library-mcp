---
name: check-inbox
description: Checks for unread UDP messages from peers before the agent stops
metadata:
  openclaw:
    emoji: "\U0001F4EC"
    events:
      - command:stop
    requires:
      bins:
        - node
---

# Check Inbox Hook

Before the agent stops, this hook checks if there are unread UDP messages from trusted peers. If messages exist and the conversation limit hasn't been reached, the agent is prompted to process them.
