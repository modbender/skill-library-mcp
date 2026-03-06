---
name: feishu-block-ops
description: |
  Low-level Feishu document block operations via REST API. Use when feishu_doc built-in actions are insufficient: batch update cells, precise position insert, traverse block tree, table row/column manipulation, image replacement, or any operation requiring direct block-level control. Complements feishu-doc, not a replacement.
---

# Feishu Block Operations

Direct REST API operations for Feishu cloud documents when the `feishu_doc` tool's built-in actions don't cover your needs.

## When to Use This (vs feishu_doc)

| Need | Use |
|------|-----|
| Read/write/append document | `feishu_doc` |
| Create simple table | `feishu_doc` `create_table_with_values` |
| Upload image/file | `feishu_doc` `upload_image`/`upload_file` |
| **Batch update 200 cells at once** | **This skill** |
| **Insert content at exact position** | **This skill** (or `feishu-md2blocks`) |
| **Traverse block tree** | **This skill** |
| **Table row/column insert/delete** | **This skill** |
| **Merge/unmerge table cells** | **This skill** |
| **Replace images in-place** | **This skill** |
| **Delete blocks by index range** | **This skill** |

## Authentication

Get tenant access token from OpenClaw config:

```python
import json, urllib.request

def get_feishu_token():
    with open(os.path.expanduser("~/.openclaw/openclaw.json")) as f:
        c = json.load(f)["channels"]["feishu"]
    payload = json.dumps({"app_id": c["appId"], "app_secret": c["appSecret"]}).encode()
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=payload, headers={"Content-Type": "application/json"}, method="POST")
    return json.loads(urllib.request.urlopen(req).read())["tenant_access_token"]
```

All API calls use header: `Authorization: Bearer {token}`

## Rate Limits

| Operation | Limit |
|-----------|-------|
| Read (GET) | 5 req/sec per app |
| Write (POST/PATCH/DELETE) | 3 req/sec per app, 3 req/sec per document |

Use `time.sleep(0.35)` between write calls. For reads, `time.sleep(0.25)`.

## API Reference

Base URL: `https://open.feishu.cn/open-apis/docx/v1/documents`

### 1. Get Block

```
GET /docx/v1/documents/{doc}/blocks/{block_id}
```

Returns single block with full content (type, elements, children IDs, styles).

### 2. Get Children (with optional full tree)

```
GET /docx/v1/documents/{doc}/blocks/{block_id}/children
    ?with_descendants=true    # get ALL descendants, not just direct children
    &page_size=500            # max 500
    &document_revision_id=-1  # latest revision
```

**Tip:** Use `with_descendants=true` on table blocks to get all cells + cell content in one call.

### 3. Create Blocks (simple, flat only)

```
POST /docx/v1/documents/{doc}/blocks/{parent_id}/children
Body: {"children": [...blocks], "index": 0}
```

- Max 50 blocks per call
- **Cannot** create nested structures (e.g. table with cell content)
- `index` in body: 0=beginning, -1=end (default)

### 4. Create Nested Blocks (tables, grids, etc.)

```
POST /docx/v1/documents/{doc}/blocks/{parent_id}/descendant
Body: {
    "children_id": ["temp_id_1", "temp_id_2"],
    "descendants": [...all_blocks_with_parent_child_relations],
    "index": 0
}
```

- Max 1000 blocks per call
- `children_id`: only first-level child IDs (NOT grandchildren — causes error 1770006)
- `descendants`: flat array of ALL blocks including nested ones, each with `block_id`, `block_type`, `children` (list of child temp IDs)
- ⚠️ **`index` MUST be in request body, NOT as URL query parameter** — `?index=N` is silently ignored

### 5. Batch Update Blocks

```
PATCH /docx/v1/documents/{doc}/blocks/batch_update
Body: {"requests": [...update_requests]}
```

Max 200 blocks per call. Each request object contains `block_id` + one operation:

| Operation | Purpose |
|-----------|---------|
| `update_text_elements` | Replace text content + inline elements |
| `update_text_style` | Change alignment, folded, language, wrap, background_color |
| `update_table_property` | Modify column widths, header rows/columns |
| `insert_table_row` | Insert rows at index |
| `insert_table_column` | Insert columns at index |
| `delete_table_rows` | Delete rows by index + count |
| `delete_table_columns` | Delete columns by index + count |
| `merge_table_cells` | Merge cells (row_start, row_end, column_start, column_end) |
| `unmerge_table_cells` | Unmerge previously merged cells |
| `replace_image` | Replace image block's content with new file_token |

#### Example: batch update text in multiple cells

```python
requests = []
for block_id, new_text in updates.items():
    requests.append({
        "block_id": block_id,
        "update_text_elements": {
            "elements": [{"text_run": {"content": new_text}}]
        }
    })

api_call(token, "PATCH",
    f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc}/blocks/batch_update",
    {"requests": requests})
```

### 6. Update Single Block

```
PATCH /docx/v1/documents/{doc}/blocks/{block_id}
Body: {same operations as batch_update, without block_id wrapper}
```

