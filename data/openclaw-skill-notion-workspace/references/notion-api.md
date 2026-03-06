# Notion API Reference

## Authentication
- Bearer token in `Authorization` header
- Header: `Notion-Version: 2022-06-28`

## Base URL
`https://api.notion.com/v1`

## Endpoints Used

### Search
`POST /search`
```json
{
  "query": "search term",
  "filter": {"value": "page", "property": "object"},
  "page_size": 20
}
```

### Get Page
`GET /pages/{page_id}`

### Get Page Blocks
`GET /blocks/{block_id}/children?page_size=100`

### Create Page
`POST /pages`
```json
{
  "parent": {"database_id": "DATABASE_ID"},
  "properties": {
    "title": {
      "title": [{"type": "text", "text": {"content": "Page Title"}}]
    }
  }
}
```

### Append Blocks
`PATCH /blocks/{page_id}/children`
```json
{
  "children": [
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [{"type": "text", "text": {"content": "Your text"}}]
      }
    }
  ]
}
```

## Block Types
- `paragraph` - Regular text
- `heading_1`, `heading_2`, `heading_3` - Headings
- `bulleted_list_item` - Bullet point
- `numbered_list_item` - Numbered list
- `to_do` - Checkbox
- `code` - Code block
- `quote` - Quote
- `divider` - Horizontal rule

## Property Types (Database)
- `title` - Page title (required)
- `rich_text` - Text property
- `number` - Number
- `select` - Single select
- `multi_select` - Multiple select
- `date` - Date
- `checkbox` - Boolean
- `url` - URL
- `email` - Email
- `phone_number` - Phone

## Rate Limits
- 3 requests per second average
- Burst allowed up to higher rates

## Pagination
Responses include `has_more` and `next_cursor` for paginated results.
