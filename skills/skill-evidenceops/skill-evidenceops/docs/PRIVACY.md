# Privacy Policy - EvidenceOps

## Overview

EvidenceOps handles potentially sensitive data and is designed with privacy protections built-in. This document outlines privacy considerations, data handling practices, and compliance information.

## Data We Handle

### Evidence Files

- Images (JPEG, PNG, GIF, WebP)
- Videos (MP4, WebM)
- Audio files (MP3, WAV, OGG)
- Documents (PDF, TXT)
- Archives (ZIP)

### Metadata

- EXIF data (may include GPS coordinates)
- File timestamps
- Author information
- Device identifiers
- Source channel information

### Operational Data

- Audit logs
- Chain of custody records
- Case manifests
- Access records

## Data Handling Principles

### 1. Local-First

All data is stored locally by default:
- No automatic cloud sync
- No telemetry or analytics
- No data sent to external services
- User controls all data location

### 2. Minimization

We collect only what's necessary:
- Original filenames preserved but sanitized
- Source channel logged for chain of custody
- Metadata extracted automatically (not added)
- No unnecessary tracking

### 3. Purpose Limitation

Data is used only for:
- Evidence integrity verification
- Chain of custody maintenance
- Audit compliance
- User-requested operations

### 4. Retention Limits

Data is retained according to policy:
- Configurable retention periods
- Automatic deletion scheduling
- Legal hold support
- Retention audit trail

## Privacy Protections

### Automatic Redaction

The following are automatically redacted from logs:

| Data Type | Redaction Pattern | Example |
|-----------|-------------------|---------|
| Email addresses | `[a-z]+@...` | `u***@example.com` |
| Phone numbers | `***-***-XXXX` | `555-***-1234` |
| Credit cards | `****-****-****-XXXX` | `****-****-****-1234` |
| SSN | `***-**-XXXX` | `***-**-4567` |
| API keys | `[REDACTED]` | `sk-***...` |
| Passwords | `[REDACTED]` | `password=***` |

### Manifest Privacy

Case manifests DO NOT contain:
- Passwords or secrets
- Unredacted PII in metadata
- External service credentials
- Private keys or tokens

### Audit Log Privacy

Audit logs contain redacted versions of:
- Sender identifiers
- Message content references
- File paths (internal paths only)
- Session information

## LGPD Compliance (Brazil)

### Direitos do Titular

EvidenceOps suporta os direitos do titular de dados:

| Direito | Implementação |
|---------|---------------|
| Acesso | `evidence.manifest()` retorna todos os dados |
| Correção | Manifest pode ser atualizado |
| Eliminação | Caso pode ser exportado e removido |
| Portabilidade | `evidence.export()` gera arquivo portátil |
| Informação | Manifest e audit log documentam tratamento |

### Base Legal

O tratamento de dados pessoais no EvidenceOps geralmente se baseia em:
- Cumprimento de obrigação legal
- Exercício regular de direitos
- Legítimo interesse (investigação interna)

### DPO (Encarregado de Dados)

Organizações devem designar um DPO para:
- Supervisionar uso do EvidenceOps
- Responder a solicitações de titulares
- Garantir conformidade com LGPD

## GDPR Compliance (EU)

### Data Subject Rights

EvidenceOps supports GDPR rights:

| Right | Implementation |
|-------|----------------|
| Access | Full manifest access |
| Rectification | Manifest update capability |
| Erasure | Case deletion (when legally permitted) |
| Portability | Export functionality |
| Restriction | Legal hold controls |
| Objection | Retention policy modification |

### Lawful Basis

Processing is typically based on:
- Legal obligation
- Legitimate interests
- Contract performance

### Data Protection Officer

Organizations should appoint a DPO to:
- Oversee EvidenceOps deployment
- Handle data subject requests
- Ensure GDPR compliance

## Data Retention

### Default Retention Periods

| Sensitivity | Retention | Notes |
|-------------|-----------|-------|
| public | 365 days | General retention |
| internal | 5 years | Business records |
| confidential | 7 years | Legal requirements |
| restricted | Indefinite | Legal hold |

### Retention Implementation

```json
{
  "retentionPolicy": {
    "retentionDays": 2555,
    "legalHold": false,
    "deleteAfter": "2033-02-17T00:00:00.000Z"
  }
}
```

### Legal Hold

When legal hold is active:
- Retention period suspended
- No automatic deletion
- Export still available
- Audit continues

## Data Security

### Encryption

- At rest: Filesystem permissions, optional disk encryption
- In transit: HTTPS for S3, local-only for filesystem
- Access control: Channel allowlist, pairing requirements

### Access Control

- Role-based access (via OpenClaw permissions)
- Channel-level restrictions
- Session isolation
- Audit logging

### Integrity

- SHA-256 hashing for all files
- Hash chain for manifests
- Read-only originals
- Tamper detection

## Third-Party Services

### S3/MinIO (Optional)

When configured for S3 storage:
- Data stored in your S3 bucket
- You control bucket policies
- You control encryption settings
- No data shared with OpenClaw

### No Analytics

EvidenceOps does NOT:
- Send telemetry data
- Use external analytics
- Track usage patterns
- Share data with third parties

## Examples and Documentation

### No Real Personal Data

All examples use:
- Redacted email addresses
- Fake names and identifiers
- Placeholder phone numbers
- Example case IDs

### Safe Sample Data

Example manifests contain:
- Synthetic evidence IDs
- Redacted source information
- Dummy hash values
- Template structures only

## Privacy Best Practices

### 1. Minimize Collection

Only ingest evidence that's necessary:
- Don't ingest everything by default
- Review before adding to case
- Use appropriate sensitivity tags

### 2. Limit Access

Restrict who can access evidence:
- Use channel allowlists
- Require pairing for DMs
- Review access logs regularly

### 3. Set Appropriate Retention

Match retention to requirements:
- Legal minimums for legal evidence
- Business needs for business records
- Privacy considerations for PII

### 4. Regular Audits

Review privacy posture:
- Check audit logs for anomalies
- Verify redaction is working
- Confirm retention compliance
- Review access patterns

## Privacy Contact

For privacy-related questions:
- Open an issue (for general questions)
- Email: privacy@openclaw.ai (for sensitive matters)

## Related Documents

- [SECURITY.md](./SECURITY.md) - Security policy
- [DESIGN.md](../../docs/DESIGN.md) - Architecture
- [README.md](../../README.md) - Usage guide
