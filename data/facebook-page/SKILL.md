---
name: facebook-page
description: "Facebook Page manager: post, schedule, reply, get insights & more. Requires: powershell/pwsh. Reads ~/.config/fb-page/credentials.json (FB_PAGE_TOKEN, FB_PAGE_ID). FB_APP_SECRET for one-time setup only — delete afterward. Long-lived token; rotate periodically and immediately if host is compromised. Grant minimal permissions only. No data forwarded to third parties; all calls go to graph.facebook.com only."
metadata: {"openclaw":{"emoji":"[fb]","requires":{"anyBins":["powershell","pwsh"]}}}
---


# facebook-page â€” Universal Meta Graph API Skill

Constructs and executes Meta Graph API calls inline based on what the user wants. No scripts needed.

API version: **v25.0**
Base URL: `https://graph.facebook.com/v25.0`

---

## STEP 1 â€” Load Credentials

Credentials are stored in `~/.config/fb-page/credentials.json`.

```powershell
$cfg    = Get-Content "$HOME/.config/fb-page/credentials.json" -Raw | ConvertFrom-Json
$token  = $cfg.FB_PAGE_TOKEN
$pageId = $cfg.FB_PAGE_ID
```

**If the file doesn't exist**, guide setup. Required fields:

| Field | Purpose |
|---|---|
| `FB_PAGE_TOKEN` | Never-expiring Page access token â€” used for all API calls |
| `FB_PAGE_ID` | Numeric Facebook Page ID |
| `FB_APP_ID` | Meta App ID â€” only needed during token exchange |
| `FB_APP_SECRET` | Meta App Secret â€” only needed during token exchange |

**One-time token exchange setup:**
```powershell
# Provide: $appId, $appSecret, $shortToken (from Graph API Explorer), $pageId
# 1. Exchange for long-lived user token
$r1 = Invoke-RestMethod "https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=$appId&client_secret=$appSecret&fb_exchange_token=$shortToken"
# 2. Get never-expiring Page token
$r2 = Invoke-RestMethod "https://graph.facebook.com/v25.0/$pageId?fields=access_token&access_token=$($r1.access_token)"
$pageToken = $r2.access_token
# 3. Save â€” only these four fields, nothing else
@{
    FB_PAGE_ID    = $pageId
    FB_PAGE_TOKEN = $pageToken
    FB_APP_ID     = $appId
    FB_APP_SECRET = $appSecret
} | ConvertTo-Json | Set-Content "$HOME/.config/fb-page/credentials.json" -Encoding UTF8
```

**Restrict file permissions immediately after saving:**
```powershell
# Windows
icacls "$HOME/.config/fb-page/credentials.json" /inheritance:r /grant:r "$($env:USERNAME):(R,W)"
# macOS / Linux
# chmod 600 ~/.config/fb-page/credentials.json
```

> âš ï¸ Never commit this file to version control. It contains long-lived secrets.
> This skill makes no external calls other than to `graph.facebook.com`. No data is forwarded to third parties.

---

## STEP 2 â€” Figure Out the API Call

### Common Endpoints

| What user wants | Method | Endpoint |
|---|---|---|
| Post text | POST | `/$pageId/feed` â€” body: `message` |
| Post with image | POST | `/$pageId/photos` â€” multipart: `source` + `message` |
| Post with video | POST | `/$pageId/videos` â€” multipart: `source` + `description` |
| Post with link | POST | `/$pageId/feed` â€” body: `message` + `link` |
| Delete a post | DELETE | `/{post-id}` |
| Schedule a post | POST | `/$pageId/feed` â€” body: `message` + `published=false` + `scheduled_publish_time` (unix timestamp) |
| Get recent posts | GET | `/$pageId/published_posts?fields=id,message,created_time&limit=10` |
| Get page info | GET | `/$pageId?fields=name,fan_count,followers_count,about` |
| Like a post | POST | `/{post-id}/likes` |
| Get comments | GET | `/{post-id}/comments?fields=message,from,created_time` |
| Reply to comment | POST | `/{comment-id}/comments` â€” body: `message` |
| Hide comment | POST | `/{comment-id}` â€” body: `is_hidden=true` |
| Delete comment | DELETE | `/{comment-id}` |
| Get page insights | GET | `/$pageId/insights?metric=page_fans,page_impressions&period=day` |
| Get post insights | GET | `/{post-id}/insights?metric=post_impressions,post_reactions_by_type_total` |
| List events | GET | `/$pageId/events?fields=name,start_time,description` |
| Create event | POST | `/$pageId/events` â€” body: `name`, `start_time`, `description` |
| List albums | GET | `/$pageId/albums?fields=name,count` |
| Get page roles | GET | `/$pageId/roles` |
| Publish draft post | POST | `/{post-id}` â€” body: `is_published=true` |

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

