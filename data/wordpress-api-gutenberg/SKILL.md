---
name: wordpress-api-gutenberg
description: Create, edit, and publish WordPress posts via REST API with full Gutenberg block support. Use when Codex needs to automate WordPress content publishing, generate articles programmatically, or manage posts through API calls. Includes authentication methods (JWT, Application Passwords), Gutenberg block serialization, featured images, categories, tags, and draft/publish workflows.
---

# WordPress API with Gutenberg

## Overview

This skill provides comprehensive guidance for interacting with WordPress REST API to create and manage posts using Gutenberg block editor format. It covers authentication, block serialization, media upload, and publishing workflows.

## Quick Start

Before using the API, ensure you have:

1. **WordPress site** with REST API enabled (default)
2. **Authentication credentials**:
   - Application Password (WordPress 5.6+): Generate at `/wp-admin/admin.php?page=application-passwords`
   - JWT Authentication plugin installed (alternative)
   - Username/password for Basic Auth (not recommended for production)

3. **Base URL**: `https://your-site.com/wp-json/wp/v2`

## Authentication

### Application Password (Recommended)

```bash
# Set environment variables
export WP_URL="https://your-site.com"
export WP_USERNAME="admin"
export WP_APPLICATION_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx"
```

```python
import requests
import os

wp_url = os.environ.get('WP_URL')
username = os.environ.get('WP_USERNAME')
password = os.environ.get('WP_APPLICATION_PASSWORD')

auth = (username, password)
```

### JWT Authentication

If using JWT plugin, obtain token first:

```python
import requests

wp_url = "https://your-site.com"
username = "admin"
password = "password"

# Get token
resp = requests.post(f"{wp_url}/wp-json/jwt-auth/v1/token", 
                     json={"username": username, "password": password})
token = resp.json()['token']

headers = {"Authorization": f"Bearer {token}"}
```

## Creating Posts with Gutenberg Blocks

WordPress REST API expects posts in Gutenberg's serialized block format. The content field should contain block comments and HTML.

### Basic Block Structure

```python
def create_gutenberg_post(title, content_blocks):
    """
    Create a post with Gutenberg blocks.
    
    Args:
        title: Post title
        content_blocks: List of block dictionaries with 'blockName' and 'attrs'
    
    Returns:
        JSON data for POST request
    """
    # Serialize blocks to Gutenberg format
    block_html = []
    for block in content_blocks:
        block_name = block.get('blockName', 'core/paragraph')
        attrs = block.get('attrs', {})
        inner_html = block.get('innerHTML', '')
        
        # Create block comment
        attrs_json = json.dumps(attrs) if attrs else ''
        block_comment = f'<!-- wp:{block_name} {attrs_json} -->'
        block_html.append(f'{block_comment}{inner_html}<!-- /wp:{block_name} -->')
    
    content = '\n\n'.join(block_html)
    
    return {
        "title": title,
        "content": content,
        "status": "draft",  # or "publish"
        "format": "standard"
    }
```

### Common Block Examples

See [references/common_blocks.md](references/common_blocks.md) for detailed examples of:
- Paragraph blocks with formatting
- Heading blocks (h2-h4)
- Image blocks with captions and alignment
- List blocks (ordered/unordered)
- Quote blocks
- Code blocks
- Custom HTML blocks
- Columns and layout blocks

## Complete Workflow

### Step 1: Prepare Authentication
Set up credentials as environment variables or in a configuration file.

### Step 2: Create Post Data
Define title, content blocks, categories, tags, featured image.

### Step 3: Upload Media (if needed)
```python
def upload_image(image_path, post_id=None):
    """Upload image to WordPress media library."""
    with open(image_path, 'rb') as f:
        files = {'file': f}
        data = {}
        if post_id:
            data['post'] = post_id
        
        response = requests.post(f"{wp_url}/wp-json/wp/v2/media",
                                 files=files, data=data, auth=auth)
        return response.json()
```

### Step 4: Create Post
```python
def create_post(post_data):
    """Create new WordPress post."""
    response = requests.post(f"{wp_url}/wp-json/wp/v2/posts",
                             json=post_data, auth=auth)
    return response.json()
```

### Step 5: Update Status
Change from draft to publish:
```python
def publish_post(post_id):
    """Publish a draft post."""
    response = requests.post(f"{wp_url}/wp-json/wp/v2/posts/{post_id}",
                             json={"status": "publish"}, auth=auth)
    return response.json()
```

## Advanced Features

### Categories and Tags
```python
# Get or create category
def ensure_category(name, slug=None):
    categories = requests.get(f"{wp_url}/wp-json/wp/v2/categories",
                             params={"search": name}, auth=auth).json()
    if categories:
        return categories[0]['id']
    else:
        new_cat = requests.post(f"{wp_url}/wp-json/wp/v2/categories",
                               json={"name": name, "slug": slug or name.lower()},
                               auth=auth).json()
        return new_cat['id']
```

### Featured Image
```python
# Upload image first, then set as featured
image_data = upload_image("path/to/image.jpg")
post_data["featured_media"] = image_data['id']
```

### Custom Fields (ACF)
If using Advanced Custom Fields plugin:
```python
post_data["meta"] = {
    "your_field_name": "field_value"
}
```

## Error Handling

Always check responses:
```python
response = requests.post(...)
if response.status_code in [200, 201]:
    print("Success!")
else:
    print(f"Error {response.status_code}: {response.text}")
```

Common issues:
- 401: Authentication failed
- 403: User lacks permission
- 404: Endpoint not found (check WordPress version)
- 500: Server error (check PHP error logs)

## Scripts

The `scripts/` directory contains helper utilities:

- `wp_publish.py`: Complete publishing pipeline
- `block_generator.py`: Generate Gutenberg block HTML from markdown
- `media_uploader.py`: Batch upload images

## References

- [common_blocks.md](references/common_blocks.md): Detailed block examples
- [api_reference.md](references/api_reference.md): Complete WordPress REST API reference
- [troubleshooting.md](references/troubleshooting.md): Common issues and solutions

## Assets

- `templates/article_template.json`: JSON template for typical article structure
- `block_samples/`: Example block HTML for various content types

## Example Request

```bash
# Using curl with Application Password
curl -X POST https://your-site.com/wp-json/wp/v2/posts \
  -u "admin:xxxx xxxx xxxx xxxx xxxx xxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My New Post",
    "content": "<!-- wp:paragraph --><p>Hello World!</p><!-- /wp:paragraph -->",
    "status": "draft"
  }'
```
