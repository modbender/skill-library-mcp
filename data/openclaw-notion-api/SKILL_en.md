---
name: openclaw-notion-api
description: Notion API for creating and managing pages, databases, and blocks. Includes image upload functionality with corrected API parameters.
homepage: https://developers.notion.com
author: ionepub
metadata: {"clawdbot":{"emoji":"📝"}}
---

# openclaw-notion-api

Use the Notion API to create/read/update pages, data sources (databases), and blocks.

## Setup

1. Create an integration at https://notion.so/my-integrations
2. Copy the API key (starts with `ntn_` or `secret_`)
3. Store it:
```bash
mkdir -p ~/.config/notion
echo "ntn_your_key_here" > ~/.config/notion/api_key
```
4. Share target pages/databases with your integration (click "..." → "Connect to" → your integration name)

## API Basics

All requests need:
```bash
NOTION_KEY=$(cat ~/.config/notion/api_key)
curl -X GET "https://api.notion.com/v1/..." \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json"
```

> **Note:** The `Notion-Version` header is required. This skill uses `2025-09-03` (latest). In this version, databases are called "data sources" in the API.

## Common Operations

**Search for pages and data sources:**
```bash
curl -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"query": "page title"}'
```

**Get page:**
```bash
curl "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03"
```

**Get page content (blocks):**
```bash
curl "https://api.notion.com/v1/blocks/{page_id}/children" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03"
```

**Create page in a data source:**
```bash
curl -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "xxx"},
    "properties": {
      "Name": {"title": [{"text": {"content": "New Item"}}]},
      "Status": {"select": {"name": "Todo"}}
    }
  }'
```

**Query a data source (database):**
```bash
curl -X POST "https://api.notion.com/v1/data_sources/{data_source_id}/query" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {"property": "Status", "select": {"equals": "Active"}},
    "sorts": [{"property": "Date", "direction": "descending"}]
  }'
```

**Create a data source (database):**
```bash
curl -X POST "https://api.notion.com/v1/data_sources" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"page_id": "xxx"},
    "title": [{"text": {"content": "My Database"}}],
    "properties": {
      "Name": {"title": {}},
      "Status": {"select": {"options": [{"name": "Todo"}, {"name": "Done"}]}},
      "Date": {"date": {}}
    }
  }'
```

**Update page properties:**
```bash
curl -X PATCH "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"properties": {"Status": {"select": {"name": "Done"}}}}'
```

**Add blocks to page:**
```bash
curl -X PATCH "https://api.notion.com/v1/blocks/{page_id}/children" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "children": [
      {"type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Hello"}}]}}
    ]
  }'
```

## Property Types

Common property formats for database items:
- **Title:** `{"title": [{"text": {"content": "..."}}]}`
- **Rich text:** `{"rich_text": [{"text": {"content": "..."}}]}`
- **Select:** `{"select": {"name": "Option"}}`
- **Multi-select:** `{"multi_select": [{"name": "A"}, {"name": "B"}]}`
- **Date:** `{"date": {"start": "2024-01-15", "end": "2024-01-16"}}`
- **Checkbox:** `{"checkbox": true}`
- **Number:** `{"number": 42}`
- **URL:** `{"url": "https://..."}`
- **Email:** `{"email": "a@b.com"}`
- **Relation:** `{"relation": [{"id": "page_id"}]}`

## Key Differences in 2025-09-03

- **Databases → Data Sources:** Use `/data_sources/` endpoints for queries and retrieval
- **Two IDs:** Each database now has both a `database_id` and a `data_source_id`
  - Use `database_id` when creating pages (`parent: {"database_id": "..."}`)
  - Use `data_source_id` when querying (`POST /v1/data_sources/{id}/query`)
- **Search results:** Databases return as `"object": "data_source"` with their `data_source_id`
- **Parent in responses:** Pages show `parent.data_source_id` alongside `parent.database_id`
- **Finding the data_source_id:** Search for the database, or call `GET /v1/data_sources/{data_source_id}`

## File Upload

Upload images or files to Notion using the Direct Upload method (files up to 20MB). The steps are identical for both, with only the block type differing in Step 3.

### Step 1: Create File Upload Object

Create an upload object to get the upload URL:
```bash
curl --request POST \
  --url 'https://api.notion.com/v1/file_uploads' \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H 'Content-Type: application/json' \
  -H 'Notion-Version: 2025-09-03' \
  --data '{}'
```

Response includes:
- `id`: File upload ID (used in step 3)
- `upload_url`: URL for uploading the file content

### Step 2: Upload File Content

Upload the actual file using multipart/form-data:
```bash
curl --request POST \
  --url 'https://api.notion.com/v1/file_uploads/{file_upload_id}/send' \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H 'Notion-Version: 2025-09-03' \
  -H 'Content-Type: multipart/form-data' \
  -F "file=@/path/to/file.png"
```

**Important:**
- Use `POST` method (not PUT)
- Include `Authorization` and `Notion-Version` headers
- Use `-F` for multipart/form-data
- File size must be ≤ 20MB

### Step 3: Insert into Page

Add the uploaded file as a block. Choose the appropriate block type based on the file type:

**Upload image:**
```bash
curl --request PATCH \
  --url "https://api.notion.com/v1/blocks/{page_id}/children" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H 'Content-Type: application/json' \
  -H 'Notion-Version: 2025-09-03' \
  --data '{
    "children": [
      {
        "type": "image",
        "image": {
          "type": "file_upload",
          "file_upload": {
            "id": "{file_upload_id}"
          }
        }
      }
    ]
  }'
```

**Upload file:**
```bash
curl --request PATCH \
  --url "https://api.notion.com/v1/blocks/{page_id}/children" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H 'Content-Type: application/json' \
  -H 'Notion-Version: 2025-09-03' \
  --data '{
    "children": [
      {
        "type": "file",
        "file": {
          "type": "file_upload",
          "file_upload": {
            "id": "{file_upload_id}"
          }
        }
      }
    ]
  }'
```

**Note:** Do not include `"object": "block"` in the block definition.

### Common Errors

- **invalid_request_url**: Check that you're using `POST` method and the correct URL format
- **unauthorized**: Ensure `Authorization` and `Notion-Version` headers are present in step 2
- **validation_error**: File must be uploaded (step 2) before attaching (step 3)

## Notes

- Page/database IDs are UUIDs (with or without dashes)
- The API cannot set database view filters — that's UI-only
- Rate limit: ~3 requests/second average
- Use `is_inline: true` when creating data sources to embed them in pages
