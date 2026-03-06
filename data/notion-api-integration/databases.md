# Databases - Notion API

## Query Database

```bash
curl -X POST 'https://api.notion.com/v1/databases/DATABASE_ID/query' \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{"page_size": 100}'
```

### With Filter

```bash
curl -X POST 'https://api.notion.com/v1/databases/DATABASE_ID/query' \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {
      "property": "Status",
      "status": {"equals": "Done"}
    }
  }'
```

### With Sort

```bash
curl -X POST 'https://api.notion.com/v1/databases/DATABASE_ID/query' \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{
    "sorts": [{"property": "Due Date", "direction": "ascending"}]
  }'
```

## Retrieve Database

```bash
curl 'https://api.notion.com/v1/databases/DATABASE_ID' \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28"
```

## Create Database

```bash
curl -X POST 'https://api.notion.com/v1/databases' \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"type": "page_id", "page_id": "PARENT_PAGE_ID"},
    "title": [{"type": "text", "text": {"content": "My Database"}}],
    "properties": {
      "Name": {"title": {}},
      "Status": {"select": {"options": [
        {"name": "To Do", "color": "gray"},
        {"name": "Done", "color": "green"}
      ]}}
    }
  }'
```

## Update Database

```bash
curl -X PATCH 'https://api.notion.com/v1/databases/DATABASE_ID' \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{
    "title": [{"text": {"content": "Updated Name"}}]
  }'
```

## List All Databases

```bash
curl -X POST 'https://api.notion.com/v1/search' \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{"filter": {"value": "database", "property": "object"}}'
```

## Database ID from URL

URL: `https://notion.so/workspace/abc123def456?v=...`
Database ID: `abc123def456` (remove dashes if present)
