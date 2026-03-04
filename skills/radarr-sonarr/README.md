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

# Install dependencies
cd radarr-sonarr
pip install -r requirements.txt
```

### 2. Configure Radarr and Sonarr

#### Radarr Setup

1. Go to **Settings → General**
2. Enable **API Key** and copy it
3. Note your Radarr URL (e.g., `http://localhost:7878`)
4. Configure a **Quality Profile** (e.g., HD-1080p)
5. Set a **Root Folder** for movies (e.g., `/data/movies`)

#### Sonarr Setup

1. Go to **Settings → General**
2. Enable **API Key** and copy it
3. Note your Sonarr URL (e.g., `http://localhost:8989`)
4. Configure a **Quality Profile** (e.g., HD-1080p)
5. Set a **Root Folder** for TV shows (e.g., `/data/tv`)

#### Full Configuration Guide

##### Indexers (Finding Torrents)

**Using Jackett (Recommended):**

1. Install Jackett on your server or use a Docker container
2. In Jackett, add trackers you want to use:
   - Go to **Add Indexer**
   - Select your preferred torrent trackers
   - Configure API key access
3. In Radarr/Sonarr:
   - Go to **Settings → Indexers**
   - Click **Add Indexer**
   - Select **Torznab** (for Jackett)
   - URL: `http://your-jackett-server:9117/api/v2.0/indexers/your-indexer/results/torznab/`
   - API Key: Your Jackett API key (found in Jackett settings)
   - Click **Test** to verify

**Supported Indexers via Jackett:**
- Yggtorrent (French)
- RARBG (International)
- ThePirateBay
- KickassTorrents
- And 100+ more...

**Minimum Seeders:**
- Recommended: 10+ seeders for faster downloads
- Configure in Radarr/Sonarr → Indexers → Your Indexer → Minimum Seeders

##### Download Clients (Getting the Files)

**Common Download Clients:**

| Client | Protocol | Notes |
|--------|----------|-------|
| rtorrent | rTorrent | Popular on seedboxes |
| qBittorrent | qBittorrent | Cross-platform |
| Deluge | Deluge | Lightweight |
| Transmission | HTTP | macOS/Linux |
| SABnzbd | NZB | For usenet (not torrents) |

**Setup Steps:**

1. Go to **Settings → Download Clients**
2. Click **Add Client**
3. Select your client type
4. Configure:
   - **Host:** Server address (e.g., `localhost` or seedbox IP)
   - **Port:** Client port (e.g., 5000 for qBittorrent)
   - **Username/Password:** If required
   - **Category/Label:** Optional (e.g., `radarr` or `sonarr`)
5. Click **Test** to verify connection

**Example qBittorrent Setup:**
```
Host: localhost
Port: 8080
Username: admin
Password: yourpassword
Category: radarr
```

##### Media Management (File Organization)

**Root Folders:**

Configure where downloaded files are stored:

**Radarr:**
```
Root Folder: /data/movies
         or /mnt/storage/movies
```

**Sonarr:**
```
Root Folder: /data/tv
         or /mnt/storage/TV Shows
```

**Folder Naming:**
```
{r Movie Title} ({Release Year})/
    └── {Movie Title}.mp4
```

**Recommended Settings:**
- **Rename Movies/Episodes:** Enable
- **Replace Illegal Characters:** Replace
- **Colon (:) Replacement:** Replace with space or dash
- **Standard Movie Format:** `{Movie Title} ({Year})/{Movie Title} ({Year})`
- **TV Show Format:** `{Show Title}/Season {season}/{Show Title} - S{season:00}E{episode:00}`

##### Quality Profiles

Create quality profiles based on your storage and bandwidth:

| Profile | Max Size | Use Case |
|---------|----------|----------|
| SD | 4GB | Low storage |
| HD-720p | 6GB | Balanced |
| HD-1080p | 10GB | HD streaming |
| UHD-4K | 25GB | 4K quality |
| Any | No limit | Maximum quality |

**Recommended Settings:**
- **Minimum Age:** 0 minutes (get immediately)
- **Preferred Score:** Positive for preferred quality
- **Language:** Match your preference (English, French, etc.)

### 3. Configure the Skill

Create a `.env` file or set environment variables:

```bash
# Required
RADARR_URL=http://localhost:7878
RADARR_API_KEY=your_radarr_api_key
SONARR_URL=http://localhost:8989
SONARR_API_KEY=your_sonarr_api_key

# Optional (with defaults)
RADARR_ROOT_FOLDER=/data/movies
SONARR_ROOT_FOLDER=/data/tv
RADARR_QUALITY_PROFILE=HD-1080p
SONARR_QUALITY_PROFILE=HD-1080p
RADARR_LANGUAGE_PROFILE=English
SONARR_LANGUAGE_PROFILE=English
```

