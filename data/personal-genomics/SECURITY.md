# Security Policy

## Privacy by Design

This project is built with privacy as a core principle:

- **Zero network requests** — All analysis runs locally
- **No telemetry** — We don't collect any usage data
- **No external dependencies at runtime** — No API calls
- **Your data stays yours** — Nothing leaves your machine

## Reporting a Vulnerability

If you discover a security issue, please report it by:

1. **GitHub Issues:** Open an issue on this repository
2. **Subject:** `[SECURITY] personal-genomics: <brief description>`

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## Genetic Data Security

### Recommendations for Users

1. **Encrypt your DNA files** — Use FileVault, VeraCrypt, or similar
2. **Don't commit DNA data** — The `.gitignore` blocks common patterns
3. **Secure your reports** — Output files contain sensitive health info
4. **Be cautious sharing** — Genetic data affects your family too

### What We Do

- `.gitignore` excludes common DNA file patterns
- Documentation warns about data sensitivity
- No hardcoded paths to personal data
- Output directory is user-configurable

## Known Limitations

- Results are **not clinically validated**
- SNP databases may contain errors
- Consumer chip coverage is limited (~0.02% of genome)
- Population reference bias exists

## Responsible Disclosure

We ask that you:
- Give us reasonable time to address issues before public disclosure
- Don't access or modify other users' data
- Don't exploit vulnerabilities maliciously

Thank you for helping keep genetic data safe.
