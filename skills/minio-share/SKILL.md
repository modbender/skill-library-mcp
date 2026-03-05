---
name: minio-share
description: Upload files to MinIO object storage and generate shareable links with Markdown formatting. Use when users ask to send files, share files, upload files, download videos, or get a download link for files. Supports custom filenames from titles and provides formatted output with clickable links and media previews. Requires MINIO_API_URL, MINIO_CONSOLE_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, and MINIO_BUCKET environment variables.
---

# MinIO Share

Upload files to MinIO and generate shareable links for users with Markdown formatting.

## Requirements

Ensure these environment variables are set:
- `MINIO_API_URL` - MinIO S3 API endpoint (e.g., `https://minio-api.example.com`)
- `MINIO_CONSOLE_URL` - MinIO Web Console URL (e.g., `https://minio.example.com`)
- `MINIO_ACCESS_KEY` - MinIO access key
- `MINIO_SECRET_KEY` - MinIO secret key
- `MINIO_BUCKET` - Default bucket name for uploads

## Installation

Install the minio Python package if not already available:
```bash
pip install minio
```

## Usage

### Basic Upload

Upload a file with Markdown output:
```bash
python3 scripts/minio_upload.py /path/to/file.txt
```

### Use Title as Filename

Upload with a custom title (sanitized for safe filenames):
```bash
python3 scripts/minio_upload.py /path/to/video.mp4 --title "My Video Title"
```

This will save the file as `My_Video_Title.mp4` (special characters replaced with underscores).

### Custom Object Name

Specify a custom name for the uploaded object:
```bash
python3 scripts/minio_upload.py /path/to/file.txt --name custom-name.pdf
```

### Adjust Link Expiry

Change the presigned URL expiry time (default: 7 days):
```bash
python3 scripts/minio_upload.py /path/to/file.txt --expiry 30
```

### JSON Output

Get structured output:
```bash
python3 scripts/minio_upload.py /path/to/file.txt --json
```

### Plain Text Output

Get just the URL:
```bash
python3 scripts/minio_upload.py /path/to/file.txt
```

## Workflow

When a user asks to send/share/upload a file or download a video:

1. **Check environment variables** - Verify MINIO_* variables are set
2. **Download the file** (if it's a URL) to a temporary location
3. **Upload the file** using `scripts/minio_upload.py`:
   - For videos: Use `--title "Video Title"` to set a meaningful filename
   - For images: They will be displayed inline with Markdown
   - For videos: A video player will be included in the output
4. **Copy the Markdown output** to your response

## Filename Sanitization

When using `--title`, the script automatically:
- Replaces illegal characters (`< > : " / \ | ? *`) with underscores
- Collapses multiple spaces/underscores
- Trims to 100 characters max
- Preserves Chinese characters, letters, numbers

## Output Formats

### Markdown Output (Default)

Provides rich formatting with:
- File information (name, size, expiry)
- Inline image preview (for image files)
- Video player (for video files)
- Clickable download link
- Console preview link
- Plain text URL for copying

### Example Markdown Output

```markdown
📄 **文件名**: `sample.mp4`
📦 **大小**: 44.51 MB
⏱️ **链接有效期**: 7 天

🌐 **[sample.mp4](...)**
```

## Error Handling

Common issues:
- Missing environment variables - Check all MINIO_* vars are set
- Bucket doesn't exist - Ensure MINIO_BUCKET exists or create it first
- File not found - Verify the file path is correct
- Connection error - Check MINIO_API_URL is accessible
- SSL errors - Use `--insecure` flag if needed (not recommended for production)
