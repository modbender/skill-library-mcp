# Blocks - Notion API

## Get Block Children

```bash
curl 'https://api.notion.com/v1/blocks/BLOCK_OR_PAGE_ID/children?page_size=100' \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28"
```

## Append Children

```bash
curl -X PATCH 'https://api.notion.com/v1/blocks/BLOCK_OR_PAGE_ID/children' \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{
    "children": [
      {"object": "block", "type": "paragraph", "paragraph": {
        "rich_text": [{"type": "text", "text": {"content": "New paragraph"}}]
      }}
    ]
  }'
```

## Block Types

### Paragraph
```json
{"type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "Text"}}]}}
```

### Headings
```json
{"type": "heading_1", "heading_1": {"rich_text": [{"type": "text", "text": {"content": "H1"}}]}}
```
Also: `heading_2`, `heading_3`

### Lists
```json
{"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Item"}}]}}
{"type": "numbered_list_item", "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": "Item"}}]}}
```

### To-Do
```json
{"type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "Task"}}], "checked": false}}
```

### Code
```json
{"type": "code", "code": {"rich_text": [{"type": "text", "text": {"content": "code"}}], "language": "javascript"}}
```

### Quote / Callout
```json
{"type": "quote", "quote": {"rich_text": [{"type": "text", "text": {"content": "Quote"}}]}}
{"type": "callout", "callout": {"rich_text": [{"type": "text", "text": {"content": "Note"}}], "icon": {"type": "emoji", "emoji": "💡"}}}
```

### Divider
```json
{"type": "divider", "divider": {}}
```

## Update Block

```bash
curl -X PATCH 'https://api.notion.com/v1/blocks/BLOCK_ID' \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{"paragraph": {"rich_text": [{"type": "text", "text": {"content": "Updated"}}]}}'
```

## Delete Block

```bash
curl -X DELETE 'https://api.notion.com/v1/blocks/BLOCK_ID' \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28"
```

## Rich Text Formatting

```json
{
  "type": "text",
  "text": {"content": "Styled", "link": {"url": "https://example.com"}},
  "annotations": {"bold": true, "italic": false, "code": false, "color": "red"}
}
```
Colors: `default`, `gray`, `brown`, `orange`, `yellow`, `green`, `blue`, `purple`, `pink`, `red`, plus `_background` variants.
