---
name: xclaw
description: XClaw Intelligence Skill. Provides real-time trending tweets, KOL deep analysis, live user crawling, profile history, and social relation tracking.
allowed-tools: Bash(node:*) Read Write
metadata:
  {
    "openclaw": { "requires": { "env": ["CRYPTOHUNT_API_KEY"] } },
    "homepage": "https://pro.cryptohunt.ai",
    "codelink": "https://github.com/mookim-eth/xclaw-skill"
  }
---

# Skill: XClaw Intelligence 🚀

XClaw is the premier intelligence layer for OpenClaw creators, providing real-time social data and insights from the CryptoHunt engine.

## Prerequisites
- **API Key Required**: Set `CRYPTOHUNT_API_KEY` in your environment.
- **Get your Key**: Purchase or register for an API key at [apidashboard.cryptohunt.ai](https://apidashboard.cryptohunt.ai).
- **Official API Docs**: Detailed endpoint documentation can be found at [pro.cryptohunt.ai](https://pro.cryptohunt.ai).

## Core Capabilities

### 1. Trending Discovery (`xclaw_hot`)
- **Action**: Fetch the top performing tweets in the last 1/4/24 hours.
- **Multi-Dimensional Filtering**: Support for region (`cn`/`global`) and tags (e.g., `AI`, `meme`).

### 2. Recent Slim Tweets (`xclaw_tweets`)
- **Action**: Fetches latest 15-20 tweets and performs data slimming (slimTweets) for efficient reading.
- **Compatibility**: Legacy aliases `xclaw_analyze` / `xclaw_crawl` are kept as redirects to this capability.

### 3. Ghost Analysis (`xclaw_ghost`)
- **Action**: Sniff out tweets that have been **deleted** by a specific user.

### 4. Identity Traces (`xclaw_traces`)
- **Action**: Retrieve history of profile changes (Bio, Avatar, Name) for a specific user to track identity evolution.

### 5. Social Pulse (`xclaw_social`)
- **Action**: Track recent **Follow** and **Unfollow** actions of a specific user.

### 6. Account Deep Rank (`xclaw_rank`)
- **Action**: Comprehensive account analysis including rankings, ability model (hexagonal chart data), soul score, and interest tags.

### 7. Tweet Deep Dive (`xclaw_detail`)
- **Action**: Fetches full content, metrics, and thread data for a specific tweet.

### 8. Smart Content Ideation (`xclaw_draft`)
- **Action**: Fetch viral topics tailored by region and tag to generate high-conversion tweet drafts with original links.

## User Commands for Agent
- "xclaw find hot": Get the last 4h of Chinese crypto hot tweets.
- "xclaw tweets <username>": Get recent slimmed tweets from @username.
- "xclaw analyze <username>" / "xclaw crawl <username>": Legacy aliases, same behavior as `xclaw tweets <username>`. 
- "xclaw ghost <username>": See what @username tried to delete.
- "xclaw traces <username>": Check if @username changed their bio or name recently (Identity Traces).
- "xclaw social <username>": See who @username recently followed or unfollowed.
- "xclaw rank <username>": Get soul score, rankings and ability model for @username.
- "xclaw detail <URL_or_ID>": Fetch all details and stats for a specific tweet.
- "xclaw draft": Automatically fetch viral hooks and suggest 3 tweet versions.

---
*CryptoHunt Intelligence - Data for Creators.*

Code link: https://github.com/mookim-eth/xclaw-skill
