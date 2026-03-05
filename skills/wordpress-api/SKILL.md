---
name: wordpress
description: |
  WordPress.com API integration with managed OAuth. Manage posts, pages, sites, and content.
  Use this skill when users want to create, read, update, or delete WordPress.com posts, pages, or manage site content.
  For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
  Requires network access and valid Maton API key.
metadata:
  author: maton
  version: "1.0"
  clawdbot:
    emoji: 🧠
    requires:
      env:
        - MATON_API_KEY
---

# WordPress.com

Access the WordPress.com REST API with managed OAuth authentication. Create and manage posts, pages, and site content on WordPress.com hosted sites.

## Quick Start

```bash
# List posts from a site
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/wordpress/rest/v1.1/sites/{site_id}/posts?number=10')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/wordpress/rest/v1.1/{endpoint}
```

The gateway proxies requests to `public-api.wordpress.com` and automatically injects your OAuth token.

**Note:** WordPress.com uses the REST v1.1 API. Site-specific endpoints use the pattern `/sites/{site_id_or_domain}/{resource}`.

## Authentication

All requests require the Maton API key in the Authorization header:

```
Authorization: Bearer $MATON_API_KEY
```

**Environment Variable:** Set your API key as `MATON_API_KEY`:

```bash
export MATON_API_KEY="YOUR_API_KEY"
```

### Getting Your API Key

1. Sign in or create an account at [maton.ai](https://maton.ai)
2. Go to [maton.ai/settings](https://maton.ai/settings)
3. Copy your API key

## Connection Management

Manage your WordPress.com OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=wordpress&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'wordpress'}).encode()
req = urllib.request.Request('https://ctrl.maton.ai/connections', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Get Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "connection": {
    "connection_id": "fb327990-1a43-4325-9c15-bad771b6a288",
    "status": "ACTIVE",
    "creation_time": "2026-02-10T07:46:26.908898Z",
    "last_updated_time": "2026-02-10T07:49:33.440422Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "wordpress",
    "metadata": {}
  }
}
```

Open the returned `url` in a browser to complete OAuth authorization.

### Delete Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}', method='DELETE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Specifying Connection

If you have multiple WordPress.com connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/wordpress/rest/v1.1/sites/{site_id}/posts')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', 'fb327990-1a43-4325-9c15-bad771b6a288')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Sites

#### Get Site Information

```bash
GET /wordpress/rest/v1.1/sites/{site_id_or_domain}
```

**Response:**
```json
{
  "ID": 252505333,
  "name": "My Blog",
  "description": "Just another WordPress.com site",
  "URL": "https://myblog.wordpress.com",
  "capabilities": {
    "edit_pages": true,
    "edit_posts": true,
    "edit_others_posts": true,
    "delete_posts": true
  }
}
```

The site identifier can be either:
- Numeric site ID (e.g., `252505333`)
- Domain name (e.g., `myblog.wordpress.com` or `en.blog.wordpress.com`)

### Posts

#### List Posts

```bash
GET /wordpress/rest/v1.1/sites/{site}/posts
```

**Query Parameters:**
- `number` - Number of posts to return (default: 20, max: 100)
- `offset` - Offset for pagination
- `page` - Page number
- `page_handle` - Cursor for pagination (from response `meta.next_page`)
- `order` - Sort order: `DESC` or `ASC`
- `order_by` - Sort field: `date`, `modified`, `title`, `comment_count`, `ID`
- `status` - Post status: `publish`, `draft`, `pending`, `private`, `future`, `trash`, `any`
- `type` - Post type: `post`, `page`, `any`
- `search` - Search term
- `category` - Category slug
- `tag` - Tag slug
- `author` - Author ID
- `fields` - Comma-separated list of fields to return

**Response:**
```json
{
  "found": 150,
  "posts": [
    {
      "ID": 83587,
      "site_ID": 3584907,
      "author": {
        "ID": 257479511,
        "login": "username",
        "name": "John Doe"
      },
      "date": "2026-02-09T15:00:00+00:00",
      "modified": "2026-02-09T16:30:00+00:00",
      "title": "My Post Title",
      "excerpt": "<p>Post excerpt...</p>",
      "content": "<p>Full post content...</p>",
      "slug": "my-post-title",
      "status": "publish",
      "type": "post",
      "categories": {...},
      "tags": {...}
    }
  ],
  "meta": {
    "next_page": "value=2026-02-09T15%3A00%3A00%2B00%3A00&id=83587"
  }
}
```

#### Get Post

```bash
GET /wordpress/rest/v1.1/sites/{site}/posts/{post_id}
```

**Response:**
```json
{
  "ID": 83587,
  "site_ID": 3584907,
  "author": {...},
  "date": "2026-02-09T15:00:00+00:00",
  "title": "My Post Title",
  "content": "<p>Full post content...</p>",
  "slug": "my-post-title",
  "status": "publish",
  "type": "post",
  "categories": {
    "news": {
      "ID": 123,
      "name": "News",
      "slug": "news"
    }
  },
  "tags": {
    "featured": {
      "ID": 456,
      "name": "Featured",
      "slug": "featured"
    }
  }
}
```

#### Create Post

```bash
POST /wordpress/rest/v1.1/sites/{site}/posts/new
Content-Type: application/json

