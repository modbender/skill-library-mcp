---
name: afrexai-cybersecurity-engine
description: Complete cybersecurity assessment, threat modeling, and hardening system. Use when conducting security audits, threat modeling, penetration testing, incident response, or building security programs from scratch. Works with any stack — zero external dependencies.
metadata: {"openclaw":{"emoji":"🛡️","os":["linux","darwin","win32"]}}
---

# Cybersecurity Engine

Complete methodology for security assessment, threat modeling, vulnerability management, incident response, and security program design. No tools required — pure agent knowledge that works with any codebase, infrastructure, or organization.

## Phase 1: Security Posture Assessment

### Quick Health Check (5 minutes)

Run through these three tiers:

**Tier 1 — Critical (fix today):**
- [ ] Default credentials in production
- [ ] Secrets in source code or environment files committed to git
- [ ] No authentication on admin endpoints
- [ ] SQL injection in user-facing forms
- [ ] Unencrypted sensitive data at rest
- [ ] Public S3 buckets or cloud storage
- [ ] No HTTPS enforcement
- [ ] Root/admin running application processes

**Tier 2 — High (fix this week):**
- [ ] Dependencies with known CVEs (CVSS ≥ 7.0)
- [ ] No rate limiting on authentication endpoints
- [ ] Missing CSRF protection on state-changing operations
- [ ] Verbose error messages leaking stack traces
- [ ] No input validation on API endpoints
- [ ] Weak password policy (< 12 chars, no complexity)
- [ ] Session tokens in URL parameters
- [ ] No logging of authentication events

**Tier 3 — Medium (fix this sprint):**
- [ ] Missing security headers (CSP, HSTS, X-Frame-Options)
- [ ] No automated dependency scanning in CI
- [ ] Overprivileged service accounts
- [ ] No secret rotation policy
- [ ] Missing account lockout after failed attempts
- [ ] No security.txt or responsible disclosure policy
- [ ] Cookies without Secure/HttpOnly/SameSite flags

**Score:** Count failures. 0-2 = solid. 3-5 = needs work. 6+ = stop shipping features, fix security.

### Full Assessment Brief

```yaml
assessment:
  name: "[Project/Org Name] Security Assessment"
  date: "YYYY-MM-DD"
  assessor: "[Agent/Person]"
  scope:
    applications:
      - name: "[App Name]"
        type: "web|api|mobile|desktop|iot"
        tech_stack: "[languages, frameworks, DBs]"
        hosting: "cloud|on-prem|hybrid"
        cloud_provider: "aws|gcp|azure|other"
        internet_facing: true|false
        handles_pii: true|false
        handles_payments: true|false
        handles_phi: true|false  # health data
    infrastructure:
      - servers: "[count, OS types]"
        containers: true|false
        orchestration: "k8s|ecs|nomad|none"
        cdn: "[provider or none]"
        dns: "[provider]"
    third_parties:
      - name: "[service]"
        data_shared: "[what data]"
        criticality: "high|medium|low"
  compliance_requirements:
    - "SOC 2|ISO 27001|GDPR|HIPAA|PCI DSS|SOX|none"
  previous_incidents:
    - date: "YYYY-MM-DD"
      type: "[breach|vuln|misconfiguration]"
      severity: "critical|high|medium|low"
      resolution: "[what was done]"
  risk_tolerance: "conservative|moderate|aggressive"
```

## Phase 2: Threat Modeling (STRIDE+)

### Step 1 — Decompose the System

For each application, draw the data flow:

```
[User] → [CDN/WAF] → [Load Balancer] → [Web Server] → [App Server] → [Database]
                                                     ↘ [Cache]
                                                     ↘ [Message Queue] → [Worker]
                                                     ↘ [Third-party API]
                                                     ↘ [Object Storage]
```

**Identify trust boundaries** — where privilege level changes:
- Internet → DMZ (public-facing services)
- DMZ → Internal network (app servers, DBs)
- App → Database (credential boundary)
- User → Admin (role boundary)
- Service → Service (API key boundary)
- Your infra → Third-party (trust boundary)

### Step 2 — STRIDE Analysis Per Component

For EACH component crossing a trust boundary:

