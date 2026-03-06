# Ghost Skill - Troubleshooting

## Credentials missing

```
GhostError: Credentials missing. Set GHOST_URL / GHOST_ADMIN_KEY in
~/.openclaw/secrets/ghost_creds or as environment variables.
```
→ Run `python3 scripts/setup.py` or create the file manually (see SKILL.md).

---

## Invalid Admin API Key format

```
GhostError: GHOST_ADMIN_KEY must be in format 'id:secret_hex'
```
Cause: key copied incorrectly or truncated.

Fix: re-copy from Ghost Admin → Settings → Integrations → your integration → **Admin API Key**.
The format is exactly `<24-char-hex-id>:<64-char-hex-secret>`.

---

## 401 Unauthorized

Cause: JWT expired, wrong key, or key revoked.

Fixes:
- JWT tokens are generated fresh per request (5-min TTL) - expiry shouldn't be the issue
- Verify the key is still active: Ghost Admin → Integrations → check the integration exists
- Confirm `secret_hex` is valid hex: `python3 -c "bytes.fromhex('your_secret')"`
- Confirm the `GHOST_URL` doesn't have a trailing slash

---

## 404 Not Found

Cause: wrong URL, Ghost not running, or resource deleted.

Fixes:
- Test: `python3 scripts/ghost.py site` - if this fails, the URL or Ghost itself is the problem
- Ensure `GHOST_URL` points to the Ghost root, e.g. `https://blog.example.com` not `https://blog.example.com/ghost`
- For get by slug: slug may have changed after a title update

---

## 409 Conflict - updated_at mismatch

```json
{"errors": [{"type": "ConflictError", "message": "Saving failed! ..."}]}
```
Cause: `updated_at` sent in the PUT request doesn't match the current value (optimistic locking).

Fix: the skill's `update_post`/`update_page` auto-fetches `updated_at` if not provided.
If calling manually, always fetch first:
```python
post = gc.get_post(post_id)
gc.update_post(post_id, updated_at=post["updated_at"], title="New Title")
```

---

## 409 Conflict - slug already exists

Cause: trying to create a post/tag with a slug that already exists.

Fix: either omit `slug` (Ghost auto-increments: `my-post-2`), or use a unique slug explicitly.

---

## 422 Validation Failed

Cause: missing required field or invalid value.

Common cases:
- `POST /posts` without `title` → add title
- Invalid `status` value → use `draft`, `published`, or `scheduled`
- `scheduled` without `published_at` → add a future ISO 8601 timestamp

---

## PermissionDeniedError: allow_publish

```
PermissionDeniedError: allow_publish is disabled in config.json
```
→ Either set `allow_publish: true` in `config.json`, or use `status: "draft"`.

---

## PermissionDeniedError: allow_delete

```
PermissionDeniedError: allow_delete is disabled in config.json
```
→ Set `allow_delete: true` in `config.json` if deletion is intentional.

---

## PermissionDeniedError: allow_member_access

```
PermissionDeniedError: allow_member_access is disabled in config.json
```
→ Set `allow_member_access: true` in `config.json` to enable member operations.

---

## HTML content not rendering

Cause: `html` field sent but Ghost isn't converting it properly.

Notes:
- Ghost v5 stores content as Lexical JSON internally
- When you `POST` with `html`, Ghost converts it via its mobiledoc/lexical importer
- Ensure HTML is valid and well-formed - unclosed tags can cause silent failures
- To retrieve rendered HTML: add `?formats=html` to GET requests

Fix:
```python
gc.get_post(post_id)  # default doesn't include html
# Request HTML explicitly:
import requests
r = requests.get(f"{gc.api_url}/posts/{post_id}?formats=html", headers=gc._headers())
```

---

## Image upload fails

Cause: unsupported format, file too large, or storage full.

Supported formats: jpg, jpeg, png, gif, svg, webp.
Max size: depends on Ghost config (default ~25MB).

Fix:
```bash
python3 scripts/ghost.py image-upload ./image.png --alt "Description"
# returns {"url": "https://...", "ref": "..."}
```

---

## Members endpoint returns 403

Cause: the integration/API key doesn't have member access, or Ghost plan doesn't include it.

Fix: verify the integration has member access in Ghost Admin → Integrations.
Also check `allow_member_access: true` in `config.json`.

---

## Rate limiting (429)

Ghost Admin API has no official rate limits for self-hosted instances.
If you hit 429, it may be from a reverse proxy (nginx/Caddy rate limiting).

Fix: add delays between requests if batch-processing large volumes.
