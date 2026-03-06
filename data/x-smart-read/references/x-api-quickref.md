# X API v2 Quick Reference

## Endpoints Used

| Endpoint | Route | Auth | Cost |
|----------|-------|------|------|
| Get Me | `GET /2/users/me` | OAuth 1.0a | ~$0.01 |
| User Tweets | `GET /2/users/:id/tweets` | OAuth 1.0a | ~$0.005 |
| User Mentions | `GET /2/users/:id/mentions` | OAuth 1.0a | ~$0.005 |
| Get User by Username | `GET /2/users/by/username/:username` | Bearer | ~$0.01 |
| Get Tweet | `GET /2/tweets/:id` | Bearer/OAuth | ~$0.005 |
| Batch Get Tweets | `GET /2/tweets?ids=id1,id2,...` | Bearer/OAuth | ~$0.005 |
| Search Recent | `GET /2/tweets/search/recent` | Bearer | ~$0.005 |
| Create Tweet | `POST /2/tweets` | OAuth 1.0a | Free |
| Delete Tweet | `DELETE /2/tweets/:id` | OAuth 1.0a | Free |
| Get Bookmarks | `GET /2/users/:id/bookmarks` | OAuth 1.0a | ~$0.005 |
| Bookmark Tweet | `POST /2/users/:id/bookmarks` | OAuth 1.0a | Free |
| Remove Bookmark | `DELETE /2/users/:id/bookmarks/:tweet_id` | OAuth 1.0a | Free |
| Usage Stats | `GET /2/usage/tweets` | Bearer | Free |

## Tweet Fields

Request via `tweet.fields` parameter:

| Field | Description |
|-------|-------------|
| `created_at` | Tweet creation timestamp (ISO 8601) |
| `text` | Full tweet text |
| `public_metrics` | Engagement counters (see below) |
| `conversation_id` | Root tweet ID of the conversation |
| `in_reply_to_user_id` | User ID being replied to |
| `referenced_tweets` | Array of {type, id} — "replied_to", "quoted", "retweeted" |
| `author_id` | Author's user ID |

## Expansions (FREE — included in same request)

| Expansion | Returns | Use Case |
|-----------|---------|----------|
| `author_id` | User object | Get tweet author's name, handle, followers |
| `referenced_tweets.id` | Tweet object(s) | Get parent/quoted tweet content |
| `referenced_tweets.id.author_id` | User object(s) | Get authors of referenced tweets |
| `in_reply_to_user_id` | User object | Get user being replied to |

## Public Metrics (tweet)

Available in `public_metrics` when requested:

| Metric | Description | Notes |
|--------|-------------|-------|
| `retweet_count` | Number of retweets | Public |
| `reply_count` | Number of replies | Public |
| `like_count` | Number of likes | Public |
| `quote_count` | Number of quote tweets | Public |
| `bookmark_count` | Number of bookmarks | Public |
| `impression_count` | Number of views | Own tweets only (OAuth 1.0a required) |

## User Fields

Request via `user.fields` parameter:

| Field | Description |
|-------|-------------|
| `created_at` | Account creation date |
| `description` | Bio text |
| `location` | Location string |
| `public_metrics` | followers_count, following_count, tweet_count, listed_count |
| `profile_image_url` | Avatar URL |
| `url` | Profile link |
| `verified` | Blue checkmark |
| `verified_type` | "blue", "business", "government", or none |

## Rate Limits

Per-app rate limits (15-minute windows):

| Endpoint | Rate Limit |
|----------|-----------|
| User Tweets | 900 req/15min |
| User Mentions | 450 req/15min |
| Users Lookup | 300 req/15min |
| Tweet Lookup | 300 req/15min |
| Search Recent | 450 req/15min |
| Create Tweet | 200 req/15min (per user) |

tweepy's `wait_on_rate_limit=True` auto-handles 429 responses.

## Pay-Per-Use Pricing (2026)

| Operation | Cost |
|-----------|------|
| Post reads (tweets) | $0.005/request (up to 100 tweets per request) |
| User reads | $0.01/request |
| DM reads | $0.01/request |
| Post creation | Free (included in API access) |
| Bookmarking | Free (write action) |

Note: Batch lookup `GET /2/tweets?ids=id1,...id100` costs $0.005 for up to 100 tweets — not $0.005 per tweet.

## Search Operators (for reference)

Useful if combining with search endpoints:
- `from:username` — tweets by a user
- `to:username` — replies to a user
- `@username` — mentions of a user
- `conversation_id:ID` — all tweets in a thread
- `-is:retweet` — exclude retweets
- `has:links` — tweets with URLs
- `has:media` — tweets with images/video

## Auth Methods

| Method | When | Keys Needed |
|--------|------|-------------|
| OAuth 1.0a (User Context) | Own tweets, mentions, get_me, posting, bookmarks | API Key + Secret + Access Token + Secret |
| Bearer Token (App Context) | Public user lookup, public tweets, search | Bearer Token only |

OAuth 1.0a is required for `impression_count` on your own tweets and all write actions (posting, bookmarking).

## Thread Reconstruction

`conversation_id` is the key — every reply in a thread shares the same conversation_id.

**Best method (< 7 days):** `GET /2/tweets/search/recent?query=conversation_id:ID from:USERNAME`
- Returns all thread parts in one $0.005 call
- Sort by `created_at` ascending for reading order

**Fallback (older threads):** Follow `referenced_tweets` chain upward, batch IDs into `GET /2/tweets?ids=...`
