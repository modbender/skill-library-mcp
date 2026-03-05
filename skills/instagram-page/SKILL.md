---
name: instagram-page
description: "Instagram Business manager: post photos, reels, stories & get insights. Requires: powershell/pwsh. Reads ~/.config/instagram-page/credentials.json (IG_ACCESS_TOKEN, IG_USER_ID). IG_APP_SECRET for one-time setup only — delete afterward. Token expires every 60 days — refresh before expiry. Grant minimal permissions only. No data forwarded to third parties; all calls go to graph.facebook.com only."
metadata: {"openclaw":{"emoji":"[ig]","requires":{"anyBins":["powershell","pwsh"]}}}
---

# instagram-page - Universal Instagram Graph API Skill

Constructs and executes Instagram Graph API calls inline based on what the user wants. No scripts needed.

> **Requires an Instagram Business or Creator account** linked to a Facebook Page.
> Personal Instagram accounts are not supported by the Instagram Graph API.

API version: **v25.0**
Base URL: `https://graph.facebook.com/v25.0`

---

## STEP 1 - Load Credentials

Credentials are stored in `~/.config/instagram-page/credentials.json`.

```powershell
$cfg      = Get-Content "$HOME/.config/instagram-page/credentials.json" -Raw | ConvertFrom-Json
$token    = $cfg.IG_ACCESS_TOKEN
$igUserId = $cfg.IG_USER_ID
```

**If the file does not exist**, guide setup. Required fields:

| Field | Purpose |
|---|---|
| `IG_ACCESS_TOKEN` | Long-lived User access token - used for all API calls |
| `IG_USER_ID` | Instagram-scoped Business/Creator User ID (numeric) |
| `IG_APP_ID` | Meta App ID - only needed during token exchange |
| `IG_APP_SECRET` | Meta App Secret - only needed during token exchange |

**Prerequisites:**
1. Instagram account must be a **Business** or **Creator** account
2. The Instagram account must be **linked to a Facebook Page**
3. A Meta App with `instagram_basic`, `instagram_content_publish`, `instagram_manage_comments`, `instagram_manage_insights` permissions

**One-time token exchange setup:**
```powershell
# Provide: $appId, $appSecret, $shortToken (from Graph API Explorer with IG permissions), $fbPageId
# 1. Exchange short-lived token for long-lived user token (valid 60 days)
$r1 = Invoke-RestMethod "https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=$appId&client_secret=$appSecret&fb_exchange_token=$shortToken"
$longToken = $r1.access_token
# 2. Get Instagram Business Account ID linked to your Facebook Page
$r2 = Invoke-RestMethod "https://graph.facebook.com/v25.0/$fbPageId?fields=instagram_business_account&access_token=$longToken"
$igUserId = $r2.instagram_business_account.id
# 3. Save - only these four fields
@{
    IG_USER_ID      = $igUserId
    IG_ACCESS_TOKEN = $longToken
    IG_APP_ID       = $appId
    IG_APP_SECRET   = $appSecret
} | ConvertTo-Json | Set-Content "$HOME/.config/instagram-page/credentials.json" -Encoding UTF8
```

**Restrict file permissions immediately after saving:**
```powershell
# Windows
icacls "$HOME/.config/instagram-page/credentials.json" /inheritance:r /grant:r "$($env:USERNAME):(R,W)"
# macOS / Linux
# chmod 600 ~/.config/instagram-page/credentials.json
```

**Refresh token before it expires (every ~50 days):**
```powershell
$r = Invoke-RestMethod "https://graph.facebook.com/oauth/access_token?grant_type=ig_refresh_token&access_token=$token"
$cfg.IG_ACCESS_TOKEN = $r.access_token
$cfg | ConvertTo-Json | Set-Content "$HOME/.config/instagram-page/credentials.json" -Encoding UTF8
```

> **Delete IG_APP_SECRET** from credentials.json after setup - it is not needed for API calls.
> Never commit this file to version control. It contains long-lived secrets.
> This skill makes no external calls other than to graph.facebook.com. No data is forwarded to third parties.

---

## STEP 2 - Figure Out the API Call

Instagram publishing uses a **two-step flow** for most media types:
1. **Create a media container** - uploads/registers the media, returns a `creation_id`
2. **Publish the container** - makes it live on Instagram

### Common Endpoints