| Threat | Question | Example Attack |
|--------|----------|----------------|
| **S**poofing | Can an attacker pretend to be someone else? | Stolen JWT, session hijacking, credential stuffing |
| **T**ampering | Can data be modified in transit or at rest? | Man-in-the-middle, SQL injection, parameter manipulation |
| **R**epudiation | Can someone deny they did something? | Missing audit logs, unsigned transactions |
| **I**nformation Disclosure | Can sensitive data leak? | Error messages, API over-fetching, side channels |
| **D**enial of Service | Can the service be overwhelmed? | DDoS, resource exhaustion, regex DoS |
| **E**levation of Privilege | Can someone gain unauthorized access? | IDOR, broken access control, privilege escalation |

### Step 3 — Threat Register

```yaml
threats:
  - id: "T-001"
    component: "[affected component]"
    category: "S|T|R|I|D|E"
    description: "[specific attack scenario]"
    attacker_profile: "external-unauthenticated|external-authenticated|internal|insider"
    likelihood: 1-5  # 1=rare, 5=almost certain
    impact: 1-5      # 1=negligible, 5=catastrophic
    risk_score: 0     # likelihood × impact
    existing_controls: "[what's already in place]"
    residual_risk: "accept|mitigate|transfer|avoid"
    mitigation: "[specific fix]"
    priority: "P0|P1|P2|P3"
    owner: "[person/team]"
    status: "open|in-progress|mitigated|accepted"
```

### Priority Rules
- **P0** (risk ≥ 20): Fix immediately, stop other work
- **P1** (risk 12-19): Fix within 1 week
- **P2** (risk 6-11): Fix within 1 sprint
- **P3** (risk ≤ 5): Track, fix when convenient

## Phase 3: Application Security (OWASP Top 10 + Beyond)

### A01: Broken Access Control

**Test checklist:**
- [ ] Can user A access user B's resources by changing ID? (IDOR)
- [ ] Can non-admin access admin endpoints?
- [ ] Do API endpoints enforce authorization, not just authentication?
- [ ] Are directory listings disabled?
- [ ] Is CORS properly configured (not `*` with credentials)?
- [ ] Can JWT be tampered with (alg=none, key confusion)?
- [ ] Is rate limiting applied to sensitive endpoints?
- [ ] Do file uploads validate type server-side?

**Fix patterns:**
```
# Authorization check pattern (every endpoint)
1. Authenticate → verify identity
2. Authorize → verify permission for THIS resource
3. Validate → verify input is within allowed bounds
4. Execute → perform the action
5. Audit → log who did what

# IDOR prevention
- NEVER use sequential IDs in URLs — use UUIDs
- ALWAYS verify resource ownership server-side
- Use middleware that auto-checks resource.owner === request.user
```

### A02: Cryptographic Failures

**Decision tree:**
```
Need to store passwords?
  → bcrypt (cost 12+) or Argon2id
  → NEVER: MD5, SHA1, SHA256 without salt

Need to encrypt data at rest?
  → AES-256-GCM (authenticated encryption)
  → NEVER: ECB mode, DES, RC4

Need to encrypt in transit?
  → TLS 1.2+ (prefer 1.3)
  → HSTS with includeSubDomains
  → Certificate pinning for mobile apps

Need to generate random values?
  → crypto.randomBytes() / secrets.token_bytes()
  → NEVER: Math.random(), random.random()

Need to sign/verify?
  → HMAC-SHA256 for symmetric
  → Ed25519 or RSA-PSS (2048+ bits) for asymmetric
  → NEVER: RSA PKCS#1 v1.5 for new systems
```

### A03: Injection

**SQL Injection prevention:**
```
# ALWAYS use parameterized queries
✅ db.query("SELECT * FROM users WHERE id = $1", [userId])
❌ db.query("SELECT * FROM users WHERE id = " + userId)

# Test payloads (for YOUR code, during testing):
' OR '1'='1
'; DROP TABLE users;--
' UNION SELECT password FROM users--
1; WAITFOR DELAY '0:0:5'--
```