{
  "title": "New Post Title",
  "content": "<p>Post content here...</p>",
  "status": "draft",
  "categories": "news, updates",
  "tags": "featured, important"
}
```

**Parameters:**
- `title` - Post title (required)
- `content` - Post content (HTML)
- `excerpt` - Post excerpt
- `status` - `publish`, `draft`, `pending`, `private`, `future`
- `date` - Post date (ISO 8601)
- `categories` - Comma-separated category names or slugs
- `tags` - Comma-separated tag names or slugs
- `format` - Post format: `standard`, `aside`, `chat`, `gallery`, `link`, `image`, `quote`, `status`, `video`, `audio`
- `slug` - URL slug
- `featured_image` - Featured image attachment ID
- `sticky` - Whether post is sticky (boolean)
- `password` - Password to protect post

**Response:**
```json
{
  "ID": 123,
  "site_ID": 252505333,
  "title": "New Post Title",
  "status": "draft",
  "date": "2026-02-10T09:50:35+00:00"
}
```

#### Update Post

```bash
POST /wordpress/rest/v1.1/sites/{site}/posts/{post_id}
Content-Type: application/json

{
  "title": "Updated Title",
  "content": "<p>Updated content...</p>"
}
```

Uses the same parameters as Create Post.

#### Delete Post

```bash
POST /wordpress/rest/v1.1/sites/{site}/posts/{post_id}/delete
```

Moves post to trash. Returns the deleted post with `status: "trash"`.

### Pages

Pages use the same endpoints as posts with `type=page`:

#### List Pages

```bash
GET /wordpress/rest/v1.1/sites/{site}/posts?type=page
```

#### Create Page

```bash
POST /wordpress/rest/v1.1/sites/{site}/posts/new?type=page
Content-Type: application/json

{
  "title": "About Us",
  "content": "<p>About page content...</p>",
  "status": "publish"
}
```

#### Get Page Dropdown List

```bash
GET /wordpress/rest/v1.1/sites/{site}/dropdown-pages/
```

Returns a simplified list of pages for dropdowns/menus.

#### Get Page Templates

```bash
GET /wordpress/rest/v1.1/sites/{site}/page-templates
```

Returns available page templates for the site's theme.

### Post Likes

#### Get Post Likes

```bash
GET /wordpress/rest/v1.1/sites/{site}/posts/{post_id}/likes
```

**Response:**
```json
{
  "found": 99,
  "i_like": false,
  "can_like": true,
  "site_ID": 3584907,
  "post_ID": 83587,
  "likes": [...]
}
```

#### Like Post

```bash
POST /wordpress/rest/v1.1/sites/{site}/posts/{post_id}/likes/new
```

#### Unlike Post

```bash
POST /wordpress/rest/v1.1/sites/{site}/posts/{post_id}/likes/mine/delete
```

### Post Reblogs

#### Check Reblog Status

```bash
GET /wordpress/rest/v1.1/sites/{site}/posts/{post_id}/reblogs/mine
```

**Response:**
```json
{
  "can_reblog": true,
  "can_user_reblog": true,
  "is_reblogged": false
}
```

### Post Types

#### List Post Types

```bash
GET /wordpress/rest/v1.1/sites/{site}/post-types
```

**Response:**
```json
{
  "found": 3,
  "post_types": {
    "post": {
      "name": "post",
      "label": "Posts",
      "labels": {...}
    },
    "page": {
      "name": "page",
      "label": "Pages",
      "labels": {...}
    }
  }
}
```

### Post Counts

#### Get Post Counts

```bash
GET /wordpress/rest/v1.1/sites/{site}/post-counts/{post_type}
```

**Example:** `/sites/{site}/post-counts/post` or `/sites/{site}/post-counts/page`

**Response:**
```json
{
  "counts": {
    "all": {"count": 150},
    "publish": {"count": 120},
    "draft": {"count": 25},
    "trash": {"count": 5}
  }
}
```

### Users

#### List Site Users

```bash
GET /wordpress/rest/v1.1/sites/{site}/users
```

**Response:**
```json
{
  "found": 3,
  "users": [
    {
      "ID": 277004271,
      "login": "username",
      "name": "John Doe",
      "email": "john@example.com",
      "roles": ["administrator"]
    }
  ]
}
```

### User Settings

#### Get User Settings

```bash
GET /wordpress/rest/v1.1/me/settings
```

**Response:**
```json
{
  "enable_translator": true,
  "surprise_me": false,
  "holidaysnow": false,
  "user_login": "username"
}
```

#### Update User Settings

```bash
POST /wordpress/rest/v1.1/me/settings/
Content-Type: application/json

