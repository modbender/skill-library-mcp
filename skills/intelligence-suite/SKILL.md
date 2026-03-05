---
name: intelligence-suite
description: Makima's All-Seeing Intelligence Suite. Combines real-time AI news tracking and global news monitoring for a comprehensive strategic briefing.
metadata:
  openclaw:
    emoji: 📡
    category: intelligence
    requires:
      bins: [node, npm]
    permissions:
      network: [openai.com, microsoft.com, firebaseio.com, reuters.com, scmp.com, rthk.hk]
      filesystem: [read]
---

# The Intelligence Suite

Makima's personal intelligence unit. Scans the web for high-signal AI news and monitors global geopolitics to provide a comprehensive strategic briefing.

## Security & Transparency
This skill is designed for deep information gathering. It performs the following actions:
- **Network Access**: Fetches RSS feeds and API data from trusted news sources and technology blogs.
- **Deep Scrape**: Occasionally visits full article URLs to extract text content for analysis.
- **Data Handling**: Processes information locally; results are provided to the agent for synthesis.

## Components

1.  **AI News Monitor**: Tracks OpenAI, DeepMind, Anthropic, and other major AI labs.
2.  **Global News Hub**: Monitored sources include Reuters, RTHK, and SCMP.

## Installation

```bash
cd skills/intelligence-suite
npm install
```

## Usage

```bash
# Scan AI news
node scripts/scan.js --report

# Monitor global news
node scripts/monitor.js --report
```

*Created and maintained by Makima (Public Safety Special Division 4).* ⛓️
