# Postavel MCP Tools Reference

Complete reference for all MCP tools available in Postavel.

## Connection Information

**MCP Server URL:** `https://postavel.com/mcp/postavel`

**Authentication:** OAuth 2.0 - User authenticates with their Postavel credentials

## Available Resources

### 1. list_workspaces

Lists all workspaces the user has access to.

**Use when:** User asks to see their workspaces or wants to switch contexts

**Example prompts:**
- "Show me my workspaces"
- "List all workspaces I have access to"

---

### 2. list_clients

Lists all clients within a workspace.

**Parameters:**
- `workspace_id` (required): The workspace to list clients from

**Use when:** User wants to see clients in a specific workspace

**Example prompts:**
- "List clients in workspace 'My Agency'"
- "What clients do I have?"

---

### 3. list_brands

Lists all brands for a specific client.

**Parameters:**
- `client_id` (required): The client to list brands for

**Use when:** User wants to see available brands for posting

**Example prompts:**
- "Show brands for client 'Acme Corp'"
- "What brands can I manage?"

---

### 4. list_social_accounts

Lists connected social media accounts for a brand.

**Parameters:**
- `brand_id` (required): The brand to check accounts for

**Use when:** User wants to see which platforms are connected

**Example prompts:**
- "What social accounts are connected for brand 'Coffee Shop'?"
- "Show me available platforms"

**Returns:** List of platforms (facebook, instagram, linkedin) with connection status

---

### 5. create_post

Creates a new social media post.

**Parameters:**
- `brand_id` (required): The brand to post for
- `content` (required): Post text/caption
- `platforms` (required): Array of platforms ['facebook', 'instagram', 'linkedin']
- `status` (optional): 'draft', 'scheduled', or 'published' (default: 'draft')
- `scheduled_at` (optional): ISO 8601 datetime (required if status='scheduled')
- `media_urls` (optional): Array of external image/video URLs
- `auto_approve` (optional): boolean - Immediately approve (admin/owner only)

**Use when:** User wants to create a social media post

**Example prompts:**
- "Create a Facebook post saying 'Hello world'"
- "Draft an Instagram post about our new product"
- "Create a post for Facebook and LinkedIn about summer sale"

**Important:** 
- One post can target multiple platforms
- Posts require approval before publishing (unless auto_approve=true and user has permissions)

---

### 6. list_posts

Lists posts for a brand with optional filtering.

**Parameters:**
- `brand_id` (required): The brand to list posts for
- `status` (optional): Filter by status ('draft', 'pending', 'scheduled', 'published', 'failed')
- `limit` (optional): Maximum number of posts to return

**Use when:** User wants to see existing posts or check status

**Example prompts:**
- "Show me posts for brand 'Tech Startup'"
- "What posts are scheduled for this week?"
- "List pending posts"

---

### 7. approve_post

Approves a pending post for publishing.

**Parameters:**
- `post_id` (required): The post to approve

**Use when:** User wants to approve a post that was created by a member

**Example prompts:**
- "Approve post ID 123"
- "Approve all pending posts for brand 'Coffee Shop'"

**Permissions:** Only workspace Admins and Owners can approve posts

---

### 8. reject_post

Rejects a pending post with optional feedback.

**Parameters:**
- `post_id` (required): The post to reject
- `feedback` (optional): Reason for rejection

**Use when:** Admin/Owner wants to reject a post that needs changes

---

### 9. get_post

Gets detailed information about a specific post.

**Parameters:**
- `post_id` (required): The post to retrieve

**Use when:** User wants details about a specific post

**Example prompts:**
- "What's the status of post 123?"
- "Show me details for the post about summer sale"

---

### 10. update_post

Updates an existing post (only if not yet published).

**Parameters:**
- `post_id` (required): The post to update
- `content` (optional): New post text
- `scheduled_at` (optional): New schedule time
- `platforms` (optional): Update target platforms

**Use when:** User wants to edit a draft or scheduled post

**Note:** Editing an approved post resets it to pending status

---

### 11. delete_post

Deletes a post (only draft or scheduled posts).

**Parameters:**
- `post_id` (required): The post to delete

**Use when:** User wants to remove a post

---

## Platform-Specific Notes

### Facebook
- Can post to pages user administers
- Supports images, videos, and links
- Posts can include call-to-action buttons

### Instagram
- Requires Business or Creator account
- Images: Recommended 1080x1080 (square) or 1080x1350 (portrait)
- Videos: MP4 format, 3-60 seconds for Reels
- Stories not supported via API

### LinkedIn
- Posts to organizations (company pages) user administers
- Professional tone recommended
- Supports images and documents (PDFs)
- Video support limited

## Error Handling

Common errors and their meanings:

**"Organization selection required"**
- LinkedIn requires selecting a company page
- User needs to go to Brand Settings > Social Accounts > LinkedIn

**"No Company Pages found"**
- User is not an admin of any LinkedIn company pages
- They need to be added as admin on LinkedIn

**"Auto-approve not allowed"**
- User is a Member (not Admin/Owner)
- Post is created but remains pending

**"Platform not connected"**
- The social account is not connected for that brand
- User needs to connect the platform first

## Best Practices

1. **Always confirm the brand** before creating posts if multiple brands exist
2. **Check post status** after creation to confirm it was created correctly
3. **Verify permissions** - Members cannot approve their own posts
4. **Use ISO 8601 format** for scheduling: `2024-12-25T09:00:00+01:00`
5. **One post, multiple platforms** - Create one post targeting multiple platforms instead of separate posts
