# Media Downloader Skill for OpenClaw

Automatic movie and TV series downloads using Radarr and Sonarr.

## Overview

This skill integrates [Radarr](https://radarr.video/) (movies) and [Sonarr](https://sonarr.tv/) (TV series) with OpenClaw, allowing you to download content using natural language commands.

### What It Does

- **Movies:** Search and download movies with quality and language preferences
- **TV Series:** Search and download entire series or specific seasons/episodes
- **Queue Status:** Check what's currently downloading
- **Wanted Lists:** View missing content

### Supported Platforms

- Radarr v3+
- Sonarr v3+
- Jackett (optional, for indexers)
- Any download client supported by Radarr/Sonarr (rtorrent, qBittorrent, Deluge, etc.)

---

## Installation

### 1. Install the Skill

Install via ClawHub or manually:

```bash
# Clone or download the skill
cd /path/to/openclaw/skills
git clone https://github.com/openclaw/skills radarr-sonarr

