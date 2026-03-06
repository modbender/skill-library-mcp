# Dropbox Integration Setup Guide

Complete step-by-step instructions for setting up read-only Dropbox access in OpenClaw.

## Overview

This guide will walk you through:
1. Creating a Dropbox App
2. Configuring OAuth settings and permissions
3. Getting your credentials
4. Running the OAuth flow
5. Testing your connection

**Estimated time:** 10 minutes

## Prerequisites

- A Dropbox account (free or paid)
- Node.js installed
- Terminal/command line access

## Step 1: Create a Dropbox App

### 1.1 Visit Dropbox App Console

Go to: https://www.dropbox.com/developers/apps/create

If you're not logged in, log in with your Dropbox account.

### 1.2 Choose API

Select **"Scoped access"** (the modern, recommended API)

❌ Don't choose "App folder access" or "Full Dropbox" here yet

### 1.3 Choose Access Type

Select **"Full Dropbox"** to access all your files

- **Full Dropbox:** Access all files and folders in your account
- **App folder:** Only access a dedicated folder (more restrictive)

For most use cases, choose **Full Dropbox**.

### 1.4 Name Your App

Enter a unique app name. Examples:
- `OpenClaw-JohnDoe`
- `MyDropboxIntegration`
- `PersonalFileAccess`

The name must be unique across all Dropbox apps.

### 1.5 Create App

Click **"Create app"** button.

You'll be taken to your app's settings page.

## Step 2: Configure OAuth Settings

### 2.1 Add Redirect URI

On the app settings page, scroll to the **"OAuth 2"** section.

In the **"Redirect URIs"** field, add:

```
http://localhost:3000/callback
```

Click **"Add"** button.

**Why this matters:** This tells Dropbox where to send users after they authorize your app. The OAuth setup script runs a local server on port 3000 to catch this redirect.

### 2.2 Copy App Credentials

Still in the **"OAuth 2"** section, you'll see:

- **App key:** A string like `abc123xyz456`
- **App secret:** Click **"Show"** to reveal, looks like `xyz789abc123`

**Important:** Keep these secret! Don't share them or commit them to git.

Copy both values - you'll need them in Step 3.

## Step 3: Configure Permissions

### 3.1 Navigate to Permissions Tab

Click the **"Permissions"** tab at the top of your app settings page.

### 3.2 Enable Read-Only Scopes

Find and **enable** these permissions:

**Files and folders:**
- ✅ `files.metadata.read` - View files and folders in your Dropbox
- ✅ `files.content.read` - Download files

**Account:**
- ✅ `account_info.read` - View your account information

### 3.3 Verify Write Permissions Are Disabled

Make sure these are **NOT enabled** (for safety):

- ❌ `files.metadata.write` - Create, edit, and delete files
- ❌ `files.content.write` - Upload files
- ❌ `files.permanent_delete` - Permanently delete files

### 3.4 Save Changes

Click **"Submit"** button at the bottom of the permissions page.

**Important:** If you add or remove permissions later, users will need to re-authorize the app.

## Step 4: Install Dependencies

### 4.1 Navigate to Skill Directory

```bash
cd /path/to/skills/dropbox-integration
```

### 4.2 Install Dropbox SDK

```bash
npm install dropbox
```

This installs the official Dropbox JavaScript SDK.

## Step 5: Save Your Credentials

### 5.1 Create credentials.json

In the skill directory, create a file named `credentials.json`:

```json
{
  "app_key": "YOUR_APP_KEY_HERE",
  "app_secret": "YOUR_APP_SECRET_HERE"
}
```

Replace `YOUR_APP_KEY_HERE` and `YOUR_APP_SECRET_HERE` with the values from Step 2.2.

**Example:**

```json
{
  "app_key": "abc123xyz456",
  "app_secret": "xyz789abc123def456"
}
```

### 5.2 Verify .gitignore

Make sure `credentials.json` and `token.json` are in your `.gitignore`:

```
credentials.json
token.json
node_modules/
```

This prevents accidental commits of sensitive data.

## Step 6: Run OAuth Setup

### 6.1 Start Setup Script

```bash
node setup-oauth.js
```

You'll see output like:

```
📦 Dropbox OAuth Setup

1. Open this URL in your browser:

   https://www.dropbox.com/oauth2/authorize?client_id=...

2. Authorize the app
3. You'll be redirected to localhost (may show an error - that's OK)
4. Copy the full URL from your browser and paste it here

🌐 Local server started on http://localhost:3000
   Waiting for authorization...
```

### 6.2 Open Authorization URL

Copy the URL from step 1 and open it in your browser.

### 6.3 Review Permissions

Dropbox will show you what the app can access:

- View files in your Dropbox
- View information about your Dropbox account

These match the permissions you configured in Step 3.

### 6.4 Authorize the App

Click **"Allow"** or **"Continue"** button.

### 6.5 Complete Redirect

