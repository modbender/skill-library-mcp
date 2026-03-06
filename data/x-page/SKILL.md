---
name: x-twitter
description: "X/Twitter manager: post, reply, search, like, retweet & get analytics. Requires: powershell/pwsh. Reads ~/.config/x-twitter/credentials.json (X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET). App credentials permanent; account tokens rotate periodically and immediately if host is compromised. Grant minimal permissions only. No data forwarded; all calls go to api.twitter.com only."
metadata: {"openclaw":{"emoji":"[x]","requires":{"anyBins":["powershell","pwsh"]}}}
---

# x-twitter - Universal X/Twitter API Skill

Constructs and executes X API v2 calls inline based on what the user wants. No scripts needed.

API version: **v2**
Base URL: `https://api.twitter.com/2`

> **Requires an X Developer App** with OAuth 1.0a User Context credentials.
> Free tier supports posting, reading own timeline, and basic lookups.
> Elevated/Pro tier required for search and higher rate limits.

---

## STEP 1 - Load Credentials

Credentials are stored in `~/.config/x-twitter/credentials.json`.

```powershell
$cfg           = Get-Content "$HOME/.config/x-twitter/credentials.json" -Raw | ConvertFrom-Json
$apiKey        = $cfg.X_API_KEY
$apiSecret     = $cfg.X_API_SECRET
$accessToken   = $cfg.X_ACCESS_TOKEN
$accessSecret  = $cfg.X_ACCESS_SECRET
```

**If the file does not exist**, guide setup. Required fields:

| Field | Purpose |
|---|---|
| `X_API_KEY` | App API Key (Consumer Key) - from X Developer Portal |
| `X_API_SECRET` | App API Secret (Consumer Secret) - from X Developer Portal |
| `X_ACCESS_TOKEN` | Account Access Token - from X Developer Portal |
| `X_ACCESS_SECRET` | Account Access Token Secret - from X Developer Portal |

