# WordPress REST API Reference

Complete reference for WordPress REST API endpoints relevant to content creation and management.

## Base URL

```
https://your-site.com/wp-json/wp/v2
```

## Authentication Methods

### Application Passwords (WordPress 5.6+)
- Generate at: `/wp-admin/admin.php?page=application-passwords`
- Format: `username:password` (password is space-separated words)
- Use with HTTP Basic Auth

### JWT Authentication
- Requires "JWT Authentication for WP REST API" plugin
- Get token: `POST /jwt-auth/v1/token`
- Use token: `Authorization: Bearer <token>`

### Cookie Authentication (for plugins/themes)
- Requires `wpnonce` and logged-in session
- Not recommended for external applications

## Core Endpoints

### Posts

**Create post**
```
POST /posts
```
Body:
```json
{
  "title": "Post Title",
  "content": "Gutenberg block HTML",
  "excerpt": "Short excerpt",
  "status": "draft|publish|pending|private",
  "format": "standard|aside|chat|gallery|link|image|quote|status|video|audio",
  "categories": [1, 2],
  "tags": [3, 4],
  "featured_media": 123,
  "meta": {"custom_field": "value"}
}
```

**Get post**
```
GET /posts/{id}
```

**Update post**
```
POST /posts/{id}
```
Supports partial updates (only include fields to change).

**Delete post**
```
DELETE /posts/{id}
```
Add `?force=true` to bypass trash.

**List posts**
```
GET /posts
```
Parameters:
- `page`, `per_page` (default 10, max 100)
- `search` - search in title and content
- `after`, `before` - date filtering
- `categories`, `tags` - filter by taxonomy
- `status` - filter by status

### Media

**Upload media**
```
POST /media
```
Content-Type: `multipart/form-data`
Form fields:
- `file` - binary file
- `title`, `caption`, `alt_text`, `description`
- `post` - attach to post ID

**Get media**
```
GET /media/{id}
```

**Update media**
```
POST /media/{id}
```

### Categories

**List categories**
```
GET /categories
```
Parameters: `search`, `page`, `per_page`

**Create category**
```
POST /categories
```
Body:
```json
{
  "name": "Category Name",
  "slug": "category-slug",
  "description": "Category description",
  "parent": 0
}
```

### Tags

Similar to categories, endpoint: `/tags`

### Users

**Get current user**
```
GET /users/me
```

**List users**
```
GET /users
```

## Gutenberg-Specific Considerations

### Block Validation
WordPress validates blocks on save. Invalid blocks may be stripped. Ensure:
- Block comments are properly closed
- Attribute JSON is valid
- Inner HTML matches block expectations

### Block Serialization
The REST API expects the same block format used in the database:
- Block comments with attributes
- No extra whitespace inside comments (though WordPress is tolerant)
- Nested blocks must be properly indented

### Raw vs Rendered Content
- `content.raw` - The stored block HTML
- `content.rendered` - HTML rendered for display
- Use `content.raw` when updating

## Custom Post Types

If using custom post types with REST API enabled:
```
GET /{namespace}/v1/{post_type}
```
Check `GET /` for available routes.

## Taxonomies

**Get registered taxonomies**
```
GET /taxonomies
```

**Get taxonomy terms**
```
GET /{taxonomy}  # e.g., /categories, /tags
```

## Meta Fields

**Register meta fields** via `register_meta` or ACF.

**Update post meta** via `meta` field in post update:
```json
{
  "meta": {
    "my_field": "value"
  }
}
```

## Error Responses

Common HTTP status codes:

- `200` - Success (GET)
- `201` - Created (POST)
- `400` - Bad request (invalid data)
- `401` - Authentication failed
- `403` - Permission denied
- `404` - Resource not found
- `500` - Server error

Error response format:
```json
{
  "code": "rest_invalid_param",
  "message": "Invalid parameter(s): status",
  "data": {
    "status": 400,
    "params": {
      "status": "status is not one of draft, publish, pending, private, future."
    }
  }
}
```

## Rate Limiting

WordPress doesn't enforce rate limiting by default. However:
- Hosting providers may impose limits
- Consider adding delays between requests (1-2 seconds)
- Batch operations when possible

## Performance Tips

1. **Use `_fields` parameter** to reduce response size:
   ```
   GET /posts?_fields=id,title,link
   ```

2. **Disable `_embed`** unless needed:
   ```
   GET /posts?_embed=false
   ```

3. **Cache responses** when appropriate

4. **Use pagination** for large collections

## WordPress.com vs Self-Hosted

- WordPress.com uses different authentication (OAuth2)
- API base: `https://public-api.wordpress.com/wp/v2/sites/{site_id}/`
- Requires application registration

## Testing with curl

```bash
# Create post with Application Password
curl -X POST https://site.com/wp-json/wp/v2/posts \
  -u "username:xxxx xxxx xxxx xxxx xxxx xxxx" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","content":"<!-- wp:paragraph --><p>Test</p><!-- /wp:paragraph -->","status":"draft"}'

# Get posts
curl -u "username:password" https://site.com/wp-json/wp/v2/posts

# Upload image
curl -X POST https://site.com/wp-json/wp/v2/media \
  -u "username:password" \
  -H "Content-Disposition: attachment; filename=test.jpg" \
  -H "Content-Type: image/jpeg" \
  --data-binary @test.jpg
```
