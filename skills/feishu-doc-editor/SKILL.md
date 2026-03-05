---
name: feishu-doc-editor
description: Feishu document creation and editing operations using OpenAPI. Activate when user needs to create, edit, or read Feishu documents programmatically.
---

# Feishu Document Editor Skill

This skill provides comprehensive guidance for creating and editing Feishu documents using the Feishu OpenAPI.

## Prerequisites

### 1. App Creation and Configuration

**Create enterprise self-built app**: Login to Feishu Open Platform, create an app and add "Bot" capability.

**Apply for API permissions**: In "Permission Management", apply for the following permissions:
- Document editing: `docx:document:write_only`
- Document viewing: `docx:document:readonly`

**Publish app**: Submit version and publish, ensuring the app coverage includes target users/departments.

### 2. Get Access Token

Call the self-built app get tenant_access_token interface:

```bash
curl -X POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal \
  -H "Content-Type: application/json" \
  -d '{"app_id": "your_app_id", "app_secret": "your_app_secret"}'
```

Response example:

```json
{
  "code": 0,
  "tenant_access_token": "t-xxx",
  "expire": 7200
}
```

## Core Operations

### Extract Document ID

Get `document_id` from document URL:

**Example URL**: `https://bigdatacenter.feishu.cn/docx/HpK2dtGu9omhMAxV12zcB6i7ngd`

**document_id** = `HpK2dtGu9omhMAxV12zcB6i7ngd`

### Grant App Document Permission

**Manually add collaborator**:
- Open document in Feishu client → Click "..." in top right → "More" → "Add document app"
- Search and add your app, grant "Can edit" permission.

### Write Text Content

**Interface**: Create Block

- **Path parameters**: `document_id` = document ID, `block_id` = document ID (root node is the document itself)
- **Request headers**:
  ```http
  Authorization: Bearer {tenant_access_token}
  Content-Type: application/json
  ```

- **Request body example** (write "hello"):
  ```json
  {
    "index": -1,
    "children": [
      {
        "block_type": 2,
        "text": {
          "elements": [
            {
              "text_run": {
                "content": "hello"
              }
            }
          ]
        }
      }
    ]
  }
  ```

### Read Document Content

**Interface**: Get Document Plain Text

```bash
curl -X GET "https://open.feishu.cn/open-apis/docx/v1/documents/{document_id}/plaintext" \
  -H "Authorization: Bearer {tenant_access_token}"
```

Response example:

```json
{
  "code": 0,
  "data": {
    "content": "Document text content here"
  }
}
```

## Common Issues

### 1. Permission Error (403 Forbidden)

- **Diagnosis**: App not added as document collaborator, or `tenant_access_token` is invalid.
- **Solution**: Re-add app as collaborator, or re-get `tenant_access_token`.

### 2. Missing Access Token (99991661)

- **Diagnosis**: Request header does not carry `Authorization: Bearer {token}`.
- **Solution**: Ensure `tenant_access_token` is correctly added to request header.

### 3. Document Not Found (404 Not Found)

- **Diagnosis**: `document_id` is incorrect or document has been deleted.
- **Solution**: Re-extract `document_id` from document URL.

## Reference Documentation

- Create Block Interface
- Get Document Plain Text Interface
- Permission Configuration Guide

Through the above steps, you can achieve editing Feishu documents via API, supporting add/delete/modify/query operations for multiple content types including text, tables, and images.
