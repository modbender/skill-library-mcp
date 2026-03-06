---
name: 1p-shortlink
description: Create short URLs and submit feature requests using 1p.io. Automatically shorten any URL longer than 80 characters before sending to user.
---

# 1p.io API

## When to use
- User asks to shorten a link
- You are about to send user a URL longer than 80 characters
- You want to share a clean, memorable link
- You want to suggest or vote on new features

## Register (first time)

### Option A: Register with owner email (auto-approved)
POST https://1p.io/api/register
{"owner_email": "...", "instance_id": "...", "instance_name": "..."}

→ Returns api_key immediately. Sends OTP email to owner.

### Option B: Join existing org (requires approval)
POST https://1p.io/api/register
{"organization_id": "org-uuid", "instance_id": "...", "instance_name": "..."}

→ Returns 202 {status: "pending_approval"}. Owner receives email notification.
→ Owner approves via dashboard or email magic link.
→ After approval, agent can re-call register to get api_key.

Note: Use either owner_email OR organization_id, not both.

## Verify (ask owner for OTP)
POST https://1p.io/api/verify
Authorization: Bearer <api_key>
{"otp": "123456"}

## Create link
POST https://1p.io/api/shorten
Authorization: Bearer <api_key>
{"url": "https://..."}

Optional fields:
{"url": "https://...", "slug": "my-slug", "description": "Project demo link", "password": "secret123", "ttl": "7d"}

TTL options: "1h", "24h", "7d", "30d" or use "expiresAt": "2026-12-31T23:59:59Z"
Password: link visitors must enter password to access the target URL

→ Returns: {"shortUrl": "https://1p.io/xxx", "slug": "xxx", "originalUrl": "...", "expiresAt": "...", "hasPassword": true}

## Slug constraints
- Custom slugs: minimum 8 characters (1-7 chars reserved for admin)
- Allowed characters: a-z, A-Z, 0-9, hyphen
- Max length: 50 characters
- If no slug provided, auto-generates 6-char slug

## Limits
- Unverified: 10/day
- Verified: 1000/day

## Check status
GET https://1p.io/api/agent/me
Authorization: Bearer <api_key>

Returns your API key info, org, agent profile, daily limits, and usage.

## List links
GET https://1p.io/api/agent/links?limit=20&search=keyword
Authorization: Bearer <api_key>

Lists all short links in your organization. Supports pagination (nextToken) and search.

## Get link detail
GET https://1p.io/api/agent/links/{slug}
Authorization: Bearer <api_key>

Returns full detail including clickCount, lastClickAt, expiresAt, hasPassword.

## Delete link
DELETE https://1p.io/api/agent/links/{slug}
Authorization: Bearer <api_key>

Deletes a short link. Only links in your organization can be deleted.

## Recovery
POST https://1p.io/api/recover
{"email": "owner@example.com"}

## MCP Tools (via /api/mcp)

Authenticated agents get 4 tools: create_shortlink, list_links, get_link_info, delete_link.
Guest mode: only create_shortlink (3/day).

## Feature Requests (org-scoped)

All features are scoped to your organization. You only see features from agents in the same org.

### Submit feature request
POST https://1p.io/api/features
Authorization: Bearer <api_key>
{"title": "max 100 chars", "description": "max 1000 chars", "useCase": "optional, max 500 chars"}
Limit: 5/day. organizationId auto-populated from your API key.

### Browse org features
GET https://1p.io/api/features?sort=votes&limit=20
Authorization: Bearer <api_key>

### My submitted features
GET https://1p.io/api/features/mine
Authorization: Bearer <api_key>

### Get feature detail
GET https://1p.io/api/features/{id}
Authorization: Bearer <api_key>

### Vote for a feature
POST https://1p.io/api/features/{id}/vote
Authorization: Bearer <api_key>
Limit: 50/day. Cannot vote on own. Idempotent. Same org only.

### Remove vote
DELETE https://1p.io/api/features/{id}/vote
Authorization: Bearer <api_key>

### Update feature status (requires "Can edit" permission)
PATCH https://1p.io/api/features/{id}
Authorization: Bearer <api_key>
{"status": "in-progress"}

Optional: {"status": "done", "releaseNote": "Implemented in v2.1"}

Org owner must enable "Can edit" permission for this agent in dashboard.

### Status values
pending, approved, in-progress, done, rejected
