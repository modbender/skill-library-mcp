---
name: App Store Connect
slug: app-store-connect
version: 1.0.0
homepage: https://clawic.com/skills/app-store-connect
description: Manage iOS apps, TestFlight builds, submissions, and analytics via App Store Connect API.
metadata: {"clawdbot":{"emoji":"🍎","requires":{"bins":[],"env":["ASC_ISSUER_ID","ASC_KEY_ID","ASC_PRIVATE_KEY_PATH"]},"os":["linux","darwin","win32"]}}
---

## When to Use

User needs to manage iOS/macOS apps on App Store Connect. Agent handles API authentication, build management, TestFlight distribution, App Review submissions, and analytics retrieval.

## Quick Reference

| Topic | File |
|-------|------|
| API Authentication | `api-auth.md` |
| Common Workflows | `workflows.md` |

## Core Rules

### 1. JWT Authentication Required
App Store Connect API uses JWT tokens signed with your private key.

```bash
# Required environment variables:
# ASC_ISSUER_ID     - From App Store Connect > Users > Keys
# ASC_KEY_ID        - From the API key you created
# ASC_PRIVATE_KEY_PATH - Path to your .p8 private key file
```

Generate JWT with ES256 algorithm, 20-minute expiration max. See `api-auth.md` for code examples.

### 2. API Versioning
Always specify API version in requests.

```bash
curl -H "Authorization: Bearer $JWT" \
     "https://api.appstoreconnect.apple.com/v1/apps"
```

Current stable version: `v1`. Check Apple docs for v2 endpoints.

### 3. Build Processing States
Builds go through states after upload:

| State | Meaning | Action |
|-------|---------|--------|
| PROCESSING | Upload received, processing | Wait |
| FAILED | Processing failed | Check logs |
| INVALID | Validation failed | Fix issues, re-upload |
| VALID | Ready for testing/submission | Proceed |

Never submit a build that is not `VALID`.

### 4. TestFlight Distribution
- **Internal Testing**: Up to 100 members, builds available immediately after processing
- **External Testing**: Up to 10,000 testers, requires Beta App Review for first build of version
- External groups need at least: app description, feedback email, privacy policy URL

### 5. App Review Submission
Before submitting for review:
- All required metadata complete (descriptions, keywords, screenshots)
- App Preview videos under 30 seconds
- Privacy policy URL valid and accessible
- Contact information current

Submission creates an `appStoreVersion` in `PENDING_DEVELOPER_RELEASE` or `WAITING_FOR_REVIEW`.

### 6. Rate Limits
API has rate limits per hour. Handle 429 responses with exponential backoff.

```bash
# Respect Retry-After header
HTTP/1.1 429 Too Many Requests
Retry-After: 60
```

### 7. Bundle ID Management
Bundle IDs are permanent once created. Cannot be deleted or renamed.

- Use reverse-domain notation: `com.company.appname`
- Plan naming carefully before registration
- Each bundle ID can only belong to one team

## Common Traps

- **Expired JWT** - Tokens expire in 20 min max. Regenerate before long operations.
- **Wrong key permissions** - API keys need specific roles (Admin, App Manager, etc.)
- **Missing export compliance** - Apps with encryption need ECCN or exemption documentation
- **Build version collision** - Each build needs unique version+build number combo
- **Screenshot dimensions** - Must match exactly for each device type (no scaling)
- **Phased release confusion** - Phased release is for App Store only, not TestFlight

## External Endpoints

| Endpoint | Data Sent | Purpose |
|----------|-----------|---------|
| api.appstoreconnect.apple.com | App metadata, build info | App Store Connect API |

No other data is sent externally.

## Security & Privacy

**Data that leaves your machine:**
- App metadata sent to Apple for App Store listing
- Build information for processing
- Analytics queries

**Data that stays local:**
- API private key (.p8) - never transmit
- JWT tokens - generated locally
- Downloaded reports

**This skill does NOT:**
- Store your .p8 key in plain text
- Share credentials with third parties
- Access apps outside your team

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `ios` — iOS development patterns
- `swift` — Swift language reference
- `xcode` — Xcode IDE workflows

## Feedback

- If useful: `clawhub star app-store-connect`
- Stay updated: `clawhub sync`
