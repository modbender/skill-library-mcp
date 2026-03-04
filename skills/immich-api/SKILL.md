---
name: immich-api
description: |
  Immich Photo Management API Bridge. Use for interacting with self-hosted Immich instances via REST API.
  Triggers when: (1) User wants to manage photos, albums, or assets in Immich, (2) Building automation around photo backups, 
  (3) Searching or organizing media, (4) User management in Immich, (5) Upload/download photos via API, 
  (6) Getting album or library information, (7) Working with Immich jobs/queues, (8) Any Immich-related photo tasks
---

# Immich API Bridge

## Configuration

### Option 1: Environment Variables

**Windows (PowerShell):**
```powershell
$env:IMMICH_URL = "https://your-immich-instance.com"
$env:IMMICH_API_KEY = "your-api-key-here"
```

**Linux/macOS (bash):**
```bash
export IMMICH_URL="https://your-immich-instance.com"
export IMMICH_API_KEY="your-api-key-here"
```

**Generate API Key in Immich:** User Profile → API Keys → Create API Key

### Option 2: CLI Arguments
```bash
python scripts/upload_photos.py --url "https://your-immich.com" --api-key "your-key" --folder ./photos
python scripts/download_album.py --url "https://your-immich.com" --api-key "your-key" --album-id "abc123" --output ./downloads
```

## Quick Start

### Authentication
```bash
# Test connection
curl -H "x-api-key: $IMMICH_API_KEY" "$IMMICH_URL/api/server-info/ping"
```

### Base URL
```
{IMMICH_URL}/api
```

## Common Operations

### Albums
```bash
# List albums
curl -H "x-api-key: $IMMICH_API_KEY" "$IMMICH_URL/api/albums"

# Create album
curl -X POST -H "x-api-key: $IMMICH_API_KEY" -H "Content-Type: application/json" \
  -d '{"albumName":"My Album"}' "$IMMICH_URL/api/albums"

# Get album assets
curl -H "x-api-key: $IMMICH_API_KEY" "$IMMICH_URL/api/albums/{albumId}"
```

### Assets
```bash
# Get all assets (paginated)
curl -H "x-api-key: $IMMICH_API_KEY" "$IMMICH_URL/api/assets?limit=100"

# Upload asset
curl -X POST -H "x-api-key: $IMMICH_API_KEY" \
  -F "file=@/path/to/photo.jpg" \
  "$IMMICH_URL/api/assets"

# Get thumbnail
curl -H "x-api-key: $IMMICH_API_KEY" \
  "$IMMICH_URL/api/assets/{assetId}/thumbnail?format=jpeg" -o thumb.jpg

# Get original file
curl -H "x-api-key: $IMMICH_API_KEY" \
  "$IMMICH_URL/api/assets/{assetId}/original" -o original.jpg
```

### Users
```bash
# List users
curl -H "x-api-key: $IMMICH_API_KEY" "$IMMICH_URL/api/users"

# Get current user
curl -H "x-api-key: $IMMICH_API_KEY" "$IMMICH_URL/api/user/me"
```

### Search
```bash
# Search assets
curl -X POST -H "x-api-key: $IMMICH_API_KEY" -H "Content-Type: application/json" \
  -d '{"query":"beach","take":10}' "$IMMICH_URL/api/search/assets"
```

### Libraries
```bash
# List libraries
curl -H "x-api-key: $IMMICH_API_KEY" "$IMMICH_URL/api/libraries"

# Scan library
curl -X POST -H "x-api-key: $IMMICH_API_KEY" \
  "$IMMICH_URL/api/libraries/{libraryId}/scan"
```

### Jobs
```bash
# Get job statuses
curl -H "x-api-key: $IMMICH_API_KEY" "$IMMICH_URL/api/jobs"

# Trigger job (e.g., thumbnail generation)
curl -X POST -H "x-api-key: $IMMICH_API_KEY" -H "Content-Type: application/json" \
  -d '{"jobName":"thumbnail-generation","force":true}' "$IMMICH_URL/api/jobs"
```

## Script Usage

Use the bundled scripts in `scripts/` for complex operations:
- `upload_photos.py` - Bulk upload photos
- `download_album.py` - Download entire album
- `sync_library.py` - Sync external library

See `references/api-endpoints.md` for complete endpoint reference.
