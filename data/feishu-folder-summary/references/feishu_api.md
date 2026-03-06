# Feishu API Reference

## Wiki API

### Get Wiki Node Info
```
feishu_wiki action="get" token="{node_token}"
```

Returns:
- node_token
- space_id
- obj_token (for documents)
- obj_type (docx, sheet, etc.)
- title
- has_child (boolean)
- parent_node_token

### List Child Nodes
```
feishu_wiki action="nodes" space_id="{space_id}" parent_node_token="{parent_token}"
```

Returns array of child nodes with:
- node_token
- obj_token
- obj_type
- title
- has_child

## Document API

### Read Document
```
feishu_doc action="read" doc_token="{obj_token}"
```

Returns:
- title
- content (text/markdown)
- revision_id
- block_count
- block_types

## URL Parsing

### Wiki URL Pattern
```
https://{domain}.feishu.cn/wiki/{node_token}
```

### Drive URL Pattern
```
https://{domain}.feishu.cn/drive/folder/{folder_token}
```

## Error Handling

Common errors:
- `403`: No permission to access document
- `404`: Document not found
- Empty content: Document has no text content
