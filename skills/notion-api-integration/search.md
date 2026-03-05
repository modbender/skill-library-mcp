# Search and Users - Notion API

## Search

```bash
curl -X POST 'https://api.notion.com/v1/search' \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{"query": "search term"}'
```

### Filter by Type

Pages only:
```json
{"query": "meeting", "filter": {"value": "page", "property": "object"}}
```

Databases only:
```json
{"filter": {"value": "database", "property": "object"}}
```

### Sort Results
```json
{"query": "project", "sort": {"direction": "descending", "timestamp": "last_edited_time"}}
```

### List All (Empty Query)
```json
{"query": "", "page_size": 100}
```

## Users

### List All Users
```bash
curl 'https://api.notion.com/v1/users' \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28"
```

### Get Current Bot
```bash
curl 'https://api.notion.com/v1/users/me' \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28"
```

### Get Specific User
```bash
curl 'https://api.notion.com/v1/users/USER_ID' \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28"
```

## Comments

### List Comments
```bash
curl 'https://api.notion.com/v1/comments?block_id=PAGE_ID' \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28"
```

### Create Comment
```bash
curl -X POST 'https://api.notion.com/v1/comments' \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"page_id": "PAGE_ID"},
    "rich_text": [{"type": "text", "text": {"content": "Comment text"}}]
  }'
```

## Search Tips

- Search is case-insensitive
- Searches page titles and content
- Does not search property values
- Results limited to pages shared with integration
