# Ghost Admin API Reference

Condensed API endpoint reference for quick lookups with security classifications.

## ⚠️ Security & Operation Classification

### Operation Summary

| Resource | Read-Only | Destructive | Public Risk |
|----------|-----------|-------------|-------------|
| **Posts** | List (GET), Get (GET) | Create (POST), Update (PUT), Delete (DELETE) | ⚠️ Publishing makes content public |
| **Pages** | List (GET), Get (GET) | Create (POST), Update (PUT), Delete (DELETE) | ⚠️ Publishing makes content public |
| **Tags** | List (GET), Get (GET) | Create (POST), Update (PUT), Delete (DELETE) | Affects post organization |
| **Users** | List (GET), Get (GET) | Invite (POST), Update (PUT), Delete (DELETE) | Modifies site access |
| **Members** | List (GET), Get (GET), Stats (GET) | Create (POST), Update (PUT), Delete (DELETE) | Affects subscriptions |
| **Tiers** | List (GET), Get (GET) | Create (POST), Update (PUT), Archive (DELETE) | Affects pricing/access |
| **Newsletters** | List (GET), Get (GET) | Create (POST), Update (PUT), Delete (DELETE) | Affects email campaigns |
| **Comments** | List (GET), Get (GET) | Reply (POST), Moderate (PUT), Delete (DELETE) | Public interaction |
| **Images** | - | Upload (POST) | Uses storage quota |
| **Site/Settings** | Get (GET) | Update (PUT) | Changes site config |
| **Webhooks** | List (GET) | Create (POST), Update (PUT), Delete (DELETE) | External integrations |

**Total:** ~45 operations (15 read-only, 30 destructive)

### ✅ Read-Only Operations (Safe)

These operations **do not modify** your Ghost site:
- All **GET** requests
- Listing posts, pages, tags, members, tiers, newsletters, comments, users
- Viewing site configuration
- Checking member stats and analytics

**Safe to run anytime** - no risk of data modification or publication.

### ⚠️ Destructive Operations (Caution Required)

These operations **modify or delete** data:

