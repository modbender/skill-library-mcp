---
name: evidenceops
description: Forensic media triage with chain of custody. Use when receiving images, videos, audio, PDFs, or documents that need evidence-grade handling, integrity verification, and audit trails.
version: 1.0.0
author: OpenClaw Community
metadata:
  openclaw:
    emoji: "🔬"
    tools:
      - evidence.ingest
      - evidence.verify
      - evidence.manifest
      - evidence.export
      - evidence.access_log
      - Read
      - Write
      - Bash
    install:
      npm: "@openclaw/evidence-vault"
    os:
      - darwin
      - linux
      - win32
    categories:
      - forensics
      - security
      - compliance
    tags:
      - evidence
      - chain-of-custody
      - forensic
      - integrity
      - audit
---

# EvidenceOps - Forensic Media Triage

## What It Does

EvidenceOps provides forensic-grade handling of media files with complete chain of custody:

1. **Media Intake** - Accept images, videos, audio, PDFs, and documents from any channel
2. **Immutable Storage** - Store originals in append-only vault with cryptographic hashes
3. **Metadata Extraction** - Extract EXIF, file properties, and media information without altering originals
4. **Derivative Generation** - Create thumbnails, transcripts, previews in separate folders
5. **Chain of Custody** - Maintain tamper-evident audit trail with hash chain
6. **Integrity Verification** - Verify evidence hasn't been modified post-ingest
7. **Audit Trail** - Complete JSONL audit log for compliance

## What It NEVER Does

- **NEVER** modifies original evidence files after ingest
- **NEVER** stores secrets, API keys, or credentials in manifests or logs
- **NEVER** accepts unsanitized paths from user input
- **NEVER** executes untrusted code or downloads remote scripts
- **NEVER** exfiltrates data to external services without explicit configuration
- **NEVER** bypasses channel allowlists or pairing requirements
- **NEVER** stores real personal data in example files

## Prerequisites

Before using this skill, ensure:

1. Plugin `@openclaw/evidence-vault` is installed and initialized
2. Vault storage directory is configured with appropriate permissions
3. Channel allowlist is configured for trusted sources only
4. Retention policies comply with your legal requirements

## Workflow

### Step 1: Receive Media

When media is received via any channel:

```
User sends: [image/video/document]
```

**Required Information:**
- File content (from attachment)
- Original filename
- Source channel (whatsapp, telegram, email, etc.)
- Sender identifier
- Message ID (if available)

### Step 2: Create or Select Case

```
IF user specifies existing caseId:
  USE that caseId
ELSE IF user requests new case:
  CREATE case with format: case-{YYYY}-{NNN}
  EXAMPLE: case-2026-001
ELSE:
  ASK user: "Should I create a new case or add to existing case [case-2026-XXX]?"
```

**Case ID Format:** `case-{year}-{sequence}`
- Must match pattern: `^case-[a-zA-Z0-9_-]+$`
- Examples: `case-2026-001`, `case-incident-alpha`, `case-legal-2026-q1`

### Step 3: Stage Original (Read-Only)

Before ingest:

1. **Save received file to temporary staging area**
2. **Calculate SHA-256 hash immediately**
3. **Record file size and MIME type**
4. **DO NOT modify the file**

```
# Staging directory structure
/tmp/evidence-staging/
├── {caseId}/
│   └── {timestamp}-{filename}
```

### Step 4: Extract Metadata

Extract metadata WITHOUT modifying original:

**For Images:**
- EXIF data (camera, GPS, timestamps)
- Dimensions
- Color profile

**For Videos:**
- Duration
- Codec information
- Resolution

**For Audio:**
- Duration
- Sample rate
- Codec

**For PDFs:**
- Page count
- Author (if embedded)
- Creation date

```
# Use Read tool or appropriate extraction commands
# NEVER write back to original file
```

### Step 5: Generate Derivatives (Optional)

