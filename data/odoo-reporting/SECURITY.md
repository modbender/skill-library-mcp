# Security Policy

## Overview

This document outlines the security model, credentials handling, and safety mechanisms of the Odoo Financial Intelligence Skill.

## Security Model

### 1. User Invocation Only (No Autonomous Execution)

**CRITICAL**: This skill is configured with `modelInvocation.disabled: true` in `skill.json`.

- AI models **CANNOT** invoke this skill automatically
- User **MUST** explicitly request Odoo operations
- Every invocation requires explicit user intent
- Skill will not execute without direct user command

### 2. Read-Only Enforcement

The skill implements **client-side** read-only enforcement:

**Blocked Methods (Will Raise PermissionError):**
- `create` - Creating new records
- `write` - Modifying existing records  
- `unlink` - Deleting records
- `copy` - Duplicating records
- `action_post` - Posting journal entries
- `action_confirm` - Confirming orders/documents
- `button_validate` - Validating records

**Allowed Methods (Read-Only):**
- `search`, `search_read` - Querying data
- `read` - Reading record details
- `search_count` - Counting records
- `fields_get` - Getting field metadata
- `name_search` - Searching by name
- `context_get`, `default_get` - Getting context/defaults

### 3. Credential Security

#### Required Credentials

The skill **REQUIRES** these environment variables:

| Variable | Required | Secret | Purpose |
|----------|----------|--------|---------|
| `ODOO_URL` | Yes | No | Odoo instance URL |
| `ODOO_DB` | Yes | No | Database name |
| `ODOO_USER` | Yes | No | Username/email |
| `ODOO_PASSWORD` | Yes | **Yes** | API key or password |

#### Storage

- Credentials stored in: `assets/autonomous-cfo/.env`
- File is excluded from git via `.gitignore`
- Credentials loaded into environment variables only
- Never logged, displayed, or transmitted elsewhere

#### API Key vs Password

**Production: Use API Keys**

1. Log into Odoo → Settings → Account Security → API Keys
2. Generate a new API key
3. Use the key as `ODOO_PASSWORD`

**Benefits of API Keys:**
- Scoped permissions (can be read-only)
- Independent revocation
- Better audit trail
- Don't expose main password

### 4. Authentication Methods

#### XML-RPC (Legacy, Default)

- Compatible with all Odoo versions
- Password/API key sent in XML-RPC request body
- Enable: `ODOO_RPC_BACKEND=xmlrpc` (or omit)

#### JSON-RPC (Odoo 19+)

- More efficient for large datasets
- **API key sent as Bearer token**: `Authorization: Bearer <api_key>`
- This is standard Odoo 19+ JSON-2 API authentication
- Enable: `ODOO_RPC_BACKEND=json2`

**Note on Bearer Tokens:**
The use of `Authorization: Bearer <token>` with the API key is the official Odoo 19+ authentication method. This is not a security vulnerability but the intended authentication flow for the JSON-2 API.

### 5. Network Security

**Network Boundaries:**
- Only connects to the Odoo URL specified in `ODOO_URL`
- No external telemetry or analytics endpoints
- No data exfiltration to third parties

**SSL/TLS:**
- HTTPS connections verified by default
- Optional: `--insecure` flag to disable SSL verification (not recommended for production)

**Request Safety:**
- Timeout protection (default: 30s)
- Retry logic for transient failures (default: 2 retries)
- Connection error handling

### 6. Data Handling

**Local Processing:**
- All report generation happens locally
- Chart rendering with matplotlib (local)
- PDF generation with fpdf2 (local)
- Excel creation with openpyxl (local)

**Output Locations:**
```
assets/autonomous-cfo/output/
├── charts/           # PNG chart images
├── whatsapp_cards/   # PNG social media cards
├── pdf_reports/      # PDF reports
└── excel/            # Excel spreadsheets
```

**No Cloud Upload:**
- No automatic cloud storage
- No external sharing
- No SaaS integrations
- Data never leaves your machine except to your specified Odoo instance

### 7. Output Security

All outputs are local files:
- PDF reports: Local file system only
- WhatsApp cards: Local PNG images (share manually if needed)
- Excel files: Local spreadsheets
- Charts: Local PNG images

**No Automatic Sharing:**
- No email automation
- No webhook calls
- No Slack/Teams integration
- User manually controls all sharing

## Security Checklist

Before using this skill in production:

- [ ] Use an Odoo API key instead of password
- [ ] Create a dedicated Odoo user with read-only permissions
- [ ] Restrict Odoo user access to necessary data only
- [ ] Verify `.env` file is in `.gitignore`
- [ ] Use HTTPS for `ODOO_URL`
- [ ] Don't use `--insecure` flag in production
- [ ] Review generated reports before sharing
- [ ] Rotate API keys periodically

## Reporting Security Issues

If you discover a security vulnerability:

1. **DO NOT** open a public issue
2. Email: [your security contact]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Security Updates

This skill will be updated to address:
- Dependency vulnerabilities
- Odoo API changes
- Python security patches
- New attack vectors

Subscribe to releases for security updates.

## Compliance

### Data Protection

- GDPR: No personal data stored or transmitted
- SOC 2: Read-only access, audit trails in Odoo
- ISO 27001: Credentials encrypted in transit (HTTPS)

### Audit Trail

All data access is logged in Odoo:
- User actions logged by Odoo
- API key usage tracked
- Read operations visible in Odoo logs

## Vulnerability Disclosure Policy

We follow responsible disclosure:

1. Report received and acknowledged within 48 hours
2. Investigation within 7 days
3. Fix developed and tested
4. Security update released
5. Public disclosure after 30 days or with reporter's consent

## Security-related Configuration

### Minimal Permissions (Odoo Side)

Create an Odoo user with these minimal permissions:

**Technical Settings:**
- Read access on all models you need to query
- No write/create/delete permissions

**Suggested Groups:**
- Accounting: Read-only (if querying financial data)
- Sales: Read-only (if querying sales data)
- Inventory: Read-only (if querying inventory)

### API Key Scope

When creating an Odoo API key:
- Name it descriptively (e.g., "Financial Reports Skill")
- Assign to read-only user
- Set expiration if desired
- Monitor usage in Odoo logs

## Contact

For security questions or concerns:
- Security issues: [security contact]
- General questions: Open a GitHub issue (not for vulnerabilities)

---

**Last Updated**: 2026-02-17  
**Version**: 2.0.0  
**Skill**: odoo-openclaw-skill
