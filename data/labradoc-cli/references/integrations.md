# Labradoc CLI Integrations

Google Drive, Gmail, and Microsoft Outlook OAuth flows.

## Google Drive

```bash
# Check connection status
labradoc-cli api google drive status

# Get OAuth token URL (scope defaults to drive.readonly)
labradoc-cli api google drive token --scope "https://www.googleapis.com/auth/drive.readonly"

# Exchange OAuth code for token
labradoc-cli api google drive code --code <oauth-code>

# Refresh access token
labradoc-cli api google drive refresh

# Revoke access
labradoc-cli api google drive revoke
```

## Gmail

```bash
# Check connection status
labradoc-cli api google gmail status

# Get OAuth token URL
labradoc-cli api google gmail token

# Exchange OAuth code for token
labradoc-cli api google gmail code --code <oauth-code>

# Revoke access
labradoc-cli api google gmail revoke
```

## Microsoft Outlook

```bash
# Get OAuth token URL
labradoc-cli api microsoft outlook token

# Exchange OAuth code for token
labradoc-cli api microsoft outlook code --code <oauth-code>
```