**One-time setup:**
1. Go to [X Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Create a Project and App (or use existing)
3. Under App Settings -> User authentication settings: enable OAuth 1.0a with Read and Write permissions
4. Go to App Keys and Tokens -> Generate Access Token and Secret (for your own account)
5. Save all four values:

```powershell
@{
    X_API_KEY       = "your_api_key"
    X_API_SECRET    = "your_api_secret"
    X_ACCESS_TOKEN  = "your_access_token"
    X_ACCESS_SECRET = "your_access_token_secret"
} | ConvertTo-Json | Set-Content "$HOME/.config/x-twitter/credentials.json" -Encoding UTF8
```

**Restrict file permissions immediately after saving:**
```powershell
# Windows
icacls "$HOME/.config/x-twitter/credentials.json" /inheritance:r /grant:r "$($env:USERNAME):(R,W)"
# macOS / Linux
# chmod 600 ~/.config/x-twitter/credentials.json
```

> Never commit this file to version control. It contains long-lived secrets.
> Rotate X_ACCESS_TOKEN and X_ACCESS_SECRET periodically and immediately if the host is ever compromised.
> X_API_KEY and X_API_SECRET are app-level credentials - keep them permanently but treat as sensitive.
> This skill makes no external calls other than to api.twitter.com. No data is forwarded to third parties.

---

## STEP 2 - Figure Out the API Call

X API v2 uses **OAuth 1.0a** for user-context actions (post, delete, like, retweet) and
**Bearer Token** for read-only public data. This skill uses OAuth 1.0a for all calls
(covers both read and write).

### OAuth 1.0a Signing Helper

All requests require an OAuth 1.0a Authorization header. Use this helper:

```powershell
function Get-OAuthHeader {
    param($method, $url, $apiKey, $apiSecret, $accessToken, $accessSecret, [hashtable]$params = @{})
    $nonce     = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes([System.Guid]::NewGuid().ToString("N")))
    $timestamp = [int][double]::Parse(([datetime]::UtcNow - [datetime]"1970-01-01").TotalSeconds)
    $oauthParams = @{
        oauth_consumer_key     = $apiKey
        oauth_nonce            = $nonce
        oauth_signature_method = "HMAC-SHA1"
        oauth_timestamp        = $timestamp
        oauth_token            = $accessToken
        oauth_version          = "1.0"
    }
    # Merge all params for signature base
    $allParams = @{}
    $oauthParams.GetEnumerator() | ForEach-Object { $allParams[$_.Key] = $_.Value }
    $params.GetEnumerator() | ForEach-Object { $allParams[$_.Key] = $_.Value }
    # Build signature base string
    $sortedParams = ($allParams.GetEnumerator() | Sort-Object Key | ForEach-Object {
        "$([Uri]::EscapeDataString($_.Key))=$([Uri]::EscapeDataString($_.Value))"
    }) -join "&"
    $baseString = "$method&$([Uri]::EscapeDataString($url))&$([Uri]::EscapeDataString($sortedParams))"
    # Sign
    $signingKey = "$([Uri]::EscapeDataString($apiSecret))&$([Uri]::EscapeDataString($accessSecret))"
    $hmac = New-Object System.Security.Cryptography.HMACSHA1
    $hmac.Key = [System.Text.Encoding]::ASCII.GetBytes($signingKey)
    $signature = [System.Convert]::ToBase64String($hmac.ComputeHash([System.Text.Encoding]::ASCII.GetBytes($baseString)))
    $oauthParams["oauth_signature"] = $signature
    # Build header
    $headerParts = $oauthParams.GetEnumerator() | Sort-Object Key | ForEach-Object {
        "$([Uri]::EscapeDataString($_.Key))=`"$([Uri]::EscapeDataString($_.Value))`""
    }
    return "OAuth $($headerParts -join ', ')"
}
```

### Common Endpoints

| What user wants | Method | Endpoint |
|---|---|---|
| Post a tweet | POST | `/tweets` body: `text` |
| Reply to a tweet | POST | `/tweets` body: `text` + `reply.in_reply_to_tweet_id` |
| Quote a tweet | POST | `/tweets` body: `text` + `quote_tweet_id` |
| Delete a tweet | DELETE | `/tweets/{id}` |
| Like a tweet | POST | `/users/{id}/likes` body: `tweet_id` |
| Unlike a tweet | DELETE | `/users/{id}/likes/{tweet_id}` |
| Retweet | POST | `/users/{id}/retweets` body: `tweet_id` |
| Undo retweet | DELETE | `/users/{id}/retweets/{tweet_id}` |
| Get own timeline | GET | `/users/{id}/tweets?max_results=10&tweet.fields=created_at,public_metrics` |
| Get home timeline | GET | `/users/{id}/timelines/reverse_chronological?max_results=10` |
| Search recent tweets | GET | `/tweets/search/recent?query=...&max_results=10` |
| Get tweet by ID | GET | `/tweets/{id}?tweet.fields=created_at,public_metrics,author_id` |
| Get own user info | GET | `/users/me?user.fields=username,name,public_metrics,description` |
| Get user by username | GET | `/users/by/username/{username}?user.fields=public_metrics` |
| Get followers | GET | `/users/{id}/followers?max_results=100` |
| Get following | GET | `/users/{id}/following?max_results=100` |
| Follow a user | POST | `/users/{id}/following` body: `target_user_id` |
| Unfollow a user | DELETE | `/users/{id}/following/{target_id}` |
| Get mentions | GET | `/users/{id}/mentions?max_results=10&tweet.fields=created_at,author_id` |
| Get bookmarks | GET | `/users/{id}/bookmarks?max_results=10` |
| Bookmark a tweet | POST | `/users/{id}/bookmarks` body: `tweet_id` |
| Create a list | POST | `/lists` body: `name`, `private` |
| Get own lists | GET | `/users/{id}/owned_lists` |
| Add member to list | POST | `/lists/{id}/members` body: `user_id` |

### API Call Patterns

**GET:**
```powershell
$url    = "https://api.twitter.com/2/ENDPOINT"
$authHeader = Get-OAuthHeader -method "GET" -url $url -apiKey $apiKey -apiSecret $apiSecret -accessToken $accessToken -accessSecret $accessSecret
$result = Invoke-RestMethod -Uri $url -Headers @{ Authorization = $authHeader } -ErrorAction Stop
```

**GET with query params (include in signature):**
```powershell
$url    = "https://api.twitter.com/2/tweets/search/recent"
$qp     = @{ query = "from:username"; max_results = "10" }
$authHeader = Get-OAuthHeader -method "GET" -url $url -apiKey $apiKey -apiSecret $apiSecret -accessToken $accessToken -accessSecret $accessSecret -params $qp
$qs     = ($qp.GetEnumerator() | ForEach-Object { "$($_.Key)=$([Uri]::EscapeDataString($_.Value))" }) -join "&"
$result = Invoke-RestMethod -Uri "$url`?$qs" -Headers @{ Authorization = $authHeader } -ErrorAction Stop
```

**POST (JSON body):**
```powershell
$url    = "https://api.twitter.com/2/tweets"
$body   = @{ text = "Hello from OpenClaw!" } | ConvertTo-Json
$authHeader = Get-OAuthHeader -method "POST" -url $url -apiKey $apiKey -apiSecret $apiSecret -accessToken $accessToken -accessSecret $accessSecret
$result = Invoke-RestMethod -Uri $url -Method POST -Headers @{ Authorization = $authHeader; "Content-Type" = "application/json" } -Body $body -ErrorAction Stop
Write-Host "Posted tweet ID: $($result.data.id)"
```

**DELETE:**
```powershell
$url    = "https://api.twitter.com/2/tweets/{id}"
$authHeader = Get-OAuthHeader -method "DELETE" -url $url -apiKey $apiKey -apiSecret $apiSecret -accessToken $accessToken -accessSecret $accessSecret
$result = Invoke-RestMethod -Uri $url -Method DELETE -Headers @{ Authorization = $authHeader } -ErrorAction Stop
```

### Get Own User ID (needed for user-context endpoints)

```powershell
$url    = "https://api.twitter.com/2/users/me"
$authHeader = Get-OAuthHeader -method "GET" -url $url -apiKey $apiKey -apiSecret $apiSecret -accessToken $accessToken -accessSecret $accessSecret
$me     = Invoke-RestMethod -Uri $url -Headers @{ Authorization = $authHeader } -ErrorAction Stop
$userId = $me.data.id
```

### Post with Media (image attachment)

```powershell
# Step 1: Upload media via v1.1 endpoint (media upload is not on v2 yet)
$mediaUrl   = "https://upload.twitter.com/1.1/media/upload.json"
$fileBytes  = [System.IO.File]::ReadAllBytes($imagePath)
$b64        = [System.Convert]::ToBase64String($fileBytes)
$uploadAuth = Get-OAuthHeader -method "POST" -url $mediaUrl -apiKey $apiKey -apiSecret $apiSecret -accessToken $accessToken -accessSecret $accessSecret
$upload     = Invoke-RestMethod -Uri $mediaUrl -Method POST -Headers @{ Authorization = $uploadAuth; "Content-Type" = "application/json" } `
    -Body (@{ media_data = $b64 } | ConvertTo-Json) -ErrorAction Stop
$mediaId    = $upload.media_id_string
# Step 2: Post tweet with media
$tweetUrl   = "https://api.twitter.com/2/tweets"
$tweetAuth  = Get-OAuthHeader -method "POST" -url $tweetUrl -apiKey $apiKey -apiSecret $apiSecret -accessToken $accessToken -accessSecret $accessSecret
$result     = Invoke-RestMethod -Uri $tweetUrl -Method POST `
    -Headers @{ Authorization = $tweetAuth; "Content-Type" = "application/json" } `
    -Body (@{ text = $caption; media = @{ media_ids = @($mediaId) } } | ConvertTo-Json -Depth 3) -ErrorAction Stop
Write-Host "Posted tweet with media ID: $($result.data.id)"
```