| What user wants | Method | Endpoint |
|---|---|---|
| Post single photo | POST x2 | Step 1: `/$igUserId/media` Step 2: `/$igUserId/media_publish` |
| Post reel (video) | POST x2 | Step 1: `/$igUserId/media` (media_type=REELS) Step 2: `/$igUserId/media_publish` |
| Post story | POST x2 | Step 1: `/$igUserId/media` (media_type=STORIES) Step 2: `/$igUserId/media_publish` |
| Post carousel | POST x3+ | Step 1: item containers Step 2: carousel container Step 3: publish |
| Get recent media | GET | `/$igUserId/media?fields=id,caption,media_type,timestamp,like_count,comments_count` |
| Get account info | GET | `/$igUserId?fields=username,name,biography,followers_count,media_count` |
| Get comments | GET | `/{media-id}/comments?fields=text,username,timestamp` |
| Reply to comment | POST | `/{comment-id}/replies` body: `message` |
| Delete comment | DELETE | `/{comment-id}` |
| Hide/show comment | POST | `/{comment-id}` body: `hide=true/false` |
| Get media insights | GET | `/{media-id}/insights?metric=impressions,reach,likes,comments,shares,saved` |
| Get account insights | GET | `/$igUserId/insights?metric=impressions,reach,follower_count&period=day` |
| Get hashtag ID | GET | `ig/hashtags?user_id=$igUserId&q=hashtag` |
| Search hashtag media | GET | `/{hashtag-id}/top_media?user_id=$igUserId&fields=id,caption,media_type` |
| Get tagged media | GET | `/$igUserId/tags?fields=caption,media_url,timestamp` |

### API Call Patterns

**GET:**
```powershell
$result = Invoke-RestMethod -Uri "https://graph.facebook.com/v25.0/ENDPOINT?access_token=$token" -ErrorAction Stop
```

**POST (form body):**
```powershell
$result = Invoke-RestMethod -Uri "https://graph.facebook.com/v25.0/ENDPOINT" -Method POST `
    -Body @{ field1="value1"; field2="value2"; access_token=$token } -ErrorAction Stop
```

**DELETE:**
```powershell
$result = Invoke-RestMethod -Uri "https://graph.facebook.com/v25.0/{id}?access_token=$token" -Method DELETE -ErrorAction Stop
```

### Publishing Patterns

**Single photo post:**
```powershell
# image_url must be publicly accessible
$container = Invoke-RestMethod -Uri "https://graph.facebook.com/v25.0/$igUserId/media" -Method POST `
    -Body @{ image_url=$imageUrl; caption=$caption; access_token=$token } -ErrorAction Stop
$post = Invoke-RestMethod -Uri "https://graph.facebook.com/v25.0/$igUserId/media_publish" -Method POST `
    -Body @{ creation_id=$container.id; access_token=$token } -ErrorAction Stop
Write-Host "Published post ID: $($post.id)"
```

**Reel post (video):**
```powershell
# video_url must be publicly accessible MP4 (H.264, AAC audio, max 1GB, max 60s for feed)
$container = Invoke-RestMethod -Uri "https://graph.facebook.com/v25.0/$igUserId/media" -Method POST `
    -Body @{ media_type="REELS"; video_url=$videoUrl; caption=$caption; share_to_feed="true"; access_token=$token } -ErrorAction Stop
# Poll for processing status - video upload is async
do {
    Start-Sleep -Seconds 5
    $status = Invoke-RestMethod "https://graph.facebook.com/v25.0/$($container.id)?fields=status_code&access_token=$token"
} while ($status.status_code -eq "IN_PROGRESS")
if ($status.status_code -ne "FINISHED") { throw "Video processing failed: $($status.status_code)" }
$post = Invoke-RestMethod -Uri "https://graph.facebook.com/v25.0/$igUserId/media_publish" -Method POST `
    -Body @{ creation_id=$container.id; access_token=$token } -ErrorAction Stop
