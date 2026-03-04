---
name: pt-site
description: Search and download torrents from NexusPHP-based PT sites, then add to qBittorrent. Use when user wants to search a specific PT site, download torrent, or find seeds on a private tracker.
---

# PT Site - NexusPHP Torrent Search & Download

Search torrents on NexusPHP-based private trackers, download .torrent files, and add them to qBittorrent.

## Setup

Credentials: `~/.clawdbot/credentials/pt-site/sites.json`

```json
{
  "sites": {
    "mySite": {
      "url": "https://pt.example.com",
      "cookie": "c_secure_uid=xxx; c_secure_pass=xxx"
    }
  }
}
```

## Usage

### 1. Search Torrents

```bash
# Search using browser or web_fetch
browser action=open targetUrl="https://pt.example.com/torrents.php?search=keyword&search_type=0"
```

Or use the site's search API if available.

### 2. Parse Results

NexusPHP torrent pages typically have:
- Table with class `torrents`
- Columns: `#`, `Type`, `Title`, `Download`, `Size`, `Seeders`, `Leechers`, `Complete`
- Download link: `download.php?id=<id>` or `download.php?id=<id>&passkey=<passkey>`

Extract:
- Torrent ID
- Download URL (may need passkey)
- Title, size, seeders/leechers

### 3. Download Torrent

```bash
# Download with curl, include Cookie header
curl -L -o /tmp/torrent.torrent "https://pt.example.com/download.php?id=123" \
  -H "Cookie: c_secure_uid=xxx; c_secure_pass=xxx"
```

### 4. Add to qBittorrent

Use qbittorrent skill:

```bash
# Add downloaded torrent
./scripts/qbit-api.sh add-file /tmp/torrent.torrent --category "PT"
```

Or by magnet/URL:
```bash
./scripts/qbit-api.sh add "magnet:?xt=..." --category "PT"
```

## Workflow

1. **Ask user** which PT site and search term
2. **Load credentials** from `sites.json`
3. **Search** via browser or direct URL
4. **Present results** (title, size, seeds, leeches)
5. **User selects** which torrent to download
6. **Download** .torrent file
7. **Add to qBittorrent** using qbittorrent skill

## Notes

- Many NexusPHP sites require passkey for download - may need to extract from user's profile
- Respect site rules - don't spam requests
- Store torrents in `/tmp/` with unique names to avoid conflicts