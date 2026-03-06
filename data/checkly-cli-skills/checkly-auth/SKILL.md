---
name: checkly-auth
description: Manage Checkly CLI authentication including login/logout, check auth status, and configure API credentials. Use when setting up Checkly CLI for first time, troubleshooting auth issues, or switching Checkly accounts. Triggers on checkly login, checkly logout, authentication, API key, account ID, credentials.
---

# checkly auth

Manage Checkly CLI authentication.

## Quick start

```bash
# Interactive login (browser-based)
npx checkly login

# Check authentication status
npx checkly whoami

# Manual configuration (for CI/CD)
export CHECKLY_API_KEY="your-api-key"
export CHECKLY_ACCOUNT_ID="your-account-id"
```

## Authentication methods

### Interactive login (recommended for local development)

```bash
npx checkly login
```

Opens browser to authenticate and automatically saves credentials to your system config.

**Credential storage location:**
- Linux/macOS: `~/.config/@checkly/cli/config.json`
- Windows: `%APPDATA%\@checkly\cli\config.json`

### Environment variables (recommended for CI/CD)

```bash
export CHECKLY_API_KEY="cu_abc123..."
export CHECKLY_ACCOUNT_ID="12345"

# Test authentication
npx checkly whoami
```

**Getting your credentials:**
1. Log into [app.checklyhq.com](https://app.checklyhq.com)
2. Navigate to Account Settings → API Keys
3. Create new API key with appropriate permissions
4. Copy Account ID from URL or account settings

### Configuration file (manual)

Create/edit config file at `~/.config/@checkly/cli/config.json`:

```json
{
  "apiKey": "cu_abc123...",
  "accountId": "12345"
}
```

## Workflows

### First-time setup

1. **Sign up for Checkly account** (if needed):
   ```bash
   # Opens signup page
   npx checkly login
   ```

2. **Authenticate CLI**:
   ```bash
   npx checkly login
   ```

3. **Verify authentication**:
   ```bash
   npx checkly whoami
   ```

   Expected output:
   ```
   Logged in as john@example.com
   Account: Acme Corp (ID: 12345)
   ```

4. **Initialize project**:
   ```bash
   npm create checkly@latest
   ```

### Switching accounts

If you have multiple Checkly accounts:

1. **Logout from current account**:
   ```bash
   # Manual logout (delete config)
   rm ~/.config/@checkly/cli/config.json
   ```

2. **Login to different account**:
   ```bash
   npx checkly login
   ```

3. **Verify new account**:
   ```bash
   npx checkly whoami
   ```

### CI/CD authentication

For automated pipelines (GitHub Actions, GitLab CI, etc.):

1. **Create API key in Checkly UI**:
   - Navigate to Account Settings → API Keys
   - Click "Create API Key"
   - Name: "CI/CD Pipeline"
   - Permissions: Read/Write (for deploy)
   - Copy the key (starts with `cu_`)

2. **Add secrets to CI/CD platform**:
   - `CHECKLY_API_KEY`: Your API key
   - `CHECKLY_ACCOUNT_ID`: Your account ID

3. **Use in pipeline**:
   ```yaml
   # GitHub Actions example
   - name: Test checks
     env:
       CHECKLY_API_KEY: ${{ secrets.CHECKLY_API_KEY }}
       CHECKLY_ACCOUNT_ID: ${{ secrets.CHECKLY_ACCOUNT_ID }}
     run: npx checkly test
   
   - name: Deploy checks
     env:
       CHECKLY_API_KEY: ${{ secrets.CHECKLY_API_KEY }}
       CHECKLY_ACCOUNT_ID: ${{ secrets.CHECKLY_ACCOUNT_ID }}
     run: npx checkly deploy --force
   ```

## Troubleshooting

### "Could not find Checkly credentials"

**Cause**: No authentication configured

**Solution**:
```bash
# Option 1: Interactive login
npx checkly login

# Option 2: Set environment variables
export CHECKLY_API_KEY="your-key"
export CHECKLY_ACCOUNT_ID="your-account-id"
```

### "401 Unauthorized"

**Possible causes**:
- API key has been deleted or revoked
- API key doesn't have required permissions
- Account ID doesn't match API key

**Solution**:
1. Verify credentials:
   ```bash
   npx checkly whoami
   ```

2. If invalid, re-authenticate:
   ```bash
   npx checkly login
   ```

3. For CI/CD, regenerate API key in Checkly UI

### "Account not found"

**Cause**: Account ID is incorrect

**Solution**:
1. Log into [app.checklyhq.com](https://app.checklyhq.com)
2. Check URL: `app.checklyhq.com/accounts/{ACCOUNT_ID}/...`
3. Or check Account Settings → Account ID
4. Update `CHECKLY_ACCOUNT_ID` environment variable

### Permission errors during deploy

**Cause**: API key has read-only permissions

**Solution**:
1. Go to Account Settings → API Keys in Checkly UI
2. Create new API key with "Read/Write" permissions
3. Update your API key

## Environment variables reference

| Variable | Required | Description |
|----------|----------|-------------|
| `CHECKLY_API_KEY` | Yes | API key (starts with `cu_`) |
| `CHECKLY_ACCOUNT_ID` | Yes | Numeric account ID |
| `CHECKLY_API_URL` | No | Override API URL (default: `https://api.checklyhq.com`) |
| `CHECKLY_SKIP_AUTH` | No | Skip authentication (for debugging flags) |

## Security best practices

### Local development

- ✅ Use `npx checkly login` (credentials stored securely)
- ✅ Add config file to `.gitignore` (if using manual config)
- ❌ Don't commit API keys to version control

### CI/CD pipelines

- ✅ Store credentials as encrypted secrets
- ✅ Use API keys with minimal required permissions
- ✅ Rotate API keys regularly
- ❌ Don't log API keys in pipeline output

### API key management

- ✅ Create separate API keys for different purposes (CI/CD, local dev)
- ✅ Name keys descriptively ("GitHub Actions Deploy", "John's Laptop")
- ✅ Revoke unused or compromised keys immediately
- ❌ Don't share API keys between team members

## Related Skills

**Next steps after authentication:**
- See `checkly-config` to configure your project
- See `checkly-test` to run checks locally
- See `checkly-deploy` to deploy checks to Checkly

**Project setup:**
- New project: Use `npm create checkly@latest` (includes auth setup)
- Existing project: Install `checkly` package and authenticate
