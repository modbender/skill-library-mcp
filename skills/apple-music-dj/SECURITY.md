# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 3.x     | ✅ Yes    |
| < 3.0   | ❌ No     |

## Reporting a Vulnerability

If you discover a security vulnerability in Apple Music DJ, please report it responsibly.

**Do NOT open a public GitHub issue for security vulnerabilities.**

Instead, email: **<and3rn3t@icloud.com>**

Include:

- Description of the vulnerability
- Steps to reproduce
- Impact assessment (what data could be exposed, etc.)
- Any suggested fix (optional)

### What qualifies as a security issue

- Token exposure (dev token or user token leaked in logs, output, or cache files)
- Cache files containing sensitive data beyond what's documented
- Scripts making network requests to undocumented endpoints
- File permission issues allowing unauthorized access to cached data
- Code injection via user-supplied arguments (artist names, playlist names, etc.)

### What does NOT qualify

- Apple Music API rate limiting (expected behavior)
- Token expiration (documented, not a vulnerability)
- Missing features or bugs that don't expose data

## Response Timeline

- **Acknowledgment:** Within 48 hours
- **Assessment:** Within 7 days
- **Fix (if confirmed):** Targeted within 14 days, depending on severity

## Security Best Practices for Users

1. **Never commit tokens** — Use environment variables, not hardcoded values
2. **Keep `.env` in `.gitignore`** — The repo ships with this configured
3. **Rotate tokens periodically** — Dev tokens support up to 6-month lifetime
4. **Review cache contents** — `~/.apple-music-dj/` contains your taste profile
5. **Clear cache when sharing machines** — `rm -rf ~/.apple-music-dj/`
