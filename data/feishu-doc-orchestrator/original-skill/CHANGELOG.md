# Changelog

## [v1.1.0] - 2026-02-13

### New Features

- **Image upload support**: Feishu document creation now supports automatic local image upload!
  - Use `![alt](D:/path/to/image.png)` syntax in Markdown
  - Parser auto-detects local paths and stores in `local_path` field
  - Block adder executes 3-step flow: create block -> upload file -> set token
  - Supported formats: `.png`, `.jpg`, `.jpeg`, `.gif`
  - Network image URLs display as links only, no file upload

### Fixes

- **Image path parsing**: Fixed `local_path` field retrieval (from block level instead of data)

---

## [Unversioned] - 2025-02-11

### Fixes

- **Table creation**: Fixed table cells having extra blank lines and misalignment.
