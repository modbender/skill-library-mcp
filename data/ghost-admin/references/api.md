# Ghost Admin API Reference

Read this file when you need details on specific endpoints, field names, filters,
or error codes not covered by the main SKILL.md.

## Table of Contents
1. [Base URL & Auth](#1-base-url--auth)
2. [JWT Generation](#2-jwt-generation)
3. [Posts](#3-posts)
4. [Pages](#4-pages)
5. [Tags](#5-tags)
6. [Images & Media](#6-images--media)
7. [Members](#7-members)
8. [Newsletters](#8-newsletters)
9. [Tiers](#9-tiers)
10. [Site & Users](#10-site--users)
11. [Filtering & Pagination](#11-filtering--pagination)
12. [Post / Page Fields](#12-post--page-fields)
13. [Error Codes](#13-error-codes)

---

## 1. Base URL & Auth

```
Base URL : {GHOST_URL}/ghost/api/admin
Headers  :
  Authorization : Ghost {jwt_token}
  Accept-Version: v5.0
  Content-Type  : application/json  (for POST/PUT)
```

---

## 2. JWT Generation

Admin API Key format: `{id}:{secret_hex}` (copy from Ghost Admin → Integrations).

```python
import hmac, hashlib, base64, json, time

def b64url(data): return base64.urlsafe_b64encode(data).rstrip(b"=").decode()
def make_jwt(key_id, secret_hex):
    now = int(time.time())
    h = b64url(json.dumps({"alg":"HS256","typ":"JWT","kid":key_id}, separators=(",",":")).encode())
    p = b64url(json.dumps({"iat":now,"exp":now+300,"aud":"/admin/"}, separators=(",",":")).encode())
    sig = hmac.new(bytes.fromhex(secret_hex), f"{h}.{p}".encode(), hashlib.sha256).digest()
    return f"{h}.{p}.{b64url(sig)}"
```

Tokens expire in 5 minutes. Generate a fresh token per request.

---

## 3. Posts

### GET /posts - List posts
```
Params:
  limit   : int    - default 15, max 'all'
  page    : int    - default 1
  filter  : string - NQL filter (see §11)
  order   : string - "published_at desc" (default)
  include : string - comma-separated: "tags,authors,tiers"
  fields  : string - comma-separated field names (projection)
  formats : string - "html,lexical,mobiledoc,plaintext"
Returns: { posts: [...], meta: { pagination: { page, limit, pages, total, next, prev } } }
```

### GET /posts/{id} - Get by ID
### GET /posts/slug/{slug} - Get by slug

### POST /posts - Create post
```json
{
  "posts": [{
    "title":             "string (required)",
    "html":              "string - HTML content (converted to Lexical internally)",
    "lexical":           "string - Lexical JSON (preferred for Ghost v5)",
    "status":            "draft | published | scheduled",
    "tags":              [{"name": "tag-name"} | {"id": "tag-id"}],
    "authors":           [{"id": "author-id"}],
    "featured":          false,
    "slug":              "string - auto-generated if omitted",
    "custom_excerpt":    "string",
    "meta_title":        "string",
    "meta_description":  "string",
    "og_title":          "string",
    "og_description":    "string",
    "twitter_title":     "string",
    "twitter_description":"string",
    "feature_image":     "string - URL",
    "published_at":      "ISO 8601 - required when status=scheduled",
    "visibility":        "public | members | paid | tiers",
    "canonical_url":     "string"
  }]
}
Returns: { posts: [created_post] }
```

### PUT /posts/{id} - Update post
```
Body: { "posts": [{ "updated_at": "ISO 8601 (required)", ...fields }] }
Note: updated_at must match the current value to prevent conflicts. Fetch it first.
```

### DELETE /posts/{id}
```
Status: 204 No Content
```

---

## 4. Pages

Identical schema to Posts. Endpoints:
- `GET /pages`, `GET /pages/{id}`, `GET /pages/slug/{slug}`
- `POST /pages`, `PUT /pages/{id}`, `DELETE /pages/{id}`

Pages do not have tags/newsletters/email settings by default.

---

## 5. Tags

### GET /tags - List tags
```
Params: limit, page, include="count.posts", filter, order
Returns: { tags: [...], meta: { pagination: {...} } }
```

### GET /tags/{id} | GET /tags/slug/{slug}

### POST /tags - Create tag
```json
{
  "tags": [{
    "name":             "string (required)",
    "slug":             "string - auto-generated if omitted",
    "description":      "string",
    "feature_image":    "string - URL",
    "visibility":       "public | internal",
    "meta_title":       "string",
    "meta_description": "string",
    "og_title":         "string",
    "twitter_title":    "string",
    "accent_color":     "#hex"
  }]
}
```

### PUT /tags/{id} - Update tag (no updated_at required)
### DELETE /tags/{id} - Status 204

---

## 6. Images & Media

### POST /images/upload - Upload image
```
Content-Type: multipart/form-data
Fields:
  file     : binary (jpg, png, gif, svg, webp)
  purpose  : "image" (default) | "profile_image" | "icon"
  alt      : string (optional alt text)
  ref      : string (optional reference/filename hint)
Returns: { images: [{ url, ref }] }
```

### POST /media/upload - Upload video/audio
```
Same multipart format. Supported: mp4, webm, ogv, mp3, wav, ogg, m4a.
Returns: { media: [{ url, ref }] }
```

### POST /files/upload - Upload any file
```
Returns: { files: [{ url, ref }] }
```

---

## 7. Members

Requires `allow_member_access: true` in config.json.

### GET /members
```
Params: limit, page, filter, order, include="newsletters,labels,subscriptions"
Filter examples:
  subscribed:true
  status:paid
  label:[my-label]
```

### GET /members/{id}
### POST /members
```json
{ "members": [{ "email": "required", "name": "string", "note": "string",
                "labels": [{"name":"label"}], "newsletters": [{"id":"id"}] }] }
```

### PUT /members/{id}
### DELETE /members/{id} - Status 204

---

## 8. Newsletters

### GET /newsletters
```
Params: limit, filter, include="count.members,count.posts"
```
### GET /newsletters/{id}
### POST /newsletters - Create newsletter (name required)
### PUT /newsletters/{id} - Update newsletter

---

## 9. Tiers

### GET /tiers
```
Params: limit, include="monthly_price,yearly_price,benefits"
Returns active and archived tiers (subscription plans)
```

---

## 10. Site & Users

### GET /site
```
Returns: { site: { title, description, url, version, ... } }
```

### GET /users - List users (authors/staff)
### GET /users/{id} | GET /users/me
```
include: "roles,count.posts"
```

---

## 11. Filtering & Pagination

Ghost uses **NQL (Nangular Query Language)** for filtering.

### NQL syntax
```
filter=status:published
filter=status:published+featured:true
filter=status:[draft,scheduled]
filter=tag:devops
filter=published_at:>'2024-01-01'
filter=title:~'linux'           # contains
```

### Operators
| Op | Meaning |
|----|---------|
| `:` | equals |
| `:-` | not equals |
| `:>` / `:<` | greater/less than |
| `:>=` / `:<=` | gte / lte |
| `:~` | contains |
| `+` | AND |
| `,` | OR |
| `[a,b]` | IN |

### Pagination
```json
"meta": {
  "pagination": {
    "page": 1, "limit": 15,
    "pages": 4, "total": 52,
    "next": 2, "prev": null
  }
}
```
Use `limit=all` to retrieve everything (use with caution on large sites).

---

## 12. Post / Page Fields

Key fields returned in list/get responses:

| Field | Type | Notes |
|-------|------|-------|
| `id` | string | 24-char hex ID |
| `uuid` | string | UUID |
| `title` | string | |
| `slug` | string | URL-safe identifier |
| `html` | string | Rendered HTML (included with `formats=html`) |
| `lexical` | string | JSON string (Lexical editor format) |
| `status` | string | `draft`, `published`, `scheduled` |
| `visibility` | string | `public`, `members`, `paid` |
| `featured` | bool | |
| `published_at` | ISO 8601 | null if draft |
| `updated_at` | ISO 8601 | **Required for PUT requests** |
| `created_at` | ISO 8601 | |
| `url` | string | Full public URL |
| `excerpt` | string | Auto-generated from content |
| `custom_excerpt` | string | Manual excerpt |
| `reading_time` | int | Minutes |
| `tags` | array | `[{id, name, slug, ...}]` |
| `authors` | array | `[{id, name, slug, ...}]` |
| `feature_image` | string | Cover image URL |
| `meta_title` | string | SEO title |
| `meta_description` | string | SEO description |
| `og_title` / `og_description` | string | Open Graph |
| `twitter_title` / `twitter_description` | string | Twitter card |
| `canonical_url` | string | |
| `email_only` | bool | Send to members but don't publish publicly |

---

## 13. Error Codes

### HTTP status codes
| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 204 | No Content (DELETE success) |
| 400 | Bad Request - malformed body, missing fields |
| 401 | Unauthorized - invalid or expired JWT |
| 403 | Forbidden - insufficient permissions |
| 404 | Not Found |
| 409 | Conflict - slug already exists, or `updated_at` mismatch on PUT |
| 422 | Validation Failed - see errors array |
| 429 | Rate Limited |
| 500 | Internal Server Error |

### Error response format
```json
{
  "errors": [{
    "message": "human-readable message",
    "context": "additional context",
    "type": "ValidationError | NotFoundError | UnauthorizedError | ...",
    "details": null,
    "property": "field name if applicable",
    "help": "docs URL",
    "code": "ERROR_CODE",
    "id": "error-uuid"
  }]
}
```

### Common `updated_at` conflict (409)
Always fetch the post before updating to get the current `updated_at`.
Ghost uses optimistic locking to prevent overwriting concurrent edits.
