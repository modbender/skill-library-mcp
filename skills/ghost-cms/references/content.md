# Content Management

Creating, publishing, scheduling, and managing Ghost posts and pages.

## Content Format: Lexical

**Ghost 5.0+ uses Lexical format** for all content creation and updates. Ghost's Lexical editor is built on Meta's Lexical framework (same tech powering Facebook/Instagram).

**Important:**
- Send content in `lexical` field (JSON string)
- Ghost stores it internally as mobiledoc (legacy format)
- When reading, use `?formats=html` to get rendered HTML
- HTML and mobiledoc are deprecated for write operations

## Creating Posts

### Basic Post Creation

```bash
curl -X POST "${GHOST_URL}/ghost/api/admin/posts/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "posts": [{
      "title": "Your Post Title",
      "lexical": "{\"root\":{\"children\":[{\"children\":[{\"detail\":0,\"format\":0,\"mode\":\"normal\",\"style\":\"\",\"text\":\"Your content here\",\"type\":\"extended-text\",\"version\":1}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"paragraph\",\"version\":1}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
      "status": "draft"
    }]
  }'
```

### Lexical Structure

**Basic paragraph:**
```json
{
  "root": {
    "children": [
      {
        "children": [
          {
            "detail": 0,
            "format": 0,
            "mode": "normal",
            "style": "",
            "text": "Your paragraph text here",
            "type": "extended-text",
            "version": 1
          }
        ],
        "direction": "ltr",
        "format": "",
        "indent": 0,
        "type": "paragraph",
        "version": 1
      }
    ],
    "direction": "ltr",
    "format": "",
    "indent": 0,
    "type": "root",
    "version": 1
  }
}
```

**Heading (H2):**
```json
{
  "children": [
    {
      "detail": 0,
      "format": 1,
      "mode": "normal",
      "style": "",
      "text": "Heading Text",
      "type": "extended-text",
      "version": 1
    }
  ],
  "direction": "ltr",
  "format": "",
  "indent": 0,
  "type": "heading",
  "version": 1,
  "tag": "h2"
}
```

**Multiple paragraphs:**
```json
{
  "root": {
    "children": [
      {
        "children": [
          {
            "detail": 0,
            "format": 0,
            "mode": "normal",
            "style": "",
            "text": "First paragraph",
            "type": "extended-text",
            "version": 1
          }
        ],
        "direction": "ltr",
        "format": "",
        "indent": 0,
        "type": "paragraph",
        "version": 1
      },
      {
        "children": [
          {
            "detail": 0,
            "format": 0,
            "mode": "normal",
            "style": "",
            "text": "Second paragraph",
            "type": "extended-text",
            "version": 1
          }
        ],
        "direction": "ltr",
        "format": "",
        "indent": 0,
        "type": "paragraph",
        "version": 1
      }
    ],
    "direction": "ltr",
    "format": "",
    "indent": 0,
    "type": "root",
    "version": 1
  }
}
```

**Text formatting:**
- `"format": 0` - Normal text
- `"format": 1` - Bold
- `"format": 2` - Italic
- `"format": 3` - Bold + Italic

**Heading tags:**
- `"tag": "h1"` - H1 heading
- `"tag": "h2"` - H2 heading  
- `"tag": "h3"` - H3 heading
- `"tag": "h4"` - H4 heading

### Post with Full Metadata

```bash
curl -X POST "${GHOST_URL}/ghost/api/admin/posts/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "posts": [{
      "title": "Complete Post Example",
      "lexical": "{\"root\":{\"children\":[{\"children\":[{\"detail\":0,\"format\":0,\"mode\":\"normal\",\"style\":\"\",\"text\":\"Full post content with formatting\",\"type\":\"extended-text\",\"version\":1}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"paragraph\",\"version\":1}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
      "status": "draft",
      "tags": [
        {"name": "Technology"},
        {"name": "Tutorial"}
      ],
      "authors": [
        {"email": "navi@chrisgiddings.net"}
      ],
      "feature_image": "https://example.com/image.jpg",
      "featured": false,
      "meta_title": "SEO Title",
      "meta_description": "SEO description",
      "og_title": "Social Media Title",
      "og_description": "Social media description"
    }]
  }'
```

## Publishing & Scheduling

### Publish Immediately

```bash
curl -X PUT "${GHOST_URL}/ghost/api/admin/posts/${POST_ID}/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "posts": [{
      "status": "published",
      "published_at": null
    }]
  }'
```

`published_at: null` means "publish now"

### Schedule for Future

```bash
curl -X PUT "${GHOST_URL}/ghost/api/admin/posts/${POST_ID}/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "posts": [{
      "status": "scheduled",
      "published_at": "2026-02-10T09:00:00.000Z"
    }]
  }'
```

**Date format:** ISO 8601 with timezone (UTC)

## Updating Posts

### Update Content (Lexical)

```bash
curl -X PUT "${GHOST_URL}/ghost/api/admin/posts/${POST_ID}/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "posts": [{
      "lexical": "{\"root\":{\"children\":[{\"children\":[{\"detail\":0,\"format\":0,\"mode\":\"normal\",\"style\":\"\",\"text\":\"Updated content\",\"type\":\"extended-text\",\"version\":1}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"paragraph\",\"version\":1}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
      "updated_at": "2026-01-31T12:00:00.000Z"
    }]
  }'
```

**Important:** Include `updated_at` from the original post to prevent conflicts.

### Update Tags

