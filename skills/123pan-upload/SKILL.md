---
name: 123pan-upload
description: Upload files to 123pan (123云盘) and generate shareable links. Use when users need to upload files to 123pan and get links for sharing. Supports short share links (privacy-friendly) or direct download links. Works with small files (under 1GB) via single-step upload.
---

# 123pan-upload

Upload files to 123云盘 and generate shareable links. Supports both short links (privacy-friendly) and direct download links.

## Quick Start

```bash
# Default: returns short share link (recommended)
python scripts/upload.py --file /path/to/file

# Get direct link instead
python scripts/upload.py --file /path/to/file --short-link=false
```

## Configuration

Required environment variables:

```bash
export PAN123_ACCESS_TOKEN="your_access_token"
export PAN123_DIRECT_FOLDER_ID="your_folder_id"
```

- `access_token`: Get from <https://www.123pan.com/dashboard/dev>
- `folder_id`: The numeric ID of a folder with direct link enabled

## Usage

### Default (Short Link)

Returns privacy-friendly short link:
```bash
python scripts/upload.py --file /path/to/file.txt
# Output: https://www.123pan.com/s/xxxxx
```

### Direct Link (Long URL)

Returns direct download link (contains user ID in URL):
```bash
python scripts/upload.py --file /path/to/file.txt --short-link=false
```

### Specify Target Folder

```bash
python scripts/upload.py --file /path/to/file.txt --folder 30767843
```

## Output Format

### Short Link (Default)
```json
{
  "success": true,
  "file_id": 12345678,
  "filename": "example.zip",
  "size": 10485760,
  "link": "https://www.123pan.com/s/xxxxx",
  "link_type": "short_link"
}
```

### Direct Link
```json
{
  "success": true,
  "file_id": 12345678,
  "filename": "example.zip",
  "size": 10485760,
  "link": "https://xxx.v.123pan.cn/xxx/xxx/example.zip",
  "link_type": "direct_link"
}
```

## API Workflow

1. **Get upload domain** - Call `/upload/v2/file/domain` to get upload server
2. **Upload file** - POST to `/upload/v2/file/single/create` (<1GB files)
3. **Create share link** (default) - POST `/api/v1/share/create` for short link
4. **Get direct link** (optional) - GET `/api/v1/direct-link/url?fileID={id}`

## Privacy Note

- **Short links** (`--short-link`): Privacy-friendly format, no user ID exposed in URL
- **Direct links**: Contain user ID and full path, less private but allows direct download

## Limitations

- Single upload limit: 1GB per file
- Requires folder with direct link enabled

## References

- API details: [references/api-reference.md](references/api-reference.md)
