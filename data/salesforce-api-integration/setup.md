# Setup - Salesforce API Integration

## Authentication Methods

### Option 1: Connected App (Recommended)

1. **Create Connected App in Salesforce:**
   - Setup → App Manager → New Connected App
   - Enable OAuth Settings
   - Callback URL: `https://login.salesforce.com/services/oauth2/callback`
   - Select scopes: `api`, `refresh_token`
   - Save and wait 10 minutes for propagation

2. **Get Access Token (Username-Password Flow):**

```bash
curl -X POST "https://login.salesforce.com/services/oauth2/token" \
  -d "grant_type=password" \
  -d "client_id=YOUR_CONSUMER_KEY" \
  -d "client_secret=YOUR_CONSUMER_SECRET" \
  -d "username=YOUR_USERNAME" \
  -d "password=YOUR_PASSWORD_AND_SECURITY_TOKEN"
```

Response:
```json
{
  "access_token": "00D...",
  "instance_url": "https://yourorg.my.salesforce.com",
  "token_type": "Bearer"
}
```

3. **Set Environment Variables:**

```bash
export SF_ACCESS_TOKEN="00D..."
export SF_INSTANCE_URL="https://yourorg.my.salesforce.com"
```

### Option 2: Web Server Flow (Interactive)

For apps with user interaction:

```bash
# Step 1: Redirect user to authorization URL
https://login.salesforce.com/services/oauth2/authorize?
  response_type=code&
  client_id=YOUR_CONSUMER_KEY&
  redirect_uri=YOUR_CALLBACK_URL

# Step 2: Exchange code for token
curl -X POST "https://login.salesforce.com/services/oauth2/token" \
  -d "grant_type=authorization_code" \
  -d "client_id=YOUR_CONSUMER_KEY" \
  -d "client_secret=YOUR_CONSUMER_SECRET" \
  -d "redirect_uri=YOUR_CALLBACK_URL" \
  -d "code=AUTH_CODE_FROM_CALLBACK"
```

### Option 3: Refresh Token

```bash
curl -X POST "https://login.salesforce.com/services/oauth2/token" \
  -d "grant_type=refresh_token" \
  -d "client_id=YOUR_CONSUMER_KEY" \
  -d "client_secret=YOUR_CONSUMER_SECRET" \
  -d "refresh_token=YOUR_REFRESH_TOKEN"
```

## Sandbox vs Production

| Environment | Login URL |
|-------------|-----------|
| Production | `https://login.salesforce.com` |
| Sandbox | `https://test.salesforce.com` |

## Test Connection

```bash
curl "$SF_INSTANCE_URL/services/data/v59.0/" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

Expected: List of available API resources.

## Memory Setup

```bash
mkdir -p ~/salesforce-api-integration
```

Then initialize memory by asking the agent about your Salesforce org.

## Security Token

If IP restrictions are enabled, append security token to password:
- Get token: Setup → My Personal Information → Reset My Security Token
- Password becomes: `YourPassword` + `SecurityToken`

## API Versions

Check available versions:
```bash
curl "$SF_INSTANCE_URL/services/data/"
```

Use the latest stable version (v59.0 or newer).

## Troubleshooting

### INVALID_SESSION_ID
- Token expired → refresh or re-authenticate
- Wrong instance URL → verify SF_INSTANCE_URL

### INVALID_CLIENT
- Consumer key/secret wrong
- Connected App not properly configured

### IP_RANGE_ERROR  
- IP not whitelisted → add security token to password
- Or whitelist IP in Connected App settings
