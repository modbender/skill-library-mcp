# EvidenceOps - Design Notes

## Overview

EvidenceOps is a forensic-grade evidence management system for OpenClaw, providing:
- Media triage with chain of custody
- Immutable evidence storage with pluggable vault backends
- Cryptographic integrity verification
- Audit trail for compliance

## Case Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EVIDENCE OPS FLOW                                    │
└─────────────────────────────────────────────────────────────────────────────┘

1. INTAKE
   ┌──────────┐    ┌──────────────┐    ┌─────────────┐
   │  Media   │───▶│   Staging    │───▶│  Calculate  │
   │  Input   │    │  (read-only) │    │  SHA-256    │
   └──────────┘    └──────────────┘    └─────────────┘
                                              │
                                              ▼
2. METADATA EXTRACTION                   ┌─────────────┐
   ┌──────────┐    ┌──────────────┐     │  Manifest   │
   │  EXIF/   │───▶│  Metadata    │────▶│  Update     │
   │  Media   │    │  (JSON)      │     │             │
   └──────────┘    └──────────────┘     └─────────────┘
                                              │
                                              ▼
3. DERIVATIVES GENERATION                ┌─────────────┐
   ┌──────────┐    ┌──────────────┐     │  Vault      │
   │ Thumbnail│    │  Transcript  │────▶│  Ingest     │
   │  OCR     │    │  Preview     │     │             │
   └──────────┘    └──────────────┘     └─────────────┘
                                              │
                                              ▼
4. VAULT STORAGE                         ┌─────────────┐
   ┌──────────┐    ┌──────────────┐     │  Receipt    │
   │ Original │    │  Audit Log   │────▶│  Return     │
   │ (locked) │    │  (JSONL)     │     │             │
   └──────────┘    └──────────────┘     └─────────────┘
```

## Directory Structure

```
evidence-vault/
├── cases/
│   └── {caseId}/
│       ├── manifest.json          # Case manifest
│       ├── originals/             # Immutable originals
│       │   └── {evidenceId}.{ext}
│       ├── derivatives/           # Generated artifacts
│       │   ├── thumbnails/
│       │   ├── transcripts/
│       │   └── previews/
│       ├── metadata/              # Extracted metadata
│       │   └── {evidenceId}.json
│       └── audit.jsonl            # Audit trail
├── index/
│   └── cases-index.json           # Global case index
└── system/
    └── config.json                # Vault configuration
