# WRITE Endpoints V2 (POST/PATCH, login_cookies + proxy required)

All v2 write endpoints require:
1. **login_cookies** -- from `POST /twitter/user_login_v2`
2. **proxy** -- residential proxy URL: `http://user:pass@host:port`

## Authentication

**Login V2** `POST /twitter/user_login_v2` (300 credits)
```bash
curl -s -X POST "https://api.twitterapi.io/twitter/user_login_v2" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "USERNAME",
    "email": "EMAIL",
    "password": "PASSWORD",
    "proxy": "http://user:pass@host:port",
    "totp_secret": "2FA_SECRET_16CHAR"
  }'
```
Response: `{ "login_cookie": "...", "status": "success", "msg": "..." }`

Important:
- `totp_secret` must be a **16-character string** (not numbers). Without it, login may succeed but the cookie will be faulty, causing 400 errors on all v2 action endpoints.
- Cookie stays valid indefinitely with residential proxies + good-standing account.
- Response field is `login_cookie` (singular) but use `login_cookies` (plural) in action requests.

## Tweet Actions

**Create Tweet** `POST /twitter/create_tweet_v2` (300 credits)
```bash
curl -s -X POST "https://api.twitterapi.io/twitter/create_tweet_v2" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "login_cookies": "COOKIE",
    "tweet_text": "Hello world!",
    "proxy": "http://user:pass@host:port"
  }'
```
Optional: `reply_to_tweet_id`, `attachment_url` (quote tweet URL), `community_id`, `is_note_tweet` (Premium only, >280 chars), `media_ids` (array)
Response: `{ "tweet_id": "1234...", "status": "success", "msg": "..." }`

**Delete Tweet** `POST /twitter/delete_tweet_v2` (200 credits)
```bash
curl -s -X POST "https://api.twitterapi.io/twitter/delete_tweet_v2" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "login_cookies": "COOKIE", "tweet_id": "ID", "proxy": "PROXY" }'
```

**Like Tweet** `POST /twitter/like_tweet_v2` (200 credits)
```bash
curl -s -X POST "https://api.twitterapi.io/twitter/like_tweet_v2" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "login_cookies": "COOKIE", "tweet_id": "ID", "proxy": "PROXY" }'
```

**Unlike Tweet** `POST /twitter/unlike_tweet_v2` (200 credits)
```bash
curl -s -X POST "https://api.twitterapi.io/twitter/unlike_tweet_v2" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "login_cookies": "COOKIE", "tweet_id": "ID", "proxy": "PROXY" }'
```

**Retweet** `POST /twitter/retweet_tweet_v2` (200 credits)
```bash
curl -s -X POST "https://api.twitterapi.io/twitter/retweet_tweet_v2" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "login_cookies": "COOKIE", "tweet_id": "ID", "proxy": "PROXY" }'
```

## User Actions

**Follow User** `POST /twitter/follow_user_v2` (200 credits)
```bash
curl -s -X POST "https://api.twitterapi.io/twitter/follow_user_v2" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "login_cookies": "COOKIE", "user_id": "NUMERIC_USER_ID", "proxy": "PROXY" }'
```
Needs numeric `user_id`. Get from `GET /twitter/user/info` first.

**Unfollow User** `POST /twitter/unfollow_user_v2` (200 credits)
```bash
curl -s -X POST "https://api.twitterapi.io/twitter/unfollow_user_v2" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "login_cookies": "COOKIE", "user_id": "NUMERIC_USER_ID", "proxy": "PROXY" }'
```

## DM Actions

**Send DM** `POST /twitter/send_dm_to_user` (300 credits)
```bash
curl -s -X POST "https://api.twitterapi.io/twitter/send_dm_to_user" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "login_cookies": "COOKIE", "receiver_id": "USER_ID", "text": "Hello!", "proxy": "PROXY" }'
```
Note: Can only DM users who have DMs enabled. May fail intermittently -- retry on failure.

## Media

**Upload Media** `POST /twitter/upload_media_v2` (300 credits) -- **multipart/form-data**, not JSON!
```bash
curl -s -X POST "https://api.twitterapi.io/twitter/upload_media_v2" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY" \
  -F "file=@/path/to/image.jpg" \
  -F "login_cookies=COOKIE" \
  -F "proxy=PROXY"
```
Optional: `is_long_video` (boolean, Premium only -- videos >2:20)
Returns: `{ "media_id": "...", "status": "success" }` -- use in `create_tweet_v2`'s `media_ids` array.

## Profile Updates (PATCH)

**Update Avatar** `PATCH /twitter/update_avatar_v2` (300 credits)
```bash
curl -s -X PATCH "https://api.twitterapi.io/twitter/update_avatar_v2" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "login_cookies": "COOKIE", "image_url": "https://example.com/avatar.jpg", "proxy": "PROXY" }'
```
Image: JPG/PNG, 400x400px recommended, max 700KB.

**Update Banner** `PATCH /twitter/update_banner_v2` (300 credits)
```bash
curl -s -X PATCH "https://api.twitterapi.io/twitter/update_banner_v2" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "login_cookies": "COOKIE", "image_url": "https://example.com/banner.jpg", "proxy": "PROXY" }'
```
Image: JPG/PNG, 1500x500px recommended, max 2MB.

**Update Profile** `PATCH /twitter/update_profile_v2` (300 credits)
```bash
curl -s -X PATCH "https://api.twitterapi.io/twitter/update_profile_v2" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "login_cookies": "COOKIE",
    "name": "Display Name",
    "description": "Bio text",
    "location": "City",
    "proxy": "PROXY"
  }'
```

## Community Actions (POST, v2)

**Create Community** `POST /twitter/create_community_v2` (300 credits)
```bash
curl -s -X POST "https://api.twitterapi.io/twitter/create_community_v2" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY" -H "Content-Type: application/json" \
  -d '{ "login_cookies": "COOKIE", "name": "My Community", "proxy": "PROXY" }'
```

**Join Community** `POST /twitter/join_community_v2` (300 credits)
**Leave Community** `POST /twitter/leave_community_v2` (300 credits)
**Delete Community** `POST /twitter/delete_community_v2` (300 credits)
All take: `{ "login_cookies": "COOKIE", "community_id": "ID", "proxy": "PROXY" }`