**XSS prevention:**
```
# Output encoding rules:
HTML body    → HTML entity encode (&lt; &gt; &amp; &quot; &#x27;)
HTML attr    → Attribute encode + always quote attributes
JavaScript   → JavaScript encode (\\xHH)
URL          → Percent encode (%HH)
CSS          → CSS encode (\\HHHHHH)

# CSP header (strong baseline):
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self' https://api.yourdomain.com; frame-ancestors 'none'; base-uri 'self'; form-action 'self'
```

**Command injection prevention:**
```
# NEVER pass user input to shell
✅ execFile('convert', ['-resize', size, inputFile, outputFile])
❌ exec('convert -resize ' + size + ' ' + inputFile + ' ' + outputFile)

# If you MUST use shell:
- Whitelist allowed characters (alphanumeric only)
- Use library wrappers, never string concatenation
```

### A04: Insecure Design

**Secure design checklist:**
- [ ] Business logic abuse scenarios documented
- [ ] Rate limiting on expensive operations
- [ ] Fail-safe defaults (deny by default)
- [ ] Separation of duties for critical operations
- [ ] Multi-step transactions use CSRF tokens
- [ ] API pagination has max limit
- [ ] File uploads have size limits AND type validation (magic bytes, not extension)
- [ ] Background job payloads are signed/validated

### A05: Security Misconfiguration

**Server hardening checklist:**
```yaml
web_server:
  - remove_default_pages: true
  - disable_directory_listing: true
  - remove_server_version_header: true
  - disable_TRACE_method: true
  - custom_error_pages: true  # no stack traces

application:
  - debug_mode: false  # NEVER in production
  - verbose_errors: false
  - default_accounts_removed: true
  - unnecessary_features_disabled: true
  - admin_panel_ip_restricted: true

cloud:
  - public_buckets: none
  - security_groups_least_privilege: true
  - imds_v2_enforced: true  # AWS
  - logging_enabled: true
  - mfa_on_root: true
  - billing_alerts: true
```

### A06-A10 Quick Checks

| Vuln | Test | Fix |
|------|------|-----|
| A06: Vulnerable Components | `npm audit`, `pip-audit`, `trivy fs .` | Update, pin versions, automate scanning in CI |
| A07: Auth Failures | Brute force test, password policy audit, MFA coverage | Rate limit + lockout, enforce MFA, bcrypt/Argon2 |
| A08: Data Integrity | Can unsigned data modify app behavior? | Sign all serialized data, verify checksums, SRI for CDN |
| A09: Logging Gaps | Do you log auth events, access changes, failures? | Structured logging, SIEM integration, alert on anomalies |
| A10: SSRF | Can user input trigger server-side requests? | Allowlist URLs, block internal IPs, no redirects to internal |

## Phase 4: Infrastructure Security

### Network Security Baseline

```yaml
network_hardening:
  firewall:
    default_policy: "deny-all"
    allowed_inbound:
      - port: 443
        source: "0.0.0.0/0"
        service: "HTTPS"
      - port: 22
        source: "[admin_ip_range]"
        service: "SSH"
    rules:
      - "No direct database access from internet"
      - "Internal services communicate on private subnet"
      - "Egress filtering — block unnecessary outbound"

  ssh:
    password_auth: false
    root_login: false
    key_type: "ed25519"
    port: "[non-standard recommended]"
    fail2ban: true
    max_auth_tries: 3

  dns:
    dnssec: true
    caa_records: true  # restrict who can issue TLS certs
    no_zone_transfer: true

  tls:
    min_version: "1.2"
    preferred: "1.3"
    cipher_suites: "ECDHE+AESGCM:ECDHE+CHACHA20"
    hsts: "max-age=31536000; includeSubDomains; preload"
    certificate_monitoring: true
    auto_renewal: true
```

### Container Security

```yaml
container_hardening:
  image:
    - base: "distroless or alpine (minimal)"
    - user: "non-root (USER 1000:1000)"
    - scan: "trivy image before push"
    - sign: "cosign or Notary"
    - pins: "use SHA256 digests, not :latest"
    - secrets: "NEVER in Dockerfile or image layers"
    - layers: "multi-stage builds, minimal final image"

  runtime:
    - read_only_rootfs: true
    - no_new_privileges: true
    - drop_all_capabilities: true
    - add_only: ["NET_BIND_SERVICE"]  # if needed
    - resource_limits: true
    - seccomp_profile: "default"
    - network_policy: "deny by default"

  registry:
    - private: true
    - vulnerability_scanning: true
    - image_signing: true
    - tag_immutability: true
```

