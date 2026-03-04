# Last.fm Authentication Guide

This guide explains how to set up authentication for Last.fm write operations (love/unlove tracks, scrobble).

## Overview

Read operations only require an API key. Write operations require a session key obtained through Last.fm's authentication flow.

## Authentication Types

| Type | Use Case | Requires |
|------|----------|----------|
| API Key Only | Read operations | API key |
| Desktop Auth | Write operations (local app) | API key + secret |
| Web Auth | Write operations (web app) | API key + secret + callback URL |

This skill uses **Desktop Auth** for write operations.

---

## Step 1: Get API Key and Secret

1. Visit https://www.last.fm/api/account/create
2. Fill in application details:
   - **Name**: Your preferred name
   - **Description**: Personal OpenClaw skill
   - **Application URL**: Leave blank or use your site
3. After creation, note both:
   - **API Key** - Used for all requests
   - **Shared Secret** - Used for signing write requests

## Step 2: Store Credentials

Add to `~/.openclaw/openclaw.json`:

```json5
{
  skills: {
    entries: {
      lastfm: {
        enabled: true,
        env: {
          LASTFM_API_KEY: "your_api_key",
          LASTFM_API_SECRET: "your_shared_secret",
          LASTFM_USERNAME: "your_username",
          LASTFM_SESSION_KEY: ""  // Will be filled after auth
        }
      }
    }
  }
}
```

**Security Note:** Never commit your API secret to a public repository.

---

## Step 3: Get Authentication Token

Request a token from Last.fm:

```bash
curl "https://ws.audioscrobbler.com/2.0/?method=auth.gettoken&api_key=YOUR_API_KEY&format=json"
```

Response:
```json
{
  "token": "your_auth_token"
}
```

**Note:** Tokens expire after 60 minutes if not used.

---

## Step 4: Authorize the Token

1. Construct authorization URL:
   ```
   https://www.last.fm/api/auth/?api_key=YOUR_API_KEY&token=YOUR_TOKEN
   ```

2. Open this URL in your browser

3. Log in to Last.fm and click "Yes, allow access"

4. You'll be redirected to a confirmation page

---

## Step 5: Get Session Key

After authorizing, exchange the token for a session key:

```bash
# First, create the method signature
# Signature = md5(api_key + method + token + secret)

# Example using common tools:
API_KEY="your_api_key"
API_SECRET="your_secret"
TOKEN="your_token"

# Create signature string (params in alphabetical order, without format)
SIG_STRING="api_key${API_KEY}methodauth.getSessiontoken${TOKEN}${API_SECRET}"
SIGNATURE=$(echo -n "$SIG_STRING" | md5sum | cut -d' ' -f1)

# Request session key
curl "https://ws.audioscrobbler.com/2.0/?method=auth.getSession&api_key=${API_KEY}&token=${TOKEN}&api_sig=${SIGNATURE}&format=json"
```

Response:
```json
{
  "session": {
    "name": "your_username",
    "key": "your_session_key",
    "subscriber": "0"
  }
}
```

---

## Step 6: Store Session Key

Add the session key to your configuration:

```json5
{
  skills: {
    entries: {
      lastfm: {
        enabled: true,
        env: {
          LASTFM_API_KEY: "your_api_key",
          LASTFM_API_SECRET: "your_secret",
          LASTFM_USERNAME: "your_username",
          LASTFM_SESSION_KEY: "your_session_key"
        }
      }
    }
  }
}
```

**Important:** Session keys do not expire unless the user revokes access.

---

## Creating Method Signatures

For write operations, you must create an API signature:

### Rules

1. Sort all parameters alphabetically (excluding `format`)
2. Concatenate: `param1value1param2value2...`
3. Append your API secret
4. Calculate MD5 hash of the string

### Example

For `track.love`:

```
Parameters: api_key=XXX, artist=Radiohead, method=track.love, sk=YYY, track=Creep

Sorted: api_keyXXXartistRadioheadmethodtrack.loveskYYYtrackCreep

With secret: api_keyXXXartistRadioheadmethodtrack.loveskYYYtrackCreepSECRET

Signature: md5("api_keyXXXartistRadioheadmethodtrack.loveskYYYtrackCreepSECRET")
```

### Code Example (Bash)

```bash
generate_signature() {
    local params=("$@")
    local secret="${LASTFM_API_SECRET}"
    
    # Sort params alphabetically
    IFS=$'\n' sorted=($(sort <<<"${params[*]}"))
    unset IFS
    
    # Concatenate
    local sig_string=""
    for param in "${sorted[@]}"; do
        sig_string+="${param}"
    done
    sig_string+="${secret}"
    
    # MD5 hash
    echo -n "$sig_string" | md5sum | cut -d' ' -f1
}

# Usage
signature=$(generate_signature "api_key${LASTFM_API_KEY}" "artistRadiohead" "methodtrack.love" "sk${LASTFM_SESSION_KEY}" "trackCreep")
```

---

## Revoking Access

To revoke session key access:

1. Visit https://www.last.fm/settings/applications
2. Find your application
3. Click "Revoke access"

After revoking, you'll need to repeat the authentication flow.

---

## Troubleshooting

### "Invalid session key"

- Token expired before authorization (60 min limit)
- User revoked access
- Session key is incorrect in config

### "Invalid method signature"

- Parameters not sorted alphabetically
- Secret incorrect
- Parameter names/values concatenated incorrectly

### "Token has expired"

Tokens are single-use and expire after 60 minutes. Request a new token and start over.

---

## Security Notes

1. **Never share** your API secret or session key
2. **Never commit** secrets to version control
3. **Use environment variables** for all credentials
4. **Revoke access** if you suspect compromise
5. **Session keys are long-lived** - store them securely
