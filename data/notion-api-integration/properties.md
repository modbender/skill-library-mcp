# Property Types - Notion API

## Title (Required)
```json
{"Name": {"title": [{"type": "text", "text": {"content": "Page title"}}]}}
```

## Rich Text
```json
{"Description": {"rich_text": [{"type": "text", "text": {"content": "Text"}}]}}
```

## Number
```json
{"Price": {"number": 99.99}}
```

## Select
```json
{"Status": {"select": {"name": "In Progress"}}}
```

## Multi-Select
```json
{"Tags": {"multi_select": [{"name": "Tag1"}, {"name": "Tag2"}]}}
```

## Status
```json
{"Status": {"status": {"name": "Done"}}}
```

## Date
```json
{"Due Date": {"date": {"start": "2025-12-31"}}}
{"Duration": {"date": {"start": "2025-01-01", "end": "2025-01-07"}}}
{"Meeting": {"date": {"start": "2025-01-15T14:00:00.000+00:00", "time_zone": "America/New_York"}}}
```

## Checkbox
```json
{"Done": {"checkbox": true}}
```

## URL
```json
{"Link": {"url": "https://example.com"}}
```

## Email
```json
{"Contact": {"email": "user@example.com"}}
```

## Phone
```json
{"Phone": {"phone_number": "+1-555-123-4567"}}
```

## People
```json
{"Assignee": {"people": [{"id": "USER_ID"}]}}
```

## Files
```json
{"Attachments": {"files": [{"name": "doc.pdf", "type": "external", "external": {"url": "https://example.com/doc.pdf"}}]}}
```

## Relation
```json
{"Related": {"relation": [{"id": "PAGE_ID_1"}, {"id": "PAGE_ID_2"}]}}
```

## Rollup (Read-only)
```json
{"Total": {"rollup": {"type": "number", "number": 150, "function": "sum"}}}
```

## Formula (Read-only)
```json
{"Computed": {"formula": {"type": "string", "string": "Result"}}}
```

## Created Time (Read-only)
```json
{"Created": {"created_time": "2025-01-01T12:00:00.000Z"}}
```

## Last Edited Time (Read-only)
```json
{"Updated": {"last_edited_time": "2025-01-15T14:30:00.000Z"}}
```

## Unique ID (Read-only)
```json
{"ID": {"unique_id": {"prefix": "TASK", "number": 42}}}
```

## Clear Property
```json
{"Due Date": {"date": null}}
{"Tags": {"multi_select": []}}
```
