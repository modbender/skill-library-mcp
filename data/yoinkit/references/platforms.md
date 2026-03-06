# Yoinkit Platform Capabilities

| Platform | Content | Transcript | Search | Trending | User Feed | Notes |
|----------|:-------:|:----------:|:------:|:--------:|:---------:|-------|
| YouTube | ✅ | ✅ | ✅ | ✅ | ✅ | Full support; channel videos via handle or ID |
| TikTok | ✅ | ✅ | ✅ | ✅ | ✅ | trending, popular, hashtags endpoints |
| Instagram | ✅ | ✅ | ✅ | ❌ | ✅ | Search reels; user posts and reels |
| Twitter/X | ✅ | ✅ | ❌ | ❌ | ✅ | Content and user tweets |
| Facebook | ✅ | ✅ | ❌ | ❌ | ✅ | Posts and reels from pages |
| LinkedIn | ✅ | ❌ | ❌ | ❌ | ❌ | Post content only |
| Reddit | ✅ | ❌ | ✅ | ❌ | ❌ | Search + subreddit browsing |
| Pinterest | ✅ | ❌ | ✅ | ❌ | ❌ | Pin content and search |
| Threads | ✅ | ❌ | ❌ | ❌ | ✅ | Post content and user posts |
| Bluesky | ✅ | ❌ | ❌ | ❌ | ✅ | Post content and user posts |
| Truth Social | ✅ | ❌ | ❌ | ❌ | ✅ | Post content and user posts |
| Twitch | ✅ | ❌ | ❌ | ❌ | ❌ | Clips only |
| Kick | ✅ | ❌ | ❌ | ❌ | ❌ | Clips only |

## Endpoint Quick Reference

### Content (single post/video)
All take `url` (required):
- `youtube/video?url=URL`
- `tiktok/video?url=URL` (optional: `get_transcript`, `region`, `trim`)
- `instagram/post?url=URL` (optional: `trim`)
- `twitter/tweet?url=URL` (optional: `trim`)
- `facebook/post?url=URL` (optional: `get_comments`, `get_transcript`)
- `linkedin/post?url=URL`
- `reddit/post?url=URL` (optional: `cursor`, `trim`)
- `pinterest/pin?url=URL` (optional: `trim`)
- `threads/post?url=URL` (optional: `trim`)
- `bluesky/post?url=URL`
- `truthsocial/post?url=URL`
- `twitch/clip?url=URL`
- `kick/clip?url=URL`

### Transcript
All take `url` (required):
- `youtube/transcript?url=URL` (optional: `language`)
- `tiktok/transcript?url=URL` (optional: `language`, `use_ai_as_fallback`)
- `instagram/transcript?url=URL`
- `twitter/transcript?url=URL`
- `facebook/transcript?url=URL`

### Search
- `youtube/search?query=Q` (optional: `sortBy`, `uploadDate`, `filter`, `continuationToken`, `includeExtras`)
- `youtube/search/hashtag?hashtag=H` (optional: `continuationToken`, `type`)
- `tiktok/search?query=Q` (optional: `sort_by`, `date_posted`, `region`, `cursor`, `trim`)
- `tiktok/search/hashtag?hashtag=H` (optional: `cursor`, `trim`)
- `tiktok/search/top?query=Q` (optional: `cursor`, `trim`)
- `instagram/search?query=Q` (optional: `page`)
- `reddit/search?query=Q` (optional: `sort`, `timeframe`, `after`, `trim`)
- `reddit/subreddit?subreddit=NAME` (optional: `sort`, `timeframe`, `cursor`)
- `reddit/subreddit/search?subreddit=NAME` (optional: `query`, `filter`, `sort`, `timeframe`, `cursor`)
- `pinterest/search?query=Q` (optional: `cursor`, `trim`)

### Trending
- `youtube/trending` (no parameters)
- `tiktok/trending?region=CC` (optional: `trim`)
- `tiktok/popular` (optional: `period`, `page`, `orderBy`, `countryCode`)
- `tiktok/hashtags` (optional: `period`, `page`, `countryCode`, `newOnBoard`)

### User Feed
- `youtube/channel/videos` (use `channelId` or `handle`; optional: `sort`, `continuationToken`, `includeExtras`)
- `tiktok/user/videos` (use `handle` or `user_id`; optional: `cursor`, `trim`)
- `instagram/user/posts?handle=H` (optional: `max_id`)
- `instagram/user/reels` (use `handle` or `user_id`; optional: `max_id`)
- `twitter/user/tweets` (use `handle` or `userId`; optional: `cursor`, `trim`)
- `facebook/user/posts` (use `url` or `pageId`; optional: `cursor`)
- `facebook/user/reels` (use `url` or `pageId`; optional: `cursor`)
- `threads/user/posts?handle=H` (optional: `max_id`, `trim`)
- `bluesky/user/posts` (use `handle` or `user_id`; optional: `cursor`)
- `truthsocial/user/posts` (use `handle` or `user_id`; optional: `max_id`)
