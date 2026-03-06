# Changelog

All notable changes to the EvidenceOps project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-17

### Added

#### Skill: EvidenceOps (`skill-evidenceops/`)

- **SKILL.md** - Complete skill definition for ClawHub publication
  - YAML frontmatter with OpenClaw metadata
  - Comprehensive workflow documentation for forensic media triage
  - Tool reference for all 5 evidence tools
  - Security posture section with channel allowlist/denylist guidance
  - Troubleshooting guide for common error codes
  - Configuration examples for production deployment

- **Templates**
  - `manifest.schema.json` - JSON Schema for case manifest validation
  - `case-manifest.example.json` - Sample manifest with 3 evidence items
  - `chain-of-custody.example.md` - Human-readable custody log template

- **Documentation**
  - `SECURITY.md` - Security architecture, threat model, and incident response procedures
  - `PRIVACY.md` - LGPD/GDPR compliance, data handling, and privacy protections

#### Plugin: Evidence Vault (`plugin-evidence-vault/`)

- **Core Types** (`src/types.ts`)
  - `CaseManifest` - Case-level manifest with items and chain of custody
  - `EvidenceItem` - Individual evidence with original, metadata, derivatives, and vault info
  - `AuditEvent` - JSONL audit log event structure
  - Error codes: `E_PATH_TRAVERSAL`, `E_INVALID_MIME`, `E_SIZE_LIMIT`, `E_HASH_MISMATCH`, etc.

- **Storage Drivers**
  - `FilesystemDriver` - Local filesystem storage with:
    - Append-only storage mode
    - Hash chain for manifest integrity
    - Read-only original files (chmod 444)
    - JSONL audit logging with redaction
  - `S3Driver` - S3/MinIO backend with:
    - Object Lock support (when available)
    - Metadata storage on objects
    - Graceful degradation without Object Lock
    - Local cache for manifests and audit logs

- **Tools** (OpenClaw tool interface)
  - `evidence.ingest` - Ingest file into vault with chain of custody
  - `evidence.verify` - Verify evidence integrity via SHA-256 comparison
  - `evidence.manifest` - Retrieve case manifest
  - `evidence.export` - Export case as ZIP archive with hash
  - `evidence.access_log` - Retrieve JSONL audit trail

- **Utilities**
  - `crypto.ts` - SHA-256 hashing, hash chain generation, ID generation
  - `path.ts` - Path sanitization, traversal prevention, case/evidence ID validation
  - `redaction.ts` - Automatic PII/secret redaction (emails, phones, API keys, passwords)

- **Tests**
  - `driver.test.ts` - Unit tests for crypto, path, redaction, and filesystem driver
  - `integration.test.ts` - E2E tests for full workflow, channel security, manifest determinism

#### Infrastructure

- **CI/CD** (`.github/workflows/`)
  - `ci.yml` - Lint, typecheck, test on Node 18/20 across Linux/macOS/Windows
  - `security.yml` - Secret scanning, dependency audit, SAST with Semgrep

- **Documentation**
  - `README.md` - Project overview, quick start, API reference
  - `docs/DESIGN.md` - Architecture diagrams, data flow, threat model, driver design

### Security

- Path traversal prevention via canonicalization and base path validation
- Automatic secret/PII redaction in all audit logs
- Channel allowlist/denylist enforcement
- Read-only original evidence files after ingest
- Hash chain for tamper-evident chain of custody
- No hardcoded secrets or credentials in codebase
- No real personal data in examples/templates

### Compliance

- LGPD (Brazil) data subject rights support
- GDPR (EU) compliance considerations
- Configurable retention policies (default: 7 years)
- Legal hold support
- Complete audit trail for all operations

### Dependencies

- `@aws-sdk/client-s3` ^3.500.0 - S3/MinIO support
- `archiver` ^6.0.0 - ZIP export functionality
- `exifreader` ^4.21.0 - EXIF metadata extraction
- `filenamify` ^6.0.0 - Safe filename generation
- `pino` ^8.18.0 - Structured logging
- `uuid` ^9.0.0 - Unique identifier generation

---

## Release Notes Summary

### v1.0.0 - Initial Release

This is the initial release of EvidenceOps, a forensic-grade evidence management system for OpenClaw. It provides:

1. **Complete Skill for ClawHub** - Ready-to-publish skill with comprehensive documentation
2. **Dual Storage Drivers** - Filesystem (local) and S3/MinIO (cloud) backends
3. **Chain of Custody** - Cryptographic hash chain for evidence integrity
4. **Security-First Design** - Path sanitization, secret redaction, channel controls
5. **Full Test Coverage** - Unit and integration tests for core functionality

The skill teaches OpenClaw agents how to:
- Accept media from any channel
- Create/manage cases with proper IDs
- Stage originals without modification
- Extract metadata (EXIF, duration, pages)
- Generate derivatives in separate folders
- Maintain tamper-evident audit trails
- Return evidence receipts to users

The plugin provides the backend implementation with:
- Pluggable storage architecture
- Deterministic manifest generation
- Channel-based access control
- Comprehensive error handling
