# Pages - Notion API

## Retrieve Page

```bash
curl 'https://api.notion.com/v1/pages/PAGE_ID' \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28"
```

## Create Page in Database

```bash
curl -X POST 'https://api.notion.com/v1/pages' \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "DATABASE_ID"},
    "properties": {
      "Name": {"title": [{"text": {"content": "New Task"}}]},
      "Status": {"select": {"name": "To Do"}}
    }
  }'
```

## Create Page under Page

```bash
curl -X POST 'https://api.notion.com/v1/pages' \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"page_id": "PARENT_PAGE_ID"},
    "properties": {
      "title": {"title": [{"text": {"content": "Subpage Title"}}]}
    },
    "children": [
      {"object": "block", "type": "paragraph", "paragraph": {
        "rich_text": [{"type": "text", "text": {"content": "Page content."}}]
      }}
    ]
  }'
```

## Update Page Properties

```bash
curl -X PATCH 'https://api.notion.com/v1/pages/PAGE_ID' \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{"properties": {"Status": {"select": {"name": "Done"}}}}'
```

## Archive Page

```bash
curl -X PATCH 'https://api.notion.com/v1/pages/PAGE_ID' \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{"archived": true}'
```

## Set Page Icon and Cover

```bash
curl -X PATCH 'https://api.notion.com/v1/pages/PAGE_ID' \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{
    "icon": {"type": "emoji", "emoji": "🚀"},
    "cover": {"type": "external", "external": {"url": "https://example.com/image.jpg"}}
  }'
```

## Page ID from URL

URL: `https://notion.so/Page-Title-abc123def456`
Page ID: `abc123def456` (last part, remove dashes)
