# Deprecated V1 Endpoints (avoid -- will be removed)

| V1 Endpoint | Path | Use Instead |
|-------------|------|-------------|
| Login Step 1 | `POST /twitter/login_by_email_or_username` | `user_login_v2` |
| Login Step 2 | `POST /twitter/login_by_2fa` | `user_login_v2` |
| Create Tweet | `POST /twitter/create_tweet` | `create_tweet_v2` |
| Like Tweet | `POST /twitter/like_tweet` | `like_tweet_v2` |
| Retweet | `POST /twitter/retweet_tweet` | `retweet_tweet_v2` |
| Upload Image | `POST /twitter/upload_image` | `upload_media_v2` |