Create derivative artifacts in SEPARATE folder:

```
derivatives/
├── thumbnails/
│   └── {evidenceId}-thumb.jpg
├── transcripts/
│   └── {evidenceId}-transcript.txt
└── previews/
    └── {evidenceId}-preview.pdf
```

**Derivative Types:**
- `thumbnail` - Reduced resolution image/video preview
- `transcript` - Speech-to-text for audio/video
- `preview` - PDF or text representation
- `ocr` - Extracted text from images

### Step 6: Ingest to Vault

Call the evidence.ingest tool:

```json
{
  "filePath": "/path/to/staged/file",
  "filename": "original-filename.jpg",
  "caseId": "case-2026-001",
  "channel": "whatsapp",
  "sender": "user@example.com",
  "messageId": "msg-abc123",
  "retentionDays": 2555,
  "metadata": {
    "exif": { ... },
    "extracted": { ... }
  }
}
```

**Response:**
```json
{
  "success": true,
  "evidenceId": "ev-abc123...",
  "sha256": "a1b2c3...",
  "vaultUrl": "file:///vault/cases/case-2026-001/originals/ev-abc123.jpg",
  "timestamp": "2026-02-17T10:30:00.000Z"
}
```

### Step 7: Update Manifest

The manifest is automatically updated by the ingest operation.

**Manifest Location:** `{vault}/cases/{caseId}/manifest.json`

**Manifest Contents:**
- Case metadata
- Evidence items with hashes
- Derivatives
- Chain of custody entries
- Retention policy

### Step 8: Return Receipt

Provide user with evidence receipt:

```
📋 EVIDENCE RECEIPT

Case ID: case-2026-001
Evidence ID: ev-abc123...
File: original-filename.jpg
SHA-256: a1b2c3d4e5f6...
Size: 1.2 MB
Received: 2026-02-17 10:30:00 UTC
Vault: file:///vault/cases/case-2026-001/originals/ev-abc123.jpg

✅ Chain of custody established
✅ Original preserved immutably
✅ Audit trail active
```

## Tool Reference

### evidence.ingest

Ingest a file into the evidence vault.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| filePath | string | Yes | Path to the staged file |
| filename | string | Yes | Original filename |
| caseId | string | Yes | Case identifier |
| channel | string | No | Source channel |
| sender | string | No | Sender identifier |
| messageId | string | No | Message ID from source |
| retentionDays | number | No | Retention period |
| metadata | object | No | Additional metadata |

**Returns:** `{ evidenceId, sha256, vaultUrl, timestamp }`

### evidence.verify

Verify evidence integrity.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| evidenceId | string | Yes | Evidence to verify |
| caseId | string | No | Limit search to case |

**Returns:** `{ verified, details: { originalIntact, hashMatch, lastVerifiedAt } }`

### evidence.manifest

Get case manifest.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| caseId | string | Yes | Case identifier |

**Returns:** Complete case manifest with all items

### evidence.export

Export case as archive.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| caseId | string | Yes | Case identifier |
| format | string | No | 'zip' or 'tar' (default: zip) |

**Returns:** `{ exportPath, sha256, size, itemCount }`

### evidence.access_log

Get audit trail.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| caseId | string | Yes | Case identifier |
| limit | number | No | Max events (default: 100) |

**Returns:** `{ events: [ ... ], count }`

## SECURITY POSTURE

### Channel Allowlist Configuration

Configure which channels can submit evidence:

```yaml
# ~/.openclaw/openclaw.json
{
  "plugins": {
    "evidence-vault": {
      "channelAllowlist": ["whatsapp", "telegram", "email"],
      "channelDenylist": ["public-discord"],
      "requirePairing": true
    }
  }
}
```

### Pairing Requirements

For Direct Messages (DMs):
- **REQUIRE** pairing before accepting evidence
- **BLOCK** unpaired DMs by default
- **LOG** rejected ingestion attempts