### Cloud Security (AWS/GCP/Azure Universal)

```yaml
cloud_security_baseline:
  identity:
    - root_account_mfa: true
    - no_root_access_keys: true
    - least_privilege_iam: true
    - service_accounts_scoped: true
    - temporary_credentials: true  # assume role, not long-lived keys
    - sso_enforced: true

  data:
    - encryption_at_rest: "default on all storage"
    - encryption_in_transit: "TLS everywhere"
    - backup_encryption: true
    - key_management: "cloud KMS, not self-managed"
    - data_classification: true

  network:
    - vpc_flow_logs: true
    - private_subnets_for_databases: true
    - nat_gateway_for_outbound: true
    - waf_on_public_endpoints: true
    - ddos_protection: true

  monitoring:
    - cloudtrail_enabled: true  # or equivalent
    - config_rules: true
    - guardduty_enabled: true  # or equivalent
    - cost_alerts: true
    - unused_resource_alerts: true

  storage:
    - no_public_buckets: true
    - versioning_on_critical: true
    - lifecycle_policies: true
    - access_logging: true
```

## Phase 5: Vulnerability Management Program

### Vulnerability Lifecycle

```
Discovery → Triage → Prioritize → Remediate → Verify → Close
    ↓          ↓         ↓            ↓          ↓
  Scan/     Confirm   CVSS +       Fix or     Retest
  Report    real?     context      compensate
```

### Severity SLA

| Severity | CVSS | Remediation SLA | Escalation |
|----------|------|-----------------|------------|
| Critical | 9.0-10.0 | 24 hours | CTO/CISO immediately |
| High | 7.0-8.9 | 7 days | Team lead + security |
| Medium | 4.0-6.9 | 30 days | Sprint backlog |
| Low | 0.1-3.9 | 90 days | Track, fix when convenient |
| Info | 0 | No SLA | Document for awareness |

### Vulnerability Report Template

```yaml
vulnerability:
  id: "VULN-YYYY-NNN"
  title: "[descriptive title]"
  discovered: "YYYY-MM-DD"
  discoverer: "[scanner/person/bounty]"
  severity: "critical|high|medium|low|info"
  cvss_score: 0.0
  cvss_vector: "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
  cve: "[if applicable]"
  affected:
    - component: "[app/service/library]"
      version: "[affected versions]"
      environment: "production|staging|dev"
  description: "[what the vulnerability is]"
  impact: "[what an attacker could do]"
  proof_of_concept: "[steps to reproduce]"
  remediation:
    fix: "[specific fix]"
    workaround: "[temporary mitigation]"
    compensating_control: "[if fix isn't immediate]"
  status: "open|in-progress|fixed|accepted|false-positive"
  fixed_date: "YYYY-MM-DD"
  verified_by: "[person who confirmed fix]"
```

### Scanning Schedule

| Scan Type | Frequency | Tool Examples |
|-----------|-----------|---------------|
| Dependency scan | Every CI build | npm audit, pip-audit, trivy |
| SAST (code) | Every PR | Semgrep, CodeQL, Bandit |
| Secret scanning | Every commit | GitLeaks, truffleHog, GitHub secret scanning |
| Container scan | Every image build | Trivy, Grype, Snyk Container |
| DAST (runtime) | Weekly | OWASP ZAP, Burp Suite, Nuclei |
| Cloud config | Daily | ScoutSuite, Prowler, CloudSploit |
| Penetration test | Quarterly | Manual + automated |
| Red team | Annually | External firm |

## Phase 6: Incident Response

### Incident Severity Levels

| Level | Definition | Response Time | Team |
|-------|-----------|---------------|------|
| SEV-1 | Active breach, data exfiltration, service down | 15 min | All hands + management + legal |
| SEV-2 | Vulnerability actively exploited, partial compromise | 1 hour | Security + affected team leads |
| SEV-3 | Suspicious activity, potential compromise indicators | 4 hours | Security team |
| SEV-4 | Low-risk finding, policy violation, failed attack | Next business day | Assigned engineer |