```

## Manifest Format

```json
{
  "schemaVersion": "1.0.0",
  "caseId": "case-2026-001",
  "createdAt": "2026-02-17T10:30:00.000Z",
  "updatedAt": "2026-02-17T10:45:00.000Z",
  "sensitivityTag": "confidential",
  "retentionPolicy": {
    "retentionDays": 2555,
    "legalHold": false,
    "deleteAfter": "2033-02-17T10:30:00.000Z"
  },
  "items": [
    {
      "evidenceId": "ev-abc123",
      "original": {
        "filename": "document.pdf",
        "sha256": "a1b2c3...",
        "size": 102400,
        "mime": "application/pdf",
        "receivedAt": "2026-02-17T10:30:00.000Z",
        "source": {
          "channel": "whatsapp",
          "sender": "user@example.com",
          "messageId": "msg-xyz"
        }
      },
      "metadata": {
        "pages": 5,
        "author": "Unknown",
        "createdAt": "2026-01-15T08:00:00.000Z"
      },
      "derivatives": [
        {
          "type": "thumbnail",
          "filename": "ev-abc123-thumb.png",
          "sha256": "d4e5f6...",
          "size": 2048,
          "generatedAt": "2026-02-17T10:35:00.000Z"
        }
      ],
      "vault": {
        "provider": "filesystem",
        "vaultUrl": "file:///evidence-vault/cases/case-2026-001/originals/ev-abc123.pdf",
        "ingestedAt": "2026-02-17T10:40:00.000Z"
      }
    }
  ],
  "chainOfCustody": [
    {
      "event": "case_created",
      "timestamp": "2026-02-17T10:30:00.000Z",
      "actor": "system",
      "previousHash": null,
      "currentHash": "abc123..."
    },
    {
      "event": "evidence_ingested",
      "timestamp": "2026-02-17T10:40:00.000Z",
      "actor": "session-user-001",
      "evidenceId": "ev-abc123",
      "previousHash": "abc123...",
      "currentHash": "def456..."
    }
  ]
}
```

## Threat Model

### Assets
1. **Evidence Files** - Original media (images, videos, documents, audio)
2. **Metadata** - EXIF, file properties, extracted information
3. **Manifests** - Case indices and chain of custody
4. **Audit Logs** - Activity records
5. **Configuration** - API keys, retention policies

### Threats

| Threat ID | Description | Likelihood | Impact | Mitigation |
|-----------|-------------|------------|--------|------------|
| T01 | Path traversal attack via user input | High | Critical | Strict path sanitization, allowlist validation |
| T02 | Evidence tampering post-ingest | Medium | Critical | Append-only storage, hash chain verification |
| T03 | Secret exfiltration via logs | Medium | High | Redaction filter, allowlist-based logging |
| T04 | Malicious skill abuse | Medium | High | Tool restrictions, channel allowlists |
| T05 | Unauthorized access from untrusted channels | High | High | Deny-by-default, pairing requirements |
| T06 | Evidence deletion/loss | Low | Critical | Retention policies, backup recommendations |
| T07 | Hash collision attack | Very Low | Critical | SHA-256 (collision-resistant) |
| T08 | Replay attack on manifest | Low | Medium | Timestamp validation, hash chain |
| T09 | Metadata injection | Medium | Medium | Schema validation, sanitization |
| T10 | Resource exhaustion (zip bomb, etc.) | Medium | Medium | Size limits, format validation |

### Attack Surfaces

1. **File Input**
   - Malicious filenames (path traversal)
   - Oversized files (DoS)
   - Polyglot files (format confusion)
   - Embedded payloads in metadata

2. **Channel Input**
   - Untrusted senders
   - DM without pairing
   - Public channels

3. **Plugin Tools**
   - Malicious skill calling evidence tools
   - Parameter injection

4. **Storage Backend**
   - S3 bucket misconfiguration
   - Local filesystem permissions

### Security Controls

1. **Input Validation**
   - Filename sanitization (alphanumeric + limited chars)
   - Path canonicalization
   - MIME type verification (magic bytes)
   - Size limits enforcement

2. **Access Control**
   - Channel allowlist/denylist
   - Session pairing requirement
   - Tool permission scoping

3. **Integrity**
   - SHA-256 hashing
   - Hash chain for manifests
   - Append-only storage mode
   - Regular integrity verification

4. **Audit**
   - JSONL audit log
   - Secret redaction
   - Immutable log entries

5. **Data Protection**
   - No secrets in manifests
   - Sensitivity tagging
   - Retention policy enforcement

## Driver Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   EvidenceVaultPlugin                    │
├─────────────────────────────────────────────────────────┤
│  Tools Layer                                             │
│  ┌─────────────────────────────────────────────────┐    │
│  │ evidence.ingest()  evidence.verify()            │    │
│  │ evidence.manifest() evidence.export()           │    │
│  │ evidence.access_log()                           │    │
│  └─────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────┤
│  Driver Interface                                        │
│  ┌─────────────────────────────────────────────────┐    │
│  │ initialize()  ingest()  verify()  export()      │    │
│  │ getManifest()  writeAudit()  healthCheck()      │    │
│  └─────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────┤
│  Drivers                                                 │
│  ┌─────────────────┐    ┌─────────────────────────┐     │
│  │ FilesystemDriver│    │ S3Driver                │     │
│  │ - Local storage │    │ - S3/MinIO backend      │     │
│  │ - Append-only   │    │ - Object Lock support   │     │
│  │ - Hash chain    │    │ - Versioning            │     │
│  └─────────────────┘    └─────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

## Driver Selection

```yaml
# config.yaml
vault:
  driver: filesystem  # or s3
  
  filesystem:
    basePath: /var/evidence-vault
    appendOnly: true
    
  s3:
    endpoint: https://s3.example.com
    bucket: evidence-vault
    region: us-east-1
    objectLock: true
    # credentials via environment or IAM
```

## Audit Event Types

| Event | Description |
|-------|-------------|
| `case_created` | New case initialized |
| `evidence_ingested` | Evidence file stored |
| `evidence_verified` | Integrity check performed |
| `evidence_exported` | Export archive created |
| `manifest_updated` | Case manifest modified |
| `derivative_created` | Derivative artifact generated |
| `retention_applied` | Retention policy executed |

## Error Handling

All errors follow a standard format:

```json
{
  "error": {
    "code": "E_PATH_TRAVERSAL",
    "message": "Path traversal attempt detected",
    "details": {
      "input": "../etc/passwd",
      "sanitized": null
    }
  }
}
```

Error codes:
- `E_PATH_TRAVERSAL` - Path traversal attempt
- `E_INVALID_MIME` - MIME type mismatch
- `E_SIZE_LIMIT` - File size exceeded
- `E_HASH_MISMATCH` - Integrity verification failed
- `E_NOT_FOUND` - Resource not found
- `E_PERMISSION_DENIED` - Access denied
- `E_VAULT_ERROR` - Storage backend error
- `E_INVALID_CASE` - Invalid case ID
- `E_CHANNEL_BLOCKED` - Channel not allowed

## Configuration Schema

```typescript
interface VaultConfig {
  driver: 'filesystem' | 's3';
  filesystem?: {
    basePath: string;
    appendOnly: boolean;
    maxFileSizeBytes: number;
  };
  s3?: {
    endpoint: string;
    bucket: string;
    region: string;
    objectLock: boolean;
    prefix?: string;
  };
  security: {
    allowedChannels: string[];
    blockedChannels: string[];
    requirePairing: boolean;
    maxFileSizeBytes: number;
    allowedMimeTypes: string[];
  };
  retention: {
    defaultRetentionDays: number;
    enforceLegalHold: boolean;
  };
  audit: {
    logPath: string;
    redactPatterns: string[];
  };
}
```
