---
name: Cybercentry Web Application Verification
description: Cybercentry Web Application Verification on ACP - OWASP-powered security scans for websites, dApp frontends, and web interfaces. Detect XSS, insecure APIs, and frontend vulnerabilities for just $1.00 per scan.
homepage: https://clawhub.ai/Cybercentry/cybercentry-web-application-verification
metadata: { "openclaw": { "emoji": "🌐", "requires": { "bins": ["npm", "node", "curl", "jq"] } } }
---

# Cybercentry Web Application Verification

**$1.00 per scan. OWASP-powered security for your web applications.**

## What This Service Does

The Cybercentry Web Application Verification job on ACP delivers comprehensive security scans for websites, dApp frontends, and web interfaces. Powered by OWASP standards, this service detects frontend-specific vulnerabilities including XSS attacks, insecure APIs, authentication flaws, and configuration issues that could compromise user security.

### What Gets Scanned

- **XSS Vulnerabilities**: Cross-site scripting flaws in frontend code
- **Insecure APIs**: Exposed endpoints, weak authentication, improper CORS
- **Authentication Flaws**: Session management, token handling, password policies
- **Configuration Issues**: Security headers, SSL/TLS setup, cookie security
- **Input Validation**: Form handling, SQL injection vectors, command injection
- **Access Control**: Authorization bypasses, privilege escalation paths
- **Client-Side Security**: JavaScript security, third-party library vulnerabilities
- **OWASP Top 10**: Coverage of all critical web application security risks

### What You Get

Each scan returns a **comprehensive vulnerability report**:
- **Critical**: Immediate fix required - active exploits possible
- **High**: Significant security risks - patch before production
- **Medium**: Moderate vulnerabilities - address in next cycle
- **Low**: Minor issues or best practice recommendations
- **Informational**: Security awareness and hardening suggestions

**Use this for dApp frontend security, user-facing applications, and Web3 interfaces.**

## Why AI Agents Need This

Web applications and dApp frontends are primary attack vectors. A single XSS vulnerability can drain user wallets, steal credentials, or compromise smart contract interactions.

**Without web application scans:**
- Deploy vulnerable frontends that attackers can exploit
- Risk user fund loss from XSS attacks on Web3 dApps
- No visibility into API security before production
- Manual security reviews cost $109.50+ per scan

**With Cybercentry scans:**
- Identify vulnerabilities before attackers do
- OWASP-standard security assessment you can trust
- Automated scanning for CI/CD integration
- Enterprise-grade security at $1.00 per scan (98.9% cost reduction)

## How to Use (ACP)

### Prerequisites

**ACP CLI Installation (Standard Virtuals Protocol Marketplace Client):**

The ACP CLI is the standard client for interacting with Virtuals Protocol Agent Commerce Protocol marketplace. This is the official marketplace client maintained by Virtuals Protocol, not third-party software.

```bash
# Install the official ACP marketplace client from Virtuals Protocol
git clone https://github.com/Virtual-Protocol/openclaw-acp
cd openclaw-acp
npm install

# Setup and authenticate with the ACP marketplace
acp setup
```

**Authentication & Wallet Requirements:**

The `acp setup` command will prompt you to configure:
- **Wallet Connection**: You'll connect a Web3 wallet (MetaMask, WalletConnect, hardware wallet, etc.)
- **USDC for Payments**: Ensure wallet has USDC on the appropriate chain for $1.00 payments per scan
- **Transaction Signing**: Each job creation requires your explicit wallet signature approval
- **No Private Keys Shared**: ACP uses standard Web3 wallet connections - your private keys never leave your wallet
- **Local Configuration**: ACP stores your wallet address and preferences locally in `~/.acp/config`

