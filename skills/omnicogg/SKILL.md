---
name: omnicog
description: Universal service integration for OpenClaw — connect Reddit, Steam, Spotify, GitHub, Discord, and more with a single API.
metadata:
  openclaw:
    version: "1.0.0"
    platforms:
      - linux
      - macos
      - windows
    requires:
      env:
        - OMNICOG_REDDIT_CLIENT_ID
        - OMNICOG_REDDIT_CLIENT_SECRET
        - OMNICOG_STEAM_API_KEY
        - OMNICOG_SPOTIFY_CLIENT_ID
        - OMNICOG_SPOTIFY_CLIENT_SECRET
        - OMNICOG_GITHUB_TOKEN
        - OMNICOG_DISCORD_TOKEN
        - OMNICOG_YOUTUBE_API_KEY
    bins: []
    pythonPackages: []
    systemPackages: []
    permissions: []
    categories:
      - integration
      - api
      - social
      - gaming
    tags:
      - reddit
      - steam
      - spotify
      - github
      - discord
      - youtube
      - integration
      - api
    primaryEnv: OMNICOG_REDDIT_CLIENT_ID
  clawdbot:
    nix: null
    config: null
    cliHelp: null
---

# OmniCog — Universal Service Integration for OpenClaw

**One Cog to Integrate Them All.**

Connect Reddit, Steam, Spotify, GitHub, Discord, YouTube, and more with a unified, simple API. No more juggling different authentication methods or rate limits — OmniCog handles it all.

## What is OmniCog?

OmniCog is a universal integration layer that provides a consistent interface across multiple services. Whether you need to:

- 📊 **Monitor Reddit** — Track posts, comments, and subreddit activity
- 🎮 **Integrate Steam** — Get owned games, achievements, and friend status
- 🎵 **Control Spotify** — Play music, manage playlists, and discover new tracks
- 🐙 **Manage GitHub** — Watch repositories, track issues, and automate workflows
- 💬 **Interact with Discord** — Send messages, manage channels, and monitor servers
- 📺 **Search YouTube** — Find videos, get channel stats, and track uploads

**OmniCog unifies them all into one simple API.**

## Quick Start

```python
# Install the package (required)
pip install omnicog

# Import and initialize
from omnicog import OmniClient

client = OmniClient(
    reddit={
        "client_id": "YOUR_REDDIT_CLIENT_ID",
        "client_secret": "YOUR_REDDIT_CLIENT_SECRET",
        "user_agent": "OmniCog/1.0"
    },
    steam={
        "api_key": "YOUR_STEAM_API_KEY"
    },
    spotify={
        "client_id": "YOUR_SPOTIFY_CLIENT_ID",
        "client_secret": "YOUR_SPOTIFY_CLIENT_SECRET"
    }
)

# Use any service with the same simple API
posts = client.reddit.get_hot("programming", limit=10)
games = client.steam.get_owned_games()
track = client.spotify.search_track("metallica")
