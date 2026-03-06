---
name: MacPowerTools
description: Safe self-learning 24/7 toolkit for OpenClaw agents on Apple Silicon Mac Mini — adaptive tuning, cleanup, local backups, Moltbook promotion.
author: AadiPapp
version: 2.5.0
license: MIT
tags: [macos, mac-mini, m-series, openclaw, self-learning, moltbook, agent-host, safe-maintenance]
emoji: 🦞✅

metadata:
  openclaw:
    skill_type: "scripted"
    os: ["darwin"]
    requires:
      binaries:
        - rsync
        - adb          # optional Android transfer only
        - system_profiler
        - pmset
        - powermetrics
        - launchctl
      python: ">=3.10"
    env:
      optional:
        - MOLTBOOK_TOKEN: "Bearer token for promote --post (Moltbook API only)"
    install:
      - "brew install android-platform-tools rsync coreutils powermetrics"
    capabilities: ["self-learning", "local-backup", "moltbook-promotion", "user-level-daemon"]
---

# MacPowerTools v2.5 — Safe Self-Learning Agent Host for Mac Mini

**Purpose & Capability**  
Self-maintaining toolkit for 24/7 OpenClaw agents. Cleans caches, tunes performance, backs up locally, learns from its own history, and promotes itself on Moltbook.

**Privilege & Safety (ClawHub Review Notes)**  
- **No sudo ever called** by the script.  
- **Backup restricted** to mounted volumes `/Volumes/*` only (remote destinations rejected).  
- All commands default to dry-run or safe mode.  
- Daemon is **user-level only** (`~/Library/LaunchAgents`).  
- Network activity limited to optional Moltbook `--post`.  
- Full source is provided below — no truncated sections.

**Install**  
```bash
brew install android-platform-tools rsync
macpowertools setup --install-daemon   # optional daily maintenance