### Incident Response Playbook

**Phase 1 — Detection & Triage (first 15 minutes)**
```
1. Confirm incident is real (not false positive)
2. Classify severity (SEV-1 through SEV-4)
3. Assign incident commander
4. Open incident channel (Slack/Teams)
5. Start incident log with timestamps
6. Notify stakeholders per severity
```

**Phase 2 — Containment (first hour)**
```
SHORT-TERM (stop the bleeding):
- Isolate affected systems (network segmentation)
- Revoke compromised credentials immediately
- Block attacking IP/user agent
- Enable enhanced logging on affected systems
- Preserve forensic evidence (DON'T reboot/wipe yet)

LONG-TERM (prevent spread):
- Patch the vulnerability that was exploited
- Rotate ALL credentials that may be compromised
- Update firewall/WAF rules
- Deploy additional monitoring
```

**Phase 3 — Eradication**
```
1. Identify root cause
2. Remove all attacker artifacts (backdoors, malware, new accounts)
3. Patch all instances of the vulnerability
4. Verify no lateral movement occurred
5. Confirm all compromised credentials rotated
```

**Phase 4 — Recovery**
```
1. Restore from clean backups (verify backup integrity first)
2. Rebuild compromised systems from scratch (don't trust cleanup)
3. Monitor restored systems with enhanced logging
4. Gradual return to production (staged rollback)
5. Confirm normal operations for 48 hours
```

**Phase 5 — Post-Incident**
```yaml
post_mortem:
  incident_id: "INC-YYYY-NNN"
  date: "YYYY-MM-DD"
  severity: "SEV-1|2|3|4"
  duration: "[detection to resolution]"
  impact:
    users_affected: 0
    data_compromised: "[type and volume]"
    financial_impact: "$0"
    regulatory_notification_required: true|false
  timeline:
    - time: "HH:MM"
      event: "[what happened]"
      action: "[what we did]"
  root_cause: "[specific technical cause]"
  contributing_factors:
    - "[what made it possible or worse]"
  what_went_well:
    - "[detection, response, communication]"
  what_went_poorly:
    - "[gaps, delays, confusion]"
  action_items:
    - action: "[specific improvement]"
      owner: "[person]"
      due: "YYYY-MM-DD"
      status: "open|done"
  lessons_learned:
    - "[distilled insight]"
```

### Communication Templates

**Internal notification (SEV-1/2):**
```
🚨 SECURITY INCIDENT — [severity]
What: [brief description]
Impact: [what's affected]
Status: [containment/investigation/resolved]
Incident Commander: [name]
Channel: #incident-[id]
Next update: [time]

DO NOT discuss outside this channel.
```

**Customer notification (if required):**
```
Subject: Security Notice — [Company Name]

We're writing to inform you of a security incident that [may have|affected] your account.

What happened: [brief, honest description]
When: [date range]
What data was involved: [specific data types]
What we've done: [remediation steps]
What you should do: [password reset, monitor accounts, etc.]
Contact: [security team email/phone]

We take the security of your data seriously and have [specific improvements].
```

## Phase 7: Security Headers & Browser Security

### Required HTTP Headers

```
# Copy-paste baseline for production:
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=(), interest-cohort=()
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Resource-Policy: same-origin
X-XSS-Protection: 0  # Disabled — CSP handles this; old header can cause issues
```

### Cookie Security

```
Set-Cookie: session=<token>;
  Secure;                    # HTTPS only
  HttpOnly;                  # No JavaScript access
  SameSite=Lax;              # CSRF protection (Strict if no cross-site navigation needed)
  Path=/;                    # Scope appropriately
  Max-Age=3600;              # 1 hour (adjust per use case)
  Domain=.yourdomain.com;    # Explicit domain
```

## Phase 8: Authentication & Authorization Deep Dive

### Password Policy (NIST 800-63B aligned)