Or use the included `.env.example` template:

```bash
cp .env.example .env
# Edit .env with your values
```

---

## Usage

### Natural Language Commands

Send these commands to your OpenClaw bot:

#### Movies

| Command | Description |
|---------|-------------|
| `Download Inception in 4K English` | Download Inception in 4K with English audio |
| `Download Dune in 1080p` | Download Dune in 1080p |
| `Add Matrix in HD` | Add Matrix in HD quality |
| `Search for Avatar` | Search for Avatar without downloading |

#### TV Series

| Command | Description |
|---------|-------------|
| `Download Supernatural season 4` | Download all of Supernatural Season 4 |
| `Add Breaking Bad season 1 episode 3` | Download a specific episode |
| `Find Stranger Things in 4K` | Search for Stranger Things in 4K |
| `Download The Office` | Download all available episodes |

#### Status Commands

| Command | Description |
|---------|-------------|
| `Radarr status` | Show Radarr download queue |
| `Sonarr status` | Show Sonarr download queue |
| `Downloads` | Show all download queues |
| `Radarr wanted` | Show missing/wanted movies |
| `Sonarr wanted` | Show missing/wanted episodes |

### Command-Line Interface

The skill also includes a CLI for terminal use:

```bash
# Auto-parse natural language
python scripts/cli.py auto "Download Inception in 4K"

# Radarr commands
python scripts/cli.py radarr search "Inception"
python scripts/cli.py radarr download 12345
python scripts/cli.py radarr queue
python scripts/cli.py radarr wanted
python scripts/cli.py radarr status

# Sonarr commands
python scripts/cli.py sonarr search "Supernatural"
python scripts/cli.py sonarr download 12345
python scripts/cli.py sonarr season 12345 4
python scripts/cli.py sonarr queue
python scripts/cli.py sonarr wanted
python scripts/cli.py sonarr status
```

---

## Quality Profiles

Recognized quality keywords:

| Keyword | Quality |
|---------|---------|
| `4K`, `UHD`, `Ultra`, `2160p` | 4K Ultra HD |
| `1080p`, `HD 1080p`, `Full HD` | 1080p HD |
| `720p`, `HD 720p`, `HD` | 720p HD |
| `480p`, `SD` | SD |

Default: **1080p**

---

## Language Profiles

Recognized language keywords:

| Keyword | Language |
|---------|----------|
| `English`, `EN`, `ENG`, `VO` | English |
| `French`, `FR`, `FRA`, `VF` | French |
| `Spanish`, `ES`, `ESP` | Spanish |
| `German`, `DE`, `GER` | German |
| `Multi`, `Multilingual` | Multiple languages |

Default: **English**

---

## Troubleshooting

### Connection Errors

**"Radarr is not configured"**
- Check `RADARR_URL` and `RADARR_API_KEY` environment variables
- Verify Radarr is running and accessible
- Ensure no firewall blocking the connection

**"API error"**
- Verify API key is correct
- Check Radarr/Sonarr logs for details
- Ensure API access is enabled in settings

### Download Not Starting

1. Check indexers are configured in Radarr/Sonarr
2. Verify minimum seeders requirements
3. Check quality profile settings
4. Look for restrictions in indexer configuration

### Quality Not Matching

- Quality profiles must exist in Radarr/Sonarr
- The skill uses default quality profile if not specified
- Check quality profile names match exactly

---

## Plex, Seedbox & Media Server Integration

### Seedbox Setup (Recommended)

A seedbox provides fast downloads and acts as a private tracker gateway.

**Popular Seedbox Providers:**

| Provider | Features | Link |
|----------|----------|------|
| Ultra.cc | 1-click apps, Plex included | https://ultra.cc |
| Seedboxes.cc | Affordable, Docker support | https://seedboxes.cc |
| Hetzner | Dedicated servers, self-hosted | https://hetzner.de |
| OVH | French provider, dedicated servers | https://ovh.com |

**Ultra.cc 1-Click Installation:**

1. Order a seedbox with apps
2. Install from the dashboard:
   - **Radarr**
   - **Sonarr**
   - **Jackett**
   - **Plex** (optional)
   - **rtorrent** or **qBittorrent**

3. Configure each app to connect to your download client

**Seedbox Configuration:**

```bash
# URLs for Ultra.cc style setup
RADARR_URL=https://your-username.apex.usbx.me/radarr
SONARR_URL=https://your-username.apex.usbx.me/sonarr
JACKETT_URL=https://your-username.apex.usbx.me/jackett
```

