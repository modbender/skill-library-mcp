---
name: detect-file-type-local
version: 0.2.0
description: Local, offline AI-powered file type detection — no network, no API keys
homepage: https://github.com/pgeraghty/openclaw-detect-file-type-local
metadata:
  openclaw:
    requires:
      bins: [python3]
    install:
      - kind: uv
        package: detect-file-type-local
        bins: [detect_file_type]
---

# Detect File Type - Local

**Local-only, offline file type detection.** Uses an embedded ML model (Google Magika) to identify 214 file types by content — no network calls, no API keys, no data leaves the machine. All inference runs on-device via ONNX Runtime.

## When to Use

- Identify unknown files by their content (not just extension) — **locally, without sending data anywhere**
- Verify that a file's extension matches its actual content
- Check MIME types before processing uploads or downloads
- Triage files in a directory by type
- Detect extension mismatches and masquerading (e.g., `.pdf.exe`, `.xlsx.lnk`)
- Flag suspicious polyglot-style payloads (for example PDF/ZIP or PDF/HTA-style chains)
- When privacy matters — file bytes never leave the local machine

## Installation

```bash
pip install detect-file-type-local
```

From source:

```bash
pip install -e /path/to/detect-file-type-skill
```

## Usage

### Single file
```bash
detect_file_type path/to/file
```

### Multiple files
```bash
detect_file_type file1.pdf file2.png file3.zip
```

### Recursive directory scan
```bash
detect_file_type --recursive ./uploads/
```

### From stdin
```bash
cat mystery_file | detect_file_type -

# Optional best-effort fast path (head only)
cat mystery_file | detect_file_type --stdin-mode head --stdin-max-bytes 1048576 -
```

### Output formats
```bash
detect_file_type --json file.pdf    # JSON (default)
detect_file_type --human file.pdf   # Human-readable
detect_file_type --mime file.pdf    # Bare MIME type
```

### Programmatic (Python)
```python
python -m detect_file_type path/to/file
```

## Output Schema (JSON)

Single file returns an object; multiple files return an array.

```json
{
  "path": "document.pdf",
  "label": "pdf",
  "mime_type": "application/pdf",
  "score": 0.99,
  "group": "document",
  "description": "PDF document",
  "is_text": false
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `path` | string | Input path (or `-` for stdin) |
| `label` | string | Detected file type label (e.g., `pdf`, `png`, `python`) |
| `mime_type` | string | MIME type (e.g., `application/pdf`) |
| `score` | float | Confidence score (0.0–1.0) |
| `group` | string | Category (e.g., `document`, `image`, `code`) |
| `description` | string | Human-readable description |
| `is_text` | bool | Whether the file is text-based |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All files detected successfully |
| 1 | Fatal error (no results produced) |
| 2 | Partial failure (some files failed, some succeeded) |

## Error Handling

Errors are printed to stderr. Common cases:
- **File not found**: `error: path/to/file: No such file or directory`
- **Permission denied**: `error: path/to/file: Permission denied`
- **Not a regular file**: `error: path/to/dir: Not a regular file`

When processing multiple files, detection continues for remaining files even if some fail.

## Limitations

- Default stdin mode (`spool`) writes stdin to a temporary file and uses Magika path detection.
- `--stdin-mode head` is best effort and may miss trailing-byte signatures.
- Very small files (< ~16 bytes) may produce low-confidence results
- Empty files are detected as `empty`
- Detection is content-based — file extensions are ignored

## Security Context

- [MITRE ATT&CK: Masquerading](https://attack.mitre.org/techniques/T1036/)
- [Proofpoint: Call It What You Want, Threat Actor Delivers Highly Targeted Multistage Polyglot](https://www.proofpoint.com/us/blog/threat-insight/call-it-what-you-want-threat-actor-delivers-highly-targeted-multistage-polyglot)
