---
name: tiktok-page
description: "TikTok manager: post videos, list content & check account stats. Requires: powershell/pwsh. Reads ~/.config/tiktok-page/credentials.json (TIKTOK_ACCESS_TOKEN, TIKTOK_REFRESH_TOKEN, TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_OPEN_ID). Tokens expire every 24h — auto-refresh via TIKTOK_REFRESH_TOKEN. Grant minimal permissions only. Rotate immediately if host is compromised. No data forwarded; all calls go to open.tiktokapis.com only."
metadata: {"openclaw":{"emoji":"[tt]","requires":{"anyBins":["powershell","pwsh"]}}}
---

# tiktok-page — Universal TikTok API Skill

Constructs and executes TikTok API calls inline based on what the user wants. No scripts needed.

API base URL: `https://open.tiktokapis.com/v2`

---

## STEP 1 - Load Credentials

Credentials are stored in `~/.config/tiktok-page/credentials.json`.

```powershell
$cfg          = Get-Content "$HOME/.config/tiktok-page/credentials.json" -Raw | ConvertFrom-Json
$accessToken  = $cfg.TIKTOK_ACCESS_TOKEN
$refreshToken = $cfg.TIKTOK_REFRESH_TOKEN
$clientKey    = $cfg.TIKTOK_CLIENT_KEY
$clientSecret = $cfg.TIKTOK_CLIENT_SECRET
$openId       = $cfg.TIKTOK_OPEN_ID
```

If the file does not exist, guide setup:

| Field | Purpose |
|---|---|
| TIKTOK_ACCESS_TOKEN | OAuth2 access token — used for all API calls |
| TIKTOK_REFRESH_TOKEN | Used to refresh access token when expired |
| TIKTOK_CLIENT_KEY | App Client Key from TikTok Developer Portal |
| TIKTOK_CLIENT_SECRET | App Client Secret — for token refresh only |
| TIKTOK_OPEN_ID | TikTok user open_id returned during OAuth |

**One-time OAuth2 setup:**
```
1. Go to https://developers.tiktok.com — create or select your app
2. Add redirect URI (e.g. https://localhost or your callback URL)
3. Note your Client Key and Client Secret
4. Direct user to:
   https://www.tiktok.com/v2/auth/authorize/?client_key=CLIENT_KEY&redirect_uri=REDIRECT_URI&response_type=code&scope=user.info.basic,video.list,video.publish,video.upload,comment.list&state=random
5. After redirect, copy the code param from the callback URL
```

```powershell
# Exchange auth code for tokens
$clientKey   = "<your-client-key>"
$clientSecret = "<your-client-secret>"
$code        = "<auth-code-from-redirect>"
$redirectUri = "<your-redirect-uri>"

$body = "client_key=$clientKey&client_secret=$clientSecret&code=$code&grant_type=authorization_code&redirect_uri=$redirectUri"
$r = Invoke-RestMethod "https://open.tiktokapis.com/v2/oauth/token/" -Method POST `
    -Headers @{ "Content-Type" = "application/x-www-form-urlencoded" } -Body $body -ErrorAction Stop

New-Item -ItemType Directory -Force -Path "$HOME/.config/tiktok-page" | Out-Null
@{
    TIKTOK_ACCESS_TOKEN  = $r.access_token
    TIKTOK_REFRESH_TOKEN = $r.refresh_token
    TIKTOK_CLIENT_KEY    = $clientKey
    TIKTOK_CLIENT_SECRET = $clientSecret
    TIKTOK_OPEN_ID       = $r.open_id
} | ConvertTo-Json | Set-Content "$HOME/.config/tiktok-page/credentials.json" -Encoding UTF8
```

**Restrict file permissions immediately after saving:**
```powershell
# Windows
icacls "$HOME/.config/tiktok-page/credentials.json" /inheritance:r /grant:r "$($env:USERNAME):(R,W)"
# macOS / Linux
# chmod 600 ~/.config/tiktok-page/credentials.json
```

> Never commit this file to version control. It contains long-lived secrets.
> This skill makes no external calls other than to open.tiktokapis.com. No data is forwarded to third parties.

---

## STEP 2 - Token Refresh

TikTok access tokens expire after 24 hours. Refresh before making calls if needed:

```powershell
$cfg = Get-Content "$HOME/.config/tiktok-page/credentials.json" -Raw | ConvertFrom-Json
$body = "client_key=$($cfg.TIKTOK_CLIENT_KEY)&client_secret=$($cfg.TIKTOK_CLIENT_SECRET)&grant_type=refresh_token&refresh_token=$($cfg.TIKTOK_REFRESH_TOKEN)"
$r = Invoke-RestMethod "https://open.tiktokapis.com/v2/oauth/token/" -Method POST `
    -Headers @{ "Content-Type" = "application/x-www-form-urlencoded" } -Body $body -ErrorAction Stop

$cfg.TIKTOK_ACCESS_TOKEN  = $r.access_token
$cfg.TIKTOK_REFRESH_TOKEN = $r.refresh_token
$cfg | ConvertTo-Json | Set-Content "$HOME/.config/tiktok-page/credentials.json" -Encoding UTF8
Write-Host "Tokens refreshed."
```

