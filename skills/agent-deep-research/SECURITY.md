# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest release | Yes |
| Older releases | No |

Only the latest release receives security fixes. Update to the latest version to stay protected.

## Reporting a Vulnerability

**Do not report security vulnerabilities through public GitHub issues.**

Instead, use [GitHub Security Advisories](https://github.com/24601/agent-deep-research/security/advisories/new) to report vulnerabilities privately.

Please include:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## Response Timeline

- **Acknowledgment**: within 48 hours
- **Initial assessment**: within 7 days
- **Fix release**: as soon as practical, typically within 30 days for confirmed vulnerabilities

## API Key Handling

This project uses Google API keys for Gemini API access. Keys are read exclusively from environment variables (`GEMINI_DEEP_RESEARCH_API_KEY`, `GOOGLE_API_KEY`, `GEMINI_API_KEY`) and are never written to disk or logged. If you discover a code path that exposes API keys, please report it immediately.