```bash
curl -X PUT "${GHOST_URL}/ghost/api/admin/posts/${POST_ID}/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "posts": [{
      "tags": [
        {"name": "New Tag"},
        {"name": "Another Tag"}
      ]
    }]
  }'
```

Tags are **replaced**, not appended. Include existing tags to keep them.

## Listing Posts

### Get All Posts

```bash
curl "${GHOST_URL}/ghost/api/admin/posts/?limit=15&include=authors,tags" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

### Get Post with HTML Output

```bash
curl "${GHOST_URL}/ghost/api/admin/posts/${POST_ID}/?formats=html" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

Returns rendered HTML in the `html` field for display purposes.

### Filter by Status

**Drafts only:**
```bash
curl "${GHOST_URL}/ghost/api/admin/posts/?filter=status:draft" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

**Published only:**
```bash
curl "${GHOST_URL}/ghost/api/admin/posts/?filter=status:published" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

**Scheduled only:**
```bash
curl "${GHOST_URL}/ghost/api/admin/posts/?filter=status:scheduled" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

### Search Posts

```bash
curl "${GHOST_URL}/ghost/api/admin/posts/?filter=title:~'keyword'" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

The `~` operator means "contains"

### Recent Posts

```bash
curl "${GHOST_URL}/ghost/api/admin/posts/?order=published_at%20desc&limit=5" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

## Member-Exclusive Content

### Set Visibility Tier

```bash
curl -X POST "${GHOST_URL}/ghost/api/admin/posts/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "posts": [{
      "title": "Premium Content",
      "lexical": "{\"root\":{\"children\":[{\"children\":[{\"detail\":0,\"format\":0,\"mode\":\"normal\",\"style\":\"\",\"text\":\"Exclusive content\",\"type\":\"extended-text\",\"version\":1}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"paragraph\",\"version\":1}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
      "visibility": "paid",
      "tiers": [
        {"id": "tier_id_here"}
      ]
    }]
  }'
```

**Visibility options:**
- `public` - Everyone (default)
- `members` - All logged-in members
- `paid` - Paid members only
- `tiers` - Specific tiers (requires `tiers` array)

### Find Tier IDs

```bash
curl "${GHOST_URL}/ghost/api/admin/tiers/" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

## Tags

### Create New Tag

```bash
curl -X POST "${GHOST_URL}/ghost/api/admin/tags/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "tags": [{
      "name": "New Tag",
      "slug": "new-tag",
      "description": "Tag description"
    }]
  }'
```

### List All Tags

```bash
curl "${GHOST_URL}/ghost/api/admin/tags/?limit=all" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

## Pages vs Posts

**Posts** appear in RSS feed, blog index, are dated.
**Pages** are standalone (About, Contact, etc.)

Create pages the same way as posts, but use `/pages/` endpoint:

```bash
curl -X POST "${GHOST_URL}/ghost/api/admin/pages/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "pages": [{
      "title": "About Page",
      "lexical": "{\"root\":{\"children\":[{\"children\":[{\"detail\":0,\"format\":0,\"mode\":\"normal\",\"style\":\"\",\"text\":\"About content\",\"type\":\"extended-text\",\"version\":1}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"paragraph\",\"version\":1}],\"direction\":\"ltr\",\"format\":\"\",\"indent\":0,\"type\":\"root\",\"version\":1}}",
      "status": "published"
    }]
  }'
```

## Helper: Building Lexical from Text

**Simple helper to convert plain text paragraphs to Lexical:**

```javascript
function textToLexical(text) {
  const paragraphs = text.split('\n\n').filter(p => p.trim());
  
  const children = paragraphs.map(para => ({
    children: [{
      detail: 0,
      format: 0,
      mode: "normal",
      style: "",
      text: para.trim(),
      type: "extended-text",
      version: 1
    }],
    direction: "ltr",
    format: "",
    indent: 0,
    type: "paragraph",
    version: 1
  }));
  
  return JSON.stringify({
    root: {
      children,
      direction: "ltr",
      format: "",
      indent: 0,
      type: "root",
      version: 1
    }
  });
}

// Usage:
const lexicalContent = textToLexical("First paragraph.\n\nSecond paragraph.");
```

## Common Workflows

### Draft from Notion → Ghost

1. Content drafted collaboratively in Notion
2. Export Notion page as HTML or Markdown
3. Convert to Lexical format
4. POST to Ghost as draft
5. Review in Ghost admin
6. Publish or schedule

### Weekly Series (Automated)

1. Generate content based on weekly topics/discussions
2. Convert to Lexical format
3. Set author to "Navi" (find author by email)
4. Apply consistent tags (e.g., "Weekly Series")
5. Schedule for consistent day/time (e.g., Monday 9am)
6. POST with `status: scheduled`

### Bulk Tag Update

1. List posts with filter
2. For each post, GET current tags
3. Append new tag to existing list
4. PUT updated tags back

## Best Practices

- **Use Lexical format** for all create/update operations (Ghost 5.0+)
- **Always include `updated_at`** when updating posts (prevents conflicts)
- **Use slugs for URLs** - Auto-generated from title, but can override
- **Feature images** - Use HTTPS URLs, ideally on your domain or CDN
- **SEO metadata** - Set `meta_title`, `meta_description`, `og_title`, `og_description`
- **Tags are lowercase** - Ghost auto-lowercases tag names
- **Test in draft first** - Create as draft, review in admin, then publish
- **Read with `?formats=html`** - Get rendered HTML for display/reading
- **Write with `lexical`** - Ghost converts internally to mobiledoc
