# Microsoft Graph Azure App Registration Setup Guide

This guide provides step-by-step instructions for creating and configuring an Azure App Registration to use with the Microsoft Graph skill.

## Time Required

**Estimated time:** 10-15 minutes

## Prerequisites

- Microsoft account with access to Azure Portal
- Azure Active Directory (Azure AD) tenant
  - If you have Microsoft 365, you already have this
  - Personal Microsoft accounts need an Azure AD tenant (free tier available)
- Administrator permissions (or ability to request admin consent)

## Step 1: Access Azure Portal

1. Navigate to https://portal.azure.com
2. Sign in with your Microsoft account
3. Confirm you're in the correct directory (top-right corner)
   - If managing multiple tenants, switch to the correct one

## Step 2: Create App Registration

1. In Azure Portal, search for "App registrations" in the top search bar
2. Click **+ New registration**

3. **Configure the registration:**
   - **Name**: Enter a descriptive name
     - Example: "OpenClaw Microsoft Graph Integration"
   - **Supported account types**: Select one:
     - ✅ **"Accounts in this organizational directory only (Single tenant)"** (Recommended for most users)
     - "Accounts in any organizational directory (Multi-tenant)" (For cross-organization)
     - ❌ "Personal Microsoft accounts" (Not compatible with this skill)
   - **Redirect URI**: Leave blank (not needed for device code flow)
   
4. Click **Register**

## Step 3: Copy Application IDs

After registration, you'll see the Overview page.

