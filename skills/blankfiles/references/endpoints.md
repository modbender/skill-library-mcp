# Blank Files API Reference

Base URL: `https://blankfiles.com`

## Health and catalog metadata

- `GET /api/v1/status`
- Returns service status + catalog counts + catalog/cdn source URLs.

## List all files

- `GET /api/v1/files`
- Response shape:

```json
{
  "files": [
    {
      "category": "video",
      "type": "wmv",
      "url": "https://cdn.jsdelivr.net/gh/filearchitect/blank-files@main/files/blank.wmv",
      "package": false
    }
  ],
  "meta": {
    "version": "v1",
    "generated_at": "2026-02-15T21:13:00+00:00",
    "count": 92
  }
}
```

## Filter by type

- `GET /api/v1/files/{type}`
- Example: `/api/v1/files/parquet`

## Exact by category + type

- `GET /api/v1/files/{category}/{type}`
- Example: `/api/v1/files/network/pcapng`

## Notes

- Use links from API (`files[].url`) as canonical download URLs.
- API supports ETag and Last-Modified for efficient polling.
