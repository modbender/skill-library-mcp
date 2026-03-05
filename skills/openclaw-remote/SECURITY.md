# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this skill or in the procedures it documents, please report it to:

- **Email**: security@ishi.so
- **Discord**: [Join the Claw Discord](https://discord.gg/claw) and DM a moderator

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if you have one)

## Security Best Practices

This skill documents security hardening procedures for OpenClaw installations. When following these procedures:

1. **Always test in a non-production environment first**
2. **Git-track all config changes for rollback capability**
3. **Verify localhost-only binding before exposing to networks**
4. **Rotate API keys every 90 days minimum**
5. **Use dedicated bot accounts, never personal credentials**

## What This Skill Does NOT Do

This skill does NOT:
- Store or transmit API keys
- Modify your OpenClaw installation without explicit user consent
- Connect to external services (beyond documented OpenClaw operations)
- Execute arbitrary code without user review

## OpenClaw Security

For security issues with OpenClaw itself (not this skill), please report to the [OpenClaw repository](https://github.com/openclaw).

## Disclosure Policy

- We will acknowledge receipt of your vulnerability report within 48 hours
- We will provide a detailed response within 7 days
- We will work with you to understand and resolve the issue
- We will credit you in the security advisory (unless you prefer to remain anonymous)