---

## STEP 3 - Figure Out the API Call

### Common Endpoints

| What user wants | Method | Endpoint |
|---|---|---|
| Get account info | POST | /user/info/ |
| List own videos | POST | /video/list/ |
| Get video detail | POST | /video/query/ |
| Get comments | GET | /video/comment/list/?video_id={id} |
| Publish video from URL | POST | /post/publish/video/init/ with PULL_FROM_URL |
| Upload video from file | POST then PUT | /post/publish/video/init/ then upload_url |
| Check publish status | GET | /post/publish/status/fetch/?publish_id={id} |

### API Call Patterns

**GET account info:**
```powershell
$cfg = Get-Content "$HOME/.config/tiktok-page/credentials.json" -Raw | ConvertFrom-Json
$headers = @{ "Authorization" = "Bearer $($cfg.TIKTOK_ACCESS_TOKEN)"; "Content-Type" = "application/json; charset=UTF-8" }
$body    = @{ fields = "display_name,avatar_url,follower_count,following_count,likes_count,video_count" } | ConvertTo-Json
$result  = Invoke-RestMethod "https://open.tiktokapis.com/v2/user/info/" -Method POST -Headers $headers -Body $body -ErrorAction Stop
$result.data.user
```

**List videos:**
```powershell
$cfg = Get-Content "$HOME/.config/tiktok-page/credentials.json" -Raw | ConvertFrom-Json
$headers = @{ "Authorization" = "Bearer $($cfg.TIKTOK_ACCESS_TOKEN)"; "Content-Type" = "application/json; charset=UTF-8" }
$body    = @{ max_count = 20; fields = "id,title,create_time,cover_image_url,share_url,view_count,like_count,comment_count,share_count" } | ConvertTo-Json
$result  = Invoke-RestMethod "https://open.tiktokapis.com/v2/video/list/" -Method POST -Headers $headers -Body $body -ErrorAction Stop
$result.data.videos | Format-Table id, title, view_count, like_count, create_time
```

**Get video detail by ID:**
```powershell
$cfg = Get-Content "$HOME/.config/tiktok-page/credentials.json" -Raw | ConvertFrom-Json
$headers = @{ "Authorization" = "Bearer $($cfg.TIKTOK_ACCESS_TOKEN)"; "Content-Type" = "application/json; charset=UTF-8" }
$body    = @{ filters = @{ video_ids = @("<video_id>") }; fields = "id,title,view_count,like_count,comment_count,share_count,embed_html" } | ConvertTo-Json -Depth 4
$result  = Invoke-RestMethod "https://open.tiktokapis.com/v2/video/query/" -Method POST -Headers $headers -Body $body -ErrorAction Stop
$result.data.videos
```

**Publish video from URL:**
```powershell
$cfg = Get-Content "$HOME/.config/tiktok-page/credentials.json" -Raw | ConvertFrom-Json
$headers = @{ "Authorization" = "Bearer $($cfg.TIKTOK_ACCESS_TOKEN)"; "Content-Type" = "application/json; charset=UTF-8" }
$body = @{
    post_info = @{
        title           = "Your video caption"
        privacy_level   = "PUBLIC_TO_EVERYONE"
        disable_duet    = $false
        disable_stitch  = $false
        disable_comment = $false
    }
    source_info = @{
        source            = "PULL_FROM_URL"
        video_url         = "https://example.com/video.mp4"
        video_size        = 12345678
        chunk_size        = 10000000
        total_chunk_count = 1
    }
} | ConvertTo-Json -Depth 5
$result = Invoke-RestMethod "https://open.tiktokapis.com/v2/post/publish/video/init/" -Method POST -Headers $headers -Body $body -ErrorAction Stop
Write-Host "Publish ID: $($result.data.publish_id)"
```

