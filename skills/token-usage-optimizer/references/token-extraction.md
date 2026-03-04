# Token Extraction Guide

How to get your Claude Code OAuth tokens for usage monitoring.

## Method 1: Via Claude CLI (Recommended)

### macOS

1. **Authenticate with Claude CLI:**
   ```bash
   claude auth login
   ```

2. **Find the auth file:**
   ```bash
   # Try these locations:
   cat ~/.claude/auth.json
   cat ~/Library/Application\ Support/Claude/auth.json
   
   # Or search:
   find ~/Library/Application\ Support -name "*auth*" -type f 2>/dev/null | grep -i claude
   ```

3. **Extract tokens from JSON:**
   ```json
   {
     "accessToken": "sk-ant-oat01-...",
     "refreshToken": "sk-ant-ort01-...",
     "expiresAt": 1234567890000
   }
   ```

### Linux

1. **Authenticate:**
   ```bash
   claude auth login
   ```

2. **Find auth data:**
   ```bash
   # Common locations:
   cat ~/.config/claude/auth.json
   cat ~/.claude/auth.json
   
   # Or use secret-tool:
   secret-tool search application "Claude Code"
   ```

## Method 2: Browser DevTools

If you can't find the auth file:

1. Open https://claude.ai in your browser
2. Sign in to your account
3. Open DevTools (F12 or Cmd+Opt+I)
4. Go to **Application** → **Local Storage** → `https://claude.ai`
5. Look for keys like `auth_token`, `oauth_token`, or similar
6. Copy the values

**Note:** This may not work for all setups. Method 1 is preferred.

## Method 3: Manual OAuth Flow

Advanced users can implement the OAuth flow manually:

1. **Authorization endpoint:**
   ```
   https://claude.ai/oauth/authorize
   ```

2. **Token endpoint:**
   ```
   https://platform.claude.com/oauth/token
   ```

3. **Required scopes:**
   - `user:inference`
   - `user:sessions:claude_code`
   - `user:profile`

See Anthropic OAuth docs for full details.

## Token Format

- **Access Token:** `sk-ant-oat01-...` (long alphanumeric string)
- **Refresh Token:** `sk-ant-ort01-...` (long alphanumeric string)

## Security

- ✅ **Do:** Store tokens in `.tokens` file (gitignored)
- ✅ **Do:** Set file permissions to 600 (`chmod 600 .tokens`)
- ❌ **Don't:** Commit tokens to git
- ❌ **Don't:** Share tokens publicly
- ❌ **Don't:** Use someone else's tokens

## Token Expiry

- Access tokens expire after a certain time
- Use refresh token to get a new access token
- This skill doesn't auto-refresh yet (manual re-run of setup required)

## Troubleshooting

**"No auth file found"**
→ Run `claude auth login` first

**"Permission denied"**
→ Check file permissions: `ls -l ~/.claude/auth.json`

**"Token invalid"**
→ Token may have expired. Re-run `claude auth login`
