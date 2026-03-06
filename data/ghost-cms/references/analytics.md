# Analytics & Insights

Subscriber counts, popular content, and performance metrics.

## Version & API Coverage

**Ghost Version Support:**
- Ghost 5.0+ - Full support
- Ghost 6.0+ - Compatible (but limited analytics access)

**API Version Used:** `v5.0` (Accept-Version header)

**Important:** While Ghost 6.0 introduced native analytics, **integration API tokens do not have access to the full analytics suite**. See [Limitations](#limitations) below for details.

## Authentication Types & Capabilities

### Integration Token Authentication (Current)
**What you CAN access:**
- ✅ Basic member counts and lists
- ✅ Post metadata (including email stats when available)
- ✅ Email engagement metrics (opens, clicks)
- ✅ Tag/author statistics
- ✅ Comment counts
- ✅ Newsletter subscriber counts

**What you CANNOT access:**
- ❌ Web traffic analytics (page views, sources, devices)
- ❌ Real-time visitor data
- ❌ Detailed engagement analytics from Ghost Analytics
- ❌ Member behavior analytics beyond email
- ❌ Advanced stats endpoints (`/stats/*`)

### User Authentication (Not Recommended for Automation)
**Full access** to all analytics features, but requires:
- Email/password login
- Session management
- 2FA support
- Not suitable for programmatic access

### Tinybird Integration (Advanced)
For self-hosted Ghost, you can configure Tinybird directly for analytics:
- Requires separate Tinybird account
- Can query analytics data via Tinybird API
- See Ghost's [Tinybird integration docs](https://ghost.org/integrations/tinybird)

## Available Analytics (Integration Token)

### Subscriber Metrics

#### Total Subscriber Count

```bash
curl "${GHOST_URL}/ghost/api/admin/members/stats/count/" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

Returns:
```json
{
  "data": {
    "total": 1234,
    "paid": 56,
    "free": 1178,
    "comped": 0
  }
}
```

**Note:** This endpoint is available but may return permissions error with some integration tokens.

#### New Subscribers (Time Period)

```bash
# Subscribers added in last 30 days
THIRTY_DAYS_AGO=$(date -u -v-30d '+%Y-%m-%dT%H:%M:%S.000Z')

curl "${GHOST_URL}/ghost/api/admin/members/?filter=created_at:>'${THIRTY_DAYS_AGO}'&limit=all" \
  -H "Authorization: Ghost ${GHOST_KEY}" | \
  jq '.members | length'
```

#### Recent Subscribers

```bash
curl "${GHOST_URL}/ghost/api/admin/members/?order=created_at%20desc&limit=10" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

### Email Performance Metrics

**Available for posts that were sent as newsletters:**

```bash
# Get post with email stats
curl "${GHOST_URL}/ghost/api/admin/posts/${POST_ID}/?include=email" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

Returns email engagement data:
```json
{
  "posts": [{
    "email": {
      "email_count": 12,
      "delivered_count": 12,
      "opened_count": 5,
      "failed_count": 0,
      "subject": "Post Title",
      "status": "submitted"
    }
  }]
}
```

**Metrics available:**
- `email_count` - Total emails sent
- `delivered_count` - Successfully delivered
- `opened_count` - Unique opens
- `failed_count` - Delivery failures

**To calculate open rate:**
```bash
curl "${GHOST_URL}/ghost/api/admin/posts/${POST_ID}/?include=email" \
  -H "Authorization: Ghost ${GHOST_KEY}" | \
  jq '.posts[0].email | {
    sent: .email_count,
    opened: .opened_count,
    open_rate: ((.opened_count / .email_count) * 100 | round)
  }'
```

### Content Engagement Proxies

Since direct view counts aren't available, use these engagement indicators:

#### Posts by Email Opens

```bash
curl "${GHOST_URL}/ghost/api/admin/posts/?filter=status:published&limit=50&include=email" \
  -H "Authorization: Ghost ${GHOST_KEY}" | \
  jq '[.posts[] | select(.email != null) | {
    title: .title,
    opened: .email.opened_count,
    sent: .email.email_count,
    open_rate: ((.email.opened_count / .email.email_count) * 100 | round)
  }] | sort_by(.opened) | reverse | .[0:10]'
```

#### Posts by Click Count

```bash
curl "${GHOST_URL}/ghost/api/admin/posts/?limit=50&include=count.clicks" \
  -H "Authorization: Ghost ${GHOST_KEY}" | \
  jq '.posts | sort_by(.count.clicks) | reverse | .[0:10] | .[] | {
    title: .title,
    clicks: .count.clicks
  }'
```

### Tag/Topic Performance

```bash
# Get tag usage counts
curl "${GHOST_URL}/ghost/api/admin/tags/?limit=all&include=count.posts" \
  -H "Authorization: Ghost ${GHOST_KEY}" | \
  jq '.tags | sort_by(.count.posts) | reverse'
