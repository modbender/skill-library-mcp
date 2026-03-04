# Filters and Sorts - Notion API

## Text Filter
```json
{"filter": {"property": "Name", "rich_text": {"contains": "search term"}}}
```
Operations: `equals`, `does_not_equal`, `contains`, `does_not_contain`, `starts_with`, `ends_with`, `is_empty`, `is_not_empty`

## Number Filter
```json
{"filter": {"property": "Price", "number": {"greater_than": 100}}}
```
Operations: `equals`, `does_not_equal`, `greater_than`, `less_than`, `greater_than_or_equal_to`, `less_than_or_equal_to`, `is_empty`, `is_not_empty`

## Select Filter
```json
{"filter": {"property": "Status", "select": {"equals": "Done"}}}
```

## Multi-Select Filter
```json
{"filter": {"property": "Tags", "multi_select": {"contains": "Important"}}}
```

## Status Filter
```json
{"filter": {"property": "Status", "status": {"equals": "In Progress"}}}
```

## Date Filter
```json
{"filter": {"property": "Due Date", "date": {"on_or_after": "2025-01-01"}}}
```
Operations: `equals`, `before`, `after`, `on_or_before`, `on_or_after`, `is_empty`, `is_not_empty`, `past_week`, `past_month`, `next_week`, `next_month`, `this_week`

## Checkbox Filter
```json
{"filter": {"property": "Done", "checkbox": {"equals": true}}}
```

## People Filter
```json
{"filter": {"property": "Assignee", "people": {"contains": "USER_ID"}}}
```

## Compound Filters

### AND
```json
{"filter": {"and": [
  {"property": "Status", "status": {"equals": "In Progress"}},
  {"property": "Priority", "select": {"equals": "High"}}
]}}
```

### OR
```json
{"filter": {"or": [
  {"property": "Status", "status": {"equals": "Done"}},
  {"property": "Status", "status": {"equals": "Archived"}}
]}}
```

## Sorts

### Single Sort
```json
{"sorts": [{"property": "Due Date", "direction": "ascending"}]}
```

### Multiple Sorts
```json
{"sorts": [
  {"property": "Priority", "direction": "descending"},
  {"property": "Due Date", "direction": "ascending"}
]}
```

### Sort by Timestamp
```json
{"sorts": [{"timestamp": "last_edited_time", "direction": "descending"}]}
```

## Full Query Example

```bash
curl -X POST 'https://api.notion.com/v1/databases/DATABASE_ID/query' \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {"and": [
      {"property": "Status", "status": {"does_not_equal": "Done"}},
      {"property": "Due Date", "date": {"on_or_before": "2025-01-31"}}
    ]},
    "sorts": [{"property": "Due Date", "direction": "ascending"}],
    "page_size": 100
  }'
```
