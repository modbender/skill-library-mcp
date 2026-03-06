# Security

## Security Measures

This skill implements several security measures to protect user data and prevent abuse:

### 1. Localhost-Only Binding

The MCP server binds to `127.0.0.1` (localhost) only, not `0.0.0.0`. This means:
- ✅ Only local processes can connect
- ✅ No external network access
- ✅ Reduced attack surface

### 2. Restricted CORS Policy

CORS is limited to localhost origins:
```python
allow_origins=["http://localhost:*", "http://127.0.0.1:*"]
```

This prevents:
- ❌ Cross-site request forgery from external sites
- ❌ Unauthorized API access from web browsers
- ❌ Data exfiltration attempts

### 3. Environment-Based API Keys

API keys are loaded from environment variables, never hard-coded:
```python
etherscan_api_key = os.environ.get("ETHERSCAN_API_KEY")
```

Benefits:
- ✅ Keys not exposed in source code
- ✅ Easy to rotate keys
- ✅ Different keys per environment
- ✅ Keys excluded from version control

### 4. Read-Only Analysis

The skill never:
- ❌ Requests private keys
- ❌ Stores wallet credentials
- ❌ Executes transactions
- ❌ Accesses user wallets

All operations are read-only blockchain queries.

### 5. No Data Storage

- ❌ No user data is stored
- ❌ No query history retained
- ❌ No personal information collected

Each analysis is stateless.

## Best Practices

### For Users

1. **API Keys**: Always set via environment variables
   ```bash
   export ETHERSCAN_API_KEY="your_key_here"
   ```

2. **Never share**: Don't share your API keys publicly

3. **Rotate regularly**: Change API keys periodically

4. **Use free tier**: The free Etherscan API tier is sufficient

### For Developers

1. **No secrets in code**: Never commit API keys to git

2. **Use .gitignore**: Exclude sensitive files
   ```
   .env
   *.key
   secrets/
   ```

3. **Environment files**: Use `.env` files (not committed)
   ```bash
   # .env file (add to .gitignore!)
   ETHERSCAN_API_KEY=your_key_here
   ```

4. **Least privilege**: Request minimum necessary permissions

## Vulnerability Reporting

If you discover a security vulnerability:

1. **DO NOT** open a public issue
2. Email: security@trustclaw.dev
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours.

## Security Checklist

Before deploying:

- [ ] No API keys in source code
- [ ] Server binds to localhost only
- [ ] CORS restricted to localhost
- [ ] No private key handling
- [ ] No user data storage
- [ ] Input validation on all endpoints
- [ ] Rate limiting configured
- [ ] Dependencies up to date
- [ ] Security headers configured

## Updates & Patches

Security updates are released as:
- **Critical**: Immediate (within 24h)
- **High**: Within 1 week
- **Medium**: Within 1 month
- **Low**: Next release cycle

Subscribe to security advisories:
- Watch repository for security issues
- Follow @trustclaw on Twitter/X
- Join our Discord for announcements

## Compliance

This skill complies with:
- ✅ OWASP API Security Top 10
- ✅ GDPR (no personal data collected)
- ✅ SOC 2 Type II principles
- ✅ NIST Cybersecurity Framework

## License

See LICENSE file for terms.

---

**Security is everyone's responsibility. Report issues, practice safe coding, and stay vigilant!**

