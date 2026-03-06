# Security Policy

## Supported Versions

We release security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| 1.0.x   | :white_check_mark: (until 2026-06-06) |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: **security@anmolnagpal.com**

Include the following information:

1. **Description** of the vulnerability
2. **Steps to reproduce** the issue
3. **Potential impact** (what could an attacker do?)
4. **Suggested fix** (if you have one)
5. **Your contact information** (for follow-up)

### What to Expect

- **Acknowledgment:** Within 48 hours
- **Initial assessment:** Within 1 week
- **Fix timeline:** Depends on severity
  - Critical: Within 7 days
  - High: Within 14 days
  - Medium: Within 30 days
  - Low: Next regular release

### Security Update Process

1. We investigate and confirm the vulnerability
2. We develop a fix
3. We test the fix
4. We release a security update
5. We publish a security advisory

## Security Best Practices

When using these skills:

### DO ✅

- **Test on non-production repos** first
- **Review all changes** before applying
- **Use exclude patterns** for critical repos
- **Enable audit logging** in GitHub
- **Rotate credentials** regularly
- **Follow SAFETY.md** procedures
- **Keep configs private** (don't commit secrets)
- **Use minimal permissions** for automation tokens

### DON'T ❌

- **Don't commit secrets** to configs
- **Don't skip validation** steps
- **Don't run on production** without testing
- **Don't share tokens** publicly
- **Don't ignore errors** during execution
- **Don't bypass safety checks**

## Known Security Considerations

### 1. GitHub Token Permissions

Required minimum permissions:
```yaml
contents: write      # For commits and releases
workflows: write     # For workflow updates
pull-requests: write # If using PR workflow
```

**Recommendation:** Use fine-grained personal access tokens with repository-specific scope.

### 2. Secrets Management

These skills do NOT store secrets. Configuration files should only contain:
- Repository patterns
- Version numbers
- Organization names
- Workflow SHAs

**Never commit:**
- API tokens
- Private keys
- Passwords
- Credentials

### 3. Code Execution

Shell scripts execute with your user permissions. Always:
- Review scripts before running
- Run in isolated environments for testing
- Use version control for tracking changes
- Maintain audit logs

### 4. Supply Chain Security

We follow these practices:
- MIT license for transparency
- No external dependencies in core skills
- Minimal shell script usage
- Open source for community review

## Scope

### In Scope
- Vulnerabilities in core skills
- Vulnerabilities in scripts
- Security issues in documentation
- Misconfigurations that could lead to security issues
- Dependency vulnerabilities

### Out of Scope
- Issues in GitHub Copilot itself
- Issues in Terraform or cloud providers
- Issues in user's custom configurations
- Social engineering attacks
- Brute force attacks on external systems

## Bug Bounty

We currently do not offer a bug bounty program, but we deeply appreciate security researchers who responsibly disclose vulnerabilities. We will:

- Publicly credit researchers (if desired)
- Provide a detailed write-up of the fix
- Share the advisory once fixed

## Security Advisories

Published advisories: [GitHub Security Advisories](https://github.com/anmolnagpal/terraform-ai-skills/security/advisories)

## Questions?

For security questions that are not vulnerability reports, please open a [GitHub Discussion](https://github.com/anmolnagpal/terraform-ai-skills/issues) or email security@anmolnagpal.com.

---

**Last Updated:** 2026-02-06
