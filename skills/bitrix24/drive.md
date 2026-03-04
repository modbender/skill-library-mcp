# Drive (Files)

**Important:** File operations require the `disk` scope in the webhook/app permissions.

## Storages

```bash
# List all storages
curl -s "${BITRIX24_WEBHOOK_URL}disk.storage.getlist.json" | jq .result

# Get storage by ID
curl -s "${BITRIX24_WEBHOOK_URL}disk.storage.get.json" -d 'id=1' | jq .result

# List root contents of a storage
curl -s "${BITRIX24_WEBHOOK_URL}disk.storage.getchildren.json" -d 'id=1' | jq .result
```

**Storage types:** `common` (shared), `user` (personal per user), `group` (workgroup).

## Folders

```bash
# List folder contents
curl -s "${BITRIX24_WEBHOOK_URL}disk.folder.getchildren.json" -d 'id=123' | jq .result

# Create folder
curl -s "${BITRIX24_WEBHOOK_URL}disk.folder.addsubfolder.json" \
  -d 'id=123&data[NAME]=New Folder' | jq .result

# Upload file to folder
curl -s "${BITRIX24_WEBHOOK_URL}disk.folder.uploadfile.json" \
  -d 'id=123&data[NAME]=report.pdf&fileContent[0]=report.pdf&fileContent[1]=<base64_content>' | jq .result

# Delete folder (to trash)
curl -s "${BITRIX24_WEBHOOK_URL}disk.folder.markdeleted.json" -d 'id=123' | jq .result

# Rename folder
curl -s "${BITRIX24_WEBHOOK_URL}disk.folder.rename.json" \
  -d 'id=123&newName=Renamed Folder' | jq .result
```

## Files

```bash
# Get file info
curl -s "${BITRIX24_WEBHOOK_URL}disk.file.get.json" -d 'id=456' | jq .result

# Upload file to storage root
curl -s "${BITRIX24_WEBHOOK_URL}disk.storage.uploadfile.json" \
  -d 'id=1&data[NAME]=document.txt&fileContent[0]=document.txt&fileContent[1]=<base64_content>' | jq .result

# Delete file (to trash)
curl -s "${BITRIX24_WEBHOOK_URL}disk.file.markdeleted.json" -d 'id=456' | jq .result

# Rename file
curl -s "${BITRIX24_WEBHOOK_URL}disk.file.rename.json" \
  -d 'id=456&newName=new_name.pdf' | jq .result

# Move file to another folder
curl -s "${BITRIX24_WEBHOOK_URL}disk.file.moveto.json" \
  -d 'id=456&targetFolderId=789' | jq .result

# Copy file
curl -s "${BITRIX24_WEBHOOK_URL}disk.file.copyto.json" \
  -d 'id=456&targetFolderId=789' | jq .result

# Restore from trash
curl -s "${BITRIX24_WEBHOOK_URL}disk.file.restore.json" -d 'id=456' | jq .result
```

## Publishing Files to Chat

To send a file into a Bitrix24 chat (requires `im` scope):

```bash
# Step 1: Upload to disk storage
curl -s "${BITRIX24_WEBHOOK_URL}disk.storage.uploadfile.json" \
  -d 'id=1&data[NAME]=photo.jpg&fileContent[0]=photo.jpg&fileContent[1]=<base64>' | jq .result
# → returns file with ID, e.g. "ID": "42"

# Step 2: Commit file to chat
curl -s "${BITRIX24_WEBHOOK_URL}im.disk.file.commit.json" \
  -d 'CHAT_ID=100&UPLOAD_ID=42&MESSAGE=Check this file' | jq .result
```

## File Download

The `DOWNLOAD_URL` from `disk.file.get` requires authentication. Append `&auth=<token>` to the URL when downloading programmatically.

## Reference

**File fields:** ID, NAME, SIZE, CODE, STORAGE_ID, TYPE (file/folder), PARENT_ID, DOWNLOAD_URL, DETAIL_URL, CREATE_TIME, UPDATE_TIME, CREATED_BY, UPDATED_BY.

**Upload format:** `fileContent` is an array of `[filename, base64_encoded_content]`.

## More Methods (MCP)

This file covers common drive methods. For additional methods or updated parameters, use MCP:
- `bitrix-search "disk file"` — find all file-related methods
- `bitrix-search "disk storage"` — find storage methods
- `bitrix-method-details disk.file.get` — get full spec for any method