### Plex Integration

**Automatic Library Updates:**

1. Go to **Radarr → Settings → Connect**
2. Click **Add Connection**
3. Select **Plex Media Server**
4. Configure:
   - **Plex URL:** `http://localhost:32400` (local) or remote URL
   - **Plex Token:** Find in Plex settings → Account → Public API tokens
   - **Update Library:** Enable
   - **Click Finish** to save

**Sonarr Plex Setup:**

1. Go to **Sonarr → Settings → Connect**
2. Add **Plex Media Server**
3. Configure the same as Radarr

**Manual Library Scan:**

If automatic updates don't work:

```bash
# Via CLI on Plex server
curl -X POST http://localhost:32400/library/sections/all/refresh
```

**Plex Path Mapping:**

If Radarr/Sonarr run on a different machine than Plex:

1. Go to **Radarr → Settings → Media Management**
2. Click **Add Path Mapping**
3. Add:
   - **Remote Path:** `/home/your-username/downloads/`
   - **Local Path:** `/mnt/plex/media/`

### Complete Docker Stack Example

```yaml
version: '3.8'
services:
  radarr:
    image: lscr.io/linuxserver/radarr:latest
    container_name: radarr
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Europe/Paris
    volumes:
      - ./config/radarr:/config
      - /mnt/storage:/mnt/storage
    ports:
      - "7878:7878"
    restart: unless-stopped

  sonarr:
    image: lscr.io/linuxserver/sonarr:latest
    container_name: sonarr
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Europe/Paris
    volumes:
      - ./config/sonarr:/config
      - /mnt/storage:/mnt/storage
    ports:
      - "8989:8989"
    restart: unless-stopped

  jackett:
    image: lscr.io/linuxserver/jackett:latest
    container_name: jackett
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Europe/Paris
      - AUTO_UPDATE=true
    volumes:
      - ./config/jackett:/config
      - /mnt/downloads:/downloads
    ports:
      - "9117:9117"
    restart: unless-stopped

  qbittorrent:
    image: lscr.io/linuxserver/qbittorrent:latest
    container_name: qbittorrent
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Europe/Paris
      - WEBUI_PORT=8080
    volumes:
      - ./config/qbittorrent:/config
      - /mnt/downloads:/downloads
    ports:
      - "8080:8080"
      - "6881:6881"
      - "6881:6881/udp"
    restart: unless-stopped

  plex:
    image: lscr.io/linuxserver/plex:latest
    container_name: plex
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Europe/Paris
      - VERSION=docker
    volumes:
      - ./config/plex:/config
      - /mnt/storage:/data
    ports:
      - "32400:32400"
    restart: unless-stopped
```

---

## Advanced Configuration

### Custom Quality Profiles

If you use custom quality profile names, set them explicitly:

```bash
RADARR_QUALITY_PROFILE=My Custom Profile
SONARR_QUALITY_PROFILE=My Custom Profile
```

### Custom Root Folders

```bash
RADARR_ROOT_FOLDER=/mnt/storage/movies
SONARR_ROOT_FOLDER=/mnt/storage/tv
```

### Docker Environments

For Docker installations:

```bash
RADARR_URL=http://radarr:7878
SONARR_URL=http://sonarr:8989
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   OPENCLAW (User Input)                         │
│  "Download Inception in 4K English"                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 RADARR-SONARR SKILL                            │
│  • Natural language parser                                     │
│  • Radarr API client                                           │
│  • Sonarr API client                                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    YOUR AUTOMATION SERVER                       │
│  • Radarr (movies)                                             │
│  • Sonarr (TV)                                                │
│  • Jackett (indexers)                                         │
│  • Download client                                            │
│  • Plex/Emby/Jellyfin                                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## File Structure

```
radarr-sonarr/
├── SKILL.md              # OpenClaw skill metadata
├── README.md             # This file
├── CONFIG.md             # Configuration guide
├── .env.example          # Environment template
├── requirements.txt      # Python dependencies
└── scripts/
    ├── __init__.py
    ├── radarr.py         # Radarr API wrapper
    ├── sonarr.py         # Sonarr API wrapper
    ├── parser.py         # Natural language parser
    ├── cli.py            # Command-line interface
    └── openclaw.py       # OpenClaw integration
```

---

## Contributing

Contributions welcome! Areas for improvement:

- Additional indexers beyond Jackett
- More language mappings
- Better error handling
- Docker support documentation
- Tests

---

## License

MIT License - See LICENSE file for details.

---

**Last Updated:** 2026-02-07
