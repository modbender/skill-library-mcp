# Security Guidelines for Zen+ Health OpenClaw Skill

## Overview

The Zen+ Health OpenClaw skill uses **personal API keys** for authentication. This document explains the security model and best practices.

## Authentication Method

### API Key Format

```
zen_ak_<40 hexadecimal characters>
```

Example: `zen_ak_a1b2c3d4e5f6789012345678901234567890abcd`

### Storage and Hashing

- **Client-side**: Store API keys in environment variables (never hardcode)
- **Server-side**: All API keys are SHA-256 hashed before storage
- **Transmission**: Always use HTTPS (`https://api.zenplus.health`)

## Permissions and Scopes

API keys for this skill are **read-only** with limited scopes:

| Scope | Access | Can Modify? |
|-------|--------|-------------|
| `user:restricted` | View limited profile data | ❌ No |
| `timeline:read` | View activity history | ❌ No |
| `notification:read` | View notifications | ❌ No |
| `catalog:read` | Browse task catalogue | ❌ No |
| `working_hours:read` | View working hours | ❌ No |

**This skill cannot**:
- Modify your profile
- Create or delete tasks
- Send notifications
- Access payment information
- Change your settings

## Best Practices

### ✅ Do

- Store API keys in environment variables (`ZEN_API_KEY`)
- Use separate API keys for different integrations
- Revoke keys immediately if compromised
- Monitor API key usage in your Zen+ Health settings
- Use the minimum required scopes

### ❌ Don't

- Hardcode API keys in scripts or code
- Share API keys in chat logs or screenshots
- Share API keys anywhere
- Commit API keys to version control
- Use production keys for testing
- Grant unnecessary scopes

## Key Management

### Creating a Key

1. Log in to [zenplus.health](https://app.zenplus.health)
2. Navigate to **Settings → API Keys**
3. Click **"Create New API Key"**
4. Name it (e.g., "OpenClaw Integration")
5. **Copy the key immediately** - it won't be shown again

### Revoking a Key

1. Go to **Settings → API Keys**
2. Find the key in your list
3. Click **"Revoke"**
4. Key is immediately invalidated across all systems

### Key Rotation

Rotate API keys every 90 days or immediately if:
- Key may have been exposed
- Employee/contractor leaves
- Integration is no longer in use
- Suspicious API activity detected

## Rate Limiting

API keys are rate-limited to prevent abuse. Rate limit headers are returned in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1707824400
```

## Security Model

### What Zen+ Health Protects

✅ API keys are secure
✅ HTTPS enforced for all API requests  
✅ API keys are single-user scoped  
✅ API keys have no access to change data
✅ Audit logs for all API requests

### What You Must Protect

🔐 Keep `ZEN_API_KEY` environment variable secure  
🔐 Don't share keys between users  
🔐 Revoke keys when no longer needed  
🔐 Use separate keys for dev/staging/production

## Privacy Considerations

### Data Access

This skill can read:
- Your wellness notifications
- Your activity timeline
- Your profile information (name, email, preferences)
- Available task catalogue (public data)

This skill **cannot** read:
- Other users' data
- Payment information
- Password or credentials
- Private notes, journal entries, screening results, past task activity, check-ins.

### Data Transmission

- All API requests use HTTPS/TLS 1.3
- Data is encrypted in transit
- No data is cached by OpenClaw (unless you configure it)
- API responses may be logged by your OpenClaw instance

## Incident Response

### If Your API Key is Compromised

1. **Immediately revoke** the key at [zenplus.health/settings/api-keys](https://zenplus.health/settings/api-keys)
2. **Review usage logs** for unauthorized access
3. **Create a new key** with a unique name
4. **Update your environment variables** with the new key
5. **Contact support** if suspicious activity detected: [support@zenplus.health](mailto:support@zenplus.health)

### Reporting Security Issues

Found a security vulnerability? Report it responsibly:

- **Email**: [security@zenplus.health](mailto:security@zenplus.health)

**Do not** disclose security vulnerabilities publicly until we've had a chance to address them.

## Questions?

- **Documentation**: [zenplus.health/api/docs](https://zenplus.health/api/docs)
- **Support**: [support@zenplus.health](mailto:support@zenplus.health)
- **Security**: [security@zenplus.health](mailto:security@zenplus.health)
