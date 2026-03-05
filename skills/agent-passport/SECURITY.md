# Security Policy

## Supported Versions

We maintain security fixes on the latest published version only.

| Version | Supported |
|---------|-----------|
| 2.x (latest) | Yes |
| 1.x | No |

## Reporting a Vulnerability

Do not open a public issue for security vulnerabilities.

Email us at: **security@agentpassportai.com**

Include:
- A description of the vulnerability
- Steps to reproduce it
- The potential impact
- Any suggested fix (optional)

We aim to respond within 72 hours and will keep you updated as we work on a fix.

## Scope

Security issues we care most about:

- Mandate bypass (an agent bypassing consent gates it should not be able to bypass)
- Audit trail tampering (manipulation of the ledger or audit log)
- Privilege escalation via the KYA or mandate schema
- Shell injection in the mandate-ledger script

Out of scope:

- Issues requiring physical access to the machine
- Issues in dependencies of the runtime environment (bash, jq, etc.)

## Disclosure

We follow a 90-day coordinated disclosure window. After a fix is released, we will credit the reporter in the release notes unless they prefer to remain anonymous.
