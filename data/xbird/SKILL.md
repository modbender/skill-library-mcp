---
name: xbird
description: "Use when the user asks to tweet, post threads, read tweets, search Twitter/X, check mentions, manage engagement (like/retweet/bookmark), update profile (bio, avatar, banner), upload media, or interact with Twitter accounts. Triggers: twitter, tweet, post, thread, timeline, mentions, followers, following, likes, retweet, bookmark, profile picture, bio."
argument-hint: "[action or query]"
---

# xbird — Twitter/X for AI Agents

34 MCP tools for Twitter/X with x402 micropayments. Runs locally from residential IP.

## Setup

Add xbird MCP server to Claude Code:

```bash
claude mcp add xbird -- npx @checkra1n/xbird
```

Required environment variables (set in `~/.claude/settings.json` or shell):
- `XBIRD_AUTH_TOKEN` — from x.com cookies (DevTools → Application → Cookies → `auth_token`)
- `XBIRD_CT0` — from x.com cookies (DevTools → Application → Cookies → `ct0`)
- `XBIRD_PRIVATE_KEY` — wallet private key for x402 payments (optional, needed for paid tier)

## Tools Reference

### Read — $0.001/call
| Tool | Description |
|------|-------------|
| `get_tweet` | Get tweet by ID |
| `get_thread` | Get full thread/conversation chain |
| `get_replies` | Get replies to a tweet (supports `count`, `cursor`) |
| `get_user` | Get user profile by handle |
| `get_user_about` | Get detailed user info (bio, stats, links) |
| `get_current_user` | Get authenticated user's profile |
| `get_home_timeline` | Get home feed (supports `count`, `cursor`) |
| `get_news` | Get trending topics (tabs: `trending`, `forYou`, `news`, `sports`, `entertainment`) |
| `get_lists` | Get owned Twitter lists |
| `get_list_timeline` | Get tweets from a list by list ID |

### Search — $0.005/call
| Tool | Description |
|------|-------------|
| `search_tweets` | Search tweets. Supports operators: `from:user`, `to:user`, `since:2024-01-01`, `filter:media`, `-filter:retweets` |
| `get_mentions` | Get mentions for a handle |

### Bulk — $0.01/call
| Tool | Description |
|------|-------------|
| `get_user_tweets` | Get user's tweets. **Requires numeric `userId`** — get it from `get_user` first |
| `get_followers` | Get user's followers. **Requires numeric `userId`** |
| `get_following` | Get who user follows. **Requires numeric `userId`** |
| `get_likes` | Get user's liked tweets. **Requires numeric `userId`** |
| `get_bookmarks` | Get bookmarked tweets |
| `get_list_memberships` | Get lists user is a member of |

### Write — $0.01/call
| Tool | Description |
|------|-------------|
| `post_tweet` | Post a tweet. Pass `mediaIds` array to attach media |
| `reply_to_tweet` | Reply to a tweet by `replyToId` |
| `post_thread` | Post a thread — array of strings, **minimum 2 tweets** |
| `like_tweet` / `unlike_tweet` | Like or unlike by tweet ID |
| `retweet` / `unretweet` | Retweet or undo by tweet ID |
| `bookmark_tweet` / `unbookmark_tweet` | Bookmark or remove by tweet ID |
| `follow_user` / `unfollow_user` | Follow or unfollow by handle |

### Profile — $0.01/call
| Tool | Description |
|------|-------------|
| `update_profile` | Update bio/description text |
| `update_profile_image` | Update avatar — absolute file path to image |
| `update_profile_banner` | Update banner — absolute file path to image |
| `remove_profile_banner` | Remove banner image |

### Media — $0.05/call
| Tool | Description |
|------|-------------|
| `upload_media` | Upload image/video, returns `mediaId`. Pass it to `post_tweet` or `reply_to_tweet` via `mediaIds` |

## Common Workflows

### Post a tweet with an image
1. `upload_media` with file path → get `mediaId`
2. `post_tweet` with text and `mediaIds: ["<mediaId>"]`

### Get someone's recent tweets
1. `get_user` with handle → get numeric `userId`
2. `get_user_tweets` with `userId`

### Update profile with new avatar and bio
1. `update_profile_image` with file path
2. `update_profile` with new description text

### Search and engage
1. `search_tweets` with query (e.g. `"AI agents" since:2024-01-01 -filter:retweets`)
2. `like_tweet` or `retweet` interesting results

## Important Notes

- **Handles**: work with or without `@` prefix
- **userId vs handle**: Bulk tools require numeric `userId`. Always call `get_user` first to resolve handle → userId
- **Pagination**: most list tools accept `cursor` from previous response for next page
- **Media flow**: always upload first, then attach `mediaId` to tweet
- **Rate limits**: if a tool returns an error about rate limiting, wait 1-2 minutes before retrying
- **x402 payments**: all calls are metered via micropayments on Base (USDC). Free tier available without wallet key
