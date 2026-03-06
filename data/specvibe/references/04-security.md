# Reference: 04 - Security (OWASP 2025 Edition)

Security is not a feature; it's a prerequisite. This guide aligns with the **OWASP Top 10 for 2025** [1] and the principle of **Zero Trust Architecture** ("never trust, always verify") [2]. Every line of code should be written with a security-first mindset.

## The Delegate/Review/Own Model for Security

- **Delegate**: Use automated tools (SAST, DAST, dependency scanners) in your CI/CD pipeline to catch common vulnerabilities. Ask the AI to scan for basic security flaws.
- **Review**: A human must review all security-critical code, especially authentication, authorization, and input validation logic. Do not blindly trust AI-generated security code.
- **Own**: The ultimate responsibility for the application's security posture rests with the development team.

## OWASP Top 10: 2025 Checklist

This checklist must be reviewed before any production deployment.

| ID | Risk | Mitigation Strategy |
| :--- | :--- | :--- |
| **A01** | **Broken Access Control** | Implement role-based access control (RBAC). Deny by default. Verify permissions on every request. Use Row-Level Security (RLS) for multi-tenant applications. |
| **A02** | **Security Misconfiguration** | Use Infrastructure as Code (IaC) to manage configuration. Remove all default passwords and unused features. Harden HTTP headers (CSP, HSTS, X-Frame-Options). |
| **A03** | **Software Supply Chain Failures** | Use a dependency scanner (e.g., `npm audit`, Snyk) to find known vulnerabilities in your libraries. Pin dependencies to specific versions. Verify the integrity of packages. |
| **A04** | **Cryptographic Failures** | Use modern, industry-standard encryption (TLS 1.3, Argon2 for hashing). Never roll your own crypto. Store secrets in a dedicated vault. |
| **A05** | **Injection** | Use prepared statements and parameterized queries for all database access. Sanitize user input before rendering in the UI. |
| **A06** | **Insecure Design** | Security must be part of the design phase. Use threat modeling to identify potential risks before writing code. |
| **A07** | **Authentication Failures** | Enforce multi-factor authentication (MFA). Implement strong password policies. Use rate limiting to prevent brute-force attacks. |
| **A08** | **Software or Data Integrity Failures** | Use digital signatures or checksums to verify the integrity of data and software updates. Protect your CI/CD pipeline from unauthorized access. |
| **A09** | **Security Logging and Alerting Failures** | Log all security-relevant events (logins, failed logins, access denials). Set up automated alerts for suspicious activity. Ensure logs do not contain sensitive data (PII, tokens). |
| **A10** | **Mishandling of Exceptional Conditions** | Ensure that error messages do not leak sensitive information (stack traces, internal paths). Implement robust, structured error handling that fails securely (fail-closed, not fail-open). |

## Practical Implementation

### 1. Authentication (AuthN): Who are you?

- **Use Standard Protocols**: Use battle-tested standards like OAuth 2.0 or OpenID Connect (OIDC). For simple token-based auth, use JSON Web Tokens (JWT).
- **Secure JWTs**: Use a strong, randomly generated secret key (at least 256 bits) loaded from an environment variable. Set a short expiration time for access tokens (e.g., 15 minutes) and use refresh tokens for longer sessions.
- **Password Security**: NEVER store passwords in plain text. Use a strong, slow hashing algorithm like Argon2 or bcrypt.

### 2. Authorization (AuthZ): What can you do?

- **Principle of Least Privilege**: Users should only have the minimum permissions necessary.
- **Implement Middleware**: Authorization checks should be implemented as middleware that runs before your API endpoint logic.
- **Role-Based Access Control (RBAC)**: Assign roles to users (e.g., `ADMIN`, `JUDGE`, `VIEWER`) and define permissions for each role.
- **Row-Level Security (RLS)**: For multi-tenant applications, ensure that users from one organization cannot access data from another.

### 3. Input Validation: Trust Nothing

**All data coming from the client is untrusted.** This is the most important rule of web security.

- **Validate at the Edge**: Validate all incoming data at the API boundary before it reaches your business logic.
- **Use a Schema-Based Library**: Use a library like **Zod** or **Joi** to define schemas for your request bodies, parameters, and query strings.
- **Prevent Injection Attacks**: Use an ORM or parameterized queries to prevent SQL injection. Sanitize all user-provided data to prevent Cross-Site Scripting (XSS).

### 4. Secrets Management

- **NEVER Hardcode Secrets**: API keys, database credentials, JWT secrets, and any other sensitive information must NEVER be committed to version control.
- **Use Environment Variables**: Load all secrets from environment variables.
- **Use a Secret Manager**: For production, use a dedicated secret management service (e.g., AWS Secrets Manager, Google Secret Manager, HashiCorp Vault).

---

### References

[1] OWASP. (2025). *OWASP Top 10:2025*. OWASP Foundation.
[2] OWASP. *Zero Trust Architecture Cheat Sheet*. OWASP Cheat Sheet Series.
