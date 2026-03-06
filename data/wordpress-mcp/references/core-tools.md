# Core WordPress Tools Reference

## Posts & Pages

### wp_get_posts
List posts. Returns: ID, title, status, excerpt, link (no full content).
- `post_type` (string): "post", "page", etc. Default: "post"
- `post_status` (string): "publish", "draft", "any"
- `posts_per_page` (int): Number of results. Default: 10
- `orderby` (string): "date", "title", "modified"
- `order` (string): "DESC" or "ASC"
- `category` (string): Category slug filter
- `tag` (string): Tag slug filter
- `search` (string): Search keyword

### wp_get_post
Get a single post by ID. Returns full content.
- `id` (int, required): Post ID

### wp_get_post_snapshot
Get complete post data in ONE call: all fields, all meta, all terms/taxonomies.
- `id` (int, required): Post ID
- Best for getting complete post context efficiently.

### wp_create_post
Create a post or page.
- `post_title` (string, required)
- `post_content` (string): Markdown accepted
- `post_status` (string): "draft" (default), "publish", "private"
- `post_type` (string): "post", "page"
- `post_excerpt` (string)
- `post_author` (int): User ID
- `meta` (object): Custom fields `{"key": "value"}`
- `terms` (object): Taxonomies `{"category": [1,2], "post_tag": [3]}`

### wp_update_post
Update post fields and/or meta.
- `id` (int, required): Post ID
- `fields` (object): Any post fields (`post_title`, `post_content`, `post_status`, etc.)
- `meta` (object): Custom fields to update

### wp_delete_post
Delete or trash a post.
- `id` (int, required)
- `force` (bool): Skip trash, permanent delete

### wp_alter_post
Search-and-replace inside a post field without re-uploading entire content.
- `id` (int, required)
- `field` (string): Field to alter (default: "post_content")
- `search` (string, required): Text to find
- `replace` (string, required): Replacement text

### wp_count_posts
Count posts by status.
- `post_type` (string): Default "post"

## Media

### wp_get_media
List media items.
- `posts_per_page` (int)
- `mime_type` (string): Filter e.g. "image/jpeg"
- `search` (string)

### wp_upload_media
Upload media from URL.
- `url` (string, required): Image/file URL
- `title` (string)
- `alt_text` (string)
- `caption` (string)

### wp_upload_request
Upload a local file via temporary upload endpoint.
- Returns an upload URL and instructions.

### wp_update_media
Update attachment metadata.
- `id` (int, required)
- `fields` (object): `alt_text`, `title`, `caption`, `description`

### wp_delete_media
Delete an attachment.
- `id` (int, required)
- `force` (bool): Permanent delete

### wp_set_featured_image
Set or remove featured image.
- `post_id` (int, required)
- `media_id` (int): Set to 0 to remove

## Post Meta

### wp_get_post_meta
- `id` (int, required): Post ID
- `key` (string): Specific meta key, or omit for all

### wp_update_post_meta
- `id` (int, required)
- `meta` (object): `{"key": "value"}` — update multiple fields at once

### wp_delete_post_meta
- `id` (int, required)
- `key` (string, required)
- `value` (string): Specific value to remove (omit to remove all)

## Taxonomies & Terms

### wp_get_taxonomies
- `post_type` (string): List taxonomies for a post type

### wp_get_terms
- `taxonomy` (string, required): e.g. "category", "post_tag"
- `search` (string)
- `hide_empty` (bool)

### wp_create_term
- `taxonomy` (string, required)
- `name` (string, required)
- `slug` (string)
- `parent` (int)

### wp_get_post_terms
- `id` (int, required): Post ID
- `taxonomy` (string, required)

### wp_add_post_terms
- `id` (int, required)
- `taxonomy` (string, required)
- `terms` (array): Term IDs
- `append` (bool): true = add to existing, false = replace

## Users

### wp_get_users
- `role` (string): Filter by role
- `number` (int): Limit

### wp_create_user
- `user_login` (string, required)
- `user_email` (string, required)
- `user_pass` (string): Random if omitted
- `role` (string)

### wp_update_user
- `id` (int, required)
- `fields` (object): `user_email`, `display_name`, etc.

## Options

### wp_get_option
- `key` (string, required)

### wp_update_option
- `key` (string, required)
- `value` (mixed, required)

## Plugins

### wp_list_plugins
No parameters. Returns: `[{Name, Version}]`
