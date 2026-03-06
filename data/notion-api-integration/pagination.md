# Pagination - Notion API

## Response Structure

```json
{
  "object": "list",
  "results": [...],
  "next_cursor": "abc123",
  "has_more": true
}
```

## Using Pagination

### First Request
```bash
curl -X POST 'https://api.notion.com/v1/databases/DATABASE_ID/query' \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{"page_size": 100}'
```

### Next Page
```bash
curl -X POST 'https://api.notion.com/v1/databases/DATABASE_ID/query' \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{"page_size": 100, "start_cursor": "abc123"}'
```

## Complete Fetch Pattern

### Python
```python
def fetch_all(database_id):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28"
    }
    
    results = []
    cursor = None
    
    while True:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        
        response = requests.post(url, headers=headers, json=body)
        data = response.json()
        
        results.extend(data["results"])
        
        if not data.get("has_more"):
            break
        cursor = data["next_cursor"]
    
    return results
```

### JavaScript
```javascript
async function fetchAll(databaseId) {
  const results = [];
  let cursor = undefined;

  while (true) {
    const response = await fetch(
      `https://api.notion.com/v1/databases/${databaseId}/query`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${NOTION_API_KEY}`,
          'Notion-Version': '2022-06-28',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          page_size: 100,
          ...(cursor && { start_cursor: cursor }),
        }),
      }
    );

    const data = await response.json();
    results.push(...data.results);

    if (!data.has_more) break;
    cursor = data.next_cursor;
  }

  return results;
}
```

## Paginated Endpoints

| Endpoint | Max per page |
|----------|--------------|
| Database query | 100 |
| Block children | 100 |
| Search | 100 |
| Users list | 100 |
| Comments list | 100 |

## Best Practices

1. Always check `has_more`
2. Use max page_size (100)
3. Handle rate limits with retry
4. Stream large datasets
