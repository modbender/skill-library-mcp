---
name: notion-2025
description: "Query, create, and manage Notion databases and pages using the 2025-09-03 API format. Use when: (1) querying or filtering database entries via data_source_id, (2) creating new database items, (3) updating page properties, (4) adding content blocks to pages. Requires NOTION_API_KEY in secrets/notion_api_key.txt."
metadata:
  {
    "openclaw":
      {
        "requires": {
          "bins": ["curl", "jq"],
          "env": ["NOTION_API_KEY_PATH=~/.openclaw/workspace/secrets/notion_api_key.txt"]
        },
        "primaryEnv": "NOTION_API_KEY_PATH"
      }
  }
---

# Notion 2025 API Skill

This skill provides utilities for working with Notion databases and pages using the **2025-09-03 API format**, which separates `database_id` (for creating pages) from `data_source_id` (for querying entries).

## Quick Reference

**Key Difference (2025-09-03):**
- `database_id` → Use when creating NEW pages in a database
- `data_source_id` → Use when QUERYING existing entries in a database

## Common Operations

### 1. Query a Database

```bash
NOTION_KEY=$(cat ~/.openclaw/workspace/secrets/notion_api_key.txt)
DATA_SOURCE_ID="YOUR_DATA_SOURCE_ID"

curl -s -X POST "https://api.notion.com/v1/data_sources/$DATA_SOURCE_ID/query" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {"property": "Status", "select": {"equals": "Active"}},
    "sorts": [{"property": "Last Updated", "direction": "descending"}]
  }' | jq '.results[]'
```

### 2. Create a Database Entry

```bash
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "YOUR_DATABASE_ID"},
    "properties": {
      "Name": {"title": [{"text": {"content": "Entry Name"}}]},
      "Status": {"select": {"name": "Active"}},
      "Count": {"number": 42}
    }
  }' | jq '.id'
```

### 3. Update a Page

```bash
ENTRY_ID="YOUR_ENTRY_ID"

curl -s -X PATCH "https://api.notion.com/v1/pages/$ENTRY_ID" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "Status": {"select": {"name": "Complete"}},
      "Description": {"rich_text": [{"text": {"content": "Updated content"}}]}
    }
  }' | jq '.properties'
```

### 4. Add Content Blocks to a Page

```bash
PAGE_ID="YOUR_PAGE_ID"

curl -s -X PATCH "https://api.notion.com/v1/blocks/$PAGE_ID/children" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "children": [
      {
        "object": "block",
        "type": "heading_2",
        "heading_2": {"rich_text": [{"text": {"content": "Section Title"}}]}
      },
      {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": [{"text": {"content": "Paragraph content"}}]}
      }
    ]
  }' | jq '.object'
```

## Property Types (2025-09-03)

When updating or creating entries, use these property formats:

| Type | Format | Example |
|------|--------|---------|
| **Title** | `{"title": [{"text": {"content": "..."}}]}` | `{"title": [{"text": {"content": "My Title"}}]}` |
| **Rich Text** | `{"rich_text": [{"text": {"content": "..."}}]}` | `{"rich_text": [{"text": {"content": "Body text"}}]}` |
| **Select** | `{"select": {"name": "Option"}}` | `{"select": {"name": "Active"}}` |
| **Number** | `{"number": VALUE}` | `{"number": 42}` |
| **Date** | `{"date": {"start": "YYYY-MM-DD"}}` | `{"date": {"start": "2026-03-03"}}` |
| **Checkbox** | `{"checkbox": true/false}` | `{"checkbox": true}` |
| **URL** | `{"url": "https://..."}` | `{"url": "https://example.com"}` |
| **Status** | `{"status": {"name": "..."}}` | `{"status": {"name": "Active"}}` |

## Filter Syntax (for queries)

```json
{
  "filter": {
    "and": [
      {"property": "Status", "select": {"equals": "Active"}},
      {"property": "Count", "number": {"greater_than": 5}}
    ]
  }
}
```

Common filters:
- `{"select": {"equals": "Value"}}`
- `{"number": {"greater_than": N}}`
- `{"date": {"on_or_after": "2026-01-01"}}`
- `{"rich_text": {"contains": "keyword"}}`

## Bundled References

- **[API_REFERENCE.md](references/API_REFERENCE.md)** — Complete endpoint documentation and property types
- **[EXAMPLES.md](references/EXAMPLES.md)** — Real-world examples and use cases

## Setup

1. Create integration at https://notion.so/my-integrations
2. Copy API key
3. Store in `~/.openclaw/workspace/secrets/notion_api_key.txt`
4. Share target Notion pages/databases with your integration (Invite → select integration)

## Security & Safety

### Credentials
- **API Key Storage:** Stored in `~/.openclaw/workspace/secrets/notion_api_key.txt`
- **Scope:** Notion API access only (limited to Notion endpoints)
- **No Elevation:** This skill does not request elevated permissions
- **Key Rotation:** If key is compromised, revoke at https://notion.so/my-integrations

### Input Validation ⚠️
**IMPORTANT:** The helper script uses JSON string concatenation. Only use with:
- Trusted input (your own data)
- IDs from Notion (database_id, page_id, data_source_id)
- Known property names from your Notion schema

❌ **DO NOT** pass untrusted user input directly to the script:
```bash
# UNSAFE - if user_input contains special chars/quotes
./notion_helper.sh create "$db_id" "$user_input"
```

✅ **SAFE** - Use proper escaping or JSON libraries:
```bash
# SAFE - properly escaped
title=$(echo "$user_input" | jq -Rs '.')
./notion_helper.sh create "$db_id" "$title"
```

### External Dependencies
- **curl** — HTTP requests to Notion API
- **jq** — JSON parsing and formatting
- **date** — Date calculations (macOS/Linux)

All are standard utilities; verify they're available before use.

## Important Notes

- **API Version:** Always use `Notion-Version: 2025-09-03`
- **IDs:** database_id and data_source_id are different—use the correct one for your operation
- **Permissions:** Integration must be invited to pages/databases via Notion UI
- **Rate limit:** ~3 requests/second average
- **Untrusted Input:** Never pass unsanitized user input to JSON construction