**Upload video from local file:**
```powershell
$cfg = Get-Content "$HOME/.config/tiktok-page/credentials.json" -Raw | ConvertFrom-Json
$headers = @{ "Authorization" = "Bearer $($cfg.TIKTOK_ACCESS_TOKEN)"; "Content-Type" = "application/json; charset=UTF-8" }
$filePath  = "C:\path\to\video.mp4"
$fileSize  = (Get-Item $filePath).Length
$chunkSize = 10MB

$initBody = @{
    post_info = @{
        title           = "Your caption"
        privacy_level   = "PUBLIC_TO_EVERYONE"
        disable_duet    = $false
        disable_stitch  = $false
        disable_comment = $false
    }
    source_info = @{
        source            = "FILE_UPLOAD"
        video_size        = $fileSize
        chunk_size        = $chunkSize
        total_chunk_count = [math]::Ceiling($fileSize / $chunkSize)
    }
} | ConvertTo-Json -Depth 5
$initResult = Invoke-RestMethod "https://open.tiktokapis.com/v2/post/publish/video/init/" -Method POST -Headers $headers -Body $initBody -ErrorAction Stop
$uploadUrl  = $initResult.data.upload_url
$publishId  = $initResult.data.publish_id

# Upload chunks
$fileStream = [System.IO.File]::OpenRead($filePath)
$buffer     = New-Object byte[] $chunkSize
$chunkIndex = 0
while (($bytesRead = $fileStream.Read($buffer, 0, $chunkSize)) -gt 0) {
    $chunk      = $buffer[0..($bytesRead - 1)]
    $rangeStart = $chunkIndex * $chunkSize
    $rangeEnd   = $rangeStart + $bytesRead - 1
    Invoke-RestMethod $uploadUrl -Method PUT -Headers @{
        "Content-Range" = "bytes $rangeStart-$rangeEnd/$fileSize"
        "Content-Type"  = "video/mp4"
    } -Body $chunk | Out-Null
    $chunkIndex++
}
$fileStream.Close()
Write-Host "Upload complete. Publish ID: $publishId"
```

**Check publish status:**
```powershell
$cfg = Get-Content "$HOME/.config/tiktok-page/credentials.json" -Raw | ConvertFrom-Json
$headers = @{ "Authorization" = "Bearer $($cfg.TIKTOK_ACCESS_TOKEN)" }
$result  = Invoke-RestMethod "https://open.tiktokapis.com/v2/post/publish/status/fetch/?publish_id=<publish_id>" -Headers $headers -ErrorAction Stop
Write-Host "Status: $($result.data.status)"
```

**Get comments:**
```powershell
$cfg = Get-Content "$HOME/.config/tiktok-page/credentials.json" -Raw | ConvertFrom-Json
$headers = @{ "Authorization" = "Bearer $($cfg.TIKTOK_ACCESS_TOKEN)" }
$result  = Invoke-RestMethod "https://open.tiktokapis.com/v2/video/comment/list/?video_id=<video_id>&fields=id,text,create_time,like_count" -Headers $headers -ErrorAction Stop
$result.data.comments | Format-Table id, text, like_count, create_time
```

---

## STEP 4 - Handle Errors

```powershell
try {
    # ... API call ...
} catch {
    $err     = $_.ErrorDetails.Message | ConvertFrom-Json -ErrorAction SilentlyContinue
    $code    = $err.error.code
    $message = $err.error.message
    Write-Host "TikTok API Error $code: $message"
}
```

| Code | Meaning | Fix |
|---|---|---|
| access_token_invalid | Token revoked or invalid | Re-run OAuth2 setup in STEP 1 |
| access_token_expired | Access token expired (24h TTL) | Run token refresh in STEP 2 |
| spam_risk_too_many_requests | Rate limited | Wait and retry; reduce request frequency |
| scope_not_authorized | Missing OAuth scope | Re-authorize with the required scope (see below) |
| video_not_found | Video ID invalid or deleted | Verify the video ID |
| privacy_level_not_allowed | Privacy setting not permitted | Use PUBLIC_TO_EVERYONE or SELF_ONLY |
| file_size_check_failed | Video file too large | Must be under 4GB and 60 minutes |
| duration_check_failed | Video too short or too long | Min 1 second, max 10 minutes (60 min for some accounts) |

### Scopes Reference

| Scope | Required for |
|---|---|
| user.info.basic | Get account info |
| video.list | List own videos |
| video.publish | Publish videos |
| video.upload | Upload video chunks |
| comment.list | Read comments on own videos |
| comment.list.manage | Hide or delete comments |

If a scope is missing:
1. Go to https://developers.tiktok.com — select your app
2. Under Products, add the required scope
3. Re-authorize (repeat STEP 1 OAuth2) with the new scope added to the URL
4. Save the new tokens to credentials.json

---

## AGENT RULES

- Always load credentials first. If missing, guide OAuth2 setup from STEP 1.
- Only use TIKTOK_ACCESS_TOKEN for API calls. TIKTOK_CLIENT_SECRET is for token refresh only.
- Rotate TIKTOK_REFRESH_TOKEN and TIKTOK_ACCESS_TOKEN immediately if the host is ever compromised.
- Never write extra fields to the credentials file.
- All API calls go to open.tiktokapis.com only. No external forwarding, no third-party services.
- Construct API calls inline from user intent — do not look for script files.
- Access tokens expire after 24 hours. If a call returns access_token_expired, run STEP 2 first then retry.
- On any error: parse error.code, map to the table above, tell the user exactly what to do.
- If a scope is missing: name it, link to developers.tiktok.com, say to re-authorize.
- OS detection: env:OS eq Windows_NT -> powershell; otherwise -> pwsh.
- No hardcoded user IDs, video IDs, or tokens — all come from credentials.json.