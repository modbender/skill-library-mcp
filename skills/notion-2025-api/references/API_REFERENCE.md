# Notion 2025-09-03 API Reference

## Key Changes from Previous Versions

### Database IDs (NEW in 2025-09-03)

Each database now has TWO IDs:

| ID Type | Purpose | Used For |
|---------|---------|----------|
| `database_id` | Creating new pages | `POST /v1/pages` with `parent: {"database_id": "..."}` |
| `data_source_id` | Querying entries | `POST /v1/data_sources/{id}/query` |

**Finding your data_source_id:**
- When querying a database, the Notion UI shows: "Create a connection" → Copy the ID
- Or, list a database's data_sources: `GET /v1/databases/{database_id}` → check `.data_sources[0].id`

### Authentication

All requests require:

```
Authorization: Bearer ntn_xxx...
Notion-Version: 2025-09-03
Content-Type: application/json
```

## Endpoints

### Query Database

```
POST /v1/data_sources/{data_source_id}/query
```

**Body:**
```json
{
  "filter": { /* optional filter */ },
  "sorts": [ /* optional sort */ ],
  "page_size": 100
}
```

**Response:** `{ "results": [...], "next_cursor": "..." }`

### Create Database Entry

```
POST /v1/pages
```

**Body:**
```json
{
  "parent": {"database_id": "xxx"},
  "properties": { /* property values */ }
}
```

### Update Page Properties

```
PATCH /v1/pages/{page_id}
```

**Body:**
```json
{
  "properties": { /* updated properties */ }
}
```

### Add Blocks to Page

```
PATCH /v1/blocks/{page_id}/children
```

**Body:**
```json
{
  "children": [ /* block objects */ ]
}
```

### Get Page

```
GET /v1/pages/{page_id}
```

### Get Block Children

```
GET /v1/blocks/{block_id}/children?page_size=100
```

## Property Value Formats

### Rich Text

```json
{
  "rich_text": [
    {
      "type": "text",
      "text": {
        "content": "Your text here",
        "link": null
      },
      "annotations": {
        "bold": false,
        "italic": false,
        "strikethrough": false,
        "underline": false,
        "code": false,
        "color": "default"
      }
    }
  ]
}
```

### Select

```json
{
  "select": {
    "name": "Active"  // must match existing option
  }
}
```

### Status

```json
{
  "status": {
    "name": "In Progress"  // must match existing status
  }
}
```

### Title (Database Entry Name)

```json
{
  "title": [
    {
      "type": "text",
      "text": {
        "content": "Entry Title"
      }
    }
  ]
}
```

### Date

```json
{
  "date": {
    "start": "2026-03-03",
    "end": null  // optional
  }
}
```

### Number

```json
{
  "number": 42
}
```

### Checkbox

```json
{
  "checkbox": true
}
```

### URL

```json
{
  "url": "https://example.com"
}
```

## Block Types (for adding content)

### Heading 2

```json
{
  "type": "heading_2",
  "heading_2": {
    "rich_text": [{"text": {"content": "Section"}}]
  }
}
```

### Paragraph

```json
{
  "type": "paragraph",
  "paragraph": {
    "rich_text": [{"text": {"content": "Content"}}]
  }
}
```

### Bulleted List Item

```json
{
  "type": "bulleted_list_item",
  "bulleted_list_item": {
    "rich_text": [{"text": {"content": "Item"}}]
  }
}
```

### Code Block

```json
{
  "type": "code",
  "code": {
    "rich_text": [{"text": {"content": "code here"}}],
    "language": "bash"
  }
}
```

### Divider

```json
{
  "type": "divider",
  "divider": {}
}
```

## Common Filters

### Select Equals

```json
{
  "property": "Status",
  "select": {"equals": "Active"}
}
```

### Number Greater Than

```json
{
  "property": "Count",
  "number": {"greater_than": 5}
}
```

### Date On or After

```json
{
  "property": "Created",
  "date": {"on_or_after": "2026-01-01"}
}
```

### Rich Text Contains

```json
{
  "property": "Title",
  "rich_text": {"contains": "keyword"}
}
```

### AND / OR

```json
{
  "and": [
    {"property": "Status", "select": {"equals": "Active"}},
    {"property": "Count", "number": {"greater_than": 0}}
  ]
}
```

## Error Handling

Common errors:

| Error | Cause | Fix |
|-------|-------|-----|
| `400 validation_error` | Invalid property type or format | Check property name and format in references |
| `404 object_not_found` | Integration not shared with database | Invite integration in Notion UI |
| `401 unauthorized` | Invalid API key | Verify key location in skill setup section |
| `429 rate_limit_exceeded` | Too many requests | Add delay between requests (aim for ~3/second max) |