**Multipart (image/video upload):**
```powershell
$boundary  = [System.Guid]::NewGuid().ToString()
$fileBytes = [System.IO.File]::ReadAllBytes($filePath)
$fileName  = [System.IO.Path]::GetFileName($filePath)
$stream    = New-Object System.IO.MemoryStream
$writer    = New-Object System.IO.StreamWriter($stream)
$writer.Write("--$boundary`r`nContent-Disposition: form-data; name=`"message`"`r`n`r`n$message`r`n")
$writer.Write("--$boundary`r`nContent-Disposition: form-data; name=`"access_token`"`r`n`r`n$token`r`n")
$writer.Write("--$boundary`r`nContent-Disposition: form-data; name=`"source`"; filename=`"$fileName`"`r`nContent-Type: image/jpeg`r`n`r`n")
$writer.Flush(); $stream.Write($fileBytes, 0, $fileBytes.Length)
$writer.Write("`r`n--$boundary--`r`n"); $writer.Flush()
$result = Invoke-RestMethod -Uri "https://graph.facebook.com/v25.0/$pageId/photos" -Method POST `
    -ContentType "multipart/form-data; boundary=$boundary" -Body $stream.ToArray() -ErrorAction Stop
```

**Scheduled post** â€” convert local time to Unix timestamp:
```powershell
$runAt    = [datetime]"2026-03-15 09:00"
$unixTime = [int][double]::Parse(($runAt.ToUniversalTime() - [datetime]"1970-01-01").TotalSeconds)
$result   = Invoke-RestMethod -Uri "https://graph.facebook.com/v25.0/$pageId/feed" -Method POST `
    -Body @{ message="text"; published="false"; scheduled_publish_time=$unixTime; access_token=$token } -ErrorAction Stop
```

---

## STEP 3 â€” Handle Errors

```powershell
try {
    # ... API call ...
} catch {
    $err     = $_.ErrorDetails.Message | ConvertFrom-Json -ErrorAction SilentlyContinue
    $code    = $err.error.code
    $subcode = $err.error.error_subcode
    $msg     = $err.error.message
}
```

| Code | Subcode | Meaning | Fix |
|---|---|---|---|
| 100 | â€” | Invalid parameter | Check the parameter values |
| 102 | â€” | Session expired | Re-run setup to get a new token |
| 190 | 460 | Token expired | Re-run setup with a new short-lived token |
| 190 | 467 | Invalid token | Re-run setup |
| 200 | â€” | Permission denied | Add the permission listed in `error.message` to your app |
| 10 | â€” | Permission denied (page) | Add `pages_read_engagement` or `pages_manage_posts` |
| 230 | â€” | Requires re-auth | Re-run setup |
| 368 | â€” | Temporarily blocked | Wait and retry; page may be rate-limited |

### Permissions Reference

| Permission | Required for |
|---|---|
| `pages_manage_posts` | Create, delete, schedule posts |
| `pages_read_engagement` | Read posts, likes, comments, insights |
| `pages_show_list` | List pages you manage |
| `pages_manage_metadata` | Update page settings |
| `pages_manage_engagement` | Moderate comments, reply to reviews |
| `pages_read_user_content` | Read visitor posts and comments |
| `pages_manage_ads` | Manage ad campaigns on the page |
| `pages_manage_instant_articles` | Manage Instant Articles |

**If a permission is missing:**
1. Go to [Meta for Developers](https://developers.facebook.com/apps/)
2. Select your app â†’ Permissions and Features
3. Add the required permission
4. Regenerate token via [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
5. Re-run setup with the new token

---

## AGENT RULES

- **Always load credentials first.** If missing or incomplete, guide setup.
- **Only use `FB_PAGE_TOKEN` and `FB_PAGE_ID`** for API calls. `FB_APP_ID` and `FB_APP_SECRET` are for token exchange only.
- **Never write extra fields** to the credentials file (no owner IDs, conv IDs, or third-party keys).
- **Remove FB_APP_SECRET** from credentials.json after token exchange â€” it is not needed for API calls.
- **Least-privilege:** only request the permissions your use case needs. Do not request `pages_manage_ads` or `pages_manage_instant_articles` unless explicitly needed.
- **Rotate FB_PAGE_TOKEN** periodically via Graph API Explorer, and immediately if the host is ever compromised.
- **All API calls go to `graph.facebook.com` only.** No external forwarding, no third-party services.
- **Construct API calls inline** from user intent â€” don't look for script files.
- **On any error:** parse `error.code` + `error.error_subcode`, map to the table above, tell the user exactly what to do.
- **If a permission is missing:** name it, link to Meta for Developers, say to re-run setup.
