# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it by:

1. **Do NOT** open a public issue
2. Email security@parcosta.dev with details
3. Include steps to reproduce the vulnerability
4. Allow time for assessment and remediation before public disclosure

We will respond within 48 hours and work with you to address the issue.

## Security Measures

This project implements the following security measures:

### Input Sanitization

- All user inputs are validated before use
- Repository names must match `^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$`
- Agent IDs must match `^[a-zA-Z0-9_-]+$`
- No shell command injection possible through validated inputs

### Authentication

- API key is read from environment variable only
- No hardcoded credentials in source code
- Basic Auth with base64 encoding
- API key never logged or displayed

### Safe File Handling

- Temporary files created with `mktemp`
- Cache directory uses XDG standard with fallback
- Proper cleanup on exit
- No world-writable files

### Command Execution

- No user-controlled command execution
- All external commands use hardcoded paths where possible
- `curl` options are fixed, not user-configurable

### Dependencies

- Minimal dependencies: bash, curl, jq, base64
- All dependencies are standard system tools
- No third-party libraries or packages

## Security Scanning

This project uses:

- **shellcheck**: Static analysis for shell scripts
- **Trivy**: Vulnerability scanner
- **GitHub CodeQL**: Automated security analysis
- **Secret detection**: Automated scanning for secrets in PRs

## Best Practices for Users

### API Key Management

1. Store `CURSOR_API_KEY` in `~/.openclaw/.env` with restricted permissions:
   ```bash
   chmod 600 ~/.openclaw/.env
   ```

2. Never commit API keys to version control

3. Rotate keys regularly

4. Use separate keys for different environments

### Repository Access

1. Only grant Cursor Cloud Agents access to repositories that need it

2. Regularly review the Cursor GitHub App permissions

3. Remove access for repositories no longer using the skill

### Cache Security

1. Cache files are stored in `~/.cache/cursor-api/` by default

2. Ensure your home directory has appropriate permissions:
   ```bash
   chmod 700 ~
   ```

3. Clear cache periodically if on a shared system:
   ```bash
   cursor-api.sh clear-cache
   ```

## Security Checklist for Contributors

Before submitting a PR, ensure:

- [ ] No secrets or credentials in code
- [ ] All user inputs are sanitized
- [ ] No command injection vectors
- [ ] Temporary files are cleaned up
- [ ] shellcheck passes without errors
- [ ] Tests cover security-sensitive code paths

## Automated Security Scanning Notes

This skill may trigger automated security scanners due to legitimate patterns required for API integration:

### Patterns That May Trigger Scanners

1. **base64 encoding**: Used for HTTP Basic Authentication (RFC 7617) per Cursor API specification
   - Location: `scripts/cursor-api.sh` in `get_auth_header()`
   - Purpose: Encode API key for Authorization header
   - Not obfuscation: This is standard HTTP Basic Auth

2. **External API calls**: Calls to `api.cursor.com`
   - Purpose: Required functionality for Cursor Cloud Agents
   - No user-controlled URLs: Endpoint is hardcoded

3. **curl with variables**: Dynamic curl commands
   - Purpose: HTTP requests to Cursor API
   - Input validation: All variables are sanitized before use
   - No command injection: User inputs don't reach shell commands directly

These patterns are necessary for the skill's core functionality and are implemented securely with proper input validation and sanitization.

## Known Limitations

1. **Cache files**: Response cache is stored unencrypted on disk. On shared systems, other users with appropriate permissions could read cached API responses.

2. **API Key in environment**: The API key is available in the process environment. Other processes running as the same user could potentially access it.

3. **Rate limiting**: Local rate limiting helps prevent abuse but doesn't guarantee API compliance under all edge cases.

## Security Updates

Security updates will be released as patch versions (e.g., 1.0.1). Users should:

1. Watch this repository for security advisories
2. Update promptly when security fixes are released
3. Review the changelog for security-related changes

## Acknowledgments

We thank the following for responsible disclosure of security issues:

- (None yet - this section will be updated as appropriate)
