# Index

| API | Line |
|-----|------|
| LinkedIn | 91 |
| Instagram Graph API | 154 |
| TikTok | 217 |
| Pinterest | 296 |
| Reddit | 372 |
| Twitch | 452 |

---

# Twitter / X

## Base URL
```
https://api.twitter.com/2
```

## Authentication
```bash
# OAuth 2.0 Bearer Token (app-only)
curl "https://api.twitter.com/2/users/me" \
  -H "Authorization: Bearer $TWITTER_BEARER_TOKEN"

# OAuth 1.0a (user context) - required for posting
# Use OAuth library for signature generation
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /tweets | POST | Create tweet |
| /tweets/:id | GET | Get tweet |
| /tweets/:id | DELETE | Delete tweet |
| /users/me | GET | Get current user |
| /users/:id/tweets | GET | Get user tweets |
| /tweets/search/recent | GET | Search tweets |

## Quick Examples

### Get Tweet
```bash
curl "https://api.twitter.com/2/tweets/1234567890?expansions=author_id&tweet.fields=created_at,public_metrics" \
  -H "Authorization: Bearer $TWITTER_BEARER_TOKEN"
```

### Get User Tweets
```bash
curl "https://api.twitter.com/2/users/$USER_ID/tweets?max_results=10&tweet.fields=created_at,public_metrics" \
  -H "Authorization: Bearer $TWITTER_BEARER_TOKEN"
```

### Search Tweets
```bash
curl "https://api.twitter.com/2/tweets/search/recent?query=from:username&max_results=10" \
  -H "Authorization: Bearer $TWITTER_BEARER_TOKEN"
```

### Post Tweet (OAuth 1.0a required)
```bash
curl -X POST "https://api.twitter.com/2/tweets" \
  -H "Authorization: OAuth oauth_consumer_key=...,oauth_token=...,oauth_signature=..." \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, World!"}'
```

### Get User by Username
```bash
curl "https://api.twitter.com/2/users/by/username/$USERNAME?user.fields=description,public_metrics" \
  -H "Authorization: Bearer $TWITTER_BEARER_TOKEN"
```

## Fields & Expansions

| Parameter | Example |
|-----------|---------|
| tweet.fields | created_at,public_metrics,author_id |
| user.fields | description,public_metrics,verified |
| expansions | author_id,referenced_tweets.id |

## Common Traps

- Read operations: Bearer token works
- Write operations: OAuth 1.0a required (complex signatures)
- API v2 is different from v1.1 (still exists but deprecated)
- Free tier: very limited (1500 tweets/month read)
- Rate limits vary significantly by endpoint

## Rate Limits

Free tier (very limited):
- 1500 tweets/month read
- 50 tweets/month write
- 1 request/15 min for some endpoints

Basic tier ($100/month) much higher.

## Official Docs
https://developer.twitter.com/en/docs/twitter-api
# LinkedIn

Professional networking API for accessing profiles, connections, and company data.

## Base URL
`https://api.linkedin.com/v2`

## Authentication
OAuth 2.0 with 3-legged flow. Requires access token via Authorization header.

```bash
curl -X GET "https://api.linkedin.com/v2/userinfo" \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

## Core Endpoints

### Get User Profile
```bash
curl -X GET "https://api.linkedin.com/v2/userinfo" \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### Get Profile (with projections)
```bash
curl -X GET "https://api.linkedin.com/v2/me?projection=(id,firstName,lastName,profilePicture)" \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### Share Post
```bash
curl -X POST "https://api.linkedin.com/v2/ugcPosts" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "author": "urn:li:person:{PERSON_ID}",
    "lifecycleState": "PUBLISHED",
    "specificContent": {
      "com.linkedin.ugc.ShareContent": {
        "shareCommentary": {"text": "Hello LinkedIn!"},
        "shareMediaCategory": "NONE"
      }
    },
    "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
  }'
```

## Rate Limits
- 100 requests/day for most endpoints (varies by product)
- Application-level and member-level limits apply
- Rate limit headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`