```

Returns tags sorted by number of posts.

#### Popular Tags (Last 6 Months)

```bash
# Get posts from last 6 months
SIX_MONTHS_AGO=$(date -u -v-6m '+%Y-%m-%dT%H:%M:%S.000Z')

curl "${GHOST_URL}/ghost/api/admin/posts/?filter=published_at:>'${SIX_MONTHS_AGO}'&include=tags&limit=all" \
  -H "Authorization: Ghost ${GHOST_KEY}" | \
  jq '[.posts[].tags[].name] | group_by(.) | map({tag: .[0], count: length}) | sort_by(.count) | reverse'
```

### Member Activity

#### Active Members (Recent Logins)

```bash
# Members who logged in recently
LAST_WEEK=$(date -u -v-7d '+%Y-%m-%dT%H:%M:%S.000Z')

curl "${GHOST_URL}/ghost/api/admin/members/?filter=last_seen_at:>'${LAST_WEEK}'&limit=all" \
  -H "Authorization: Ghost ${GHOST_KEY}" | \
  jq '.members | length'
```

#### Paid vs Free Distribution

```bash
curl "${GHOST_URL}/ghost/api/admin/members/stats/count/" \
  -H "Authorization: Ghost ${GHOST_KEY}" | \
  jq '.data | {
    total: .total,
    paid_percent: ((.paid / .total) * 100 | round),
    free_percent: ((.free / .total) * 100 | round)
  }'
```

## Newsletter Performance

### Newsletter Stats

```bash
# Get newsletter info including subscriber counts
curl "${GHOST_URL}/ghost/api/admin/newsletters/" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

Returns:
```json
{
  "newsletters": [{
    "name": "Newsletter Name",
    "slug": "newsletter-slug",
    "sender_email": "sender@example.com",
    "status": "active",
    "subscribe_on_signup": true
  }]
}
```

## Content Insights

### Publishing Frequency

```bash
# Posts per month (last 6 months)
for i in {0..5}; do
  START=$(date -u -v-${i}m -v1d '+%Y-%m-01T00:00:00.000Z')
  END=$(date -u -v-${i}m -v+1m -v1d '+%Y-%m-01T00:00:00.000Z')
  
  COUNT=$(curl -s "${GHOST_URL}/ghost/api/admin/posts/?filter=published_at:>'${START}'+published_at:<'${END}'" \
    -H "Authorization: Ghost ${GHOST_KEY}" | \
    jq '.posts | length')
  
  MONTH=$(date -v-${i}m '+%B %Y')
  echo "${MONTH}: ${COUNT} posts"
done
```

### Member-Only Content Check

```bash
# Last subscriber-exclusive post
curl "${GHOST_URL}/ghost/api/admin/posts/?filter=visibility:paid&order=published_at%20desc&limit=1" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

Returns most recent paid-members-only post.

### Content by Author

```bash
# Posts by author in last month
LAST_MONTH=$(date -u -v-30d '+%Y-%m-%dT%H:%M:%S.000Z')

curl "${GHOST_URL}/ghost/api/admin/posts/?filter=published_at:>'${LAST_MONTH}'&include=authors&limit=all" \
  -H "Authorization: Ghost ${GHOST_KEY}" | \
  jq '[.posts[].authors[0].name] | group_by(.) | map({author: .[0], posts: length}) | sort_by(.posts) | reverse'
```

## Time-Based Queries

### Posts This Week

```bash
WEEK_START=$(date -u -v-mon '+%Y-%m-%dT00:00:00.000Z')

curl "${GHOST_URL}/ghost/api/admin/posts/?filter=published_at:>'${WEEK_START}'&limit=all" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

### Posts Today

```bash
TODAY=$(date -u -v '+%Y-%m-%dT00:00:00.000Z')

curl "${GHOST_URL}/ghost/api/admin/posts/?filter=published_at:>'${TODAY}'&limit=all" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

## Common Analytics Queries

### "How many new subscribers this month?"

```bash
MONTH_START=$(date -u -v1d '+%Y-%m-01T00:00:00.000Z')

curl "${GHOST_URL}/ghost/api/admin/members/?filter=created_at:>'${MONTH_START}'&limit=all" \
  -H "Authorization: Ghost ${GHOST_KEY}" | \
  jq '.members | length'
```

### "What tags have been most popular in the past 6 months?"

See "Popular Tags (Last 6 Months)" above.

### "What was my most popular post by email opens?"

```bash
curl "${GHOST_URL}/ghost/api/admin/posts/?filter=status:published&limit=all&include=email" \
  -H "Authorization: Ghost ${GHOST_KEY}" | \
  jq '[.posts[] | select(.email != null)] | sort_by(.email.opened_count) | reverse | .[0] | {
    title: .title,
    published_at: .published_at,
    sent: .email.email_count,
    opened: .email.opened_count,
    open_rate: ((.email.opened_count / .email.email_count) * 100 | round)
  }'