### 7. Delete Blocks

```
DELETE /docx/v1/documents/{doc}/blocks/{parent_id}/children/batch_delete
Body: {"start_index": 0, "end_index": 5}
```

- ⚠️ Uses `start_index`/`end_index` (half-open interval `[start, end)`), **NOT** `block_ids`
- Indices are relative to the parent block's children list

## Block Types

| Type | ID | Notes |
|------|---:|-------|
| Page | 1 | Document root, always one |
| Text | 2 | Plain paragraph |
| Heading1–9 | 3–11 | |
| Bullet | 12 | Unordered list item |
| Ordered | 13 | Ordered list item |
| Code | 14 | Code block |
| Quote | 15 | Block quote |
| Todo | 17 | Checkbox item |
| Callout | 19 | Highlighted block |
| Divider | 22 | Horizontal rule (body: `{}`) |
| Grid | 24 | Multi-column layout |
| GridColumn | 25 | Column in grid |
| Image | 27 | Image block |
| Table | 31 | Table container |
| TableCell | 32 | Cell in table |
| QuoteContainer | 34 | Quote wrapper (body: `{}`) |

## Text Elements

Text blocks contain an `elements` array. Each element is one of:

```python
# Plain text
{"text_run": {"content": "hello", "text_element_style": {"bold": True, "link": {"url": "..."}}}}

# Mention user
{"mention_user": {"user_id": "ou_xxx", "text_element_style": {}}}

# Mention document
{"mention_doc": {"token": "xxx", "obj_type": 22, "text_element_style": {}}}

# Equation (LaTeX)
{"equation": {"content": "E=mc^2"}}

# Reminder
{"reminder": {"expire_time": 1234567890, "is_whole_day": True}}
```

## Common Patterns

### Pattern 1: Read table content

```python
# 1. Get table's descendants in one call
url = f".../blocks/{table_block_id}/children?with_descendants=true&page_size=500&document_revision_id=-1"
items = api_call(token, "GET", url)["data"]["items"]

# 2. Extract text from cells
for item in items:
    if item["block_type"] == 2 and "text" in item:
        text = "".join(e.get("text_run", {}).get("content", "") for e in item["text"]["elements"])
```

### Pattern 2: Insert Markdown at position

Use `feishu-md2blocks` skill's `md2blocks.py` script with `--after <block_id>`.

Or manually:
```python
# 1. Convert markdown
convert_resp = api_call(token, "POST", ".../blocks/convert",
    {"content_type": "markdown", "content": md_text})

# 2. Clean table blocks (remove merge_info)
for block in convert_resp["data"]["blocks"]:
    if block.get("block_type") == 31 and "table" in block:
        block["table"]["property"].pop("merge_info", None)

# 3. Insert at position (index IN BODY)
api_call(token, "POST", f".../blocks/{parent_id}/descendant", {
    "children_id": convert_resp["data"]["first_level_block_ids"],
    "descendants": convert_resp["data"]["blocks"],
    "index": target_index
})
```

### Pattern 3: Batch edit table cells

```python
# 1. Get all descendants of table
items = get_descendants(table_id)

# 2. Build update map
updates = []
for item in items:
    if needs_update(item):
        updates.append({
            "block_id": item["block_id"],
            "update_text_elements": {
                "elements": [{"text_run": {"content": new_value}}]
            }
        })

# 3. Batch update (max 200 per call)
for i in range(0, len(updates), 200):
    api_call(token, "PATCH", f".../blocks/batch_update",
        {"requests": updates[i:i+200]})
    time.sleep(0.35)
```

### Pattern 4: Delete then re-insert (position workaround)

When you need to replace content at a specific position:

```python
# 1. Find the index range to replace
children = get_doc_children(doc)
start_idx = children.index(first_block_to_replace)
end_idx = children.index(last_block_to_replace) + 1

# 2. Delete old blocks
api_call(token, "DELETE", f".../children/batch_delete",
    {"start_index": start_idx, "end_index": end_idx})

# 3. Insert new content at same position
api_call(token, "POST", f".../blocks/{doc}/descendant", {
    "children_id": new_ids,
    "descendants": new_blocks,
    "index": start_idx
})
```

## Gotchas & Lessons Learned

1. **`/descendant` index in body, not URL** — The most common pitfall. `?index=N` compiles but is silently ignored.
2. **`batch_delete` uses index range** — `{"start_index": 0, "end_index": 5}` deletes children[0..4]. Do NOT pass `block_ids`.
3. **Table `merge_info` is read-only** — Must strip from blocks before insertion or API returns error.
4. **`children_id` is first-level only** — Including grandchild IDs in `children_id` causes error 1770006.
5. **Rate limit is per-document** — Multiple concurrent edits to the same doc share the 3/sec limit.
6. **`with_descendants=true` saves calls** — One GET instead of N+1 for reading table content.
7. **Convert API returns temp IDs** — After insertion, actual block IDs differ from the temp IDs used during convert.
