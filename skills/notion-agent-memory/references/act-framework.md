# ACT Framework — Database Schemas

## ACT I: Hidden Narratives

Track patterns, assumptions, blind spots discovered during operation.

| Property | Type | Options |
|----------|------|---------|
| Narrative | Title | The pattern or belief identified |
| Date | Date | When discovered |
| Category | Select | `belief`, `pattern`, `assumption`, `signal` |
| Impact | Select | `low`, `medium`, `high`, `critical` |
| Action | Select | `eliminate`, `optimize`, `adopt` |
| Status | Select | `active`, `processing`, `resolved`, `superseded` |
| Notes | Rich Text | Context, evidence, reasoning |

**Default view:** Table sorted by Date descending

---

## ACT II: Limitless (MMM)

Track breakthroughs in Mindset, Methods, Motivation.

| Property | Type | Options |
|----------|------|---------|
| Breakthrough | Title | What changed or was learned |
| Date | Date | When it happened |
| Type | Select | `mindset`, `method`, `motivation` |
| Trigger | Rich Text | What caused this breakthrough |
| Before | Rich Text | Previous state/belief |
| After | Rich Text | New state/belief |
| Status | Select | `emerging`, `established`, `integrated` |

**Default view:** Board grouped by Type

---

## ACT III: Ideas Pipeline

Capture, evaluate, and track ideas through to action.

| Property | Type | Options |
|----------|------|---------|
| Idea | Title | Short description |
| Date | Date | When captured |
| Category | Select | `product`, `content`, `process`, `revenue`, `experiment` |
| Status | Select | `captured`, `evaluating`, `in progress`, `shipped`, `parked`, `killed` |
| Effort | Select | `trivial`, `low`, `medium`, `high` |
| Revenue | Select | `$`, `$$`, `$$$`, `$$$$` |
| Notes | Rich Text | Details, next steps, blockers |
| Link | URL | Related resource |

**Default view:** Table grouped by Status

---

## Creating via API

```bash
# Create ACT I database
curl -X POST 'https://api.notion.com/v1/databases' \
  -H "Authorization: Bearer $(cat ~/.config/notion/api_key)" \
  -H 'Notion-Version: 2022-06-28' \
  -H 'Content-Type: application/json' \
  -d '{
    "parent": {"page_id": "YOUR_PAGE_ID"},
    "icon": {"emoji": "🔍"},
    "title": [{"text": {"content": "ACT I: Hidden Narratives"}}],
    "properties": {
      "Narrative": {"title": {}},
      "Date": {"date": {}},
      "Category": {"select": {"options": [
        {"name": "belief", "color": "blue"},
        {"name": "pattern", "color": "purple"},
        {"name": "assumption", "color": "orange"},
        {"name": "signal", "color": "green"}
      ]}},
      "Impact": {"select": {"options": [
        {"name": "low", "color": "gray"},
        {"name": "medium", "color": "yellow"},
        {"name": "high", "color": "orange"},
        {"name": "critical", "color": "red"}
      ]}},
      "Action": {"select": {"options": [
        {"name": "eliminate", "color": "red"},
        {"name": "optimize", "color": "yellow"},
        {"name": "adopt", "color": "green"}
      ]}},
      "Status": {"select": {"options": [
        {"name": "active", "color": "blue"},
        {"name": "processing", "color": "yellow"},
        {"name": "resolved", "color": "green"},
        {"name": "superseded", "color": "gray"}
      ]}},
      "Notes": {"rich_text": {}}
    }
  }'
```

Repeat pattern for ACT II and ACT III with their respective schemas.