Your browser will be redirected to `http://localhost:3000/callback?code=...`

The local server will automatically catch this and exchange the code for tokens.

You should see:

```
✅ Authorization successful!
Your access token has been saved to token.json
You can close this window and return to your terminal.
```

### 6.6 Verify Token Storage

Back in your terminal, you should see:

```
✅ Success! Token saved to token.json

Token details:
  - Access token: sl.B3g5xyz...
  - Refresh token: abc123xyz...
  - This token will not expire (use refresh token to get new access tokens)
```

Your `token.json` file now contains:

```json
{
  "access_token": "sl.B3g5xyz...",
  "token_type": "bearer",
  "expires_in": 14400,
  "refresh_token": "abc123xyz...",
  "uid": "123456789",
  "account_id": "dbid:..."
}
```

**Important:** This file is gitignored and should never be committed.

## Step 7: Test Your Connection

### 7.1 Run Test Script

```bash
node test-connection.js
```

### 7.2 Verify Success

You should see your Dropbox account information:

```
🔐 Testing Dropbox connection...

✅ Connected successfully!

Account: John Doe (john@example.com)
Account ID: dbid:AAH4f99T0taONIb-OurWxbNQ6ywGRopQngc
Locale: en
Team: (none)
```

If you see errors, check the Troubleshooting section below.

## Step 8: Try Basic Operations

### 8.1 Browse Root Folder

```bash
node browse.js
```

### 8.2 Browse Specific Folder

```bash
node browse.js "/Documents"
```

### 8.3 Search for Files

```bash
node search-files.js "report"
```

### 8.4 Download a File

```bash
node download.js "/path/to/file.pdf" "./local-file.pdf"
```

## Troubleshooting

### Problem: "credentials.json not found"

**Solution:** Create `credentials.json` in the skill directory with your app key and secret (see Step 5).

### Problem: "redirect_uri_mismatch" error

**Solution:** Make sure you added `http://localhost:3000/callback` to your app's redirect URIs (see Step 2.1).

### Problem: "invalid_scope" error

**Solution:** You may have requested permissions that weren't enabled in your app. Go back to Step 3 and verify permissions are submitted.

### Problem: Browser shows "This site can't be reached"

**Solution:** This is normal! The local server is running on port 3000. Make sure the setup script is still running, and check that the URL contains a `code=` parameter. Copy the full URL if needed.

### Problem: "Token refresh failed"

**Solution:** Your refresh token may have been revoked. Re-run `node setup-oauth.js` to re-authenticate.

### Problem: "Permission denied" when accessing files

**Solution:** 
1. Verify permissions are enabled in your Dropbox App settings
2. Make sure you clicked "Submit" after changing permissions
3. Re-run OAuth setup to get tokens with the updated permissions

### Problem: Port 3000 already in use

**Solution:** Another process is using port 3000. Either stop that process or edit `setup-oauth.js` to use a different port (make sure to update the redirect URI in your Dropbox App settings too).

## Advanced Configuration

### Using App Folder Instead of Full Dropbox

If you only want to give the app access to a specific folder:

1. When creating the app (Step 1.3), choose **"App folder"**
2. The app will only see files in `/Apps/YourAppName/` folder
3. This is more restrictive but safer

### Custom Redirect URI

If you need to use a different port or domain:

1. Update the redirect URI in your Dropbox App settings
2. Edit `setup-oauth.js` and change the `REDIRECT_URI` constant
3. Update the server port if needed

### Revoking Access

To revoke the app's access to your Dropbox:

1. Go to https://www.dropbox.com/account/connected_apps
2. Find your app in the list
3. Click **"Revoke access"**

Your `token.json` will stop working, and you'll need to re-authenticate.

## Security Best Practices

1. **Never commit credentials:** Always keep `credentials.json` and `token.json` gitignored
2. **Use read-only permissions:** Only enable write permissions if absolutely necessary
3. **Rotate tokens regularly:** Consider re-authenticating periodically
4. **Monitor app usage:** Check the Dropbox App Console for usage stats
5. **Revoke unused apps:** Regularly audit connected apps in your Dropbox account

## Next Steps

Now that setup is complete:

1. ✅ Browse your files with `browse.js`
2. ✅ Search for specific files with `search-files.js`
3. ✅ Download files with `download.js`
4. ✅ Integrate with OpenClaw using the `exec` tool
5. ✅ Build custom automation using `dropbox-helper.js`

## Additional Resources

- [Dropbox API Documentation](https://www.dropbox.com/developers/documentation)
- [OAuth 2.0 Guide](https://www.dropbox.com/developers/reference/oauth-guide)
- [JavaScript SDK Reference](https://dropbox.github.io/dropbox-sdk-js/)
- [App Console](https://www.dropbox.com/developers/apps) - Manage your apps

---

**Having issues?** Check the troubleshooting section above or review the Dropbox API documentation for error codes.