---

## STEP 3 - Handle Errors

```powershell
try {
    # ... API call ...
} catch {
    $err    = $_.ErrorDetails.Message | ConvertFrom-Json -ErrorAction SilentlyContinue
    $status = $_.Exception.Response.StatusCode.value__
    $title  = $err.title
    $detail = $err.detail
    Write-Host "HTTP $status - $title : $detail"
}
```

| HTTP Status | Title / Code | Meaning | Fix |
|---|---|---|---|
| 400 | Invalid Request | Bad parameters or malformed JSON | Check required fields; ensure JSON body is valid |
| 401 | Unauthorized | Invalid or expired credentials | Regenerate Access Token and Secret in Developer Portal |
| 403 | Forbidden | App lacks permission or write access disabled | Enable Read and Write in App -> User authentication settings |
| 403 | duplicate-content | Tweet text is a duplicate | Change the tweet text |
| 429 | Too Many Requests | Rate limit exceeded | Check `x-rate-limit-reset` header; wait until reset time |
| 404 | Not Found | Tweet or user does not exist | Verify the ID; tweet may have been deleted |
| 453 | Access to endpoint denied | Endpoint requires elevated access tier | Upgrade to Basic/Pro at developer.twitter.com |

### Rate Limits (Free Tier)

| Action | Limit |
|---|---|
| POST /tweets | 17 tweets per 24h per user; 50 per app |
| DELETE /tweets | 50 per 15 min |
| GET /users/me | 25 per 24h |
| GET /tweets/search/recent | Requires Basic tier or above |
| GET timelines | 5 per 15 min (Free); 180 per 15 min (Basic) |

