# Authentication Setup

## Service Accounts vs User Accounts

| Aspect | Service Account | User Account |
|--------|-----------------|--------------|
| Best for | Automated operations, servers | Interactive, per-user access |
| Quotas | Usually higher | Per-user limits |
| MFA | Not applicable | May be required |
| Audit | Clear service identity | Mixed with user activity |

**Rule:** Use service accounts for automation; user accounts for interactive tools.

---

## AWS Authentication

```bash
# Environment variables (session)
export AWS_ACCESS_KEY_ID=AKIA...
export AWS_SECRET_ACCESS_KEY=...
export AWS_DEFAULT_REGION=us-east-1

# Named profiles (~/.aws/credentials)
[profile-name]
aws_access_key_id = AKIA...
aws_secret_access_key = ...
region = us-east-1

# IAM roles (recommended for EC2/Lambda)
# Automatic via instance metadata
```

**Traps:**
- Access keys rotate; automate rotation
- Root account keys = security incident
- Region mismatch = "bucket not found" errors

---

## Google Cloud Authentication

```bash
# Service account (recommended)
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json

# User account (interactive)
gcloud auth login
gcloud auth application-default login

# Impersonation (for local dev with SA permissions)
gcloud auth application-default login --impersonate-service-account=SA@PROJECT.iam.gserviceaccount.com
```

**Traps:**
- OAuth tokens expire in 1 hour
- Service account keys are security-sensitive; prefer Workload Identity
- `application-default` vs `gcloud auth` are different credential chains

---

## Azure Authentication

```bash
# Service Principal
export AZURE_CLIENT_ID=...
export AZURE_TENANT_ID=...
export AZURE_CLIENT_SECRET=...

# CLI login
az login
az account set --subscription NAME

# Managed Identity (Azure VMs)
# Automatic via IMDS
```

**Traps:**
- Tenant vs subscription confusion
- SAS tokens leak easily; use short expiration
- RBAC propagation takes minutes

---

## OAuth for Consumer Services

### Google Drive / Dropbox / OneDrive

1. **Create OAuth app** in provider console
2. **Request minimal scopes** — `drive.file` not `drive` for Google
3. **Store refresh tokens** — access tokens expire quickly
4. **Handle token refresh** before long operations

**Traps:**
- Refresh tokens can be revoked by user
- Scopes determine what operations work
- Rate limits often per-user, not per-app
