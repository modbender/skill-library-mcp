# Newsletters

Managing newsletter settings, email campaigns, and subscriber preferences.

## Newsletter Basics

Ghost newsletters are email versions of your blog posts. Each site can have multiple newsletters with different audiences and settings.

## Listing Newsletters

```bash
curl "${GHOST_URL}/ghost/api/admin/newsletters/" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

Returns:
```json
{
  "newsletters": [{
    "id": "newsletter_id",
    "uuid": "newsletter_uuid",
    "name": "Main Newsletter",
    "slug": "default-newsletter",
    "sender_email": "noreply@yourdomain.com",
    "sender_name": "Your Name",
    "sender_reply_to": "reply",
    "status": "active",
    "subscribe_on_signup": true,
    "header_image": null,
    "body_font_category": "sans_serif",
    "footer_content": "Unsubscribe | Manage preferences",
    "show_header_icon": true,
    "show_header_title": true,
    "title_font_category": "sans_serif",
    "show_feature_image": true,
    "count": {
      "members": 1234,
      "posts": 56
    }
  }]
}
```

## Creating a Newsletter

```bash
curl -X POST "${GHOST_URL}/ghost/api/admin/newsletters/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "newsletters": [{
      "name": "Weekly Digest",
      "slug": "weekly-digest",
      "sender_email": "weekly@yourdomain.com",
      "sender_name": "Navi",
      "sender_reply_to": "reply",
      "status": "active",
      "subscribe_on_signup": false,
      "body_font_category": "sans_serif",
      "title_font_category": "sans_serif"
    }]
  }'
```

## Updating Newsletter Settings

```bash
curl -X PUT "${GHOST_URL}/ghost/api/admin/newsletters/${NEWSLETTER_ID}/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "newsletters": [{
      "sender_name": "Updated Name",
      "footer_content": "Custom footer text"
    }]
  }'
```

## Sending Newsletters

Newsletters are sent automatically when you publish a post. To control newsletter sending:

### Publish Post Without Newsletter

```bash
curl -X POST "${GHOST_URL}/ghost/api/admin/posts/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "posts": [{
      "title": "Post Title",
      "html": "<p>Content</p>",
      "status": "published",
      "newsletter_id": null
    }]
  }'
```

`newsletter_id: null` prevents email send.

### Send to Specific Newsletter

```bash
curl -X POST "${GHOST_URL}/ghost/api/admin/posts/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "posts": [{
      "title": "Post Title",
      "html": "<p>Content</p>",
      "status": "published",
      "newsletter_id": "specific_newsletter_id"
    }]
  }'
```

### Schedule Newsletter Send

```bash
curl -X POST "${GHOST_URL}/ghost/api/admin/posts/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "posts": [{
      "title": "Scheduled Post",
      "html": "<p>Content</p>",
      "status": "scheduled",
      "published_at": "2026-02-10T09:00:00.000Z",
      "newsletter_id": "newsletter_id_here"
    }]
  }'
```

## Newsletter-Only Posts

Create posts that only go to email subscribers (not published on site):

```bash
curl -X POST "${GHOST_URL}/ghost/api/admin/posts/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "posts": [{
      "title": "Email-Only Update",
      "html": "<p>Exclusive newsletter content</p>",
      "status": "sent",
      "newsletter_id": "newsletter_id_here",
      "email_only": true
    }]
  }'
```

`email_only: true` sends the email but doesn't publish on the blog.

## Member Newsletter Preferences

### Check Member's Newsletter Subscriptions

```bash
curl "${GHOST_URL}/ghost/api/admin/members/${MEMBER_ID}/?include=newsletters" \
  -H "Authorization: Ghost ${GHOST_KEY}" | \
  jq '.members[0].newsletters'
```

### Subscribe Member to Newsletter

```bash
curl -X PUT "${GHOST_URL}/ghost/api/admin/members/${MEMBER_ID}/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "members": [{
      "newsletters": [
        {"id": "newsletter_1_id"},
        {"id": "newsletter_2_id"}
      ]
    }]
  }'
```

**Note:** This replaces all newsletter subscriptions. Include all newsletters you want them subscribed to.

### Unsubscribe Member

```bash
curl -X PUT "${GHOST_URL}/ghost/api/admin/members/${MEMBER_ID}/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "members": [{
      "newsletters": []
    }]
  }'
```

## Newsletter Analytics

### Subscriber Count per Newsletter

```bash
curl "${GHOST_URL}/ghost/api/admin/newsletters/${NEWSLETTER_ID}/" \
  -H "Authorization: Ghost ${GHOST_KEY}" | \
  jq '.newsletters[0].count.members'
```

### Posts Sent to Newsletter

```bash
curl "${GHOST_URL}/ghost/api/admin/newsletters/${NEWSLETTER_ID}/" \
  -H "Authorization: Ghost ${GHOST_KEY}" | \
  jq '.newsletters[0].count.posts'
```

### Email Performance (Pro)

If using Ghost Analytics Pro:

```bash
curl "${GHOST_URL}/ghost/api/admin/stats/email/${POST_ID}/" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

Returns:
- Delivered count
- Opened count
- Open rate
- Clicked count
- Click rate

## Newsletter Customization

### Email Design Settings

**Font categories:**
- `sans_serif` - Clean, modern
- `serif` - Traditional, elegant

**Layout options:**
- `show_header_icon` - Display site icon
- `show_header_title` - Display newsletter name
- `show_feature_image` - Show post featured image

```bash
curl -X PUT "${GHOST_URL}/ghost/api/admin/newsletters/${NEWSLETTER_ID}/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "newsletters": [{
      "body_font_category": "serif",
      "title_font_category": "serif",
      "show_feature_image": true,
      "show_header_icon": true
    }]
  }'
```

