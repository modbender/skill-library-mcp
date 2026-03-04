---
name: openkm-rest
description: OpenKM Document Management via REST API (folders, documents, metadata, versioning, search, workflows)
metadata:
  openclaw:
    emoji: "📁"
    requires:
      bins: ["python"]
      env:
        - OPENKM_BASE_URL
        - OPENKM_USERNAME
        - OPENKM_PASSWORD
    primaryEnv: OPENKM_BASE_URL
user-invocable: true
disable-model-invocation: false
---

# OpenKM REST Skill

This skill provides a **local CLI** that accesses OpenKM **exclusively via REST**
(no SOAP, no CMIS).

The agent uses **shell calls** to `openkm_cli.py`.

## Environment Variables (Required)

```bash
OPENKM_BASE_URL=https://openkm.example.com   # WITHOUT /OpenKM
OPENKM_USERNAME=okm_admin
OPENKM_PASSWORD=secret
```

## Folder Operations

### List folder contents
```bash
python3 openkm_cli.py list --folder-path /okm:root
```

### Create folder structure
Creates parent folders if they don't exist:
```bash
python3 openkm_cli.py ensure-structure --parts Folder1 Subfolder
```

## Document Operations

### Upload document
```bash
python3 openkm_cli.py upload --okm-path /okm:root/Folder/file.pdf --local-path /path/file.pdf
```

### Download document
```bash
python3 openkm_cli.py download --doc-id <uuid> --local-path /path/file.pdf
```

### Move document
Move a document to another folder (using folder UUID as target):
```bash
python3 openkm_cli.py move --doc-id <doc-uuid> --target-path <folder-uuid>
```

### Rename document
```bash
python3 openkm_cli.py rename --doc-id <uuid> --new-name new_filename.pdf
```

### Delete document
```bash
python3 openkm_cli.py delete --doc-id <uuid>
```

## Metadata & Organization

### Get document properties
Shows title, description, keywords, categories, and other metadata:
```bash
python3 openkm_cli.py properties --doc-id <uuid>
```

### Set title and description
```bash
python3 openkm_cli.py set-properties --doc-id <uuid> --title "My Title" --description "My description"
```

### Add keyword
```bash
python3 openkm_cli.py add-keyword --doc-id <uuid> --keyword "Invoice"
```

### Remove keyword
```bash
python3 openkm_cli.py remove-keyword --doc-id <uuid> --keyword "Invoice"
```

### Add category
Category ID can be a UUID or path (e.g., `/okm:categories/Finance`):
```bash
python3 openkm_cli.py add-category --doc-id <uuid> --category-id <category-uuid-or-path>
```

### Remove category
```bash
python3 openkm_cli.py remove-category --doc-id <uuid> --category-id <category-uuid-or-path>
```

## Versioning

### Get version history
```bash
python3 openkm_cli.py versions --doc-id <uuid>
```

### Download specific version
```bash
python3 openkm_cli.py download-version --doc-id <uuid> --version 1.0 --local-path /path/file_v1.pdf
```

### Restore version
Restores document to a previous version:
```bash
python3 openkm_cli.py restore-version --doc-id <uuid> --version 1.0
```

## Search

### Search by content (full-text)
```bash
python3 openkm_cli.py search-content --content "invoice hosting"
```

### Search by filename
```bash
python3 openkm_cli.py search-name --name "hetzner"
```

### Search by keywords
```bash
python3 openkm_cli.py search-keywords --keywords "Invoice,Hosting"
```

### General search with filters
```bash
python3 openkm_cli.py search --content "server" --author "john.doe" --path "/okm:root"
```

## Workflows

> **Note:** Workflow features require workflows to be configured in OpenKM. 
> If workflows are not enabled, these commands will return 404.

### List available workflows
```bash
python3 openkm_cli.py workflows
python3 openkm_cli.py workflows --name "approval"
```

### Start a workflow
```bash
python3 openkm_cli.py start-workflow --workflow-uuid <workflow-uuid> --doc-id <doc-uuid>
```

### List tasks
```bash
# Tasks for a document
python3 openkm_cli.py tasks --doc-id <uuid>

# Tasks for an actor
python3 openkm_cli.py tasks --actor-id john.doe
```

### Complete a task
```bash
python3 openkm_cli.py complete-task --task-id <task-id> --transition "approve"
```

### Add comment to task
```bash
python3 openkm_cli.py comment-task --task-id <task-id> --message "Review complete"
```

### Assign task to actor
```bash
python3 openkm_cli.py assign-task --task-id <task-id> --actor-id john.doe
```

## Notes

- The API expects `Content-Type: application/xml` for POST requests with path as body
- Paths must be URL-encoded when passed as query parameters
- The `fldId`, `docId`, `dstId`, `nodeId`, `catId` parameters accept either UUIDs or paths (e.g., `/okm:root/Folder`)
- For move operations, the `target-path` should be the UUID of the destination folder
- For rename operations, provide only the new filename (not full path)
- Keywords are free-form text tags; categories are predefined in OpenKM
- Version names are typically numbers like `1.0`, `1.1`, `2.0`, etc.
- Search results include a relevance score
- Workflow features require proper workflow configuration in OpenKM

## API Reference

The skill uses the OpenKM 6.3 REST API endpoints:

**Folders:**
- `GET /folder/getChildren` - List folder contents
- `POST /folder/createSimple` - Create folder

**Documents:**
- `POST /document/createSimple` - Upload document
- `GET /document/getContent` - Download document
- `GET /document/getProperties` - Get document metadata
- `PUT /document/setProperties` - Update title/description
- `PUT /document/move` - Move document
- `PUT /document/rename` - Rename document
- `DELETE /document/delete` - Delete document

**Versioning:**
- `GET /document/getVersionHistory` - Get version history
- `PUT /document/restoreVersion` - Restore to version
- `GET /document/getContentByVersion` - Download specific version

**Properties/Metadata:**
- `POST /property/addKeyword` - Add keyword
- `DELETE /property/removeKeyword` - Remove keyword
- `POST /property/addCategory` - Add category
- `DELETE /property/removeCategory` - Remove category

**Search:**
- `GET /search/find` - General search with filters
- `GET /search/findByContent` - Full-text search
- `GET /search/findByName` - Filename search
- `GET /search/findByKeywords` - Keyword search

**Workflows:**
- `GET /workflow/getAllProcessDefinitions` - List workflows
- `GET /workflow/getAllProcessDefinitionsByName` - Find workflow by name
- `POST /workflow/runProcessDefinition` - Start workflow
- `GET /workflow/findTaskInstances` - Get tasks by document
- `GET /workflow/findTaskInstancesByActor` - Get tasks by actor
- `POST /workflow/setTaskInstanceValues` - Complete task
- `POST /workflow/addTaskInstanceComment` - Add comment
- `POST /workflow/setTaskInstanceActor` - Assign task