```

### "When was my last subscriber-exclusive post?"

```bash
curl "${GHOST_URL}/ghost/api/admin/posts/?filter=visibility:paid&order=published_at%20desc&limit=1" \
  -H "Authorization: Ghost ${GHOST_KEY}" | \
  jq '.posts[0] | {
    title: .title,
    published_at: .published_at,
    days_ago: ((now - (.published_at | fromdateiso8601)) / 86400 | floor)
  }'
```

## Data Export

### Export All Subscribers

```bash
curl "${GHOST_URL}/ghost/api/admin/members/?limit=all" \
  -H "Authorization: Ghost ${GHOST_KEY}" | \
  jq -r '.members[] | [.email, .name, .created_at, .status] | @csv' > members.csv
```

### Export Post Metrics

```bash
curl "${GHOST_URL}/ghost/api/admin/posts/?limit=all&include=tags,authors,email" \
  -H "Authorization: Ghost ${GHOST_KEY}" | \
  jq -r '.posts[] | [
    .title,
    .published_at,
    (.tags | map(.name) | join(";")),
    (.email.email_count // 0),
    (.email.opened_count // 0),
    (if .email then ((.email.opened_count / .email.email_count) * 100 | round) else 0 end)
  ] | @csv' > posts.csv
```

## Limitations

### Ghost 6.0 Analytics Not Available via API Token

Ghost 6.0 introduced a comprehensive native analytics suite with:
- Real-time traffic monitoring
- Audience filtering (public/free/paid)
- Source tracking
- Device/browser analytics
- Content performance metrics

**However:** These features are **NOT accessible via integration API tokens**.

**Error when attempting to access:**
```bash
curl "${GHOST_URL}/ghost/api/admin/stats/" \
  -H "Authorization: Ghost ${GHOST_KEY}"
```

Returns:
```json
{
  "errors": [{
    "message": "API tokens do not have permission to access this endpoint",
    "type": "NoPermissionError"
  }]
}
```

### What Analytics ARE Available

With integration tokens, you can access:
- ✅ Email engagement (opens, clicks, delivery status)
- ✅ Member counts and growth
- ✅ Tag/author usage statistics
- ✅ Newsletter subscriber counts
- ✅ Publishing frequency metrics

### Accessing Full Ghost Analytics

**Option 1: Ghost Admin Web Interface**
- Log into your Ghost admin panel
- Navigate to Analytics section
- View all traffic, engagement, and member data
- Export reports manually

**Option 2: User Authentication (Advanced)**
- Use email/password login via session API
- Requires 2FA support
- Not recommended for automation
- See Ghost's [user authentication docs](https://ghost.org/docs/admin-api/#user-authentication)

**Option 3: Tinybird (Self-Hosted Only)**
If you're self-hosting Ghost:
- Configure Tinybird integration
- Query analytics via Tinybird API directly
- Requires separate Tinybird account
- See [Ghost's Tinybird integration guide](https://ghost.org/integrations/tinybird)

**Option 4: Third-Party Analytics**
Integrate external analytics tools:
- Google Analytics
- Plausible Analytics
- Fathom Analytics
- Custom tracking with webhooks

### API Version Notes

**Current API Version:** `v5.0`
- Used in all skill requests via `Accept-Version` header
- Fully compatible with Ghost 5.x and 6.x
- Some Ghost 6.0 features may not be exposed in v5.0 API

**Future:** Ghost may introduce `v6.0` API with:
- Improved analytics access
- New endpoints
- Enhanced authentication options

Monitor [Ghost's API changelog](https://ghost.org/docs/faq/api-versioning/) for updates.

## Best Practices

- **Use email metrics** - Most reliable engagement indicator available
- **Cache results** - Analytics queries can be resource-intensive
- **Batch requests** - Get all data in one call when possible
- **Use time filters** - Narrow queries to relevant time periods
- **Export periodically** - Keep historical data for trend analysis
- **Combine metrics** - Look at multiple signals for full picture
- **Consider external tools** - For traffic analytics, use Google Analytics or similar

## Troubleshooting

### "NoPermissionError" on stats endpoints

This is expected with integration tokens. Stats endpoints require user authentication.

**Solution:** Access analytics via Ghost Admin web interface, or use email engagement metrics as proxy.

### "UPDATE_CLIENT" error

Your API version (`v5.0`) is behind Ghost's current version.

**Solution:** This is informational. Ghost 6.x is backwards compatible with v5.0 API. No action needed unless you want to upgrade to a future v6.0 API when available.

### Missing email metrics on posts

Email metrics only appear on posts that were sent as newsletters.

**Check:**
- Post must be published
- Post must have been sent to newsletter subscribers
- Include `?include=email` in your request
