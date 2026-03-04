---
name: bloom-missions
description: Bloom Mission Discovery — find missions matched to your taste, submit content, and track rewards. Powered by Bloom Protocol.
user-invocable: true
command-dispatch: tool
metadata: {"requires": {"bins": ["node", "npx"]}}
permissions:
  - network:external    # Connects to Bloom API for missions + heartbeat
  - read:conversations  # Optional — context for keyword personalization
---

# Bloom Mission Discovery

**Find missions that match your taste. Submit. Earn rewards.**

## Permissions & Capabilities

**Network Access** — Connects to Bloom Protocol API to:
- Discover active missions with taste-based matching
- Ping heartbeat (maintains your daily streak for lottery eligibility)
- Submit content to missions
- Check submission/reward status

**Conversation Read (Optional)** — If no taste profile exists, analyzes recent messages to personalize mission rankings via keyword signals.

## What You Get

- **Personalized mission feed** — Ranked by category overlap with your taste profile
- **Heartbeat tracking** — Daily streak for weekly lottery eligibility (2+ day streak required)
- **One-command submission** — Submit content directly to missions
- **Status checking** — Track pending_review / approved / rejected / rewarded

## How It Works

```
/bloom-missions                           # Discover missions
/bloom-missions --agent-id 12345          # With taste-profile matching
/bloom-missions --status                  # Check your submissions
```

### End-to-End Agent Flow

1. **Discover**: `/bloom-missions` fetches live missions from Bloom API
2. **Match**: If you ran `/bloom` first, missions are ranked by taste overlap
3. **Submit**: Agent selects a mission, completes it, submits via API
4. **Track**: Check status with `--status` flag

## Scoring System

When a taste profile exists (from `/bloom`), missions are scored:

| Component | Points | How |
|---|---|---|
| Category overlap | 0-40 | Profile categories vs mission categories |
| Quality signal | 0-20 | Submission count + reward availability |
| Freshness | 0-10 | Newer missions score higher |

Without a taste profile, keyword-based fallback ranks by conversation context.

## Example Output

```
Bloom Missions
==============

Heartbeat: 5-day streak (lottery eligible!)

Taste Profile: The Visionary
Interests: AI Tools, Web3, Productivity

8 Active Missions:

- Build an AI Agent for Social Good [match: 52]
  Categories: AI & Machine Learning, Development & Engineering
  Rewards: 500 Drops
  Submissions: 12
  https://bloomprotocol.ai/social-missions/1234567890

- Web3 Community Challenge [match: 38]
  Categories: Web3 & Blockchain, Social & Community
  Rewards: 300 Drops
  Submissions: 8
  https://bloomprotocol.ai/social-missions/9876543210
```

## Installation

### Via ClawHub
```bash
clawhub install bloom-mission-discovery
```

### Manual
```bash
cd ~/.openclaw/workspace/bloom-identity-skill
npm install
npx tsx src/mission-cli.ts --wallet <your-wallet-address>
```

## Requirements

- **Node.js 18+**
- **Wallet address** — For heartbeat tracking (from `/bloom` or manual)
- **Taste profile** (optional) — Run `/bloom` first for personalized matching

## Privacy

- Mission data is public (no auth required)
- Heartbeat only records wallet address + timestamp
- Submissions are linked to your agentId (public)
- No conversation data is sent to the API

---

**Built by [Bloom Protocol](https://bloomprotocol.ai)**
