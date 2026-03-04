---
name: meegle-api-work-item-attachment
description: Meegle OpenAPI for work item attachment operations.
metadata: { openclaw: {} }
---

# Meegle API — Attachment

Work item attachment related APIs for uploading, listing, and managing attachments on work items.

## Scope

- Upload attachment to work item
- List attachments
- Download or delete attachments
- Related attachment endpoints

---

## Add Attachment

Add an attachment to an attachment field under a specified work item. One file per request; max 100M per file. Attachment-type fields have a limit of 50 files.

### Points to Note

1. **If the interface responds successfully but no files are visible on the page**, check the content of the file field in the form. If the file is empty, it may not be intercepted.
2. **When the browser cannot display the attachment preview**, check the **MimeType** set during upload and use a MimeType that matches the file type (e.g. JPEG: `image/jpeg`, MP4 audio: `audio/mp4`, MP4 video: `video/mp4`).
3. **The attachment quantity limit for an Attachment-type field is 50.** Adding new attachments when the count exceeds 50 will fail.

### When to Use

- When uploading a file to a work item’s attachment field
- When adding files to a specific field by field_key or field_alias
- When uploading to a composite field (use index to specify array subscript)

### API Spec: add_attachment

```yaml
name: add_attachment
type: api
description: Add attachment to work item field; one file per request max 100M; field limit 50 files; multipart/form-data.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/file/upload" }
headers: { X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string, work_item_type_key: string, work_item_id: string }
inputs: { file: { type: file, required: true }, field_key: string, field_alias: string, index: string }
outputs: {}
constraints: [Permission: Permissions, one file max 100M, 50 per field]
error_mapping: { 1000050255: Project not found, 1000050174: Size limit 100M, 1000050190: Form null, 1000050262: Upload fail }
```

### Usage notes

- **file**: Send as multipart/form-data; one file per request; max 100M.
- **field_key** or **field_alias**: Provide one to specify the target attachment field.
- **index**: Use for composite (compound) fields to specify array subscript.
- Set **MimeType** correctly (e.g. image/jpeg, video/mp4) so the browser can preview the attachment.

---

## Upload Files or Rich Text Images

General file upload that returns the resource path (URL) after uploading. Mainly used for uploading images in rich text content. Does not attach to a specific work item field; use the returned URL in rich text or elsewhere.

### When to Use

- When uploading images for use in rich text (e.g. comment or description)
- When needing a stable file URL to reference in content
- When uploading a file without binding it to a work item attachment field

### API Spec: upload_files_or_rich_text_images

```yaml
name: upload_files_or_rich_text_images
type: api
description: General file upload; returns resource URL; for rich text images; max 100M.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/{project_key}/file/upload" }
headers: { X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string }
inputs: { file: { type: file, required: true } }
outputs: { data: string }
constraints: [Permission: Work Item Instance, max 100M]
error_mapping: { 30016: Project not found, 1000050174: Size limit 100M }
```

### Usage notes

- **file**: Send as multipart/form-data; max 100M.
- **data**: Use the returned URL as the image or file link in rich text (e.g. comments, descriptions).

---

## Download Attachment

Download a specified attachment under a work item. The response is a binary file stream. Max supported size 100M.

### When to Use

- When downloading an attachment from a work item by its uuid
- When fetching file content from rich text (multi_texts) or attachment field (multi_file)
- When syncing or backing up work item attachments

### API Spec: download_attachment

```yaml
name: download_attachment
type: api
description: Download attachment by uuid; returns binary stream; max 100M.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/file/download" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string, work_item_type_key: string, work_item_id: string }
inputs: { uuid: { type: string, required: true } }
outputs: {}
constraints: [Permission: Work Item Instance, max 100M]
error_mapping: { 1000050255: Project not found }
```

### Usage notes

- **uuid**: Attachment ID from Get Work Item Details (multi_texts or multi_file field).
- Response body is a **binary file stream**; handle as file download in your client.

---

## Delete Attachment

Delete one or more attachments from an attachment-type field of a specified work item. Pass exactly one of field_key or field_alias to identify the target field.

### When to Use

- When removing attachments from a work item’s attachment field
- When cleaning up or replacing files in multi_file fields
- When syncing deletions from external systems

### API Spec: delete_attachment

```yaml
name: delete_attachment
type: api
description: Delete attachments from field; exactly one of field_key or field_alias; uuids from Get Work Item Details.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/file/delete" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
inputs: { work_item_id: integer, project_key: string, field_key: string, field_alias: string, uuids: { type: array, required: true } }
outputs: { data: object }
constraints: [Permission: Work Item Instances, one of field_key/field_alias]
error_mapping: { 30019: File not found }
```

### Usage notes

- **work_item_id**, **project_key**: Identify the work item and space.
- **field_key** or **field_alias**: Provide exactly one to specify the attachment field.
- **uuids**: List of attachment UUIDs from Get Work Item Details (multi_file field).
