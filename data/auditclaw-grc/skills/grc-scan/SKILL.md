---
name: grc-scan
description: Security scan menu (headers/SSL/GDPR)
user-invocable: true
metadata: {"openclaw":{"requires":{"bins":["python3"]}}}
---
# GRC Scan

Launch a security scan.

## What to do
Using the auditclaw-grc skill, ask the user what they want to scan:
1. **Security Headers**: HTTP security headers check
2. **SSL/TLS**: Certificate and protocol analysis
3. **GDPR**: Cookie consent and privacy compliance

Then run the selected scan against a URL the user provides.
