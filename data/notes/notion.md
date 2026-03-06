# Notion — Notes Platform

## Overview

Manage Notion pages and databases via REST API. Cross-platform.

## Requirements

- Notion account
- Notion integration (API key)

## Setup

### 1. Create Integration

1. Go to https://notion.so/my-integrations
2. Click "New integration"
3. Name it (e.g., "Notes Agent")
4. Copy the API key (starts with `ntn_` or `secret_`)

### 2. Store API Key

```bash
mkdir -p ~/.config/notion
echo "ntn_your_key_here" > ~/.config/notion/api_key
chmod 600 ~/.config/notion/api_key
```

### 3. Share Pages with Integration

For each page/database you want to access:
1. Open in Notion
2. Click "..." menu → "Connect to"
3. Select your integration name

## API Basics

All requests:

```bash
NOTION_KEY=$(cat ~/.config/notion/api_key)

curl -X GET "https://api.notion.com/v1/..." \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json"
```

## Common Operations

### Search

```bash
curl -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"query": "product roadmap"}'
```

### Get Page

```bash
curl "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03"
```

### Get Page Content (Blocks)

```bash
curl "https://api.notion.com/v1/blocks/{page_id}/children" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03"
```

### Create Page

**In a database:**
```bash
curl -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "xxx"},
    "properties": {
      "Name": {"title": [{"text": {"content": "Meeting: Product Sync"}}]},
      "Date": {"date": {"start": "2026-02-19"}},
      "Type": {"select": {"name": "Meeting"}}
    }
  }'
```

**As child of page:**
```bash
curl -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"page_id": "xxx"},
    "properties": {
      "title": {"title": [{"text": {"content": "Meeting Notes"}}]}
    }
  }'
```

### Add Content to Page

```bash
curl -X PATCH "https://api.notion.com/v1/blocks/{page_id}/children" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "children": [
      {"type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "Key Points"}}]}},
      {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "Point 1"}}]}},
      {"type": "to_do", "to_do": {"rich_text": [{"text": {"content": "@alice: Update doc"}}], "checked": false}}
    ]
  }'
```

### Query Database

```bash
curl -X POST "https://api.notion.com/v1/data_sources/{data_source_id}/query" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {"property": "Type", "select": {"equals": "Meeting"}},
    "sorts": [{"property": "Date", "direction": "descending"}]
  }'
```

## Property Types

| Type | Format |
|------|--------|
| Title | `{"title": [{"text": {"content": "..."}}]}` |
| Rich text | `{"rich_text": [{"text": {"content": "..."}}]}` |
| Select | `{"select": {"name": "Option"}}` |
| Multi-select | `{"multi_select": [{"name": "A"}, {"name": "B"}]}` |
| Date | `{"date": {"start": "2026-02-19"}}` |
| Checkbox | `{"checkbox": true}` |
| Number | `{"number": 42}` |

## Recommended Database Schema

For notes tracking:

| Property | Type | Options |
|----------|------|---------|
| Name | Title | — |
| Type | Select | Meeting, Decision, Project, Journal, Quick |
| Date | Date | — |
| Tags | Multi-select | product, engineering, etc. |
| Status | Select | Draft, Active, Archived |

## Block Types for Notes

| Block | Purpose |
|-------|---------|
| `heading_1/2/3` | Section headers |
| `paragraph` | Body text |
| `bulleted_list_item` | Key points |
| `numbered_list_item` | Ordered lists |
| `to_do` | Action items (with checkbox) |
| `callout` | Highlights, warnings |
| `divider` | Section breaks |

## Rate Limits

- ~3 requests/second average
- Batch operations when possible

## Integration Notes

- Action items (`to_do` blocks) extracted → sync to `~/notes/actions.md`
- Search results include Notion with `notion:Page Name` format
- If API key not configured → fall back to local
- Data leaves machine (sent to Notion API)
