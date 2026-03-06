# Severity Rating Guide

A unified severity scoring reference for consistent, defensible severity assignments across all vulnerability types and platforms.

---

## Quick Severity Decision Matrix

Ask these 4 questions in order:

```
1. Does the attacker need authentication?
   No → potential Critical/High
   Yes (low-privilege) → potential High/Medium  
   Yes (admin-only) → Medium/Low

2. Does victim interaction (click/visit) required?
   No → +1 severity tier
   Yes → standard

3. What is the data/system impact?
   RCE / full account takeover → Critical
   Other accounts' sensitive data / admin access → High
   Attacker's own data only → Medium/Low

4. Is the scope changed? (attacker moves beyond originally targeted component)
   Yes (e.g., SSRF internal, XSS → ATO) → Critical/High
   No → stay at base level
```

---

## Severity Definitions

### 🔴 Critical
- Unauthenticated RCE on production server
- Unauthenticated account takeover of any user (including admin)
- Full cloud credential exposure (AWS/GCP/Azure with admin permissions)
- Authentication bypass → admin access without credentials
- Mass data exfiltration of sensitive PII/financial data at scale

**Threshold:** Immediate, severe, widespread impact with no prerequisites.

---

### 🟠 High
- Authenticated RCE (any user)
- Stored XSS with ATO potential (reads HttpOnly-free session cookie)
- SQLi with data exfiltration of sensitive tables
- SSRF to internal services / IMDS
- IDOR accessing sensitive data of other users (PII, financials)
- OAuth / JWT forgery → full account takeover
- Subdomain takeover on auth-relevant subdomain
- CORS misconfiguration leaking authenticated API responses
- Mass assignment → role escalation to admin

**Threshold:** Significant unauthorized access or data exposure requiring some attacker effort or prerequisites.

---

### 🟡 Medium
- Reflected XSS (requires victim to click link)
- SQLi with blind confirmation but no data exfil verified
- IDOR on non-sensitive data (public profile info)
- SSRF (blind, no internal access confirmed)
- Path traversal reading non-sensitive files
- CSRF on sensitive action (password change, email change)
- Subdomain takeover on marketing/CDN subdomain
- Rate limit bypass on sensitive action
- Open redirect chained with OAuth → auth code theft

**Threshold:** Real vulnerability with limited impact or requiring meaningful victim interaction.

---

### 🟢 Low
- Open redirect (standalone, no auth chain)
- Path traversal reading non-sensitive application files
- IDOR on fully public data
- Missing security headers (CSP, HSTS) — only if isolated from other vulns
- Version disclosure that reveals software with known CVEs (unconfirmed exploitability)
- SSRF (external-only, no internal access)
- Blind CSRF on low-sensitivity action

**Threshold:** Real vulnerability but limited practical impact without additional conditions.

---

### ⚪ Informational / Not Reportable
- GraphQL introspection enabled (alone)
- Missing `X-Frame-Options` without PoC clickjacking
- SPF/DMARC misconfiguration alone
- Content-Security-Policy not implemented (alone)
- Open directory listing with no sensitive files
- Self-XSS (attacker-on-attacker only)
- CSRF on login / logout
- Rate limiting missing (without exploitable action)
- Version number in response (without confirmed CVE)

---

## Platform Severity Mapping

| Our Rating | HackerOne | Bugcrowd | Intigriti | YesWeHack |
|---|---|---|---|---|
| Critical | Critical (9.0–10.0) | P1 | Critical | Critical |
| High | High (7.0–8.9) | P2 | High | High |
| Medium | Medium (4.0–6.9) | P3 | Medium | Medium |
| Low | Low (0.1–3.9) | P4 | Low | Low |
| Informational | N/A | P5 | Informational | Informational |

---

## CVSS v3.1 Quick Scoring (for HackerOne reports)

When HackerOne requests CVSS justification, use this:

| Metric | Value | Score Impact |
|---|---|---|
| Attack Vector (AV) | Network | Highest |
| Attack Complexity (AC) | Low | Highest |
| Privileges Required (PR) | None | Highest |
| User Interaction (UI) | None | Highest |
| Scope (S) | Changed | Higher |
| Confidentiality (C) | High | Up to 3.3 |
| Integrity (I) | High | Up to 3.3 |
| Availability (A) | High | Up to 3.3 |

**Maximum score:** AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H = **10.0 (Critical)**

**Common example — Stored XSS with ATO:**
`AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N` = **8.7 (High)**

---

## Severity Downgrade Conditions

Always downgrade if:
- Attack requires social engineering or victim to be deceived (−1 tier)
- Attack only works in non-default / obscure browser configurations (−1 tier)
- Attack requires admin-level privileges to reach the vuln (−1 to −2 tiers)
- Vulnerability exists only in staging/dev environment not affecting prod (−1 tier)
- Impact limited to attacker's own data / self-only (−2 tiers usually → not reportable)
- WAF effectively blocks all known exploit variants (note as theoretical)

---

## Reporting Severity With Confidence

In every finding, state:
```
Severity: High
CVSS: AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (8.1)
Justification: Exploitable over network (AV:N), low complexity (AC:L), 
               requires authenticated user (PR:L), no victim interaction (UI:N),
               scope unchanged (S:U), full confidentiality and integrity impact.
```
