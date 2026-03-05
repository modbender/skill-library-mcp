# Provider-Specific Patterns

## Object Storage (S3-compatible)

### AWS S3
- **Presigned URLs** — v4 signatures required; include `Content-Type` for uploads
- **Eventual consistency** — `PUT` then immediate `GET` may 404; wait or use strong consistency regions
- **Lifecycle rules** — transition conflicts with delete; check rule order

### Google Cloud Storage
- **Signed URLs** — use `signBlob` IAM permission; service account required
- **Object holds** — legal hold blocks deletion even by owner
- **Composite objects** — max 32 components per compose operation

### Azure Blob
- **SAS tokens** — account-level vs container-level vs blob-level scope
- **Hot/Cool/Archive** — archive retrieval takes hours; plan ahead
- **Soft delete** — enabled by default on new accounts; check retention

### Backblaze B2
- **S3-compatible API** — most S3 tools work; use `s3.region.backblazeb2.com` endpoint
- **Application keys** — bucket-restricted keys for least privilege
- **Minimum file size** — small files charged as 10KB minimum

### Cloudflare R2
- **No egress fees** — major cost advantage for serving content
- **S3 compatibility** — most operations work; some advanced features missing
- **Workers integration** — can access R2 without egress via Workers

---

## Consumer/Prosumer Storage

### Google Drive
- **Shortcuts vs files** — shortcuts don't copy; operations on shortcuts affect original
- **Shared drives** — different ownership model; files owned by organization
- **API quotas** — 10 queries/second/user; batch requests help
- **Export formats** — Google Docs download as DOCX/PDF, not native format

### Dropbox
- **Team folders** — admin controls override user permissions
- **Paper docs** — separate from regular files; different API
- **Selective sync** — `.dropbox` files appear when excluded
- **2GB file limit** — API upload; desktop client handles larger via chunked

### OneDrive / SharePoint
- **Personal vs Business** — different APIs, quotas, features
- **Conflict handling** — renames to `file (1).txt` automatically
- **SharePoint libraries** — complex permission inheritance
- **Delta sync** — use delta API for efficient change detection

### iCloud
- **No public API** — use CloudKit for app data, not file access
- **Optimized storage** — files may be stubs; download before operations
- **Family sharing** — shared folder permissions are limited