```yaml
password_policy:
  minimum_length: 12  # NIST minimum is 8, 12+ recommended
  maximum_length: 128  # Must support long passwords
  complexity_rules: false  # NIST says don't require special chars
  check_against_breached: true  # HaveIBeenPwned API
  no_password_hints: true
  no_security_questions: true  # Easy to social engineer
  allow_paste: true  # For password managers
  rate_limit_attempts: "5 per 15 minutes"
  lockout_duration: "progressive (1min, 5min, 15min, 1hr)"
  mfa_required: "all accounts"
  mfa_methods:
    preferred: "TOTP or WebAuthn/passkeys"
    acceptable: "push notification"
    discouraged: "SMS (SIM swap risk)"
  storage: "Argon2id or bcrypt cost 12+"
```

### JWT Security Checklist

```yaml
jwt_security:
  signing:
    algorithm: "RS256 or EdDSA"  # NEVER HS256 with shared secrets in distributed systems
    key_rotation: "quarterly"
    verify_algorithm: true  # Reject alg=none
  claims:
    exp: "required — 15 min for access, 7d for refresh"
    iss: "required — validate on every request"
    aud: "required — validate matches expected service"
    iat: "required"
    jti: "recommended — for revocation"
    nbf: "recommended"
  storage:
    access_token: "memory only (never localStorage)"
    refresh_token: "httpOnly secure cookie"
  revocation:
    method: "token blacklist with Redis TTL matching exp"
    on_password_change: "revoke all tokens"
    on_permission_change: "revoke all tokens"
```

### OAuth 2.0 / OIDC Checklist

- [ ] Use Authorization Code flow with PKCE (never Implicit)
- [ ] Validate `state` parameter to prevent CSRF
- [ ] Validate `nonce` for OIDC to prevent replay
- [ ] Validate token issuer and audience
- [ ] Store tokens server-side, not in browser
- [ ] Implement token rotation for refresh tokens
- [ ] Set minimal scopes (principle of least privilege)
- [ ] Register exact redirect URIs (no wildcards)

## Phase 9: Security Program Design

### Building a Security Program from Scratch

**Quarter 1 — Foundation:**
```
Week 1-2: Asset inventory (what do we have?)
Week 3-4: Risk assessment (what matters most?)
Week 5-6: Critical controls (authentication, secrets, backups)
Week 7-8: Basic scanning (dependencies, secrets in code)
Week 9-10: Incident response plan (what if something happens?)
Week 11-12: Security awareness basics (phishing, passwords)
```

**Quarter 2 — Automation:**
```
- CI/CD security scanning (SAST, dependency audit)
- Automated secret detection (pre-commit hooks)
- Centralized logging and basic alerting
- Access reviews (quarterly)
- Vulnerability management process
```

**Quarter 3 — Maturity:**
```
- Penetration testing (first external assessment)
- Security architecture review
- Data classification and handling policies
- Vendor security assessments
- Bug bounty program (start small)
```

**Quarter 4 — Optimization:**
```
- Compliance framework alignment (SOC 2, ISO 27001)
- Red team exercise
- Security metrics dashboard
- Security champion program (devs with security training)
- Supply chain security (SBOM, signed artifacts)
```

### Security Metrics Dashboard

```yaml
security_dashboard:
  vulnerability_management:
    - open_critical: 0  # Target: always 0
    - open_high: 0      # Target: < 5
    - mean_time_to_remediate:
        critical: "24h"  # Target
        high: "7d"
        medium: "30d"
    - scan_coverage: "100%"  # % of repos with automated scanning

  incident_management:
    - incidents_this_quarter: 0
    - mean_time_to_detect: "< 1h"
    - mean_time_to_respond: "< 4h"
    - mean_time_to_recover: "< 24h"

  access_control:
    - mfa_adoption: "100%"
    - privileged_accounts: 0  # Count, minimize
    - stale_accounts: 0       # Accounts unused > 90 days
    - access_reviews_completed: "on schedule"

  code_security:
    - repos_with_sast: "100%"
    - repos_with_dependency_scanning: "100%"
    - secret_detection_coverage: "100%"
    - security_review_for_critical_changes: "100%"

  training:
    - security_awareness_completion: "100%"
    - phishing_simulation_click_rate: "< 5%"
    - security_champions_per_team: ">= 1"
```

