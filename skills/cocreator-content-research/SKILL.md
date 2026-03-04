---
name: cocreator-content-research
description: "Pure intelligence gathering for social media platforms (TikTok & Instagram). Use when an agent needs to discover trending hooks, analyze a competitor's strategy, or look up a specific creator's profile data. This skill does not generate content or post; it relies entirely on ScrapeCreators to return data for analysis."
metadata:
  {
    "openclaw": {
      "emoji": "🔍",
      "requires": {
        "bins": ["uv"],
        "env": ["SCRAPE_CREATORS_API_KEY"]
      },
      "primaryEnv": "SCRAPE_CREATORS_API_KEY",
      "install": [
        {
          "id": "uv-brew",
          "kind": "brew",
          "formula": "uv",
          "bins": ["uv"],
          "label": "Install uv (brew)"
        }
      ]
    }
  }
---

# Content Research Skill

This skill provides agents with the ability to gather raw intelligence on social media performance (TikTok and Instagram) using the ScrapeCreators API. It does not generate content or interact with posting APIs.

## Prerequisites
- `uv` installed
- `SCRAPE_CREATORS_API_KEY` set in the environment

## Capabilities

### 1. Broad Content Discovery (Keywords & Hashtags)
Use this to find top-performing hooks for a specific niche or topic. It returns the top 5 most viral videos/reels and their captions.

```bash
uv run {baseDir}/scripts/keyword-search.py --platform tiktok --type keyword --query "dinner recipes"
uv run {baseDir}/scripts/keyword-search.py --platform instagram --type keyword --query "dinner recipes"
```

### 2. Competitor Hook Research
Use this to analyze specific competitor handles. It returns their follower counts, average views, and their 3 most viral hooks.

```bash
uv run {baseDir}/scripts/competitor-research.py --platform tiktok --handles user1 user2 user3
uv run {baseDir}/scripts/competitor-research.py --platform instagram --handles user1 user2
```

### 3. Profile Lookup
Use this to get raw metric data (followers, following, bio) for a specific creator.

```bash
uv run {baseDir}/scripts/profile-lookup.py --platform tiktok --handle <handle>
uv run {baseDir}/scripts/profile-lookup.py --platform instagram --handle <handle>
```
