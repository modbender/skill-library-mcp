---
name: fork-and-skill-scanner-ultimate
version: 1.1.1
description: "Scan 1,000 GitHub forks per run. Surface the gold, skip the clones — fully automated."
metadata:
  openclaw:
    owner: kn7623hrcwt6rg73a67xw3wyx580asdw
    category: developer-tools
    tags:
      - github
      - forks
      - skill-discovery
      - automation
      - community-insights
    license: MIT
    notes:
      security: "Uses GitHub's public API (read-only) to list and compare forks. No write access, no authentication required for public repos. Sub-agents are spawned locally via OpenClaw's sessions_spawn. Reports delivered through existing configured channels (WhatsApp, etc). No credentials stored or requested."
---

# Ultimate Fork and Skill Scanner

**1,000 forks. 3 filters. Only gold reaches your inbox.**

Most forks are exact clones gathering dust. Somewhere in the pile, someone rewrote your auth layer, tripled throughput, or added a feature you hadn't thought of. This skill finds those needles — automatically.

## How It Works

A three-stage funnel keeps costs low and signal high:

1. **Bash Pre-Filter** — Discards inactive and identical forks in seconds. No tokens wasted on dead copies.
2. **Sub-Agent Deep Analysis** — Surviving forks get inspected by parallel agents: diff quality, new patterns, performance changes.
3. **Actionable Report** — Only forks worth your attention make the cut. Delivered to WhatsApp. No noise, no empty summaries.

## Skill Scanner

Reviews 10 ClawHub skills daily. Surfaces top picks, tracks emerging trends, and follows skilled authors to find more of their work.

## What You Get

- Up to 1,000 forks analyzed per run
- Daily skill reviews with trend detection
- Reports only when there's something worth reporting
- Token-efficient by design — bash does the heavy lifting before agents spend a single token

*Clone it. Fork it. Break it. Make it yours.*

👉 Explore the full project: [github.com/globalcaos/clawdbot-moltbot-openclaw](https://github.com/globalcaos/clawdbot-moltbot-openclaw)