**Content Management:**
- **POST /posts/** - Create draft post
- **PUT /posts/:id/** - Update post (can publish if status changed!)
- **DELETE /posts/:id/** - Delete post permanently
- **POST /pages/** - Create page
- **PUT /pages/:id/** - Update page (can publish!)
- **DELETE /pages/:id/** - Delete page permanently

**🚨 CRITICAL:** Setting `status: "published"` makes content **immediately public**

**Organization:**
- **POST /tags/** - Create tag
- **PUT /tags/:id/** - Update tag
- **DELETE /tags/:id/** - Delete tag (affects all tagged posts)

**Members & Subscriptions:**
- **POST /members/** - Add member
- **PUT /members/:id/** - Update member (can change subscription status)
- **DELETE /members/:id/** - Delete member permanently
- **POST /tiers/** - Create pricing tier
- **PUT /tiers/:id/** - Update tier pricing/benefits
- **DELETE /tiers/:id/** - Archive tier

**Communication:**
- **POST /newsletters/** - Create newsletter
- **PUT /newsletters/:id/** - Update newsletter settings
- **DELETE /newsletters/:id/** - Delete newsletter
- **POST /comments/** - Reply to comment (public)
- **PUT /comments/:id/** - Approve/reject comment (affects visibility)
- **DELETE /comments/:id/** - Delete comment permanently

**Site Administration:**
- **POST /users/** - Invite user (sends email)
- **PUT /users/:id/** - Update user permissions
- **DELETE /users/:id/** - Delete user
- **POST /images/upload/** - Upload image (uses storage)
- **PUT /settings/** - Change site settings
- **POST /webhooks/** - Create webhook integration

### Recovery & Undo Guide

| Operation | Undo Method | Permanent? |
|-----------|-------------|------------|
| Create post/page | Delete it | No (can delete) |
| Publish post/page | Set status to 'draft' | Content was public temporarily |
| Update post/page | Update again with old values | No version history |
| Delete post/page | **Cannot undo** | ✅ Yes - permanent |
| Create tag | Delete tag | No (safe to delete if unused) |
| Update tag | Update with old values | Affects all tagged posts |
| Delete tag | **Cannot undo** | ✅ Yes - permanent |
| Create member | Delete member | No (data kept for compliance) |
| Update member subscription | Update again | Billing may have been affected |
| Delete member | **Cannot easily undo** | Subscription data lost |
| Create tier | Archive tier | No (can unarchive) |
| Update tier pricing | Update again | Active subscriptions affected |
| Create comment reply | Delete it | Reply was public temporarily |
| Approve comment | Reject it | Comment was public temporarily |
| Delete comment | **Cannot undo** | ✅ Yes - permanent |
| Upload image | Delete file manually | Uses storage quota |
| Invite user | Revoke invitation/delete user | Invitation email sent |
| Delete user | **Cannot undo** | ✅ Yes - user access removed |

**⚠️ No version history** - Ghost does not keep revision history for most content. Always save important data before modifying.

### Security Best Practices

**Before ANY destructive operation:**

1. **Review what will change** - Read current state with GET request first
2. **Check for public risk** - Will this publish content? Affect members?
3. **Test on staging** - Use a test Ghost site when possible
4. **Save current state** - Keep a copy if you might need to revert
5. **Start with drafts** - Create content as drafts, review, then publish
6. **Verify results** - Check the response and verify with another GET

**Safe Workflow Example:**

```bash
# 1. Get current post state
curl -s "${GHOST_URL}/ghost/api/admin/posts/${POST_ID}/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  | jq '.' > post-before.json

# 2. Review what you're about to change
echo "Current status: $(jq -r '.posts[0].status' post-before.json)"
echo "Will change to: published"

# 3. Make the change
curl -X PUT "${GHOST_URL}/ghost/api/admin/posts/${POST_ID}/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"posts": [{"status": "published"}]}'

# 4. Verify the change
curl -s "${GHOST_URL}/ghost/api/admin/posts/${POST_ID}/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  | jq '.posts[0].status'

# 5. Revert if needed (within seconds)
curl -X PUT "${GHOST_URL}/ghost/api/admin/posts/${POST_ID}/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d @post-before.json
```

**For publish operations:**
- **Always review content first** - typos, formatting, links
- **Check featured image** - is it set correctly?
- **Verify tags** - are they correct for SEO/organization?
- **Test links** - do all URLs work?
- **Consider scheduling** - use `status: "scheduled"` + `published_at` for review time

**Rate limiting awareness:**
- 500 requests/hour per integration
- Batch operations count as multiple requests
- Monitor `X-RateLimit-Remaining` header

**Key rotation:**
- Create new integration every 90 days
- Revoke old integrations immediately
- Never commit keys to version control

---

## Authentication

All requests require:
```bash
Authorization: Ghost ${ADMIN_API_KEY}
Content-Type: application/json
```

Base URL: `${GHOST_URL}/ghost/api/admin/`

## API Version

Current: **v5.0**

Include in request:
```bash
Accept-Version: v5.0
```

(Optional, defaults to latest)

## Posts

| Endpoint | Method | Type | Description |
|----------|--------|------|-------------|
| `/posts/` | GET | ✅ Safe | List all posts |
| `/posts/${id}/` | GET | ✅ Safe | Get single post |
| `/posts/` | POST | ⚠️ Destructive | Create post (draft by default) |
| `/posts/${id}/` | PUT | ⚠️ Destructive | Update post (can publish!) |
| `/posts/${id}/` | DELETE | 🚨 Permanent | Delete post permanently |

**🚨 PUBLISHING RISK:** Setting `status: "published"` in POST or PUT makes content **immediately public**.

**Query params:**
- `limit` - Number of posts (default 15, max 100, 'all' for unlimited)
- `page` - Page number for pagination
- `filter` - NQL filter string
- `order` - Sort order (e.g., `published_at desc`)
- `include` - Related data (tags, authors, count.comments)

**Common filters:**
- `status:draft` - Draft posts only
- `status:published` - Published only
- `status:scheduled` - Scheduled only
- `tag:slug` - Posts with specific tag
- `title:~'keyword'` - Title contains keyword
- `published_at:>'2026-01-01'` - Published after date

## Pages

| Endpoint | Method | Type | Description |
|----------|--------|------|-------------|
| `/pages/` | GET | ✅ Safe | List all pages |
| `/pages/${id}/` | GET | ✅ Safe | Get single page |
| `/pages/` | POST | ⚠️ Destructive | Create page (draft by default) |
| `/pages/${id}/` | PUT | ⚠️ Destructive | Update page (can publish!) |
| `/pages/${id}/` | DELETE | 🚨 Permanent | Delete page permanently |

**🚨 PUBLISHING RISK:** Setting `status: "published"` makes pages **immediately public**.

Same query params as posts.

## Tags

| Endpoint | Method | Type | Description |
|----------|--------|------|-------------|
| `/tags/` | GET | ✅ Safe | List all tags |
| `/tags/${id}/` | GET | ✅ Safe | Get single tag |
| `/tags/` | POST | ⚠️ Destructive | Create tag |
| `/tags/${id}/` | PUT | ⚠️ Destructive | Update tag (affects all tagged posts) |
| `/tags/${id}/` | DELETE | 🚨 Permanent | Delete tag (removes from all posts) |

**Include options:**
- `count.posts` - Number of posts with tag

## Authors/Users

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/users/` | GET | List users |
| `/users/${id}/` | GET | Get user |
| `/users/` | POST | Create user (invite) |
| `/users/${id}/` | PUT | Update user |
| `/users/${id}/` | DELETE | Delete user |

**Include options:**
- `count.posts` - Number of posts by author

## Members

| Endpoint | Method | Type | Description |
|----------|--------|------|-------------|
| `/members/` | GET | ✅ Safe | List members |
| `/members/${id}/` | GET | ✅ Safe | Get member |
| `/members/` | POST | ⚠️ Destructive | Create member (may send email) |
| `/members/${id}/` | PUT | ⚠️ Destructive | Update member (can change subscription!) |
| `/members/${id}/` | DELETE | 🚨 Permanent | Delete member (subscription data lost) |

**Query params:**
- `search` - Search name/email
- `filter` - NQL filter (e.g., `status:paid`)
- `include` - Related data (newsletters, subscriptions)

**Common filters:**
- `status:free` - Free members
- `status:paid` - Paid members
- `status:comped` - Comped members
- `created_at:>'2026-01-01'` - Joined after date
- `label:vip` - Members with label

## Member Stats

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/members/stats/count/` | GET | Total member counts |
| `/members/stats/mrr/` | GET | Monthly recurring revenue |

## Tiers

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/tiers/` | GET | List subscription tiers |
| `/tiers/${id}/` | GET | Get tier |
| `/tiers/` | POST | Create tier |
| `/tiers/${id}/` | PUT | Update tier |
| `/tiers/${id}/` | DELETE | Delete tier (archive) |

## Newsletters

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/newsletters/` | GET | List newsletters |
| `/newsletters/${id}/` | GET | Get newsletter |
| `/newsletters/` | POST | Create newsletter |
| `/newsletters/${id}/` | PUT | Update newsletter |
| `/newsletters/${id}/` | DELETE | Delete newsletter |

## Comments (if enabled)

| Endpoint | Method | Type | Description |
|----------|--------|------|-------------|
| `/comments/` | GET | ✅ Safe | List comments |
| `/comments/${id}/` | GET | ✅ Safe | Get comment |
| `/comments/` | POST | ⚠️ Destructive | Create comment reply (public) |
| `/comments/${id}/` | PUT | ⚠️ Destructive | Update comment status (approve/reject, affects visibility) |
| `/comments/${id}/` | DELETE | 🚨 Permanent | Delete comment permanently |

**Query params:**
- `filter` - NQL filter (e.g., `post_id:'${post_id}'`)
- `include` - Related data (post, member)

**Common filters:**
- `status:published` - Approved comments
- `status:pending` - Awaiting moderation
- `post_id:'${id}'` - Comments on specific post

## Images

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/images/upload/` | POST | Upload image |

**Request:**
```bash
curl -X POST "${GHOST_URL}/ghost/api/admin/images/upload/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -F "file=@image.jpg" \
  -F "purpose=image" \
  -F "ref=post_id_here"
```

Returns image URL.

## Site

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/site/` | GET | Get site configuration |

Returns:
- Title, description
- URL, timezone
- Version info
- Feature flags

## Settings

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/settings/` | GET | Get all settings |
| `/settings/` | PUT | Update settings |

**Note:** Most settings managed via Ghost Admin UI, not API.

## Webhooks

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/webhooks/` | GET | List webhooks |
| `/webhooks/` | POST | Create webhook |
| `/webhooks/${id}/` | PUT | Update webhook |
| `/webhooks/${id}/` | DELETE | Delete webhook |

**Webhook events:**
- `site.changed`
- `post.added`, `post.deleted`, `post.edited`, `post.published`, `post.unpublished`, `post.scheduled`
- `page.added`, `page.deleted`, `page.edited`, `page.published`, `page.unpublished`, `page.scheduled`
- `tag.added`, `tag.deleted`, `tag.edited`
- `member.added`, `member.deleted`, `member.edited`
- `member.subscription.added`, `member.subscription.deleted`, `member.subscription.updated`

## Theme Management

| Endpoint | Method | Description | Safety |
|----------|--------|-------------|--------|
| `/themes/` | GET | List installed themes | ✅ Safe |
| `/themes/upload/` | POST | Upload theme ZIP | ⚠️ Destructive |
| `/themes/${name}/activate/` | PUT | Activate theme | ⚠️ Destructive |
| `/themes/${name}/download/` | GET | Download theme ZIP | ✅ Safe |
| `/themes/${name}/` | DELETE | Delete theme | ⚠️ Destructive |

**Upload parameters:**
- `file` - Theme ZIP file (multipart/form-data)
- `activate` - Optional: activate after upload (true/false)

**Notes:**
- Themes control site appearance - activation is **immediate and public**
- Cannot delete active theme (switch first)
- Themes must be valid Ghost theme ZIP files
- See [references/themes.md](themes.md) for complete documentation

**CLI tool:**
```bash
# See theme-manager.js for full theme management
node theme-manager.js list
node theme-manager.js upload theme.zip --activate
node theme-manager.js activate theme-name
node theme-manager.js delete old-theme
```

## Response Format

All responses follow this structure:

**Success:**
```json
{
  "posts": [...],
  "meta": {
    "pagination": {
      "page": 1,
      "limit": 15,
      "pages": 5,
      "total": 67,
      "next": 2,
      "prev": null
    }
  }
}
```

**Error:**
```json
{
  "errors": [{
    "message": "Error message",
    "context": "Additional context",
    "type": "ValidationError",
    "details": null,
    "property": null,
    "help": "Help text",
    "code": "VALIDATION_ERROR",
    "id": "error_id"
  }]
}
```

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Success |
| 201 | Created - Resource created |
| 204 | No Content - Deleted successfully |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid/missing API key |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 422 | Unprocessable Entity - Validation failed |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Ghost error |

## Rate Limits

- **500 requests per hour** per integration
- Headers returned:
  - `X-RateLimit-Limit: 500`
  - `X-RateLimit-Remaining: 498`
  - `X-RateLimit-Reset: 1643673600`

When rate limited (429), response includes:
```json
{
  "errors": [{
    "message": "Too many requests.",
    "type": "RateLimitError"
  }]
}
```

## NQL (Ghost Query Language)

Ghost uses NQL for filtering. Common patterns:

**Comparisons:**
- `field:value` - Equals
- `field:~'value'` - Contains (case-insensitive)
- `field:>'value'` - Greater than
- `field:<'value'` - Less than
- `field:>='value'` - Greater than or equal
- `field:<='value'` - Less than or equal

**Logical:**
- `+` - AND (e.g., `status:published+tag:news`)
- `,` - OR (e.g., `status:draft,status:scheduled`)
- `-` - NOT (e.g., `-tag:archived`)

**Grouping:**
- `(...)` - Parentheses for precedence

**Examples:**
- `status:published+tag:tutorial` - Published posts tagged "tutorial"
- `status:[draft,scheduled]` - Drafts OR scheduled
- `published_at:>'2026-01-01'+tag:~'tech'` - Published after date, tech-related
- `-status:archived+created_at:>'2025-01-01'` - Not archived, created this year

## Pagination

Large result sets are paginated:

**Request:**
```bash
curl "${GHOST_URL}/ghost/api/admin/posts/?page=2&limit=15"
```

**Response meta:**
```json
{
  "meta": {
    "pagination": {
      "page": 2,
      "limit": 15,
      "pages": 5,
      "total": 67,
      "next": 3,
      "prev": 1
    }
  }
}
```

**Get all results:**
Use `limit=all` to bypass pagination (use carefully, can be slow for large datasets).

## Content Formats

Ghost accepts HTML for post/page content:

**Field:** `html`

**Format:** Valid HTML string

**Common elements:**
- `<p>` - Paragraphs
- `<h2>`, `<h3>`, etc. - Headings
- `<ul>`, `<ol>`, `<li>` - Lists
- `<a href="">` - Links
- `<img src="" alt="">` - Images
- `<pre><code>` - Code blocks
- `<blockquote>` - Quotes

**Ghost-specific cards:**
- `<figure class="kg-card kg-image-card">` - Image cards
- `<figure class="kg-card kg-gallery-card">` - Gallery
- `<figure class="kg-card kg-bookmark-card">` - Bookmark
- `<div class="kg-card kg-button-card">` - Button

**Alternative:** Ghost also supports `mobiledoc` and `lexical` formats (advanced).

## Common Patterns

### Paginated List

```bash
page=1
while true; do
  response=$(curl -s "${GHOST_URL}/ghost/api/admin/posts/?page=${page}" \
    -H "Authorization: Ghost ${GHOST_KEY}")
  
  # Process posts
  echo "$response" | jq '.posts[]'
  
  # Check if there's a next page
  next=$(echo "$response" | jq '.meta.pagination.next')
  if [ "$next" = "null" ]; then break; fi
  
  page=$next
done
```

### Batch Update

```bash
# Get all posts with old tag
posts=$(curl -s "${GHOST_URL}/ghost/api/admin/posts/?filter=tag:old-tag&limit=all" \
  -H "Authorization: Ghost ${GHOST_KEY}" | \
  jq -r '.posts[].id')

# Update each post
for id in $posts; do
  curl -X PUT "${GHOST_URL}/ghost/api/admin/posts/${id}/" \
    -H "Authorization: Ghost ${GHOST_KEY}" \
    -H "Content-Type: application/json" \
    -d '{
      "posts": [{
        "tags": [{"name": "new-tag"}]
      }]
    }'
done
```

### Error Handling

```bash
response=$(curl -s -w "\n%{http_code}" "${GHOST_URL}/ghost/api/admin/posts/" \
  -H "Authorization: Ghost ${GHOST_KEY}")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
  echo "$body" | jq '.posts'
else
  echo "Error $http_code:"
  echo "$body" | jq '.errors'
fi
```

## Additional Resources

- **Official docs:** https://ghost.org/docs/admin-api/
- **API explorer:** https://ghost.org/docs/admin-api/#explorer
- **JavaScript library:** @tryghost/admin-api
- **Community:** Ghost Forum (forum.ghost.org)