Write-Host "Published reel ID: $($post.id)"
```

**Carousel post (2-10 images/videos):**
```powershell
# Create item containers for each media URL
$itemIds = @()
foreach ($url in $mediaUrls) {
    $item = Invoke-RestMethod -Uri "https://graph.facebook.com/v25.0/$igUserId/media" -Method POST `
        -Body @{ image_url=$url; is_carousel_item="true"; access_token=$token } -ErrorAction Stop
    $itemIds += $item.id
}
# Create carousel container
$carousel = Invoke-RestMethod -Uri "https://graph.facebook.com/v25.0/$igUserId/media" -Method POST `
    -Body @{ media_type="CAROUSEL"; children=($itemIds -join ","); caption=$caption; access_token=$token } -ErrorAction Stop
# Publish
$post = Invoke-RestMethod -Uri "https://graph.facebook.com/v25.0/$igUserId/media_publish" -Method POST `
    -Body @{ creation_id=$carousel.id; access_token=$token } -ErrorAction Stop
Write-Host "Published carousel ID: $($post.id)"
```

**Story:**
```powershell
$container = Invoke-RestMethod -Uri "https://graph.facebook.com/v25.0/$igUserId/media" -Method POST `
    -Body @{ media_type="STORIES"; image_url=$imageUrl; access_token=$token } -ErrorAction Stop
$post = Invoke-RestMethod -Uri "https://graph.facebook.com/v25.0/$igUserId/media_publish" -Method POST `
    -Body @{ creation_id=$container.id; access_token=$token } -ErrorAction Stop
Write-Host "Published story ID: $($post.id)"
```

> **Image/video URLs must be publicly accessible** - local files are not accepted by the API.
> Upload to a public server or CDN before calling. Instagram limits ~50 API-published posts per 24h.

---

## STEP 3 - Handle Errors

```powershell
try {
    # ... API call ...
} catch {
    $err     = $_.ErrorDetails.Message | ConvertFrom-Json -ErrorAction SilentlyContinue
    $code    = $err.error.code
    $subcode = $err.error.error_subcode
    $msg     = $err.error.message
    Write-Host "Error $code/$subcode : $msg"
}
```

| Code | Subcode | Meaning | Fix |
|---|---|---|---|
| 100 | - | Invalid parameter | Check parameter values; image/video URL must be public |
| 102 | - | Session expired | Refresh token - run the refresh snippet in STEP 1 |
| 190 | 460 | Token expired (60 days) | Refresh token - run the refresh snippet in STEP 1 |
| 190 | 467 | Invalid token | Re-run full setup to get a new token |
| 200 | - | Permission denied | Add the missing permission to your Meta App and regenerate token |
| 10 | - | Permission denied (IG scope) | Add permission listed in error.message; re-run setup |
| 24 | - | No linked IG Business account | Link Instagram account to your Facebook Page in Instagram settings |
| 32 | - | Page request limit reached | Wait and retry; hourly rate limit hit |
| 368 | - | Temporarily blocked | Wait and retry; account may be temporarily restricted |
| 9007 | - | Publishing limit reached | Instagram limits ~50 API-published posts per 24h |
| 2207026 | - | Video format invalid | MP4 required; H.264 video, AAC audio, max 1GB, 60s for feed reels |

### Permissions Reference

| Permission | Required for |
|---|---|
| `instagram_basic` | Read account info, media list |
| `instagram_content_publish` | Create and publish posts, reels, stories, carousels |
| `instagram_manage_comments` | Read, reply to, hide, delete comments |
| `instagram_manage_insights` | Access account and media insights |
| `pages_show_list` | List Facebook Pages (needed during IG account lookup) |
| `pages_read_engagement` | Read Facebook Page linked to Instagram account |

**If a permission is missing:**
1. Go to [Meta for Developers](https://developers.facebook.com/apps/)
2. Select your app -> Permissions and Features
3. Add the required permission
4. Regenerate token via [Graph API Explorer](https://developers.facebook.com/tools/explorer/) with the permission checked
5. Re-run setup with the new token

---

## AGENT RULES

- **Always load credentials first.** If missing or incomplete, guide setup.
- **Only use `IG_ACCESS_TOKEN` and `IG_USER_ID`** for API calls. `IG_APP_ID` and `IG_APP_SECRET` are for token exchange only.
- **Delete `IG_APP_SECRET`** from credentials.json after token exchange - it is not needed for API calls.
- **Token expiry:** `IG_ACCESS_TOKEN` expires every 60 days. Remind the user to refresh before expiry using the refresh snippet in STEP 1. Rotate immediately if the host is ever compromised.
- **Two-step publishing:** always create a container first, then publish. Never try to publish in a single API call.
- **Public URLs only:** image/video URLs must be publicly accessible. If the user provides a local file path, tell them to upload it to a public server or CDN first.
- **Reel processing:** poll `status_code` until `FINISHED` before publishing - video processing is async and can take minutes.
- **Least-privilege:** only request the permissions the use case needs.
- **All API calls go to `graph.facebook.com` only.** No external forwarding, no third-party services.
- **Construct API calls inline** from user intent - do not look for script files.
- **On any error:** parse `error.code` + `error.error_subcode`, map to the table above, tell the user exactly what to do.
- **If a permission is missing:** name it, link to Meta for Developers, say to re-run setup.
- **Business/Creator only:** if the user has a personal Instagram account, tell them to convert it to Business or Creator in Instagram settings first - personal accounts are not supported by the Instagram Graph API.