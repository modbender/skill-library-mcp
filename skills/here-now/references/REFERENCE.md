# here.now API Reference

Base URL: `https://here.now`

## Authentication

Two modes:

- **Authenticated**: include `Authorization: Bearer <API_KEY>` header.
- **Anonymous**: omit the header entirely. Publishes expire in 24 hours with lower limits.

### Optional client attribution header

You can include an optional header on publish calls:

- `X-HereNow-Client: <agent>/<tool>`

Examples:

- `X-HereNow-Client: cursor/publish-sh`
- `X-HereNow-Client: claude-code/publish-sh`
- `X-HereNow-Client: codex/cli`
- `X-HereNow-Client: openclaw/direct-api`

This helps here.now debug publish reliability by client. Missing or invalid values are ignored; publishes are never rejected because this header is absent.

### Getting an API key (agent-assisted sign-up)

Agents can trigger the sign-up flow on behalf of the user:

**1. Send magic link:**

```bash
curl -sS https://here.now/api/auth/login \
  -H "content-type: application/json" \
  -d '{"email": "user@example.com"}'
```

Response: `{"success": true}`

No account needed beforehand. If the email is new, an account is created automatically when the user clicks the link.

**2. User clicks the link in their email.** They land on the here.now dashboard, signed in.

**3. User copies their API key** from the dashboard (API key tab) and provides it to the agent.

The agent cannot retrieve the API key programmatically (it requires a browser session). The user must copy it manually.

The login endpoint also accepts an optional `returnTo` field (a path like `"/"`), which controls where the user lands after clicking the magic link.

## Endpoints

### Create a new publish

`POST /api/v1/publish`

Creates a new publish with a random slug. Works with or without authentication.

**Request body:**

```json
{
  "files": [
    { "path": "index.html", "size": 1234, "contentType": "text/html; charset=utf-8" },
    { "path": "assets/app.js", "size": 999, "contentType": "text/javascript; charset=utf-8" }
  ],
  "ttlSeconds": null,
  "viewer": {
    "title": "My site",
    "description": "Published by an agent",
    "ogImagePath": "assets/cover.png"
  }
}
```

- `files` (required): array of `{ path, size, contentType }`. At least one file. Paths should be relative to the site root (e.g. `index.html`, `assets/style.css`) — don't include a parent directory name like `my-project/index.html`.
- `ttlSeconds` (optional): expiry in seconds. Ignored for anonymous publishes (always 24h).
- `viewer` (optional): metadata for auto-viewer pages (only used when no `index.html`).

**Response (authenticated):**

```json
{
  "slug": "bright-canvas-a7k2",
  "siteUrl": "https://bright-canvas-a7k2.here.now/",
  "status": "pending",
  "isLive": false,
  "requiresFinalize": true,
  "note": "Publish created, but this slug is not live yet. Upload all files to upload.uploads[], then POST upload.finalizeUrl with {\"versionId\":\"...\"}.",
  "upload": {
    "versionId": "01J...",
    "uploads": [
      {
        "path": "index.html",
        "method": "PUT",
        "url": "https://<presigned-r2-url>",
        "headers": { "Content-Type": "text/html; charset=utf-8" }
      }
    ],
    "finalizeUrl": "https://here.now/api/v1/publish/bright-canvas-a7k2/finalize",
    "expiresInSeconds": 3600
  }
}
```

**This step only creates a pending publish. It is not complete yet.**

- You **must upload every file** in `upload.uploads[]`.
- Then you **must finalize** with `POST upload.finalizeUrl` and body `{ "versionId": "..." }`.
- For brand-new slugs, `siteUrl` may return 404 until finalize succeeds.
- For updates to an existing slug, the previous version can stay live until finalize switches to the new version.

**Response (anonymous), additional fields:**

```json
{
  "claimToken": "abc123...",
  "claimUrl": "https://here.now/claim?slug=bright-canvas-a7k2&token=abc123...",
  "expiresAt": "2026-02-19T01:00:00.000Z",
  "anonymous": true,
  "warning": "IMPORTANT: Save the claimToken and claimUrl. They are returned only once and cannot be recovered. Share the claimUrl with the user so they can keep the site permanently."
}
```

**IMPORTANT: The `claimToken` and `claimUrl` are returned only once and cannot be recovered. Always save the `claimToken` and share the `claimUrl` with the user so they can claim the site and keep it permanently. If you lose the claim token, the site will expire in 24 hours with no way to save it.**

`claimToken`, `claimUrl`, and `expiresAt` are only present for anonymous publishes. Authenticated publishes do not include these fields.

---

### Upload files

For each entry in `upload.uploads[]`, PUT the file to the presigned URL:

```bash
curl -X PUT "<presigned-url>" \
  -H "Content-Type: <content-type>" \
  --data-binary @<local-file>
```

