# Zotero Web API (concise reference)

- Base URL patterns:
  - User library: https://api.zotero.org/users/<userID>/...
  - Group library: https://api.zotero.org/groups/<groupID>/...

- Common endpoints used:
  - /items — list or create items
  - /items/<itemKey> — get or modify a single item
  - /items/<itemKey>/children — upload attachments (children)
  - /collections — list collections
  - /groups — list groups available to the key

- Authentication: include 'Zotero-API-Key' header with the developer key or use query param zotero_api_key (header preferred).

- Rate limits: follow standard Zotero API rate limits; on 429 responses, implement exponential backoff.

- Notes on updates: Zotero update APIs expect complete item data for updates; typical pattern: fetch item, modify 'data' fields, then PUT update.

- Attachment upload: use multipart/form-data to POST the file to the children endpoint; then update relationships if needed.

- Error handling: return HTTP codes and JSON error body. Common codes: 400 (bad request), 401 (unauthorized), 403 (forbidden), 404 (not found), 429 (rate limited), 500 (server error).
