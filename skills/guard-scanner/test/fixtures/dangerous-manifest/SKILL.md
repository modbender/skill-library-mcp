---
name: dangerous-manifest-skill
description: A skill with dangerous requirements
metadata:
  clawdbot:
    emoji: "💀"
    requires:
      bins:
        - node
        - sudo
        - rm
        - curl
      env:
        - AWS_SECRET_ACCESS_KEY
    files: ["**/*"]
---

# Dangerous Manifest Skill

This skill requires dangerous binaries and overly broad file access.
