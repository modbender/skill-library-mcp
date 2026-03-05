---
name: ezyhost
description: Deploy, manage, and monitor static websites via the EzyHost API. Upload files, build with AI, track analytics, manage custom domains, QR codes, email capture, and team collaboration.
homepage: https://ezyhost.io
metadata:
  openclaw:
    emoji: "🚀"
    requires:
      env:
        - EZYHOST_API_KEY
    primaryEnv: EZYHOST_API_KEY
    permissions:
      version: 1
      declared_purpose: "Deploy and manage static websites on EzyHost. Upload files, run SEO analysis, track analytics, generate sites with AI, configure custom domains, manage versions, teams, QR codes, and email capture."
      network:
        - "ezyhost.io"
      env:
        - "EZYHOST_API_KEY"
      filesystem: []
      exec: []
      sensitive_data:
        credentials: false
---

# EzyHost — Agent Skill

> This document describes how AI agents can interact with EzyHost programmatically.
> For human users, visit [ezyhost.io](https://ezyhost.io).

## Base URL

```
https://ezyhost.io/api
```

## Authentication

All API requests require an API key passed as a header:

```
x-api-key: $EZYHOST_API_KEY
```

The key is loaded from the `EZYHOST_API_KEY` environment variable. Generate your API key at `https://ezyhost.io/dashboard/api-keys`.

**Note:** API access requires the Pro plan or higher.

---

## Endpoints

### Projects

#### List Projects
```
GET /api/projects
```
Returns `{ projects: [{ id, name, slug, subdomain, customDomain, status, storageUsed, seoScore, deployedAt, _count: { files, analytics } }] }`

#### Create Project
```
POST /api/projects
Content-Type: application/json
Body: { "name": "my-site", "subdomain": "my-site" }
```
Returns `{ project: { id, name, subdomain, s3Prefix, url, ... } }`

The subdomain must be 3+ characters, lowercase alphanumeric with hyphens. Returns `409 SUBDOMAIN_TAKEN` if already in use. Your site will be live at `https://{subdomain}.ezyhost.site`.

Optional fields: `displayMode` ("standard" | "presentation"), `hideFromSearch` (boolean), `password` (string).

#### Check Subdomain Availability
```
GET /api/projects/check-subdomain/:subdomain
```
Returns `{ available: true/false, subdomain }`. Use this to validate before creating.

#### Get Project
```
GET /api/projects/:id
```
Returns `{ project: { id, name, subdomain, customDomain, status, storageUsed, seoScore, files: [...], ... } }`

#### Update Project
```
PATCH /api/projects/:id
Content-Type: application/json
Body: { "name": "new-name", "metaTitle": "...", "metaDescription": "...", "password": "...", "removeBranding": true, "displayMode": "standard", "hideFromSearch": false, "emailCapture": true }
```

#### Delete Project
```
DELETE /api/projects/:id
```
Deletes the project and all associated files from storage. This cannot be undone.

---

### File Upload

#### Upload Files (ZIP or individual)
```
POST /api/upload/:projectId
Content-Type: multipart/form-data
Body: files (multipart)
```
Returns `{ message, filesUploaded, totalSize, project: { id, subdomain } }`

Supports `.zip` archives (auto-extracted) and individual files. All uploaded files go through malware scanning (ClamAV + magic byte validation).

**Supported file types:** HTML, CSS, JS, JSON, XML, SVG, images (PNG, JPG, GIF, WebP, AVIF, ICO), PDFs, presentations (PPTX), documents (DOCX, XLSX), audio (MP3, WAV, OGG, FLAC, AAC), video (MP4, WebM, MOV), fonts (WOFF, WOFF2, TTF, OTF, EOT), archives (ZIP), 3D models (GLB, GLTF, OBJ), and any other static asset.

**Blocked file types:** Executables (.exe, .dll, .bat, .sh, .php, .asp, .jar) and SVGs containing scripts or event handlers are rejected.

#### Delete a File
```
DELETE /api/upload/:projectId/files/:fileId
```

#### Bulk Delete Files
```
POST /api/upload/:projectId/files/bulk-delete
Content-Type: application/json
Body: { "fileIds": ["id1", "id2", "id3"] }
```

#### Rename a File
```
PATCH /api/upload/:projectId/files/:fileId
Content-Type: application/json
Body: { "newPath": "assets/renamed-file.png" }
```

---

### GitHub Import

#### Import from GitHub
```
POST /api/github/:projectId
Content-Type: application/json
Body: { "owner": "username", "repo": "repo-name", "branch": "main", "subfolder": "dist" }
```
Returns `{ message, repo, branch, filesUploaded, filesSkipped, totalSize }`

Imports files from a public GitHub repository. The `branch` defaults to "main" and automatically falls back to "master" if not found. The optional `subfolder` field lets you import only a subdirectory (e.g. "dist", "build").

Requires Pro plan or higher.

---

### Version Rollback

#### List Versions
```
GET /api/versions/:projectId
```
Returns `{ versions: [{ id, version, label, fileCount, totalSize, createdAt }] }`

#### Create Version Snapshot
```
POST /api/versions/:projectId
Content-Type: application/json
Body: { "label": "v1.0" }
```
Snapshots the current state of all project files. Requires Pro plan or higher.

#### Rollback to Version
```
POST /api/versions/:projectId/rollback/:version
```
Restores all files to the state captured in the specified version number.

---

### SEO

#### Get SEO Report
```
GET /api/seo/:projectId
```
Returns `{ score, suggestions: [{ id, type, severity, message, resolved }] }`

Requires Pro plan or higher.

#### Run SEO Analysis
```
POST /api/seo/:projectId/analyze
```
Triggers a fresh SEO scan and returns updated suggestions.

#### Resolve a Suggestion
```
PATCH /api/seo/suggestion/:id/resolve
```

#### AI Auto-Fix SEO Issues
```
POST /api/seo/:projectId/ai-fix
Content-Type: application/json
Body: { "suggestionIds": ["id1", "id2"] }
```
Uses AI to automatically fix SEO issues in your HTML files. Counts against AI generation limits.

---

### Analytics

#### Get Analytics
```
GET /api/analytics/:projectId?period=7d
```
Periods: `24h`, `7d`, `30d`, `90d`

**Basic analytics (all plans):**
Returns `{ totalVisits, visitsByDay, topPages, isAdvanced }`

**Advanced analytics (Pro+ plans):**
Additionally returns `{ uniqueVisitors, uniqueByDay, topReferrers, topCountries, devices, browsers }`

Free plan users receive `isAdvanced: false` and advanced fields are empty.

#### Track Event (public, no auth required)
```
POST /api/analytics/track
Content-Type: application/json
Body: { "projectId": "...", "path": "/page", "referrer": "..." }
```

---

### QR Codes

#### Generate QR Code
```
POST /api/qrcode/:projectId
```
Returns `{ qrCodeUrl: "data:image/png;base64,...", siteUrl: "https://..." }`

Generates a QR code pointing to the project's live URL (subdomain or custom domain). Returns a base64 data URL. Available on all paid plans.

#### Get QR Code
```
GET /api/qrcode/:projectId
```
Returns `{ qrCodeUrl: "data:image/..." | null }`

---

### Email Capture

#### Toggle Email Capture on Project
```
PATCH /api/emails/:projectId/toggle
```
Returns `{ emailCapture: true/false }`. Requires Business plan.

When enabled, visitors to the hosted site see a popup email collection form after 5 seconds.

#### Submit Email (public, no auth)
```
POST /api/emails/submit
Content-Type: application/json
Body: { "email": "visitor@example.com", "projectId": "...", "source": "modal" }
```
Source options: `modal`, `inline`, `api`. Only works if the project has email capture enabled and the project owner has a Business plan.

#### Get Captured Emails
```
GET /api/emails/:projectId?page=1&limit=50
```
Returns `{ emails: [{ id, email, source, createdAt }], total, page, totalPages }`

Requires Business plan.

#### Export Emails as CSV
```
GET /api/emails/:projectId/export
```
Returns a CSV file download. Requires Business plan.

#### Delete a Captured Email
```
DELETE /api/emails/:projectId/:emailId
```

---

### Teams

#### List Teams
```
GET /api/teams
```
Returns `{ teams: [{ id, name, ownerId, members: [...] }] }`

#### Create Team
```
POST /api/teams
Content-Type: application/json
Body: { "name": "My Team" }
```
Requires Business plan.

#### Add Team Member
```
POST /api/teams/:teamId/members
Content-Type: application/json
Body: { "email": "user@example.com", "role": "editor" }
```
Roles: `editor`, `viewer`.

#### Update Member Role
```
PATCH /api/teams/:teamId/members/:memberId
Content-Type: application/json
Body: { "role": "viewer" }
```

#### Remove Team Member
```
DELETE /api/teams/:teamId/members/:memberId
```

#### Leave Team
```
POST /api/teams/:teamId/leave
```

#### Delete Team
```
DELETE /api/teams/:teamId
```

---

### Domains

#### Add Custom Domain
```
POST /api/domains/:projectId
Content-Type: application/json
Body: { "domain": "example.com" }
```
Returns `{ dnsInstructions: { type, name, value } }` — DNS records you need to create.

Requires Pro plan or higher.

#### Verify Domain DNS
```
GET /api/domains/:projectId/verify
```
Returns `{ verified: true/false, dnsInstructions }`. Call this after setting up DNS records.

#### Remove Domain
```
DELETE /api/domains/:projectId
```

---

### AI Builder

#### Chat (generate/edit websites via AI)
```
POST /api/aibuilder/chat
Content-Type: application/json
Body: { "message": "build a portfolio site", "history": [], "currentFiles": [] }
```
Returns **SSE stream** with events:
- `status` — progress updates ("Generating HTML...")
- `progress` — percentage (0-100)
- `done` — `{ files: [{ filename, content }] }` — the generated files
- `error` — `{ message }` on failure

Counts against per-plan AI generation limits. Only one AI generation can run at a time per user.

#### Deploy AI-Generated Files
```
POST /api/aibuilder/deploy/:projectId
Content-Type: application/json
Body: { "files": [{ "filename": "index.html", "content": "<!DOCTYPE html>..." }] }
```

#### Download as ZIP
```
POST /api/aibuilder/download-zip
Content-Type: application/json
Body: { "files": [{ "filename": "index.html", "content": "..." }] }
```
Returns a ZIP file download.

#### Templates

```
GET    /api/aibuilder/templates           — list saved templates
GET    /api/aibuilder/templates/:id       — get template details
POST   /api/aibuilder/templates           — save new template
PATCH  /api/aibuilder/templates/:id       — update template
DELETE /api/aibuilder/templates/:id       — delete template
```

Template body: `{ "name": "My Template", "description": "...", "messages": [...], "files": [...] }`

---

### API Keys

#### Get Current Key
```
GET /api/apikey
```
Returns `{ hasKey: true/false, apiKey: "ag_••••..." }` — key is partially masked.

#### Generate New Key
```
POST /api/apikey/generate
```
Returns `{ apiKey: "ag_..." }` — full key shown only once. Store it securely. Revokes any previous key.

Requires Pro plan or higher.

#### Revoke Key
```
DELETE /api/apikey
```

---

### Plans (Public)

#### Get All Plans
```
GET /api/plans
```
No authentication required. Returns `{ plans: [{ plan, name, priceMonthly, maxProjects, maxStorageMB, ... }] }` with all feature flags and limits for each plan.

---

### Billing

#### Get Billing Info
```
GET /api/billing
```
Returns `{ plan, subscription, aiCredits, usage }`.

#### Get AI Usage
```
GET /api/billing/ai-usage
```
Returns `{ used, limit, remaining, resetsAt }`.

---

## Plan Limits

| Feature | Free | Pro ($9/mo) | Business ($29/mo) |
|---------|------|-------------|-------------------|
| Projects | 2 | 15 | Unlimited |
| Storage | 50 MB | 2 GB | 20 GB |
| Max file size | 10 MB | 100 MB | 500 MB |
| Custom domains | — | 3 | Unlimited |
| API access | — | ✅ | ✅ |
| GitHub import | — | ✅ | ✅ |
| Version rollback | — | Up to 5 | Up to 30 |
| Password protection | — | ✅ | ✅ |
| Remove branding | — | ✅ | ✅ |
| SEO tools | — | ✅ | ✅ |
| Advanced analytics | — | ✅ | ✅ |
| QR codes | ✅ | ✅ | ✅ |
| Hide from search | — | ✅ | ✅ |
| Email capture | — | — | ✅ |
| Team members | — | — | Up to 5 |
| Priority support | — | — | ✅ |
| AI generations | 3/mo | 10/mo | 30/mo |
| AI templates | 1 | 10 | Unlimited |
| Presentation mode | — | ✅ | ✅ |
| Basic analytics | ✅ | ✅ | ✅ |

---

## Hosted Site URLs

Sites are served at:
- **Free subdomain:** `https://{subdomain}.ezyhost.site`
- **Custom domain:** `https://{your-domain.com}` (Pro+ plans)

All sites include HTTPS, CDN caching, automatic file browser for non-HTML projects, and optional presentation mode for PDF/PPTX files.

**Injected features on served sites:**
- **Branding badge:** "Hosted on ezyhost" badge shown on free plan sites. Removable on paid plans via `removeBranding` project setting.
- **Email capture popup:** When enabled (Business plan), visitors see a subscribe popup after 5 seconds. Dismissible and stored in sessionStorage.
- **Analytics tracking:** Pageviews are automatically tracked for HTML files.

---

## Error Responses

All errors return JSON:
```json
{ "error": "Description of the error" }
```

Plan limit errors include `"upgrade": true` to indicate a higher plan is needed:
```json
{ "error": "GitHub import requires a Pro plan or higher", "upgrade": true }
```

Subdomain conflicts:
```json
{ "error": "The subdomain \"my-site\" is already taken.", "code": "SUBDOMAIN_TAKEN" }
```

Common HTTP status codes:
- `400` — Bad request / validation error
- `401` — Not authenticated
- `403` — Plan limit reached or feature disabled
- `404` — Resource not found
- `409` — Conflict (subdomain taken)
- `429` — Rate limited
- `500` — Server error

---

## Rate Limits

- **General API:** 300 requests per 15 minutes per API key
- **Upload:** 2 requests per second
- **Analytics tracking:** 60 writes per minute per IP
- **Email capture submit:** 10 per minute per IP
- **AI Builder:** Subject to per-plan generation limits (1 concurrent request max)

---

## Example: Deploy a Static Site

```bash
# 1. Check subdomain availability
curl https://ezyhost.io/api/projects/check-subdomain/my-site \
  -H "x-api-key: $EZYHOST_API_KEY"

# 2. Create a project
curl -X POST https://ezyhost.io/api/projects \
  -H "x-api-key: $EZYHOST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "my-site", "subdomain": "my-site"}'

# 3. Upload files (ZIP)
curl -X POST https://ezyhost.io/api/upload/PROJECT_ID \
  -H "x-api-key: $EZYHOST_API_KEY" \
  -F "files=@site.zip"

# 4. Generate QR code
curl -X POST https://ezyhost.io/api/qrcode/PROJECT_ID \
  -H "x-api-key: $EZYHOST_API_KEY"

# 5. Check SEO (Pro+)
curl https://ezyhost.io/api/seo/PROJECT_ID \
  -H "x-api-key: $EZYHOST_API_KEY"

# 6. Add custom domain (Pro+)
curl -X POST https://ezyhost.io/api/domains/PROJECT_ID \
  -H "x-api-key: $EZYHOST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com"}'
```

Your site is now live at `https://my-site.ezyhost.site`

## Example: Import from GitHub

```bash
# Import a public repo (auto-detects main/master branch)
curl -X POST https://ezyhost.io/api/github/PROJECT_ID \
  -H "x-api-key: $EZYHOST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"owner": "emilbaehr", "repo": "automatic-app-landing-page"}'
```

## Example: AI-Generate and Deploy

```bash
# 1. Generate a site with AI (SSE stream)
curl -N -X POST https://ezyhost.io/api/aibuilder/chat \
  -H "x-api-key: $EZYHOST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "build a modern portfolio with dark theme", "history": []}'

# 2. Deploy the generated files to a project
curl -X POST https://ezyhost.io/api/aibuilder/deploy/PROJECT_ID \
  -H "x-api-key: $EZYHOST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"files": [{"filename": "index.html", "content": "..."}]}'
```