**If rate limited:** read the `x-rate-limit-reset` response header (Unix timestamp) and tell the user when they can retry.

### Access Tiers

| Tier | Cost | Key limits |
|---|---|---|
| Free | $0 | 17 tweets/day write; very limited read |
| Basic | $100/month | 100 tweets/day; search; higher read limits |
| Pro | $5000/month | Full access; high rate limits |

---

## AGENT RULES

- **Always load credentials first.** If missing or incomplete, guide setup.
- **Always use OAuth 1.0a** via the Get-OAuthHeader helper - never send raw tokens in query strings.
- **Get own user ID first** when calling user-context endpoints (`/users/{id}/...`) - use `/users/me`.
- **Never embed tokens as literals** - read all four credential fields fresh from disk at runtime.
- **Rotate credentials** if the host is ever compromised: regenerate Access Token and Secret in Developer Portal.
- **Rate limits:** on HTTP 429, read `x-rate-limit-reset` header and tell the user the exact retry time.
- **Free tier restrictions:** search requires Basic tier; if user gets 453 "Access to endpoint denied", tell them the required tier and link to developer.twitter.com/en/portal/products.
- **Media upload:** uses v1.1 upload endpoint (`upload.twitter.com`) - this is intentional and expected; it is still Twitter/X infrastructure. State this if the user asks.
- **Least-privilege:** instruct user to enable only Read and Write in app settings; do not request DM permissions unless explicitly needed.
- **All API calls go to `api.twitter.com` and `upload.twitter.com` only** - both are X/Twitter infrastructure. No external forwarding, no third-party services.
- **Construct API calls inline** from user intent - do not look for script files.
- **On any error:** parse HTTP status, map to the table above, tell the user exactly what to do.
- **Duplicate tweet:** if user tries to post the same text twice, tell them X blocks duplicate content and ask them to change the wording.