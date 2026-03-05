# Security Policy

## Reporting Vulnerabilities

If you discover a security vulnerability in this project, please report it responsibly.

**Do not open a public GitHub issue for security vulnerabilities.**

Instead, use one of the following methods:

1. **GitHub Security Advisories** (preferred): Go to the repository's Security tab and click "Report a vulnerability" to submit a private advisory.
2. **Email**: Send details to the maintainers via the contact information in the repository profile.

Please include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if you have one)

We will acknowledge receipt within 48 hours and provide a timeline for resolution.

## Scope

This security policy covers:

- **Skill code**: SKILL.md manifests and sub-skill definitions
- **Scripts**: All Python scripts in `scripts/` (onboard, doctor, schema)
- **Rules content**: Markdown files in `rules/` that may contain executable examples
- **CI/CD workflows**: GitHub Actions workflow definitions

## API Key and Credential Safety

This skill interacts with SurrealDB instances and may be used alongside various AI agent frameworks. Follow these rules strictly:

- **Never commit API keys, tokens, or passwords** to the repository.
- **Use environment variables** for all credentials:
  ```bash
  export SURREAL_USER="root"
  export SURREAL_PASS="root"
  export SURREAL_ENDPOINT="http://localhost:8000"
  ```
- The `.gitignore` file excludes `.env` files. Use `.env` for local development credentials.
- Scripts should read credentials from environment variables or CLI arguments, never from hardcoded values.

## Database Credential Handling

When working with SurrealDB instances:

- **Development**: Use default `root`/`root` credentials only for local development. Never use these in production.
- **Production**: Use SurrealDB's built-in access control system with properly scoped credentials.
- **Connection strings**: Never log or print full connection strings that include credentials.
- **Scripts**: The `onboard.py` and `schema.py` scripts accept credentials via CLI flags or environment variables. They do not persist credentials to disk.

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 1.0.x   | Yes       |

## Security Best Practices for Users

When using this skill with AI coding agents:

1. Review any generated SurrealQL before executing it against production databases.
2. Use read-only database credentials when running introspection scripts.
3. Scope agent permissions to the minimum required namespace and database.
4. Audit the `rules/security.md` guide for SurrealDB-specific hardening recommendations.