{
  "enable_translator": false
}
```

### User Likes

#### Get User's Liked Posts

```bash
GET /wordpress/rest/v1.1/me/likes
```

**Response:**
```json
{
  "found": 10,
  "likes": [
    {
      "ID": 83587,
      "site_ID": 3584907,
      "title": "Liked Post Title"
    }
  ]
}
```

### Embeds

#### Get Site Embeds

```bash
GET /wordpress/rest/v1.1/sites/{site}/embeds
```

Returns available embed handlers for the site.

### Shortcodes

#### Get Available Shortcodes

```bash
GET /wordpress/rest/v1.1/sites/{site}/shortcodes
```

Returns shortcodes available on the site.

## Pagination

WordPress.com uses cursor-based pagination with `page_handle`:

```python
import os
import requests

headers = {
    'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'
}

# Initial request
response = requests.get(
    'https://gateway.maton.ai/wordpress/rest/v1.1/sites/{site}/posts',
    headers=headers,
    params={'number': 20}
)
result = response.json()
all_posts = result['posts']

# Continue with page_handle
while result.get('meta', {}).get('next_page'):
    response = requests.get(
        'https://gateway.maton.ai/wordpress/rest/v1.1/sites/{site}/posts',
        headers=headers,
        params={'number': 20, 'page_handle': result['meta']['next_page']}
    )
    result = response.json()
    all_posts.extend(result['posts'])

print(f"Total posts: {len(all_posts)}")
```

Alternatively, use `offset` for simple pagination:

```bash
GET /wordpress/rest/v1.1/sites/{site}/posts?number=20&offset=20
```

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/wordpress/rest/v1.1/sites/{site}/posts?number=10',
  {
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`
    }
  }
);
const data = await response.json();
console.log(`Found ${data.found} posts`);
```

### Python

```python
import os
import requests

response = requests.get(
    'https://gateway.maton.ai/wordpress/rest/v1.1/sites/{site}/posts',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'},
    params={'number': 10, 'status': 'publish'}
)
data = response.json()
print(f"Found {data['found']} posts")
```

### Python (Create Post)

```python
import os
import requests

response = requests.post(
    'https://gateway.maton.ai/wordpress/rest/v1.1/sites/{site}/posts/new',
    headers={
        'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
        'Content-Type': 'application/json'
    },
    json={
        'title': 'My New Post',
        'content': '<p>Hello World!</p>',
        'status': 'draft',
        'categories': 'news',
        'tags': 'hello, first-post'
    }
)
post = response.json()
print(f"Created post ID: {post['ID']}")
```

## Notes

- WordPress.com API uses REST v1.1 (not v2)
- Site identifiers can be numeric IDs or domain names
- POST requests to `/posts/{id}` update the post (not PUT/PATCH)
- DELETE uses POST to `/posts/{id}/delete` (not HTTP DELETE)
- Categories and tags are created automatically when referenced in posts
- Date/time values are in ISO 8601 format
- All content is HTML-formatted
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing WordPress connection or bad request |
| 401 | Invalid or missing Maton API key |
| 403 | Insufficient permissions or OAuth scope |
| 404 | Site or resource not found |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from WordPress.com API |

Error responses include details:
```json
{
  "error": "unauthorized",
  "message": "User cannot view users for specified site"
}
```

### Troubleshooting: API Key Issues

1. Check that the `MATON_API_KEY` environment variable is set:

```bash
echo $MATON_API_KEY
```

2. Verify the API key is valid by listing connections:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Troubleshooting: Invalid App Name

1. Ensure your URL path starts with `wordpress`. For example:

- Correct: `https://gateway.maton.ai/wordpress/rest/v1.1/sites/{site_id}/posts`
- Incorrect: `https://gateway.maton.ai/rest/v1.1/sites/{site_id}/posts`

## Resources

- [WordPress.com REST API Overview](https://developer.wordpress.com/docs/api/)
- [Getting Started Guide](https://developer.wordpress.com/docs/api/getting-started/)
- [API Reference](https://developer.wordpress.com/docs/api/rest-api-reference/)
- [OAuth Authentication](https://developer.wordpress.com/docs/oauth2/)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