## Gotchas
- Requires LinkedIn Developer Program membership for most APIs
- Marketing APIs require separate approval and different scopes
- Profile fields changed significantly in v2; use projections syntax
- `r_liteprofile` scope deprecated; use `openid`, `profile`, `email` scopes
- Company page posting requires `w_member_social` or `w_organization_social`

## Links
- [Docs](https://learn.microsoft.com/en-us/linkedin/)
- [Authentication](https://learn.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow)
- [API Reference](https://learn.microsoft.com/en-us/linkedin/shared/integrations/people)
# Instagram Graph API

Meta's Instagram Graph API for business accounts and content publishing.

## Base URL
`https://graph.instagram.com` (Instagram Graph API)
`https://graph.facebook.com/v21.0` (via Facebook Graph API)

## Authentication
OAuth 2.0 via Facebook Login. Requires Facebook App and Instagram Business/Creator Account linked to a Facebook Page.

```bash
curl -X GET "https://graph.instagram.com/me?fields=id,username&access_token={ACCESS_TOKEN}"
```

## Core Endpoints

### Get User Profile
```bash
curl -X GET "https://graph.instagram.com/me?fields=id,username,account_type,media_count&access_token={ACCESS_TOKEN}"
```

### Get User Media
```bash
curl -X GET "https://graph.instagram.com/me/media?fields=id,caption,media_type,media_url,timestamp&access_token={ACCESS_TOKEN}"
```

### Publish Photo
```bash
# Step 1: Create media container
curl -X POST "https://graph.facebook.com/v21.0/{IG_USER_ID}/media" \
  -d "image_url=https://example.com/photo.jpg" \
  -d "caption=My photo #hashtag" \
  -d "access_token={ACCESS_TOKEN}"

# Step 2: Publish container
curl -X POST "https://graph.facebook.com/v21.0/{IG_USER_ID}/media_publish" \
  -d "creation_id={CONTAINER_ID}" \
  -d "access_token={ACCESS_TOKEN}"
```

### Get Insights
```bash
curl -X GET "https://graph.instagram.com/{MEDIA_ID}/insights?metric=impressions,reach,engagement&access_token={ACCESS_TOKEN}"
```

## Rate Limits
- 200 calls/hour per user (Instagram Graph API)
- 4800 calls/24h per app per user
- Content Publishing: 25 posts per 24-hour period

## Gotchas
- Only works with Business/Creator accounts (not personal)
- Must link Instagram account to a Facebook Page
- Basic Display API deprecated; use Instagram Graph API with Instagram Login
- Carousel posts require creating all media containers first
- Stories API only available for certain use cases
- Reels have separate content publishing flow

## Links
- [Docs](https://developers.facebook.com/docs/instagram-api)
- [Instagram Graph API](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api)
- [Content Publishing](https://developers.facebook.com/docs/instagram-api/guides/content-publishing)
# TikTok

TikTok API for content display, posting, and research access.

## Base URL
`https://open.tiktokapis.com/v2`

## Authentication
OAuth 2.0. Requires registered app on TikTok for Developers portal and user authorization for scopes.

```bash
curl -X POST "https://open.tiktokapis.com/v2/post/publish/creator_info/query/" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json"
```

## Core Endpoints

### Query Creator Info
```bash
curl -X POST "https://open.tiktokapis.com/v2/post/publish/creator_info/query/" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json"
```

### Direct Post Video (FILE_UPLOAD)
```bash
curl -X POST "https://open.tiktokapis.com/v2/post/publish/video/init/" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "post_info": {
      "title": "My video #fyp",
      "privacy_level": "PUBLIC_TO_EVERYONE",
      "disable_duet": false,
      "disable_comment": false,
      "disable_stitch": false
    },
    "source_info": {
      "source": "FILE_UPLOAD",
      "video_size": 50000000,
      "chunk_size": 10000000,
      "total_chunk_count": 5
    }
  }'
```

### Get User Info (Display API)
```bash
curl -X GET "https://open.tiktokapis.com/v2/user/info/?fields=open_id,display_name,avatar_url" \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### Get User Videos
```bash
curl -X POST "https://open.tiktokapis.com/v2/video/list/?fields=id,title,video_description,create_time,cover_image_url" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"max_count": 20}'
```

## Rate Limits
- Display API: 1000 requests/day per user
- Content Posting API: Rate limits vary by endpoint
- Research API: Subject to application approval

## Gotchas
- **Unaudited apps**: All content posted is PRIVATE until app passes audit
- Requires `video.publish` scope for posting (needs approval)
- Video restrictions: MP4/MOV, H.264 codec, max 10 min, max 4GB
- Photo posts require URL from verified domain (not file upload)
- Privacy levels depend on creator's account settings
- Research API requires separate academic/business approval

## Links
- [Docs](https://developers.tiktok.com/doc/overview)
- [Content Posting API](https://developers.tiktok.com/doc/content-posting-api-get-started)
- [Display API](https://developers.tiktok.com/doc/display-api-get-started)
- [Login Kit](https://developers.tiktok.com/doc/login-kit-ios-quickstart)
# Pinterest

Pinterest API for pins, boards, and analytics management.

## Base URL
`https://api.pinterest.com/v5`

## Authentication
OAuth 2.0. Requires app registration and user authorization.

```bash
curl -X GET "https://api.pinterest.com/v5/user_account" \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

## Core Endpoints

### Get User Account
```bash
curl -X GET "https://api.pinterest.com/v5/user_account" \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### List Pins
```bash
curl -X GET "https://api.pinterest.com/v5/pins" \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### Create Pin
```bash
curl -X POST "https://api.pinterest.com/v5/pins" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "board_id": "1234567890",
    "title": "My Pin",
    "description": "Pin description",
    "link": "https://example.com",
    "media_source": {
      "source_type": "image_url",
      "url": "https://example.com/image.jpg"
    }
  }'
```

### Get Boards
```bash
curl -X GET "https://api.pinterest.com/v5/boards" \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### Get Pin Analytics
```bash
curl -X GET "https://api.pinterest.com/v5/pins/{pin_id}/analytics?start_date=2024-01-01&end_date=2024-01-31&metric_types=IMPRESSION,SAVE,PIN_CLICK" \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

## Rate Limits
- 1000 requests/minute per access token (standard)
- Write operations: 10 requests/minute per user
- Analytics: Lower limits, varies by endpoint

## Gotchas
- API v5 is current; v3/v4 deprecated
- Business accounts required for analytics endpoints
- Pin creation requires `pins:write` scope
- Video pins have separate upload flow (media upload → create pin)
- Image URLs must be publicly accessible
- `creative_type` field shows pin type (image, video, carousel, etc.)
- Some features (protected pins) may timeout with `creative_type` filter

## Links
- [Docs](https://developers.pinterest.com/docs/getting-started/introduction/)
- [API Reference](https://developers.pinterest.com/docs/api/v5/)
- [Authentication](https://developers.pinterest.com/docs/getting-started/authentication/)
# Reddit

Reddit API for posts, comments, subreddits, and user data.

## Base URL
`https://oauth.reddit.com` (authenticated)
`https://www.reddit.com` (public, append `.json`)

## Authentication
OAuth 2.0. Supports "script" (personal use), "web app", and "installed app" types.

```bash
# Get access token
curl -X POST "https://www.reddit.com/api/v1/access_token" \
  -u "CLIENT_ID:CLIENT_SECRET" \
  -d "grant_type=password&username=USER&password=PASS"

# Use token
curl -X GET "https://oauth.reddit.com/api/v1/me" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "User-Agent: MyApp/1.0"
```

## Core Endpoints

### Get Current User
```bash
curl -X GET "https://oauth.reddit.com/api/v1/me" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "User-Agent: MyApp/1.0"
```

### Get Subreddit Posts
```bash
curl -X GET "https://oauth.reddit.com/r/programming/hot?limit=25" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "User-Agent: MyApp/1.0"
```

### Submit Post
```bash
curl -X POST "https://oauth.reddit.com/api/submit" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "User-Agent: MyApp/1.0" \
  -d "sr=test&kind=self&title=Test Post&text=Hello world"
```

### Submit Comment
```bash
curl -X POST "https://oauth.reddit.com/api/comment" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "User-Agent: MyApp/1.0" \
  -d "thing_id=t3_abc123&text=My comment"
```

### Vote
```bash
curl -X POST "https://oauth.reddit.com/api/vote" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "User-Agent: MyApp/1.0" \
  -d "id=t3_abc123&dir=1"
```

## Rate Limits
- 60 requests/minute per OAuth client
- 10 requests/minute without OAuth
- Must include User-Agent header (Reddit blocks generic agents)

## Gotchas
- **User-Agent required**: Must be descriptive (e.g., `platform:app:version (by /u/username)`)
- Thing IDs prefixed: `t1_` (comment), `t2_` (account), `t3_` (link/post), `t4_` (message), `t5_` (subreddit)
- Password grant only for "script" apps (personal use)
- Public endpoints work with `.json` suffix but have lower rate limits
- Subreddit names are case-insensitive
- Posting requires account with sufficient karma in many subreddits

## Links
- [Docs](https://www.reddit.com/dev/api/)
- [OAuth2](https://github.com/reddit-archive/reddit/wiki/OAuth2)
- [API Rules](https://www.reddit.com/wiki/api)
# Twitch

Twitch Helix API for streams, users, clips, and channel management.

## Base URL
`https://api.twitch.tv/helix`

## Authentication
OAuth 2.0. Requires Client ID header and Bearer token. Some endpoints work with app access tokens, others require user tokens.

```bash
curl -X GET "https://api.twitch.tv/helix/users" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Client-Id: {CLIENT_ID}"
```

## Core Endpoints

### Get Users
```bash
curl -X GET "https://api.twitch.tv/helix/users?login=twitchdev" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Client-Id: {CLIENT_ID}"
```

### Get Streams
```bash
curl -X GET "https://api.twitch.tv/helix/streams?user_login=twitchdev" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Client-Id: {CLIENT_ID}"
```

### Get Channel Info
```bash
curl -X GET "https://api.twitch.tv/helix/channels?broadcaster_id=12345" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Client-Id: {CLIENT_ID}"
```

### Create Clip
```bash
curl -X POST "https://api.twitch.tv/helix/clips?broadcaster_id=12345" \
  -H "Authorization: Bearer {USER_ACCESS_TOKEN}" \
  -H "Client-Id: {CLIENT_ID}"
```

### Get Videos
```bash
curl -X GET "https://api.twitch.tv/helix/videos?user_id=12345" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Client-Id: {CLIENT_ID}"
```

### Send Chat Message
```bash
curl -X POST "https://api.twitch.tv/helix/chat/messages" \
  -H "Authorization: Bearer {USER_ACCESS_TOKEN}" \
  -H "Client-Id: {CLIENT_ID}" \
  -H "Content-Type: application/json" \
  -d '{"broadcaster_id": "12345", "sender_id": "67890", "message": "Hello!"}'
```

## Rate Limits
- 800 requests/minute (app access token)
- 30 requests/minute for certain endpoints (clips, etc.)
- Points-based system: different endpoints cost different points
- Headers: `Ratelimit-Limit`, `Ratelimit-Remaining`, `Ratelimit-Reset`

## Gotchas
- **Two header requirement**: Both `Authorization` AND `Client-Id` required
- v5 (Kraken) API deprecated; use Helix only
- User IDs are numeric strings, not usernames
- EventSub preferred over webhooks for real-time events
- Some endpoints need user tokens (e.g., sending messages, creating clips)
- Pagination uses cursor, not offset
- Thumbnail URLs have `{width}` and `{height}` placeholders

## Links
- [Docs](https://dev.twitch.tv/docs/api/)
- [API Reference](https://dev.twitch.tv/docs/api/reference/)
- [Authentication](https://dev.twitch.tv/docs/authentication/)
- [EventSub](https://dev.twitch.tv/docs/eventsub/)
