# Security Advisory — 2026-02-26

**Project:** openclaw-protonmail-skill  
**Affected version:** `0.1.0`  
**Patched version:** `0.1.1` (pending release)

## Summary
Community scanner feedback identified two security concerns in `0.1.0`:

1. Insecure TLS override configuration (`rejectUnauthorized: false`)
2. Insufficient sanitization of IMAP search query input

We reviewed the findings, confirmed hardening opportunities, and implemented remediation.

## Impact
No confirmed exploitation has been reported. However, these conditions could increase risk in compromised localhost scenarios and malformed query-input handling.

## Remediation
- Removed insecure TLS bypass behavior
- Enforced localhost-only Bridge host policy (`127.0.0.1`, `localhost`, `::1`)
- Added strict IMAP query validation and sanitization

## Action Required
If you installed `0.1.0`, upgrade to `0.1.1` as soon as available.

## Upgrade Guidance
- Pull latest code from `main` after release
- Reinstall skill package / run your normal update workflow
- Validate Bridge host remains localhost-only

## Credits
Thanks to the community/scanner feedback that prompted this review.
