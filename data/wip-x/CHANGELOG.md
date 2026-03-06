# Changelog


## 1.0.1 (2026-02-21)

Release.

## 1.0.0 (2026-02-20)

Initial release. X Platform API wrapper built on @xdevplatform/xdk.

### Sensor (Read)
- `fetch_post` ... fetch a single post by ID or URL
- `search_recent` ... search recent tweets (last 7 days)
- `get_bookmarks` ... get authenticated user's bookmarks
- `get_user` ... get user profile by username or ID
- `get_me` ... get authenticated user's profile

### Actuator (Write)
- `post_tweet` ... post a new tweet (with optional reply, quote, media)
- `delete_tweet` ... delete a tweet by ID
- `bookmark_post` ... bookmark a post
- `unbookmark_post` ... remove a bookmark
- `upload_media` ... upload image/video/gif for tweets

### Interfaces
- CLI (`wip-x`)
- MCP server (7 tools)
- ES module (importable)
- SKILL.md (agent instructions)

Built on @xdevplatform/xdk v0.4.0 (official X TypeScript SDK, MIT, zero transitive deps).
