# Kalshi API Setup Guide

## Getting API Credentials

1. **Sign up for Kalshi** at https://kalshi.com if you don't have an account

2. **Generate API credentials:**
   - Log in to Kalshi
   - Go to Settings → API
   - Click "Generate API Key"
   - Save your API Key ID (UUID format)
   - Download the private key PEM file

3. **Save the private key:**

   ```bash
   # Move the downloaded key to a secure location
   mv ~/Downloads/kalshi_private_key.pem ~/.openclaw/kalshi_private_key.pem
   chmod 600 ~/.openclaw/kalshi_private_key.pem
   ```

4. **Set environment variables:**

   Add to your shell config file (`~/.zshrc`, `~/.bashrc`, etc.):

   ```bash
   export KALSHI_API_KEY_ID="your-api-key-uuid-here"
   export KALSHI_PRIVATE_KEY_PATH="$HOME/.openclaw/kalshi_private_key.pem"
   ```

   Or in OpenClaw's config:

   ```yaml
   env:
     KALSHI_API_KEY_ID: "your-api-key-uuid-here"
     KALSHI_PRIVATE_KEY_PATH: "/Users/yourusername/.openclaw/kalshi_private_key.pem"
   ```

5. **Reload your shell:**

   ```bash
   source ~/.zshrc  # or ~/.bashrc
   ```

6. **Test the connection:**
   ```bash
   node /path/to/kalshi-cli.mjs balance
   ```

## Security Notes

- **Never commit your private key** to git or share it publicly
- The private key is your authentication - treat it like a password
- API keys can be revoked from the Kalshi settings page
- Use file permissions to restrict access: `chmod 600 kalshi_private_key.pem`

## Demo vs Production

The CLI uses **production** by default: `https://api.elections.kalshi.com`

For testing, Kalshi offers a demo environment at `https://demo-api.kalshi.co`

To use demo:

1. Get separate demo API credentials from Kalshi
2. Modify `BASE_URL` in `kalshi-cli.mjs` line 21

## Rate Limits

Kalshi doesn't publish explicit rate limits, but best practices:

- Don't poll endpoints in tight loops
- Cache results when appropriate (trending markets don't change second-to-second)
- Batch operations when possible

## Troubleshooting

**Error: "Missing env vars"**

- Verify `KALSHI_API_KEY_ID` and `KALSHI_PRIVATE_KEY_PATH` are set
- Check: `echo $KALSHI_API_KEY_ID`

**Error: "ENOENT: no such file or directory"**

- Verify the private key path is correct
- Check: `ls -l $KALSHI_PRIVATE_KEY_PATH`

**Error: "401 Unauthorized" or signature errors**

- Your API key may be invalid or revoked
- Generate a new key pair from Kalshi settings
- Make sure the private key matches the API key ID

**Error: "INSUFFICIENT_BALANCE"**

- You need to deposit funds at https://kalshi.com
- Check balance with: `node kalshi-cli.mjs balance`