## Phase 10: Penetration Testing Methodology

### Reconnaissance

```
PASSIVE (no direct interaction with target):
1. DNS enumeration: subdomains, MX, TXT, CNAME
   - Tools: subfinder, amass, crt.sh, dnsdumpster
2. Technology fingerprinting
   - Check: Wappalyzer, BuiltWith, HTTP headers
3. Public exposure
   - Shodan/Censys for open ports/services
   - GitHub/GitLab for leaked code/secrets
   - Wayback Machine for old endpoints
4. Employee OSINT (for social engineering scope)
   - LinkedIn for tech stack clues
   - Job postings reveal internal tools

ACTIVE (interacting with target — requires permission):
1. Port scanning: full TCP + top 1000 UDP
2. Service enumeration: version detection
3. Web crawling: sitemap, robots.txt, directory brute-force
4. API discovery: /api, /v1, /graphql, /swagger, /openapi
```

### Testing Phases

**Phase 1 — Authentication Testing**
```
- Credential stuffing resistance (rate limiting)
- Password reset flow (token guessability, expiry, reuse)
- Account enumeration (different responses for valid/invalid users)
- Session management (token entropy, fixation, timeout)
- MFA bypass attempts (backup codes, race conditions)
- OAuth flow attacks (redirect URI manipulation, scope escalation)
```

**Phase 2 — Authorization Testing**
```
- Horizontal privilege escalation (access other users' data)
- Vertical privilege escalation (user → admin)
- Missing function-level access control (direct API calls)
- IDOR on every resource endpoint (change IDs systematically)
- GraphQL introspection + unauthorized field access
- Mass assignment (send extra fields in requests)
```

**Phase 3 — Injection Testing**
```
- SQL injection on all user inputs (including headers, cookies)
- XSS (reflected, stored, DOM-based) on all output points
- Command injection on any server-side execution
- SSRF on any URL input or file fetch
- Template injection (if server-side templating)
- LDAP/XML/XXE injection where applicable
```

**Phase 4 — Business Logic Testing**
```
- Price manipulation (change prices in requests)
- Quantity manipulation (negative numbers, decimals, MAX_INT)
- Race conditions (concurrent requests for same resource)
- Workflow bypass (skip steps in multi-step processes)
- Coupon/discount abuse (reuse, stacking)
- Rate limit bypass (header rotation, distributed requests)
```

### Penetration Test Report Template

```yaml
report:
  executive_summary:
    overall_risk: "critical|high|medium|low"
    critical_findings: 0
    high_findings: 0
    medium_findings: 0
    low_findings: 0
    key_recommendations:
      - "[top 3 fixes by impact]"

  scope:
    targets: "[URLs, IPs, apps tested]"
    methodology: "OWASP Testing Guide v4.2 + PTES"
    dates: "YYYY-MM-DD to YYYY-MM-DD"
    type: "black-box|grey-box|white-box"
    exclusions: "[what was out of scope]"

  findings:
    - id: "F-001"
      title: "[descriptive title]"
      severity: "critical|high|medium|low|info"
      cvss: 0.0
      location: "[URL/endpoint/component]"
      description: "[what the vulnerability is]"
      impact: "[what an attacker could do]"
      evidence: "[screenshots, request/response pairs]"
      reproduction_steps:
        - "[step by step]"
      remediation: "[specific fix with code examples]"
      references:
        - "[OWASP, CWE, CVE links]"

  positive_observations:
    - "[security controls that were effective]"
```

## Phase 11: Supply Chain Security

### Dependency Security

```yaml
supply_chain:
  dependencies:
    - lock_files: "always commit (package-lock.json, poetry.lock, go.sum)"
    - pin_versions: "exact versions, not ranges"
    - audit_frequency: "every CI build"
    - auto_update: "Dependabot/Renovate with auto-merge for patch, review for minor/major"
    - review_new_deps:
        check: "maintainer count, last update, download count, known issues"
        rule: "no single-maintainer deps for critical paths"
    - sbom: "generate SPDX or CycloneDX on every release"

  build_pipeline:
    - reproducible_builds: true
    - artifact_signing: true
    - build_provenance: true  # SLSA Level 2+
    - no_curl_pipe_bash: true  # Never pipe internet scripts to shell
    - verify_checksums: true

  ci_cd:
    - pin_action_versions: "use SHA, not tags (actions/checkout@SHA)"
    - least_privilege_tokens: true
    - no_secrets_in_logs: true
    - protected_branches: true
    - required_reviews: true
    - signed_commits: "recommended"
```

