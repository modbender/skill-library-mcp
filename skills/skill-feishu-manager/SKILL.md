---
name: skill-feishu-manager
description: |
  Comprehensive Feishu (飞书) management toolkit for documents, knowledge bases, bitables, and cloud storage.
---

# Feishu Manager Skill

Complete toolkit for managing Feishu workspace.

## Tools Used

- feishu_doc - Document operations
- feishu_wiki - Knowledge base operations  
- feishu_bitable_* - Table operations
- feishu_drive - Cloud storage operations

## Quick Reference

### Documents
- Read: feishu_doc { "action": "read", "doc_token": "ABC123" }
- Create: feishu_doc { "action": "create", "title": "New Doc" }
- Write: feishu_doc { "action": "write", "doc_token": "ABC123", "content": "# Title" }

### Wiki
- List spaces: feishu_wiki { "action": "spaces" }
- Create page: feishu_wiki { "action": "create", "space_id": "...", "title": "Page" }

### Bitable
- Create table: feishu_bitable_create_app { "name": "Project" }
- List records: feishu_bitable_list_records { "app_token": "...", "table_id": "..." }

### Drive
- List folder: feishu_drive { "action": "list", "folder_token": "..." }
- Create folder: feishu_drive { "action": "create_folder", "name": "New" }

## Permissions Required

- docx:document
- wiki:wiki
- drive:drive
- bitable:data
