---
name: dropbox-integration
description: Read-only Dropbox integration for browsing, searching, and downloading files from your Dropbox account. Includes automatic OAuth token refresh, secure credential storage, and comprehensive setup guide. Perfect for accessing your Dropbox files from OpenClaw without giving write access.
---

# Dropbox Integration

## Overview

This skill provides **read-only** access to your Dropbox account, allowing you to browse folders, search files, and download content from OpenClaw. It uses OAuth 2.0 authentication with automatic token refresh for seamless long-term access.

**Perfect for:** Safely accessing your Dropbox files without worrying about accidental modifications or deletions.

## Capabilities

### Browse Files & Folders
- List contents of any folder in your Dropbox
- View file sizes and modification dates
- Navigate folder hierarchies

### Search Files
- Full-text search across file names
- Find files anywhere in your Dropbox
- Get file metadata and locations

### Download Files
- Download any file from your Dropbox
- Save to local filesystem
- Batch download support

### Automatic Token Management
- OAuth 2.0 authentication with refresh tokens
- Automatic token refresh (no manual re-authentication)
- Secure credential storage
- Token expiration handling with 5-minute buffer

## Security & Permissions

This skill is configured for **read-only access** with the following Dropbox scopes:

- `files.metadata.read` - Read file/folder metadata
- `files.content.read` - Read file content
- `account_info.read` - Read account information

**NOT included:**
- ❌ `files.content.write` - Cannot upload or modify files
- ❌ `files.metadata.write` - Cannot rename or move files
- ❌ `files.permanent_delete` - Cannot delete files

This ensures your Dropbox content remains safe from accidental modifications.

## Prerequisites

Before using this skill, you need:

1. A **Dropbox account** (free or paid)
2. A **Dropbox App** registration (takes 5 minutes)
3. **App key** and **App secret** from your Dropbox App
4. Node.js with `dropbox` package (auto-installed)

**Setup time: ~10 minutes**

See [Setup Guide](references/setup-guide.md) for step-by-step instructions.

## Quick Start

### 1. Create Dropbox App

Visit https://www.dropbox.com/developers/apps/create and create a new app:

- **API:** Scoped access
- **Access type:** Full Dropbox (or App folder for restricted access)
- **App name:** Something unique like "OpenClaw-YourName"

### 2. Configure OAuth

In your app's settings:
1. Add redirect URI: `http://localhost:3000/callback`
2. Copy your **App key** and **App secret**
3. Under **Permissions** tab, enable:
   - `files.metadata.read`
   - `files.content.read`
   - `account_info.read`

### 3. Save Credentials

Create `credentials.json` in the skill directory:

```json
{
  "app_key": "your_dropbox_app_key_here",
  "app_secret": "your_dropbox_app_secret_here"
}
```

**Important:** This file is gitignored and will never be committed.

### 4. Run OAuth Setup

```bash
node setup-oauth.js
```

This will:
1. Open your browser for Dropbox authorization
2. Start a local server to capture the authorization code
3. Exchange the code for access + refresh tokens
4. Save tokens securely to `token.json`

### 5. Test Connection

```bash
node test-connection.js
```

If successful, you'll see your Dropbox account information!

## Usage Examples

### Browse a Folder

```bash
# List root folder
node browse.js

# List specific folder
node browse.js "/Documents"
node browse.js "/Photos/2024"
```

Output:
```
📁 Listing: /Documents

📄 report.pdf (2.3 MB) - 2024-02-01
📄 presentation.pptx (5.1 MB) - 2024-01-28
📁 Projects
📁 Archive

Total: 4 items
```

### Search Files

```bash
node search-files.js "budget 2024"
node search-files.js "contract"
```

Output:
```
🔍 Searching for: "budget 2024"

✅ Found 3 matches:

📄 /Finance/budget-2024-q1.xlsx
   Size: 156.3 KB
   Modified: 2024-01-15T10:30:00Z

📄 /Reports/budget-2024-summary.pdf
   Size: 2.1 MB
   Modified: 2024-02-01T14:22:00Z
```

### Download Files

```bash
# Download to local file
node download.js "/Documents/report.pdf" "./downloads/report.pdf"

# Download to current directory
node download.js "/Photos/vacation.jpg" "./vacation.jpg"
```

Output:
```
📥 Downloading: /Documents/report.pdf
✅ Saved to: ./downloads/report.pdf (2.3 MB)
```

## Integration with OpenClaw

From OpenClaw, you can use the `exec` tool to run these scripts:

**Browse files:**
```
Run: node /path/to/dropbox-integration/browse.js "/Documents"
```

**Search for files:**
```
Run: node /path/to/dropbox-integration/search-files.js "contract"
```

**Download a file:**
```
Run: node /path/to/dropbox-integration/download.js "/path/in/dropbox" "./local/path"
```

