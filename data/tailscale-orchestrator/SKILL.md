---
name: SKILL.md
description: "name: Tailscale Network Orchestrator slug: tailscale-orchestrator
  summary: Manage your Tailscale network and devices directly from ClawBot.
  description: |- This skill provides commands to check Tai..."
---

# SKILL.md

name: Tailscale Network Orchestrator
slug: tailscale-orchestrator
summary: Manage your Tailscale network and devices directly from ClawBot.
description: |-
  This skill provides commands to check Tailscale status, list connected devices, and perform basic network operations. It leverages the `tailscale` command-line interface (CLI) installed on the host machine where ClawBot is running. This allows for secure and direct management of your Tailscale network without exposing sensitive API keys directly to the skill.
author: Manus AI
version: 0.1.0
trigger:
  - "manage tailscale"
  - "tailscale status"
  - "list tailscale devices"
commands:
  - name: status
    description: Displays the current Tailscale status, including connection state and active nodes.
    usage: "status"
    script: python3 main.py status
  - name: devices
    description: Lists all connected devices in your Tailscale network with their status and IP addresses.
    usage: "devices"
    script: python3 main.py devices
