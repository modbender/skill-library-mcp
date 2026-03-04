# Download Clients

Torrent and usenet download clients commonly used with TrueNAS homelab setups.

## Environment Variables

```
QBITTORRENT_URL                      — qBittorrent web UI (typically no auth)
SABNZBD_URL, SABNZBD_API_KEY         — SABnzbd usenet client
FLARESOLVERR_URL                     — Captcha solving proxy (no auth)
```

## qBittorrent

```bash
# All torrents
curl -s "$QBITTORRENT_URL/api/v2/torrents/info"

# Active torrents only
curl -s "$QBITTORRENT_URL/api/v2/torrents/info?filter=active" \
  | jq '.[] | {name, progress, state}'

# Pause all
curl -s "$QBITTORRENT_URL/api/v2/torrents/pause?hashes=all"

# Resume all
curl -s "$QBITTORRENT_URL/api/v2/torrents/resume?hashes=all"

# Add magnet link
curl -X POST "$QBITTORRENT_URL/api/v2/torrents/add" -d "urls=MAGNET_LINK"
```

## SABnzbd

```bash
# Queue
curl -s "$SABNZBD_URL/api?mode=queue&output=json&apikey=$SABNZBD_API_KEY"

# History
curl -s "$SABNZBD_URL/api?mode=history&output=json&apikey=$SABNZBD_API_KEY"

# Pause
curl -s "$SABNZBD_URL/api?mode=pause&apikey=$SABNZBD_API_KEY"

# Resume
curl -s "$SABNZBD_URL/api?mode=resume&apikey=$SABNZBD_API_KEY"
```

## FlareSolverr

Captcha-solving proxy used by Prowlarr and other indexer tools.

```bash
# Health check
curl -s "$FLARESOLVERR_URL/health"

# Solve captcha
curl -X POST "$FLARESOLVERR_URL/v1" -H "Content-Type: application/json" \
  -d '{"cmd": "request.get", "url": "https://example.com", "maxTimeout": 60000}'
```

## Common Agent Tasks

### "What's downloading?"

```bash
# Torrents
curl -s "$QBITTORRENT_URL/api/v2/torrents/info?filter=active" \
  | jq '.[] | {name, progress, state}'

# Usenet
curl -s "$SABNZBD_URL/api?mode=queue&output=json&apikey=$SABNZBD_API_KEY" \
  | jq '.queue.slots'
```

### "Pause/resume all downloads"

Use the pause/resume endpoints above for both clients.