Uploads can run in parallel. Presigned URLs are valid for 1 hour.

---

### Finalize a publish

`POST /api/v1/publish/:slug/finalize`

Makes the publish live by flipping the slug pointer to the new version.

**Request body:**

```json
{ "versionId": "01J..." }
```

**Auth:**
- Owned publishes: requires `Authorization: Bearer <API_KEY>`.
- Anonymous publishes: no auth required for finalize.

**Response:**

```json
{
  "success": true,
  "slug": "bright-canvas-a7k2",
  "siteUrl": "https://bright-canvas-a7k2.here.now/",
  "previousVersionId": null,
  "currentVersionId": "01J..."
}
```

---

### Update an existing publish

`PUT /api/v1/publish/:slug`

Same request body as create. Returns new presigned upload URLs and a new `finalizeUrl`.
The update response also includes `status: "pending"` and `isLive: false` to indicate the new version is not live until finalize.

**Auth for owned publishes:** requires `Authorization: Bearer <API_KEY>` matching the owner.

**Auth for anonymous publishes:** include `claimToken` in the request body:

```json
{
  "files": [...],
  "claimToken": "<claimToken>"
}
```

Anonymous updates do not extend the original expiration timer. Returns `410 Gone` if expired.

---

### Claim an anonymous publish

`POST /api/v1/publish/:slug/claim`

Transfers ownership to an authenticated user and removes the expiration.

**Requires:** `Authorization: Bearer <API_KEY>`

**Request body:**

```json
{ "claimToken": "abc123..." }
```

**Response:**

```json
{
  "success": true,
  "slug": "bright-canvas-a7k2",
  "siteUrl": "https://bright-canvas-a7k2.here.now/",
  "expiresAt": null
}
```

Users can also claim by visiting the `claimUrl` in a browser and signing in.

---

### Patch viewer metadata

`PATCH /api/v1/publish/:slug/metadata`

Update title, description, og:image, or TTL without re-uploading files.

**Requires:** `Authorization: Bearer <API_KEY>`

**Request body:**

```json
{
  "ttlSeconds": 604800,
  "viewer": {
    "title": "Updated title",
    "description": "New description",
    "ogImagePath": "assets/cover.png"
  }
}
```

All fields optional. `ogImagePath` must reference an image file within the current publish.

**Response:**

```json
{
  "success": true,
  "effectiveForRootDocument": true,
  "note": "Viewer metadata applies because this publish has no index.html."
}
```

If the publish has an `index.html`, viewer metadata is stored but the site's own HTML controls what browsers see.

---

### Delete a publish

`DELETE /api/v1/publish/:slug`

Hard deletes the publish, all versions, and the slug-index entry.

**Requires:** `Authorization: Bearer <API_KEY>`

**Response:**

```json
{ "success": true }
```

---

### List publishes

`GET /api/v1/publishes`

Returns all publishes owned by the authenticated user.

**Requires:** `Authorization: Bearer <API_KEY>`

**Response:**

```json
{
  "publishes": [
    {
      "slug": "bright-canvas-a7k2",
      "siteUrl": "https://bright-canvas-a7k2.here.now/",
      "updatedAt": "2026-02-18T...",
      "expiresAt": null,
      "status": "active",
      "currentVersionId": "01J...",
      "pendingVersionId": null
    }
  ]
}
```

---

### Refresh upload URLs

`POST /api/v1/publish/:slug/uploads/refresh`

Returns fresh presigned URLs for a pending upload (same version, no new version created).

**Requires:** `Authorization: Bearer <API_KEY>`

Use when presigned URLs expire mid-upload (they're valid for 1 hour).

---

## URL Structure

Each publish gets its own subdomain: `https://<slug>.here.now/`

Asset paths work naturally from the subdomain root:
- `/styles.css`, `/images/a.jpg` resolve as expected
- Relative paths (`styles.css`, `./images/a.jpg`) also work

### Serving rules

1. If `index.html` exists at root → serve it as the document.
2. Else if exactly one file in the entire publish → serve an auto-viewer page (images, PDF, video, audio get rich viewers; everything else gets a download page).
3. Else if an `index.html` exists in any subdirectory → serve the first one found.
4. Otherwise → serve an auto-generated directory listing. Folders are clickable, images render as a gallery, and other files are listed with sizes. No `index.html` required.

Direct file paths always work: `https://<slug>.here.now/report.pdf`

## Limits

|                | Anonymous          | Authenticated                |
| -------------- | ------------------ | ---------------------------- |
| Max file size  | 250 MB             | 5 GB                         |
| Expiry         | 24 hours           | Permanent (or custom TTL)    |
| Rate limit     | 5 / hour / IP      | 60 / hour / account          |
| Account needed | No                 | Yes (get key at here.now)    |
