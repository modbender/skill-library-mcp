# Security Considerations

This skill interacts with Twitter/X using authenticated sessions. Please read and understand these security implications.

## ⚠️ Cookie Authentication

This skill uses the `bird` CLI which requires Twitter session cookies (`AUTH_TOKEN` and `CT0`). These are **sensitive credentials** that grant full access to your Twitter account.

### Risks

1. **Account Access**: Anyone with these cookies can act as you on Twitter
2. **Session Hijacking**: Cookies can be stolen if exposed
3. **Terms of Service**: Automated access may violate Twitter's ToS
4. **Rate Limiting**: Excessive requests may trigger account restrictions

### Best Practices

- **Never commit cookies** to version control
- **Use environment variables** instead of hardcoded values
- **Rotate cookies periodically** (re-login to invalidate old sessions)
- **Monitor account activity** for unauthorized actions
- **Use a dedicated account** for scraping if possible

## 🔒 Safe Credential Storage

### Environment Variables (Recommended)

```bash
# In your shell profile (~/.bashrc, ~/.zshrc)
export AUTH_TOKEN="your_token_here"
export CT0="your_ct0_here"

# Or use a .env file (NOT committed to git)
# and load with: source .env
```

### Getting Cookies

1. Log into Twitter in your browser
2. Open Developer Tools (F12)
3. Go to Application → Cookies → twitter.com
4. Copy `auth_token` and `ct0` values

**Note**: Cookies expire when you log out or after extended periods.

## 📁 Data Storage

Tweets are stored locally in `~/.openclaw/workspace/data/tweets/`.

### What's Stored

- Tweet text and metadata
- Author information
- Engagement metrics
- URLs and media references

### Recommendations

- **Don't share** stored tweet files containing private account data
- **Be mindful** of storing tweets from protected accounts
- **Clean up** old data you no longer need

## 🚫 What NOT to Do

1. **Don't share cookies** in issues, chats, or public posts
2. **Don't commit** the `data/` directory to version control
3. **Don't scrape** excessively (respect rate limits)
4. **Don't store** credentials in script files
5. **Don't hardcode** any authentication tokens

## ✅ What This Skill Does

- ✅ Reads cookies from environment variables only
- ✅ Stores only tweet content locally
- ✅ No credential logging
- ✅ No data exfiltration

## ❌ What This Skill Does NOT Do

- ❌ Store your cookies in files
- ❌ Transmit cookies anywhere except to Twitter
- ❌ Log authentication tokens
- ❌ Access accounts without explicit credentials

## Rate Limits

Twitter has rate limits. Excessive requests may result in:

- Temporary blocks
- CAPTCHA challenges
- Account suspension

**Recommendations:**
- Fetch reasonable amounts (20-50 tweets)
- Don't run automated scripts too frequently
- Use `--count` to limit requests

## Incident Response

If you suspect your cookies were compromised:

1. **Log out** of Twitter on all devices
2. **Change password** immediately
3. **Revoke** third-party app access
4. **Generate new cookies** by logging in again
5. **Review** recent account activity

## Reporting Security Issues

If you find a security vulnerability in this skill:

1. **DO NOT** open a public GitHub issue
2. Email: security@openclaw.dev
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact

We will respond within 48 hours.

## Audit Status

- **Last audit:** 2026-02-21
- **Status:** ✅ No hardcoded credentials
- **Status:** ✅ No sensitive data exposure
- **Status:** ✅ Cookies read from env vars only
- **Status:** ✅ Safe patterns documented

---

**Remember:** Your Twitter session cookies are like your password. Treat them with the same level of security.