**Copy these values** (you'll need them later):

1. **Application (client) ID**
   - Example: `12345678-1234-1234-1234-123456789abc`
   - This is your `AZURE_CLIENT_ID`

2. **Directory (tenant) ID**
   - Example: `87654321-4321-4321-4321-cba987654321`
   - This is your `AZURE_TENANT_ID`

**Store these safely** - you'll add them to OpenClaw configuration later.

## Step 4: Create Client Secret

1. In the left sidebar, click **Certificates & secrets**
2. Click **+ New client secret**
3. **Configure the secret:**
   - **Description**: Enter a description
     - Example: "OpenClaw production secret"
   - **Expires**: Choose expiration
     - ✅ **24 months** (Recommended - balance of security and maintenance)
     - 6 months / 12 months / Custom (More secure, requires more frequent renewal)
4. Click **Add**

**⚠️ IMPORTANT:** The secret **Value** is displayed ONLY ONCE!

- **Copy the "Value" immediately** (not the "Secret ID")
- Example: `AbC1~dEf2GhI3jKl4MnO5pQr6StU7vWx8YzA9bCd0`
- This is your `AZURE_CLIENT_SECRET`
- If you lose it, you must create a new secret

## Step 5: Configure API Permissions

1. In the left sidebar, click **API permissions**
2. You'll see `User.Read` already granted by default
3. Click **+ Add a permission**

**Add each of the following permissions:**

### For Email Support:
1. Click **Microsoft Graph** → **Delegated permissions**
2. Search for and select:
   - `Mail.Read`
   - `Mail.ReadWrite`
   - `Mail.Send`
3. Click **Add permissions**

### For Calendar Support:
1. Click **+ Add a permission** → **Microsoft Graph** → **Delegated permissions**
2. Search for and select:
   - `Calendars.Read`
   - `Calendars.ReadWrite`
3. Click **Add permissions**

### For Contacts Support:
1. Click **+ Add a permission** → **Microsoft Graph** → **Delegated permissions**
2. Search for and select:
   - `Contacts.Read`
   - `Contacts.ReadWrite`
3. Click **Add permissions**

### For Token Refresh (Required):
1. Click **+ Add a permission** → **Microsoft Graph** → **Delegated permissions**
2. Search for and select:
   - `offline_access`
3. Click **Add permissions**

**Final permission list should include:**
- User.Read (default)
- Mail.Read
- Mail.ReadWrite
- Mail.Send
- Calendars.Read
- Calendars.ReadWrite
- Contacts.Read
- Contacts.ReadWrite
- offline_access

## Step 6: Grant Admin Consent (If Required)

**Check if admin consent is needed:**

Look at the "Status" column for each permission:
- ✅ Green checkmark = Consent granted
- ⚠️ "Not granted" = Admin consent required

**If admin consent is required:**

### Option A: You have admin rights
1. Click **Grant admin consent for [Your Organization]**
2. Click **Yes** to confirm
3. All permissions should now show green checkmarks

### Option B: Request admin consent
1. Copy the app's consent URL:
   - Format: `https://login.microsoftonline.com/{tenant-id}/adminconsent?client_id={client-id}`
   - Replace `{tenant-id}` with your Directory (tenant) ID
   - Replace `{client-id}` with your Application (client) ID
2. Send this URL to your IT administrator
3. Wait for admin approval
4. Refresh the API permissions page to check status

**Note:** If your organization requires admin consent, the app won't work until consent is granted.

## Step 7: Enable Public Client Flow

1. In the left sidebar, click **Authentication**
2. Scroll down to **Advanced settings** → **Allow public client flows**
3. Toggle **Enable the following mobile and desktop flows** to **Yes**
4. Click **Save** at the top

**Why this is needed:** The device code flow requires public client flow to be enabled.

## Step 8: Configure OpenClaw

Now that Azure setup is complete, configure OpenClaw with your credentials.

### Option A: Environment Variables

```bash
export AZURE_TENANT_ID="your-tenant-id-here"
export AZURE_CLIENT_ID="your-client-id-here"
export AZURE_CLIENT_SECRET="your-client-secret-here"
```

### Option B: OpenClaw Config File

Edit your OpenClaw configuration (`~/.openclaw/openclaw.json` or via `/config` command):

```json
{
  "env": {
    "vars": {
      "AZURE_TENANT_ID": "your-tenant-id-here",
      "AZURE_CLIENT_ID": "your-client-id-here",
      "AZURE_CLIENT_SECRET": "your-client-secret-here"
    }
  }
}
```

**⚠️ Security note:** 
- Client secrets are sensitive - treat them like passwords
- Don't commit secrets to version control
- Restrict file permissions: `chmod 600 ~/.openclaw/openclaw.json`

## Step 9: First Authentication

When you first use the Microsoft Graph skill:

1. OpenClaw will display a device code and URL
2. Open the URL in your browser: https://microsoft.com/devicelogin
3. Enter the device code shown
4. Sign in with your Microsoft account
5. Review and accept the permission consent screen
6. Return to OpenClaw - authentication complete!

**Token storage:** Tokens are saved to `~/.openclaw/auth/microsoft-graph.json` and automatically refreshed.

## Verification Checklist

Before testing, verify:

- ✅ App registration created in Azure Portal
- ✅ Application (client) ID copied
- ✅ Directory (tenant) ID copied
- ✅ Client secret created and value copied
- ✅ All 9 permissions added (User.Read, Mail.*, Calendars.*, Contacts.*, offline_access)
- ✅ Admin consent granted (if required)
- ✅ Public client flow enabled
- ✅ Credentials added to OpenClaw config
- ✅ First authentication completed successfully

## Troubleshooting

### "AADSTS700016: Application not found in directory"

**Cause:** Tenant ID doesn't match the app registration tenant.

**Solution:**
1. Verify you're signed in to the correct Azure AD tenant
2. Check the Directory (tenant) ID matches
3. Ensure the app wasn't deleted

### "AADSTS7000215: Invalid client secret provided"

**Cause:** Client secret is incorrect or expired.

**Solution:**
1. Generate a new client secret in Azure Portal
2. Update OpenClaw configuration with new secret
3. Verify you copied the secret "Value", not "Secret ID"

### "AADSTS65001: The user or administrator has not consented"

**Cause:** Permissions haven't been granted yet.

**Solution:**
1. Complete the device code flow authentication
2. Accept the consent screen
3. If admin consent is required, request it from your IT admin

### "AADSTS700082: The refresh token has expired"

**Cause:** Refresh token validity expired (typical after 90 days of inactivity).

**Solution:**
1. Delete `~/.openclaw/auth/microsoft-graph.json`
2. Re-authenticate using device code flow

### "AADSTS50020: User account from identity provider does not exist in tenant"

**Cause:** Trying to use a personal Microsoft account with single-tenant app.

**Solution:**
1. Either use a work/school account
2. Or re-create the app registration with multi-tenant support

### "Insufficient privileges to complete the operation"

**Cause:** One or more required permissions are missing.

**Solution:**
1. Go to Azure Portal → App registrations → API permissions
2. Verify all required permissions are listed
3. Check that admin consent is granted (green checkmarks)
4. Re-authenticate if permissions were added after initial login

### "Request rate is large"

**Cause:** Hitting Microsoft Graph rate limits.

**Solution:**
- Wait for rate limit to reset (typically 1 hour)
- The skill automatically retries with exponential backoff
- Consider reducing request frequency

## Security Best Practices

1. **Rotate secrets regularly**
   - Set calendar reminder for secret expiration
   - Generate new secret before old one expires
   - Update OpenClaw config with new secret

2. **Use least privilege**
   - Only request permissions you actually need
   - Remove unused permissions

3. **Monitor app usage**
   - Azure Portal → App registrations → Your app → Sign-in logs
   - Review for suspicious activity

4. **Secure token storage**
   - Tokens stored at `~/.openclaw/auth/microsoft-graph.json`
   - File permissions should be 600 (owner read/write only)
   - Never commit token file to version control

5. **Use Azure AD Conditional Access** (if available)
   - Require MFA for sensitive operations
   - Restrict access by IP range
   - Monitor sign-in risk

## Additional Resources

- **Azure App Registration docs**: https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app
- **Microsoft Graph permissions reference**: https://learn.microsoft.com/en-us/graph/permissions-reference
- **Device code flow**: https://learn.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-device-code
- **Token lifetime**: https://learn.microsoft.com/en-us/azure/active-directory/develop/active-directory-configurable-token-lifetimes

## Support

If you encounter issues not covered in this guide:

1. Check Azure Portal → Azure Active Directory → Sign-in logs for error details
2. Review Microsoft Graph API error codes: https://learn.microsoft.com/en-us/graph/errors
3. Consult OpenClaw documentation
4. Reach out to your organization's IT support for admin consent issues
