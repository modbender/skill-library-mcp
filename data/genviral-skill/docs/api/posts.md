# Post Commands

## create-post
Create a post (video OR slideshow) targeting one or more accounts. This is the core posting command.

**Video post:**

```bash
genviral.sh create-post \
  --caption "Your caption with #hashtags" \
  --media-type video \
  --media-url "https://cdn.genviral.com/your-video.mp4" \
  --accounts "account_id_1,account_id_2" \
  --scheduled-at "2025-03-01T15:00:00Z"
```

**Slideshow post:**

```bash
genviral.sh create-post \
  --caption "Your caption" \
  --media-type slideshow \
  --media-urls "url1,url2,url3,url4,url5,url6" \
  --accounts "account_id_1" \
  --music-url "https://www.tiktok.com/@user/video/1234567890"
```

**TikTok-specific settings** (only when ALL accounts are TikTok BYO):

```bash
genviral.sh create-post \
  --caption "Caption" \
  --media-type slideshow \
  --media-urls "url1,url2,url3,url4,url5,url6" \
  --accounts "tiktok_account_id" \
  --tiktok-title "Optional title" \
  --tiktok-description "Optional description" \
  --tiktok-post-mode "MEDIA_UPLOAD" \
  --tiktok-privacy "SELF_ONLY" \
  --tiktok-disable-comment \
  --tiktok-disable-duet \
  --tiktok-disable-stitch \
  --auto-add-music true \
  --is-commercial false \
  --is-branded-content false \
  --user-consent true \
  --is-your-brand false
```

Boolean TikTok toggles support both forms:
- `--tiktok-disable-comment` (sets `true`)
- `--tiktok-disable-comment false` (explicit false)

Same behavior applies to: `--tiktok-disable-duet`, `--tiktok-disable-stitch`, `--auto-add-music`, `--is-commercial`, `--is-branded-content`, `--user-consent`, `--is-your-brand`.

TikTok `post_mode` options:
- `DIRECT_POST` - publish immediately (default)
- `MEDIA_UPLOAD` - save to TikTok drafts inbox (only supported for slideshow media)

TikTok `privacy_level` options:
- `PUBLIC_TO_EVERYONE` (default)
- `MUTUAL_FOLLOW_FRIENDS`
- `FOLLOWER_OF_CREATOR`
- `SELF_ONLY` (draft mode)

**Pinterest-specific settings** (when at least one account is Pinterest):

```bash
genviral.sh create-post \
  --caption "10 minimalist desk setups" \
  --media-type slideshow \
  --media-urls "url1,url2,url3" \
  --accounts "pinterest_account_id" \
  --pinterest-board-id "BOARD_ID" \
  --pinterest-title "Pin title (max 100 chars)" \
  --pinterest-link "https://yourblog.com/article" \
  --pinterest-tags "desk setup,minimalism,home office"
```

Pinterest options:
- `--pinterest-board-id` - Target board ID (max 128 chars). Omit to use account defaults.
- `--pinterest-title` - Pin title override (max 100 chars)
- `--pinterest-link` - Destination URL on the pin
- `--pinterest-tags` - Comma-separated topic tags (up to 30, multi-word supported)

**Important:** TikTok and Pinterest settings are mutually exclusive in one request. Use only one platform-specific block per post.

**Scheduling:**

- Omit `--scheduled-at` or set it within 30 seconds of now: post is queued for immediate publish (status: `pending`)
- Provide future ISO timestamp: post is scheduled (status: `scheduled`)
- `--scheduled-at` must be ISO 8601 with timezone offset (example: `2026-02-14T19:47:00Z`)

**Draft timing note:** For TikTok draft uploads (`post_mode=MEDIA_UPLOAD`), `pending` is normal. It means the post is queued and waiting for the posting worker (typically every ~5 minutes). `pending` can persist for a few minutes before the account state flips to `posted`. Check `accounts.states[].last_attempted_at` and `published_at` before concluding it failed.

**Draft cap guardrail:** TikTok may reject draft uploads with `spam_risk_too_many_pending_share` when you exceed ~5 pending-share uploads in a rolling 24h window. The CLI now enforces a guardrail:
- Warn at 4 uploads in last 24h per account
- Block at 5+ by default
- Override only if you really need to test: `--force-media-upload-cap` (supported in `create-post` and `post-draft`)

`--music-url` must point to a TikTok URL.

**Multi-account posting:**

You can target up to 10 accounts per post. Mix TikTok, Instagram, etc. Music is only supported when ALL accounts support it (currently TikTok only). TikTok-specific settings only work when ALL accounts are TikTok BYO.

---

## update-post
Update an existing post (only editable if status is draft, pending, scheduled, retry, or failed).

```bash
genviral.sh update-post \
  --id POST_ID \
  --caption "Updated caption" \
  --media-type video \
  --media-url "https://new-video.mp4" \
  --accounts "new_account_id_1,new_account_id_2" \
  --scheduled-at "2025-03-15T18:00:00Z"
```

Clear operations:
- Remove music: `--music-url null`
- Clear scheduled time: `--clear-scheduled-at`
- Clear all TikTok settings: `--clear-tiktok`
- Clear all Pinterest settings: `--clear-pinterest`

Pinterest update example:
```bash
genviral.sh update-post \
  --id POST_ID \
  --pinterest-board-id "NEW_BOARD_ID" \
  --pinterest-title "Updated pin title" \
  --pinterest-link "https://yourblog.com/new-article" \
  --pinterest-tags "new tag 1,new tag 2"
```

Validation notes:
- `--scheduled-at` must be ISO 8601 with timezone offset
- `--music-url` must be a TikTok URL (unless using `null` to clear)
- TikTok/Pinterest boolean toggles support both flag form and explicit values
- TikTok and Pinterest settings are mutually exclusive

---

## retry-posts
Retry failed or partial posts.

```bash
genviral.sh retry-posts --post-ids "post_id_1,post_id_2"
genviral.sh retry-posts --post-ids "post_id_1" --account-ids "account_id_1"
```

Limits:
- `post_ids`: 1-20 IDs
- `account_ids`: 1-10 IDs

---

## list-posts
List posts with optional filters.

```bash
genviral.sh list-posts
genviral.sh list-posts --status scheduled --limit 20
genviral.sh list-posts --since "2025-02-01T00:00:00Z" --until "2025-02-28T23:59:59Z"
genviral.sh list-posts --json
```

`--since` and `--until` must be ISO 8601 datetimes with timezone offset.

Status filters: `draft`, `pending`, `scheduled`, `posted`, `failed`, `partial`, `retry`

---

## get-post
Get details for a specific post.

```bash
genviral.sh get-post --id POST_ID
```

---

## delete-posts (alias: `delete-post`)
Bulk delete posts by IDs.

```bash
genviral.sh delete-posts --ids "post_id_1,post_id_2,post_id_3"
genviral.sh delete-posts --post-ids "post_id_1,post_id_2,post_id_3"
genviral.sh delete-post --ids "post_id_1,post_id_2"
```

Limit: up to 50 IDs per request.

Returns structured delete results including:
- `deletedIds`
- `blockedStatuses` (posts that can't be deleted due to status)
- `skipped`
- `errors`