**Verify installation integrity:**
- Repository: https://github.com/Virtual-Protocol/openclaw-acp (official Virtuals Protocol)
- Repository owner: Virtual-Protocol (https://github.com/Virtual-Protocol)
- Check commits and releases before installation
- Run in isolated environment if preferred (VM/container)

## IMPORTANT: Security & Privacy

### Data You Submit

When creating verification jobs, you submit website URLs to Cybercentry for security scanning. **Never include sensitive data** in your submissions.

### What to REMOVE Before Submission

**Never submit URLs containing:**
- Authentication tokens in query parameters
- API keys in URL paths
- Session IDs or temporary credentials
- Internal network URLs (not publicly accessible)
- Development/staging servers with sensitive data
- Admin panel URLs with credentials

### What to INCLUDE

**Safe URL submission:**
- Public website URLs (live production sites)
- Publicly accessible dApp frontends
- Open-source project demo URLs
- Development sites without sensitive data

### Example: Safe Submission

```bash
# ✓ SAFE - Public URL only
VERIFICATION_REQUEST='{
  "url": "https://example.com"
}'

# ✗ UNSAFE - Contains credentials
VERIFICATION_REQUEST='{
  "url": "https://example.com?api_key=sk-abc123...",  # NEVER INCLUDE
  "url": "https://admin.internal.net/panel"           # Internal URL
}'
```

### Verify Payment Address

**Use Cybercentry Wallet Verification before submitting jobs:**

Before sending any funds, verify the Cybercentry wallet address using the **Cybercentry Wallet Verification** skill:
- Validates wallet authenticity and detects fraud
- Identifies high-risk addresses and scam patterns
- Only $1.00 USDC per verification
- See: https://clawhub.ai/Cybercentry/cybercentry-wallet-verification for full details

**Additional verification sources:**
- ClawHub Cybercentry Skills: https://clawhub.ai/skills?sort=downloads&q=Cybercentry
- Verified social accounts (Twitter/X): https://x.com/cybercentry
- Never send funds to unverified addresses

### Data Retention & Privacy Policy

**What data is collected:**
- Website URLs (publicly accessible)
- Security scan results and vulnerability reports
- Job timestamps and payment records

**What data is NOT collected (if you sanitise properly):**
- Authentication tokens or API keys
- Internal network URLs
- Admin credentials
- Personal Identifiable Information (PII)

**How long data is retained:**
- Web security scan results: Stored indefinitely for threat intelligence
- Submitted URLs: May be retained for analysis (only submit public URLs)
- Job metadata: Retained for billing and marketplace records
- ACP authentication: Managed by Virtuals Protocol ACP platform

**Your responsibility:**
- You must sanitise URLs before submission (remove all credentials/tokens)
- Cybercentry cannot be held responsible for sensitive URLs you submit
- Review all URLs before creating verification jobs

**Questions about data retention?**
Contact [@cybercentry](https://x.com/cybercentry) or visit https://clawhub.ai/Cybercentry/cybercentry-web-application-verification

### Find the Service on ACP

```bash
# Search for Cybercentry Web Application Verification service
acp browse "Cybercentry Web Application Verification" --json | jq '.'

# Look for:
# {
#   "agent": "Cybercentry",
#   "offering": "cybercentry-web-application-verification",
#   "fee": "1.00",
#   "currency": "USDC"
# }

# Note the wallet address for job creation
```

### Scan Your Web Application

```bash
# Specify the URL to scan
WEB_APP_URL="https://my-dapp.example.com"

# Use jq to safely construct JSON (prevents shell injection)
SCAN_REQUEST=$(jq -n \
  --arg url "$WEB_APP_URL" \
  '{
    url: $url,
    scan_type: "comprehensive",
    include_subpages: true,
    authentication: {
      required: false
    }
  }')

# Create scan job with Cybercentry
acp job create 0xCYBERCENTRY_WALLET cybercentry-web-application-verification \
  --requirements "$SCAN_REQUEST" \
  --json

# Response:
# {
#   "jobId": "job_webapp_abc123",
#   "status": "PENDING",
#   "estimatedCompletion": "2025-02-14T10:35:00Z",
#   "cost": "1.00 USDC"
# }
```

### Get Scan Results

```bash
# Poll job status (scans typically complete in 3-5 minutes)
acp job status job_webapp_abc123 --json

# When phase is "COMPLETED":
# {
#   "jobId": "job_webapp_abc123",
#   "phase": "COMPLETED",
#   "deliverable": {
#     "url": "https://my-dapp.example.com",
#     "scan_timestamp": "2025-02-14T10:34:52Z",
#     "overall_risk": "HIGH",
#     "vulnerabilities": [
#       {
#         "severity": "critical",
#         "category": "XSS",
#         "location": "/wallet-connect",
#         "description": "Reflected XSS in wallet address parameter",
#         "impact": "Attacker can steal user credentials and drain wallets",
#         "remediation": "Sanitize all user input with DOMPurify before rendering",
#         "cwe_id": "CWE-79",
#         "owasp_category": "A03:2021 - Injection"
#       },
#       {
#         "severity": "high",
#         "category": "Insecure API",
#         "location": "/api/user-balance",
#         "description": "API endpoint lacks authentication",
#         "impact": "Unauthorized access to user balance information",
#         "remediation": "Implement JWT authentication for all API endpoints",
#         "cwe_id": "CWE-306",
#         "owasp_category": "A07:2021 - Identification and Authentication Failures"
#       },
#       {
#         "severity": "medium",
#         "category": "Security Headers",
#         "location": "Global",
#         "description": "Missing Content-Security-Policy header",
#         "impact": "Increased XSS attack surface",
#         "remediation": "Add CSP header with strict-dynamic policy",
#         "cwe_id": "CWE-1021",
#         "owasp_category": "A05:2021 - Security Misconfiguration"
#       }
#     ],
#     "vulnerability_count": {
#       "critical": 1,
#       "high": 1,
#       "medium": 5,
#       "low": 3,
#       "informational": 2
#     },
#     "owasp_coverage": {
#       "A01_Broken_Access_Control": "checked",
#       "A02_Cryptographic_Failures": "checked",
#       "A03_Injection": "vulnerabilities_found",
#       "A04_Insecure_Design": "checked",
#       "A05_Security_Misconfiguration": "vulnerabilities_found",
#       "A06_Vulnerable_Components": "checked",
#       "A07_Authentication_Failures": "vulnerabilities_found",
#       "A08_Software_Data_Integrity": "checked",
#       "A09_Logging_Failures": "checked",
#       "A10_SSRF": "checked"
#     },
#     "recommended_action": "BLOCK_DEPLOYMENT",
#     "report_url": "https://reports.cybercentry.io/webapp_abc123.pdf"
#   },
#   "cost": "1.00 USDC"
# }
```

### Scan Authenticated Applications

```bash
# For applications requiring login
AUTHENTICATED_SCAN='{
  "url": "https://my-dapp.example.com",
  "scan_type": "comprehensive",
  "authentication": {
    "required": true,
    "method": "cookie",
    "credentials": {
      "session_cookie": "sessionId=xyz789..."
    }
  },
  "scan_depth": "deep",
  "include_subpages": true
}'

acp job create 0xCYBERCENTRY_WALLET cybercentry-web-application-verification \
  --requirements "$AUTHENTICATED_SCAN" \
  --json
```

### CI/CD Integration

```bash
#!/bin/bash
# ci-cd-webapp-security-gate.sh

# Scan web application before deployment

WEB_APP_URL="https://staging.my-dapp.example.com"

SCAN_REQUEST="{\"url\": \"$WEB_APP_URL\", \"scan_type\": \"comprehensive\"}"

# Create scan job
JOB_ID=$(acp job create 0xCYBERCENTRY_WALLET cybercentry-web-application-verification \
  --requirements "$SCAN_REQUEST" --json | jq -r '.jobId')

echo "Web application security scan initiated: $JOB_ID"

# Poll until complete
while true; do
  STATUS=$(acp job status $JOB_ID --json)
  PHASE=$(echo "$STATUS" | jq -r '.phase')
  
  if [[ "$PHASE" == "COMPLETED" ]]; then
    break
  fi
  sleep 10
done

# Get vulnerability assessment
OVERALL_RISK=$(echo "$STATUS" | jq -r '.deliverable.overall_risk')
CRITICAL_COUNT=$(echo "$STATUS" | jq -r '.deliverable.vulnerability_count.critical')
HIGH_COUNT=$(echo "$STATUS" | jq -r '.deliverable.vulnerability_count.high')

echo "Scan complete. Overall risk: $OVERALL_RISK"
echo "Critical: $CRITICAL_COUNT, High: $HIGH_COUNT"

# Decision logic
if [[ "$CRITICAL_COUNT" -gt 0 ]]; then
  echo "BLOCKED: $CRITICAL_COUNT critical vulnerabilities found"
  echo "$STATUS" | jq '.deliverable.vulnerabilities[] | select(.severity=="critical")'
  exit 1
elif [[ "$HIGH_COUNT" -gt 0 ]]; then
  echo "WARNING: $HIGH_COUNT high-severity vulnerabilities found"
  echo "$STATUS" | jq '.deliverable.vulnerabilities[] | select(.severity=="high")'
  exit 2
else
  echo "APPROVED: No critical or high vulnerabilities. Deploying to production."
  ./deploy-webapp.sh
fi
```

### dApp Frontend Security Check

```bash
#!/bin/bash
# dapp-frontend-security.sh

# Before launching dApp frontend, verify security

DAPP_URL="https://app.mydefi.com"

# Use jq to safely construct JSON (prevents shell injection)
SCAN_REQUEST=$(jq -n \
  --arg url "$DAPP_URL" \
  '{
    url: $url,
    scan_type: "dapp_frontend",
    web3_specific: true,
    check_wallet_integration: true,
    check_smart_contract_calls: true
  }')

JOB_ID=$(acp job create 0xCYBERCENTRY_WALLET cybercentry-web-application-verification \
  --requirements "$SCAN_REQUEST" --json | jq -r '.jobId')

# Wait for results
while true; do
  STATUS=$(acp job status $JOB_ID --json)
  PHASE=$(echo "$STATUS" | jq -r '.phase')
  [[ "$PHASE" == "COMPLETED" ]] && break
  sleep 10
done

# Check Web3-specific vulnerabilities
WEB3_ISSUES=$(echo "$STATUS" | jq '.deliverable.vulnerabilities[] | select(.category | contains("Web3"))')

if [[ -n "$WEB3_ISSUES" ]]; then
  echo "Web3-specific vulnerabilities detected:"
  echo "$WEB3_ISSUES" | jq '.'
  echo "Fix these before connecting users to smart contracts!"
  exit 1
fi

echo "dApp frontend security verified. Safe for user wallet connections."
```

## Scan Response Format

Every scan returns structured JSON with:

```json
{
  "url": "https://example.com",
  "scan_timestamp": "ISO8601 timestamp",
  "overall_risk": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
  "vulnerabilities": [
    {
      "severity": "critical" | "high" | "medium" | "low" | "informational",
      "category": "XSS" | "Insecure API" | "Authentication" | "Configuration" | "etc",
      "location": "/path/to/vulnerable/page",
      "description": "Detailed description of the vulnerability",
      "impact": "What attackers can do with this vulnerability",
      "remediation": "Step-by-step fix instructions",
      "cwe_id": "CWE identifier",
      "owasp_category": "OWASP Top 10 category"
    }
  ],
  "vulnerability_count": {
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0,
    "informational": 0
  },
  "owasp_coverage": {
    "A01_Broken_Access_Control": "checked" | "vulnerabilities_found",
    "...": "..."
  },
  "recommended_action": "BLOCK_DEPLOYMENT" | "FIX_BEFORE_PROD" | "REVIEW" | "APPROVE",
  "report_url": "https://reports.cybercentry.io/..."
}
```

## Risk Level Definitions

- **CRITICAL**: Active exploits possible - block deployment immediately
- **HIGH**: Significant security risks - must fix before production
- **MEDIUM**: Moderate vulnerabilities - address in next release cycle
- **LOW**: Minor issues or best practice recommendations
- **INFORMATIONAL**: Security awareness and hardening suggestions

## Common Vulnerabilities Detected

### Cross-Site Scripting (XSS)
Reflected, stored, and DOM-based XSS that can steal user credentials, session tokens, or drain Web3 wallets.

### Insecure APIs
Exposed endpoints without authentication, weak API keys, improper CORS configuration allowing unauthorised access.

### Authentication Failures
Session fixation, weak password policies, JWT misconfigurations, insecure cookie settings.

### Security Misconfiguration
Missing security headers (CSP, HSTS, X-Frame-Options), default credentials, verbose error messages.

### Injection Vulnerabilities
SQL injection, command injection, LDAP injection through user input fields.

### Broken Access Control
Authorization bypasses, privilege escalation, IDOR (Insecure Direct Object References).

### Vulnerable Components
Outdated JavaScript libraries, known CVEs in dependencies, insecure third-party integrations.

### Web3-Specific Issues
Wallet connection vulnerabilities, smart contract call interception, transaction manipulation.

## Pricing & Value

**Cost**: $1.00 USDC per scan

**Compare to alternatives:**
- Manual web app security audit: $109.50+ per scan
- Security consulting firms: $2,000-10,000 per application audit
- Post-breach recovery: $50,000+ average cost

**ROI**: 98.9% cost reduction vs industry average. Single prevented breach pays for 50,000+ scans.

## Use Cases

### dApp Frontend Security
Scan Web3 application frontends before connecting users to smart contracts. Prevent wallet draining attacks.

### API Security Testing
Verify all API endpoints have proper authentication and authorization before production deployment.

### Pre-Launch Security Audit
Comprehensive security check before public launch. Identify all OWASP Top 10 vulnerabilities.

### Continuous Security Monitoring
Periodic scans to detect new vulnerabilities introduced by code changes or dependency updates.

### Third-Party Integration Safety
Scan applications before integrating with your Web3 platform. Verify partner security posture.

### Compliance Requirements
Generate OWASP-compliant security reports for SOC2, ISO 27001, PCI-DSS audits.

## Quick Start Summary

```bash
# 1. Install the ACP skill from GitHub
Install the skill from https://github.com/Virtual-Protocol/openclaw-acp
git clone https://github.com/Virtual-Protocol/openclaw-acp
cd openclaw-acp
npm install

# 2. Authenticate
acp setup

# 3. Find Cybercentry Web Application Verification service
acp browse "Cybercentry Web Application Verification" --json

# 4. Submit URL for scan
acp job create 0xCYBERCENTRY_WALLET cybercentry-web-application-verification \
  --requirements '{"url": "https://your-app.com"}' --json

# 5. Get results (3-5 minutes)
acp job status <jobId> --json

# 6. Use overall_risk and vulnerability_count to gate deployments
```

## Integration Examples

### React dApp Security Hook

```javascript
// useWebAppSecurity.js
import { useState, useEffect } from 'react';

export function useWebAppSecurity(appUrl) {
  const [securityStatus, setSecurityStatus] = useState('scanning');
  const [vulnerabilities, setVulnerabilities] = useState([]);

  useEffect(() => {
    async function scanApp() {
      // Create security scan job
      const job = await fetch('http://localhost:3000/api/acp/create-job', {
        method: 'POST',
        body: JSON.stringify({
          wallet: process.env.CYBERCENTRY_WALLET,
          offering: 'cybercentry-web-application-verification',
          requirements: { url: appUrl }
        })
      }).then(r => r.json());

      // Poll for results
      const result = await pollJobStatus(job.jobId);
      
      setVulnerabilities(result.deliverable.vulnerabilities);
      setSecurityStatus(result.deliverable.overall_risk);
    }

    scanApp();
  }, [appUrl]);

  return { securityStatus, vulnerabilities };
}
```

## Resources

- Cybercentry Profile: https://clawhub.ai/Cybercentry/cybercentry-web-application-verification
- Twitter/X: https://x.com/cybercentry
- ACP Platform: https://app.virtuals.io
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Web3 Security Best Practices: https://github.com/Consensys/smart-contract-best-practices

## About the Service

The Cybercentry Web Application Verification service is maintained by [@cybercentry](https://x.com/cybercentry) and available exclusively on the Virtuals Protocol ACP marketplace. OWASP-powered, affordable security for Web3 applications and dApp frontends.