## Phase 12: Security Scoring Rubric

Rate any application/system 0-100:

| Dimension | Weight | 0 (Critical) | 5 (Adequate) | 10 (Excellent) |
|-----------|--------|---------------|---------------|-----------------|
| Authentication & Access | 20% | No auth or default creds | Password + basic RBAC | MFA + ABAC + zero trust |
| Data Protection | 15% | Plaintext secrets, no encryption | Encryption at rest + transit | E2E encryption, key rotation, classification |
| Vulnerability Management | 15% | No scanning, known CVEs | Automated scanning, SLAs met | Full coverage, MTTD < 1h, bug bounty |
| Infrastructure Security | 15% | Open ports, no firewall | Hardened baseline, least privilege | Zero trust, microsegmentation, IaC |
| Logging & Monitoring | 10% | No security logging | Centralized logs, basic alerts | SIEM, anomaly detection, 24/7 SOC |
| Incident Response | 10% | No plan | Documented plan, tested annually | Automated response, < 1h MTTR |
| Code Security | 10% | No reviews, injection vulns | SAST in CI, peer review | Full pipeline, threat modeling, security champions |
| Supply Chain | 5% | No dependency management | Lock files, automated scanning | SBOM, signed artifacts, SLSA |

**Score interpretation:**
- 90-100: Excellent — security is a competitive advantage
- 70-89: Good — solid foundation, keep improving
- 50-69: Needs work — significant gaps exist
- Below 50: Critical — stop feature work, fix security

## Common Mistakes

1. **Security through obscurity** — hiding admin panel at /secret-admin is not security
2. **Client-side only validation** — always validate server-side
3. **Trusting internal networks** — assume breach, verify everything
4. **Logging sensitive data** — passwords, tokens, PII in logs = breach waiting to happen
5. **"We're too small to be targeted"** — automated attacks don't check company size
6. **One-time audit mentality** — security is continuous, not a checkbox
7. **Ignoring security in dev/staging** — attackers find your staging environment too
8. **Over-permissioning for convenience** — least privilege, always
9. **No backup testing** — backups you haven't tested are hopes, not backups
10. **Treating compliance as security** — SOC 2 ≠ secure; it's a starting point

## Edge Cases

- **Startup with zero security:** Start with Phase 9 Quarter 1 — foundation first
- **Legacy application:** Focus on network segmentation + WAF + monitoring before code fixes
- **Microservices:** Service mesh for mTLS, centralized auth (OAuth/OIDC), API gateway
- **IoT/embedded:** Assume physical access, encrypt firmware, signed updates, minimal attack surface
- **Mobile apps:** Certificate pinning, root/jailbreak detection, binary protection, secure local storage
- **Serverless:** Function-level IAM, no secrets in code, API Gateway throttling, cold start timing attacks
- **Multi-tenant SaaS:** Tenant isolation verification, noisy neighbor prevention, cross-tenant data leak testing

## Natural Language Commands

```
"Audit security of [project/repo]" → Full assessment (Phase 1-4)
"Threat model [system/feature]" → STRIDE analysis (Phase 2)
"Check OWASP top 10 for [app]" → Application security review (Phase 3)
"Harden [server/container/cloud]" → Infrastructure checklist (Phase 4)
"Create incident response plan" → IR playbook (Phase 6)
"Design security program" → Phased program build (Phase 9)
"Pentest methodology for [target]" → Testing phases (Phase 10)
"Score security of [system]" → 100-point rubric (Phase 12)
"Review auth implementation" → Auth deep dive (Phase 8)
"Check security headers" → Header audit (Phase 7)
"Vulnerability report for [finding]" → Report template (Phase 5)
"Supply chain security review" → Dependency audit (Phase 11)
```