Or create custom automation workflows that use the `dropbox-helper.js` module directly.

## How It Works

### Authentication Flow

1. **Initial Setup:** User authorizes the app via OAuth 2.0
2. **Token Storage:** Access token + refresh token saved to `token.json`
3. **Auto-Refresh:** Before each API call, checks if token needs refresh
4. **Seamless Access:** Automatically refreshes tokens 5 minutes before expiration

### Token Lifecycle

- **Access Token:** Short-lived (typically 4 hours)
- **Refresh Token:** Long-lived (doesn't expire unless revoked)
- **Auto-refresh:** Happens transparently in `dropbox-helper.js`
- **Refresh Buffer:** 5 minutes before expiration to prevent edge cases

### File Structure

```
dropbox-integration/
├── SKILL.md                 # This file
├── dropbox-helper.js        # Auto-refresh Dropbox client
├── setup-oauth.js           # OAuth setup script
├── browse.js                # Browse folders
├── search-files.js          # Search files
├── download.js              # Download files
├── test-connection.js       # Test authentication
├── credentials.json.example # Template for credentials
├── .gitignore               # Excludes credentials.json and token.json
└── references/
    └── setup-guide.md       # Detailed setup instructions
```

## Troubleshooting

### "credentials.json not found"
Create `credentials.json` with your Dropbox app key and secret (see Quick Start step 3).

### "Token refresh failed"
Your refresh token may have been revoked. Re-run `node setup-oauth.js` to re-authenticate.

### "Permission denied" errors
Check that you enabled the required permissions in your Dropbox App settings under the Permissions tab.

### "redirect_uri_mismatch"
Make sure you added `http://localhost:3000/callback` to your app's redirect URIs in Dropbox App Console.

### OAuth setup gets stuck
If the local server doesn't catch the redirect, manually copy the full URL from your browser after authorization and look for the `code=` parameter.

## Limitations

- **Read-only:** Cannot upload, modify, or delete files (by design)
- **File size:** Practical limit ~150MB per download (Dropbox API constraint)
- **Rate limits:** Dropbox API has rate limits (typically not an issue for personal use)
- **Shared folders:** Access depends on your Dropbox account permissions

## Security Best Practices

1. **Never commit credentials:** `credentials.json` and `token.json` are gitignored
2. **File permissions:** Tokens are saved with mode 0600 (user read/write only)
3. **App-specific tokens:** Each app has its own tokens (easily revokable)
4. **Scope limitation:** Only request permissions you actually need
5. **Token rotation:** Refresh tokens are rotated automatically

## Resources

### References

- [Setup Guide](references/setup-guide.md) - Detailed step-by-step instructions with screenshots
- [Dropbox API Documentation](https://www.dropbox.com/developers/documentation)
- [OAuth 2.0 Guide](https://www.dropbox.com/developers/reference/oauth-guide)

### Dropbox Developer Resources

- [App Console](https://www.dropbox.com/developers/apps) - Manage your apps
- [API Explorer](https://dropbox.github.io/dropbox-api-v2-explorer/) - Test API calls
- [SDK Documentation](https://dropbox.github.io/dropbox-sdk-js/) - JavaScript SDK reference

## Advanced Usage

### Using the Helper Module

For custom integrations, import the helper directly:

```javascript
const { getDropboxClient } = require('./dropbox-helper');

async function myCustomFunction() {
  const dbx = await getDropboxClient(); // Auto-refreshing client
  
  // Use any Dropbox SDK method
  const response = await dbx.filesListFolder({ path: '/Photos' });
  console.log(response.result.entries);
}
```

The helper automatically handles token refresh, so you never need to worry about expiration.

### Batch Operations

Download multiple files in sequence:

```javascript
const { getDropboxClient } = require('./dropbox-helper');
const fs = require('fs').promises;

async function downloadMultiple(files) {
  const dbx = await getDropboxClient();
  
  for (const file of files) {
    const response = await dbx.filesDownload({ path: file.dropboxPath });
    await fs.writeFile(file.localPath, response.result.fileBinary);
    console.log(`Downloaded: ${file.dropboxPath}`);
  }
}
```

## Dependencies

This skill requires the `dropbox` npm package:

```bash
npm install dropbox
```

The package is automatically installed when you install this skill via ClawHub.

## License

MIT - Free to use, modify, and distribute.

## Support

For issues or questions:
- Check the [Setup Guide](references/setup-guide.md) for detailed instructions
- Review Dropbox API errors in the [API documentation](https://www.dropbox.com/developers/documentation)
- Open an issue on the skill repository

---

**Note:** This skill is designed for personal use. For production applications with multiple users, consider implementing proper OAuth flow with state management and error handling for concurrent users.
