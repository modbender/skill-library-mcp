# Changelog - AgentShield

All notable changes to AgentShield are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [6.4.0] - 2026-02-26

### 🆕 Added - CRL + Registry Release

**Certificate Revocation**
- Certificate Revocation List (CRL) endpoint `/api/crl/download`
- RFC 5280 compliant CRL format
- Instant revocation via `/api/crl/revoke/:id`
- CRL check endpoint `/api/crl/check/:id`
- Automatic CRL generation every 24 hours

**Public Trust Registry**
- Public agent registry at `/registry` page
- Search functionality for verified agents
- Trust score display with tier badges
- Pagination for large agent lists
- Agent profile pages with verification history

**Trust Score System**
- Trust score calculation algorithm (0-100)
- Tier system: UNVERIFIED (0) → BASIC (1-49) → VERIFIED (50-79) → TRUSTED (80-100)
- Score factors: 40% verifications, 30% age, 30% success rate
- Automatic score updates on new verifications

**Frontend Improvements**
- Trust score badges on registry
- CRL status indicators
- Filter by verification tier
- Responsive registry table
- Real-time status updates

### 🔧 Changed
- Updated API rate limits for registry endpoints
- Enhanced certificate metadata storage
- Improved database schema for CRL support

### 📚 Documentation
- Added CRL architecture documentation
- Trust score calculation explained
- Registry API endpoints documented
- Updated security model diagrams

---

## [6.3.0] - 2026-02-20

### 🆕 Added - Agent Registry

**Public Registry**
- Agent certificate directory at `/api/registry/agents`
- Search endpoint `/api/registry/search`
- Public verification status pages
- Trust score badges

**Multi-Verification Support**
- Track multiple verifications per agent
- Calculate trust score from verification history
- Display verification count in registry

**Database Enhancements**
- PostgreSQL production database
- SQLite local development fallback
- Certificate persistence layer
- Verification history tracking

### 🔧 Changed
- API responses include trust score
- Certificate format extended with metadata
- Frontend displays public registry link

---

## [6.2.0] - 2026-02-15

### 🆕 Added - Challenge-Response Protocol

**Cryptographic Identity**
- Ed25519 key pair generation (local)
- Challenge-response verification
- Zero-knowledge proof of identity
- Public key registry

**Security Enhancements**
- Private keys never transmitted
- Challenge nonce with 5-minute expiry
- Signature validation on backend
- Tamper-proof certificate issuance

**API Endpoints**
- `/api/challenge/create` - Generate challenge nonce
- `/api/challenge/verify` - Validate signature
- `/api/verify/:agent_id` - Check certificate status

### 🔧 Changed
- Certificate format now includes public key hash
- Assessment results linked to cryptographic identity
- PDF reports include Ed25519 fingerprint

### 📚 Documentation
- Challenge-response protocol explained
- Ed25519 signature examples
- Security architecture diagrams

---

## [6.1.0] - 2026-02-10

### 🆕 Added - Privacy-First Tests

**Local Security Testing**
- 52+ security tests run locally in agent environment
- Subagent-based test execution
- Zero data exfiltration to AgentShield servers
- Open source test suite

**Test Categories**
- Input Sanitizer (prompt injection detection)
- EchoLeak (zero-click data exfiltration tests)
- Tool Sandbox (permission boundary controls)
- Output DLP (PII/API key detection)
- Supply Chain Scanner (dependency integrity)

**Privacy Architecture**
- All tests execute in user's agent session
- No code or prompt data uploaded
- Only public certificate data stored
- GDPR/CCPA compliant design

**Rate Limiting**
- 3 free audits per hour
- 1 audit per hour after limit
- Rate limit headers in API responses
- SQLite-based rate tracking

### 🔧 Changed
- Moved from cloud-based to local-first testing
- Reduced API payload to public key only
- Enhanced privacy guarantees in documentation

### 📚 Documentation
- Privacy-first architecture explained
- Local vs cloud scanning comparison
- Open source test verification guide

---

## [6.0.0] - 2026-02-01

### 🆕 Added - Initial Release

**Core Features**
- Basic security assessment framework
- PDF report generation
- API backend deployment
- Certificate issuance (basic)

**Security Tests**
- Token optimization analysis
- Code vulnerability scanning
- Basic prompt injection tests

**Infrastructure**
- Heroku backend deployment
- SQLite database for certificates
- Basic rate limiting

### 📚 Documentation
- README with quick start guide
- Basic API documentation
- Installation instructions

---

## Version Numbering

- **Major (X.0.0)**: Breaking API changes, major architecture overhaul
- **Minor (6.X.0)**: New features, backwards-compatible additions
- **Patch (6.4.X)**: Bug fixes, minor improvements

---

## Upgrade Guides

### Upgrading to v6.4
```bash
# Update skill
clawhub update agentshield-audit

# No breaking changes - existing certificates remain valid
```

### Upgrading to v6.3
```bash
# Database migration required for registry
python migrate.py --to-6.3

# Existing certificates auto-imported to registry
```

### Upgrading to v6.2
```bash
# Re-run assessment to generate Ed25519 identity
agentshield-audit --auto --yes

# Old certificates remain valid but lack cryptographic proof
```

---

## Roadmap

### Upcoming Features (v6.5+)

**Planned:**
- 🔄 Automatic certificate renewal
- 🏢 Enterprise self-hosted registry
- 🔗 Blockchain anchoring (optional)
- 🌐 Multi-language support
- 📊 Trust score analytics dashboard

**Under Consideration:**
- Integration with major AI platforms
- Cross-platform agent verification
- Federation protocol for multiple registries
- Hardware security module (HSM) support

**Vote on features:** [GitHub Discussions](https://github.com/bartelmost/agentshield/discussions)

---

## Breaking Changes

### v6.0 → v6.1
- **API Endpoint Change:** `/audit` → `/api/assess`
- **Migration:** Update ClawHub skill to latest version

### v6.1 → v6.2
- **Certificate Format:** Added Ed25519 public key field
- **Migration:** Re-run assessment to upgrade certificate

### v6.2 → v6.3
- **Database Schema:** New `verifications` table
- **Migration:** Run `migrate.py` script

### v6.3 → v6.4
- **Database Schema:** New `crl_entries` table
- **Migration:** Auto-migration on first API start

---

## Security Advisories

**None reported yet.**

For responsible disclosure: ratgeberpro@gmail.com

**Bug Bounty:** See [SECURITY.md](./SECURITY.md#bug-bounty)

---

*Maintained by Kalle-OC*  
*Last Updated: 2026-02-26*
