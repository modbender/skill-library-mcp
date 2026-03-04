# Notion Integration Guide

*How to connect your agent to Notion for persistent memory and structured data.*

---

## Quick Setup

### 1. Get Your API Key

1. Go to [notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Create a new integration
3. Copy the "Internal Integration Secret" (starts with `ntn_`)

### 2. Save It

```bash
echo "ntn_your_key_here" > ~/.config/notion/api_key
```

### 3. Share Your Database

1. Open your Notion database (or page)
2. Click Share → Add connections
3. Find your integration and add it

---

## Basic API Patterns

### Query a Database

```bash
TOKEN=$(grep -o '"token"[[:space:]]*:[[:space:]]*"[^"]*"' ~/.config/notion/api_key | cut -d'"' -f4)
DB_ID="your-database-id-here"

curl -s -X POST "https://api.notion.com/v1/databases/$DB_ID/query" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{"page_size": 10}'
```

### Get a Page

```bash
TOKEN=$(grep -o '"token"[[:space:]]*:[[:space:]]*"[^"]*"' ~/.config/notion/api_key | cut -d'"' -f4)
PAGE_ID="your-page-id-here"

curl -s "https://api.notion.com/v1/pages/$PAGE_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Notion-Version: 2022-06-28"
```

### Create a Page

```bash
TOKEN=$(grep -o '"token"[[:space:]]*:[[:space:]]*"[^"]*"' ~/.config/notion/api_key | cut -d'"' -f4)
DB_ID="your-database-id-here"

curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d "{
    \"parent\": {\"database_id\": \"$DB_ID\"},
    \"properties\": {
      \"Name\": {
        \"title\": [{ \"text\": { \"content\": \"My New Entry\" } }]
      },
      \"Status\": {
        \"select\": { \"name\": \"Captured\" }
      }
    }
  }"
```

### Update a Page

```bash
TOKEN=$(grep -o '"token"[[:space:]]*:[[:space:]]*"[^"]*"' ~/.config/notion/api_key | cut -d'"' -f4)
PAGE_ID="your-page-id-here"

curl -s -X PATCH "https://api.notion.com/v1/pages/$PAGE_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d "{
    \"properties\": {
      \"Status\": {
        \"select\": { \"name\": \"In Progress\" }
      }
    }
  }"
```

---

---

## Common Database IDs

*Replace these with your actual database IDs.*

| Database | ID |
|----------|-----|
| ACT I: Hidden Narratives | `your-id-here` |
| ACT II: Limitless | `your-id-here` |
| ACT III: Ideas Pipeline | `your-id-here` |

---

## Tips

1. **Database IDs** are 32-character strings with dashes
2. **Page IDs** are also 32-character strings (different from database IDs)
3. Use `page_size` to limit results (max 100)
4. Notion API returns paginated results — handle `has_more` and `next_cursor`

---

*For more, see: https://developers.notion.io*
