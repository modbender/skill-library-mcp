# HubSpot Authentication Setup

## Private Apps (Recommended)

### 1. Create Private App
1. Go to Settings → Integrations → Private Apps
2. Click "Create a private app"
3. Select required scopes (see below)
4. Generate token: `pat-na1-xxx` or `pat-eu1-xxx`

### 2. Set Environment Variable
```bash
export HUBSPOT_ACCESS_TOKEN="pat-na1-xxxxxxxxxxxx"
```

### 3. Test Authentication
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v3/objects/contacts?limit=1"
```

## Required Scopes

### CRM Scopes
- `crm.objects.contacts.read` / `crm.objects.contacts.write`
- `crm.objects.companies.read` / `crm.objects.companies.write`
- `crm.objects.deals.read` / `crm.objects.deals.write`
- `crm.objects.tickets.read` / `crm.objects.tickets.write`
- `crm.objects.custom.read` / `crm.objects.custom.write`

### Association Scopes
- `crm.associations.read` / `crm.associations.write`

### Properties & Schema
- `crm.schemas.contacts.read` / `crm.schemas.contacts.write`
- `crm.schemas.companies.read` / `crm.schemas.companies.write`
- `crm.schemas.deals.read` / `crm.schemas.deals.write`
- `crm.schemas.custom.read` / `crm.schemas.custom.write`

### Activities & Engagements
- `crm.objects.activities.read` / `crm.objects.activities.write`

### Marketing & Automation
- `automation` (for workflows)
- `forms` (for forms API)
- `marketing-email` (for email campaigns)

### Reporting & Analytics
- `reports` (for custom reports)

## Legacy API Key (Deprecated)

Still works but Private Apps are preferred:

```bash
export HUBSPOT_API_KEY="your-api-key"

# Usage
curl "https://api.hubapi.com/crm/v3/objects/contacts?hapikey=$HUBSPOT_API_KEY"
```

## New HubSpot Developer Platform

### 1. Install HubSpot CLI
```bash
npm install -g @hubspot/cli
```

### 2. Authenticate
```bash
hs auth
```

### 3. Create New Project
```bash
hs project create my-hubspot-app
cd my-hubspot-app
```

### 4. Available Project Templates
- `empty` - Blank project
- `react-ui-extensions` - Custom cards/panels
- `serverless-functions` - HubSpot Functions
- `webpack-serverless` - Advanced serverless setup

### 5. Deploy Functions
```bash
hs project upload
```

### 6. Create Custom Object Schema
```bash
hs custom-object schema create contacts-extended
```

## OAuth Apps (Advanced)

### 1. Create OAuth App
1. Go to Settings → Integrations → Connected Apps
2. Create public or private app
3. Set redirect URI
4. Note Client ID and Client Secret

### 2. Authorization URL
```
https://app.hubspot.com/oauth/authorize?client_id=CLIENT_ID&scope=SCOPES&redirect_uri=REDIRECT_URI
```

### 3. Exchange Code for Token
```bash
curl -X POST "https://api.hubapi.com/oauth/v1/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code&client_id=CLIENT_ID&client_secret=CLIENT_SECRET&redirect_uri=REDIRECT_URI&code=AUTH_CODE"
```

## Multi-Portal Setup

For agencies managing multiple HubSpot accounts:

```bash
# Portal 1
export HUBSPOT_ACCESS_TOKEN_PORTAL1="pat-na1-xxx"

# Portal 2  
export HUBSPOT_ACCESS_TOKEN_PORTAL2="pat-eu1-xxx"

# Switch contexts
alias hs-portal1='export HUBSPOT_ACCESS_TOKEN=$HUBSPOT_ACCESS_TOKEN_PORTAL1'
alias hs-portal2='export HUBSPOT_ACCESS_TOKEN=$HUBSPOT_ACCESS_TOKEN_PORTAL2'
```

## Testing Your Setup

### Get Account Info
```bash
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/integrations/v1/me"
```

### Check Rate Limits
```bash
curl -I -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v3/objects/contacts?limit=1" | grep -i rate
```

### Test Scopes
```bash
# Test contact read
curl -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  "https://api.hubapi.com/crm/v3/objects/contacts?limit=1"

# Test contact write  
curl -X POST "https://api.hubapi.com/crm/v3/objects/contacts" \
  -H "Authorization: Bearer $HUBSPOT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"properties": {"email": "test@example.com"}}'
```

## Common Authentication Issues

### 401 Unauthorized
- Token expired or invalid
- Missing required scopes
- Wrong API endpoint region (na1 vs eu1)

### 403 Forbidden  
- Insufficient permissions
- Object type not accessible
- Portal limits exceeded

### 429 Rate Limited
- Too many requests
- See rate-limits.md for handling

## Environment Configuration

Create `.env` file:
```bash
HUBSPOT_ACCESS_TOKEN=pat-na1-xxxxxxxxxxxx
HUBSPOT_PORTAL_ID=12345678
HUBSPOT_BASE_URL=https://api.hubapi.com
```

Load with:
```bash
set -a && source .env && set +a
```

## Security Best Practices

1. **Never commit tokens** to version control
2. **Use environment variables** not hardcoded values
3. **Rotate tokens regularly** (Private Apps)
4. **Minimum required scopes** only
5. **Monitor API usage** for anomalies
6. **Use HTTPS** always for OAuth redirects