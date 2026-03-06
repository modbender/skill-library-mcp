---
name: meegle-api-work-item-attachment
description: |
  Meegle OpenAPI for work item attachment operations.
metadata:
  openclaw: {}
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
description: >
  Add an attachment to an attachment field under a specified work item.
  One file per request; max 100M. Attachment field limit 50 files.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/file/upload
  headers:
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"
  content_type: multipart/form-data

path_params:
  project_key:
    type: string
    required: true
    description: >
      Space ID (project_key) or space domain name (simple_name).
      project_key: Double-click space name in Meegle.
      simple_name: From space URL, e.g. https://meegle.com/doc/overview → doc.
  work_item_type_key:
    type: string
    required: true
    description: >
      Work item type. Obtainable via "Get work item types in the space".
      Must match the work item instance identified by work_item_id.
  work_item_id:
    type: string
    required: true
    description: Work item instance ID. In work item details, click ··· in the upper right, then ID to copy.

inputs:
  file:
    type: file
    required: true
    description: >
      Attachment file. Only one attachment per request; max size 100M.
  field_key:
    type: string
    required: false
    description: >
      Unique identifier of the attachment upload field. Pass either field_key or field_alias.
  field_alias:
    type: string
    required: false
    description: >
      Docking identifier for the attachment upload field. Pass either field_key or field_alias.
  index:
    type: string
    required: false
    description: For composite fields, used to specify the array subscript.

outputs:
  description: Success returns err_code 0.

constraints:
  - Permission: Developer Platform – Permissions / Permission Management
  - One file per request; max 100M per file
  - Attachment field limit: 50 files per field
  - Use multipart/form-data; set MimeType correctly for preview

error_mapping:
  1000050255: Project not found (project_key incorrect)
  1000050174: Uploaded file size limit 100M (file exceeds 100M)
  1000050190: Request form is null (form parameters invalid)
  1000050262: Upload file fail
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
description: >
  General file upload that returns the resource path (URL).
  Mainly used for uploading images in rich text. Max 100M per file.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/{project_key}/file/upload
  headers:
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"
  content_type: multipart/form-data

path_params:
  project_key:
    type: string
    required: true
    description: >
      Space ID (project_key) or space domain name (simple_name).
      project_key: Double-click space name in Meegle.
      simple_name: From space URL, e.g. https://meegle.com/doc/overview → doc.

inputs:
  file:
    type: file
    required: true
    description: Attachment file. Max size 100M.

outputs:
  data:
    type: string
    description: Attachment link (resource URL) to use in rich text or elsewhere.

constraints:
  - Permission: Permission Management – Work Item Instance
  - Max file size 100M

error_mapping:
  30016: Project not found (project_key incorrect)
  1000050174: Uploaded file size limit 100M (file exceeds 100M)
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
description: >
  Download a specified attachment under a work item.
  Returns a binary file stream. Max supported size 100M.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/file/download
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

path_params:
  project_key:
    type: string
    required: true
    description: >
      Space ID (project_key) or space domain name (simple_name).
      project_key: Double-click space name in Meegle.
      simple_name: From space URL, e.g. https://meegle.com/doc/overview → doc.
  work_item_type_key:
    type: string
    required: true
    description: >
      Work item type. Obtainable via "Get work item types in the space".
      Must match the work item instance identified by work_item_id.
  work_item_id:
    type: string
    required: true
    description: Work item instance ID. In work item details, click ··· in the upper right, then ID to copy.

inputs:
  uuid:
    type: string
    required: true
    description: >
      Attachment ID. Obtain from the rich text (multi_texts) or attachment field
      (multi_file) in the Get Work Item Details response. Max supported size 100M.

outputs:
  description: Binary file stream (the attachment content).

constraints:
  - Permission: Permission Management – Work Item Instance
  - Max download size 100M

error_mapping:
  1000050255: Project not found (project_key incorrect)
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
description: >
  Delete one or more attachments from an attachment-type field of a specified work item.
  Pass exactly one of field_key or field_alias to identify the target field.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/file/delete
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

inputs:
  work_item_id:
    type: integer
    required: true
    description: >
      Work item instance ID. In work item details, expand ··· > ID in the upper right to obtain.
  project_key:
    type: string
    required: true
    description: >
      Space ID (project_key) or space domain name (simple_name).
      project_key: Double-click space name in Meegle/Feishu project space.
      simple_name: From space URL, e.g. https://project.feishu.cn/doc/overview → doc.
  field_key:
    type: string
    required: false
    description: >
      Attachment field ID. Obtain via Get Work Item Creation Metadata.
      Supports composite sub-fields. Pass either field_key or field_alias, not both and not neither.
  field_alias:
    type: string
    required: false
    description: >
      Docking identifier of the attachment field. Obtain via Get Work Item Creation Metadata.
      Supports composite sub-fields. Pass either field_key or field_alias, not both and not neither.
  uuids:
    type: array
    items: string
    required: true
    description: >
      List of attachment UUIDs to delete. Obtain from the attachment field (multi_file type)
      in the Get Work Item Details response.

outputs:
  data:
    type: object
    description: Empty object on success.

constraints:
  - Permission: Permission Management – Work Item Instances
  - Exactly one of field_key or field_alias must be provided (not both, not neither)

error_mapping:
  30019: File not found (specified file does not exist or cannot be accessed)
```

### Usage notes

- **work_item_id**, **project_key**: Identify the work item and space.
- **field_key** or **field_alias**: Provide exactly one to specify the attachment field.
- **uuids**: List of attachment UUIDs from Get Work Item Details (multi_file field).
