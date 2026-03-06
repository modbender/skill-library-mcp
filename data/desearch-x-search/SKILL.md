---
name: desearch-x-search
description: Search X (Twitter) in real time. Find posts by keyword, user, or hashtag. Get a user's timeline, replies, retweeters, or fetch specific posts by ID or URL. Supports advanced filters like date range, language, engagement thresholds, and media type.
metadata: {"clawdbot":{"emoji":"𝕏","homepage":"https://desearch.ai","requires":{"env":["DESEARCH_API_KEY"]}}}
---

# X (Twitter) Search By Desearch

Real-time X/Twitter search and monitoring. Search posts, track users, get timelines, replies, and retweeters with powerful filtering.

## Setup

1. Get an API key from https://console.desearch.ai
2. Set environment variable: `export DESEARCH_API_KEY='your-key-here'`

## Common Fields

All tweet-returning endpoints share these shapes. Fields marked `*` are always present.

### Tweet
| Field | Type | Description |
|-------|------|-------------|
| `id`* | string | Post ID |
| `text`* | string | Post content |
| `created_at`* | string | ISO 8601 timestamp |
| `url` | string\|null | Direct link: `https://x.com/{username}/status/{id}` |
| `like_count`* | int | Likes |
| `retweet_count`* | int | Retweets |
| `reply_count`* | int | Replies |
| `quote_count`* | int | Quotes |
| `bookmark_count`* | int | Bookmarks |
| `view_count` | int\|null | Views |
| `lang` | string\|null | Language code (e.g. `en`) |
| `is_retweet` | bool\|null | Is a retweet |
| `is_quote_tweet` | bool\|null | Is a quote tweet |
| `conversation_id` | string\|null | Thread ID |
| `in_reply_to_screen_name` | string\|null | Username of post being replied to |
| `in_reply_to_status_id` | string\|null | ID of post being replied to |
| `media` | array\|null | `[{media_url, type}]` — type: `photo`, `video`, `animated_gif` |
| `entities` | object\|null | `{hashtags, symbols, urls, user_mentions}` |
| `quote` | Tweet\|null | Nested quoted tweet |
| `retweet` | Tweet\|null | Original tweet _(timeline endpoint only)_ |
| `user` | User\|null | Post author — see User below |

### User
| Field | Type | Description |
|-------|------|-------------|
| `id`* | string | User ID |
| `username`* | string | @handle (without `@`) |
| `name` | string\|null | Display name |
| `url` | string\|null | Profile URL |
| `description` | string\|null | Bio |
| `followers_count` | int\|null | Followers |
| `followings_count` | int\|null | Following |
| `statuses_count` | int\|null | Total tweets posted |
| `verified` | bool\|null | Legacy verified badge |
| `is_blue_verified` | bool\|null | Twitter Blue subscriber |
| `location` | string\|null | Self-reported location |
| `created_at` | string\|null | Account creation date |
| `profile_image_url` | string\|null | Avatar URL |

## Endpoints

### `x` — Search Posts

Search X posts by keyword, hashtag, or user with engagement filters.

```bash
scripts/desearch.py x "Bittensor TAO" --sort Latest --count 10
scripts/desearch.py x "AI news" --user elonmusk --start-date 2025-01-01
scripts/desearch.py x "crypto" --min-likes 100 --verified --lang en
```

**Options:**
| Option | Description |
|--------|-------------|
| `--sort` | `Top` (default) or `Latest` |
| `--user`, `-u` | Filter to posts by username |
| `--start-date` | Start date UTC (YYYY-MM-DD) |
| `--end-date` | End date UTC (YYYY-MM-DD) |
| `--lang` | Language code (e.g. `en`, `es`) |
| `--verified` | Only verified users |
| `--blue-verified` | Only Twitter Blue users |
| `--is-quote` | Only quote tweets |
| `--is-video` | Only posts with video |
| `--is-image` | Only posts with images |
| `--min-retweets` | Minimum retweet count |
| `--min-replies` | Minimum reply count |
| `--min-likes` | Minimum like count |
| `--count`, `-n` | Results count (default: 20, max: 100) |

**Response:** `Tweet[]`


### `x_post` — Retrieve Post by ID

Fetch a single post by its numeric ID.

```bash
scripts/desearch.py x_post 1892527552029499853
```

**Response:** `Tweet`


### `x_urls` — Fetch Posts by URLs

Retrieve one or more posts by their X URLs.

```bash
scripts/desearch.py x_urls "https://x.com/user/status/123" "https://x.com/user/status/456"
```

**Response:** `Tweet[]`


### `x_user` — Search Posts by User

Search within a specific user's posts for a keyword.

```bash
scripts/desearch.py x_user elonmusk --query "AI" --count 10
```

**Options:**
| Option | Description |
|--------|-------------|
| `--query`, `-q` | Keyword to filter the user's posts |
| `--count`, `-n` | Results count (default: 10, max: 100) |

**Response:** `Tweet[]`


### `x_timeline` — Get User Timeline

Fetch the most recent posts from a user's timeline. Retweets include a `retweet` field with the original post.

```bash
scripts/desearch.py x_timeline elonmusk --count 20
```

**Options:**
| Option | Description |
|--------|-------------|
| `--count`, `-n` | Number of posts (default: 20, max: 100) |

**Response:** `{ user: User, tweets: Tweet[] }`


### `x_retweeters` — Get Retweeters of a Post

List users who retweeted a specific post. Supports cursor-based pagination.

```bash
scripts/desearch.py x_retweeters 1982770537081532854
scripts/desearch.py x_retweeters 1982770537081532854 --cursor "AAAAANextCursorValue=="
```

**Options:**
| Option | Description |
|--------|-------------|
| `--cursor` | Pagination cursor from a previous response |

**Response:** `{ users: User[], next_cursor: string|null }` — `next_cursor` is `null` when no more pages remain.


### `x_replies` — Get User's Replies

Fetch a user's tweets-and-replies timeline. Replies have `in_reply_to_screen_name` and `in_reply_to_status_id` set.

```bash
scripts/desearch.py x_replies elonmusk --count 10
scripts/desearch.py x_replies elonmusk --query "AI" --count 10
```

**Options:**
| Option | Description |
|--------|-------------|
| `--count`, `-n` | Results count (default: 10, max: 100) |
| `--query`, `-q` | Filter keyword |

**Response:** `Tweet[]`


### `x_post_replies` — Get Replies to a Post

Fetch replies to a specific post by ID.

```bash
scripts/desearch.py x_post_replies 1234567890 --count 10
scripts/desearch.py x_post_replies 1234567890 --query "thanks" --count 5
```

**Options:**
| Option | Description |
|--------|-------------|
| `--count`, `-n` | Results count (default: 10, max: 100) |
| `--query`, `-q` | Filter keyword within replies |

**Response:** `Tweet[]`

### Errors
Status 401, Unauthorized (e.g., missing/invalid API key)
```json
{
  "detail": "Invalid or missing API key"
}
```

Status 402, Payment Required (e.g., balance depleted)
```json
{
  "detail": "Insufficient balance, please add funds to your account to continue using the service."
}
```

## Resources
- [API Reference](https://desearch.ai/docs/api-reference)
- [Desearch Console](https://console.desearch.ai)
