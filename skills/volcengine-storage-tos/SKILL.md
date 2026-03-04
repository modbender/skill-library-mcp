---
name: volcengine-storage-tos
description: Object storage operations for Volcengine TOS. Use when users need upload/download/sync, bucket policy checks, signed URLs, or storage troubleshooting.
---

# volcengine-storage-tos

Manage TOS buckets and objects with explicit path mapping and permission verification.

## Execution Checklist

1. Confirm bucket, region, and object paths.
2. Validate auth and bucket policy.
3. Execute upload/download/sync task.
4. Return result manifest with object keys and URLs.

## Safety Rules

- Avoid destructive deletes without explicit confirmation inputs.
- Preserve metadata and content type on uploads.
- Provide checksum or size verification where possible.

## References

- `references/sources.md`
