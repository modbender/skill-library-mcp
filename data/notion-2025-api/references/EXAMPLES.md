# Notion 2025 API Examples

Real-world examples for common tasks.

## Example 1: Query Series Database (from Blog)

**Task:** Query all Active blog series, sorted by last update

```bash
NOTION_KEY=$(cat ~/.openclaw/workspace/secrets/notion_api_key.txt)
DATA_SOURCE_ID="YOUR_DATA_SOURCE_ID"  # Replace with your actual data source ID

curl -s -X POST "https://api.notion.com/v1/data_sources/$DATA_SOURCE_ID/query" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {"property": "Status", "status": {"equals": "In progress"}},
    "sorts": [{"property": "Last edited time", "direction": "descending"}]
  }' | jq '.results[] | {name: .properties.Name.title[0].plain_text, status: .properties.Status.status.name}'
```

**Output:**
```json
{
  "name": "Minecraft 生存效能與實務全指南",
  "status": "In progress"
}
```

---

## Example 2: Create a Blog Series Entry

**Task:** Add a new series to the Blog Series database

```bash
NOTION_KEY=$(cat ~/.openclaw/workspace/secrets/notion_api_key.txt)
DATABASE_ID="YOUR_DATABASE_ID"  # Blog Series database

curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "'$DATABASE_ID'"},
    "properties": {
      "Name": {"title": [{"text": {"content": "Fallout Game Series Guide"}}]},
      "Status": {"status": {"name": "Draft"}},
      "Spoke Count": {"number": 3},
      "Category": {"select": {"name": "Gaming"}},
      "Description": {"rich_text": [{"text": {"content": "Complete guide to Fallout game mechanics and building strategies"}}]},
      "URL": {"url": "https://github.com/example/fallout-series"}
    }
  }' | jq '.id'
```

---

## Example 3: Update Spoke Count for a Series

**Task:** Update the Spoke Count when new articles are added

```bash
NOTION_KEY=$(cat ~/.openclaw/workspace/secrets/notion_api_key.txt)
ENTRY_ID="YOUR_ENTRY_ID"  # Minecraft series entry

curl -s -X PATCH "https://api.notion.com/v1/pages/$ENTRY_ID" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "Spoke Count": {"number": 5}
    }
  }' | jq '.properties["Spoke Count"].number'
```

---

## Example 4: Add Content to a Page

**Task:** Add sections and content to a database entry page

```bash
NOTION_KEY=$(cat ~/.openclaw/workspace/secrets/notion_api_key.txt)
PAGE_ID="YOUR_ENTRY_ID"

curl -s -X PATCH "https://api.notion.com/v1/blocks/$PAGE_ID/children" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "children": [
      {
        "object": "block",
        "type": "heading_2",
        "heading_2": {"rich_text": [{"text": {"content": "Series Overview"}}]}
      },
      {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": [{"text": {"content": "A comprehensive guide to survival mechanics and optimization in Minecraft."}}]}
      },
      {
        "object": "block",
        "type": "heading_2",
        "heading_2": {"rich_text": [{"text": {"content": "Articles"}}]}
      },
      {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": [{"text": {"content": "keepInventory guide"}}]}
      },
      {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": [{"text": {"content": "Difficulty adjustment commands"}}]}
      }
    ]
  }' | jq '.object'
```

---

## Example 5: Filter by Multiple Conditions

**Task:** Find all Active gaming series updated in the last 7 days

```bash
NOTION_KEY=$(cat ~/.openclaw/workspace/secrets/notion_api_key.txt)
DATA_SOURCE_ID="YOUR_DATA_SOURCE_ID"

# Note: Requires calculating date 7 days ago
SEVEN_DAYS_AGO=$(date -u -v-7d +"%Y-%m-%d")  # macOS
# For Linux: SEVEN_DAYS_AGO=$(date -u -d "7 days ago" +"%Y-%m-%d")

curl -s -X POST "https://api.notion.com/v1/data_sources/$DATA_SOURCE_ID/query" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {
      "and": [
        {"property": "Status", "status": {"equals": "In progress"}},
        {"property": "Category", "select": {"equals": "Gaming"}},
        {"property": "Last edited time", "date": {"on_or_after": "'$SEVEN_DAYS_AGO'"}}
      ]
    }
  }' | jq '.results[] | {name: .properties.Name.title[0].plain_text, updated: .last_edited_time}'
```

---

## Example 6: Batch Update Multiple Entries

**Task:** Update status for multiple series

```bash
NOTION_KEY=$(cat ~/.openclaw/workspace/secrets/notion_api_key.txt)

# Get all Draft series
SERIES=$(curl -s -X POST "https://api.notion.com/v1/data_sources/YOUR_DATA_SOURCE_ID/query" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"filter": {"property": "Status", "status": {"equals": "Draft"}}}' | jq -r '.results[].id')

# Update each to "In progress"
for entry_id in $SERIES; do
  curl -s -X PATCH "https://api.notion.com/v1/pages/$entry_id" \
    -H "Authorization: Bearer $NOTION_KEY" \
    -H "Notion-Version: 2025-09-03" \
    -H "Content-Type: application/json" \
    -d '{"properties": {"Status": {"status": {"name": "In progress"}}}}' > /dev/null
  echo "Updated: $entry_id"
done
```

---

## Example 7: Create and Link Related Entries (Advanced)

**Task:** Create a new blog series and link it to articles

```bash
NOTION_KEY=$(cat ~/.openclaw/workspace/secrets/notion_api_key.txt)
SERIES_DB="YOUR_DATABASE_ID"

# Step 1: Create series entry
SERIES_ID=$(curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "'$SERIES_DB'"},
    "properties": {
      "Name": {"title": [{"text": {"content": "New Series"}}]},
      "Status": {"status": {"name": "Planning"}},
      "Spoke Count": {"number": 0}
    }
  }' | jq -r '.id')

echo "Created series: $SERIES_ID"

# Step 2: Articles would reference this series ID
# (If you have an Articles database with a Series relation field)
```
