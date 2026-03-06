# openclaw-notion-skill

**Notion API 2025-09-03 integration for OpenClaw** — Query, create, and manage Notion databases and pages with full support for the latest Notion API format.

[![clawhub](https://img.shields.io/badge/Available%20on-ClawHub-blue)](https://clawhub.com)

## Features

✅ **Database Operations**
- Query entries with filters and sorting
- Create new database entries
- Update entry properties
- Batch operations support

✅ **Page Management**
- Update page properties
- Add content blocks (headings, paragraphs, lists, code, etc.)
- Get page details
- Organize content hierarchically

✅ **2025-09-03 API Support**
- Correct `data_source_id` vs `database_id` handling
- Latest property formats
- Status, select, number, date, rich text, and URL fields
- Block types: headings, paragraphs, bulleted lists, code blocks

✅ **Developer Friendly**
- Comprehensive examples included
- Ready-to-use bash helper script
- Complete API reference
- Error handling guides

## Installation

### Via ClawHub (Recommended)

```bash
clawhub install openclaw-notion-skill
```

### Manual

1. Clone the repo:
```bash
git clone https://github.com/kai-tw/openclaw-notion-skill.git
cd openclaw-notion-skill
```

2. Copy to your OpenClaw skills directory:
```bash
cp -r . ~/.openclaw/workspace/skills/notion-2025/
```

## Setup

### 1. Create Notion Integration

1. Go to https://notion.so/my-integrations
2. Click "Create new integration"
3. Name it (e.g., "OpenClaw")
4. Copy the **API key** (starts with `ntn_`)

### 2. Store API Key

```bash
mkdir -p ~/.openclaw/workspace/secrets
echo "ntn_YOUR_KEY_HERE" > ~/.openclaw/workspace/secrets/notion_api_key.txt
chmod 600 ~/.openclaw/workspace/secrets/notion_api_key.txt
```

### 3. Share Notion Pages/Databases

In Notion:
1. Open the page or database
2. Click **Share** (top right)
3. Search for your integration name
4. Grant **"Can edit"** permission

## Quick Start

### Query a Database

```bash
# Set your data_source_id and filter
DATA_SOURCE_ID="your_data_source_id"

curl -s -X POST "https://api.notion.com/v1/data_sources/$DATA_SOURCE_ID/query" \
  -H "Authorization: Bearer $(cat ~/.openclaw/workspace/secrets/notion_api_key.txt)" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {"property": "Status", "select": {"equals": "Active"}},
    "sorts": [{"property": "Updated", "direction": "descending"}]
  }' | jq '.results[]'
```

### Create a Database Entry

```bash
DATABASE_ID="your_database_id"

curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $(cat ~/.openclaw/workspace/secrets/notion_api_key.txt)" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "'$DATABASE_ID'"},
    "properties": {
      "Name": {"title": [{"text": {"content": "My Entry"}}]},
      "Status": {"select": {"name": "Active"}},
      "Count": {"number": 42}
    }
  }' | jq '.id'
```

### Use the Helper Script

```bash
# Query database
./scripts/notion_helper.sh query YOUR_DATA_SOURCE_ID

# Create entry
./scripts/notion_helper.sh create YOUR_DATABASE_ID "Entry Title"

# Update property
./scripts/notion_helper.sh update YOUR_PAGE_ID '"Status": {"status": {"name": "Complete"}}' 

# Get page details
./scripts/notion_helper.sh get YOUR_PAGE_ID
```

## Documentation

- **[SKILL.md](SKILL.md)** — How to use with OpenClaw
- **[API_REFERENCE.md](references/API_REFERENCE.md)** — Complete endpoint documentation
- **[EXAMPLES.md](references/EXAMPLES.md)** — Real-world examples

## Key Concepts

### database_id vs data_source_id

The 2025-09-03 API separates these IDs:

| ID | Purpose | Used In |
|----|---------| --------|
| `database_id` | Creating new pages | `POST /v1/pages` |
| `data_source_id` | Querying entries | `POST /v1/data_sources/{id}/query` |

**Finding your data_source_id:**
- In Notion database view, click "Connect a tool" → Copy the ID shown
- Or query the database endpoint

### Filter & Sort

Query with advanced filtering:

```json
{
  "filter": {
    "and": [
      {"property": "Status", "select": {"equals": "Active"}},
      {"property": "Count", "number": {"greater_than": 5}}
    ]
  },
  "sorts": [
    {"property": "Updated", "direction": "descending"}
  ]
}
```

### Property Types

Supported property types:
- `title` — Database entry name
- `rich_text` — Text content with formatting
- `select` — Single-choice dropdown
- `status` — Status field
- `number` — Numeric value
- `date` — Date with optional end date
- `checkbox` — Boolean toggle
- `url` — URL link

## Block Types

Supported content blocks:
- `heading_1`, `heading_2`, `heading_3` — Headings
- `paragraph` — Text paragraph
- `bulleted_list_item` — Bullet point
- `numbered_list_item` — Numbered item
- `code` — Code block with language
- `divider` — Horizontal divider
- `quote` — Block quote

See [EXAMPLES.md](references/EXAMPLES.md) for block syntax.

## Troubleshooting

### `404 object_not_found`
**Cause:** Integration not shared with the database  
**Fix:** Go to Notion database → Share → Add integration → Grant access

### `400 validation_error`
**Cause:** Incorrect property format or name  
**Fix:** Check property name and format in [API_REFERENCE.md](references/API_REFERENCE.md)

### `401 unauthorized`
**Cause:** Invalid or missing API key  
**Fix:** Verify `~/.openclaw/workspace/secrets/notion_api_key.txt` exists and contains valid key

### `429 rate_limit_exceeded`
**Cause:** Too many requests (limit ~3/second)  
**Fix:** Add delay between requests: `sleep 0.5` between commands

## Examples

See [EXAMPLES.md](references/EXAMPLES.md) for:
- Querying with filters
- Creating entries
- Batch updating
- Adding content blocks
- Working with different property types

## Contributing

Found a bug or want to improve the skill?

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-improvement`)
3. Commit changes (`git commit -am 'Add improvement'`)
4. Push to branch (`git push origin feature/my-improvement`)
5. Open a Pull Request

## License

MIT — See [LICENSE](LICENSE) for details

## Support

- **Notion API Docs:** https://developers.notion.com
- **2025 API Upgrade Guide:** https://developers.notion.com/guides/get-started/upgrade-guide-2025-09-03
- **ClawHub:** https://clawhub.com

---

**Created for OpenClaw** | [OpenClaw Docs](https://docs.openclaw.ai)
