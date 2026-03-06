---
name: "blankfiles"
description: "Use blankfiles.com as a binary test-file gateway: discover formats, filter by type/category, and return direct download URLs from the public API."
homepage: "https://blankfiles.com"
metadata: {"openclaw":{"homepage":"https://blankfiles.com","always":true}}
---

# Blank Files Gateway

Use this skill when the user needs real, downloadable blank binary files for upload testing.

Primary API:

- `https://blankfiles.com/api/v1/status`
- `https://blankfiles.com/api/v1/files`
- `https://blankfiles.com/api/v1/files/{type}`
- `https://blankfiles.com/api/v1/files/{category}/{type}`

## Behavior

1. Prefer the API endpoints above to discover current formats.
2. Return direct file URLs from the API response (`files[].url`) whenever possible.
3. If a format is not found, suggest close alternatives from the same category.
4. Keep responses concise and practical: format, category, URL, and one-line use case.

## Guardrails

- Treat this as a read-only gateway. Do not ask users to run shell scripts or installers.
- Do not fabricate file formats or URLs.
- Always verify availability via API before claiming a format exists.
- Use exact API route shapes (`/api/v1/...`), not deprecated routes.

## Quick Recipes

### Find all available formats

Use:

- `GET /api/v1/files`

Return:

- Total count
- Top relevant matches for user intent
- Direct links

### Get one format by type

Use:

- `GET /api/v1/files/{type}`

Return:

- Matching files with direct URLs
- If none, propose neighboring types in same domain

### Get exact category + type

Use:

- `GET /api/v1/files/{category}/{type}`

Return:

- One direct URL when available
- 404-safe fallback suggestions when missing

## Output Template

- `format`: `<type>`
- `category`: `<category>`
- `download_url`: `<url>`
- `notes`: `<short testing context>`

## References

Read:

- `{baseDir}/references/endpoints.md`
- `{baseDir}/references/publish.md`