### Custom Footer

```bash
curl -X PUT "${GHOST_URL}/ghost/api/admin/newsletters/${NEWSLETTER_ID}/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "newsletters": [{
      "footer_content": "<p>Thanks for reading!</p><p>Reply to this email to get in touch.</p>"
    }]
  }'
```

Supports HTML.

## Multiple Newsletters Strategy

### Use Cases

**Primary newsletter** - All blog posts, default signup
**Weekly digest** - Curated content, manual send
**Premium newsletter** - Paid members only
**Product updates** - Feature announcements
**Series-specific** - Topic-based (e.g., "Tech Tutorials" vs "Book Reviews")

### Setup Example

1. **Main Newsletter** (default)
   - Auto-send on all published posts
   - `subscribe_on_signup: true`
   - Largest audience

2. **Weekly Digest**
   - Manual/scheduled
   - `subscribe_on_signup: false`
   - Opt-in only

3. **Premium Newsletter**
   - Member-tier filtered posts
   - `subscribe_on_signup: false`
   - Paid members auto-subscribed via automation

## Testing Newsletters

### Send Test Email

Ghost Admin UI provides "Send test email" functionality. API doesn't directly support test sends.

**Workaround:**
1. Create draft post with test content
2. Publish to yourself as a member
3. Review email
4. Delete post if needed

## Common Workflows

### Weekly Content Series

**Goal:** Send weekly digest every Monday at 9am

1. Write/curate content throughout week
2. Create post as draft
3. Schedule for Monday 9am with newsletter_id
4. Newsletter auto-sends on publish

```bash
curl -X POST "${GHOST_URL}/ghost/api/admin/posts/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "posts": [{
      "title": "Weekly Digest - Feb 10",
      "html": "<p>This week's highlights...</p>",
      "status": "scheduled",
      "published_at": "2026-02-10T14:00:00.000Z",
      "newsletter_id": "weekly_digest_id",
      "tags": [{"name": "Weekly Digest"}]
    }]
  }'
```

### Announcement Email

**Goal:** Send one-time announcement to all subscribers

1. Create newsletter-only post
2. Use `email_only: true`
3. Set status to `sent` or `scheduled`

```bash
curl -X POST "${GHOST_URL}/ghost/api/admin/posts/" \
  -H "Authorization: Ghost ${GHOST_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "posts": [{
      "title": "Important Announcement",
      "html": "<p>We have exciting news...</p>",
      "status": "sent",
      "newsletter_id": "main_newsletter_id",
      "email_only": true
    }]
  }'
```

### Newsletter Migration

**Goal:** Move subscribers from old newsletter to new one

```bash
# Get all members subscribed to old newsletter
OLD_NEWSLETTER_ID="old_id"
NEW_NEWSLETTER_ID="new_id"

MEMBERS=$(curl -s "${GHOST_URL}/ghost/api/admin/members/?limit=all&include=newsletters" \
  -H "Authorization: Ghost ${GHOST_KEY}" | \
  jq -r ".members[] | select(.newsletters[]?.id == \"$OLD_NEWSLETTER_ID\") | .id")

# Update each member
for MEMBER_ID in $MEMBERS; do
  # Get current newsletters
  CURRENT=$(curl -s "${GHOST_URL}/ghost/api/admin/members/${MEMBER_ID}/?include=newsletters" \
    -H "Authorization: Ghost ${GHOST_KEY}" | \
    jq -c '.members[0].newsletters')
  
  # Replace old with new
  UPDATED=$(echo $CURRENT | jq --arg old "$OLD_NEWSLETTER_ID" --arg new "$NEW_NEWSLETTER_ID" \
    'map(if .id == $old then .id = $new else . end)')
  
  # Update member
  curl -X PUT "${GHOST_URL}/ghost/api/admin/members/${MEMBER_ID}/" \
    -H "Authorization: Ghost ${GHOST_KEY}" \
    -H "Content-Type: application/json" \
    -d "{
      \"members\": [{
        \"newsletters\": $UPDATED
      }]
    }"
done
```

## Email Service Configuration

Ghost handles email delivery via:
- **Mailgun** (default for Ghost(Pro))
- **Custom SMTP** (self-hosted)
- **Bulk email API** (advanced)

Configure in Ghost Admin → Settings → Email newsletter.

**Note:** The API doesn't manage email service settings; those are configured in Ghost Admin.

## Best Practices

- **Consistent schedule** - Train readers to expect emails at set times
- **Clear sender identity** - Use recognizable sender name/email
- **Valuable content** - Every email should provide value
- **Mobile-friendly** - Keep designs simple and scannable
- **Respect preferences** - Make unsubscribe easy, honor choices
- **Test before sending** - Always review test emails
- **Monitor engagement** - Track opens/clicks, adjust strategy
- **Segment audiences** - Use multiple newsletters for different interests
- **Personal touch** - Write conversationally, avoid corporate speak
- **Call to action** - Give readers a clear next step

## Troubleshooting

### Emails not sending
- Check newsletter status is "active"
- Verify member is subscribed to that newsletter
- Confirm email service is configured correctly
- Check Ghost Admin logs for delivery errors

### Members not receiving
- Verify member's email is valid
- Check member's newsletter subscription status
- Look for unsubscribe/bounce records
- Test with a known-good email address

### Formatting issues
- Keep HTML simple and semantic
- Avoid complex CSS (email clients strip it)
- Test across email clients (Gmail, Outlook, Apple Mail)
- Use Ghost's built-in email cards for consistency