For Group Channels:
- **VERIFY** channel is in allowlist
- **REJECT** evidence from untrusted channels
- **NEVER** auto-ingest from public channels

### Path Sanitization Rules

ALL paths are validated:

1. **No path traversal** - `../` sequences rejected
2. **No null bytes** - `\0` rejected
3. **No home directory** - `~/` rejected
4. **Canonicalization** - Paths resolved before validation
5. **Base path check** - Must be within vault directory

**Violations result in:** `E_PATH_TRAVERSAL` error + audit log entry

### Destructive Action Confirmation

Before any potentially destructive operation:

1. **EXPORT** - Confirm export destination
2. **RETENTION DELETE** - Require explicit confirmation (if enabled)
3. **LEGAL HOLD RELEASE** - Require explicit confirmation

**Confirmation format:**
```
⚠️ DESTRUCTIVE ACTION

You are about to: [describe action]
Case: [caseId]
Items affected: [count]

Type "CONFIRM" to proceed:
```

### Secrets Handling

**NEVER include in logs or manifests:**
- API keys
- Passwords
- Tokens
- Credit card numbers
- Email addresses (redacted)
- Phone numbers (redacted)
- SSN (redacted)

**Redaction is automatic** via regex patterns.

## Troubleshooting

### Error: E_PATH_TRAVERSAL

**Cause:** Filename or path contains disallowed characters

**Solution:**
- Filenames are automatically sanitized
- If error persists, check for unusual characters
- Original filename is preserved in manifest metadata

### Error: E_INVALID_MIME

**Cause:** File type not in allowed list

**Solution:**
- Check `allowedMimeTypes` configuration
- Add MIME type to allowlist if appropriate
- Verify file is not corrupted

### Error: E_SIZE_LIMIT

**Cause:** File exceeds maximum size

**Solution:**
- Check `maxFileSizeBytes` configuration
- Split large files if appropriate
- Compress before ingest (note in metadata)

### Error: E_CHANNEL_BLOCKED

**Cause:** Evidence from blocked or non-allowlisted channel

**Solution:**
- Verify channel in allowlist
- Check if pairing is required
- Review security configuration

### Error: E_HASH_MISMATCH

**Cause:** Evidence file modified after ingest

**Solution:**
- This indicates potential tampering
- Review access logs for case
- Escalate per incident response procedures

### Verification Fails

**Symptoms:** `verified: false` in verify response

**Diagnostic steps:**
1. Check if original file exists
2. Compare current hash with manifest hash
3. Review audit log for modifications
4. Check filesystem permissions

## Configuration Example

```yaml
# openclaw.yaml
plugins:
  evidence-vault:
    driver: filesystem  # or s3
    basePath: /var/evidence-vault
    maxFileSizeBytes: 524288000  # 500MB
    defaultRetentionDays: 2555   # 7 years
    allowedMimeTypes:
      - image/jpeg
      - image/png
      - video/mp4
      - audio/mpeg
      - application/pdf
    channelAllowlist:
      - whatsapp
      - telegram
      - slack
    requirePairing: true
    
    # S3 driver options (if driver: s3)
    s3:
      endpoint: https://s3.example.com
      bucket: evidence-vault
      region: us-east-1
      objectLock: true
```

## Legal and Compliance Notes

### LGPD/GDPR Considerations

- Tag sensitive data with `sensitivityTag`
- Configure appropriate retention periods
- Never store real personal data in examples
- Implement data subject access request procedures

### Retention Policies

| Sensitivity | Default Retention |
|-------------|-------------------|
| public | 365 days |
| internal | 1825 days (5 years) |
| confidential | 2555 days (7 years) |
| restricted | Legal hold |

### Audit Requirements

All operations logged to JSONL audit file:
- Case creation/deletion
- Evidence ingest
- Verification attempts
- Export operations
- Access requests

**Audit log retention:** Same as case retention
