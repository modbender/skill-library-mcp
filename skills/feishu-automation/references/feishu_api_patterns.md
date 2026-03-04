# Feishu API Patterns

Common patterns and examples for working with Feishu APIs through OpenClaw.

## Tool Overview

OpenClaw provides these Feishu tools:

| Tool | Purpose | Key Actions |
|------|---------|-------------|
| `feishu_doc` | Document operations | read, write, create, append, list_blocks |
| `feishu_wiki` | Knowledge base | spaces, nodes, get, create, move |
| `feishu_bitable_*` | Bitable operations | get_meta, list_fields, list_records, create_record |
| `feishu_drive` | Cloud storage | list, info, create_folder, move |

## Common Patterns

### 1. Document Creation with Template
```json
{
  "tool": "feishu_doc",
  "action": "create",
  "title": "Weekly Report {{date}}",
  "content": "# Weekly Report\n\n## Summary\n{{summary}}\n\n## Details\n{{details}}",
  "folder_token": "fldcnXXX"
}
```

### 2. Reading and Updating Documents
```json
// 1. Read document
{
  "tool": "feishu_doc",
  "action": "read",
  "doc_token": "doxcnXXX"
}

// 2. Check for structured content
if (response.block_types.includes("Table")) {
  // 3. Get full blocks for tables/images
  {
    "tool": "feishu_doc",
    "action": "list_blocks",
    "doc_token": "doxcnXXX"
  }
}

// 4. Update document
{
  "tool": "feishu_doc",
  "action": "write",
  "doc_token": "doxcnXXX",
  "content": "Updated content"
}
```

### 3. Bitable Data Processing
```json
// 1. Parse URL to get tokens
{
  "tool": "feishu_bitable_get_meta",
  "url": "https://xxx.feishu.cn/base/app_token?table=table_id"
}

// 2. List records
{
  "tool": "feishu_bitable_list_records",
  "app_token": "basXXX",
  "table_id": "tblYYY",
  "page_size": 100
}

// 3. Create new record
{
  "tool": "feishu_bitable_create_record",
  "app_token": "basXXX",
  "table_id": "tblYYY",
  "fields": {
    "Name": "New Item",
    "Status": "Active",
    "Priority": 1
  }
}
```

### 4. Wiki Navigation
```json
// 1. List spaces
{
  "tool": "feishu_wiki",
  "action": "spaces"
}

// 2. List nodes in space
{
  "tool": "feishu_wiki",
  "action": "nodes",
  "space_id": "7xxx"
}

// 3. Get specific node
{
  "tool": "feishu_wiki",
  "action": "get",
  "token": "wikcnXXX"
}

// 4. Read wiki page content (via document token)
{
  "tool": "feishu_doc",
  "action": "read",
  "doc_token": "obj_token_from_wiki"
}
```

### 5. File Management
```json
// 1. List folder contents
{
  "tool": "feishu_drive",
  "action": "list",
  "folder_token": "fldcnXXX"
}

// 2. Create folder
{
  "tool": "feishu_drive",
  "action": "create_folder",
  "name": "Archive",
  "folder_token": "fldcnXXX"
}

// 3. Move file
{
  "tool": "feishu_drive",
  "action": "move",
  "file_token": "doxcnXXX",
  "type": "docx",
  "folder_token": "fldcnYYY"
}
```

## Error Handling Patterns

### Rate Limiting
- Feishu APIs have rate limits (varies by endpoint)
- Implement retry with exponential backoff
- Monitor `X-RateLimit-*` headers when available

### Common Errors
- `99991663` - No permission to access
- `99991664` - File not found
- `99991665` - Invalid parameter
- `99991672` - Rate limit exceeded

### Permission Requirements
Ensure your Feishu app has these scopes:
- Documents: `docx:document`
- Wiki: `wiki:wiki`  
- Bitable: `bitable:app`
- Drive: `drive:drive`

## Performance Tips

1. **Batch operations**: When updating multiple documents, consider batch processing
2. **Cache tokens**: Document/wiki tokens don't change frequently
3. **Pagination**: Use `page_size` and `page_token` for large datasets
4. **Async processing**: For long-running tasks, use background processing

## Integration Examples

### Document + Bitable Sync
1. Query Bitable for updated records
2. Generate markdown report
3. Create/update document
4. Update Bitable with document link

### Wiki + Drive Backup
1. List all wiki pages
2. Export each to markdown
3. Create backup folder in Drive
4. Upload backup files

### Cross-Space Migration
1. List source space documents
2. Read content and metadata
3. Create in target space
4. Update links and references
