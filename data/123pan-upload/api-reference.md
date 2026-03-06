# 123pan API Reference

Complete API documentation for 123pan OpenAPI.

Base URL: `https://open-api.123pan.com`

## Authentication

All requests require:
- Header `Authorization: Bearer {access_token}`
- Header `Platform: open_platform`

## Upload Workflow

### 1. Get Upload Domain

**GET** `/api/v1/oss/domain`

Returns the upload server domain to use for file uploads.

Response:
```json
{
  "code": 0,
  "data": {
    "domain": "https://open-api-upload.123pan.com"
  }
}
```

### 2. Single-Step Upload (<1GB)

**POST** `{upload_domain}/upload/v2/file/single/create`

For small files, upload in a single request.

Parameters:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| parentFileID | number | Yes | Parent folder ID (0 for root) |
| filename | string | Yes | File name (<256 chars, no \/:*?\|><) |
| etag | string | Yes | MD5 hash of file |
| size | number | Yes | File size in bytes |
| duplicate | number | No | 1=keep both, 2=overwrite (default: 1) |
| file | file | Yes | The file content |

Response:
```json
{
  "code": 0,
  "data": {
    "fileID": 12345678,
    "completed": true
  }
}
```

### 3. Create File (Multi-step, >1GB)

**POST** `/upload/v2/file/create`

Initialize a chunked upload session.

Parameters:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| parentFileID | number | Yes | Parent folder ID |
| filename | string | Yes | File name |
| etag | string | Yes | MD5 hash |
| size | number | Yes | File size in bytes |
| duplicate | number | No | 1=keep both, 2=overwrite |
| containDir | bool | No | Whether filename contains path |

Response:
```json
{
  "code": 0,
  "data": {
    "fileID": 0,
    "preuploadID": "xxx",
    "reuse": false,
    "sliceSize": 16777216,
    "servers": ["http://xxx.123242.com"]
  }
}
```

### 4. Upload Slice

**POST** `{upload_server}/upload/v1/file/slice`

Upload file chunks. Chunk size must match `sliceSize` from create response.

### 5. Complete Upload

**POST** `/upload/v2/file/upload_complete`

Finalize the upload after all chunks are uploaded.

Parameters:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| preuploadID | string | Yes | The preupload ID from create |

Response:
```json
{
  "code": 0,
  "data": {
    "completed": true,
    "fileID": 12345678
  }
}
```

## Direct Link APIs

### Enable Direct Link on Folder

**POST** `/api/v1/direct-link/enable`

Enable direct link capability on a folder.

Parameters:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| fileID | number | Yes | The folder ID to enable |

Response:
```json
{
  "code": 0,
  "data": {
    "filename": "folder_name"
  }
}
```

### Get Direct Link URL

**GET** `/api/v1/direct-link/url?fileID={file_id}`

Get the direct download URL for a file.

Response:
```json
{
  "code": 0,
  "data": {
    "url": "https://vip.123pan.cn/xxx/xxx/filename"
  }
}
```

## Error Codes

- `0`: Success
- Non-zero: Various error conditions (see response message)
