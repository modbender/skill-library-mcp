# Comment Management

Reading, responding to, and moderating Ghost comments.

## Listing Comments

### All Comments

```bash
curl "${GHOST_URL}/ghost/api/admin/comments/?include=post&limit=15" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

### Pending/Unanswered Comments

```bash
curl "${GHOST_URL}/ghost/api/admin/comments/?filter=status:pending" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

### Comments by Post

```bash
curl "${GHOST_URL}/ghost/api/admin/comments/?filter=post_id:'${POST_ID}'" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

### Recent Comments

```bash
curl "${GHOST_URL}/ghost/api/admin/comments/?order=created_at%20desc&limit=10" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

## Comment Structure

Comments in the response include:

```json
{
  "comments": [{
    "id": "comment_id_here",
    "post_id": "post_id_here",
    "member_id": "member_id_here",
    "html": "<p>Comment text</p>",
    "status": "published",
    "created_at": "2026-01-31T12:00:00.000Z",
    "member": {
      "name": "Commenter Name",
      "email": "email@example.com"
    },
    "post": {
      "title": "Post Title",
      "slug": "post-slug"
    }
  }]
}
```

## Responding to Comments

### Reply to Comment

```bash
curl -X POST "${GHOST_URL}/ghost/api/admin/comments/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "comments": [{
      "post_id": "post_id_here",
      "parent_id": "parent_comment_id",
      "html": "<p>Your reply here</p>",
      "status": "published"
    }]
  }'
```

**Important:** Include `parent_id` to thread the reply under the original comment.

### As Site Owner/Admin

To reply as the site owner (you), make sure you're authenticated with an admin API key. The comment will show your name/avatar automatically.

### As Different Author

If your site has multiple authors and you want to reply as "Navi":

```bash
curl -X POST "${GHOST_URL}/ghost/api/admin/comments/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "comments": [{
      "post_id": "post_id_here",
      "parent_id": "parent_comment_id",
      "html": "<p>Reply as Navi</p>",
      "status": "published",
      "member_id": "navi_member_id"
    }]
  }'
```

**Note:** You need Navi to be a member account. For staff replies, it uses the authenticated admin user.

## Comment Moderation

### Approve Comment

```bash
curl -X PUT "${GHOST_URL}/ghost/api/admin/comments/${COMMENT_ID}/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "comments": [{
      "status": "published"
    }]
  }'
```

### Hide/Delete Comment

```bash
curl -X DELETE "${GHOST_URL}/ghost/api/admin/comments/${COMMENT_ID}/" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

### Mark as Spam

```bash
curl -X PUT "${GHOST_URL}/ghost/api/admin/comments/${COMMENT_ID}/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "comments": [{
      "status": "spam"
    }]
  }'
```

## Checking for New Comments

### Comments Since Last Check

```bash
# Store last check time
LAST_CHECK="2026-01-31T10:00:00.000Z"

curl "${GHOST_URL}/ghost/api/admin/comments/?filter=created_at:>'${LAST_CHECK}'" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

### Unanswered Comments

Comments without replies (no child comments):

```bash
# This requires checking each comment's replies
# Get all comments, filter for those with no replies

curl "${GHOST_URL}/ghost/api/admin/comments/?limit=all" \
  -H "Authorization: Ghost ${GHOST_KEY}" | \
  jq '.comments[] | select(.replies | length == 0)'
```

## Common Workflows

### Daily Comment Check

**User asks:** "Are there any comments I need to respond to?"

1. Fetch recent comments (last 24-48 hours)
2. Filter for:
   - Status: published (not spam/deleted)
   - No replies from site team
3. Group by post title
4. Present list: "Post Title - Commenter Name - Comment preview"

### Responding to Specific Comment

**User asks:** "Respond to comment #123 with [response]"

1. GET comment #123 to confirm post_id
2. POST reply with parent_id set to #123
3. Confirm reply posted successfully

### Bulk Moderation

**User asks:** "Approve all pending comments"

1. Fetch all comments with status:pending
2. For each comment:
   - Review content (optional AI check for spam)
   - PUT status:published
3. Report count approved

## Formatting Responses

Use HTML in comment replies:

**Simple text:**
```html
<p>Thanks for the comment!</p>
```

**Multi-paragraph:**
```html
<p>Great question!</p>
<p>Here's the answer...</p>
```

**With links:**
```html
<p>Check out <a href="https://example.com">this resource</a>.</p>
```

**Code snippets:**
```html
<p>Try this:</p>
<pre><code>example code here</code></pre>
```

## Notification Integration

Ghost sends email notifications for comments automatically. No API action needed.

If you want custom notifications:
- Use webhooks (comment.added, comment.published)
- Set up in Ghost Admin → Integrations → Webhooks

## Best Practices

- **Reply promptly** - Aim for <24h response time
- **Be personable** - Use commenter's name if available
- **Thread replies** - Always set parent_id for context
- **Moderate proactively** - Check for spam/inappropriate content
- **Encourage discussion** - Ask follow-up questions when appropriate
- **Link to related posts** - Direct commenters to relevant content

## Comment Settings

Comment system settings are managed in Ghost Admin:

- **Enable/disable comments** - Per post or site-wide
- **Member-only comments** - Require login to comment
- **Comment moderation** - Auto-approve or require approval

API doesn't directly control these settings; manage in Ghost Admin dashboard.
